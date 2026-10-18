"""Regression tests for rc=9009 Windows CMake/Ninja executable discovery."""
from pathlib import Path
import os
import tempfile
import unittest
from unittest import mock

import rexauto


class FakeContext:
    def __init__(self, base, cmake, ninja):
        self.work = str(base / "game")
        self.port = str(base / "game" / "port")
        Path(self.work).mkdir(parents=True)
        Path(self.port).mkdir(parents=True)
        self.env = {
            "cmake": str(cmake),
            "ninja": str(ninja),
            "vcvars": r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
            "clang": r"C:\Program Files\LLVM\bin\clang.exe",
            "clangxx": r"C:\Program Files\LLVM\bin\clang++.exe",
            "sdk": r"C:\ReXGlue SDK",
        }

    def load_state(self):
        return {}


class BuildToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        folder = self.base / "CMake & Native Tools"
        folder.mkdir()
        self.cmake = folder / "cmake.exe"
        self.ninja = folder / "ninja.exe"
        self.cmake.write_bytes(b"test-cmake")
        self.ninja.write_bytes(b"test-ninja")

    def test_discovery_of_absolute_paths_including_spaces(self):
        with mock.patch.dict(os.environ, {"CMAKE": str(self.cmake), "NINJA": str(self.ninja)}):
            result = rexauto.detect_env()
        self.assertEqual(result["cmake"], str(self.cmake))
        self.assertEqual(result["ninja"], str(self.ninja))

    def test_build_batch_uses_absolute_quoted_tools_and_checks_errors(self):
        ctx = FakeContext(self.base, self.cmake, self.ninja)
        bat = Path(rexauto.write_build_bat(ctx, parallel=2)).read_text()
        exe = '"' + str(self.cmake).replace("\\", "/") + '"'
        self.assertIn(exe + " --preset win-amd64-release", bat)
        self.assertIn(exe + " --build out/build/win-amd64-release", bat)
        self.assertIn('-DCMAKE_MAKE_PROGRAM:FILEPATH="' +
                      str(self.ninja).replace("\\", "/") + '"', bat)
        self.assertGreaterEqual(bat.count("if errorlevel 1"), 3)
        self.assertIn("Visual Studio vcvars64.bat failed", bat)
        self.assertNotIn("\ncmake --build", bat)

    def test_missing_ninja_fails_before_build_command_is_written(self):
        ctx = FakeContext(self.base, self.cmake, self.base / "missing.exe")
        with self.assertRaisesRegex(RuntimeError, "Missing CMake or Ninja"):
            rexauto.write_build_bat(ctx)
        self.assertFalse((Path(ctx.work) / "_build.bat").exists())

    def test_preflight_reports_missing_ninja_before_game_pipeline(self):
        from types import SimpleNamespace
        ctx = FakeContext(self.base, self.cmake, self.ninja)
        ctx.env.update({"rexglue": "test", "python": "test"})
        ctx.env["ninja"] = None
        with self.assertRaises(SystemExit) as err:
            rexauto.preflight(ctx.env, SimpleNamespace(no_jumptables=True))
        self.assertIn("Ninja build tool", str(err.exception))
        self.assertIn("Setup", str(err.exception))


if __name__ == "__main__":
    unittest.main()
