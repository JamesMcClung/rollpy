import sys
import re
from random import randint
from macros import macros
from group import Group
from roll import Roll
from util import intersperse, ParseException

# get user input
args = sys.argv[1:]


def extract_seps(arg: str, seps: list) -> list:
    """Extracts a list of args from given arg where each separator is its own arg"""
    out = [""]
    for c in arg:
        if c in seps:
            out += [c, ""]
        else:
            out[-1] += c
    return [a for a in out if a] # remove empty strings

# extract all separators from args
args2 = []
separators = ["[", "]"]
for arg in args:
    args2 += extract_seps(arg, separators)


def expand_macs(arg: str) -> list:
    """Recursively expands macros in given arg."""
    if arg in macros:
        ls = []
        for el in macros[arg].split():
            ls += expand_macs(el)
        return ls
    return [arg]

# expand macros
args3 = []
for arg in args2:
    args3 += expand_macs(arg)

try:
    biggroup = Group(args3)
    biggroup.execute()
except ParseException as e:
    print(e)