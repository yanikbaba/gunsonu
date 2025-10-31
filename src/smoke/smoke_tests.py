#!/usr/bin/env python3
"""
Local Smoke Tests (v0.8.1)
Run:
    python src/smoke/smoke_tests.py
"""
import os, sys, unittest, pathlib

class Smoke(unittest.TestCase):
    def test_dist_exe_exists(self):
        # Accept either root or portable
        paths = ["dist/GunSonu.exe", "dist/GunSonu/GunSonu.exe"]
        self.assertTrue(any(os.path.exists(p) for p in paths), f"Missing EXE in {paths}")
    def test_reports_dir(self):
        pathlib.Path("reports").mkdir(exist_ok=True)
        self.assertTrue(os.path.exists("reports"))
    def test_backup_dir(self):
        pathlib.Path("backup").mkdir(exist_ok=True)
        self.assertTrue(os.path.exists("backup"))

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Smoke)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
