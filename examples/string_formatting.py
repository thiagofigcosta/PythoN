#!/bin/python3
# Every way to build a string, and the format spec mini-language.

name = "Pytho{N}"
value = 1234.56789
count = 7

print("concatenation: " + name + " is fine for two pieces")
print("percent style: %s has %d characters" % (name, len(name)))
print("format method: {} has {} characters".format(name, len(name)))
print("f-string: {} has {} characters".format(name, len(name)))
print(f"f-string directly: {name} has {len(name)} characters")

print("positional reuse: {0}-{0}-{1}".format("a", "b"))
print("named: {who} scored {points}".format(who="ana", points=9))

print("padding right: [{:<12}]".format("left"))
print("padding left:  [{:>12}]".format("right"))
print("centred:       [{:^12}]".format("mid"))
print("filled:        [{:*^12}]".format("mid"))

print("fixed decimals: {:.2f}".format(value))
print("thousands separator: {:,.2f}".format(value))
print("percentage: {:.1%}".format(0.4567))
print("scientific: {:.3e}".format(value))
print("integer padding: {:05d}".format(count))
print("sign always shown: {:+d}".format(count))
print("binary, octal, hex: {0:b} {0:o} {0:x} {0:X}".format(255))

print("repr instead of str: {!r}".format("quoted"))
print("literal braces: {{ and }}".format())

width = 9
print("width from a variable: [{:>{}}]".format("dyn", width))

print(f"expression inside an f-string: {count * 2}")
print(f"format spec inside an f-string: {value:.3f}")
print(f"nested quotes: {'inner'.upper()}")

rows = [("apple", 3), ("kiwi", 12), ("banana", 7)]
for fruit, quantity in rows {
    print("  {:<8} {:>3}".format(fruit, quantity))
}
