#!/bin/python3
# Strings are the hard case for a brace-based pre-compiler: a } inside a string is
# text, not the end of a block. Every form below used to be a hazard.

single = 'a } inside single quotes'
double = "a { inside double quotes"
escaped = "she said \"hello\" and left"
raw = r"a raw string keeps its \backslashes\ and its {braces}"

print(single)
print(double)
print(escaped)
print(raw)

# A triple-quoted string may contain anything at all, including braces that look
# exactly like block delimiters, and its own indentation is preserved verbatim.
if True {
    block = """
      indented two extra spaces
        indented four
    } this brace is text {
"""
    print("multi-line string, indentation intact:")
    print(block.rstrip())
}

name = "world"
count = 3
print(f"f-string: {name} repeated {count} times")
print(f"f-string with a dict lookup: {  {'k': 'v'}['k']  }")
print("format: {} and {}".format("first", "second"))
print("literal braces via format: {{ }}".format())

# A comment may contain a closing brace } and it is still just a comment.
if count == 3 {
    # this } does not end the block
    print("comment containing a brace is harmless")
}

lines = """first
second
third""".splitlines()
for index, line in enumerate(lines) {
    print("  {}: {}".format(index, line))
}

joined = ", ".join([w for w in ["braces", "strings", "comments"]])
print("all handled:", joined)
