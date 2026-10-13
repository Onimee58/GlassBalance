"""Exact arithmetic in thousandths of a currency unit."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation


def as_mills(value: object) -> int:
    """Convert a numeric amount to integral thousandths of a currency unit without float accumulation."""
    if isinstance(value, bool) or value is None:
        raise ValueError("Amount must be a number.")
    try:
        parsed = Decimal(str(value).replace(",", "").replace("$", "").strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid amount: {value!r}") from exc
    if not parsed.is_finite():
        raise ValueError("Amount must be finite.")
    scaled = parsed * 1000
    if scaled != scaled.to_integral_value():
        raise ValueError("Amounts can have at most three decimal places.")
    mills = int(scaled)
    if abs(mills) > 100_000_000_000:
        raise ValueError("Amount is outside the supported range.")
    return mills


def mills_as_decimal(mills: int) -> str:
    return str(Decimal(mills) / 1000)


def display_money(mills: int, currency: str = "$") -> str:
    prefix = "−" if mills < 0 else ""
    absolute = abs(mills)
    whole, fractional = divmod(absolute, 1000)
    digits = f"{fractional:03d}" if fractional % 10 else f"{fractional // 10:02d}"
    return f"{prefix}{currency}{whole:,}.{digits}"
