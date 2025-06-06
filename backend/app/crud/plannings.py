# app/crud/plannings.py

from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas


def get_planning_by_id(db: Session, plan_id: int) -> Optional[models.Planning]:
    """
    플랜 ID로 특정 플랜을 조회합니다.
    """
    return db.query(models.Planning).filter(models.Planning.plan_id == plan_id).first()


def get_planning_by_id_and_work_id(
    db: Session, work_id: int, plan_id: int
) -> Optional[models.Planning]:
    """
    작품 ID와 플랜 ID로 특정 플랜을 조회합니다.
    (해당 작품에 속한 플랜인지 확인용)
    """
    return (
        db.query(models.Planning)
        .filter(models.Planning.plan_id == plan_id, models.Planning.works_id == work_id)
        .first()
    )


def get_plannings_by_work_id(
    db: Session, work_id: int
) -> List[models.Planning]:
    """
    특정 작품 ID에 속한 모든 플랜 목록을 조회합니다 (페이지네이션 지원).
    """
    return (
        db.query(models.Planning)
        .filter(models.Planning.works_id == work_id)
        .all()
    )


def create_work_planning(
    db: Session, work_id: int, planning_data: schemas.PlanningCreate
) -> models.Planning:
    """
    특정 작품(work_id)에 새로운 플랜을 생성합니다.
    """
    db_planning = models.Planning(
        works_id=work_id,
        plan_title=planning_data.plan_title,
        plan_content=planning_data.plan_content,
    )
    db.add(db_planning)
    db.commit()
    db.refresh(db_planning)
    return db_planning


def update_planning(
    db: Session, plan_id: int, planning_update_data: schemas.PlanningUpdate
) -> Optional[models.Planning]:
    """
    특정 플랜 ID의 정보를 수정합니다.
    """
    db_planning = get_planning_by_id(db, plan_id=plan_id)  
    if not db_planning:
        return None 

    update_data = planning_update_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_planning, key):
            setattr(db_planning, key, value)

    db.commit()
    db.refresh(db_planning)
    return db_planning


def delete_planning(db: Session, plan_id: int) -> Optional[models.Planning]:
    """
    특정 플랜 ID의 플랜을 삭제합니다.
    """
    db_planning = get_planning_by_id(db, plan_id=plan_id) 
    if not db_planning:
        return None  

    db.delete(db_planning)
    db.commit()
    return db_planning 
