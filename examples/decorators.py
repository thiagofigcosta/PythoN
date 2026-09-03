#!/bin/python3
# Decorators, including ones that take arguments and ones that stack.

import functools


def announce(function) {
    @functools.wraps(function)
    def wrapper(*args, **kwargs) {
        print("  -> {}".format(function.__name__))
        return function(*args, **kwargs)
    }
    return wrapper
}


def repeat(times) {
    def decorator(function) {
        @functools.wraps(function)
        def wrapper(*args, **kwargs) {
            results = []
            for _ in range(times) {
                results.append(function(*args, **kwargs))
            }
            return results
        }
        return wrapper
    }
    return decorator
}


def memoize(function) {
    cache = {}

    @functools.wraps(function)
    def wrapper(argument) {
        if argument not in cache {
            cache[argument] = function(argument)
        }
        return cache[argument]
    }
    wrapper.cache = cache
    return wrapper
}


@announce
def greet(name) {
    return "hello {}".format(name)
}


@repeat(3)
def roll() {
    return 4
}


@memoize
def slow_square(n) {
    print("    computing {}".format(n))
    return n * n
}


print(greet("world"))
print("name survives the decorator:", greet.__name__)
print("stacked and parametrised:", roll())
slow_square(6)
print("second call is cached:", slow_square(6))
print("cache contents:", slow_square.cache)
