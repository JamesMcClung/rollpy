import re
from roll import Roll
import util

# an arg is a modifier iff it starts with this char
MODIFIER_INDICATOR = '.'

def is_modifier(arg: str) -> bool:
    """Returns whether or not the given arg is formatted as a modifier."""
    return arg[0] == MODIFIER_INDICATOR

_bonus_regex: re.Pattern = re.compile(r"^\.(?P<val>[\+-]\d+)$")
def modify(roll: Roll, modifier: str):
    """Modifies the given roll according to the given modifier."""
    if _bonus_regex.match(modifier):
        # change the roll's bonus
        bonus = int(_bonus_regex.search(modifier).group("val"))
        roll.bonus += bonus
    else:
        raise util.ParseException("Invalid modifier: '{}'".format(modifier))

def get_bonus_modifier(bonus: int) -> str:
    """Returns a valid bonus modifier."""
    return MODIFIER_INDICATOR + ("+" if bonus >= 0 else "") + str(bonus)