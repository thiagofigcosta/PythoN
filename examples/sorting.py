#!/bin/python3
# Sorting: keys, reverse, stability, and sorting things that are not numbers.

import operator

people = [
    {"name": "ana", "age": 31},
    {"name": "bruno", "age": 24},
    {"name": "carla", "age": 31},
    {"name": "diego", "age": 19}
]

by_age = sorted(people, key=lambda person: person["age"])
print("by age:", [p["name"] for p in by_age])

by_age_then_name = sorted(people, key=lambda p: (p["age"], p["name"]))
print("by age then name:", [p["name"] for p in by_age_then_name])

print("descending:", [p["name"] for p in sorted(people, key=operator.itemgetter("age"), reverse=True)])

words = ["Banana", "apple", "Cherry"]
print("default is case sensitive:", sorted(words))
print("case insensitive:", sorted(words, key=str.lower))

numbers = [5, 3, 9, 1]
numbers.sort()
print("sort mutates in place:", numbers)
print("sorted returns a new list:", sorted(numbers, reverse=True), numbers)

# Stability: equal keys keep their original relative order.
pairs = [("b", 2), ("a", 1), ("c", 2)]
print("stable by second element:", sorted(pairs, key=operator.itemgetter(1)))

print("max and min take a key too:", max(people, key=lambda p: p["age"])["name"])

counts = {"x": 3, "y": 1, "z": 2}
print("sorting a dict by value:", sorted(counts.items(), key=operator.itemgetter(1)))
