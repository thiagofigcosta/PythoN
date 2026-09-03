#!/bin/python3
# Functions, closures, decorators and generators.

def greet(name, greeting="Hello") {
    return "{}, {}!".format(greeting, name)
}

def totals(*numbers, **labels) {
    return sum(numbers), labels
}

def counter(start) {
    count = start
    def step() {
        nonlocal count
        count += 1
        return count
    }
    return step
}

def logged(function) {
    def wrapper(*args, **kwargs) {
        print("  calling {}".format(function.__name__))
        return function(*args, **kwargs)
    }
    return wrapper
}

@logged
def multiply(a, b) {
    return a * b
}

def first_squares(limit) {
    for n in range(limit) {
        yield n * n
    }
}

print(greet("world"))
print(greet("world", greeting="Goodbye"))
print("varargs:", totals(1, 2, 3, unit="items"))

tick = counter(10)
tick()
print("closure keeps state:", tick())

print("decorated result:", multiply(6, 7))
print("generator:", list(first_squares(5)))

# A default argument that is a dictionary - braces as data, inside a signature.
def configure(options={"debug": False}) {
    return dict(options)
}
print("default dict argument:", configure())

double = lambda n: n * 2
print("lambda:", [double(n) for n in range(4)])
