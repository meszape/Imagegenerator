from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.enums import Provider, SafetyProfile
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file='.env', extra='ignore')
    openai_api_key:str|None=None; gemini_api_key:str|None=None
    database_url:str='sqlite:///./data/image_service.db'; asset_root:str='./data/assets'
    log_level:str='INFO'; default_provider:Provider=Provider.openai
    default_openai_model:str='gpt-image-1'; default_gemini_model:str='gemini-2.5-flash-image-preview'
    default_safety_profile:SafetyProfile=SafetyProfile.balanced; enable_fallback:bool=False
    max_turn_context:int=6; request_timeout_seconds:int=120; log_prompts:bool=False
@lru_cache
def get_settings()->Settings: return Settings()
