from typing import Protocol
import random

class RandomGenerator(Protocol):
    def next_int(self, bound: int) -> int:
        pass

class DefaultRandomGenerator:
    def next_int(self, bound: int) -> int:
        return random.randint(0, bound - 1)
