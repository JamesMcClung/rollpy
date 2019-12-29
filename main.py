import sys
import re
from random import randint
from macros import macros
from group import Group
from roll import Roll
import character
import util

# get user input
args = sys.argv[1:]

# check if input was given
if not args:
    raise Exception("Expected inputs; none given")

# interpret commands
if args[0] == "!":

    # character management
    if args[1] == "char":

        # set current character
        if args[2] == "set":
            name = args[3]
            character.set_current_character(name)
            print("Set character to", name)
        
        # making new character, or overriding existing character
        elif args[2] == "make":
            character.make_character()
        
        # viewing current or specified character stats and proficiencies
        elif args[2] == "view":
            name = util.list_get(args, 3, default_func=character.get_current_character_name)
            print(str(character.load_characters()[name]))
        
        # display a list of all characters
        elif args[2] == "list":
            current = character.get_current_character_name()
            charlist = list(character.load_characters().keys())
            charlist[charlist.index(current)] += " (current)"
            print("List of characters:")
            print("  " + "\n  ".join(charlist))
        
        # delete the specified character
        elif args[2] == "delete":
            name = args[3]
            character.delete_character(name)
        
        # update the current or specified character
        elif args[2] == "update":
            name = util.list_get(args, 3, default_func=character.get_current_character_name)
            character.update_character(name)
            

    raise SystemExit() # exit program

# if not a command, clean up the arguments and expand macros before parsing

# a list of characters that partition individual arguments
delimiters = ["[", "]"]

def expand_delimiters(arg: str, delimiters: list) -> list:
    """Partitions the given arg into a list of subarguments using the given delimiters, which are included in the resulting list."""
    out = [""]
    for c in arg:
        if c in delimiters:
            out += [c, ""]
        else:
            out[-1] += c
    return [a for a in out if a] # remove empty strings

def expand_macro(arg: str) -> list:
    """Returns whatever the macro expands into, or if not a macro, returns the arg."""
    # normal macro
    if arg in macros:
        return macros[arg].split()
    # character roll, or not a macro at all
    return [character.get_current_character_roll(arg) or arg]

# expand everything
util.expand(args, [expand_macro, lambda arg: expand_delimiters(arg, delimiters)])

# now parse the rolls
try:
    biggroup = Group(args)
    biggroup.execute()
except util.ParseException as e:
    print(e)