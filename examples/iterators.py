#!/bin/python3
# Iteration protocol: iter, next, and writing your own iterable.

numbers = [10, 20, 30]
cursor = iter(numbers)
print("next:", next(cursor), next(cursor), next(cursor))
print("exhausted returns the default:", next(cursor, "done"))


class Countdown {
    def __init__(self, start) {
        self.start = start
    }

    def __iter__(self) {
        self.current = self.start
        return self
    }

    def __next__(self) {
        if self.current <= 0 {
            raise StopIteration
        }
        self.current -= 1
        return self.current + 1
    }
}

print("custom iterator:", list(Countdown(4)))

for index, letter in enumerate("abc", start=1) {
    print("  enumerate {} -> {}".format(index, letter))
}

for left, right in zip([1, 2, 3], "xyz") {
    print("  zip {} with {}".format(left, right))
}

print("reversed:", list(reversed([1, 2, 3])))
print("any and all:", any(n > 2 for n in numbers), all(n > 2 for n in numbers))
print("min, max, sum:", min(numbers), max(numbers), sum(numbers))
print("sorted by last digit:", sorted([31, 12, 23], key=lambda n: n % 10))
