#!/bin/python3
# Slicing works on any sequence, and the syntax is unchanged by the braces.

letters = list("abcdefghij")

print("whole:", letters)
print("first three:", letters[:3])
print("last three:", letters[-3:])
print("middle:", letters[3:7])
print("every second:", letters[::2])
print("reversed:", letters[::-1])
print("every third from the second:", letters[1::3])

text = "Pytho{N} slices strings too"
print("string slice:", text[:8])
print("string reversed:", text[::-1][:8])

numbers = list(range(10))
numbers[2:5] = [99, 98]
print("slice assignment shortens the list:", numbers)

del numbers[:2]
print("slice deletion:", numbers)

window = slice(1, 4)
print("a reusable slice object:", letters[window])

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
for row in matrix {
    print("  row without its middle:", row[:1] + row[2:])
}

column = [row[1] for row in matrix]
print("second column:", column)
