#!/bin/python3
# The collections module: the containers the built-ins do not cover.

from collections import Counter, defaultdict, deque, namedtuple, OrderedDict

words = "the quick brown fox jumps over the lazy dog the end".split()

counts = Counter(words)
print("most common:", counts.most_common(2))
print("count of a missing key is zero, not an error:", counts["absent"])

grouped = defaultdict(list)
for word in words {
    grouped[len(word)].append(word)
}
print("grouped by length:", dict(sorted(grouped.items())))

totals = defaultdict(int)
for letter in "abracadabra" {
    totals[letter] += 1
}
print("counted without initialising:", dict(sorted(totals.items())))

queue = deque([1, 2, 3])
queue.appendleft(0)
queue.append(4)
queue.rotate(1)
print("deque after rotate:", list(queue))
print("popped from both ends:", queue.popleft(), queue.pop())

Point = namedtuple("Point", ["x", "y"])
location = Point(3, 4)
print("namedtuple:", location, "x is", location.x)
print("unpacks like a tuple:", tuple(location))
print("as a dict:", location._asdict())

ordered = OrderedDict()
for key in "cab" {
    ordered[key] = key.upper()
}
print("insertion order preserved:", list(ordered.items()))
