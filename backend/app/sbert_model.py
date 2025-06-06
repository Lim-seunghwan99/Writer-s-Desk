from sentence_transformers import SentenceTransformer
from functools import lru_cache
from . import config
SBERT_EMBEDDING_DIMENSION = 768


class SBERTEmbedder:
    def __init__(self):
        model_name_to_load = config.EMBEDDING_MODEL_NAME
        self.model = SentenceTransformer(model_name_to_load)
        print(f"SBERT Embedder initialized with model: {model_name_to_load}")

    def encode(
        self, texts, show_progress_bar=False
    ):  
        return self.model.encode(texts, show_progress_bar=show_progress_bar)


@lru_cache()
def get_embedder():
    return SBERTEmbedder()
