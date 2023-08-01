from __future__ import annotations
from typing import Iterator

from pydantic_core.core_schema import FieldValidationInfo

from pydantic import (
    BaseModel,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    field_validator,
)

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


class LoanTerm(BaseModel):
    """Description of a period of a loan with a fixed interest rate.

    Attributes:
        rate: Interest rate.
        term: Length in periods of the LoanTerm.
        to_period: How many times a year the rate compounds.
        simple: Does the rate get converted using a simple or equivalent rate?
    """

    rate: float
    term: PositiveInt
    from_period: PositiveInt = 1
    to_period: PositiveInt = 12
    simple: bool = True


def convert_rate(
    rate: float, from_period: float = 1.0, to_period: float = 12, simple: bool = True
) -> float:
    """Convert an interest rate over one period to an equivalent rate over another period.

    `(1 + j)**to_period == (1 + i)**from_period`

    `j == (1 + i)**(from_period/to_period) - 1`

    Arguments:
        rate: Rate to convert.
        from_period: Number of times the rate compounds.
        to_period: Number of times the equivalent rate compounds.

    Examples:
        >>> rate = convert_rate(0.05, 1, 12, simple=False)
        >>> round(rate, 4)
        0.0041
        >>> rate = convert_rate(rate, 12, 1, simple=False)
        >>> round(rate, 12)
        0.05

    """
    if simple:
        return rate * from_period / to_period
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
    repayment_period: NonNegativeInt,
    time_step: NonNegativeInt = 0,
    tol: float = 1e-5,
) -> float:
    """Find the flat payment such that a loan is paid off at maturity.

    Arguments:
        start_value: Loan amount at the outset.
        interest_rate_process: Process governing the interest rate at each time step.
        repayment_period: Number of time steps until the loan matures.
        time_step: Begining time step.
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


def illustrative_mortgage(
    start_value: NonNegativeFloat,
    loan_terms: list[LoanTerm],
    repayment_period: PositiveInt = 300,
) -> list[LoanPeriod]:
    """

    Examples:
        >>> start_value = 240_000
        >>> repayment_period = 300
        >>> loan_terms = [
        ...     LoanTerm(rate=0.0519, term=24),
        ...     LoanTerm(rate=0.0779, term=1),
        ... ]
        >>> loan_periods = illustrative_mortgage(
        ...     start_value=start_value,
        ...     loan_terms=loan_terms,
        ...     repayment_period=repayment_period,
        ... )
        >>> len(loan_periods)
        300
        >>> round(loan_periods[0].payment, 2)
        1429.71
        >>> round(loan_periods[24].payment, 2)
        1794.71
        >>> round(sum(lp.payment for lp in loan_periods))
        529653
    """
    if not loan_terms:
        raise ValueError("Must provide at least one loan term.")

    time_step = 0
    loan_periods: list[LoanPeriod] = []

    for lidx, loan_term in enumerate(loan_terms):
        term_rate = convert_rate(
            rate=loan_term.rate,
            from_period=loan_term.from_period,
            to_period=loan_term.to_period,
            simple=loan_term.simple,
        )

        # find the start value of the current period
        if lidx:
            time_step = sum(lt.term for lt in loan_terms[:lidx])
            start_value = loan_periods[time_step - 1].end_value
            loan_periods = loan_periods[:time_step]

        # find the flat payment assuming the new interest rate for the
        # remainder of the loan
        payment = find_flat_payment(
            start_value=start_value,
            interest_rate_process=term_rate,
            time_step=time_step,
            repayment_period=repayment_period,
            tol=1e-5,
        )

        loan_periods += list(
            loan(
                start_value=start_value,
                interest_rate_process=term_rate,
                payment_process=payment,
                time_step=time_step,
                repayment_period=repayment_period,
            )
        )

    return loan_periods
