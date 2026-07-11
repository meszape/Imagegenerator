from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.storage.db import get_db
from app.storage.repositories import Repository
from app.core.session_manager import SessionManager
from app.core.schemas import SessionCreate, SessionRead, TurnRead, GenerateRequest, GenerateResponse, AssetRead
from app.dependencies import get_router
from app.services.image_service import ImageService
from app.storage.asset_store import AssetStore
from app.config import get_settings
router=APIRouter()
@router.post('/sessions',response_model=SessionRead)
def create_session(req:SessionCreate, db:Session=Depends(get_db)): return SessionManager(Repository(db)).create(req)
@router.get('/sessions/{session_id}',response_model=SessionRead)
def get_session(session_id:str, db:Session=Depends(get_db)): return Repository(db).get_session(session_id)
@router.get('/sessions/{session_id}/turns',response_model=list[TurnRead])
def turns(session_id:str, db:Session=Depends(get_db)): repo=Repository(db); repo.get_session(session_id); return repo.list_turns(session_id)
@router.post('/sessions/{session_id}/generate',response_model=GenerateResponse)
def generate(session_id:str, req:GenerateRequest, db:Session=Depends(get_db)):
    turn,assets,provider,fb,orig=ImageService(Repository(db),get_router(),AssetStore(get_settings().asset_root)).generate(session_id,req)
    return GenerateResponse(session_id=session_id,turn=turn,assets=assets,provider=provider,fallback_attempted=fb,original_error=orig)
@router.post('/sessions/{session_id}/edit',response_model=GenerateResponse)
def edit(session_id:str, req:GenerateRequest, db:Session=Depends(get_db)): return generate(session_id,req,db)
@router.get('/sessions/{session_id}/assets',response_model=list[AssetRead])
def assets(session_id:str, db:Session=Depends(get_db)): repo=Repository(db); repo.get_session(session_id); return repo.list_assets(session_id)
@router.get('/providers/capabilities')
def capabilities(): return get_router().capabilities()
