import os  # 필요시
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Body,
    status,
    Query,
)
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas, database
from ..crud import opensearch_crud  
router = APIRouter(
    prefix="/works/{work_id}", 
    tags=["characters"], 
)


# POST /works/{work_id}/characters/ - 새 캐릭터 추가
@router.post("/characters", response_model=schemas.Character, status_code=status.HTTP_201_CREATED, summary="특정 작품에 새로운 캐릭터 추가")
def create_character_for_work_route(
    work_id: int = Path(..., description="캐릭터를 추가할 작품의 ID"),
    character_data: schemas.CharacterCreate = Body(...),  
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    try:
        created_character = crud.characters.create_work_character(
            db=db, work_id=work_id, character=character_data
        )
        if created_character and created_character.character_settings:
            try:
                opensearch_crud.update_opensearch_document_for_character(
                    db, created_character.character_id
                )
                print(
                    f"Character {created_character.character_id} settings indexed in OpenSearch."
                )
            except Exception as os_exc:
                print(
                    f"Error indexing character {created_character.character_id} settings in OpenSearch: {os_exc}"
                )

        return created_character
    except Exception as e:
        print(f"Error creating character for work {work_id}: {e}")  
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"캐릭터 추가 중 오류 발생: {str(e)}",
        )


# GET /works/{work_id}/characters/ - 해당 작품의 모든 캐릭터 조회
@router.get("/characters",response_model=List[schemas.Character],summary="특정 작품의 모든 캐릭터 목록 조회")
def read_characters_for_work_route(
    work_id: int = Path(..., description="캐릭터 목록을 조회할 작품의 ID"),
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=200, description="반환할 최대 항목 수"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    characters_list = crud.characters.get_characters_by_work_id(
        db=db, work_id=work_id, skip=skip, limit=limit
    )
    return characters_list


# GET /works/{work_id}/characters/{character_id} - 특정 캐릭터 조회
@router.get("/characters/{character_id}", response_model=schemas.Character,summary="특정 작품의 특정 캐릭터 상세 정보 조회")
def read_character_route(
    work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
    character_id: int = Path(..., description="조회할 캐릭터의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    db_character = crud.characters.get_character_by_id_and_work_id(
        db=db, work_id=work_id, character_id=character_id
    )
    if db_character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {work_id}에 ID가 {character_id}인 캐릭터를 찾을 수 없습니다.",
        )
    return db_character


# PUT /works/{work_id}/characters/{character_id} - 특정 캐릭터 정보 수정
@router.put("/characters/{character_id}",response_model=schemas.Character,summary="특정 작품의 특정 캐릭터 정보 수정")
def update_character_route(
    work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
    character_id: int = Path(..., description="수정할 캐릭터의 ID"),
    character_update: schemas.CharacterUpdate = Body(...),  # Body 명시
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    db_character_to_update = crud.characters.get_character_by_id_and_work_id(
        db=db, work_id=work_id, character_id=character_id
    )
    if not db_character_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"수정할 캐릭터 ID {character_id}를 작품 ID {work_id}에서 찾을 수 없습니다.",
        )
    updated_character = crud.characters.update_character(
        db=db, character_id=character_id, character_update=character_update
    )
    if updated_character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"캐릭터 ID {character_id} 업데이트에 실패했습니다.",
        )
    settings_updated_in_request = False
    if hasattr(character_update, "model_fields_set"):  
        if "character_settings" in character_update.model_fields_set:
            settings_updated_in_request = True
    elif hasattr(character_update, "__fields_set__"):  
        if "character_settings" in character_update.model_fields_set:
            settings_updated_in_request = True
    else:
        if (
            character_update.character_settings is not None
        ):
            settings_updated_in_request = True

    if (
        settings_updated_in_request
    ):  
        try:
            opensearch_crud.update_opensearch_document_for_character(
                db, updated_character.character_id
            )
            print(
                f"Character {updated_character.character_id} settings updated in OpenSearch."
            )
        except Exception as os_exc:
            print(
                f"Error updating character {updated_character.character_id} settings in OpenSearch: {os_exc}"
            )
    return updated_character


# DELETE /works/{work_id}/characters/{character_id} - 특정 캐릭터 삭제
@router.delete(
    "/characters/{character_id}",  
    response_model=Optional[schemas.Character],
    summary="특정 작품의 특정 캐릭터 삭제",
)
def delete_character_route(
    work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
    character_id: int = Path(..., description="삭제할 캐릭터의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    db_character_to_delete = crud.characters.get_character_by_id_and_work_id(
        db=db, work_id=work_id, character_id=character_id
    )
    if not db_character_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"삭제할 캐릭터 ID {character_id}를 작품 ID {work_id}에서 찾을 수 없습니다.",
        )
    deleted_character_info = crud.characters.delete_character(
        db=db, character_id=character_id
    )
    if deleted_character_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"캐릭터 ID {character_id} 삭제에 실패했습니다.",
        )
    opensearch_doc_id = f"char_{character_id}"
    try:
        opensearch_crud.delete_opensearch_document(opensearch_doc_id)
        print(f"Character document {opensearch_doc_id} deleted from OpenSearch.")
    except Exception as os_exc:
        print(
            f"Error deleting character document {opensearch_doc_id} from OpenSearch: {os_exc}"
        )
    return deleted_character_info
