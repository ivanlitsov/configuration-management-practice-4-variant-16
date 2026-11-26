"""Проверки запуска CLI с файлами и диагностики ошибок."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
MAIN = PROJECT / "src" / "main.py"
EXAMPLES = PROJECT / "examples"


def run_cli(source, output, option="--output"):
    return subprocess.run(
        [sys.executable, str(MAIN), option, str(output)],
        input=source, capture_output=True, check=False,
    )


class CliTest(unittest.TestCase):
    def test_server(self):
        source = (EXAMPLES / "server.cfg").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "server.json"
            result = run_cli(source, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {
                "host": "127.0.0.1",
                "ports": [8080, 8443],
                "checks": [
                    {"path": "/status", "method": "GET"},
                    {"path": "/ready", "method": "GET"},
                ],
            })

    def test_weather(self):
        source = (EXAMPLES / "weather.cfg").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "weather.json"
            result = run_cli(source, output, "-o")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {
                "station": "Север",
                "sensors": [
                    {"title": "Температура", "correction": -2},
                    {"title": "Скорость ветра", "correction": 0},
                ],
                "limits": {"low": -30, "high": 45},
                "alarms": [],
            })

    def test_invalid_input_preserves_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.json"
            output.write_text("old", encoding="utf-8")
            result = run_cli(b"{item -> 1}", output)
            self.assertEqual(result.returncode, 1)
            message = result.stderr.decode("utf-8", errors="replace")
            self.assertIn("'}'", message)
            self.assertEqual(output.read_text(encoding="utf-8"), "old")
