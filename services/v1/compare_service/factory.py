from __future__ import annotations

from typing import ClassVar

from models.enums import ComparisonType
from services.v1.compare_service.strategy import ComparisonStrategy
from services.v1.compare_service.strategy import CreditComparisonStrategy
from services.v1.compare_service.strategy import GoalStrategyComparisonStrategy
from services.v1.compare_service.strategy import MortgageComparisonStrategy
from services.v1.compare_service.strategy import SavingsComparisonStrategy
from services.v1.financial_calculator import FinancialCalculator


class ComparisonStrategyFactory:
    _strategies: ClassVar[dict[ComparisonType, ComparisonStrategy]] = {}

    @classmethod
    def register(
        cls,
        comparison_type: ComparisonType,
        strategy: ComparisonStrategy
    ) -> ComparisonStrategy:
        cls._strategies[comparison_type] = strategy

    @classmethod
    def create(cls, comparison_type: ComparisonType) -> ComparisonStrategy:
        strategy = cls._strategies.get(comparison_type)
        if strategy is None:
            raise ValueError(f"Unknown comparison type: {comparison_type}")
        return strategy


calculator = FinancialCalculator
ComparisonStrategyFactory.register(
    ComparisonType.MORTGAGE,
    MortgageComparisonStrategy(calculator),
)
ComparisonStrategyFactory.register(
    ComparisonType.CREDIT,
    CreditComparisonStrategy(calculator),
)
ComparisonStrategyFactory.register(
    ComparisonType.SAVINGS,
    SavingsComparisonStrategy(calculator),
)
ComparisonStrategyFactory.register(
    ComparisonType.GOAL,
    GoalStrategyComparisonStrategy(calculator),
)
