#!/bin/python3
# The re module. Note that the conventional variable name for a result is `match`,
# which is also a soft keyword - both readings appear here.

import re

text = "order 1234 shipped on 2026-09-03 to ana@example.com"

match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
if match {
    print("matched:", match.group(0))
    print("groups:", match.groups())
    print("span:", match.span())
}

named = re.search(r"(?P<user>\w+)@(?P<host>[\w.]+)", text)
if named {
    print("named groups:", named.group("user"), "at", named.group("host"))
    print("as a dict:", named.groupdict())
}

print("findall:", re.findall(r"\d+", text))
print("split on whitespace:", re.split(r"\s+", "a  b   c"))
print("substitution:", re.sub(r"\d", "#", "abc123"))
print("substitution with a function:", re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "5 and 10"))

compiled = re.compile(r"^\w+", re.IGNORECASE)
print("compiled pattern:", compiled.match(text).group())

for candidate in ["2026-01-01", "not a date", "1999-12-31"] {
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", candidate) {
        print("  {} looks like a date".format(candidate))
    } else {
        print("  {} does not".format(candidate))
    }
}

# The brace quantifier {4} above is inside a string, so it is never a block.
counts = {"digits": len(re.findall(r"\d", text)), "words": len(re.findall(r"[a-z]+", text))}
print("counted with a dict comprehension of results:", counts)
