#!/bin/python3
# Inheritance, cooperative super(), mixins and abstract base classes.

from abc import ABC, abstractmethod


class Describable(ABC) {
    @abstractmethod
    def describe(self) {
        raise NotImplementedError
    }
}


class Timestamped {
    def stamp(self) {
        return "[{}]".format(type(self).__name__)
    }
}


class Animal(Describable) {
    def __init__(self, name) {
        self.name = name
    }

    def speak(self) {
        return "..."
    }

    def describe(self) {
        return "{} says {}".format(self.name, self.speak())
    }
}


class Dog(Timestamped, Animal) {
    def speak(self) {
        return "woof"
    }
}


class Puppy(Dog) {
    def speak(self) {
        return super().speak() + "!"
    }
}


dog = Dog("rex")
puppy = Puppy("bit")

print(dog.describe())
print(puppy.describe())
print("mixin method:", puppy.stamp())
print("super() chains through the hierarchy:", puppy.speak())

print("method resolution order:")
for klass in Puppy.__mro__ {
    print("  " + klass.__name__)
}

print("isinstance across the chain:", isinstance(puppy, Animal), isinstance(puppy, Describable))
print("issubclass:", issubclass(Puppy, Dog))

try {
    Describable()
} except TypeError as error {
    print("cannot instantiate an abstract class:", str(error)[:44])
}

for animal in [dog, puppy] {
    print("  polymorphic call:", animal.describe())
}
