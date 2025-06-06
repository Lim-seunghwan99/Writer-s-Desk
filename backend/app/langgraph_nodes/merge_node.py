def merge_node(state: dict) -> dict:
    print(f"--- Node: merge (Input State: {state}) ---")
    query = state.get("query")
    rag_words = state.get("retrieved_from_rag", [])
    web_words = state.get("web_search_words", [])
    llm_words = state.get("llm_generated_words", [])
    target_word_count = state.get("target_word_count", 5)

    all_found_words = rag_words + web_words + llm_words
    final_unique_words = []
    seen_words_lower = {query.lower()}  

    for word in all_found_words:
        if word.strip() and word.lower() not in seen_words_lower:
            final_unique_words.append(word)
            seen_words_lower.add(word.lower())

    final_selected_words = final_unique_words[:target_word_count]
    print(
        f"Merge: Final selected {len(final_selected_words)} words: {final_selected_words}"
    )

    return {
        "query": query,
        "final_words": final_selected_words,
        "target_word_count": target_word_count,
        "rag_source_count": len(rag_words),
        "web_source_count": len(web_words),
        "llm_source_count": len(llm_words),
    }
