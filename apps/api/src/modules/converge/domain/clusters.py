class ClusterTitleError(ValueError):
    """Raised when a cluster title is blank."""


def validate_cluster_title(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ClusterTitleError("A cluster needs a title")
    return cleaned
