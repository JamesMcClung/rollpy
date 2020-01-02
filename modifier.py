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

def modify(roll, arg: str):
    """Modifies the given roll (or rolls, if a group was passed) according to the given arg (a modifier)."""
    # recursively apply to groups
    if isinstance(roll, group.Group):
        for thing in roll:
            modify(thing, arg)
        return

    if _bonus_regex.match(arg):
        # change the roll's bonus
        bonus = int(_bonus_regex.search(arg).group("val"))
        roll.bonus += bonus
    elif _count_regex.match(arg):
        # change the number of dice in the roll
        type = _count_regex.search(arg).group("type")
        val = int(_count_regex.search(arg).group("val"))
        if type == "x":
            roll.count *= val
        else:
            roll.count += val
    elif _highlow_regex.match(arg):
        # change the number of dice to take, whether the highest or lowest
        type = _highlow_regex.search(arg).group("type")
        val = int(_highlow_regex.search(arg).group("val"))
        if type == "h":
            roll.ceil = val
        else:
            roll.floor = val
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
