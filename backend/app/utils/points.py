from datetime import datetime, timezone


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def calculate_points(
    revealed_at: datetime,
    clicked_at: datetime,
    timer_minutes: int,
    max_points: int,
) -> int:
    revealed_at = _ensure_utc(revealed_at)
    clicked_at = _ensure_utc(clicked_at)
    elapsed_seconds = (clicked_at - revealed_at).total_seconds()
    timer_seconds = timer_minutes * 60
    if elapsed_seconds >= timer_seconds:
        return 0

    interval = timer_seconds / 10
    bucket = int(elapsed_seconds / interval)
    step = max_points / 10
    return int(max_points - bucket * step)


def difficulty_default_points(difficulty: str) -> int:
    return {"easy": 5, "medium": 10, "hard": 20}.get(difficulty, 10)
