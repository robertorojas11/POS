"""Business profiles: one codebase, one deployment per business, behaviour chosen by BUSINESS_TYPE.

Only flags for features that exist in the code are True. Flip a flag to True when the feature ships;
the frontend reads these from GET /api/config and hides what is off.
"""

_BASE = {
    'fractional_quantities': True,   # kg / liters via Product.uom + min_sale_qty
    'barcode_scanning': True,
    'loyalty': True,
    'tables': False,                 # restaurant/bar: open tabs per table (not built)
    'modifiers': False,              # restaurant/bar: "no onion", extra shot (not built)
    'tips': False,                   # restaurant/bar (not built)
    'kitchen_tickets': False,        # restaurant (not built)
    'age_check': False,              # bar / liquor (not built)
}

PROFILES = {
    'retail': {**_BASE},             # grocery, toys, hardware, general store
    'restaurant': {**_BASE, 'barcode_scanning': False},
    'bar': {**_BASE, 'barcode_scanning': False},
}


def features_for(business_type):
    if business_type not in PROFILES:
        raise RuntimeError(f"Unknown BUSINESS_TYPE '{business_type}'. Use one of: {', '.join(PROFILES)}")
    return PROFILES[business_type]
