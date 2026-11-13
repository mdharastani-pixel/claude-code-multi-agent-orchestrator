"""Testläufer ohne pytest: python3 run_tests.py"""
import sys, traceback, importlib, glob, os

failed = total = 0
for path in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_*.py"))):
    mod = importlib.import_module(os.path.basename(path)[:-3])
    for name in sorted(n for n in dir(mod) if n.startswith("test_")):
        total += 1
        try:
            getattr(mod, name)()
            print("ok  ", name)
        except Exception:
            failed += 1
            print("FAIL", name)
            traceback.print_exc(limit=1)
print(f"{total - failed}/{total} bestanden")
sys.exit(1 if failed else 0)
