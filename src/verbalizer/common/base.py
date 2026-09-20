from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic, TypeVar

T_in = TypeVar("T_in")
T_out = TypeVar("T_out")


class VerbalizerMode(Enum):
    STANDARD = "standard"
    TECHNICAL = "technical"


class BaseConverter(ABC, Generic[T_in, T_out]):
    """Abstract base class for all verbalizer converters."""

    def __init__(self, mode: VerbalizerMode = VerbalizerMode.STANDARD):
        self.mode = mode

    @abstractmethod
    def convert(self, item: T_in) -> T_out:
        """Convert input item to target representation."""