# app/routers/plannings.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas, database

router = APIRouter(
    prefix="/works/{work_id}", 
    tags=["plannings"], 
)


# POST /works/{work_id}/plannings/ - 새 플랜 추가
@router.post(
    "/plannings",
    response_model=schemas.Planning,
    status_code=status.HTTP_201_CREATED,
    summary="특정 작품에 새로운 플랜(기획) 추가",
)
def create_planning_for_work_route(
    work_id: int = Path(..., description="플랜을 추가할 작품의 ID"),
    *,
    planning_data: schemas.PlanningCreate,
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id) 
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    try:
        created_planning = crud.plannings.create_work_planning(
            db=db, work_id=work_id, planning_data=planning_data
        )
        return created_planning
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"플랜 추가 중 오류 발생: {str(e)}"
        )


# GET /works/{work_id}/plannings/ - 해당 작품의 모든 플랜 조회
@router.get(
    "/plannings",
    response_model=List[schemas.Planning],
    summary="특정 작품의 모든 플랜(기획) 목록 조회",
)
def read_plannings_for_work_route(
    work_id: int = Path(..., description="플랜 목록을 조회할 작품의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    plannings_list = crud.plannings.get_plannings_by_work_id(
        db=db, work_id=work_id
    )
    return plannings_list


# GET /works/{work_id}/plannings/{plan_id} - 특정 플랜 조회
@router.get(
    "/plannings/{plan_id}",
    response_model=schemas.Planning,
    summary="특정 작품의 특정 플랜(기획) 상세 정보 조회",
)
def read_planning_route(
    work_id: int = Path(..., description="플랜이 속한 작품의 ID"),
    plan_id: int = Path(..., description="조회할 플랜의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    db_planning = crud.plannings.get_planning_by_id_and_work_id(
        db=db, work_id=work_id, plan_id=plan_id
    )
    if db_planning is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {work_id}에 ID가 {plan_id}인 플랜을 찾을 수 없습니다."
        )
    return db_planning


# PUT /works/{work_id}/plannings/{plan_id} - 특정 플랜 정보 수정
@router.put(
    "/plannings/{plan_id}",
    response_model=schemas.Planning,
    summary="특정 작품의 특정 플랜(기획) 정보 수정",
)
def update_planning_route(
    work_id: int = Path(..., description="플랜이 속한 작품의 ID"),
    plan_id: int = Path(..., description="수정할 플랜의 ID"),
    *,
    planning_update_data: schemas.PlanningUpdate,
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    db_planning_to_update = crud.plannings.get_planning_by_id_and_work_id(
        db=db, work_id=work_id, plan_id=plan_id
    )
    if not db_planning_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"수정할 플랜 ID {plan_id}를 작품 ID {work_id}에서 찾을 수 없습니다."
        )
    updated_planning = crud.plannings.update_planning(
        db=db, plan_id=plan_id, planning_update_data=planning_update_data
    )
    if updated_planning is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"플랜 ID {plan_id} 업데이트에 실패했습니다."
        )
    return updated_planning


# DELETE /works/{work_id}/plannings/{plan_id} - 특정 플랜 삭제
@router.delete(
    "/plannings/{plan_id}",
    response_model=Optional[schemas.Planning],  
    summary="특정 작품의 특정 플랜(기획) 삭제",
)
def delete_planning_route(
    work_id: int = Path(..., description="플랜이 속한 작품의 ID"),
    plan_id: int = Path(..., description="삭제할 플랜의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    db_planning_to_delete = crud.plannings.get_planning_by_id_and_work_id(
        db=db, work_id=work_id, plan_id=plan_id
    )
    if not db_planning_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"삭제할 플랜 ID {plan_id}를 작품 ID {work_id}에서 찾을 수 없습니다."
        )
    deleted_planning_info = crud.plannings.delete_planning(db=db, plan_id=plan_id)
    if deleted_planning_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"플랜 ID {plan_id} 삭제에 실패했습니다."
        )
    return deleted_planning_info
