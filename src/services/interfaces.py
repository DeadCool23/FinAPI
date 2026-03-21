from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from models.schemas import CompareRequest
from models.schemas import CompareResponse
from models.schemas import CreditRequest
from models.schemas import CreditResponse
from models.schemas import GoalRequest
from models.schemas import GoalResponse
from models.schemas import MonteCarloRequest
from models.schemas import MonteCarloResponse
from models.schemas import MortgageRequest
from models.schemas import MortgageResponse
from models.schemas import SavingsRequest
from models.schemas import SavingsResponse


class IFinancialCalculator(ABC):
    @abstractmethod
    def calculate_mortgage(self, request: MortgageRequest) -> MortgageResponse:
        pass

    @abstractmethod
    def calculate_savings(self, request: SavingsRequest) -> SavingsResponse:
        pass

    @abstractmethod
    def calculate_credit(self, request: CreditRequest) -> CreditResponse:
        pass

    @abstractmethod
    def calculate_goal(self, request: GoalRequest) -> GoalResponse:
        pass


class IMonteCarloService(ABC):
    @abstractmethod
    async def simulate(self, request: MonteCarloRequest) -> MonteCarloResponse:
        pass


class ICompareService(ABC):
    @abstractmethod
    def comparison(self, request: CompareRequest) -> CompareResponse:
        pass
