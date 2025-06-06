# app/crud/worlds.py
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas


def get_world_by_id(db: Session, world_id: int) -> Optional[models.World]:
    """
    세계관 ID로 특정 세계관을 조회합니다.
    """
    return db.query(models.World).filter(models.World.worlds_id == world_id).first()


def get_world_by_id_and_work_id(
    db: Session, work_id: int, world_id: int
) -> Optional[models.World]:
    """
    작품 ID와 세계관 ID로 특정 세계관을 조회합니다.
    (해당 작품에 속한 세계관인지 확인용)
    """
    return (
        db.query(models.World)
        .filter(models.World.worlds_id == world_id, models.World.works_id == work_id)
        .first()
    )


def get_worlds_by_work_id(
    db: Session, work_id: int
) -> List[models.World]:
    """
    특정 작품 ID에 속한 모든 세계관 목록을 조회합니다 (페이지네이션 지원).
    """
    return (
        db.query(models.World)
        .filter(models.World.works_id == work_id)
        .all()
    )


def create_work_world(
    db: Session, work_id: int, world_data: schemas.WorldCreate
) -> models.World:
    """
    특정 작품(work_id)에 새로운 세계관을 생성합니다.
    """
    db_world = models.World(works_id=work_id, worlds_content=world_data.worlds_content)
    db.add(db_world)
    db.commit()
    db.refresh(db_world)
    return db_world


def update_world(
    db: Session, world_id: int, world_update_data: schemas.WorldUpdate
) -> Optional[models.World]:
    """
    특정 세계관 ID의 정보를 수정합니다.
    """
    db_world = get_world_by_id(db, world_id=world_id)
    if not db_world:
        return None

    update_data = world_update_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_world, key):
            setattr(db_world, key, value)

    db.commit()
    db.refresh(db_world)
    return db_world


def delete_world(db: Session, world_id: int) -> Optional[models.World]:
    """
    특정 세계관 ID의 세계관을 삭제합니다.
    """
    db_world = get_world_by_id(db, world_id=world_id)
    if not db_world:
        return None

    db.delete(db_world)
    db.commit()
    return db_world
