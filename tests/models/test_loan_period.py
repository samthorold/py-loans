import pytest

from py_loans.loan import LoanPeriod


def test_loan_period_end_value() -> None:
    start_value = 100
    interest = 5
    payment = 7

    expected = start_value + interest - payment

    loan_period = LoanPeriod(
        time_step=0, start_value=start_value, interest=interest, payment=payment
    )

    got = loan_period.end_value

    assert got == expected, loan_period


@pytest.mark.parametrize(
    "start_value,interest,payment,expected",
    (
        (100, 5, 7, 7),
        (100, 5, 4, 5),
        (1, 1, 4, 2),
    ),
)
def test_loan_period_payment(
    start_value: float, interest: float, payment: float, expected: float
) -> None:
    loan_period = LoanPeriod(
        time_step=0, start_value=start_value, interest=interest, payment=payment
    )
    assert loan_period.payment == expected, loan_period
