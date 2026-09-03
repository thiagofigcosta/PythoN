#!/bin/python3
# Recursion, including the shapes where a nested dict and a nested block appear
# in the same function.

import sys


def factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}


def fibonacci(n, memo={}) {
    if n in memo {
        return memo[n]
    }
    if n < 2 {
        result = n
    } else {
        result = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    }
    memo[n] = result
    return result
}


def depth_of(value) {
    if isinstance(value, dict) {
        if not value {
            return 1
        }
        return 1 + max(depth_of(inner) for inner in value.values())
    }
    return 0
}


def flatten(nested) {
    flat = []
    for item in nested {
        if isinstance(item, list) {
            flat.extend(flatten(item))
        } else {
            flat.append(item)
        }
    }
    return flat
}


def walk(tree, prefix="") {
    for key in sorted(tree) {
        print("  {}{}".format(prefix, key))
        if isinstance(tree[key], dict) {
            walk(tree[key], prefix + "  ")
        }
    }
}


print("factorial:", factorial(6))
print("memoised fibonacci:", fibonacci(40))
print("recursion limit is generous:", sys.getrecursionlimit() >= 1000)

tree = {"a": {"b": {"c": {}}}, "d": {}}
print("depth of a nested dict:", depth_of(tree))
print("flattened:", flatten([1, [2, [3, [4]], 5], 6]))
print("walking the tree:")
walk(tree)
