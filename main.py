import sys
import re
from random import randint
import macros as mac
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

    try:
        # character management
        if args[1] == "char":

            # set current character
            if args[2] == "set":
                name = args[3]
                character.set_current_character(name)
                print("Set current character to", name)
            
            # making new character, or overriding existing character
            elif args[2] == "make":
                character.make_character()
            
            # viewing current or specified character stats and proficiencies
            elif args[2] == "view":
                name = util.list_get(args, 3, default_func=character.get_current_character_name)
                print(str(character.characters[name]))
            
            # display a list of all characters
            elif args[2] == "list":
                current = character.get_current_character_name()
                charlist = list(character.characters.keys())
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
            
            # rename the current or specified character
            elif args[2] == "rename":
                newname = util.list_get(args, 4) or util.list_get(args, 3)
                oldname = args[3] if len(args) == 5 else character.get_current_character_name()
                character.rename_character(oldname, newname)
            
            # character macro management
            elif args[2] == "macro":

                # make or remake a character macro
                if args[3] == "make":
                    character.make_character_macro(character.get_current_character_name(), util.list_get(args, 4), " ".join([a.replace(" ", "\\ ") for a in args[5:]]))
            
                # delete an existing character macro
                if args[3] == "delete":
                    character.delete_character_macro(character.get_current_character_name(), util.list_get(args, 4))
        
        # macro management
        elif args[1] == "macro":

            # make or remake macro
            if args[2] == "make":
                mac.make_macro(util.list_get(args, 3), " ".join([a.replace(" ", "\\ ") for a in args[4:]]))
            
            # delete macro
            elif args[2] == "delete":
                mac.delete_macro(util.list_get(args, 3))
            
            # list macros
            elif args[2] == "list":
                mac.list_macros()
    except util.ParseException as e:
        print(e)
    # exit program
    raise SystemExit()

# if not a command, clean up the arguments and expand macros before parsing

# a list of characters that partition individual arguments
comma = ','
left_paren = util.LEFT_PAREN
right_paren = util.RIGHT_PAREN
delimiters = [left_paren, right_paren, comma]

def expand_delimiters(arg: str, delimiters: list) -> list:
    """Partitions the given arg into a list of subarguments using the given delimiters, which are included in the resulting list."""
    out = [""]
    for c in arg:
        if c in delimiters:
            out += [c, ""]
        else:
            out[-1] += c
    return [a for a in out if a] # remove empty strings

def split_macro(macro: str) -> list:
    """Splits the value of a macro. Identical to str.split(), except for the case where a macro expands into something that contains a space, which this handles properly."""
    words = macro.split()
    apos = "'"
    i = 0
    while i < len(words):
        if apos in words[i]:
            words[i] = words[i].replace(apos, "")
            while not apos in words[i]:
                words[i] += " " + words.pop(i+1)
            words[i] = words[i].replace(apos, "")
        elif words[i][-1] == "\\":
            words[i] = words[i][:-1] + " " + words.pop(i+1)
        i += 1
    return words
            

def expand_macro(arg: str) -> list:
    """Returns a list of whatever the macro expands into, or if not a macro, just the arg in a list."""
    # character macro
    if charroll := character.get_current_character_roll(arg):
        return split_macro(charroll)
    # normal macro
    if arg in mac.macros:
        return split_macro(mac.macros[arg])
    return [arg]

# expand everything
util.expand(args, [expand_macro, lambda arg: expand_delimiters(arg, delimiters)])

# interpret commas for grouping
i = 0
while i < len(args):
    if args[i] == comma:
        # find indices of all other commas at this depth, and where depth starts and ends
        comma_indices = [i]

        # find where this depth started
        depth = 0
        j = i
        while depth >= 0 and j > 0:
            j -= 1
            if args[j] == right_paren:
                depth += 1
            elif args[j] == left_paren:
                depth -= 1
        depth_start = j

        # find where this depth ends, and any other commas at this depth
        depth = 0
        j = i
        while depth >= 0 and j < len(args)-1:
            j += 1
            if args[j] == left_paren:
                depth += 1
            elif args[j] == right_paren:
                depth -= 1
            elif args[j] == comma and depth == 0:
                comma_indices.append(j)
        depth_end = j

        # remove commas and insert brackets
        args.insert(depth_end+1, right_paren)
        for index in reversed(comma_indices):
            args[index:index+1] = [right_paren, left_paren]
        args.insert(depth_start, left_paren)

    i += 1

# now parse the rolls
try:
    biggroup = Group(args)
    biggroup.execute()
except util.ParseException as e:
    print(e)