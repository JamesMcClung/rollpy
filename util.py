from os import path
import re

# Utility fields

PATH_TO_DIR = path.dirname(path.realpath(__file__))
LEFT_PAREN = "["
RIGHT_PAREN = "]"



# Utility functions

def intersperse(ls: list, sep):
    result = [sep] * (len(ls) * 2 - 1)
    result[0::2] = ls
    return result

def make_strikethrough(s: str) -> str:
    """Returns the given string but with ANSI strikethrough."""
    return "".join([c + '\u0336' for c in s])

def make_bold(s: str) -> str:
    """Returns the given string but with ANSI bold."""
    return "\033[1m" + s + "\033[0m"

class ParseException(Exception):
    pass

def expand(ls: list, expanders: list):
    """Expands entries in a list until none are expandable any more.\n
    ls: the list to be expanded
    expanders: a list of functions that map an element to a list of elements
    """
    i = 0
    while i < len(ls): # loop through elements one at a time, and don't move on to the next until the current element does not expand
        j = 0
        while j < len(expanders): # attempt to expand the current element with each function
            newargs = expanders[j](ls[i])
            if ls[i:i+1] != newargs:
                ls[i:i+1] = newargs
                j = 0 # loop through the functions again on the new element
            else:
                j += 1
        i += 1

def list_get(ls: list, index: int, default_func=None, default=None):
    if index < len(ls):
        return ls[index]
    if default_func:
        generated_default = default_func()
        if generated_default:
            return generated_default
    return default