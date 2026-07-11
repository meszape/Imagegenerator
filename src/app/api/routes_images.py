from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.storage.db import get_db
from app.storage.repositories import Repository
from app.core.schemas import AssetRead
router=APIRouter()
@router.get('/assets/{asset_id}',response_model=AssetRead)
def get_asset(asset_id:str, db:Session=Depends(get_db)): return Repository(db).get_asset(asset_id)
@router.get('/assets/{asset_id}/file')
def get_file(asset_id:str, db:Session=Depends(get_db)):
    a=Repository(db).get_asset(asset_id); return FileResponse(a.path, media_type=a.mime_type, filename=a.path.split('/')[-1])
