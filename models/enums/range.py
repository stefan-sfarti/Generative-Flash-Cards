from dataclasses import dataclass

@dataclass
class Range:
    """Represents a numeric range with units"""
    min_value: float
    max_value: float
    unit: str