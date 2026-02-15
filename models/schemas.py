from __future__ import annotations

from typing import Any
from typing import Self

from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator

from models.enums import CapitalizationType
from models.enums import ComparisonType
from models.enums import PaymentType


class MortgageRequest(BaseModel):
    """Запрос для расчета ипотечного кредита"""

    price: float = Field(
        gt=0,
        description="Полная стоимость недвижимости в рублях",
    )
    down_payment: float = Field(
        ge=0,
        description="Первоначальный взнос в рублях",
    )
    years: int = Field(
        ge=1,
        le=50,
        description="Срок кредита в полных годах",
    )
    rate: float = Field(
        ge=0.1,
        le=99,
        description="Годовая процентная ставка в процентах",
    )
    payment_type: PaymentType = Field(
        default=PaymentType.ANNUITY,
        description="Тип графика платежей",
    )

    @model_validator(mode="after")
    def down_payment_less_than_price(self) -> Self:
        if self.down_payment >= self.price:
            raise ValueError(
                "Первоначальный взнос должен быть меньше стоимости недвижимости",
            )
        return self


class MortgageMonthPayment(BaseModel):
    """Месячные данные платежей по ипотеке"""

    month: int = Field(
        description="Месяц оплаты",
    )
    payment: float = Field(
        description="Сумма платежа в этом месяце",
    )
    principal: float = Field(
        description="Часть платежа на погашение тела кредита",
    )
    interest: float = Field(
        description="Часть платежа на проценты",
    )
    balance: float = Field(
        description="Остаток долга после платежа",
    )


class MortgageResponse(BaseModel):
    """Ответ с результатами расчета ипотеки"""

    loan_amount: float = Field(
        description="Сумма кредита",
    )
    monthly_payment: float = Field(
        description="Ежемесячный платеж в рублях",
    )
    total_payment: float = Field(
        description="Общая сумма всех платежей за весь срок кредита в рублях",
    )
    total_interest: float = Field(
        description="Общая сумма переплаты по процентам в рублях",
    )
    payment_schedule: list[MortgageMonthPayment] = Field(
        description="Детальный график платежей по месяцам",
    )


class SavingsRequest(BaseModel):
    """Запрос для расчета накоплений со сложным процентом"""

    initial: float = Field(
        ge=0,
        description="Начальная сумма на счете в рублях",
    )
    monthly: float = Field(
        ge=0,
        description="Сумма ежемесячного пополнения в рублях",
    )
    years: int = Field(
        ge=1,
        le=100,
        description="Срок накоплений в полных годах",
    )
    rate: float = Field(
        ge=0,
        le=50,
        description="Годовая процентная ставка в процентах",
    )
    capitalization: CapitalizationType = Field(
        default=CapitalizationType.MONTHLY,
        description="Частота капитализации процентов",
    )
    tax_rate: float = Field(
        default=0,
        ge=0,
        le=99,
        description="Ставка налога на доход в процентах",
    )
    inflation: float = Field(
        default=0,
        ge=0,
        le=99,
        description="Ожидаемая годовая инфляция",
    )


class SavingsYear(BaseModel):
    """Годовой отчет о накоплениях"""

    year: int = Field(
        description="Номер года",
    )
    amount: float = Field(
        description="Сумма на конец года",
    )
    contributions: float = Field(
        description="Вложения за год",
    )
    interest: float = Field(
        description="Начисленные проценты за год",
    )


class SavingsResponse(BaseModel):
    """Ответ с результатами расчета накоплений"""

    final_amount_nominal: float = Field(
        description="Итоговая сумма на счете без учета инфляции",
    )
    final_amount_real: float = Field(
        description="Итоговая сумма с учетом инфляции",
    )
    total_contributions: float = Field(
        description="Всего внесено собственных средств",
    )
    total_interest: float = Field(
        description="Всего начислено процентов",
    )
    total_tax: float = Field(
        description="Сумма уплаченного налога на доход",
    )
    yearly_breakdown: list[SavingsYear] = Field(
        description="Годовой отчет о накоплениях",
    )


class CreditRequest(BaseModel):
    """Запрос для расчета потребительского кредита"""

    amount: float = Field(
        gt=0,
        description="Сумма кредита в рублях",
    )
    years: float = Field(
        ge=0.25,
        le=30,
        description="Срок кредита в годах",
    )
    rate: float = Field(
        ge=0,
        le=99,
        description="Годовая процентная ставка в процентах",
    )
    payment_type: PaymentType = Field(
        default=PaymentType.ANNUITY,
        description="Тип графика платежей",
    )
    commission: float = Field(
        default=0,
        ge=0,
        le=99,
        description="Единовременная комиссия в процентах от суммы кредита",
    )
    insurance: float = Field(
        default=0,
        ge=0,
        le=99,
        description="Годовая страховка в процентах от суммы кредита",
    )
    payment_day: int = Field(
        default=15,
        ge=1,
        le=31,
        description="Число месяца, когда производится платеж",
    )


class CreditMonthPayment(MortgageMonthPayment):
    """Месячные данные платежей по кредиту"""

    fees: float = Field(
        description="Дополнительные сборы в этом месяце",
    )


class CreditResponse(BaseModel):
    """Ответ с результатами расчета кредита"""

    monthly_payment: float = Field(
        description="Ежемесячный платеж в рублях",
    )
    total_payment: float = Field(
        description="Общая сумма всех выплат за весь срок",
    )
    total_interest: float = Field(
        description="Сумма выплаченных процентов",
    )
    effective_rate: float = Field(
        description="Эффективная процентная ставка (ПСК) в процентах",
    )
    commission_amount: float = Field(
        description="Сумма единовременной комиссии",
    )
    payment_schedule: list[CreditMonthPayment] = Field(
        description="График платежей",
    )


class GoalRequest(BaseModel):
    """Запрос для расчета достижения финансовой цели"""

    goal_amount: float = Field(
        gt=0,
        description="Желаемая сумма в будущем в рублях",
    )
    current_savings: float = Field(
        ge=0,
        description="Текущие накопления в рублях",
    )
    years: int = Field(
        ge=1,
        le=100,
        description="Срок достижения цели в полных годах",
    )
    expected_rate: float = Field(
        ge=0,
        le=99,
        description="Ожидаемая годовая доходность инвестиций в процентах",
    )
    monthly_contribution: float | None = Field(
        default=None,
        ge=0,
        description="Фиксированная сумма ежемесячного пополнения в рублях",
    )


class GoalMonth(BaseModel):
    """Месяц накоплений"""

    month: int = Field(
        description="Месяц оплаты",
    )
    amount: float = Field(
        description="Итоговая сумма на счете к концу месяца",
    )
    contributions: float = Field(
        description="Сумма взноса",
    )
    interest: float = Field(
        description="Проценты, начисленные за этот месяц",
    )


class GoalResponse(BaseModel):
    """Ответ с результатами расчета цели"""

    required_monthly: float | None = Field(
        default=None,
        description="Необходимый ежемесячный взнос в рублях",
    )
    expected_final_amount: float | None = Field(
        default=None,
        description="Ожидаемая конечная сумма в рублях",
    )
    monthly_breakdown: list[GoalMonth] = Field(
        description="Помесячный план накоплений",
    )


class MonteCarloRequest(BaseModel):
    """Запрос для симуляции Монте-Карло"""

    initial: float = Field(
        ge=0,
        description="Начальный капитал в рублях",
    )
    monthly: float = Field(
        ge=0,
        description="Ежемесячное пополнение инвестиций в рублях",
    )
    years: int = Field(
        ge=1,
        le=50,
        description="Срок моделирования в полных годах",
    )
    avg_return: float = Field(
        ge=-50,
        le=99,
        description="Средняя годовая доходность в процентах",
    )
    risk: float = Field(
        ge=0,
        le=99,
        description="Стандартное отклонение доходности (риск) в процентах",
    )
    simulations: int = Field(
        default=1000,
        ge=10,
        le=10000,
        description="Количество случайных сценариев для симуляции",
    )
    goal_amount: float | None = Field(
        default=None,
        gt=0,
        description="Целевая сумма в рублях для расчета вероятности достижения",
    )


class MonteCarloResponse(BaseModel):
    """Ответ с результатами симуляции Монте-Карло"""

    statistics: dict = Field(
        description="Основные статистики результатов",
    )
    percentiles: dict = Field(
        description="Процентили распределения результатов",
    )
    probabilities: dict = Field(
        description="Вероятности различных событий в процентах",
    )
    distribution: list[dict] = Field(
        description="Распределение результатов по диапазонам",
    )
    simulations_data: list[list[float]] | None = Field(
        default=None,
        description="Сырые данные симуляций для построения графиков",
    )


class ComparisonScenario(BaseModel):
    """Модель сценария для сравнения"""

    name: str = Field(
        description="Название сценария для отображения в результатах",
    )
    data: MortgageRequest | CreditRequest | SavingsRequest | GoalRequest = Field(
        description="Данные сценария",
    )


class CompareRequest(BaseModel):
    """Запрос для сравнения двух финансовых продуктов"""

    type: ComparisonType = Field(
        description="Тип сравнения",
    )
    scenarios: list[ComparisonScenario] = Field(
        min_items=2,
        max_items=10,
        description="Сценарии сравнения сравнения",
    )


class CompareResponse(BaseModel):
    """Ответ с результатами сравнения"""

    type: str = Field(
        description="Тип сравнения",
    )
    comparison: list[dict[str, Any]] = Field(
        description="""Результаты расчета для каждого сценария""",
    )
    recommendation: str = Field(
        description="Рекомендованный сценарий",
    )
