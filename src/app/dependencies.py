from app.config import get_settings
from app.core.enums import Provider
from app.core.provider_router import ProviderRouter
from app.providers.openai_adapter import OpenAIImageAdapter
from app.providers.gemini_adapter import GeminiImageAdapter
def get_router(): return ProviderRouter({Provider.openai:OpenAIImageAdapter(),Provider.gemini:GeminiImageAdapter()}, get_settings().enable_fallback)
