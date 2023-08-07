from __future__ import annotations
from typing import Iterator

from pydantic_core.core_schema import FieldValidationInfo

from pydantic import (
    BaseModel,
    NonNegativeInt,
    PositiveInt,
    field_validator,
    computed_field,
)

from py_loans.process import ConstantValue, Process
from py_loans.roots import bisect


class RepaymentPeriod(BaseModel):
    """A single time step in a loan repayment schedule.

    Attributes:
        time_step: Time index this step corresponds to.
        start_value: Loan amount at the beginning of the period.
        interest: Interest payable on the loan this period.
        payment: Payment made for this period. Greater than or equal to the interest.
        end_value: Loan amount at the end of this period.

    Examples:

        >>> lp = RepaymentPeriod(
        ...     time_step=0,
        ...     start_value=100,
        ...     interest=5,
        ...     payment=-7,
        ... )
        >>> lp.end_value
        98.0
        >>> lp = RepaymentPeriod(
        ...     time_step=0,
        ...     start_value=100,
        ...     interest=5,
        ...     payment=-4,
        ... )
        >>> lp.payment
        -5.0


    """

    time_step: NonNegativeInt
    start_value: float
    interest: float
    payment: float

    @field_validator("payment")
    def validate_payment_amount(cls, v: float, info: FieldValidationInfo) -> float:
        interest: float = info.data["interest"]
        return min(v, -interest)

    @computed_field  # type: ignore[misc]
    @property
    def end_value(self) -> float:
        return self.start_value + self.interest + self.payment


class RepaymentSchedule(BaseModel):
    periods: list[RepaymentPeriod]

    def __len__(self) -> int:
        return len(self.periods)

    def __getitem__(self, i: int) -> RepaymentPeriod:
        return self.periods[i]

    @computed_field  # type: ignore[misc]
    @property
    def interest(self) -> float:
        return sum(rp.interest for rp in self.periods)

    @computed_field  # type: ignore[misc]
    @property
    def total(self) -> float:
        return sum(rp.payment for rp in self.periods)


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
    start_value: float,
    interest_rate_process: Process | float,
    payment_process: Process | float,
    time_step: NonNegativeInt = 0,
    repayment_period: NonNegativeInt = 25,
) -> Iterator[RepaymentPeriod]:
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
        ... payment_process=-7,
        ... )
        >>> next(repayment_process)
        RepaymentPeriod(time_step=0, start_value=100.0, interest=5.0, payment=-7.0, end_value=98.0)
        >>> next(repayment_process)
        RepaymentPeriod(time_step=1, start_value=98.0, interest=4.9, payment=-7.0, end_value=95.9)
    """

    if isinstance(interest_rate_process, (int, float)):
        interest_rate_process = ConstantValue(value=interest_rate_process)
    if isinstance(payment_process, (int, float)):
        payment_process = ConstantValue(value=payment_process)

    while True:
        month = RepaymentPeriod(
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
    start_value: float,
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
        -4.0
        >>> payment = find_flat_payment(
        ... start_value=100,
        ... interest_rate_process=0.05,
        ... repayment_period=25,
        ... tol=0.01,
        ... )
        >>> round(payment, 2)
        -7.1

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

    root = bisect(objective_func, a=-start_value, b=0, tol=tol)

    if not root.converged:
        raise ValueError(f"Could not find payment. {root}")

    return root.value


class IllustrativeMortgage(BaseModel):
    """Illustrative mortgage repayment schedule.

    Assumes constant payments and interest rates over a series of time periods.

    Attributes:
        start_value: Loan amount at the outset.
        loan_terms: The periods of constant payments and interest rates.
        repayment_period: Number of time steps until the loan matures.

    """

    start_value: float
    loan_terms: list[LoanTerm]
    repayment_period: PositiveInt = 300

    @field_validator("loan_terms")
    def validate_loan_terms(cls, v: list[LoanTerm]) -> list[LoanTerm]:
        if not v:
            raise ValueError("Must provide at least one loan term.")
        return v

    def calculate(self) -> RepaymentSchedule:
        start_value = self.start_value
        loan_terms = self.loan_terms
        repayment_period = self.repayment_period

        time_step = 0
        loan_periods: list[RepaymentPeriod] = []

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

        return RepaymentSchedule(periods=loan_periods)
