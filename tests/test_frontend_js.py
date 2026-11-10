"""Runs the frontend JavaScript tests (tests/js/*.test.mjs) with Node's own
test runner, so `python -m unittest discover -s tests` covers them too.
Skipped when Node 22 or newer isn't installed (the app itself doesn't need Node)."""

import os
import re
import shutil
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
JS_DIR = os.path.join(HERE, "js")


def node_version():
    node = shutil.which("node")
    if not node:
        return None
    out = subprocess.run([node, "--version"], capture_output=True, text=True).stdout
    match = re.match(r"v(\d+)", out.strip())
    return int(match.group(1)) if match else None


@unittest.skipUnless((node_version() or 0) >= 22, "Node 22+ not installed")
class FrontendJsTests(unittest.TestCase):
    def test_node_tests_pass(self):
        files = sorted(os.path.join(JS_DIR, f) for f in os.listdir(JS_DIR) if f.endswith(".test.mjs"))
        self.assertTrue(files, "no tests in tests/js")
        result = subprocess.run([shutil.which("node"), "--test", *files], capture_output=True, text=True,
                                encoding="utf-8", cwd=os.path.dirname(HERE))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
