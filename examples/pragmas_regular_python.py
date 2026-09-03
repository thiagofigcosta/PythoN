#!/bin/python3
# Pytho{\}: Ignore file
#
# The directive above tells the pre-compiler to leave this file completely alone.
# It is therefore ordinary Python, indentation and all, and it can be imported by
# a brace-syntax file without either of them noticing.

INDENTED_STYLE = "this file is never transpiled"


def describe():
    lines = []
    for word in INDENTED_STYLE.split():
        lines.append(word)
    return " ".join(lines)
