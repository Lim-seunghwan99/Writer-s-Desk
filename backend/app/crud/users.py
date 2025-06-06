from sqlalchemy.orm import Session
from typing import Optional
from .. import models, schemas

def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.user_id == user_id).first()
