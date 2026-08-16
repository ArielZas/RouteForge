def time_string_to_seconds(value: str) -> int:
    """Convert a clock time to seconds after midnight."""
    parts = value.split(":")
    if len(parts) not in (2, 3):
        raise ValueError("time must use HH:MM or HH:MM:SS format")

    try:
        hour, minute = int(parts[0]), int(parts[1])
        second = int(parts[2]) if len(parts) == 3 else 0
    except ValueError as error:
        raise ValueError("time must contain only numbers") from error

    if not 0 <= hour <= 23 or not 0 <= minute <= 59 or not 0 <= second <= 59:
        raise ValueError("time is outside the valid 24-hour range")

    return hour * 3600 + minute * 60 + second


def seconds_to_time_string(value: int) -> str:
    """Convert seconds after midnight to a clock time."""
    if not 0 <= value < 86_400:
        raise ValueError("seconds from midnight must be between 0 and 86399")

    hour, remainder = divmod(value, 3600)
    minute, second = divmod(remainder, 60)
    return f"{hour:02d}:{minute:02d}:{second:02d}"
