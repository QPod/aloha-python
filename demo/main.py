import importlib
import sys

usage = """
Usage: python3 main.py module.name
    the `module.name` should be a python package file or package which include a `main()` function
"""

if len(sys.argv) < 2:
    print(usage)
    exit(-1)

m = importlib.import_module(sys.argv[1])
f_main = getattr(m, "main")

if f_main is None:
    print("Given module does not provides a `main()` function!")
else:
    f_main()
