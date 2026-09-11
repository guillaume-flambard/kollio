from pathlib import Path

import litellm
import yaml


def test_qwen_recorded_request_has_nonzero_cost_accounting():
    config_path = Path(__file__).parents[4] / "infra" / "litellm" / "config.yaml"
    config = yaml.safe_load(config_path.read_text())
    deployment = next(
        item for item in config["model_list"] if item["model_name"] == "kollio-default"
    )
    pricing = deployment["model_info"]
    litellm.register_model(
        {
            "openai/qwen3.8-flash": {
                "litellm_provider": "openai",
                "mode": "chat",
                **pricing,
            }
        }
    )

    cost = litellm.completion_cost(
        model="openai/qwen3.8-flash",
        prompt="A recorded request with input tokens",
        completion="A recorded structured response with output tokens",
    )

    assert cost > 0
    assert deployment["litellm_params"]["max_budget"] == 1
    assert deployment["litellm_params"]["budget_duration"] == "1d"
    assert config["litellm_settings"]["max_budget"] == 1
