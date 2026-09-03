#!/bin/python3
# Comprehensions build dicts and sets with curly brackets, which is exactly the
# ambiguity a brace-delimited language has to get right.

words = ["alpha", "beta", "gamma", "delta"]

lengths = {word: len(word) for word in words}
short = {word for word in words if len(word) <= 4}
squares = [n * n for n in range(6)]
lazy = (n * n for n in range(6))

print("dict comprehension:", lengths)
print("set comprehension:", sorted(short))
print("list comprehension:", squares)
print("generator expression consumed once:", sum(lazy))

nested = [[row * column for column in range(1, 4)] for row in range(1, 4)]
print("nested list comprehension:", nested)

flat = [value for row in nested for value in row]
print("flattened:", flat)

conditional = [n if n % 2 == 0 else -n for n in range(6)]
print("conditional expression inside:", conditional)

pairs = {(x, y) for x in range(2) for y in range(2)}
print("set of tuples:", sorted(pairs))

inverted = {value: key for key, value in lengths.items()}
print("inverted dict:", inverted)

# A comprehension can appear anywhere an expression can, including inside a block.
for threshold in [4, 5] {
    matching = [word for word in words if len(word) == threshold]
    print("  words of length {}: {}".format(threshold, matching))
}
