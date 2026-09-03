#!/bin/python3
# Every block-opening construct, written with curly brackets instead of indentation.

value = 7

if value > 10 {
    print("big")
} elif value > 5 {
    print("medium")
} else {
    print("small")
}

# The closing brace may sit tight against the next keyword, or be spaced out.
if value == 7 {
    print("exact match")
}elif value == 8 {
    print("never")
}   else {
    print("never either")
}

total = 0
for n in range(1, 6) {
    if n % 2 == 0 {
        continue
    }
    total += n
}
print("sum of odds below 6:", total)

countdown = 3
while countdown > 0 {
    print("  t-minus", countdown)
    countdown -= 1
}

for n in range(10) {
    if n > 2 {
        break
    }
    print("  loop", n)
}

# An inline block: header and body on one line. One level only.
if value { print("inline body") }
for n in range(2) { print("inline loop", n) }

# Nested blocks go as deep as you like, as long as each one opens on its own line.
for row in range(2) {
    for column in range(2) {
        if row == column {
            print("  diagonal at ({}, {})".format(row, column))
        }
    }
}

with open(__file__) as handle {
    first = handle.readline().strip()
    print("first line of this file:", first)
}
