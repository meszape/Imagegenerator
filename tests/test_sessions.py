import base64
from app.core.enums import Provider
from app.core.provider_router import ProviderRouter
from app.providers.base import ImageProviderAdapter, ProviderCapabilities, ProviderImage, ProviderResult
from app.main import app
from app.dependencies import get_router
from app.storage.db import init_db
class Fake(ImageProviderAdapter):
    provider=Provider.openai
    def create_initial_image(self,*a,**k): return ProviderResult(Provider.openai,'m',{}, {'id':'r'}, 'r', None, [ProviderImage(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR4nGNgYPgPAAEDAQCgAX6XAAAAAElFTkSuQmCC'))])
    def continue_image_turn(self,*a,**k): return self.create_initial_image()
    def get_capabilities(self): return ProviderCapabilities(Provider.openai,True,True,False,False,False,True,[])
def test_create_session_and_asset(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    init_db(); app.dependency_overrides[get_router]=lambda: ProviderRouter({Provider.openai:Fake()},False)
    c=TestClient(app); sid=c.post('/sessions',json={'provider':'openai','model':'m'}).json()['session_id']
    r=c.post(f'/sessions/{sid}/generate',json={'prompt':'a cat'}); assert r.status_code==200
    assert c.get(f'/sessions/{sid}/assets').json()[0]['sha256']
    app.dependency_overrides.clear()
