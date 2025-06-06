from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import models, schemas
from fastapi import HTTPException


# 유저별 단어 추가
def create_user_word(db: Session, word_data: schemas.WordCreate):
    db_word = get_word_by_name_and_user(
        db, word_name=word_data.word_name, user_id=word_data.user_id
    )
    if db_word:
        raise HTTPException(status_code=400, detail="Word already exists for this user")

    db_word = models.Word(
        user_id=word_data.user_id,
        word_name=word_data.word_name,
        word_content=word_data.word_content,
    )
    db.add(db_word)
    db.flush()  

    if word_data.examples:
        for i, example_data in enumerate(word_data.examples):
            db_example = models.WordExample(
                words_id=db_word.words_id,  
                example_sequence=i + 1,  
                word_example_content=example_data.word_example_content,
            )
            db.add(db_example)

    db.commit()
    db.refresh(db_word)
    return db_word


# --- Word CRUD (예문 추가 시 단어 조회용) ---
def get_word_by_id_and_user_id(
    db: Session, word_id: int, user_id: str
) -> Optional[models.Word]:
    """특정 사용자의 특정 단어를 ID로 조회합니다."""
    return (
        db.query(models.Word)
        .filter(models.Word.words_id == word_id, models.Word.user_id == user_id)
        .first()
    )


# 단어 이름으로 단어 조회
def get_word_by_name_and_user(db: Session, word_name: str, user_id: str):
    return (
        db.query(models.Word)
        .filter(models.Word.word_name == word_name, models.Word.user_id == user_id)
        .first()
    )


# 특정 단어를 메인key로 조회
def get_word_by_id(db: Session, word_id: int):
    return db.query(models.Word).filter(models.Word.words_id == word_id).first()


# 단어 삭제
def delete_word(db: Session, word_id: int):
    word = db.query(models.Word).filter(models.Word.words_id == word_id).first()
    if word:
        db.delete(word)
        db.commit()
        return word
    return None


# 단어 이름으로 단어 조회
def get_word_by_name(db: Session, word_name: str):
    return db.query(models.Word).filter(models.Word.word_name == word_name).first()


# 단어 예문 추가
def create_word_example(
    db: Session,
    word_id: int,
    example_create: schemas.WordExampleCreate,
) -> models.WordExample:
    """
    특정 단어(word_id)에 대한 새 예문(WordExample)을 생성합니다.
    example_sequence는 자동으로 다음 순번으로 할당됩니다.
    """
    
    last_sequence = (
        db.query(func.max(models.WordExample.example_sequence))
        .filter(models.WordExample.words_id == word_id)
        .scalar()
    )

    next_sequence = (last_sequence + 1) if last_sequence is not None else 1

    db_example = models.WordExample(
        words_id=word_id,
        example_sequence=next_sequence,
        word_example_content=example_create.word_example_content,
    )
    db.add(db_example)
    try:
        db.commit()
        db.refresh(db_example)
    except Exception as e:
        db.rollback()
        raise e  
    return db_example


# 단어 예문 조회
def get_word_examples_by_word_id(db: Session, word_id: int) -> List[models.WordExample]:
    """특정 단어에 속한 모든 예문을 조회합니다."""
    return (
        db.query(models.WordExample)
        .filter(models.WordExample.words_id == word_id)
        .order_by(models.WordExample.example_sequence)
        .all()
    )


# 단어 카운트 수로 정렬
def get_words_by_user_sorted_by_count(db: Session, user_id: str):
    return (
        db.query(models.Word)
        .filter(models.Word.user_id == user_id)
        .order_by(models.Word.word_count.desc())
        .all()
    )


# 단어 생성 시간으로 정렬
def get_words_by_user_sorted_by_created_time(db: Session, user_id: str):
    return (
        db.query(models.Word)
        .filter(models.Word.user_id == user_id)
        .order_by(models.Word.word_created_time.desc())
        .all()
    )


def increment_word_count_atomic(db: Session, word_id: int):
    db_word = db.query(models.Word).filter(models.Word.words_id == word_id).first()
    if db_word:
        if db_word.word_count is None:
            db.query(models.Word).filter(models.Word.words_id == word_id).update(
                {models.Word.word_count: 1}, synchronize_session=False
            )
        else:
            db.query(models.Word).filter(models.Word.words_id == word_id).update(
                {models.Word.word_count: models.Word.word_count + 1},
                synchronize_session=False,
            )

        db.commit()
        db.refresh(db_word)
        return db_word
    return None


def get_word_explanation_by_name(db: Session, word_name: str) -> Optional[str]:
    word = db.query(models.Word).filter(models.Word.word_name == word_name).first()
    return word.word_content if word else None