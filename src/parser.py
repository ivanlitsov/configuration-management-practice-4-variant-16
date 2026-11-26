"""Грамматика SLY и вычисление констант учебного языка."""

import json

from sly import Parser

from lexer import ConfigLexer, location


class ConfigParser(Parser):
    tokens = ConfigLexer.tokens

    def __init__(self, text):
        self.text = text
        self.constants = {}

    @_("declarations value")
    def document(self, parts):
        return parts.value

    @_("declarations LET name '=' value ';'", "")
    def declarations(self, parts):
        if parts:
            name = parts.name
            if name in self.constants:
                where = location(self.text, parts.index)
                raise ValueError(f"{where}: константа {name!r} уже объявлена")
            self.constants[name] = parts.value

    @_("NAME", "LET", "ARRAY")
    def name(self, parts):
        return parts[0]

    @_("NUMBER")
    def value(self, parts):
        return int(parts.NUMBER)

    @_("STRING")
    def value(self, parts):
        return json.loads(parts.STRING)

    @_("'@' '[' name ']'")
    def value(self, parts):
        name = parts.name
        if name not in self.constants:
            where = location(self.text, parts.index)
            raise ValueError(f"{where}: неизвестная константа {name!r}")
        return self.constants[name]

    @_("ARRAY '(' ')'")
    def value(self, parts):
        return []

    @_("ARRAY '(' items ')'")
    def value(self, parts):
        return parts.items

    @_("value")
    def items(self, parts):
        return [parts.value]

    @_("items ',' value")
    def items(self, parts):
        parts.items.append(parts.value)
        return parts.items

    @_("'{' entries '}'")
    def value(self, parts):
        return parts.entries

    @_("")
    def entries(self, parts):
        return {}

    @_("entries name ARROW value '.'")
    def entries(self, parts):
        parts.entries[parts.name] = parts.value
        return parts.entries

    def error(self, token):
        if token is None:
            where = location(self.text, len(self.text))
            raise ValueError(f"{where}: неожиданный конец ввода")
        where = location(self.text, token.index)
        raise ValueError(f"{where}: неожиданный токен {token.value!r}")


def parse_config(text):
    """Разбирает полную конфигурацию и подставляет значения констант."""
    return ConfigParser(text).parse(ConfigLexer().tokenize(text))
