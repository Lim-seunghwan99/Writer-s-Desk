from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv, find_dotenv
from ..ai_utils import generate_examples_with_gpt, evaluate_user_example
from .. import crud, models, schemas, database 
import os
from app.config import (
    OPENSEARCH_HOST,
    OPENSEARCH_PORT,
    OPENSEARCH_USER,
    OPENSEARCH_PASSWORD,
    OPENSEARCH_INDEX_NAME,
    EMBEDDING_MODEL_NAME,
    LLM_GENERATE_MODEL,
    LLM_GENERATE_TEMP,
    OPENAI_API_KEY,
)

from sentence_transformers import SentenceTransformer
from opensearchpy import (
    OpenSearch,
    ConnectionError as OpenSearchConnectionError,
    NotFoundError,
    RequestError,
)

from app.langgraph_logic.graph_builder import compiled_graph
from ..crud.word_examples import bring_exsen
embedding_model = None
opensearch_client = None
OPENSEARCH_HOSTS_CONFIG = [{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}]  
OPENSEARCH_AUTH_CONFIG = ((OPENSEARCH_USER, OPENSEARCH_PASSWORD) if OPENSEARCH_USER and OPENSEARCH_PASSWORD else None)

try:
    if EMBEDDING_MODEL_NAME:
        print(
            f"Attempting to load embedding model: '{EMBEDDING_MODEL_NAME}' from config."
        )
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"Embedding model '{EMBEDDING_MODEL_NAME}' loaded successfully.")
    else:
        print(
            "Warning: EMBEDDING_MODEL_NAME is not set in config. Embedding model not loaded."
        )

    if OPENSEARCH_HOST:  
        print(
            f"Attempting to connect to OpenSearch at {OPENSEARCH_HOSTS_CONFIG} "
            f"with user '{OPENSEARCH_USER if OPENSEARCH_USER else 'N/A'}'"
        )
        opensearch_client = OpenSearch(
            hosts=OPENSEARCH_HOSTS_CONFIG,
            http_auth=OPENSEARCH_AUTH_CONFIG,
            use_ssl=False, 
            verify_certs=False,
            timeout=30,
        )
        if not opensearch_client.ping():
            raise OpenSearchConnectionError(
                "Failed to connect to OpenSearch (ping failed)."
            )
        print("Successfully connected to OpenSearch.")
    else:
        print(
            "Warning: OPENSEARCH_HOST is not set in config. OpenSearch client not initialized."
        )

    if embedding_model and opensearch_client:
        print(
            "RAG components (Embedding Model & OpenSearch Client) initialized successfully for k-NN."
        )
    else:
        print("Warning: One or more RAG components for k-NN could not be initialized.")


except OpenSearchConnectionError as e:
    print(f"Error connecting to OpenSearch: {e}")
    opensearch_client = None
except Exception as e:
    import traceback

    print(f"Error initializing RAG components for k-NN: {e}")
    traceback.print_exc()  
    embedding_model = None 
    opensearch_client = None


router = APIRouter(
    prefix="/words",
    tags=["words"],  
)


# 단어 추가
@router.post("/",response_model=schemas.Word,status_code=status.HTTP_201_CREATED)
def create_word_for_user(
    word_data: schemas.WordCreate,
    db: Session = Depends(database.get_db),
):
    try:
        created_word = crud.words.create_user_word(db=db, word_data=word_data)
        return created_word
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"단어 추가 중 오류 발생: {str(e)}",
        )


# 단어 삭제
@router.delete("/{word_id}", response_model=schemas.Word)
def delete_word_by_id(  # 함수 이름 명확화
    word_id: int = Path(..., description="삭제할 단어의 ID"),
    db: Session = Depends(database.get_db),
):
    db_word = crud.words.get_word_by_id(db, word_id=word_id)  
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="단어를 찾을 수 없습니다."
        )

    try:
        deleted_word = crud.words.delete_word(db, word_id=word_id)
        return deleted_word  
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"단어 삭제 중 오류 발생: {str(e)}",
        )


@router.get("/{user_id}/{word_name}", response_model=schemas.Word)  
def get_word_by_name_route(  
    word_name: str = Path(..., description="조회할 단어의 이름"),
    user_id: str = Path(
        ..., description="단어 소유자 ID"
    ),  
    db: Session = Depends(database.get_db),
):
    db_word = crud.words.get_word_by_name_and_user(
        db, word_name=word_name, user_id=user_id
    )
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="단어를 찾을 수 없습니다."
        )
    try:
        updated_word = crud.words.increment_word_count_atomic(
            db, word_id=db_word.words_id
        )
        if updated_word:
            return updated_word
        else:
            return db_word
    except Exception as e:
        return db_word  


# 단어 ID로 조회 
@router.get("/{user_id}/id/{word_id}", response_model=schemas.Word)  
def get_word_by_id_route(
    user_id: str = Path(..., description="단어 소유자 ID"),
    word_id: int = Path(
        ..., description="조회할 단어의 ID"
    ),  
    db: Session = Depends(database.get_db),
):
    db_word = crud.words.get_word_by_id_and_user_id(
        db, word_id=word_id, user_id=user_id
    )

    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="단어를 찾을 수 없습니다."
        )

    try:
        updated_word = crud.words.increment_word_count_atomic(
            db, word_id=db_word.words_id
        )
        if updated_word:
            return updated_word
        else:
            return db_word
    except Exception as e:
        print(f"Error incrementing word count for word_id {db_word.words_id}: {e}")
        return db_word


# 특정 사용자의 단어들을 조회수로 내림차순 정렬하여 반환
@router.get("/count/{user_id}/sort", response_model=List[schemas.Word])
def get_user_words_sorted_by_count(  
    user_id: str = Path(
        ..., description="단어 목록을 조회할 사용자의 ID"
    ),  
    db: Session = Depends(database.get_db),
):
    words = crud.words.get_words_by_user_sorted_by_count(db, user_id=user_id)
    if not words:  
        return []
    return words


# 특정 사용자의 단어들을 생성시간으로 내림차순 정렬하여 반환
@router.get("/created_time/{user_id}/sort", response_model=List[schemas.Word])  
def get_user_words_sorted_by_creation( 
    user_id: str = Path(
        ..., description="단어 목록을 조회할 사용자의 ID"
    ),  
    db: Session = Depends(database.get_db),
):
    words = crud.words.get_words_by_user_sorted_by_created_time(db, user_id=user_id)
    if not words:
        return []
    return words


@router.get(
    "/{word}/relate/open_search",  
    response_model=List[schemas.RelatedWord],
    summary="Get related words using k-NN search",  
    description=(
        "Provides words similar to the input word using k-NN search "
        "on pre-computed embeddings (knn_vector type) stored in OpenSearch."  
    ),
)
def get_related_words_knn(  
    word: str = Path(
        ..., description="The word to find related words for.", min_length=1
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum number of k-nearest neighbors to return.",  
    ),
):
    print("--- k-NN Search Endpoint Called ---")  
    if not embedding_model or not opensearch_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="k-NN search service (RAG) is not available.",  
        )

    print(
        f"Received request for k-NN search for: '{word}' with k: {limit}"
    )
    print(f"Using OpenSearch index: '{OPENSEARCH_INDEX_NAME}' for k-NN search.")

    try:
        query_vector = embedding_model.encode(word)
        print(f"Generated query vector for '{word}', shape: {query_vector.shape}")
    except Exception as e:
        print(f"Error encoding word '{word}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embedding for the word: {str(e)}",
        )
    knn_query_body = {
        "size": limit,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_vector.tolist(),  
                    "k": limit,  
                }
            }
        },
        "_source": [  
            "form",
            "korean_definition",
            "usages",
            "english_definition",
        ],
    }
    try:
        response = opensearch_client.search(
            index=OPENSEARCH_INDEX_NAME,
            body=knn_query_body,  
        )

    except NotFoundError:
        print(f"Error: Index '{OPENSEARCH_INDEX_NAME}' not found during k-NN search.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OpenSearch index '{OPENSEARCH_INDEX_NAME}' not found.",
        )
    except RequestError as e:
        print(f"OpenSearch RequestError during k-NN search: {e.info}")
        error_detail = f"OpenSearch k-NN request error: {str(e)}"
        if (
            e.info
            and "error" in e.info
            and "root_cause" in e.info["error"]
            and e.info["error"]["root_cause"]
        ):
            error_detail = f"OpenSearch k-NN request error: {e.info['error']['root_cause'][0].get('reason', str(e))}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail
        )
    except OpenSearchConnectionError:
        print("Error: Could not connect to OpenSearch during k-NN search.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to OpenSearch. The service may be down.",
        )
    except Exception as e:
        print(f"Unexpected error during OpenSearch k-NN search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during k-NN search: {str(e)}",
        )
    related_words_found: List[schemas.RelatedWord] = []
    if response and "hits" in response and "hits" in response["hits"]:
        for hit in response["hits"]["hits"]:
            source = hit.get("_source", {})
            score = hit.get("_score")
            word_data = schemas.RelatedWord(
                form=source.get("form", "N/A"),
                korean_definition=source.get("korean_definition"),
                usages=source.get("usages"),
                english_definition=source.get("english_definition"),
                score=score,  
            )
            related_words_found.append(word_data)
    else:
        print(
            "No hits found in OpenSearch k-NN search response or response format is unexpected."
        )

    if not related_words_found:
        print(f"No related words found for '{word}' with the current k-NN query.")

    return related_words_found


@router.post("/find-related", response_model=schemas.WordResponse)
async def find_related_words(request_body: schemas.WordRequest):
    """
    주어진 쿼리와 관련된 단어들을 RAG, 웹 검색, LLM을 통해 찾아 반환합니다.
    """
    initial_state = {
        "query": request_body.query,
        "target_word_count": request_body.target_word_count,
    }
    print(f"FastAPI: Received request: {request_body.dict()}")
    print(f"FastAPI: Initial state for graph: {initial_state}")

    try:
        final_output_state = compiled_graph.invoke(initial_state)

        print(f"FastAPI: Graph execution finished. Final state: {final_output_state}")

        if final_output_state.get("error"):  
            raise HTTPException(
                status_code=500,
                detail=f"Graph processing error: {final_output_state.get('error')}",
            )

        return schemas.WordResponse(
            query=final_output_state.get("query", request_body.query),
            final_words=final_output_state.get("final_words", []),
            target_word_count=final_output_state.get(
                "target_word_count", request_body.target_word_count
            ),
            source_counts={
                "rag": final_output_state.get("rag_source_count", 0),
                "web": final_output_state.get("web_source_count", 0),
                "llm": final_output_state.get("llm_source_count", 0),
            },
        )
    except Exception as e:
        import traceback

        traceback.print_exc()  
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


# 범기님 코드 =======================================================================
# 단어 예문 테스트 (사용자 입력 예문 평가)
@router.post("/{word_id}/test_explain")
def test_explain(word_id: int, request: schemas.ExampleEvaluationRequest):
    evaluation = evaluate_user_example(str(word_id), request.sentence)
    return {
        "word_id": word_id,
        "user_sentence": request.sentence,
        "evaluation": evaluation,
    }

# 단어 예문 생성 (AI를 사용하여 예문 생성)
@router.post("/{word}/ai_word_example")
def ai_word_example(word: str):
    examples = generate_examples_with_gpt(word)
    return {"word": word, "examples": examples}


# 윤정님 코드 =======================================================================
# POST 방식 예문 생성
@router.post("/generate", response_model=schemas.ExampleResponse)
async def generate_examples_post(request: schemas.WordRequestAI):
    """
    POST 방식으로 단어에 대한 예문을 생성합니다.
    """
    try:
        result = crud.word_examples.exsen(request.word)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return schemas.ExampleResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


# GET 방식 예문 생성
@router.get("/generate/{word}")
async def generate_examples_get(word: str):
    """
    GET 방식으로 단어에 대한 예문을 생성합니다.
    """
    try:
        result = crud.word_examples.exsen(word)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")


# 윤정님 ===================================================================================
@router.get("/generate-examples/{word_id}/test")
async def generate_examples_get(word_id: int, db: Session = Depends(database.get_db)):
    """
    GET 방식으로 단어 ID를 받아 예문을 생성하는 엔드포인트

    Args:
        word_id: URL 경로에서 받은 단어 ID
        db: 데이터베이스 세션

    Returns:
        dict: 생성된 예문과 결과 정보
    """
    result = bring_exsen(word_id, db)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result



# LLM 관련 임포트 (여기에 추가)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
import re
from langchain_openai import ChatOpenAI
import json

prompt = ChatPromptTemplate.from_template(
    """
"{word}"라는 단어의 뜻은 다음과 같습니다: {explanation}.
이 뜻을 기반으로 의미적으로 유사하지만 서로 다른 한국어 단어 5개를 추천해 주세요.
형태는 JSON 리스트로만 응답해 주세요. 예: ["단어1", "단어2", ...]
"""
)

llm = ChatOpenAI(
    model=LLM_GENERATE_MODEL,
    temperature=LLM_GENERATE_TEMP,
    api_key=OPENAI_API_KEY if OPENAI_API_KEY else None,
)
chain: Runnable = prompt | llm


@router.get("/words/{word_name}/related")
def get_related_words(word_name: str, db: Session = Depends(database.get_db)):
    explanation = crud.words.get_word_explanation_by_name(db, word_name)
    if not explanation:
        raise HTTPException(
            status_code=404, detail="해당 단어 설명을 찾을 수 없습니다."
        )

    result = chain.invoke({"word": word_name, "explanation": explanation})
    raw_output = getattr(result, "content", str(result))

    # 마크다운 코드 블록 제거
    json_text = re.sub(r"```json|```", "", raw_output).strip()

    try:
        related_words = json.loads(json_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 결과 파싱 실패: {e}")

    return {"related_words": related_words}



from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


class WordRequest(BaseModel):
    word: str

class ExampleResponse(BaseModel):
    word: str
    easy_meaning: str
    success: bool
    message: str = ""

def easy_min(word: str) -> dict:
    """
    단어의 뜻을 아주 쉽게 설명하는 함수
    
    Args:
        word (str): 뜻을 생성할 단어
        
    Returns:
        dict: 결과를 포함한 딕셔너리
    """
    try:
        if not word or word.strip() == "":
            return {
                "success": False,
                "message": "단어를 입력해주세요.",
                "word": word,
                "easy_meaning": ""
            }

        prompt = ChatPromptTemplate.from_messages([
            ("system", 
            f"""
    사용자가 제공한 단어의 정확한 사전적 의미만을 참고하여, 그 뜻을 초등학생 수준에 맞춰 가장 쉽고 명확하게 설명하십시오.

엄격한 제약 조건:

1. 절대 예시나 문맥을 사용하지 마십시오. 오직 단어의 뜻 자체만을 설명해야 합니다.
2. 부가적인 내용이나 사족을 어떠한 경우에도 넣지 마십시오.
3. 친근하거나 대화체인 말투는 일체 사용하지 마십시오. 특히, '~의미해', '~있어', '~단어야', '~하는 거야', '예를 들어' 와 같은 표현은 절대 금지합니다.
4. 존댓말을 사용하지 마십시오.
5. 사전이나 백과사전에서 정의를 내릴 때 사용하는 방식처럼 격식 있고 간결한 어투를 사용하십시오.
6. 단어에 동음이의어가 하나라도 존재한다면, 반드시 모든 의미를 빠짐없이 나열하여 설명하십시오. 단 하나의 의미라도 빠뜨리는 것을 금지합니다.(예: 1. 과일의 일종으로...열매. \n2. 물 위에 ...사용)
7. 초등학생이 이해할 수 있도록 어려운 한자어나 전문 용어는 피하고 일상적인 언어로 설명하십시오.
8. 설명하고자 하는 단어를 반복적으로 사용하지 마십시오. 특히, 문장이나 문단 시작 시 해당 단어의 반복 사용을 엄격히 금지합니다.
9. 다음과 같은 구조의 문장 사용을 금지합니다: '단어는/는 ...이다' (예: 배는 ...이다).
10. 설명 외에 부가적인 정보나 묘사를 추가하지 마십시오. 정의 그 자체에 집중하십시오.

우선순위:

위에 제시된 '엄격한 제약 조건'들을 최우선으로 따르십시오. '쉽게 설명'하는 것은 언어 선택과 개념의 단순화에 한정되며, 말투나 형식에 대한 제약 조건을 위반해서는 안 됩니다.
    """),
    ('human', '{input}'),
])

        llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0,
            max_tokens=500, 
        )

        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"input": word})
        
        return {
            "success": True,
            "message": "쉬운 단어 설명 생성 완료",
            "word": word,
            "easy_meaning": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"오류가 발생했습니다: {str(e)}",
            "word": word,
            "easy_meaning": ""
        }

# GET 방식 쉬운 뜻 생성
@router.get("/generate/{word}/easy")
async def generate_examples_get(word: str):
    """
    GET 방식으로 단어에 대한 쉬운 뜻을 생성합니다.
    """
    try:
        result = easy_min(word)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

