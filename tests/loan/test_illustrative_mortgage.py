import pytest

from py_loans.loan import LoanTerm, IllustrativeMortgage


def test_illustrative_mortgage_no_loan_terms() -> None:
    with pytest.raises(ValueError, match="Must provide at least one loan term."):
        IllustrativeMortgage(start_value=0, loan_terms=[])


def test_illustrative_mortgage() -> None:
    start_value = 240_000
    repayment_period = 300
    loan_terms = [
        LoanTerm(rate=0.0519, term=24),
        LoanTerm(rate=0.0779, term=1),
    ]

    expected_total = 529_653

    repayment = IllustrativeMortgage(
        start_value=start_value,
        loan_terms=loan_terms,
        repayment_period=repayment_period,
    ).calculate()
    assert len(repayment) == 300
    assert round(repayment[0].payment, 2) == 1429.71
    assert round(repayment[24].payment, 2) == 1794.71
    assert round(repayment.interest) == (expected_total - start_value)
    assert round(repayment.total) == expected_total


def test_illustrative_mortgage_3_terms() -> None:
    start_value = 240_000
    repayment_period = 300
    loan_terms = [
        LoanTerm(rate=0.0493, term=24),
        LoanTerm(rate=0.0675, term=36),
        LoanTerm(rate=0.0849, term=1),
    ]

    expected_total = 541_800

    repayment = IllustrativeMortgage(
        start_value=start_value,
        loan_terms=loan_terms,
        repayment_period=repayment_period,
    ).calculate()
    assert len(repayment) == 300
    assert round(repayment[0].payment, 2) == 1393.25
    assert round(repayment[24].payment, 2) == 1641.37
    assert round(repayment[24 + 36].payment, 2) == 1871.97
    assert abs(round(repayment.interest) - (expected_total - start_value)) <= 1
    assert abs(round(repayment.total) - expected_total) <= 1, repayment.total
