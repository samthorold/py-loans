"""Dynamic processes governing loan interest and payment amounts over time."""

from typing import Protocol

from pydantic import BaseModel, NonNegativeInt


class Process(Protocol):
    """Interface defining a Process."""

    def step(self, t: NonNegativeInt) -> float:
        """Process value for this time step.

        Arguments:
            t: Time step.

        """
        ...


class ConstantValue(BaseModel):
    """Process that returns the same value every time step.

    Attributes:
        value: Constant value to return every time step.

    Examples:
        >>> process = ConstantValue(value=7)
        >>> process.step(0)
        7.0
        >>> process.step(100)
        7.0


    """

    value: float

    def step(self, t: NonNegativeInt) -> float:
        """Return the constant value."""
        return self.value
