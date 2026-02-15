from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from models.schemas import SavingsRequest
from models.schemas import SavingsResponse
from services.interfaces import IFinancialCalculator


router = APIRouter()


@router.post("/", response_model=SavingsResponse)
async def calculate_savings(
        request_body: SavingsRequest,
        request: Request
    ) -> SavingsResponse | HTTPException:
    """Расчет накоплений со сложным процентом

    - **initial**: Начальная сумма
    - **monthly**: Ежемесячное пополнение
    - **years**: Срок в годах (1-100)
    - **rate**: Годовая процентная ставка (0-50%)
    - **capitalization**: Тип капитализации
    - **tax_rate**: Ставка налога на доход
    - **inflation**: Ожидаемая инфляция
    """
    try:
        fin_calc: IFinancialCalculator = request.app.state.services.fin_calc
        return fin_calc.calculate_savings(request_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
