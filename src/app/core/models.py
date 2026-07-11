from datetime import datetime, UTC
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
class Base(DeclarativeBase): pass
def now(): return datetime.now(UTC)
class SessionModel(Base):
    __tablename__='sessions'
    session_id:Mapped[str]=mapped_column(String,primary_key=True); provider:Mapped[str]=mapped_column(String,index=True); model:Mapped[str]=mapped_column(String)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,index=True); updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
    default_safety_profile:Mapped[str]=mapped_column(String); provider_config:Mapped[dict]=mapped_column(JSON,default=dict); current_status:Mapped[str]=mapped_column(String,default='active')
    turns=relationship('TurnModel',back_populates='session',cascade='all, delete-orphan')
class TurnModel(Base):
    __tablename__='turns'; id:Mapped[int]=mapped_column(Integer,primary_key=True)
    turn_id:Mapped[str]=mapped_column(String,unique=True,index=True); session_id:Mapped[str]=mapped_column(ForeignKey('sessions.session_id'),index=True)
    turn_index:Mapped[int]=mapped_column(Integer); user_prompt:Mapped[str]=mapped_column(Text); normalized_instruction:Mapped[str]=mapped_column(Text)
    provider_request_payload:Mapped[dict]=mapped_column(JSON,default=dict); provider_response_payload:Mapped[dict]=mapped_column(JSON,default=dict)
    provider_response_id:Mapped[str|None]=mapped_column(String,index=True); previous_provider_response_id:Mapped[str|None]=mapped_column(String)
    safety_profile_used:Mapped[str]=mapped_column(String); block_status:Mapped[str]=mapped_column(String,default='none'); block_reason:Mapped[str|None]=mapped_column(String); revised_prompt:Mapped[str|None]=mapped_column(Text)
    output_assets:Mapped[list]=mapped_column(JSON,default=list); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,index=True)
    session=relationship('SessionModel',back_populates='turns')
    __table_args__=(Index('ix_turn_session_idx','session_id','turn_index'),)
class AssetModel(Base):
    __tablename__='assets'; asset_id:Mapped[str]=mapped_column(String,primary_key=True); session_id:Mapped[str]=mapped_column(String,index=True); turn_id:Mapped[str]=mapped_column(String,index=True)
    turn_index:Mapped[int]=mapped_column(Integer); path:Mapped[str]=mapped_column(String); metadata_path:Mapped[str]=mapped_column(String)
    sha256:Mapped[str]=mapped_column(String); width:Mapped[int|None]=mapped_column(Integer); height:Mapped[int|None]=mapped_column(Integer); mime_type:Mapped[str]=mapped_column(String)
    provider:Mapped[str]=mapped_column(String); model:Mapped[str]=mapped_column(String); provider_ids:Mapped[dict]=mapped_column(JSON,default=dict); prompt_info:Mapped[dict]=mapped_column(JSON,default=dict); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,index=True)
