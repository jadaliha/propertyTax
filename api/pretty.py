__all__ = ["i", "cls"]
# Debugging script
from rich import pretty, inspect
pretty.install()

def i(x):
    return inspect(x, all=True)

def cls():
    print("\033c")