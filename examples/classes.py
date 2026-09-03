#!/bin/python3
# Classes, inheritance, properties and dunder methods.

class Shape {
    kind = "shape"

    def __init__(self, name) {
        self.name = name
    }

    def describe(self) {
        return "{} named {}".format(self.kind, self.name)
    }

    def __repr__(self) {
        return "<{} {}>".format(type(self).__name__, self.name)
    }
}

class Rectangle(Shape) {
    kind = "rectangle"

    def __init__(self, name, width, height) {
        super().__init__(name)
        self.width = width
        self.height = height
    }

    @property
    def area(self) {
        return self.width * self.height
    }

    @staticmethod
    def unit() {
        return Rectangle("unit", 1, 1)
    }

    @classmethod
    def square(cls, name, side) {
        return cls(name, side, side)
    }

    def __eq__(self, other) {
        return (self.width, self.height) == (other.width, other.height)
    }

    def __hash__(self) {
        return hash((self.width, self.height))
    }
}

box = Rectangle("box", 3, 4)
print(box.describe())
print("repr:", repr(box))
print("area via property:", box.area)
print("staticmethod:", Rectangle.unit().area)
print("classmethod:", Rectangle.square("tile", 5).area)
print("equality:", Rectangle("a", 2, 2) == Rectangle("b", 2, 2))
print("hashable:", len({Rectangle("a", 2, 2), Rectangle("b", 2, 2)}))
print("isinstance of the base:", isinstance(box, Shape))

# A class body may hold dictionaries too - those braces are data.
class Registry {
    entries = {"first": 1, "second": 2}

    def lookup(self, key) {
        return self.entries.get(key, 0)
    }
}
print("class-level dict:", Registry().lookup("second"))
