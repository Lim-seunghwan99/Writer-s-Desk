from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas  


def create_work_episode(
    db: Session, work_id: int, episode_data: schemas.EpisodeCreate
) -> models.Episode:
    """
    특정 작품(work_id)에 새로운 에피소드를 생성합니다.
    """
    db_episode = models.Episode(
        works_id=work_id,
        episode_content=episode_data.episode_content,  
    )
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode


def get_episodes_by_work_id(db: Session, work_id: int) -> List[models.Episode]:
    """
    특정 작품(work_id)에 속한 모든 에피소드 목록을 조회합니다.
    """
    return db.query(models.Episode).filter(models.Episode.works_id == work_id).all()


def get_episode_by_id_and_work_id(
    db: Session, work_id: int, episode_id: int
) -> Optional[models.Episode]:
    """
    특정 작품(work_id)에 속한 특정 에피소드(episode_id)를 조회합니다.
    삭제나 수정 전에 해당 작품의 에피소드가 맞는지 확인하는 데 사용할 수 있습니다.
    """
    return (
        db.query(models.Episode)
        .filter(
            models.Episode.episode_id == episode_id, models.Episode.works_id == work_id
        )
        .first()
    )


def get_episode_by_work_and_episode_id(
    db: Session, work_id: int, episode_id: int
) -> Optional[models.Episode]:
    """
    주어진 work_id와 episode_id에 해당하는 특정 에피소드를 조회합니다.
    """
    return (
        db.query(models.Episode)
        .filter(
            models.Episode.works_id == work_id, models.Episode.episode_id == episode_id
        )
        .first()
    )


def update_episode_content(
    db: Session, work_id: int, episode_id: int, content: str
) -> Optional[models.Episode]:
    """
    특정 작품(work_id)의 특정 에피소드(episode_id)의 내용(content)을 수정합니다.
    """
    db_episode = get_episode_by_id_and_work_id(
        db, work_id=work_id, episode_id=episode_id
    )
    if not db_episode:
        return None

    db_episode.episode_content = content
    db.commit()
    db.refresh(db_episode)
    return db_episode


def delete_episode_by_id_and_work_id(
    db: Session, work_id: int, episode_id: int
) -> Optional[models.Episode]:
    """
    특정 작품(work_id)의 특정 에피소드(episode_id)를 삭제합니다.
    삭제 성공 시 삭제된 에피소드 객체를 (세션에서 분리된 상태로) 반환하거나,
    단순히 성공 여부를 나타내는 값을 반환할 수 있습니다.
    """
    db_episode = get_episode_by_id_and_work_id(
        db, work_id=work_id, episode_id=episode_id
    )
    if not db_episode:
        return None 

    db.delete(db_episode)
    db.commit()
    return db_episode  


def update_episode_ai_generated_content(
    db: Session, episode_id: int, new_ai_content: str
) -> Optional[models.Episode]:
    db_episode = (
        db.query(models.Episode).filter(models.Episode.episode_id == episode_id).first()
    )
    if db_episode:
        db_episode.episode_content = (
            new_ai_content  
        )
        db.add(db_episode)
        db.commit()
        db.refresh(db_episode)
        return db_episode
    return None


from ..models import Episode as EpisodeModel  

EPISODE_DESCRIPTION_TAG_START = "[에피소드 설명]"
GENERATED_DIALOGUE_TAG_START = "[생성된 대사]"
CONTENT_SEPARATOR = "\n\n"


def format_episode_content_for_db(episode_description: str, llm_dialogue: str) -> str:
    """episode_description과 llm_dialogue를 결합하여 DB에 저장할 문자열로 포맷합니다."""
    return (
        f"{EPISODE_DESCRIPTION_TAG_START}\n{episode_description}"
        f"{CONTENT_SEPARATOR}"
        f"{GENERATED_DIALOGUE_TAG_START}\n{llm_dialogue}"
    )


def parse_episode_content_from_db(
    db_content: str,
) -> tuple[Optional[str], Optional[str]]:
    """DB에 저장된 content에서 episode_description과 llm_dialogue를 분리합니다."""
    description = None
    dialogue = None

    try:
        if (
            EPISODE_DESCRIPTION_TAG_START in db_content
            and GENERATED_DIALOGUE_TAG_START in db_content
        ):
            desc_start_index = db_content.find(EPISODE_DESCRIPTION_TAG_START) + len(
                EPISODE_DESCRIPTION_TAG_START
            )
            dialogue_tag_index_for_desc_end = db_content.find(
                GENERATED_DIALOGUE_TAG_START
            )
            actual_desc_end_index = db_content.rfind(
                CONTENT_SEPARATOR, desc_start_index, dialogue_tag_index_for_desc_end
            )
            if actual_desc_end_index != -1:
                description = db_content[desc_start_index:actual_desc_end_index].strip()
            else:
                description = db_content[
                    desc_start_index:dialogue_tag_index_for_desc_end
                ].strip()

            dialogue_start_index = db_content.find(GENERATED_DIALOGUE_TAG_START) + len(
                GENERATED_DIALOGUE_TAG_START
            )
            dialogue = db_content[dialogue_start_index:].strip()

        elif (
            EPISODE_DESCRIPTION_TAG_START in db_content
        ):  
            desc_start_index = db_content.find(EPISODE_DESCRIPTION_TAG_START) + len(
                EPISODE_DESCRIPTION_TAG_START
            )
            description = db_content[
                desc_start_index:
            ].strip()

        elif GENERATED_DIALOGUE_TAG_START in db_content:  
            dialogue_start_index = db_content.find(GENERATED_DIALOGUE_TAG_START) + len(
                GENERATED_DIALOGUE_TAG_START
            )
            dialogue = db_content[dialogue_start_index:].strip()

        else:  
            dialogue = db_content.strip()

    except Exception as e:
        print(f"Error parsing episode content: {e}. Content: '{db_content[:100]}...'")

        if not dialogue:
            dialogue = db_content  

    return description, dialogue


def create_ai_generated_episode(
    db: Session,
    works_id: int,
    llm_generated_dialogue: str,  
    episode_description: str,  
) -> EpisodeModel:  

    combined_content = format_episode_content_for_db(
        episode_description, llm_generated_dialogue
    )

    db_episode_obj = EpisodeModel(
        works_id=works_id,
        episode_content=combined_content,
    )
    db.add(db_episode_obj)
    db.commit()
    db.refresh(db_episode_obj)
    return db_episode_obj  


def update_ai_generated_content_by_id(
    db: Session,
    episode_id: int,
    new_llm_dialogue: str, 
) -> Optional[EpisodeModel]:
    db_episode = (
        db.query(EpisodeModel).filter(EpisodeModel.episode_id == episode_id).first()
    )
    if db_episode:
        original_description, _ = parse_episode_content_from_db(
            db_episode.episode_content
        )

        if original_description is None:
            print(
                f"Warning: Original episode description not found in episode_id {episode_id}. Updating with new dialogue only."
            )
        
            db_episode.episode_content = format_episode_content_for_db(
                original_description or "원본 설명 없음",  
                new_llm_dialogue,
            )

        else:
            db_episode.episode_content = format_episode_content_for_db(
                original_description, new_llm_dialogue
            )

        db.commit()
        db.refresh(db_episode)
        return db_episode
    return None


# work_id까지 검증하는 버전
def update_episode_content_by_ids(
    db: Session, work_id: int, episode_id: int, new_llm_dialogue: str
) -> Optional[EpisodeModel]:
    db_episode = (
        db.query(EpisodeModel)
        .filter(EpisodeModel.works_id == work_id, EpisodeModel.episode_id == episode_id)
        .first()
    )
    if db_episode:
        original_description, _ = parse_episode_content_from_db(
            db_episode.episode_content
        )

        if original_description is None:
            print(
                f"Warning: Original episode description not found in work_id {work_id}, episode_id {episode_id}. Using placeholder."
            )
            final_description = "원본 설명 없음"  
        else:
            final_description = original_description

        db_episode.episode_content = format_episode_content_for_db(
            final_description, new_llm_dialogue
        )
        db.commit()
        db.refresh(db_episode)
        return db_episode
    return None


def get_episode_by_ids(
    db: Session, work_id: int, episode_id: int
) -> Optional[models.Episode]:
    """
    특정 작품(work_id)에 속한 특정 에피소드(episode_id)를 조회합니다.
    """
    return (
        db.query(models.Episode)
        .filter(
            models.Episode.episode_id == episode_id, models.Episode.works_id == work_id
        )
        .first()
    )
