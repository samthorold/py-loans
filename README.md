
https://onladder.co.uk/blog/how-to-calculate-mortgage-repayments/

https://www.handbook.fca.org.uk/handbook/MCOB/10A/2.pdf

`find_flat_payment(235_000, convert_rate(0.0493, 1, 12), repayment_period=25*12-1, tol=0.1)`

- Interest rate values are the annual examples over 12 (not the actual rate conversion).
- Find the example monthly payment by assuming the example interest rate holds for the remainder of the loan.
    - Initial rate for whole loan -> monthly payment.
    - For next example rate, assume previous rate paid for example period and to find the starting balance for the next interest rate process. Assume this process correct for remainder of the loan -> monthly payment.
    - Repeat.