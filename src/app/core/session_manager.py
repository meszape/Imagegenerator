from app.config import get_settings
from app.core.enums import Provider
from app.core.models import SessionModel
from app.core.schemas import SessionCreate
from app.storage.repositories import Repository
from app.utils.ids import new_id
class SessionManager:
    def __init__(self, repo:Repository): self.repo=repo
    def create(self, req:SessionCreate):
        settings=get_settings()
        model=req.model or (settings.default_openai_model if req.provider==Provider.openai else settings.default_gemini_model)
        return self.repo.add_session(SessionModel(session_id=new_id('sess'),provider=req.provider.value,model=model,default_safety_profile=req.default_safety_profile.value,provider_config=req.provider_config,current_status='active'))
