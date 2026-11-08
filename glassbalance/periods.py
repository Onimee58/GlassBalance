"""Date-range presets and in/out/net totals. Pure functions; never alter ledger data."""
from __future__ import annotations

from datetime import date, timedelta

PRESETS = ("This month", "Last month", "Last 3 months", "This year", "Last year", "All time", "Custom range")


def _month_start(d: date) -> date:
    return d.replace(day=1)


def _add_months(d: date, months: int) -> date:
    year, month = divmod(d.month - 1 + months, 12)
    return date(d.year + year, month + 1, 1)


def preset_range(name: str, today: date | None = None) -> tuple[date | None, date | None]:
    """Inclusive (start, end). (None, None) means all time. Custom is handled by the caller."""
    today = today or date.today()
    if name == "This month":
        return _month_start(today), today
    if name == "Last month":
        first = _add_months(_month_start(today), -1)
        return first, _month_start(today) - timedelta(days=1)
    if name == "Last 3 months":            # this month plus the two before it
        return _add_months(_month_start(today), -2), today
    if name == "This year":
        return date(today.year, 1, 1), today
    if name == "Last year":
        return date(today.year - 1, 1, 1), date(today.year - 1, 12, 31)
    if name == "All time":
        return None, None
    raise ValueError(f"Unknown period: {name}")


def normalize(start: date | None, end: date | None) -> tuple[date | None, date | None]:
    """Swap a reversed custom range instead of silently showing nothing."""
    if start and end and start > end:
        return end, start
    return start, end


def totals(entries, start: date | None, end: date | None) -> dict:
    """Money in, money out (positive number), net and count for transactions in [start, end].
    Opening balance is not income and is never included."""
    lo = start.isoformat() if start else None
    hi = end.isoformat() if end else None
    money_in = money_out = count = 0
    for e in entries:
        if (lo and e.date < lo) or (hi and e.date > hi):
            continue
        count += 1
        if e.mills > 0:
            money_in += e.mills
        else:
            money_out += -e.mills
    return {"in": money_in, "out": money_out, "net": money_in - money_out, "count": count}


def describe(start: date | None, end: date | None) -> str:
    if not start and not end:
        return "All transactions"
    fmt = lambda d: f"{d:%b} {d.day}, {d.year}"
    if start == end:
        return fmt(start)
    if start.year == end.year:
        return f"{start:%b} {start.day} – {fmt(end)}"
    return f"{fmt(start)} – {fmt(end)}"
