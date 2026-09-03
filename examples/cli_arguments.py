#!/bin/python3
# Arguments after the source file are handed to the program untouched.
#
#   ./Pytho\{N\}.py examples/cli_arguments.py --verbose -n 3 extra
#
# Tool flags go BEFORE the source file; everything after it belongs to you, even
# when it collides with a flag the tool itself understands.

import sys

program = sys.argv[0]
arguments = sys.argv[1:]

print("program:", program.split("/")[-1])
print("argument count:", len(arguments))

if not arguments {
    print("no arguments were passed - try:")
    print("  ./Pytho\\{N\\}.py examples/cli_arguments.py --verbose -n 3 extra")
} else {
    for index, argument in enumerate(arguments) {
        print("  {}: {}".format(index, argument))
    }
}

flags = [a for a in arguments if a.startswith("-")]
positional = [a for a in arguments if not a.startswith("-")]
print("flags:", flags)
print("positional:", positional)

settings = {"verbose": "--verbose" in arguments, "count": 1}
if "-n" in arguments {
    position = arguments.index("-n")
    if position + 1 < len(arguments) {
        settings["count"] = int(arguments[position + 1])
    }
}
print("parsed settings:", settings)
