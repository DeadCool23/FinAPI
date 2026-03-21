from __future__ import annotations

import pytest

from src.models.schemas import CapitalizationType
from src.models.schemas import SavingsRequest
from src.models.schemas import SavingsResponse
from src.services.v1.financial_calculator import FinancialCalculator


class TestSavings:
    """Тесты расчета накоплений"""

    def test_monthly_capitalization(self, savings_request):
        """Тест с ежемесячной капитализацией"""
        response = FinancialCalculator.calculate_savings(savings_request)

        total_contributions = savings_request.initial + (savings_request.monthly * 12 * savings_request.years)

        assert response.total_contributions == pytest.approx(total_contributions, rel=1e-2)
        assert response.final_amount_nominal > total_contributions
        assert response.total_interest > 0
        assert len(response.yearly_breakdown) == savings_request.years

        amounts = [year.amount for year in response.yearly_breakdown]
        assert amounts[0] < amounts[-1]

    def test_yearly_capitalization(self):
        """Тест с ежегодной капитализацией"""
        yearly_request = SavingsRequest(
            initial=100_000,
            monthly=5_000,
            years=3,
            rate=10.0,
            capitalization=CapitalizationType.YEARLY,
        )

        monthly_request = SavingsRequest(
            initial=100_000,
            monthly=5_000,
            years=3,
            rate=10.0,
            capitalization=CapitalizationType.MONTHLY,
        )

        response_yearly = FinancialCalculator.calculate_savings(yearly_request)
        response_monthly = FinancialCalculator.calculate_savings(monthly_request)

        assert response_yearly.final_amount_nominal < response_monthly.final_amount_nominal

    def test_with_tax(self):
        """Тест с налогом на доход"""
        request = SavingsRequest(
            initial=1_000_000,
            monthly=50_000,
            years=3,
            rate=15.0,
            tax_rate=13.0,
        )

        response = FinancialCalculator.calculate_savings(request)

        assert response.total_tax > 0
        assert response.final_amount_nominal == response.final_amount_real
        expected_final = response.total_contributions + response.total_interest - response.total_tax
        assert response.final_amount_nominal == pytest.approx(expected_final, rel=1e-2)

    def test_with_inflation(self):
        """Тест с учетом инфляции"""
        request = SavingsRequest(
            initial=100_000,
            monthly=10_000,
            years=10,
            rate=12.0,
            inflation=8.0,
        )

        response = FinancialCalculator.calculate_savings(request)

        assert response.final_amount_real < response.final_amount_nominal
        assert response.final_amount_real > 0

    def test_no_initial(self):
        """Тест без начальной суммы"""
        request = SavingsRequest(
            initial=0,
            monthly=20_000,
            years=5,
            rate=10.0,
        )

        response = FinancialCalculator.calculate_savings(request)

        expected_contributions = 20_000 * 12 * 5
        assert response.total_contributions == expected_contributions
        assert response.total_interest > 0

    def test_no_monthly(self):
        """Тест без ежемесячных пополнений"""
        request = SavingsRequest(
            initial=500_000,
            monthly=0,
            years=3,
            rate=8.0,
        )

        response = FinancialCalculator.calculate_savings(request)

        assert response.total_contributions == 500_000
        assert response.final_amount_nominal > 500_000

    def test_zero_rate(self):
        """Тест с нулевой процентной ставкой"""
        request = SavingsRequest(
            initial=100_000,
            monthly=10_000,
            years=2,
            rate=0.0,
        )

        response = FinancialCalculator.calculate_savings(request)

        assert response.total_interest == 0
        assert response.final_amount_nominal == response.total_contributions

    def test_yearly_breakdown(self, savings_request):
        """Тест годового отчета"""
        response = FinancialCalculator.calculate_savings(savings_request)

        assert len(response.yearly_breakdown) == savings_request.years

        amounts = [year.amount for year in response.yearly_breakdown]
        assert amounts[0] < amounts[1] < amounts[2]

        first_year = response.yearly_breakdown[0]
        assert first_year.year == 1
        assert first_year.contributions > 0
        assert first_year.interest > 0

    def test_max_years(self):
        """Тест с максимальным сроком"""
        request = SavingsRequest(
            initial=1_000,
            monthly=1_000,
            years=100,
            rate=5.0,
        )

        response = FinancialCalculator.calculate_savings(request)

        assert len(response.yearly_breakdown) == 100
        assert response.final_amount_nominal > 0


@pytest.mark.parametrize(
    "initial,monthly,years,rate",
    [
        (100_000, 10_000, 5, 10.0),
        (0, 20_000, 10, 8.0),
        (500_000, 0, 3, 12.0),
        (50_000, 5_000, 20, 7.5),
    ],
)
def test_savings_parametrized(initial, monthly, years, rate):
    """Параметризованные тесты накоплений"""
    request = SavingsRequest(
        initial=initial,
        monthly=monthly,
        years=years,
        rate=rate,
    )

    response = FinancialCalculator.calculate_savings(request)

    assert response.final_amount_nominal > 0
    assert len(response.yearly_breakdown) == years
