#!/bin/python3
# Functional building blocks: map, filter, reduce, partial, operator.

import functools
import operator

numbers = [1, 2, 3, 4, 5, 6]

doubled = list(map(lambda n: n * 2, numbers))
evens = list(filter(lambda n: n % 2 == 0, numbers))
total = functools.reduce(operator.add, numbers)
product = functools.reduce(operator.mul, numbers, 1)

print("map:", doubled)
print("filter:", evens)
print("reduce to a sum:", total)
print("reduce to a product:", product)

def power(base, exponent) {
    return base ** exponent
}

square = functools.partial(power, exponent=2)
cube = functools.partial(power, exponent=3)
print("partial application:", square(7), cube(3))

print("operator module instead of lambdas:", list(map(operator.neg, numbers)))
print("zip and map together:", list(map(operator.add, [1, 2, 3], [10, 20, 30])))

pipeline = [str.strip, str.lower, str.title]
value = "   hELLO wORLD   "
for step in pipeline {
    value = step(value)
}
print("applied a pipeline of functions:", repr(value))

@functools.lru_cache(maxsize=None)
def fibonacci(n) {
    if n < 2 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

print("lru_cache makes naive recursion fast:", fibonacci(30))
print("cache statistics:", fibonacci.cache_info().hits > 0)
