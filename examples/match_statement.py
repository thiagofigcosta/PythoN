#!/bin/python3
# `match` and `case` are SOFT keywords: they head a match statement, and they are
# also perfectly legal variable names. Both readings appear in this file.

def classify(value) {
    match value {
        case 0 {
            return "zero"
        }
        case [a, b] {
            return "a pair: {} and {}".format(a, b)
        }
        case [first, *rest] if len(rest) > 1 {
            return "a long list starting with {}".format(first)
        }
        case {"kind": kind} {
            return "a mapping of kind {}".format(kind)
        }
        case str() {
            return "a string"
        }
        case _ {
            return "something else"
        }
    }
}

for value in [0, [1, 2], [1, 2, 3, 4], {"kind": "config"}, "text", 3.5] {
    print("  {!r:24} -> {}".format(value, classify(value)))
}

# The same words used as ordinary identifiers, in the same file.
import re

match = re.match(r"(\d+)-(\d+)", "12-34")
if match {
    print("re.match result:", match.groups())
}

match = {"still": "just a dictionary"}
print("match as a dict:", match)

case = ["and", "case", "is", "a", "list"]
print("case as a list:", " ".join(case))

match[len(case)] = "subscript assignment on a variable named match"
print("subscripted:", match[5])

matches = {n: n % 2 == 0 for n in range(4)}
print("a name that merely starts with match:", matches)
