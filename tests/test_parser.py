"""Проверки грамматики и подстановки констант."""

from pathlib import Path
import sys
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from parser import parse_config


class ParserTest(unittest.TestCase):
    def test_scalars(self):
        for source, expected in [("-10", -10), ("+08", 8), ("0", 0),
                                 (r'"цитата: \"да\""', 'цитата: "да"'),
                                 ('"(* текст *)"', "(* текст *)")]:
            with self.subTest(source=source):
                self.assertEqual(parse_config(source), expected)

    def test_nested_values_and_constants(self):
        source = """
        let delta = -3;
        let settings = { offset -> @[delta]. note -> "режим". };
        let group = array(@[settings], array(+5, {}), array());
        { group -> @[group]. array -> { let -> @[settings]. }. }
        """
        settings = {"offset": -3, "note": "режим"}
        expected = {
            "group": [settings, [5, {}], []],
            "array": {"let": settings},
        }
        self.assertEqual(parse_config(source), expected)

    def test_scalar_reference(self):
        self.assertEqual(parse_config('let label = "зал"; @[label]'), "зал")

    def test_syntax_errors(self):
        for source in ["", "{a -> 2}", "array(1,)", "array(1 2)",
                       "let x = 1 2", "{a->1.} {b->2.}", '"unclosed',
                       "let x = 1;"]:
            with self.subTest(source=source), self.assertRaisesRegex(
                ValueError, r"строка \d+, столбец \d+"
            ):
                parse_config(source)

    def test_unknown_constant(self):
        with self.assertRaisesRegex(ValueError, "неизвестная константа 'x'"):
            parse_config("let y = @[x]; let x = 1; @[y]")

    def test_duplicate_constant(self):
        with self.assertRaisesRegex(ValueError, "константа 'x' уже объявлена"):
            parse_config("let x = 1;\nlet x = 2; @[x]")

    def test_constant_state_is_local(self):
        self.assertEqual(parse_config("let x = 1; @[x]"), 1)
        with self.assertRaisesRegex(ValueError, "неизвестная константа 'x'"):
            parse_config("@[x]")
