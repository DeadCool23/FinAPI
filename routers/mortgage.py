from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from models.schemas import MortgageRequest
from models.schemas import MortgageResponse
from services.interfaces import IFinancialCalculator


router = APIRouter()


@router.post("/", response_model=MortgageResponse)
async def calculate_mortgage(
        request_body: MortgageRequest,
        request: Request
    ) -> MortgageResponse | HTTPException:
    """Расчет ипотечного кредита

    - **price**: Стоимость недвижимости
    - **down_payment**: Первоначальный взнос
    - **years**: Срок кредита в годах (1-50)
    - **rate**: Годовая процентная ставка (0.1-99%)
    - **payment_type**: Тип платежа (annuity или differentiated)
    - **early_payments**: Досрочные погашения
    """
    try:
        fin_calc: IFinancialCalculator = request.app.state.services.fin_calc
        return fin_calc.calculate_mortgage(request_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
