from __future__ import annotations

import pytest

from src.models.schemas import MortgageRequest
from src.models.schemas import MortgageResponse
from src.models.schemas import PaymentType
from src.services.v1.financial_calculator import FinancialCalculator


class TestMortgage:
    """Тесты расчета ипотеки"""

    def test_annuity_success(self, mortgage_request):
        """Тест аннуитетного платежа"""
        response = FinancialCalculator.calculate_mortgage(mortgage_request)

        assert response.loan_amount == mortgage_request.price - mortgage_request.down_payment
        assert response.monthly_payment > 0
        assert response.total_payment > response.loan_amount
        assert response.total_interest == pytest.approx(response.total_payment - response.loan_amount)

        assert len(response.payment_schedule) == mortgage_request.years * 12
        assert response.payment_schedule[0].month == 1
        assert response.payment_schedule[-1].balance == pytest.approx(0, abs=1e-2)

    def test_differentiated_success(self):
        """Тест дифференцированного платежа"""
        request = MortgageRequest(
            price=3_000_000,
            down_payment=500_000,
            years=10,
            rate=10.5,
            payment_type=PaymentType.DIFFERENTIATED,
        )

        response = FinancialCalculator.calculate_mortgage(request)

        assert response.loan_amount == 2_500_000

        first_payment = response.payment_schedule[0].payment
        last_payment = response.payment_schedule[-1].payment
        assert first_payment > last_payment

    def test_minimal_down_payment(self):
        """Тест с минимальным первоначальным взносом"""
        request = MortgageRequest(
            price=2_000_000,
            down_payment=1,
            years=5,
            rate=8.0,
        )

        response = FinancialCalculator.calculate_mortgage(request)

        assert response.loan_amount == 2_000_000 - 1
        assert response.monthly_payment > 0

    def test_max_rate(self):
        """Тест с максимальной процентной ставкой"""
        request = MortgageRequest(
            price=1_000_000,
            down_payment=200_000,
            years=10,
            rate=99.0,
        )

        response = FinancialCalculator.calculate_mortgage(request)

        assert response.total_interest > response.loan_amount

    def test_short_term(self):
        """Тест с коротким сроком"""
        request = MortgageRequest(
            price=1_000_000,
            down_payment=100_000,
            years=1,
            rate=12.0,
        )

        response = FinancialCalculator.calculate_mortgage(request)

        assert len(response.payment_schedule) == 12

    def test_long_term(self):
        """Тест с длительным сроком"""
        request = MortgageRequest(
            price=1_000_000,
            down_payment=100_000,
            years=50,
            rate=12.0,
        )

        response = FinancialCalculator.calculate_mortgage(request)

        assert len(response.payment_schedule) == 50 * 12
        assert response.total_interest > response.loan_amount

    def test_annuity_payments_constant(self, mortgage_request):
        """Для аннуитета все платежи должны быть равны"""
        response = FinancialCalculator.calculate_mortgage(mortgage_request)

        payments = [p.payment for p in response.payment_schedule]
        assert all(abs(p - payments[0]) < 0.01 for p in payments)

        interests = [p.interest for p in response.payment_schedule]
        assert interests[0] > interests[-1]

        principals = [p.principal for p in response.payment_schedule]
        assert principals[0] < principals[-1]

    def test_invalid_down_payment_equal_price(self):
        """Тест: первоначальный взнос равен стоимости"""
        with pytest.raises(ValueError) as exc_info:
            MortgageRequest(
                price=1_000_000,
                down_payment=1_000_000,
                years=10,
                rate=12.0,
            )

        assert "первоначальный взнос" in str(exc_info.value).lower()
        assert "меньше" in str(exc_info.value).lower()

    def test_invalid_down_payment_greater_than_price(self):
        """Тест: первоначальный взнос больше стоимости"""
        with pytest.raises(ValueError):
            MortgageRequest(
                price=1_000_000,
                down_payment=1_500_000,
                years=10,
                rate=12.0,
            )


@pytest.mark.parametrize(
    "price,down_payment,years,rate",
    [
        (2_000_000, 500_000, 10, 10.0),
        (3_500_000, 1_000_000, 15, 8.5),
        (10_000_000, 2_000_000, 30, 12.0),
        (1_500_000, 300_000, 5, 7.0),
    ],
)
def test_mortgage_parametrized(price, down_payment, years, rate):
    """Параметризованные тесты ипотеки"""
    request = MortgageRequest(
        price=price,
        down_payment=down_payment,
        years=years,
        rate=rate,
    )

    response = FinancialCalculator.calculate_mortgage(request)

    assert response.loan_amount == price - down_payment
    assert response.monthly_payment > 0
    assert response.total_payment > response.loan_amount
