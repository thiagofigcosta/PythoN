#!/bin/python3
# Enumerations.

from enum import Enum, IntEnum, auto


class Colour(Enum) {
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

    def shout(self) {
        return self.value.upper()
    }
}


class Priority(IntEnum) {
    LOW = 1
    MEDIUM = 2
    HIGH = 3
}


class Direction(Enum) {
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()
}


print("member:", Colour.RED, "value:", Colour.RED.value, "name:", Colour.RED.name)
print("a method on the enum:", Colour.BLUE.shout())
print("lookup by value:", Colour("green"))
print("lookup by name:", Colour["BLUE"])

for colour in Colour {
    print("  iterating:", colour.name)
}

print("IntEnum compares as an int:", Priority.HIGH > Priority.LOW, Priority.MEDIUM + 1)
print("auto assigns in order:", [d.value for d in Direction])

palette = {Colour.RED: "#ff0000", Colour.GREEN: "#00ff00"}
print("enums as dict keys:", palette[Colour.RED])

if Priority.HIGH in Priority {
    print("membership works")
}
