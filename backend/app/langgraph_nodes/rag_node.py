from opensearchpy import OpenSearch

from sentence_transformers import SentenceTransformer  
from app.config import (  
    OPENSEARCH_HOST,
    OPENSEARCH_PORT,
    EMBEDDING_MODEL_NAME,
    SIMILARITY_THRESHOLD,
    OPENSEARCH_INDEX_NAME,
)

try:
    client = OpenSearch(hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}])
    if not client.ping():
        raise ConnectionError("Failed to connect to OpenSearch")
    print(
        f"Successfully connected to OpenSearch at {OPENSEARCH_HOST}:{OPENSEARCH_PORT}"
    )
except Exception as e:
    print(f"Error initializing OpenSearch client: {e}")
    client = None

try:
    embedder_sbert = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print(f"SBERT Embedder ({EMBEDDING_MODEL_NAME}) loaded successfully.")
except Exception as e:
    print(f"Error initializing SBERT Embedder: {e}")
    embedder_sbert = None


class SBERTEmbedder:  
    def __init__(self, model):
        self.model = model

    def encode(self, sentences, batch_size=32, show_progress_bar=False):
        if self.model is None:
            raise RuntimeError("SBERT model is not initialized.")
        return self.model.encode(
            sentences, batch_size=batch_size, show_progress_bar=show_progress_bar
        )


embedder = SBERTEmbedder(embedder_sbert)


# --- check_rag_function ---
def check_rag_function(state: dict) -> dict:
    print(f"--- Node: check_rag (Input State: {state}) ---")
    if client is None or embedder.model is None:
        print("Error: OpenSearch client or SBERT embedder not initialized.")
        return {
            "query": state.get("query"),
            "retrieved_from_rag": [],
            "missing_count_after_rag": state.get(
                "target_word_count", 5
            ),  
            "error": "RAG components not initialized",
        }

    query = state["query"]
    target_word_count = state.get("target_word_count", 5)  

    try:
        vector = embedder.encode([query])[0]
        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, doc['embedding']) + 1.0",  
                    "params": {"query_vector": vector.tolist()},
                },
            }
        }
        response = client.search(
            index=OPENSEARCH_INDEX_NAME,  
            body={"query": script_query, "size": 10},  
        )
        hits = response["hits"]["hits"]
    except Exception as e:
        print(f"Error during OpenSearch query in check_rag_function: {e}")
        return {
            "query": query,
            "retrieved_from_rag": [],
            "missing_count_after_rag": target_word_count,
            "target_word_count": target_word_count,
            "error": f"OpenSearch query failed: {str(e)}",
        }

    if not hits:
        print("RAG: No hits found.")
        return {
            "query": query,
            "retrieved_from_rag": [],
            "missing_count_after_rag": target_word_count,
            "target_word_count": target_word_count,
        }

    retrieved_sentences = [
        hit["_source"]["form"]
        for hit in hits
        if (hit["_score"] - 1.0)
        > SIMILARITY_THRESHOLD  
    ]
    retrieved_sentences = list(
        set(s for s in retrieved_sentences if s.lower() != query.lower())
    )

    print(
        f"RAG: Retrieved {len(retrieved_sentences)} sentences initially: {retrieved_sentences}"
    )

    retrieved_from_rag = retrieved_sentences[:target_word_count]
    missing_count_after_rag = max(0, target_word_count - len(retrieved_from_rag))

    print(f"RAG: Final {len(retrieved_from_rag)} sentences: {retrieved_from_rag}")
    print(f"RAG: Missing count after RAG: {missing_count_after_rag}")

    missing_web = 0
    missing_llm = 0
    if missing_count_after_rag > 0:
        if missing_count_after_rag % 2 == 1:
            missing_llm = missing_count_after_rag // 2 + 1
            missing_web = missing_count_after_rag // 2
        else:
            missing_llm = missing_count_after_rag // 2
            missing_web = missing_count_after_rag // 2

    return {
        "query": query,
        "retrieved_from_rag": retrieved_from_rag,
        "missing_web": missing_web,
        "missing_llm": missing_llm,
        "target_word_count": target_word_count,  
    }
