#!/bin/python3
# Numbers: integers, floats, complex, and the operators that come with them.

import math

a, b = 17, 5

print("sum, difference, product:", a + b, a - b, a * b)
print("true division:", a / b)
print("floor division and remainder:", a // b, a % b)
print("divmod gives both at once:", divmod(a, b))
print("power:", a ** 2)

print("rounding:", round(3.14159, 2), round(2.5), round(3.5))
print("floor and ceil:", math.floor(3.7), math.ceil(3.2))
print("absolute:", abs(-42))

print("bit operations:", a & b, a | b, a ^ b, a << 1, a >> 1)
print("binary, octal, hex:", bin(a), oct(a), hex(a))

print("float precision is not decimal precision:", 0.1 + 0.2 == 0.3)
print("compare with a tolerance instead:", math.isclose(0.1 + 0.2, 0.3))

complex_number = 3 + 4j
print("complex:", complex_number, "magnitude", abs(complex_number))

print("int from a string in base 2:", int("1011", 2))
print("large integers are exact:", 2 ** 70)

for value in [-2, 0, 7] {
    if value < 0 {
        label = "negative"
    } elif value == 0 {
        label = "zero"
    } else {
        label = "positive"
    }
    print("  {:>3} is {}".format(value, label))
}
