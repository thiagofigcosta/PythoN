#!/bin/python3
# Reading and writing files, using a temporary directory so the example is repeatable.

import json
import os
import tempfile

with tempfile.TemporaryDirectory() as workspace {
    text_path = os.path.join(workspace, "notes.txt")
    json_path = os.path.join(workspace, "config.json")

    with open(text_path, "w", encoding="utf-8") as handle {
        handle.write("first line\n")
        handle.write("second line\n")
        handle.writelines(["third line\n", "fourth line\n"])
    }

    with open(text_path, encoding="utf-8") as handle {
        print("whole file, {} characters".format(len(handle.read())))
    }

    with open(text_path, encoding="utf-8") as handle {
        for number, line in enumerate(handle, start=1) {
            print("  {}: {}".format(number, line.rstrip()))
        }
    }

    with open(text_path, "a", encoding="utf-8") as handle {
        handle.write("appended\n")
    }

    with open(text_path, encoding="utf-8") as handle {
        lines = handle.read().splitlines()
    }
    print("after appending, last line is:", lines[-1])

    settings = {"retries": 3, "targets": ["a", "b"], "nested": {"on": True}}
    with open(json_path, "w", encoding="utf-8") as handle {
        json.dump(settings, handle, indent=2, sort_keys=True)
    }

    with open(json_path, encoding="utf-8") as handle {
        restored = json.load(handle)
    }
    print("json round trip:", restored == settings)

    print("directory listing:", sorted(os.listdir(workspace)))
    print("size on disk is positive:", os.path.getsize(json_path) > 0)
}

print("the temporary directory is gone once the block ends")
