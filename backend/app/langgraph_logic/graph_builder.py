from langgraph.graph import StateGraph, START, END
from app.langgraph_nodes.rag_node import check_rag_function
from app.langgraph_nodes.web_search_node import web_search_node
from app.langgraph_nodes.llm_generate_node import llm_generate_node
from app.langgraph_nodes.merge_node import merge_node


def build_graph():
    builder = StateGraph(dict)

    builder.add_node("check_rag", check_rag_function)
    builder.add_node("web_search", web_search_node)
    builder.add_node("llm_generate", llm_generate_node)
    builder.add_node(
        "merge_results", merge_node
    )

    builder.add_edge(START, "check_rag")

    def route_after_rag(state: dict):
        print(f"--- Router after RAG (State: {state}) ---")
        if state.get("error"):
            print("Routing to: merge_results (due to RAG error)")
            return "to_merge" 

        missing_web = state.get("missing_web", 0)
        missing_llm = state.get("missing_llm", 0)

        if missing_web == 0 and missing_llm == 0:  
            print("Routing to: merge_results (RAG sufficient)")
            return "to_merge"
        elif missing_web > 0:
            print("Routing to: web_search")
            return "to_web_search"
        elif missing_llm > 0:
            print("Routing to: llm_generate (skipping web)")
            return "to_llm_direct"
        else:  
            print("Routing to: merge_results (fallback from after_rag)")
            return "to_merge"

    builder.add_conditional_edges(
        "check_rag",
        route_after_rag,
        {
            "to_merge": "merge_results",
            "to_web_search": "web_search",
            "to_llm_direct": "llm_generate",  
        },
    )

    def route_after_web(state: dict):
        print(f"--- Router after Web Search (State: {state}) ---")
        if state.get("error"):
            print("Routing to: merge_results (due to web_search error)")
            return "to_merge"

        missing_llm = state.get("missing_llm", 0)
        if missing_llm > 0:  
            print("Routing to: llm_generate")
            return "to_llm"
        else:  
            print("Routing to: merge_results (web_search sufficient or no llm needed)")
            return "to_merge"

    builder.add_conditional_edges(
        "web_search",
        route_after_web,
        {"to_llm": "llm_generate", "to_merge": "merge_results"},
    )

    builder.add_edge("llm_generate", "merge_results")

    builder.add_edge("merge_results", END)

    graph = builder.compile()
    print("LangGraph compiled successfully.")
    return graph


compiled_graph = build_graph()
