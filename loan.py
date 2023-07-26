"""

| Year | Starting Loan | Interest | Payment | Ending Loan |
|------|---------------|----------|---------|-------------|
|     0|            100|         5|        7|           98|
|     1|             98|         5|        7|           96|

"""

from __future__ import annotations
from collections import Counter
from typing import Callable, Iterable

from pydantic_core.core_schema import FieldValidationInfo

from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt, field_validator


class LoanMonth(BaseModel):
    time_step: NonNegativeInt
    start_value: NonNegativeFloat
    interest: NonNegativeFloat
    payment: NonNegativeFloat

    @field_validator("payment")
    def validate_payment_amount(cls, v, info: FieldValidationInfo) -> NonNegativeFloat:
        return min(
            max(v, info.data["interest"]),
            info.data["start_value"] + info.data["interest"],
        )

    @property
    def end_value(self) -> NonNegativeFloat:
        return max(0.0, self.start_value + self.interest - self.payment)


class FlatPayment(BaseModel):
    payment: NonNegativeFloat
    total: NonNegativeFloat


def loan(
    start_value: NonNegativeFloat,
    interest_rate_process: Callable[[NonNegativeInt], float],
    payment_process: Callable[[NonNegativeInt], float],
    time_step: NonNegativeInt = 0,
    repayment_period: NonNegativeInt = 25,
) -> Iterable[LoanMonth]:
    while True:
        month = LoanMonth(
            time_step=time_step,
            start_value=start_value,
            interest=start_value * interest_rate_process(time_step),
            payment=payment_process(time_step),
        )
        yield month

        loan_repaid = not month.end_value
        loan_mature = month.time_step >= (repayment_period - 1)

        if loan_repaid or loan_mature:
            break

        time_step = time_step + 1
        start_value = month.end_value


def find_flat_payment(
    start_value: NonNegativeFloat,
    interest_rate_process: Callable[[NonNegativeInt], float],
    time_step: NonNegativeInt = 0,
    repayment_period: NonNegativeInt = 25,
    payment: NonNegativeFloat = 0,
):
    while True:
        loan_gen = loan(
            start_value=start_value,
            interest_rate_process=interest_rate_process,
            payment_process=lambda t: payment,
            time_step=time_step,
            repayment_period=repayment_period,
        )
        repayment = list(loan_gen)

        yield repayment

        if not repayment[-1].end_value:
            break

        payment = repayment[-2].payment + 250


def summary_flat_payment(
    start_value: NonNegativeFloat,
    interest_rate_process: Callable[[NonNegativeInt], float],
    time_step: NonNegativeInt = 0,
    repayment_period: NonNegativeInt = 25,
    payment: NonNegativeFloat = 0,
):
    fl = find_flat_payment(
        start_value=start_value,
        interest_rate_process=interest_rate_process,
        repayment_period=repayment_period,
    )
    repayment = list(fl)[-1]
    return FlatPayment(
        payment=Counter(m.payment for m in repayment).most_common(1)[0][0],
        total=sum(m.payment for m in repayment),
    )
