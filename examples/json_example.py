#!/bin/python3
# JSON is the purest test of brace handling: the data format IS curly brackets.

import json

document = {
    "name": "Pytho{N}",
    "nested": {
        "deeper": {
            "deepest": [1, 2, {"even": "here"}]
        }
    },
    "flags": [True, False, None],
    "count": 3
}

encoded = json.dumps(document, sort_keys=True)
print("encoded:", encoded)

decoded = json.loads(encoded)
print("round trip is lossless:", decoded == document)
print("reaching into the nest:", decoded["nested"]["deeper"]["deepest"][2]["even"])

pretty = json.dumps({"a": 1, "b": [2, 3]}, indent=2, sort_keys=True)
print("indented output:")
for line in pretty.splitlines() {
    print("  " + line)
}

# A JSON string embedded in source: every brace inside it is text.
raw = '{"embedded": {"still": "just a string"}}'
print("parsed from a literal:", json.loads(raw)["embedded"]["still"])

records = [
    {"id": 1, "tags": ["a", "b"]},
    {"id": 2, "tags": []}
]
for record in records {
    if record["tags"] {
        print("  record {} has tags {}".format(record["id"], record["tags"]))
    } else {
        print("  record {} has none".format(record["id"]))
    }
}
