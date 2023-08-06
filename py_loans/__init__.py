"""

| Year | Starting Loan | Interest | Payment | Ending Loan |
|-----:|--------------:|---------:|--------:|------------:|
|     0|            100|         5|        7|           98|
|     1|             98|         5|        7|           96|


**APRC**: annual percentage rate of charge. The total value of principal + interest + other fees expressed as an annual percentage.

There is an interest rate process that is contractually, or assumed to be, fixed for typically 3 different
time periods of the mortgage's term.

- Fixed term: e.g. 24 months at a low introductory offer
- Intermediary term: e.g. 12 months at a higher rate
- Remainder: e.g. 264 months at another rate.

The total cost of the mortgage is calculated by finding the implied flat payment across each term.

1. Find the start value of the term using the payments over the prior calculated period at the new interest rate.
2. Find the flat payment assuming the new interest rate over the remainder of the loan.

"""
