from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI  
from app.config import (
    LLM_WEB_SEARCH_MODEL,
    LLM_WEB_SEARCH_TEMP,
)

try:
    llm_web = ChatOpenAI(
        model=LLM_WEB_SEARCH_MODEL,
        temperature=LLM_WEB_SEARCH_TEMP,
    )
    print(
        f"ChatOpenAI for web_search ({LLM_WEB_SEARCH_MODEL}, temp={LLM_WEB_SEARCH_TEMP}) loaded."
    )
except Exception as e:
    print(f"Error initializing ChatOpenAI for web_search_node: {e}")
    llm_web = None

# DuckDuckGoSearchResults는 llm을 필요로 하지 않음, 웹 서치 결과를 llm으로 가공해서 전달
def web_search_node(state: dict) -> dict:
    print(f"--- Node: web_search (Input State: {state}) ---")
    if llm_web is None:
        print("Error: LLM not initialized for web_search_node.")
        return {
            "query": state.get("query"),
            "retrieved_from_rag": state.get("retrieved_from_rag", []),
            "web_search_words": [],  
            "missing_web": state.get("missing_web", 0),
            "missing_llm": state.get("missing_llm", 0),
            "target_word_count": state.get("target_word_count"),
            "error": "LLM for web search not initialized",
        }

    query = state["query"]
    num_to_find_from_web = state.get("missing_web", 0)
    final_web_words = []

    if num_to_find_from_web > 0:
        search_tool = DuckDuckGoSearchResults(
            max_results=max(
                5, num_to_find_from_web * 2
            ),
        )
        try:
            search_prompt = f"'{query}'와 관련된 다양한 동의어, 유의어, 연관 검색어 또는 주제어 {num_to_find_from_web * 2}개"
            search_output_raw = search_tool.run(search_prompt)

            search_results_snippets = []
            if isinstance(search_output_raw, str):
                import re

                snippets = re.findall(
                    r"snippet: (.*?)(?:, title:|, link:|$)", search_output_raw
                )
                if snippets:
                    search_results_snippets = snippets
                else:  
                    search_results_snippets = [
                        line.strip()
                        for line in search_output_raw.split("\n")
                        if line.strip()
                    ][:5]

            elif isinstance(search_output_raw, list):  
                search_results_snippets = [str(item) for item in search_output_raw][:5]
            else:
                print(
                    f"Web Search: Unexpected type from search_tool.run(): {type(search_output_raw)}"
                )

            if search_results_snippets:
                context_for_llm = "\n".join(search_results_snippets)
                print(
                    f"Web Search: Context for LLM: {context_for_llm[:200]}..."
                )  

                prompt_content = (
                    f"다음은 '{query}'와(과) 관련된 웹 검색 결과입니다:\n---CONTEXT_START---\n{context_for_llm}\n---CONTEXT_END---\n\n"
                    f"이 정보를 바탕으로 '{query}'와(과) 의미적으로 유사하거나 관련된 고유한 핵심 단어를 정확히 {num_to_find_from_web}개 찾아주세요. "
                    f"결과는 반드시 콤마(,)로 구분된 단어 목록으로만 응답해주세요. "
                    f"다른 어떤 설명, 번호 매기기, 문장, 줄바꿈도 포함하지 마세요. "
                    f"오직 단어들만 콤마로 구분해서 한 줄로 응답해야 합니다. '{query}' 자체는 제외해주세요."
                )
                response = llm_web.invoke([HumanMessage(content=prompt_content)])
                response_text = response.content.strip()

                if response_text:
                    raw_words = [
                        word.strip()
                        for word in response_text.split(",")
                        if word.strip()
                    ]
                    unique_words = []
                    for word in raw_words:
                        if word.lower() != query.lower() and word not in unique_words:
                            unique_words.append(word)
                    final_web_words = unique_words[:num_to_find_from_web]
                    print(f"Web Search: LLM extracted words: {final_web_words}")
            else:
                print("Web Search: No usable search snippets found to pass to LLM.")

        except Exception as e:
            print(f"Error during web search or LLM processing in web_search_node: {e}")
    else:
        print("Web Search: Skipping web search as missing_web is 0.")

    return {
        "query": query,
        "retrieved_from_rag": state.get("retrieved_from_rag", []),
        "web_search_words": final_web_words,
        "missing_llm": state.get("missing_llm", 0),  
        "target_word_count": state.get("target_word_count"),
    }
