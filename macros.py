from util import PATH_TO_DIR
from os import path
import json

# macros = {
#     "a":"2d20h1",
#     "da":"2d20l1",
#     "adv":"x2 -max -verbose",
#     "dis":"x2 -min -verbose",
#     "stat":"4d6h3",
#     "char":"stat stat stat stat stat stat",
#     "pizza":"2 2 13 -hide",
# }

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

def make_macro():
    print("Making macro")
    macro = input("Macro: ")
    value = input("Value: ")
    macros[macro] = value
    _save_macros(macros)
    print("Successfully created", macro)

def delete_macro():
    print("Deleting macro")
    macro = input("Macro to delete: ")
    del macros[macro]
    _save_macros(macros)
    print("Successfully deleted", macro)

def list_macros():
    print("List of macros:")
    for macro, value in macros.items():
        print("  {}: {}".format(macro, value))