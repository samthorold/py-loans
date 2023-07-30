"""

| Year | Starting Loan | Interest | Payment | Ending Loan |
|-----:|--------------:|---------:|--------:|------------:|
|     0|            100|         5|        7|           98|
|     1|             98|         5|        7|           96|

Whatever the interest rate process is believed to be at the outset of the
loan, this will change after the fixed interest period because the variable
interest rate is random.

Recalculate the flat payment every time the interest rate process experience
is different from expected.

**APRC**: annual percentage rate of charge. The total value of principal + interest + other fees expressed as an annual percentage.

    >>> from py_loans.loan import find_flat_payment, loan
    >>> find_flat_payment(235_000, 0.0493/12, repayment_period=300, tol=1e-5)
    1364.219468232477
    >>> list(loan(235_000, 0.0675/12, 1364.22, repayment_period=300))[23]
    LoanPeriod(time_step=23, start_value=233963.36176005268, interest=1316.0439099002965, payment=1364.22)
    >>> list(loan(235_000, 0.0675/12, 1364.22, repayment_period=300))[23].end_value
    233915.18566995297
    >>> find_flat_payment(235_000, 0.0493/12, repayment_period=300-24, tol=1e-5)
    1425.0816350977402
    >>> find_flat_payment(233915.18566995297, 0.0675/12, repayment_period=300-24, tol=1e-5)
    1671.1220021973918
    >>> find_flat_payment(235_000, 0.0493/12, repayment_period=300-24, tol=1e-5)
    1425.0816350977402
    >>> find_flat_payment(235_000, 0.0493/12, repayment_period=300, tol=1e-5)
    1364.219468232477
    >>> list(loan(235_000, 0.0493/12, 1364.22, repayment_period=300))[23].end_value
    224963.6429839241
    >>> find_flat_payment(_, 0.0675/12, repayment_period=300-24, tol=1e-5)
    1607.170959885249
    >>> list(loan(224963.6429839241, 0.0675/12, _, repayment_period=300-24))[35].end_value
    211368.62599896963
    >>> find_flat_payment(_, 0.0849/12, repayment_period=300-24-36, tol=1e-5)
    1832.968484995391

"""
