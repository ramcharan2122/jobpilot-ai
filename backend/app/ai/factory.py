from app.core.config import settings
from app.ai.base import AIProvider
from app.ai.smart_mock import SmartMockAIProvider
from app.ai.gemini_provider import GeminiProvider

def get_ai_provider() -> AIProvider:
    provider_name = settings.AI_PROVIDER.upper()
    if provider_name == "GEMINI" and settings.AI_API_KEY:
        return GeminiProvider()
    elif settings.AI_API_KEY and provider_name != "SMART_MOCK":
        return GeminiProvider()
    return SmartMockAIProvider()
