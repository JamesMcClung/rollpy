import sys
import re
from random import randint
from macros import macros
from group import Group
from roll import Roll
from character import get_current_character_roll
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

def extract_all_seps(args: list, seps: list):
    """Modifies the list to separate separators from args."""
    i = 0
    while i < len(args):
        newargs = extract_seps(args[i], seps)
        args[i:i+1] = newargs
        i += len(newargs)

# extract all separators from args
separators = ["[", "]"]
extract_all_seps(args, separators)

def expand_macs(arg: str) -> list:
    """Recursively expands macros in given arg."""
    # normal macro
    if arg in macros:
        ls = []
        for el in macros[arg].split():
            ls += expand_macs(el)
        extract_all_seps(ls, separators)
        return ls
    # character macro, or not a macro at all
    return [get_current_character_roll(arg) or arg]

# expand macros
args3 = []
for arg in args:
    args3 += expand_macs(arg)

try:
    biggroup = Group(args3)
    biggroup.execute()
except ParseException as e:
    print(e)