from app.core.enums import Provider
from app.core.exceptions import AppError, ProviderRateLimitError, ProviderSafetyBlockedError, ProviderTemporaryError
from app.providers.base import ImageProviderAdapter
class ProviderRouter:
    def __init__(self, adapters:dict[Provider,ImageProviderAdapter], enable_fallback:bool=False): self.adapters=adapters; self.enable_fallback=enable_fallback
    def get(self, provider:Provider): return self.adapters[Provider(provider)]
    def capabilities(self): return {p.value:a.get_capabilities().__dict__ for p,a in self.adapters.items()}
    def can_fallback(self, exc:Exception, fallback_provider:Provider|None): return bool(fallback_provider and (self.enable_fallback or fallback_provider) and isinstance(exc,(ProviderRateLimitError,ProviderTemporaryError,ProviderSafetyBlockedError)))
