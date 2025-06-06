from fastapi import APIRouter, Depends, HTTPException, Path, status, Body
from sqlalchemy.orm import Session
from typing import List
from ..crud import dialogue_generator  
from .. import (
    crud,
    models,
    schemas,
    database,
)  

router = APIRouter(
    prefix="/works",  
    tags=["works"],  
)


# POST /works - 작품 추가
@router.post(
    "/",  
    response_model=schemas.Work,
    status_code=status.HTTP_201_CREATED,
    summary="새로운 작품 추가 (기본 정보만)",
)
def create_work(
    work_data: schemas.WorkCreate,
    db: Session = Depends(database.get_db),
):
    db_user = crud.users.get_user_by_id(db, user_id=work_data.user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID '{work_data.user_id}'를 찾을 수 없습니다. 작품을 생성할 수 없습니다.",
        )

    try:
        created_work = crud.works.create_user_work(db=db, work_data=work_data)
        return created_work
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"작품 추가 중 오류 발생: {str(e)}",
        )


# GET /works/{user_id}/user_works - 특정 사용자의 모든 작품 목록 조회
@router.get(
    "/{user_id}/user_works",
    response_model=List[schemas.Work],  
    summary="특정 사용자의 모든 작품 목록 조회",
)
def get_user_works(
    user_id: str = Path(..., description="작품 목록을 조회할 사용자의 ID"),
    db: Session = Depends(database.get_db),
):
    try:
        user_works = crud.works.get_works_by_user_id(db=db, user_id=user_id)
        if not user_works:
            return []  
        return user_works
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 작품 목록 조회 중 오류 발생: {str(e)}",
        )


# GET /works/{work_id}/work - 개별 작품 확인
@router.get(
    "/{work_id}/work", 
    response_model=schemas.Work,
    summary="ID로 개별 작품 상세 정보 조회",
)
def get_work_by_id(
    work_id: int = Path(
        ..., description="조회할 작품의 ID"
    ),
    db: Session = Depends(database.get_db),
):
    try:
        db_work = crud.works.get_work_by_id(db=db, work_id=work_id)
        if not db_work:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
            )
        return db_work
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"작품 조회 중 오류 발생: {str(e)}",
        )


# DELETE /works/{work_id} - 작품 삭제
@router.delete(
    "/{work_id}",
    response_model=schemas.Work,
    summary="ID로 특정 작품 삭제",
)
def delete_work_by_id(
    work_id: int = Path(..., description="삭제할 작품의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work_to_delete = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    try:
        deleted_work = crud.works.delete_work_by_id(db=db, work_id=work_id)
        return deleted_work
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"작품 삭제 중 오류 발생: {str(e)}",
        )


# PUT /works/{work_id}/update_work - 작품 정보 수정
@router.put(
    "/{work_id}/update_work",
    response_model=schemas.Work,
    summary="ID로 특정 작품의 제목 수정",
)
def update_work_title(
    work_id: int = Path(..., description="수정할 작품의 ID"),
    *,
    work_update: schemas.WorkUpdate,  
    db: Session = Depends(database.get_db),
):
    updated_work = crud.works.update_work(
        db=db, work_id=work_id, work_update_data=work_update
    )
    if not updated_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없거나 업데이트에 실패했습니다.",
        )
    return updated_work


# POST /works/{work_id}/generate-dialogue - 작품 정보를 바탕으로 AI 대사 생성
@router.post(
    "/{work_id}/generate-dialogue-with-context",  
    response_model=schemas.DialogueResponse,
    summary="DB에서 작품 컨텍스트를 조회하여 AI 대사 생성",
)
async def generate_dialogue_with_context_route(
    work_id: int = Path(..., description="대사를 생성할 작품 ID"),
    request: schemas.DialogueGenerationRequest = Body(
        ..., description="대사 생성 요청 본문 (컨텍스트 ID 포함)"
    ),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    worlds_content_data = (
        db_work.worlds_content
        if hasattr(db_work, "worlds_content")
        else "세계관 정보 없음"
    )
    episode_content_data = "에피소드 정보 없음"
    if request.context_ids.episode_id is not None:
        db_episode = (
            crud.episodes.get_episode_by_id_and_work_id(  
                db, work_id=work_id, episode_id=request.context_ids.episode_id
            )
        )
        if not db_episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작품 ID {work_id}에 에피소드 ID {request.context_ids.episode_id}를 찾을 수 없습니다.",
            )
        episode_content_data = (
            db_episode.episode_content
            if hasattr(db_episode, "episode_content")
            else "에피소드 내용 없음"
        )
    character_settings_data = "캐릭터 설정 정보 없음"
    if request.context_ids.character_id is not None:
        if hasattr(crud, "characters") and hasattr(
            crud.characters, "get_character_by_id_and_work_id"
        ):
            db_character = crud.characters.get_character_by_id_and_work_id(
                db, work_id=work_id, character_id=request.context_ids.character_id
            )
            if not db_character:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"작품 ID {work_id}에 캐릭터 ID {request.context_ids.character_id}를 찾을 수 없습니다.",
                )
            character_settings_data = (
                db_character.character_settings
                if hasattr(db_character, "character_settings")
                else "캐릭터 설정 없음"
            )
        else:
            print(
                f"Warning: crud.characters.get_character_by_id_and_work_id function not found. Skipping character settings."
            )
    plan_content_data = "스토리 계획 정보 없음"
    if request.context_ids.plan_id is not None:
        db_plan = (
            crud.plannings.get_planning_by_id_and_work_id(  
                db, work_id=work_id, plan_id=request.context_ids.plan_id
            )
        )
        if not db_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작품 ID {work_id}에 계획 ID {request.context_ids.plan_id}를 찾을 수 없습니다.",
            )
        plan_content_data = (
            db_plan.plan_content
            if hasattr(db_plan, "plan_content")
            else "스토리 계획 내용 없음"
        )
    try:
        generated_text = dialogue_generator.generate_dialogue_from_context(
            worlds_content=worlds_content_data,
            episode_content=episode_content_data,
            character_settings=character_settings_data,
            plan_content=plan_content_data,
            prompt=request.prompt,
        )
        return schemas.DialogueResponse(
            generated_dialogue=generated_text
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대사 생성 중 오류 발생: {str(e)}",
        )
