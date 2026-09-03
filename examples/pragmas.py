#!/bin/python3
# The three directives that let you opt out of brace syntax.
#
#   # Pytho{\}: Ignore file            - the whole file is ordinary Python
#   # Pytho{\}: Start regular Python   - opens a verbatim region
#   # Pytho{\}: End regular Python     - closes it
#
# A verbatim region has to begin at the top level, because the lines inside it are
# emitted exactly as written and receive no generated indentation.

import pragmas_regular_python as plain

print("imported an ignored file:", plain.describe())

if True {
    print("brace syntax, as usual")
}

# Pytho{\}: Start regular Python
for index in range(3):
    if index % 2 == 0:
        print("  regular Python, indented normally:", index)
    else:
        print("  odd:", index)

text = 'a region may contain anything, including { and } and the word "case"'
print("  " + text)
# Pytho{\}: End regular Python

if True {
    print("back to braces")
}

# The directives are only recognised on a line of their own. Written inside a
# string, or after code, they are just text.
not_a_directive = "# Pytho{\\}: Ignore file"
print("as a string, ignored:", not_a_directive)
