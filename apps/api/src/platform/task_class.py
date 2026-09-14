"""Named LLM task classes and the config-driven model they resolve to.

Every gateway call declares the class of work it is doing. A class maps to a
configured model, so routing premium models to the reasoning a member reads is
a configuration choice, not call sites guessing model names.

Commodity intelligence is cheap work that only has to be correct (extraction,
classification, summarising, embeddings, translation, reformatting, field
detection, routing, small checks). Visible intelligence is the reasoning a
member judges the product through (challenging, spotting what was missed,
reasoning over company constraints, contradiction, comparison, recommendation,
drawing a learning, explaining a wrong decision).
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from src.platform.config import Settings


class TaskClass(StrEnum):
    # Commodity intelligence.
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    SUMMARISATION = "summarisation"
    EMBEDDING = "embedding"
    TRANSLATION = "translation"
    ROUTING = "routing"
    SMALL_CHECK = "small_check"
    # Visible intelligence.
    CHALLENGE = "challenge"
    REASONING = "reasoning"
    CONTRADICTION = "contradiction"
    COMPARISON = "comparison"
    RECOMMENDATION = "recommendation"
    LEARNING = "learning"
    EXPLANATION = "explanation"


COMMODITY_CLASSES: frozenset[TaskClass] = frozenset(
    {
        TaskClass.EXTRACTION,
        TaskClass.CLASSIFICATION,
        TaskClass.SUMMARISATION,
        TaskClass.EMBEDDING,
        TaskClass.TRANSLATION,
        TaskClass.ROUTING,
        TaskClass.SMALL_CHECK,
    }
)

TIER = Literal["commodity", "visible"]


def intelligence_tier(task_class: TaskClass) -> TIER:
    return "commodity" if task_class in COMMODITY_CLASSES else "visible"


def resolve_model(settings: Settings, task_class: TaskClass) -> str:
    """The configured model for a task class: commodity uses the default,
    visible uses the premium model when one is configured. Defaults are equal,
    so local development and CI run the whole loop without premium credentials.
    """
    if intelligence_tier(task_class) == "visible":
        return settings.llm_model_visible or settings.llm_model
    return settings.llm_model
