"""Form validation helpers."""

from __future__ import annotations

from typing import Dict, List, Tuple


def validate_inputs(payload: Dict[str, object]) -> Tuple[bool, List[str]]:
    """Validate required fields and return errors."""
    errors: List[str] = []
    required_text_fields = [
        "project_name",
        "city",
        "micro_market",
        "project_type",
        "nearby_landmarks",
        "brand_positioning",
        "usp",
        "price_segment",
        "tone",
    ]
    for field in required_text_fields:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Please provide a valid value for {field.replace('_', ' ').title()}.")

    configuration = payload.get("configuration", [])
    target_audience = payload.get("target_audience", [])

    if not isinstance(configuration, list) or len(configuration) == 0:
        errors.append("Please select at least one Configuration.")
    if not isinstance(target_audience, list) or len(target_audience) == 0:
        errors.append("Please select at least one Target Audience.")

    return len(errors) == 0, errors
