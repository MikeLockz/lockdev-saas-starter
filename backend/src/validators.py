"""
Validation helpers for API inputs.
"""
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from src.constants import SUPPORTED_TIMEZONES


def validate_timezone(tz: str) -> bool:
    """
    Validate that a timezone string is a valid IANA timezone identifier.
    
    Args:
        tz: Timezone string to validate (e.g., "America/New_York")
        
    Returns:
        True if valid and in supported list, False otherwise
    """
    if tz not in SUPPORTED_TIMEZONES:
        return False
    
    try:
        ZoneInfo(tz)
        return True
    except ZoneInfoNotFoundError:
        return False
