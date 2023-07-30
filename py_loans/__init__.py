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

"""
