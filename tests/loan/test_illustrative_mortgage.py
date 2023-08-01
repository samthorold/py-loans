import pytest

from py_loans.loan import LoanTerm, illustrative_mortgage


def test_illustrative_mortgage_no_loan_terms() -> None:
    with pytest.raises(ValueError, match="Must provide at least one loan term."):
        illustrative_mortgage(0, [])


def test_illustrative_mortgage() -> None:
    start_value = 240_000
    repayment_period = 300
    loan_terms = [
        LoanTerm(rate=0.0519, term=24),
        LoanTerm(rate=0.0779, term=1),
    ]
    loan_periods = illustrative_mortgage(
        start_value=start_value,
        loan_terms=loan_terms,
        repayment_period=repayment_period,
    )
    assert len(loan_periods) == 300
    assert round(loan_periods[0].payment, 2) == 1429.71
    assert round(loan_periods[24].payment, 2) == 1794.71
    assert round(sum(lp.payment for lp in loan_periods)) == 529653


def test_illustrative_mortgage_3_terms() -> None:
    start_value = 240_000
    repayment_period = 300
    loan_terms = [
        LoanTerm(rate=0.0493, term=24),
        LoanTerm(rate=0.0675, term=36),
        LoanTerm(rate=0.0849, term=1),
    ]
    loan_periods = illustrative_mortgage(
        start_value=start_value,
        loan_terms=loan_terms,
        repayment_period=repayment_period,
    )
    assert len(loan_periods) == 300
    assert round(loan_periods[0].payment, 2) == 1393.25
    assert round(loan_periods[24].payment, 2) == 1641.37
    assert round(loan_periods[24 + 36].payment, 2) == 1871.97
    assert (
        abs(round(sum(lp.payment for lp in loan_periods)) - (542939 - 1139)) <= 1
    ), round(sum(lp.payment for lp in loan_periods))
