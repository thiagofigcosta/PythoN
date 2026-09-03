# Examples

Thirty-six files, one per topic. Every one of them runs, and `tests/test_examples.py`
fails the build if any stops running or starts emitting a warning.

```
./Pytho\{N\}.py examples/<file>.py
```

## Language basics

| File | What it shows |
|---|---|
| `basic.py` | A tour of the syntax - the example this project originally shipped with |
| `numbers.py` | Arithmetic, `divmod`, rounding, bit operations, float precision |
| `strings.py` | Braces inside strings and comments, f-strings, multi-line strings |
| `string_formatting.py` | `%`, `.format`, f-strings, and the whole format spec mini-language |
| `slicing.py` | Slices, negative indices, steps, slice assignment and deletion |
| `data_structures.py` | Dicts, sets, lists - braces used as DATA rather than as blocks |
| `sets_operations.py` | Union, intersection, difference, `frozenset`, and why `{}` is a dict |
| `comprehensions.py` | List, dict, set and generator comprehensions, including nested ones |
| `control_flow.py` | `if`/`elif`/`else`, loops, `break`/`continue`, `with`, inline blocks |
| `match_statement.py` | `match`/`case` as a statement AND as ordinary variable names |

## Functions and objects

| File | What it shows |
|---|---|
| `functions.py` | Defaults, `*args`/`**kwargs`, closures, generators, lambdas |
| `decorators.py` | Parametrised decorators, `functools.wraps`, stacking, memoisation |
| `functional.py` | `map`, `filter`, `reduce`, `partial`, `operator`, `lru_cache` |
| `recursion.py` | Factorial, memoised fibonacci, walking a nested dict, flattening |
| `generators.py` | `yield`, `yield from`, `send`, infinite generators |
| `iterators.py` | The iteration protocol, and writing your own `__iter__`/`__next__` |
| `classes.py` | Inheritance, properties, `@staticmethod`/`@classmethod`, dunders |
| `inheritance.py` | Cooperative `super()`, mixins, MRO, abstract base classes |
| `operator_overloading.py` | Arithmetic, comparison, indexing, `__call__`, `__contains__` |
| `dataclasses_example.py` | `@dataclass`, `frozen`, `field(default_factory=...)`, ordering |
| `enums_example.py` | `Enum`, `IntEnum`, `auto`, iteration, enums as dict keys |
| `typing_example.py` | Annotations, `Optional`, `Callable`, and why they change nothing at runtime |

## Standard library

| File | What it shows |
|---|---|
| `collections_example.py` | `Counter`, `defaultdict`, `deque`, `namedtuple`, `OrderedDict` |
| `json_example.py` | Encoding and decoding - a format made entirely of curly brackets |
| `sorting.py` | Sort keys, tuples as keys, reverse, stability, `operator.itemgetter` |
| `regex_example.py` | `re`, named groups, substitution - and `match` as a variable name |
| `datetime_example.py` | Dates, durations, parsing, formatting, comparison |
| `file_io.py` | Reading, writing, appending, JSON on disk, in a temporary directory |
| `context_managers.py` | Hand-written `__enter__`/`__exit__`, `@contextmanager`, `ExitStack` |
| `exceptions.py` | `try`/`except`/`else`/`finally`, custom exceptions, `with` |

## The tool itself

| File | What it shows |
|---|---|
| `cli_arguments.py` | Arguments after the source file reach your program untouched |
| `pragmas.py` | The three directives that opt out of brace syntax |
| `pragmas_regular_python.py` | A file marked `Ignore file`, imported by the one above |
| `basic_external_file.py` | A local import, transpiled along with whatever imports it |
| `another_basic_external_file.py` | A local import reached indirectly, two hops from the entry |
| `basic_external_regularpy_file.py` | Another `Ignore file`, imported from `basic.py` |

## The interesting ones

`strings.py` and `match_statement.py` are worth reading even if you already know the
syntax, because they cover the two cases a brace-based pre-compiler finds genuinely hard.

A `}` is only the end of a block when it is really code. Inside a string, a comment, a
dict or a set it is just a character - and `strings.py` puts one in every position at
once, including a triple-quoted string whose own indentation survives intact.

`match` and `case` are *soft* keywords: they head a match statement and they are also
legal variable names. `match_statement.py` uses both readings in the same file, with
`match = {"still": "just a dictionary"}` a few lines after a real match statement
containing a list pattern.

`cli_arguments.py` is worth running with arguments:

```
./Pytho\{N\}.py examples/cli_arguments.py --verbose -n 3 extra
```

Tool flags go before the source file; anything after it is yours, even when it collides
with a flag the tool understands.

## Known limitations

`docs/limitations.md` lists what the pre-compiler refuses rather than guesses at -
nested inline blocks, a backslash-continued inline body, and a verbatim region opened
inside a block, among others. None of them appear here, because none of them work.
