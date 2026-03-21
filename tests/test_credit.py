from __future__ import annotations

import pytest

from src.models.schemas import CreditRequest
from src.models.schemas import PaymentType
from src.services.v1.financial_calculator import FinancialCalculator


class TestCredit:
    """Тесты расчета потребительского кредита"""

    def test_annuity_success(self, credit_request):
        """Тест аннуитетного кредита"""
        response = FinancialCalculator.calculate_credit(credit_request)

        assert response.monthly_payment > 0
        assert response.total_payment > credit_request.amount
        assert response.total_interest > 0
        assert response.effective_rate >= credit_request.rate
        assert len(response.payment_schedule) == int(credit_request.years * 12)

    def test_with_commission(self):
        """Тест с единовременной комиссией"""
        request = CreditRequest(
            amount=1_000_000,
            years=2,
            rate=12.0,
            commission=5.0,
        )

        response = FinancialCalculator.calculate_credit(request)

        assert response.commission_amount == 50_000
        assert response.total_payment > request.amount + response.commission_amount

    def test_with_insurance(self):
        """Тест со страховкой"""
        request = CreditRequest(
            amount=1_000_000,
            years=3,
            rate=12.0,
            insurance=2.0,
        )

        response = FinancialCalculator.calculate_credit(request)

        total_insurance = sum(payment.fees for payment in response.payment_schedule)
        assert total_insurance > 0

        for payment in response.payment_schedule[:12]:
            assert payment.fees > 0

    def test_differentiated(self):
        """Тест дифференцированного кредита"""
        request = CreditRequest(
            amount=300_000,
            years=2,
            rate=10.0,
            payment_type=PaymentType.DIFFERENTIATED,
        )

        response = FinancialCalculator.calculate_credit(request)

        payments = [p.payment for p in response.payment_schedule]
        assert payments[0] > payments[-1]

    def test_zero_rate(self):
        """Тест с нулевой процентной ставкой"""
        request = CreditRequest(
            amount=100_000,
            years=1,
            rate=0.0,
        )

        response = FinancialCalculator.calculate_credit(request)

        assert response.total_interest == 0
        assert response.total_payment == request.amount

    def test_short_term(self):
        """Тест с минимальным сроком"""
        request = CreditRequest(
            amount=100_000,
            years=0.25,
            rate=12.0,
        )

        response = FinancialCalculator.calculate_credit(request)

        assert len(response.payment_schedule) == 3

    def test_custom_payment_day(self):
        """Тест с нестандартным днем платежа"""
        request = CreditRequest(
            amount=500_000,
            years=1,
            rate=12.0,
            payment_day=31,
        )

        response = FinancialCalculator.calculate_credit(request)

        assert len(response.payment_schedule) == 12
        assert response.monthly_payment > 0

    def test_effective_rate_calculation(self):
        """Тест расчета эффективной ставки"""
        request = CreditRequest(
            amount=100_000,
            years=1,
            rate=10.0,
            commission=3.0,
            insurance=1.0,
        )

        response = FinancialCalculator.calculate_credit(request)

        assert response.effective_rate > request.rate


@pytest.mark.parametrize(
    "amount,years,rate,commission",
    [
        (100_000, 1, 10.0, 0),
        (500_000, 3, 12.0, 2.0),
        (1_000_000, 5, 8.0, 5.0),
        (50_000, 0.5, 15.0, 1.0),
    ],
)
def test_credit_parametrized(amount, years, rate, commission):
    """Параметризованные тесты кредита"""
    request = CreditRequest(
        amount=amount,
        years=years,
        rate=rate,
        commission=commission,
    )

    response = FinancialCalculator.calculate_credit(request)

    assert response.monthly_payment > 0
    assert response.total_payment >= amount
    assert response.effective_rate >= rate
