from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.config import (  
    LLM_GENERATE_MODEL,
    LLM_GENERATE_TEMP,
    OPENAI_API_KEY,
)

try:
    llm_gen = ChatOpenAI(
        model=LLM_GENERATE_MODEL,
        temperature=LLM_GENERATE_TEMP,
        api_key=OPENAI_API_KEY if OPENAI_API_KEY else None,
    )
    print(
        f"ChatOpenAI for llm_generate ({LLM_GENERATE_MODEL}, temp={LLM_GENERATE_TEMP}) loaded."
    )
except Exception as e:
    print(f"Error initializing ChatOpenAI for llm_generate_node: {e}")
    llm_gen = None


# --- llm_generate_node ---
def llm_generate_node(state: dict) -> dict:
    print(f"--- Node: llm_generate (Input State: {state}) ---")
    if llm_gen is None:
        print("Error: LLM not initialized for llm_generate_node.")
        return {
            "query": state.get("query"),
            "retrieved_from_rag": state.get("retrieved_from_rag", []),
            "web_search_words": state.get("web_search_words", []),
            "llm_generated_words": [],  
            "missing_llm": state.get("missing_llm", 0),
            "target_word_count": state.get("target_word_count"),
            "error": "LLM for generation not initialized",
        }

    query = state.get("query")
    num_to_find_from_llm = state.get("missing_llm", 0)
    rag_words = state.get("retrieved_from_rag", [])
    web_words = state.get("web_search_words", [])
    existing_words = set(
        w.lower() for w in rag_words + web_words + [query]
    )  
    final_llm_words = []

    if num_to_find_from_llm > 0:
        context_parts = []
        if rag_words:
            context_parts.append(
                f"이미 RAG를 통해 찾은 관련 단어들: {', '.join(rag_words)}"
            )
        if web_words:
            context_parts.append(
                f"웹 검색을 통해 찾은 관련 단어들: {', '.join(web_words)}"
            )

        context_str = "\n".join(context_parts)
        if not context_str:
            context_str = f"'{query}'에 대한 추가 정보가 없습니다."
        else:
            context_str = f"'{query}'에 대해 다음 정보를 참고하세요:\n{context_str}"

        prompt_content = (
            f"{context_str}\n\n"
            f"위 정보를 바탕으로, '{query}'와(과) 의미적으로 유사하거나 관련된 새로운 핵심 단어를 정확히 {num_to_find_from_llm}개 생성해주세요. "
            f"이미 찾은 단어들({', '.join(list(existing_words))}) 및 '{query}' 자체와는 중복되지 않아야 합니다. "
            f"결과는 반드시 콤마(,)로 구분된 단어 목록으로만 응답해주세요. 다른 어떤 설명도 포함하지 마세요."
        )
        try:
            response = llm_gen.invoke([HumanMessage(content=prompt_content)])
            response_text = response.content.strip()
            if response_text:
                raw_words = [
                    word.strip() for word in response_text.split(",") if word.strip()
                ]
                unique_llm_words = []
                for word in raw_words:
                    if (
                        word.lower() not in existing_words
                        and word not in unique_llm_words
                    ):
                        unique_llm_words.append(word)
                final_llm_words = unique_llm_words[:num_to_find_from_llm]
                print(f"LLM Generate: LLM generated words: {final_llm_words}")
        except Exception as e:
            print(f"Error during LLM generation in llm_generate_node: {e}")
    else:
        print("LLM Generate: Skipping LLM generation as missing_llm is 0.")

    return {
        "query": query,
        "retrieved_from_rag": rag_words,
        "web_search_words": web_words,
        "llm_generated_words": final_llm_words,
        "target_word_count": state.get("target_word_count"),
    }
