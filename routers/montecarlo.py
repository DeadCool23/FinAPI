from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from models.schemas import MonteCarloRequest
from models.schemas import MonteCarloResponse
from services.interfaces import IMonteCarloService


router = APIRouter()


@router.post("/", response_model=MonteCarloResponse)
async def run_monte_carlo(
        request_body: MonteCarloRequest,
        request: Request
    ) -> MonteCarloResponse | HTTPException:
    """Симуляция Монте-Карло для инвестиций

    - **initial**: Начальный капитал
    - **monthly**: Ежемесячное пополнение
    - **years**: Срок моделирования (1-50)
    - **avg_return**: Средняя годовая доходность
    - **risk**: Риск (стандартное отклонение)
    - **simulations**: Количество симуляций (100-10000)
    - **goal_amount**: Целевая сумма
    """
    try:
        montecarlo_service: IMonteCarloService = request.app.state.services.montecarlo_service
        return await montecarlo_service.simulate(request_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
