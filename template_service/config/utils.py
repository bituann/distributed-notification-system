def get_attr(exc: Exception, attr: str, default=None):
    if hasattr(exc, attr):
        value = getattr(exc, attr)
        return value
    return default


def get_status_code(exc: Exception, default: int = 500) -> int:
    status = getattr(exc, "status_code", None)
    if isinstance(status, int) and 100 <= status <= 599:
        return status
    return default
