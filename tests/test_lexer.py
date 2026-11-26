"""Тесты токенов и лексических ошибок."""

from pathlib import Path
import sys
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from lexer import ConfigLexer


class LexerTest(unittest.TestCase):
    def test_tokens_and_comment(self):
        text = 'let x = (* строка\nкомментария *) array(+7, -2, "текст");'
        tokens = list(ConfigLexer().tokenize(text))
        self.assertEqual([token.type for token in tokens],
                         ["LET", "NAME", "=", "ARRAY", "(", "NUMBER",
                          ",", "NUMBER", ",", "STRING", ")", ";"])
        self.assertEqual(tokens[3].lineno, 2)

    def test_invalid_character(self):
        with self.assertRaisesRegex(ValueError, "строка 2, столбец 3"):
            list(ConfigLexer().tokenize("\n  X"))

    def test_unclosed_comment(self):
        with self.assertRaisesRegex(ValueError, "незакрытый комментарий"):
            list(ConfigLexer().tokenize("(* конец"))
