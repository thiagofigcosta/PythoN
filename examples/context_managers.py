#!/bin/python3
# Context managers, written by hand and with contextlib.

import contextlib
import io


class Tracked {
    def __init__(self, label) {
        self.label = label
    }

    def __enter__(self) {
        print("  enter {}".format(self.label))
        return self.label
    }

    def __exit__(self, kind, value, traceback) {
        print("  exit  {}".format(self.label))
        return False
    }
}


@contextlib.contextmanager
def temporary(setting, store) {
    previous = store.get(setting)
    store[setting] = "temporary"
    try {
        yield store
    } finally {
        if previous is None {
            del store[setting]
        } else {
            store[setting] = previous
        }
    }
}


with Tracked("outer") as label {
    print("  working with", label)
    with Tracked("inner") {
        print("  nested body")
    }
}

settings = {"mode": "production"}
with temporary("mode", settings) as active {
    print("  inside the context:", active["mode"])
}
print("restored afterwards:", settings["mode"])

with temporary("added", settings) {
    print("  key exists inside:", "added" in settings)
}
print("key removed afterwards:", "added" in settings)

captured = io.StringIO()
with contextlib.redirect_stdout(captured) {
    print("this goes to the buffer")
}
print("captured stdout:", repr(captured.getvalue().strip()))

with contextlib.suppress(ZeroDivisionError) {
    result = 1 / 0
}
print("suppressed an exception without a try block")

with contextlib.ExitStack() as stack {
    for name in ["a", "b"] {
        stack.enter_context(Tracked(name))
    }
    print("  both are open")
}
