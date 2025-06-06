# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# OpenSearch 설정
OPENSEARCH_HOST = os.getenv("OPENSEARCH_SINGLE_HOST")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_SINGLE_PORT"))
OPENSEARCH_INDEX_NAME = os.getenv("OPENSEARCH_INDEX_NAME")
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER") # 필요시
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD") # 필요시

# SBERT 임베딩 모델 설정
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
)
SIMILARITY_THRESHOLD = float(
    os.getenv("SIMILARITY_THRESHOLD", "0.8")
)  # .env에 추가하거나 기본값 사용

# OpenAI API 키
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 이미 .env에 정의되어 있음

# 웹 검색 노드용 LLM 설정
LLM_WEB_SEARCH_MODEL = os.getenv("LLM_WEB_SEARCH_MODEL_NAME", "gpt-4o-mini")
LLM_WEB_SEARCH_TEMP = float(os.getenv("LLM_WEB_SEARCH_TEMPERATURE", "0.0"))

# 단어 생성 노드용 LLM 설정
LLM_GENERATE_MODEL = os.getenv("LLM_GENERATE_MODEL_NAME", "gpt-4o-mini")
LLM_GENERATE_TEMP = float(os.getenv("LLM_GENERATE_TEMPERATURE", "0.1"))

# 기타 LangSmith 설정 등도 여기에 추가 가능
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"

# 대사 생성용 LLM 설정
DIALOGUE_LLM_MODEL = os.getenv("DIALOGUE_LLM_MODEL_NAME", "gpt-4o-mini")  # 기본값 설정
DIALOGUE_LLM_TEMP = float(os.getenv("DIALOGUE_LLM_TEMPERATURE", "0.7"))  # 기본값 설정

# AI_UTILS 설정
AI_UTILS_MODEL = os.getenv("AI_UTILS_MODEL_NAME", "gpt-4o-mini")  # 기본값 설정

OPENSEARCH_RAG_INDEX_NAME = os.getenv(
    "OPENSEARCH_RAG_INDEX_NAME", "works_rag_content_index"
)


