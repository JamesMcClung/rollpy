import re
from roll import Roll
import util
import group

# an arg is a modifier iff it starts with this char
MODIFIER_INDICATOR = '.'

def is_modifier(arg: str) -> bool:
    """Returns whether or not the given arg is formatted as a modifier."""
    return arg[0] == MODIFIER_INDICATOR

# regexes used to extract information from modifier strings
_bonus_regex = re.compile(r"^\.(?P<val>[\+-]\d+)$")
_count_regex = re.compile(r"^\.c(?P<type>[x\+])(?P<val>\d+)$")
_highlow_regex = re.compile(r"^\.(?P<type>[hl])(?P<val>\d+)$")
_label_regex = re.compile(r"^\.label=(?P<val>)$")

def modify(roll, arg: str):
    """Modifies the given roll (or rolls, if a group was passed) according to the given arg (a modifier)."""
    # recursively apply to groups
    if isinstance(roll, group.Group):
        for thing in roll:
            modify(thing, arg)
        return

    if match := _bonus_regex.match(arg):
        # change the roll's bonus
        roll.bonus += int(match.group("val"))
    elif match := _count_regex.match(arg):
        # change the number of dice in the roll
        val = int(match.group("val"))
        if match.group("type") == "x":
            roll.count *= val
        else:
            roll.count += val
    elif match := _highlow_regex.match(arg):
        # change the number of dice to take, whether the highest or lowest
        val = int(match.group("val"))
        if match.group("type") == "h":
            roll.ceil = val
        else:
            roll.floor = val
    elif match := _label_regex.match(arg):
        # change the label
        roll.label = match.group("val")
    else:
        raise util.ParseException("Invalid modifier: '{}'".format(arg))

def get_bonus_modifier(bonus: int) -> str:
    """Returns a valid bonus modifier."""
    return MODIFIER_INDICATOR + ("+" if bonus >= 0 else "") + str(bonus)

def get_count_modifier(mod: int, type: str = "times"):
    """Returns a valid count modifier.\n
    mod: a positive integer\n
    type: either 'times' or 'plus' to multiply or add to the count, respectively"""
    if type == "times":
        return MODIFIER_INDICATOR + "cx" + str(mod)
    elif type == "plus":
        return MODIFIER_INDICATOR + "c+" + str(mod)

def get_highlow_modifier(val: int, type: str):
    """Returns a valid reroll modifier.\n
    val: a positive integer to set the number of dice to use\n
    type: either 'h' or 'l' to take the highest or lowest dice, respectively
    """
    if type == 'h':
        return MODIFIER_INDICATOR + 'h' + str(val)
    elif type == 'l':
        return MODIFIER_INDICATOR + 'l' + str(val)

def get_label_modifier(label: str):
    """Returns a valid label modifier."""
    return MODIFIER_INDICATOR + "label=" + label