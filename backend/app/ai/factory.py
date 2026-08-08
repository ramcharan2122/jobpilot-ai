from app.core.config import settings
from app.ai.base import AIProvider
from app.ai.smart_mock import SmartMockAIProvider

def get_ai_provider() -> AIProvider:
    # Always default to SmartMockAIProvider if API keys are absent or SMART_MOCK selected
    provider_name = settings.AI_PROVIDER.upper()
    if provider_name == "SMART_MOCK" or not settings.AI_API_KEY:
        return SmartMockAIProvider()
    
    # Can extend with OpenAIProvider or GeminiProvider if API keys are provided
    return SmartMockAIProvider()
