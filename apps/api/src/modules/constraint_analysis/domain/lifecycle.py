from enum import StrEnum


class AnalysisStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"
    REVIEW_QUEUED = "review_queued"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


class InvalidAnalysisTransition(ValueError):
    """Raised when an analysis lifecycle transition is not allowed."""


def start_execution(status: AnalysisStatus) -> AnalysisStatus:
    if status not in (
        AnalysisStatus.QUEUED,
        AnalysisStatus.REVIEW_QUEUED,
        AnalysisStatus.RUNNING,
    ):
        raise InvalidAnalysisTransition(f"Cannot execute analysis in {status} status")
    return AnalysisStatus.RUNNING


def await_review(status: AnalysisStatus) -> AnalysisStatus:
    if status is not AnalysisStatus.RUNNING:
        raise InvalidAnalysisTransition(f"Cannot await review from {status} status")
    return AnalysisStatus.AWAITING_REVIEW


def queue_review(status: AnalysisStatus) -> AnalysisStatus:
    if status is not AnalysisStatus.AWAITING_REVIEW:
        raise InvalidAnalysisTransition(f"Cannot review analysis in {status} status")
    return AnalysisStatus.REVIEW_QUEUED


def finish_review(status: AnalysisStatus, approved: bool) -> AnalysisStatus:
    if status is not AnalysisStatus.RUNNING:
        raise InvalidAnalysisTransition(f"Cannot finish review from {status} status")
    return AnalysisStatus.COMPLETED if approved else AnalysisStatus.REJECTED
