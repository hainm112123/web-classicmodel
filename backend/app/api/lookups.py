from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analytics import get_lookups

router = APIRouter(prefix="/lookups", tags=["lookups"])


@router.get("")
def lookups(db: Session = Depends(get_db)):
    return get_lookups(db)

