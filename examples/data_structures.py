#!/bin/python3
# Dictionaries, sets, lists and comprehensions - the shapes that used to break the
# pre-compiler, because every one of them uses curly brackets as DATA, not as a block.

empty_dict = {}
empty_set = set()
single_line = {"language": r"Pytho{\}", "braces": "as data"}

nested = {
    "outer": {
        "inner": {
            "deep": 1
        }
    }
}

numbers = {1, 2, 3, 3, 2, 1}
pairs = [("a", 1), ("b", 2), ("c", 3)]

squares = {n: n * n for n in range(5)}
evens = [n for n in range(10) if n % 2 == 0]
unique_lengths = {len(word) for word in ["a", "bb", "cc", "ddd"]}

print("nested lookup:", nested["outer"]["inner"]["deep"])
print("set collapses duplicates:", sorted(numbers))
print("dict comprehension:", squares)
print("list comprehension:", evens)
print("set comprehension:", sorted(unique_lengths))

for key, value in sorted(single_line.items()) {
    print("  {} -> {}".format(key, value))
}

appended = []
appended.append({"dicts": "appended inline to a list"})
appended.append({"still": "just data"})
for item in appended {
    for k, v in item.items() {
        print("  {}: {}".format(k, v))
    }
}

# A lambda returning a dictionary - the brace here belongs to the lambda's body.
make_config = lambda: {"retries": 3, "verbose": True}
if make_config()["verbose"] {
    print("lambda returned:", make_config())
}
