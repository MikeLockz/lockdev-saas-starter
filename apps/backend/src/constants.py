"""
Application constants for timezone support and other global settings.
"""

# Default timezone for organizations
DEFAULT_TIMEZONE = "America/New_York"

# List of supported IANA timezone identifiers
# Grouped by region for frontend display
SUPPORTED_TIMEZONES: list[str] = [
    # US Timezones
    "America/New_York",  # Eastern
    "America/Chicago",  # Central
    "America/Denver",  # Mountain
    "America/Phoenix",  # Arizona (no DST)
    "America/Los_Angeles",  # Pacific
    "America/Anchorage",  # Alaska
    "Pacific/Honolulu",  # Hawaii
    # Canada
    "America/Toronto",
    "America/Vancouver",
    "America/Edmonton",
    "America/Halifax",
    # Europe
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Europe/Madrid",
    "Europe/Rome",
    "Europe/Amsterdam",
    "Europe/Brussels",
    "Europe/Vienna",
    "Europe/Warsaw",
    "Europe/Stockholm",
    "Europe/Athens",
    # Asia Pacific
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Hong_Kong",
    "Asia/Singapore",
    "Asia/Seoul",
    "Asia/Kolkata",
    "Asia/Dubai",
    "Australia/Sydney",
    "Australia/Melbourne",
    "Australia/Perth",
    "Pacific/Auckland",
    # Latin America
    "America/Mexico_City",
    "America/Sao_Paulo",
    "America/Buenos_Aires",
    "America/Santiago",
    "America/Bogota",
    "America/Lima",
    # Africa / Middle East
    "Africa/Cairo",
    "Africa/Johannesburg",
    "Africa/Lagos",
    "Asia/Jerusalem",
    "Asia/Riyadh",
    # UTC
    "UTC",
]

# Timezone display names for UI (IANA -> Friendly name)
TIMEZONE_DISPLAY_NAMES = {
    "America/New_York": "Eastern Time (ET)",
    "America/Chicago": "Central Time (CT)",
    "America/Denver": "Mountain Time (MT)",
    "America/Phoenix": "Arizona Time",
    "America/Los_Angeles": "Pacific Time (PT)",
    "America/Anchorage": "Alaska Time",
    "Pacific/Honolulu": "Hawaii Time",
    "Europe/London": "London (GMT/BST)",
    "Europe/Paris": "Paris (CET/CEST)",
    "Europe/Berlin": "Berlin (CET/CEST)",
    "Asia/Tokyo": "Tokyo (JST)",
    "Asia/Shanghai": "Shanghai (CST)",
    "Asia/Singapore": "Singapore (SGT)",
    "Australia/Sydney": "Sydney (AEST/AEDT)",
    "UTC": "UTC",
}
