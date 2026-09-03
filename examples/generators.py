#!/bin/python3
# Generators: lazy sequences that keep their place between calls.

def counter(limit) {
    current = 0
    while current < limit {
        yield current
        current += 1
    }
}

def evens_then_odds(limit) {
    yield from (n for n in range(limit) if n % 2 == 0)
    yield from (n for n in range(limit) if n % 2 == 1)
}

def running_total() {
    total = 0
    while True {
        received = yield total
        if received is None {
            break
        }
        total += received
    }
}

print("simple generator:", list(counter(5)))
print("yield from:", list(evens_then_odds(6)))

accumulator = running_total()
next(accumulator)
accumulator.send(10)
print("generator receiving values:", accumulator.send(5))

def infinite() {
    value = 1
    while True {
        yield value
        value *= 2
    }
}

powers = infinite()
first_five = [next(powers) for _ in range(5)]
print("infinite generator, taken five:", first_five)

lazy = (n ** 3 for n in range(4))
print("generator expression:", list(lazy))
print("consumed generators do not restart:", list(lazy))
