import pytest

from py_loans.loan import FlatPayment, LoanPeriod


def test_flat_payment_has_loan_months() -> None:
    with pytest.raises(ValueError, match="Must provide at least one LoanPeriod"):
        FlatPayment(payment=1, total=1, repayment=[])

    FlatPayment(
        payment=1,
        total=1,
        repayment=[LoanPeriod(time_step=0, start_value=100, interest=5, payment=7)],
    )
