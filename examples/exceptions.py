#!/bin/python3
# Exception handling: try / except / else / finally, custom errors, context managers.

class ConfigError(Exception) {
    pass
}

def load(settings, key) {
    try {
        value = settings[key]
    } except KeyError {
        raise ConfigError("missing key: {}".format(key))
    }
    return value
}

settings = {"host": "localhost", "port": 8080}

print("found:", load(settings, "host"))

try {
    load(settings, "timeout")
} except ConfigError as error {
    print("raised as expected:", error)
}

try {
    result = 10 / 2
} except ZeroDivisionError {
    print("never reached")
} else {
    print("else runs when nothing was raised:", result)
} finally {
    print("finally always runs")
}

# Several except clauses, and a bare one at the end.
for value in ["12", "oops", None] {
    try {
        print("  parsed:", int(value))
    } except ValueError {
        print("  not a number:", value)
    } except TypeError {
        print("  not even a string:", value)
    }
}


class Resource {
    def __enter__(self) {
        print("  acquired")
        return self
    }

    def __exit__(self, kind, value, traceback) {
        print("  released")
        return False
    }
}

with Resource() {
    print("  working inside the context")
}
