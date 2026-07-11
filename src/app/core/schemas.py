from typing import Any
from pydantic import BaseModel, Field
from app.core.enums import Provider, SafetyProfile
class SessionCreate(BaseModel):
    provider:Provider; model:str|None=None; default_safety_profile:SafetyProfile=SafetyProfile.balanced; provider_config:dict[str,Any]=Field(default_factory=dict)
class SessionRead(BaseModel):
    session_id:str; provider:str; model:str; default_safety_profile:str; provider_config:dict[str,Any]; current_status:str; created_at:Any; updated_at:Any
    class Config: from_attributes=True
class GenerateRequest(BaseModel):
    prompt:str; safety_profile:SafetyProfile|None=None; custom_safety_settings:dict[str,str]|None=None; fallback_provider:Provider|None=None; output_format:str|None='png'; metadata:dict[str,Any]=Field(default_factory=dict)
class AssetRead(BaseModel):
    asset_id:str; session_id:str; turn_id:str; turn_index:int; sha256:str; width:int|None; height:int|None; mime_type:str; provider:str; model:str; provider_ids:dict[str,Any]; prompt_info:dict[str,Any]; created_at:Any
    class Config: from_attributes=True
class TurnRead(BaseModel):
    turn_id:str; session_id:str; turn_index:int; user_prompt:str; normalized_instruction:str; provider_request_payload:dict[str,Any]; provider_response_payload:dict[str,Any]; provider_response_id:str|None; previous_provider_response_id:str|None; safety_profile_used:str; block_status:str; block_reason:str|None; revised_prompt:str|None; output_assets:list[Any]; created_at:Any
    class Config: from_attributes=True
class GenerateResponse(BaseModel):
    session_id:str; turn:TurnRead; assets:list[AssetRead]; provider:str; fallback_attempted:bool=False; original_error:dict[str,Any]|None=None
class ErrorResponse(BaseModel): code:str; message:str; provider:str|None=None; details:dict[str,Any]|None=None
