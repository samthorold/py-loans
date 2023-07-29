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
from typing import Any, Iterator

from pydantic_core.core_schema import FieldValidationInfo

from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt, field_validator

from py_loans.process import ConstantValue, Process
from py_loans.roots import RootNotFound, bisect


class LoanPeriod(BaseModel):
    time_step: NonNegativeInt
    start_value: float
    interest: float
    payment: NonNegativeFloat

    @field_validator("payment")
    def validate_payment_amount(
        cls, v: NonNegativeFloat, info: FieldValidationInfo
    ) -> NonNegativeFloat:
        interest: NonNegativeFloat = info.data["interest"]
        return max(v, interest)

    @property
    def end_value(self) -> NonNegativeFloat:
        return self.start_value + self.interest - self.payment


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
    **kwargs: Any,
) -> float:
    def objective_func(flat_payment: float) -> float:
        loan_gen = loan(
            start_value=start_value,
            interest_rate_process=interest_rate_process,
            payment_process=ConstantValue(value=flat_payment),
            time_step=time_step,
            repayment_period=repayment_period,
        )
        return list(loan_gen)[-1].end_value

    try:
        root = bisect(objective_func, **kwargs)
    except RootNotFound as e:
        raise ValueError(f"Could not find flat payment.") from e

    return root.value
