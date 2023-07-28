"""

| Year | Starting Loan | Interest | Payment | Ending Loan |
|------|---------------|----------|---------|-------------|
|     0|            100|         5|        7|           98|
|     1|             98|         5|        7|           96|

Whatever the interest rate process is believed to be at the outset of the
loan, this will change after the fixed interest period because the variable
interest rate is random.

Recalculate the flat payment every time the interest rate process experience
is different from expected.

"""

from __future__ import annotations
from collections import Counter
from typing import Callable, Iterator

from pydantic_core.core_schema import FieldValidationInfo

from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt, field_validator

from py_loans.process import ConstantValue, Process


class LoanPeriod(BaseModel):
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
    repayment: list[LoanPeriod]

    @field_validator("repayment")
    def validate_repayment(cls, v: list[LoanPeriod]) -> list[LoanPeriod]:
        if not v:
            raise ValueError("Must provide at least one LoanPeriod")
        return v


def loan(
    start_value: NonNegativeFloat,
    interest_rate_process: Process,
    payment_process: Process,
    time_step: NonNegativeInt = 0,
    repayment_period: NonNegativeInt = 25,
) -> Iterator[LoanPeriod]:
    while True:
        month = LoanPeriod(
            time_step=time_step,
            start_value=start_value,
            interest=start_value * interest_rate_process.step(time_step),
            payment=payment_process.step(time_step),
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
    interest_rate_process: Process,
    time_step: NonNegativeInt = 0,
    repayment_period: NonNegativeInt = 25,
    payment: NonNegativeFloat = 0,
    increment: float | None = None,
):
    increment = 25 if increment is None else increment

    while True:
        loan_gen = loan(
            start_value=start_value,
            interest_rate_process=interest_rate_process,
            payment_process=ConstantValue(value=payment),
            time_step=time_step,
            repayment_period=repayment_period,
        )

        repayment = list(loan_gen)

        yield FlatPayment(
            payment=Counter(m.payment for m in repayment).most_common(1)[0][0],
            total=sum(m.payment for m in repayment),
            repayment=repayment,
        )

        if not repayment[-1].end_value:
            break

        payment = repayment[-2].payment + increment
