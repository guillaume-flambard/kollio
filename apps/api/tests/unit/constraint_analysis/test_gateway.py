import pytest

from src.modules.constraint_analysis.adapters.litellm import LiteLLMConstraintAnalysisGateway
from src.modules.constraint_analysis.agent.pipeline import run_constraint_pipeline
from src.platform.config import Settings
from src.platform.locale import UnsupportedLocaleError


async def test_pipeline_rejects_unsupported_locale_before_any_provider_call() -> None:
    settings = Settings(_env_file=None, environment="development", database_url="")
    gateway = LiteLLMConstraintAnalysisGateway(settings)

    with pytest.raises(UnsupportedLocaleError, match="de"):
        await run_constraint_pipeline(
            gateway, title="Title", pitch="Pitch", locale="de", evidence=[], context={}
        )
