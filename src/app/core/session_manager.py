from app.core.enums import Provider
from app.core.models import SessionModel
from app.core.schemas import SessionCreate
from app.storage.repositories import Repository
from app.utils.ids import new_id
class SessionManager:
    def __init__(self, repo:Repository): self.repo=repo
    def create(self, req:SessionCreate):
        model=req.model or ('gpt-image-1' if req.provider==Provider.openai else 'gemini-2.5-flash-image-preview')
        return self.repo.add_session(SessionModel(session_id=new_id('sess'),provider=req.provider.value,model=model,default_safety_profile=req.default_safety_profile.value,provider_config=req.provider_config,current_status='active'))
