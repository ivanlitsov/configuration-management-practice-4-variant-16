"""Лексический анализ учебного конфигурационного языка на SLY."""

from sly import Lexer


def location(text, index):
    """Возвращает номер строки и столбца для позиции в исходном тексте."""
    line = text.count("\n", 0, index) + 1
    column = index - text.rfind("\n", 0, index)
    return f"строка {line}, столбец {column}"


class ConfigLexer(Lexer):
    tokens = {NAME, LET, ARRAY, NUMBER, STRING, ARROW}
    literals = {"{", "}", "(", ")", ",", ".", "=", ";", "@", "[", "]"}
    ignore = " \t\r"

    NAME = r"[a-z]+"
    NAME["let"] = LET
    NAME["array"] = ARRAY
    NUMBER = r"[+-]?\d+"
    STRING = r'"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"'
    ARROW = r"->"

    @_(r"\(\*[\s\S]*?\*\)")
    def ignore_comment(self, token):
        self.lineno += token.value.count("\n")

    @_(r"\n+")
    def ignore_newline(self, token):
        self.lineno += len(token.value)

    @_(r"\(\*")
    def ignore_unclosed_comment(self, token):
        where = location(self.text, token.index)
        raise ValueError(f"{where}: незакрытый комментарий")

    def error(self, token):
        where = location(self.text, token.index)
        raise ValueError(f"{where}: недопустимый символ {token.value[0]!r}")
