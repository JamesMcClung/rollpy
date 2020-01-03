from util import PATH_TO_DIR, ParseException
from os import path
import json
import re

macros_file_path = PATH_TO_DIR + "/macros.json"

def _load_macros() -> dict:
    if not path.exists(macros_file_path):
        return {}
    with open(macros_file_path) as fp:
        macros = json.load(fp)
        return macros
        # macros = {pair[0]: pair[1] for pair in map(lambda line: line.split(maxsplit=1), fp.readlines())}

macros = _load_macros()

def _save_macros(macros: dict):
    with open(macros_file_path, 'w') as fp:
        json.dump(macros, fp)

def make_macro(macro: str = None, value: str = None):
    if macro:
        print("Making macro '{}'".format(macro))
    else:
        macro = input("Macro name: ")
    assert_valid_macro(macro)
    if not value:
        value = input("Value: ")
    macros[macro] = value
    _save_macros(macros)
    print("Successfully created macro '{}' with value '{}'".format(macro, value))

def delete_macro(macro: str = None):
    if not macro:
        macro = input("Macro to delete: ")
    if macro in macros:
        del macros[macro]
        _save_macros(macros)
        print("Successfully deleted macro '{}'".format(macro))
    else:
        raise ParseException("Failure: '{}' is not a macro. Were you trying to delete a character macro?".format(macro))

def list_macros():
    print("List of macros:")
    for macro, value in macros.items():
        print("  {}: {}".format(macro, value))

def assert_valid_macro(arg: str):
    """Raises a ParseException if given arg is not a valid macro (i.e., consists of only letters, numbers, and underscore)"""
    print(arg)
    if not re.match(r"^\w+$", arg):
        raise ParseException("Invalid macro name: {}".format(arg))