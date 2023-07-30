from __future__ import annotations
from typing import Iterator

from pydantic_core.core_schema import FieldValidationInfo

from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt, field_validator

from py_loans.process import ConstantValue, Process
from py_loans.roots import bisect


class LoanPeriod(BaseModel):
    """A single time step in a loan repayment schedule.

    Attributes:
        time_step: Time index this step corresponds to.
        start_value: Loan amount at the beginning of the period.
        interest: Interest payable on the loan this period.
        payment: Payment made for this period. Greater than or equal to the interest.
        end_value: Loan amount at the end of this period.

    Examples:

        >>> lp = LoanPeriod(
        ... time_step=0,
        ... start_value=100,
        ... interest=5,
        ... payment=7,
        ... )
        >>> lp.end_value
        98.0
        >>> lp = LoanPeriod(
        ... time_step=0,
        ... start_value=100,
        ... interest=5,
        ... payment=4,
        ... )
        >>> lp.payment
        5.0


    """

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


def convert_rate(
    rate: float,
    from_period: float = 1.0,
    to_period: float = 12,
) -> float:
    """Convert an interest rate over one period to an equivalent rate over another period.

    `(1 + j)**to_period == (1 + i)**from_period`

    `j == (1 + i)**(from_period/to_period) - 1`

    Arguments:
        rate: Rate to convert.
        from_period: Number of times the rate compounds.
        to_period: Number of times the equivalent rate compounds.

    Examples:
        >>> rate = convert_rate(0.05, 1, 12)
        >>> round(rate, 4)
        0.0041
        >>> rate = convert_rate(rate, 12, 1)
        >>> round(rate, 12)
        0.05

    """
    return float((1 + rate) ** (from_period / to_period) - 1)


def loan(
    start_value: NonNegativeFloat,
    interest_rate_process: Process | float,
    payment_process: Process | float,
    time_step: NonNegativeInt = 0,
    repayment_period: NonNegativeInt = 25,
) -> Iterator[LoanPeriod]:
    """Generate loan repayments until the term of the loan.

    Arguments:
        start_value: Loan amount at the outset.
        interest_rate_process: Process governing the interest rate at each time step.
        payment_process: Process governing the payments at each time step.
        time_step: Begining time step.
        repayment_period: Number of time steps until the loan matures.

    Examples:

        >>> repayment_process = loan(
        ... start_value=100,
        ... interest_rate_process=0.05,
        ... payment_process=7,
        ... )
        >>> next(repayment_process)
        LoanPeriod(time_step=0, start_value=100.0, interest=5.0, payment=7.0)
        >>> next(repayment_process)
        LoanPeriod(time_step=1, start_value=98.0, interest=4.9, payment=7.0)
    """

    if isinstance(interest_rate_process, (int, float)):
        interest_rate_process = ConstantValue(value=interest_rate_process)
    if isinstance(payment_process, (int, float)):
        payment_process = ConstantValue(value=payment_process)

    while True:
        month = LoanPeriod(
            time_step=time_step,
            start_value=start_value,
            interest=start_value * interest_rate_process.step(time_step),
            payment=payment_process.step(time_step),
        )
        yield month

        if month.time_step >= (repayment_period - 1):
            break

        time_step = time_step + 1
        start_value = month.end_value


def find_flat_payment(
    start_value: NonNegativeFloat,
    interest_rate_process: Process | float,
    time_step: NonNegativeInt = 0,
    repayment_period: NonNegativeInt = 25,
    tol: float = 5,
) -> float:
    """Find the flat payment such that a loan is paid off at maturity.

    Arguments:
        start_value: Loan amount at the outset.
        interest_rate_process: Process governing the interest rate at each time step.
        time_step: Begining time step.
        repayment_period: Number of time steps until the loan matures.
        tol: Tolerance within which the root finding algorithm has converged.

    Examples:

        >>> payment = find_flat_payment(
        ... start_value=100,
        ... interest_rate_process=0.0,
        ... repayment_period=25,
        ... tol=0.01,
        ... )
        >>> round(payment, 2)
        4.0
        >>> payment = find_flat_payment(
        ... start_value=100,
        ... interest_rate_process=0.05,
        ... repayment_period=25,
        ... tol=0.01,
        ... )
        >>> round(payment, 2)
        7.1

    """

    def objective_func(flat_payment: float) -> float:
        loan_gen = loan(
            start_value=start_value,
            interest_rate_process=interest_rate_process,
            payment_process=ConstantValue(value=flat_payment),
            time_step=time_step,
            repayment_period=repayment_period,
        )
        repayment = list(loan_gen)
        return repayment[-1].end_value

    root = bisect(objective_func, a=0, b=start_value, tol=tol)

    if not root.converged:
        raise ValueError(f"Could not find payment. {root}")

    return root.value
