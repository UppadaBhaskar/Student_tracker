from datetime import date, datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def compute_workshop_day(start_date: date, total_days: int, reference: date | None = None) -> int:
    ref = reference or date.today()
    if ref < start_date:
        return 1
    day = (ref - start_date).days + 1
    return max(1, min(day, total_days))
