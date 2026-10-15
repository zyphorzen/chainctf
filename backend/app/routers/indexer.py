from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.indexer_service import sync_events

router = APIRouter(prefix="/indexer", tags=["Blockchain Indexer"])


@router.post("/sync")
def trigger_sync(
    from_block: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    new_events = sync_events(db, from_block=from_block)
    return {
        "status": "success",
        "new_events_indexed": new_events,
    }
