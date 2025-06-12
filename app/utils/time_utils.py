from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)


def get_local_time(tz: str = "Australia/Sydney") -> datetime:
    """
    Get current time in local timezone
    Parameters:
        tz (str): The timezone to use. Default is "Australia/Sydney"
    Returns:
        datetime: The current time in the local timezone
    """

    local_tz = pytz.timezone(tz)

    return datetime.now(local_tz)


def parse_message_date(date_str: str, tz: str = "Australia/Sydney") -> datetime | None:
    """
    Parse the MessageDate string to datetime object with timezone.

    Example:
        "2025-06-11T10:00:00"

    Returns:
        datetime: The datetime object with timezone
    """
    try:
        local_tz = pytz.timezone(tz)
        return local_tz.localize(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S"))
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing date {date_str}: {e}")
        return None
