import pytest

from src.modules.constraint_analysis.adapters.litellm import LiteLLMConstraintAnalysisGateway
from src.platform.config import Settings
from src.platform.locale import UnsupportedLocaleError


async def test_gateway_rejects_unsupported_locale_before_any_provider_call() -> None:
    settings = Settings(_env_file=None, environment="development", database_url="")
    gateway = LiteLLMConstraintAnalysisGateway(settings)

    with pytest.raises(UnsupportedLocaleError, match="de"):
        await gateway.analyze(title="Title", pitch="Pitch", locale="de", evidence=[])
