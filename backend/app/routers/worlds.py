from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
    Body,
)  
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas, database  
from ..crud import opensearch_crud 

router = APIRouter(
    prefix="/works/{work_id}",  
    tags=["worlds"],
)

# POST /works/{work_id}/worlds/ - 새 세계관 추가
@router.post(
    "/worlds",
    response_model=schemas.World,
    status_code=status.HTTP_201_CREATED,
    summary="특정 작품에 새로운 세계관 추가",
)
def create_world_for_work_route(
    work_id: int = Path(..., description="세계관을 추가할 작품의 ID"),
    world_data: schemas.WorldCreate = Body(...),  
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    try:
        created_world = crud.worlds.create_work_world(
            db=db, work_id=work_id, world_data=world_data
        )
        if created_world and created_world.worlds_content:
            try:
                opensearch_crud.update_opensearch_document_for_world(
                    db, created_world.worlds_id
                )
                print(f"World {created_world.worlds_id} content indexed in OpenSearch.")
            except Exception as os_exc:
                print(
                    f"Error indexing world {created_world.worlds_id} content in OpenSearch: {os_exc}"
                )
        return created_world
    except Exception as e:
        print(f"Error creating world for work {work_id}: {e}")  
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세계관 추가 중 오류 발생: {str(e)}",
        )


# GET /works/{work_id}/worlds/ - 해당 작품의 모든 세계관 조회
@router.get(
    "/worlds",
    response_model=List[schemas.World],
    summary="특정 작품의 모든 세계관 목록 조회",
)
def read_worlds_for_work_route(
    work_id: int = Path(..., description="세계관 목록을 조회할 작품의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    worlds_list = crud.worlds.get_worlds_by_work_id(db=db, work_id=work_id)
    return worlds_list


# GET /works/{work_id}/worlds/{world_id} - 특정 세계관 조회
@router.get(
    "/worlds/{world_id}",
    response_model=schemas.World,
    summary="특정 작품의 특정 세계관 상세 정보 조회",
)
def read_world_route(
    work_id: int = Path(..., description="세계관이 속한 작품의 ID"),
    world_id: int = Path(..., description="조회할 세계관의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    db_world = crud.worlds.get_world_by_id_and_work_id(
        db=db, work_id=work_id, world_id=world_id
    )
    if db_world is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {work_id}에 ID가 {world_id}인 세계관을 찾을 수 없습니다.",
        )
    return db_world


# PUT /works/{work_id}/worlds/{world_id} - 특정 세계관 정보 수정
@router.put(
    "/worlds/{world_id}",
    response_model=schemas.World,
    summary="특정 작품의 특정 세계관 정보 수정",
)
def update_world_route(
    work_id: int = Path(..., description="세계관이 속한 작품의 ID"),
    world_id: int = Path(..., description="수정할 세계관의 ID"),
    world_update_data: schemas.WorldUpdate = Body(...),  
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    db_world_to_update = crud.worlds.get_world_by_id_and_work_id(
        db=db, work_id=work_id, world_id=world_id
    )
    if not db_world_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"수정할 세계관 ID {world_id}를 작품 ID {work_id}에서 찾을 수 없습니다.",
        )

    updated_world = crud.worlds.update_world(
        db=db, world_id=world_id, world_update_data=world_update_data
    )
    if updated_world is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"세계관 ID {world_id} 업데이트에 실패했습니다.",
        )

    content_updated_in_request = False
    if hasattr(world_update_data, "model_fields_set"):  
        if "worlds_content" in world_update_data.model_fields_set:
            content_updated_in_request = True
    elif hasattr(world_update_data, "__fields_set__"):  
        if "worlds_content" in world_update_data.__fields_set__:
            content_updated_in_request = True
    else:
        if (
            world_update_data.worlds_content is not None
        ):
            content_updated_in_request = True

    if (
        content_updated_in_request
    ):  
        try:
            opensearch_crud.update_opensearch_document_for_world(
                db, updated_world.worlds_id
            )
            print(f"World {updated_world.worlds_id} content updated in OpenSearch.")
        except Exception as os_exc:
            print(
                f"Error updating world {updated_world.worlds_id} content in OpenSearch: {os_exc}"
            )

    return updated_world


# DELETE /works/{work_id}/worlds/{world_id} - 특정 세계관 삭제
@router.delete(
    "/worlds/{world_id}",
    response_model=Optional[schemas.World],
    summary="특정 작품의 특정 세계관 삭제",
)
def delete_world_route(
    work_id: int = Path(..., description="세계관이 속한 작품의 ID"),
    world_id: int = Path(..., description="삭제할 세계관의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    db_world_to_delete = crud.worlds.get_world_by_id_and_work_id(
        db=db, work_id=work_id, world_id=world_id
    )
    if not db_world_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"삭제할 세계관 ID {world_id}를 작품 ID {work_id}에서 찾을 수 없습니다.",
        )
        
    deleted_world_info = crud.worlds.delete_world(db=db, world_id=world_id)
    if deleted_world_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"세계관 ID {world_id} 삭제에 실패했습니다.",
        )

    opensearch_doc_id = f"world_{world_id}"
    try:
        opensearch_crud.delete_opensearch_document(opensearch_doc_id)
        print(f"World document {opensearch_doc_id} deleted from OpenSearch.")
    except Exception as os_exc:
        print(
            f"Error deleting world document {opensearch_doc_id} from OpenSearch: {os_exc}"
        )

    return deleted_world_info
