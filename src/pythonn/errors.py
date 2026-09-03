from __future__ import annotations


class PythoNError(Exception):
    """A fault in the Pytho{\\} source, reported against its real position."""

    def __init__(
        self,
        message: str,
        path: str = "",
        line: int = 0,
        column: int = 0,
        source_line: str = "",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.path = path
        self.line = line
        self.column = column
        self.source_line = source_line

    def render(self) -> str:
        if self.line == 0:
            head = "{}: error: {}".format(self.path, self.message)
        else:
            head = "{}:{}:{}: error: {}".format(
                self.path, self.line, self.column, self.message
            )
        if not self.source_line:
            return head
        caret = " " * max(0, self.column - 1) + "^"
        return "{}\n{}\n{}".format(head, self.source_line, caret)
