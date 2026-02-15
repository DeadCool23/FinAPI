from __future__ import annotations

from models.enums import CapitalizationType
from models.enums import PaymentType
from models.schemas import CreditRequest
from models.schemas import CreditResponse
from models.schemas import GoalRequest
from models.schemas import GoalResponse
from models.schemas import MortgageRequest
from models.schemas import MortgageResponse
from models.schemas import SavingsRequest
from models.schemas import SavingsResponse
from services.interfaces import IFinancialCalculator


class FinancialCalculator(IFinancialCalculator):
    @staticmethod
    def calculate_mortgage(request: MortgageRequest) -> MortgageRequest:
        loan_amount = request.price - request.down_payment
        monthly_rate = FinancialCalculator._calculate_monthly_rate(request.rate)
        months = FinancialCalculator._years_to_months(request.years)

        monthly_payment = FinancialCalculator._calculate_mortgage_monthly_payment(
            loan_amount=loan_amount,
            monthly_rate=monthly_rate,
            months=months,
            payment_type=request.payment_type,
        )
        total_payment = monthly_payment * months
        total_interest = FinancialCalculator._calculate_total_interest(
            total_payment=total_payment,
            principal=loan_amount,
        )

        schedule = FinancialCalculator._generate_mortgage_schedule(
            loan_amount=loan_amount,
            monthly_rate=monthly_rate,
            months=months,
            payment_type=request.payment_type,
            initial_monthly_payment=monthly_payment,
        )

        return MortgageResponse(
            loan_amount=round(loan_amount, 2),
            monthly_payment=round(monthly_payment, 2),
            total_payment=round(total_payment, 2),
            total_interest=round(total_interest, 2),
            payment_schedule=schedule,
        )

    @staticmethod
    def calculate_savings(request: SavingsRequest) -> SavingsResponse:
        annual_rate = FinancialCalculator._calculate_annual_rate(request.rate)
        months = FinancialCalculator._years_to_months(request.years)

        periods_per_year = FinancialCalculator._determine_periods_per_year(
            request.capitalization,
        )

        if request.capitalization != CapitalizationType.NONE:
            final_amount = FinancialCalculator._calculate_compound_savings(
                request=request,
                annual_rate=annual_rate,
                periods_per_year=periods_per_year,
            )
        else:
            final_amount = FinancialCalculator._calculate_simple_savings(
                request=request,
                annual_rate=annual_rate,
                months=months,
            )

        total_contributions = FinancialCalculator._calculate_total_contributions(
            initial=request.initial,
            monthly=request.monthly,
            months=months,
        )
        total_interest_amount = FinancialCalculator._calculate_total_interest_amount(
            final_amount=final_amount,
            total_contributions=total_contributions,
        )

        total_tax = FinancialCalculator._calculate_tax(
            total_interest_amount=total_interest_amount,
            tax_rate=request.tax_rate,
        )

        real_amount = FinancialCalculator._adjust_for_inflation(
            final_amount=final_amount,
            inflation=request.inflation,
            years=request.years,
        )

        yearly_breakdown = FinancialCalculator._generate_yearly_savings_breakdown(
            request=request,
            annual_rate=annual_rate,
        )

        return SavingsResponse(
            final_amount_nominal=round(final_amount - total_tax, 2),
            final_amount_real=round(real_amount - total_tax, 2),
            total_contributions=round(total_contributions, 2),
            total_interest=round(total_interest_amount, 2),
            total_tax=round(total_tax, 2),
            yearly_breakdown=yearly_breakdown,
        )

    @staticmethod
    def calculate_credit(request: CreditRequest) -> CreditResponse:
        monthly_rate = FinancialCalculator._calculate_monthly_rate(request.rate)
        months = int(FinancialCalculator._years_to_months(request.years))

        commission_amount = FinancialCalculator._calculate_commission_amount(
            amount=request.amount,
            commission_rate=request.commission,
        )
        effective_amount = FinancialCalculator._calculate_effective_amount(
            amount=request.amount,
            commission_amount=commission_amount,
        )

        monthly_payment = FinancialCalculator._calculate_credit_monthly_payment(
            effective_amount=effective_amount,
            monthly_rate=monthly_rate,
            months=months,
            payment_type=request.payment_type,
        )

        annual_insurance = FinancialCalculator._calculate_annual_insurance(
            amount=request.amount,
            insurance_rate=request.insurance,
        )
        monthly_insurance = FinancialCalculator._calculate_monthly_insurance(
            annual_insurance=annual_insurance,
            has_insurance=request.insurance > 0,
        )

        base_total_payment = FinancialCalculator._calculate_credit_total_payment(
            monthly_payment=monthly_payment,
            monthly_insurance=monthly_insurance,
            months=months,
        )
        total_payment = base_total_payment + commission_amount
        total_interest = FinancialCalculator._calculate_total_interest(
            total_payment=total_payment,
            principal=request.amount,
        )

        effective_rate = FinancialCalculator._calculate_effective_rate(
            base_rate=request.rate,
            commission_rate=request.commission,
            insurance_rate=request.insurance,
        )

        payment_schedule = FinancialCalculator._generate_credit_schedule(
            effective_amount=effective_amount,
            monthly_rate=monthly_rate,
            months=months,
            payment_type=request.payment_type,
            monthly_payment=monthly_payment,
            monthly_insurance=monthly_insurance,
            commission_amount=commission_amount,
        )

        return CreditResponse(
            monthly_payment=round(monthly_payment + monthly_insurance, 2),
            total_payment=round(total_payment, 2),
            total_interest=round(total_interest, 2),
            effective_rate=round(effective_rate, 2),
            commission_amount=round(commission_amount, 2),
            total_insurance=round(monthly_insurance * months, 2),
            payment_schedule=payment_schedule,
        )

    @staticmethod
    def calculate_goal(request: GoalRequest) -> GoalResponse:
        annual_rate = FinancialCalculator._calculate_annual_rate(
            request.expected_rate,
        )
        months = FinancialCalculator._years_to_months(request.years)

        if request.monthly_contribution is None:
            required_monthly = (
                FinancialCalculator._calculate_required_monthly_contribution(
                    goal_amount=request.goal_amount,
                    current_savings=request.current_savings,
                    annual_rate=annual_rate,
                    months=months,
                )
            )
            monthly_breakdown = FinancialCalculator._generate_goal_monthly_breakdown(
                current_savings=request.current_savings,
                monthly_contribution=required_monthly,
                annual_rate=annual_rate,
                months=months,
            )
            return {
                "required_monthly": round(required_monthly, 2),
                "expected_final_amount": None,
                "monthly_breakdown": monthly_breakdown,
            }

        future_value = FinancialCalculator._calculate_expected_final_amount(
            current_savings=request.current_savings,
            monthly_contribution=request.monthly_contribution,
            annual_rate=annual_rate,
            months=months,
        )
        monthly_breakdown = FinancialCalculator._generate_goal_monthly_breakdown(
            current_savings=request.current_savings,
            monthly_contribution=request.monthly_contribution,
            annual_rate=annual_rate,
            months=months,
        )
        return GoalResponse(
            required_monthly=None,
            expected_final_amount=round(future_value, 2),
            monthly_breakdown=monthly_breakdown,
        )

    @staticmethod
    def _calculate_monthly_rate(annual_rate_percent: float) -> float:
        return annual_rate_percent / 100 / 12

    @staticmethod
    def _calculate_annual_rate(annual_rate_percent: float) -> float:
        return annual_rate_percent / 100

    @staticmethod
    def _years_to_months(years: float) -> int:
        return int(years * 12)

    @staticmethod
    def _calculate_total_interest(total_payment: float, principal: float) -> float:
        return total_payment - principal

    @staticmethod
    def _calculate_mortgage_monthly_payment(
        loan_amount: float,
        monthly_rate: float,
        months: int,
        payment_type: PaymentType,
    ) -> float:
        if payment_type == PaymentType.ANNUITY:
            return loan_amount * (
                (monthly_rate * (1 + monthly_rate) ** months)
                / ((1 + monthly_rate) ** months - 1)
            )

        principal_part = loan_amount / months
        return principal_part + (loan_amount * monthly_rate)

    @staticmethod
    def _generate_mortgage_schedule(
        loan_amount: float,
        monthly_rate: float,
        months: int,
        payment_type: PaymentType,
        initial_monthly_payment: float,
    ) -> list[dict]:
        schedule: list[dict] = []
        balance = loan_amount
        monthly_payment = initial_monthly_payment

        for month in range(1, months + 1):
            interest = balance * monthly_rate
            principal = monthly_payment - interest

            if payment_type == PaymentType.DIFFERENTIATED:
                principal = loan_amount / months
                interest = balance * monthly_rate
                monthly_payment = principal + interest

            balance -= principal

            schedule.append(
                {
                    "month": month,
                    "payment": round(monthly_payment, 2),
                    "principal": round(principal, 2),
                    "interest": round(interest, 2),
                    "balance": round(max(balance, 0), 2),
                },
            )

        return schedule

    @staticmethod
    def _determine_periods_per_year(capitalization: CapitalizationType) -> int | None:
        if capitalization == CapitalizationType.DAILY:
            return 365
        if capitalization == CapitalizationType.MONTHLY:
            return 12
        if capitalization == CapitalizationType.QUARTERLY:
            return 4
        if capitalization == CapitalizationType.YEARLY:
            return 1

        return None

    @staticmethod
    def _calculate_compound_savings(
        request: SavingsRequest,
        annual_rate: float,
        periods_per_year: int,
    ) -> float:
        months_per_year = 12
        rate_per_period = annual_rate / periods_per_year
        total_periods = request.years * periods_per_year

        future_value_initial = request.initial * (1 + rate_per_period) ** total_periods

        if periods_per_year == months_per_year:
            payment_per_period = request.monthly
            periods_for_payments = total_periods
        else:
            payment_per_period = request.monthly * 12 / periods_per_year
            periods_for_payments = total_periods

        future_value_annuity = 0.0
        if payment_per_period > 0:
            future_value_annuity = (
                payment_per_period
                * ((1 + rate_per_period) ** periods_for_payments - 1)
                / rate_per_period
            )

        return future_value_initial + future_value_annuity

    @staticmethod
    def _calculate_simple_savings(
        request: SavingsRequest,
        annual_rate: float,
        months: int,
    ) -> float:
        total_interest = request.initial * annual_rate * request.years
        monthly_interest = request.monthly * annual_rate * request.years / 2
        return (
            request.initial
            + request.monthly * months
            + total_interest
            + monthly_interest
        )

    @staticmethod
    def _calculate_total_contributions(
        initial: float,
        monthly: float,
        months: int,
    ) -> float:
        return initial + (monthly * months)

    @staticmethod
    def _calculate_total_interest_amount(
        final_amount: float,
        total_contributions: float,
    ) -> float:
        return final_amount - total_contributions

    @staticmethod
    def _calculate_tax(
        total_interest_amount: float,
        tax_rate: float,
    ) -> float:
        return total_interest_amount * (tax_rate / 100)

    @staticmethod
    def _adjust_for_inflation(
        final_amount: float,
        inflation: float,
        years: int,
    ) -> float:
        if inflation > 0:
            inflation_factor = (1 - inflation / 100) ** years
            return final_amount * inflation_factor
        return final_amount

    @staticmethod
    def _generate_yearly_savings_breakdown(
        request: SavingsRequest,
        annual_rate: float,
    ) -> list[dict]:
        yearly_breakdown: list[dict] = []
        current_amount = request.initial

        for year in range(1, request.years + 1):
            yearly_contributions = request.monthly * 12
            yearly_interest = (
                current_amount * annual_rate + yearly_contributions * annual_rate / 2
            )
            current_amount += yearly_contributions + yearly_interest

            yearly_breakdown.append(
                {
                    "year": year,
                    "amount": round(current_amount, 2),
                    "contributions": round(yearly_contributions, 2),
                    "interest": round(yearly_interest, 2),
                },
            )

        return yearly_breakdown

    @staticmethod
    def _calculate_commission_amount(amount: float, commission_rate: float) -> float:
        return amount * (commission_rate / 100)

    @staticmethod
    def _calculate_effective_amount(
        amount: float,
        commission_amount: float,
    ) -> float:
        return amount - commission_amount

    @staticmethod
    def _calculate_credit_monthly_payment(
        effective_amount: float,
        monthly_rate: float,
        months: int,
        payment_type: PaymentType,
    ) -> float:
        if payment_type == PaymentType.ANNUITY:
            return effective_amount * (
                (monthly_rate * (1 + monthly_rate) ** months)
                / ((1 + monthly_rate) ** months - 1)
            )

        principal_part = effective_amount / months
        return principal_part + (effective_amount * monthly_rate)

    @staticmethod
    def _calculate_annual_insurance(
        amount: float,
        insurance_rate: float,
    ) -> float:
        return amount * (insurance_rate / 100)

    @staticmethod
    def _calculate_monthly_insurance(
        annual_insurance: float,
        has_insurance: bool,
    ) -> float:
        return annual_insurance / 12 if has_insurance else 0.0

    @staticmethod
    def _calculate_credit_total_payment(
        monthly_payment: float,
        monthly_insurance: float,
        months: int,
    ) -> float:
        return monthly_payment * months + monthly_insurance * months

    @staticmethod
    def _calculate_effective_rate(
        base_rate: float,
        commission_rate: float,
        insurance_rate: float,
    ) -> float:
        return base_rate + commission_rate + insurance_rate

    @staticmethod
    def _generate_credit_schedule(
        effective_amount: float,
        monthly_rate: float,
        months: int,
        payment_type: PaymentType,
        monthly_payment: float,
        monthly_insurance: float,
        commission_amount: float,
    ) -> list[dict]:
        schedule: list[dict] = []
        balance = effective_amount

        for month in range(1, months + 1):
            if payment_type == PaymentType.ANNUITY:
                base_payment = monthly_payment
                interest = balance * monthly_rate
                principal = base_payment - interest
            else:
                principal = effective_amount / months
                interest = balance * monthly_rate
                base_payment = principal + interest

            balance -= principal

            fees = monthly_insurance
            if month == 1 and commission_amount > 0:
                fees += commission_amount

            total_payment = base_payment + fees

            schedule.append(
                {
                    "month": month,
                    "payment": round(total_payment, 2),
                    "principal": round(principal, 2),
                    "interest": round(interest, 2),
                    "fees": round(fees, 2),
                    "balance": round(max(balance, 0), 2),
                },
            )

        return schedule

    @staticmethod
    def _calculate_required_monthly_contribution(
        goal_amount: float,
        current_savings: float,
        annual_rate: float,
        months: int,
    ) -> float:
        future_value = goal_amount
        present_value = current_savings

        if annual_rate > 0:
            monthly_rate = annual_rate / 12
            fv_factor = (1 + monthly_rate) ** months
            annuity_factor = (fv_factor - 1) / monthly_rate

            required_monthly = (
                future_value - present_value * fv_factor
            ) / annuity_factor
            return max(required_monthly, 0.0)

        return (future_value - present_value) / months

    @staticmethod
    def _calculate_expected_final_amount(
        current_savings: float,
        monthly_contribution: float,
        annual_rate: float,
        months: int,
    ) -> float:
        monthly_rate = annual_rate / 12
        fv_factor = (1 + monthly_rate) ** months
        annuity_factor = (fv_factor - 1) / monthly_rate

        return current_savings * fv_factor + monthly_contribution * annuity_factor

    @staticmethod
    def _generate_goal_monthly_breakdown(
        current_savings: float,
        monthly_contribution: float,
        annual_rate: float,
        months: int,
    ) -> list[dict]:
        monthly_rate = annual_rate / 12
        balance = current_savings
        total_contributions = 0.0
        breakdown: list[dict] = []

        for month in range(1, months + 1):
            balance += monthly_contribution
            total_contributions += monthly_contribution

            interest = balance * monthly_rate
            balance += interest

            breakdown.append(
                {
                    "month": month,
                    "amount": round(balance, 2),
                    "contributions": round(total_contributions, 2),
                    "interest": round(interest, 2),
                },
            )

        return breakdown
