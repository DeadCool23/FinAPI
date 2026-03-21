from __future__ import annotations

import pytest

from src.models.schemas import GoalRequest
from src.models.schemas import GoalResponse
from src.services.v1.financial_calculator import FinancialCalculator


class TestGoal:
    """Тесты расчета финансовой цели"""

    def test_with_monthly_contribution(self):
        """Тест с фиксированным ежемесячным взносом"""
        request = GoalRequest(
            goal_amount=1_000_000,
            current_savings=100_000,
            years=5,
            expected_rate=10.0,
            monthly_contribution=10_000,
        )
        
        response = FinancialCalculator.calculate_goal(request)
        
        assert response.required_monthly is None
        assert response.expected_final_amount is not None
        
        assert response.expected_final_amount < request.goal_amount
        assert response.is_achievable is False

    def test_without_monthly_contribution(self):
        """Тест без указания ежемесячного взноса (рассчитываем его)"""
        request = GoalRequest(
            goal_amount=1_000_000,
            current_savings=100_000,
            years=5,
            expected_rate=10.0,
            monthly_contribution=None,
        )
        
        response = FinancialCalculator.calculate_goal(request)
        
        assert response.required_monthly is not None
        assert response.required_monthly > 0
        assert response.expected_final_amount is None
        
        assert response.is_achievable is True

    def test_already_achieved(self):
        """Тест: цель уже достигнута"""
        request = GoalRequest(
            goal_amount=500_000,
            current_savings=600_000,
            years=5,
            expected_rate=5.0,
        )

        response = FinancialCalculator.calculate_goal(request)

        assert response.is_achievable is True
        assert response.required_monthly == 0

    def test_unachievable(self):
        """Тест: цель недостижима"""
        request = GoalRequest(
            goal_amount=10_000_000,
            current_savings=1_000,
            years=1,
            expected_rate=5.0,
            monthly_contribution=1_000,
        )

        response = FinancialCalculator.calculate_goal(request)

        assert response.is_achievable is False
        assert response.expected_final_amount < request.goal_amount

    def test_high_rate(self):
        """Тест с высокой доходностью"""
        request = GoalRequest(
            goal_amount=1_000_000,
            current_savings=500_000,
            years=3,
            expected_rate=99.0,
            monthly_contribution=None,
        )

        response = FinancialCalculator.calculate_goal(request)

        assert response.is_achievable is True
        assert response.required_monthly == 0

    def test_minimal_years(self):
        """Тест с минимальным сроком"""
        request = GoalRequest(
            goal_amount=1_000_000,
            current_savings=900_000,
            years=1,
            expected_rate=10.0,
            monthly_contribution=None,
        )

        response = FinancialCalculator.calculate_goal(request)

        assert response.is_achievable is True


@pytest.mark.parametrize(
    "goal_amount,current_savings,years,rate",
    [
        (1_000_000, 100_000, 5, 10.0),
        (500_000, 50_000, 3, 8.0),
        (2_000_000, 500_000, 10, 12.0),
        (100_000, 0, 2, 15.0),
    ],
)
def test_goal_parametrized(goal_amount, current_savings, years, rate):
    """Параметризованные тесты цели"""
    request = GoalRequest(
        goal_amount=goal_amount,
        current_savings=current_savings,
        years=years,
        expected_rate=rate,
        monthly_contribution=None,
    )

    response = FinancialCalculator.calculate_goal(request)

    assert response.required_monthly >= 0
