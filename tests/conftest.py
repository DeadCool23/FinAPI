from __future__ import annotations

import os
import sys

import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from src.models.schemas import CapitalizationType
from src.models.schemas import CreditRequest
from src.models.schemas import GoalRequest
from src.models.schemas import MortgageRequest
from src.models.schemas import PaymentType
from src.models.schemas import SavingsRequest


@pytest.fixture
def mortgage_request():
    """Базовая фикстура для ипотеки"""
    return MortgageRequest(
        price=5_000_000,
        down_payment=1_000_000,
        years=20,
        rate=12.0,
        payment_type=PaymentType.ANNUITY,
    )


@pytest.fixture
def credit_request():
    """Базовая фикстура для кредита"""
    return CreditRequest(
        amount=500_000,
        years=3,
        rate=15.0,
        payment_type=PaymentType.ANNUITY,
    )


@pytest.fixture
def savings_request():
    """Базовая фикстура для накоплений"""
    return SavingsRequest(
        initial=100_000,
        monthly=10_000,
        years=5,
        rate=12.0,
        capitalization=CapitalizationType.MONTHLY,
        tax_rate=0,
        inflation=0,
    )


@pytest.fixture
def goal_request():
    """Базовая фикстура для финансовой цели"""
    return GoalRequest(
        goal_amount=1_000_000,
        current_savings=100_000,
        years=5,
        expected_rate=10.0,
        monthly_contribution=None,
    )
