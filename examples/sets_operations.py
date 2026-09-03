#!/bin/python3
# Sets: the other thing curly brackets mean.

first = {1, 2, 3, 4}
second = {3, 4, 5, 6}
empty = set()

print("union:", sorted(first | second))
print("intersection:", sorted(first & second))
print("difference:", sorted(first - second))
print("symmetric difference:", sorted(first ^ second))

print("method form:", sorted(first.union(second)))
print("subset and superset:", {1, 2} <= first, first >= {1, 2})
print("disjoint:", first.isdisjoint({9, 10}))

mutable = {1, 2}
mutable.add(3)
mutable.update({4, 5})
mutable.discard(99)
mutable.remove(1)
print("after mutation:", sorted(mutable))

frozen = frozenset({1, 2, 3})
print("frozenset is hashable:", {frozen: "usable as a key"}[frozen])

print("an empty set needs set(), because {} is a dict:", type(empty).__name__, type({}).__name__)

words = ["apple", "banana", "apple", "cherry", "banana"]
print("deduplicated, order lost:", sorted(set(words)))

vowels = set("aeiou")
for word in ["rhythm", "banana"] {
    found = sorted(set(word) & vowels)
    if found {
        print("  {} contains vowels {}".format(word, found))
    } else {
        print("  {} contains no vowels".format(word))
    }
}
