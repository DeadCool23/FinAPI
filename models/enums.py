from __future__ import annotations

from enum import StrEnum


class PaymentType(StrEnum):
    ANNUITY = "annuity"
    DIFFERENTIATED = "differentiated"


class CapitalizationType(StrEnum):
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    NONE = "none"


class ComparisonType(StrEnum):
    MORTGAGE = "mortgage"
    SAVINGS = "savings"
    CREDIT = "credit"
    GOAL = "goal"
