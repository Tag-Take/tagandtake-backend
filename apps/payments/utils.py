from decimal import Decimal


def to_stripe_amount(amount: Decimal) -> int:
    """Converts a decimal amount to Stripe's integer format."""
    return int(round(float(amount) * 100))


def from_stripe_amount(stripe_amount: str) -> Decimal:
    """Converts Stripe's integer amount to a decimal format."""
    return Decimal(str(int(stripe_amount))) / Decimal(100)
