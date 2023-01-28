"""
Math utilities.
"""
from .types import CT


class IntervalType:
    def __init__(self, begin: CT, end: CT):
        if begin > end:
            raise ValueError("Begin must be less than end")

        if not (type(begin) is type(end)):
            raise ValueError("Begin and end must be of the same type.")

        self.begin = begin
        self.end = end

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IntervalType):
            return NotImplemented

        return self.begin == other.begin and self.end == other.end

    def __repr__(self):
        return f"<{self.__class__.__name__} begin={self.begin}, end={self.end}>"

    @classmethod
    def from_list(cls, xs) -> "IntervalType":
        if len(xs) < 2:
            raise ValueError("Interval contains two parts: begin and end.")

        begin, end = min(xs), max(xs)
        return IntervalType(begin, end)
