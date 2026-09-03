#!/bin/python3
# Type hints. They are annotations, so they never change what runs.

from typing import Any, Callable, Iterator, Optional, Union

Number = Union[int, float]


def add(left: Number, right: Number) -> Number {
    return left + right
}


def find(values: list, target: Any) -> Optional[int] {
    for index, value in enumerate(values) {
        if value == target {
            return index
        }
    }
    return None
}


def apply_twice(function: Callable[[int], int], value: int) -> int {
    return function(function(value))
}


def countdown(start: int) -> Iterator[int] {
    while start > 0 {
        yield start
        start -= 1
    }
}


class Box {
    contents: dict
    label: str = "unlabelled"

    def __init__(self, contents: dict, label: str = "unlabelled") -> None {
        self.contents = contents
        self.label = label
    }

    def get(self, key: str, default: Any = None) -> Any {
        return self.contents.get(key, default)
    }
}


print("annotated function:", add(2, 3.5))
print("optional return, found:", find(["a", "b", "c"], "b"))
print("optional return, missing:", find(["a"], "z"))
print("callable parameter:", apply_twice(lambda n: n * 3, 2))
print("annotated generator:", list(countdown(4)))

box = Box({"key": "value"}, label="crate")
print("annotated class:", box.label, box.get("key"), box.get("absent", "fallback"))

print("annotations are introspectable:", add.__annotations__["return"])
print("they do not enforce anything at runtime:", add("a", "b"))
