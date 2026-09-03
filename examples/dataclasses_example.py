#!/bin/python3
# Dataclasses: a decorator and a class body full of annotations.

from dataclasses import dataclass, field, asdict, replace


@dataclass
class Point {
    x: int
    y: int = 0

    def distance_from_origin(self) {
        return (self.x ** 2 + self.y ** 2) ** 0.5
    }
}


@dataclass(frozen=True, order=True)
class Version {
    major: int
    minor: int
    patch: int = 0

    def __str__(self) {
        return "{}.{}.{}".format(self.major, self.minor, self.patch)
    }
}


@dataclass
class Basket {
    owner: str
    items: list = field(default_factory=list)
    tags: dict = field(default_factory=dict)
}


origin = Point(0)
far = Point(3, 4)
print("generated repr:", far)
print("generated equality:", Point(3, 4) == far)
print("a method alongside the fields:", far.distance_from_origin())
print("as a dict:", asdict(far))
print("replace makes a modified copy:", replace(far, y=0))

versions = [Version(1, 2), Version(1, 0, 3), Version(2, 0)]
print("ordering comes free:", [str(v) for v in sorted(versions)])
print("frozen instances are hashable:", len({Version(1, 0), Version(1, 0)}))

basket = Basket("me")
basket.items.append("apple")
basket.tags["fresh"] = True
print("default_factory avoids the shared-mutable trap:", Basket("you"))
print("this one has contents:", basket)
