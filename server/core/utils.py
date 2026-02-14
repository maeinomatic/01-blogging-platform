"""Shared utility functions."""
from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """Get current UTC datetime without timezone info (naive datetime).
    
    Used for database fields that store timestamps without timezone information.
    For JWT tokens and other timezone-aware operations, use datetime.now(timezone.utc) directly.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
