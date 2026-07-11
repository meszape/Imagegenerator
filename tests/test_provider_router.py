from app.core.enums import Provider
from app.core.provider_router import ProviderRouter
from app.core.exceptions import ProviderTemporaryError
from app.providers.base import ImageProviderAdapter, ProviderCapabilities
class A(ImageProviderAdapter):
    provider=Provider.openai
    def create_initial_image(self,*a,**k): pass
    def continue_image_turn(self,*a,**k): pass
    def get_capabilities(self): return ProviderCapabilities(self.provider,True,False,False,False,False,False,[])
def test_capabilities_and_fallback():
    r=ProviderRouter({Provider.openai:A()}, True)
    assert 'openai' in r.capabilities(); assert r.can_fallback(ProviderTemporaryError('x'), Provider.gemini)
