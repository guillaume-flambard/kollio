import json as jsonlib

from src.modules.constraint_analysis.adapters.litellm import LiteLLMConstraintAnalysisGateway
from src.modules.constraint_analysis.agent.pipeline import run_constraint_pipeline
from src.modules.constraint_analysis.domain.models import ConstraintAnalysisResult
from src.platform.config import Settings
from src.platform.llm import Gateway
from src.platform.task_class import TaskClass, intelligence_tier, resolve_model

_FACTOR_NAMES = ("competition", "build_cost", "time_to_market", "defensibility", "acquisition")


def _settings(**overrides: object) -> Settings:
    base: dict[str, object] = {
        "_env_file": None,
        "environment": "development",
        "database_url": "",
        "llm_api_key": "test-key",
        "llm_model": "cheap-model",
    }
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


def _abstention(locale: str = "fr") -> dict[str, object]:
    return {
        "overall_score": None,
        "verdict": "unknown",
        "summary": "Insufficient evidence.",
        "factors": [
            {
                "name": name,
                "basis": "unknown",
                "score": None,
                "gap": "The evidence needed to score this is missing.",
                "summary": "Unknown.",
                "source_ids": [],
            }
            for name in _FACTOR_NAMES
        ],
        "contradictions": [],
        "locale": locale,
    }


class _FakeResponse:
    def __init__(self, content: str):
        self._content = content

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return {"choices": [{"message": {"content": self._content}}]}


class _QueueClient:
    payloads: list[dict] = []
    queue: list[str] = []
    timeouts: list[object] = []

    def __init__(self, *args: object, **kwargs: object):
        self.timeouts.append(kwargs.get("timeout"))
        return None

    async def __aenter__(self) -> _QueueClient:
        return self

    async def __aexit__(self, *exc: object) -> bool:
        return False

    async def post(self, url: str, json: dict | None = None, headers: dict | None = None):
        self.payloads.append(json or {})
        return _FakeResponse(self.queue.pop(0))


def test_visible_classes_resolve_to_the_premium_model() -> None:
    settings = _settings(llm_model_visible="premium-model")
    assert resolve_model(settings, TaskClass.REASONING) == "premium-model"
    assert resolve_model(settings, TaskClass.CHALLENGE) == "premium-model"


def test_commodity_classes_do_not() -> None:
    settings = _settings(llm_model_visible="premium-model")
    for commodity in (TaskClass.EXTRACTION, TaskClass.EMBEDDING, TaskClass.TRANSLATION):
        assert intelligence_tier(commodity) == "commodity"
        assert resolve_model(settings, commodity) == "cheap-model"


def test_visible_falls_back_to_the_default_without_premium_credentials() -> None:
    settings = _settings()
    assert resolve_model(settings, TaskClass.REASONING) == "cheap-model"


def test_gateways_declare_a_visible_task_class() -> None:
    assert intelligence_tier(LiteLLMConstraintAnalysisGateway.task_class) == "visible"
    assert intelligence_tier(Gateway.task_class) == "visible"


async def test_pipeline_routes_analyst_cheap_and_the_rest_premium(monkeypatch) -> None:
    monkeypatch.setattr("src.platform.llm_chat.httpx.AsyncClient", _QueueClient)
    _QueueClient.payloads = []
    _QueueClient.queue = [
        jsonlib.dumps({"arguments": ["Pilot demand is real"]}),
        jsonlib.dumps({"risks": ["Cannot staff onboarding"], "missing_evidence": []}),
        jsonlib.dumps({"facts": [], "speculation": ["Assumes willingness to pay"]}),
        jsonlib.dumps({"supports": [], "conflicts": []}),
        jsonlib.dumps(_abstention()),
    ]
    settings = _settings(llm_model="cheap-model", llm_model_visible="premium-model")
    gateway = LiteLLMConstraintAnalysisGateway(settings)
    run = await run_constraint_pipeline(
        gateway,
        title="Offline field app",
        pitch="Works without signal",
        locale="fr",
        evidence=[],
        context={},
    )
    assert isinstance(run.result, ConstraintAnalysisResult)
    models = [payload["model"] for payload in _QueueClient.payloads]
    assert models[0] == "cheap-model"  # analyst: commodity
    assert models[1:] == ["premium-model"] * 4  # challenger, critic, company fit, synthesizer
    assert len(_QueueClient.queue) == 0


async def test_analysis_payload_disables_thinking(monkeypatch) -> None:
    monkeypatch.setattr("src.platform.llm_chat.httpx.AsyncClient", _QueueClient)
    _QueueClient.payloads = []
    _QueueClient.timeouts = []
    _QueueClient.queue = [
        jsonlib.dumps({"arguments": ["Pilot demand is real"]}),
        jsonlib.dumps({"risks": ["Cannot staff onboarding"], "missing_evidence": []}),
        jsonlib.dumps({"facts": [], "speculation": ["Assumes willingness to pay"]}),
        jsonlib.dumps({"supports": [], "conflicts": []}),
        jsonlib.dumps(_abstention()),
    ]
    settings = _settings(llm_model_visible="premium-model", llm_request_timeout_seconds=512.0)
    gateway = LiteLLMConstraintAnalysisGateway(settings)
    run = await run_constraint_pipeline(
        gateway,
        title="Offline field app",
        pitch="Works without signal",
        locale="fr",
        evidence=[],
        context={},
    )

    assert isinstance(run.result, ConstraintAnalysisResult)
    assert len(_QueueClient.payloads) == 5
    for payload in _QueueClient.payloads:
        assert payload["enable_thinking"] is False
        assert payload["response_format"]["json_schema"]["strict"] is True
    assert _QueueClient.timeouts == [512.0] * 5
