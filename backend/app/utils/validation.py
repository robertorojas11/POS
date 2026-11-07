from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal('0.01')


def to_decimal(value, field, minimum=Decimal('0'), allow_zero=True):
    """Parse request input to Decimal. Raises ValueError (routes turn it into a 400)."""
    if isinstance(value, bool) or value is None or value == '':
        raise ValueError(f"{field} must be a number")
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"{field} must be a number")
    if not number.is_finite():
        raise ValueError(f"{field} must be a number")
    if number < minimum or (number == minimum and not allow_zero):
        raise ValueError(f"{field} must be {'greater than' if not allow_zero else 'at least'} {minimum}")
    return number


def money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)
