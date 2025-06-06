from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
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
)

from sentence_transformers import SentenceTransformer
from opensearchpy import (
    OpenSearch,
    ConnectionError as OpenSearchConnectionError,
)

from app.langgraph_logic.graph_builder import compiled_graph
from ..crud.word_examples import bring_exsen
embedding_model = None
opensearch_client = None
OPENSEARCH_HOSTS_CONFIG = [
    {"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}
]  
OPENSEARCH_AUTH_CONFIG = (
    (OPENSEARCH_USER, OPENSEARCH_PASSWORD)
    if OPENSEARCH_USER and OPENSEARCH_PASSWORD
    else None
)

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

@router.get("/{user_id}/{word_id}/get_examples",response_model=List[schemas.WordExample],summary="특정 사용자의 특정 단어 ID에 대한 모든 예문(용례) 조회")
def read_examples_for_word_by_id(  
    user_id: str = Path(..., description="단어를 소유한 사용자의 ID"),
    word_id: int = Path(
        ..., description="예문을 조회할 단어의 ID"
    ),  
    db: Session = Depends(database.get_db),
):
    db_word = crud.words.get_word_by_id(db, word_id=word_id)
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {word_id}인 단어를 찾을 수 없습니다.",
        )
    if db_word.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  
            detail=f"사용자 ID '{user_id}'는 ID가 {word_id}인 단어에 접근할 권한이 없습니다.",
        )
    try:
        crud.words.increment_word_count_atomic(db, word_id=db_word.words_id)
    except Exception as e:
        pass  
    examples = crud.words.get_word_examples_by_word_id(db, word_id=db_word.words_id)
    return examples


# 단어별 예문 추가 (기존 코드 스타일 반영)
@router.post("/{word_id}/examples",response_model=schemas.WordExample,status_code=status.HTTP_201_CREATED,summary="특정 단어에 예문(용례) 추가")
def add_example_to_word(example_data: schemas.WordExampleCreate,word_id: int = Path(..., description="예문을 추가할 단어의 ID"),db: Session = Depends(database.get_db)):
    db_word = crud.words.get_word_by_id(db, word_id=word_id)  
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {word_id}인 단어를 찾을 수 없습니다.",
        )
    try:
        created_example = crud.words.create_word_example(
            db=db,
            word_id=db_word.words_id,  
            example_create=example_data,
        )
        return created_example
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예문 추가 중 오류 발생: {str(e)}",
        )


# 단어별 예문 수정
@router.put("/{word_id}/examples/{example_sequence}",response_model=schemas.WordExample,summary="특정 단어의 특정 예문 수정")
def update_word_example_endpoint(  
    word_id: int = Path(..., description="예문이 속한 단어의 ID"),
    example_sequence: int = Path(..., description="수정할 예문의 시퀀스 번호"),
    example_update_data: schemas.WordExampleUpdate = Body(...),  
    db: Session = Depends(database.get_db),
):
    db_word = crud.words.get_word_by_id(db, word_id=word_id)
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {word_id}인 단어를 찾을 수 없습니다.",
        )
    db_example = crud.word_examples.get_word_example_by_ids(
        db, word_id=word_id, example_sequence=example_sequence
    )
    if not db_example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"단어 ID {word_id}에 시퀀스 번호 {example_sequence}인 예문을 찾을 수 없습니다.",
        )
    try:
        updated_example = crud.word_examples.update_word_example(
            db=db, db_example=db_example, example_update_data=example_update_data
        )
        return updated_example
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예문 수정 중 오류 발생: {str(e)}",
        )


# 단어별 예문 삭제
@router.delete(
    "/{word_id}/examples/{example_sequence}",
    response_model=Optional[schemas.WordExample],  
    summary="특정 단어의 특정 예문 삭제",
)
def delete_word_example_endpoint(
    word_id: int = Path(..., description="예문이 속한 단어의 ID"),
    example_sequence: int = Path(..., description="삭제할 예문의 시퀀스 번호"),
    db: Session = Depends(database.get_db),
):
    db_word = crud.words.get_word_by_id(db, word_id=word_id)
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {word_id}인 단어를 찾을 수 없습니다.",
        )
    db_example = crud.word_examples.get_word_example_by_ids(  
        db, word_id=word_id, example_sequence=example_sequence
    )
    if not db_example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"단어 ID {word_id}에 시퀀스 번호 {example_sequence}인 예문을 찾을 수 없습니다.",
        )
    try:
        deleted_example_data = schemas.WordExample.model_validate(db_example)
        crud.word_examples.delete_word_example(
            db=db, db_example=db_example
        )  
        return deleted_example_data

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예문 삭제 중 오류 발생: {str(e)}",
        )
