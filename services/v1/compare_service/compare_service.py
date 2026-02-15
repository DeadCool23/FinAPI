from __future__ import annotations

from models.schemas import CompareRequest
from models.schemas import CompareResponse
from services.interfaces import ICompareService
from services.v1.compare_service.factory import ComparisonStrategyFactory


class CompareService(ICompareService):
    @staticmethod
    def comparison(request: CompareRequest) -> CompareResponse:
        strategy = ComparisonStrategyFactory.create(request.type)

        results = []
        for scenario in request.scenarios:
            results.append(
                {
                    "name": scenario.name,
                    "data": strategy.calculate(scenario.data),
                },
            )

        rec = strategy.recommendation(results)

        return {
            "type": request.type,
            "recommendation": rec["name"],
            "comparison": results,
        }
