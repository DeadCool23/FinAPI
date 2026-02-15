from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from models.schemas import GoalRequest
from models.schemas import GoalResponse
from services.interfaces import IFinancialCalculator


router = APIRouter()


@router.post("/", response_model=GoalResponse)
async def calculate_goal(
        request_body: GoalRequest,
        request: Request
    ) -> GoalResponse | HTTPException:
    """Расчет необходимых взносов для достижения цели

    - **goal_amount**: Целевая сумма
    - **current_savings**: Текущие накопления
    - **years**: Срок в годах
    - **expected_rate**: Ожидаемая доходность
    - **monthly_contribution**: Фиксированный платеж (если None - рассчитывается)
    """
    try:
        fin_calc: IFinancialCalculator = request.app.state.services.fin_calc
        return fin_calc.calculate_goal(request_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
