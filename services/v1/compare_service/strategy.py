from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Self

from models.schemas import CreditRequest
from models.schemas import CreditResponse
from models.schemas import GoalRequest
from models.schemas import GoalResponse
from models.schemas import MortgageRequest
from models.schemas import MortgageResponse
from models.schemas import SavingsRequest
from models.schemas import SavingsResponse
from services.interfaces import IFinancialCalculator


class ComparisonStrategy[Req, Resp](ABC):
    @abstractmethod
    def calculate(self, request_data: Req) -> Resp:
        pass

    @staticmethod
    @abstractmethod
    def recommendation(
        calculation_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        pass


class MortgageComparisonStrategy(ComparisonStrategy):
    def __init__(self, fin_calc: IFinancialCalculator) -> Self:
        self.calculator = fin_calc

    def calculate(self, request_data: MortgageRequest) -> MortgageResponse:
        return self.calculator.calculate_mortgage(request_data)

    @staticmethod
    def recommendation(calculation_results: list[dict[str, Any]]) -> dict[str, Any]:
        return min(calculation_results, key=lambda x: x["data"].total_payment)


class CreditComparisonStrategy(ComparisonStrategy):
    def __init__(self, fin_calc: IFinancialCalculator) -> Self:
        self.calculator = fin_calc

    def calculate(self, request_data: CreditRequest) -> CreditResponse:
        return self.calculator.calculate_credit(request_data)

    @staticmethod
    def recommendation(calculation_results: list[dict[str, Any]]) -> dict[str, Any]:
        return min(calculation_results, key=lambda x: x["data"].total_payment)


class SavingsComparisonStrategy(ComparisonStrategy):
    def __init__(self, fin_calc: IFinancialCalculator) -> Self:
        self.calculator = fin_calc

    def calculate(self, request_data: SavingsRequest) -> SavingsResponse:
        return self.calculator.calculate_savings(request_data)

    @staticmethod
    def recommendation(calculation_results: list[dict[str, Any]]) -> dict[str, Any]:
        return max(calculation_results, key=lambda x: x["data"].total_interest)


class GoalStrategyComparisonStrategy(ComparisonStrategy):
    def __init__(self, fin_calc: IFinancialCalculator) -> Self:
        self.calculator = fin_calc

    def calculate(self, request_data: GoalRequest) -> GoalResponse:
        return self.calculator.calculate_goal(request_data)
    
    @staticmethod
    def recommendation(calculation_results: list[dict[str, Any]]) -> dict[str, Any]:
        sample = calculation_results[0]["data"]
        if sample.expected_final_amount is None:
            return min(
                calculation_results,
                key=lambda x: x["data"].required_monthly,
            )
        return max(
            calculation_results,
            key=lambda x: x["data"].expected_final_amount,
        )
