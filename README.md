# Pytho{\\}

I hate the fact that i need to tab "properly" python files, that may cause several errors and confusions betweens actual tabs and spaces. 
Why not just use regular curly brackets? 

So I created `Pytho{\}` a simple python pre-compiler with no pip dependencies, that simplily parses the python with curly brackets into the normal sintax and runs it, after the execution the temporary code is deleted.

Just put Pytho{N}.py file on you project and stop using ident and :

`Pytho{N}.py` is the shipped, standalone file - copy just that one file into a project and it runs. It is generated from `src/pythonn/*.py` by `scripts/build_vendor.py`; if you want to change the tool itself, edit the source modules and rebuild, don't edit the generated file directly, your changes will be overwritten on the next build.

Examples:
```
python3 Pytho\{N\}.py examples/basic.py
./Pytho\{N\}.py examples/basic.py
./Pytho\{N\}.py -v 3 examples/basic.py
./Pytho\{N\}.py -v 3 --show-cmd --print-output examples/basic.py
./Pytho\{N\}.py examples/basic.py --argument to file
./Pytho\{N\}.py #iterative shell (here you cannot use {})
```

Flags:
- `-v`/`--version` - which `python3.<version>` to run the transpiled code with (default `3`).
- `--show-cmd` - print the command line that gets shelled out to before running it.
- `--print-output` - print each transpiled file's generated Python source.
- `--keep-temp` - don't delete the build tree after the run; the path is printed to stderr.

Each run transpiles into its own `tempfile.mkdtemp` directory rather than a fixed path in the project, so two concurrent runs never clobber each other's generated code. That directory is deleted when the run finishes, unless `--keep-temp` is passed.

The runtime still has no pip dependencies - that hasn't changed. Running the test suite needs `pytest` (`pip install -e '.[dev]'`, then `python3 -m pytest`).

There is an example per language feature in [examples/](examples/), with a short index
in [examples/README.md](examples/README.md). Every one of them runs, and a test asserts
that they all still do.

Known limitations are listed in [docs/limitations.md](docs/limitations.md). Design notes and rationale for the Phase 1 hardening pass are in [docs/2026-09-03-phase1-design.md](docs/2026-09-03-phase1-design.md).
