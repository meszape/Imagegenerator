from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.models import SessionModel, TurnModel, AssetModel
from app.core.exceptions import SessionNotFoundError, AssetNotFoundError
class Repository:
    def __init__(self, db:Session): self.db=db
    def add_session(self,s): self.db.add(s); self.db.commit(); self.db.refresh(s); return s
    def get_session(self,session_id):
        s=self.db.get(SessionModel,session_id)
        if not s: raise SessionNotFoundError(f'session {session_id} not found')
        return s
    def next_turn_index(self,session_id): return (self.db.scalar(select(func.max(TurnModel.turn_index)).where(TurnModel.session_id==session_id)) or 0)+1
    def add_turn(self,t): self.db.add(t); self.db.commit(); self.db.refresh(t); return t
    def list_turns(self,session_id): return list(self.db.scalars(select(TurnModel).where(TurnModel.session_id==session_id).order_by(TurnModel.turn_index)))
    def last_provider_response_id(self,session_id,provider):
        t=self.db.scalars(select(TurnModel).where(TurnModel.session_id==session_id,TurnModel.provider_response_id.is_not(None)).order_by(TurnModel.turn_index.desc())).first(); return t.provider_response_id if t else None
    def add_asset(self,a): self.db.add(a); self.db.commit(); self.db.refresh(a); return a
    def list_assets(self,session_id): return list(self.db.scalars(select(AssetModel).where(AssetModel.session_id==session_id).order_by(AssetModel.created_at)))
    def get_asset(self,asset_id):
        a=self.db.get(AssetModel,asset_id)
        if not a: raise AssetNotFoundError(f'asset {asset_id} not found')
        return a
