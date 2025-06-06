from langchain_openai import ChatOpenAI  
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from app.config import OPENAI_API_KEY, AI_UTILS_MODEL
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, Optional
from langchain.schema.output_parser import StrOutputParser
from .. import crud, models, schemas, database
from sqlalchemy.orm import Session
import os
from fastapi import HTTPException

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    print("Warning: OPENAI_API_KEY is not set. Dialogue generation will not work.")
    client = None


def exsen(word: str) -> dict:
    """
    단어를 통해 예문을 만드는 함수

    Args:
        word (str): 예문을 생성할 단어

    Returns:
        dict: 결과를 포함한 딕셔너리
    """
    try:
        if not word or word.strip() == "":
            return {
                "success": False,
                "message": "단어를 입력해주세요.",
                "word": word,
                "examples": "",
            }

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "사용자가 제공한 단어와 관련된 다양한 예문 5개를 길지 않게 생성하라. "
                    "각 예문은 서로 다른 구조와 어휘와 형용사형 전성 어미, 동사형 접미사를 사용하여 해당 단어의 다양한 활용형을 포함해야 한다. "
                    "예문의 내용을 설명하지 말 것. "
                    "사용자가 제공한 단어 부분을 볼드체로 하라. "
                    "글머리를 넣지 마라. "
                    "부가적인 요소를 추가하지 마라.",
                ),
                ("human", "{input}"),
            ]
        )

        llm = ChatOpenAI(
            model=AI_UTILS_MODEL, 
            temperature=0.8,
            max_tokens=500,
        )

        chain = prompt | llm | StrOutputParser()

        result = chain.invoke({"input": word})

        return {
            "success": True,
            "message": "예문 생성 완료",
            "word": word,
            "examples": result,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"오류가 발생했습니다: {str(e)}",
            "word": word,
            "examples": "",
        }


def bring_exsen(word_id: int, db: Session) -> Dict[str, Any]:
    """
    단어ID를 통해 예문을 만드는 함수

    Args:
        word_id (int): 예문을 생성할 단어의 ID
        db (Session): 데이터베이스 세션

    Returns:
        dict: 결과를 포함한 딕셔너리
    """
    try:
        if not os.getenv("OPENAI_API_KEY"):
            return {
                "success": False,
                "message": "OPENAI_API_KEY 환경변수가 설정되지 않았습니다.",
                "word": "",
                "examples": "",
            }

        word = db.query(models.Word).filter(models.Word.words_id == word_id).first()

        if not word:
            raise HTTPException(
                status_code=404,
                detail=f"ID {word_id}에 해당하는 단어를 찾을 수 없습니다.",
            )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""'{word.word_name}'와 관련된 다양한 예문 5개를 길지 않게 생성하라.
            각 예문은 서로 다른 구조와 어휘와 형용사형 전성 어미, 동사형 접미사를 사용하여 해당 단어의 다양한 활용형을 포함해야 한다.
            예문의 내용을 설명하지 말 것.
            사용자가 제공한 단어 부분을 볼드체로 하라.
            글머리를 넣지 마라.
            부가적인 요소를 추가하지 마라.
            한국어로 생성해.""",
                )
            ]
        )

        llm = ChatOpenAI(
            model=AI_UTILS_MODEL,
            temperature=0.8,
            max_tokens=500,
        )

        chain = prompt | llm | StrOutputParser()

        result = chain.invoke({"word": word.word_name})

        return {
            "success": True,
            "message": "예문 생성 완료",
            "word": word.word_name,
            "examples": result,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"오류가 발생했습니다: {str(e)}",
            "word": "",
            "examples": "",
        }


def get_word_example_by_ids(
    db: Session, word_id: int, example_sequence: int
) -> Optional[models.WordExample]:
    """
    특정 단어 ID와 예문 시퀀스 번호로 단일 예문을 조회합니다.
    """
    return (
        db.query(models.WordExample)
        .filter(
            models.WordExample.words_id == word_id,
            models.WordExample.example_sequence == example_sequence,
        )
        .first()
    )


def update_word_example(
    db: Session,
    db_example: models.WordExample,  
    example_update_data: schemas.WordExampleUpdate,  
) -> models.WordExample:
    """
    주어진 예문 객체의 내용을 업데이트합니다.
    """
    update_data = example_update_data.dict(exclude_unset=True)  

    for key, value in update_data.items():
        setattr(db_example, key, value)

    db.add(
        db_example
    ) 
    db.commit()
    db.refresh(db_example)
    return db_example


def delete_word_example(db: Session, db_example: models.WordExample) -> None:
    """
    주어진 예문 객체를 DB에서 삭제합니다.
    """
    db.delete(db_example)
    db.commit()
    return None 
