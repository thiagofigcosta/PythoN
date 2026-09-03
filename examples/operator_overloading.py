#!/bin/python3
# Making your own types behave like built-in ones.

class Vector {
    def __init__(self, x, y) {
        self.x = x
        self.y = y
    }

    def __repr__(self) {
        return "Vector({}, {})".format(self.x, self.y)
    }

    def __add__(self, other) {
        return Vector(self.x + other.x, self.y + other.y)
    }

    def __sub__(self, other) {
        return Vector(self.x - other.x, self.y - other.y)
    }

    def __mul__(self, factor) {
        return Vector(self.x * factor, self.y * factor)
    }

    def __rmul__(self, factor) {
        return self * factor
    }

    def __neg__(self) {
        return Vector(-self.x, -self.y)
    }

    def __eq__(self, other) {
        return (self.x, self.y) == (other.x, other.y)
    }

    def __lt__(self, other) {
        return abs(self) < abs(other)
    }

    def __abs__(self) {
        return (self.x ** 2 + self.y ** 2) ** 0.5
    }

    def __len__(self) {
        return 2
    }

    def __getitem__(self, index) {
        return (self.x, self.y)[index]
    }

    def __iter__(self) {
        yield self.x
        yield self.y
    }

    def __hash__(self) {
        return hash((self.x, self.y))
    }

    def __call__(self, scale) {
        return self * scale
    }

    def __contains__(self, value) {
        return value in (self.x, self.y)
    }
}

a = Vector(1, 2)
b = Vector(3, 4)

print("add:", a + b)
print("subtract:", b - a)
print("scale on the right:", a * 3)
print("scale on the left:", 3 * a)
print("negate:", -a)
print("equality:", Vector(1, 2) == a)
print("magnitude:", abs(b))
print("ordering by magnitude:", sorted([b, a]))
print("length and indexing:", len(a), a[0], a[1])
print("unpacking via __iter__:", list(b))
print("callable instance:", a(10))
print("membership:", 2 in a, 9 in a)
print("hashable:", len({Vector(1, 2), Vector(1, 2), b}))
