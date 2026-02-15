from __future__ import annotations

import asyncio

import numpy as np

from models.schemas import MonteCarloRequest
from models.schemas import MonteCarloResponse
from services.interfaces import IMonteCarloService


WORKERS_CNT = 3


class MonteCarloService(IMonteCarloService):
    @staticmethod
    async def simulate(request: MonteCarloRequest) -> MonteCarloResponse:
        loop = asyncio.get_running_loop()

        monthly_rate, monthly_risk, months = MonteCarloService._prepare_parameters(
            request,
        )

        if WORKERS_CNT == 1:
            return MonteCarloService.sync_simulate(request)

        sims_per_worker = request.simulations // WORKERS_CNT
        remainder = request.simulations % WORKERS_CNT

        tasks = []

        for i in range(WORKERS_CNT):
            n = sims_per_worker + (1 if i < remainder else 0)
            if n <= 0:
                continue

            tasks.append(
                loop.run_in_executor(
                    None,
                    MonteCarloService._run_simulations,
                    request.initial,
                    request.monthly,
                    n,
                    monthly_rate,
                    monthly_risk,
                    months,
                ),
            )

        chunks = await asyncio.gather(*tasks)

        final_amounts: list[float] = []
        all_simulations: list[list[float]] = []
        for fa, sims in chunks:
            final_amounts.extend(fa)
            all_simulations.extend(sims)

        final_array = np.array(final_amounts)

        statistics = MonteCarloService._calculate_statistics(final_array)
        percentiles = MonteCarloService._calculate_percentiles(final_array)

        total_contributions = MonteCarloService._calculate_total_contributions(
            request,
            months,
        )
        probabilities = MonteCarloService._calculate_probabilities(
            final_array=final_array,
            request=request,
            total_contributions=total_contributions,
        )

        distribution = MonteCarloService._build_distribution(final_array)

        return MonteCarloResponse(
            statistics=statistics,
            percentiles=percentiles,
            probabilities=probabilities,
            distribution=distribution,
            simulations_data=all_simulations,
        )

    @staticmethod
    def _sync_simulate(request: MonteCarloRequest) -> MonteCarloResponse:
        monthly_rate, monthly_risk, months = MonteCarloService._prepare_parameters(
            request,
        )

        final_amounts, all_simulations = MonteCarloService._run_simulations(
            initial=request.initial,
            monthly_contribution=request.monthly,
            simulations=request.simulations,
            monthly_rate=monthly_rate,
            monthly_risk=monthly_risk,
            months=months,
        )

        final_array = np.array(final_amounts)

        statistics = MonteCarloService._calculate_statistics(final_array)
        percentiles = MonteCarloService._calculate_percentiles(final_array)

        total_contributions = MonteCarloService._calculate_total_contributions(
            request,
            months,
        )
        probabilities = MonteCarloService._calculate_probabilities(
            final_array=final_array,
            request=request,
            total_contributions=total_contributions,
        )

        distribution = MonteCarloService._build_distribution(final_array)

        return MonteCarloResponse(
            statistics=statistics,
            percentiles=percentiles,
            probabilities=probabilities,
            distribution=distribution,
            simulations_data=all_simulations,
        )

    @staticmethod
    def _prepare_parameters(request: MonteCarloRequest) -> tuple[float, float, int]:
        monthly_rate = request.avg_return / 100 / 12
        monthly_risk = request.risk / 100 / np.sqrt(12)
        months = request.years * 12
        return monthly_rate, monthly_risk, months

    @staticmethod
    def _run_simulations(
        initial: float,
        monthly_contribution: float,
        simulations: int,
        monthly_rate: float,
        monthly_risk: float,
        months: int,
    ) -> tuple[list[float], list[list[float]]]:
        final_amounts: list[float] = []
        all_simulations: list[list[float]] = []

        for _ in range(simulations):
            path = MonteCarloService._simulate_single_path(
                initial=initial,
                monthly_contribution=monthly_contribution,
                months=months,
                monthly_rate=monthly_rate,
                monthly_risk=monthly_risk,
            )
            final_amounts.append(path[-1])
            all_simulations.append(path)

        return final_amounts, all_simulations

    @staticmethod
    def _simulate_single_path(
        initial: float,
        monthly_contribution: float,
        months: int,
        monthly_rate: float,
        monthly_risk: float,
    ) -> list[float]:
        current_amount = initial
        path: list[float] = [current_amount]

        for _ in range(months):
            random_return = np.random.Generator().normal(monthly_rate, monthly_risk)

            current_amount += monthly_contribution
            current_amount *= 1 + random_return

            path.append(current_amount)

        return path

    @staticmethod
    def _calculate_statistics(final_array: np.ndarray) -> dict:
        return {
            "median": float(np.median(final_array)),
            "mean": float(np.mean(final_array)),
            "std": float(np.std(final_array)),
            "min": float(np.min(final_array)),
            "max": float(np.max(final_array)),
        }

    @staticmethod
    def _calculate_percentiles(final_array: np.ndarray) -> dict:
        return {
            "5": float(np.percentile(final_array, 5)),
            "10": float(np.percentile(final_array, 10)),
            "25": float(np.percentile(final_array, 25)),
            "50": float(np.percentile(final_array, 50)),
            "75": float(np.percentile(final_array, 75)),
            "90": float(np.percentile(final_array, 90)),
            "95": float(np.percentile(final_array, 95)),
        }

    @staticmethod
    def _calculate_total_contributions(
        request: MonteCarloRequest,
        months: int,
    ) -> float:
        return request.initial + (request.monthly * months)

    @staticmethod
    def _calculate_probabilities(
        final_array: np.ndarray,
        request: MonteCarloRequest,
        total_contributions: float,
    ) -> dict:
        probabilities: dict[str, float] = {
            "loss": float(np.mean(final_array < total_contributions)) * 100,
            "negative_return": float(np.mean(final_array < request.initial)) * 100,
        }

        if request.goal_amount:
            probabilities["reach_goal"] = (
                float(np.mean(final_array >= request.goal_amount)) * 100
            )

        return probabilities

    @staticmethod
    def _build_distribution(final_array: np.ndarray) -> list[dict]:
        hist, bins = np.histogram(final_array, bins=10)
        distribution: list[dict] = []

        for i in range(len(hist)):
            distribution.append(
                {
                    "range": f"{bins[i]:.0f}-{bins[i + 1]:.0f}",
                    "count": int(hist[i]),
                    "percent": float(hist[i] / len(final_array) * 100),
                },
            )

        return distribution
