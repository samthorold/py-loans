"""Dynamic processes governing loan interest and payment amounts over time."""

from typing import Protocol

from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt


class Process(Protocol):
    def step(self, t: NonNegativeInt) -> float:
        ...


class ConstantValue(BaseModel):
    value: NonNegativeFloat

    def step(self, t: NonNegativeInt) -> float:
        return self.value
