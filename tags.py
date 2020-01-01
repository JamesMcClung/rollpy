import re
from statistic import *
from util import ParseException

YIELD = "-yield"

TOTAL = "-total"
MEAN = "-mean"
STD = "-std"
MEDIAN = "-median"
MODE = "-mode"
RANGE = "-range"
MAX = "-max"
MIN = "-min"

HIDE = "-hide"
VERBOSE = "-verbose"
NICE = "-nice"

special_tag_strs = [YIELD]
stat_tag_strs = [TOTAL, MEAN, STD, MEDIAN, MODE, RANGE, MAX, MIN]
print_tag_strs = [HIDE, VERBOSE, NICE]
supertag_strs = ["-" + tag for tag in stat_tag_strs + print_tag_strs + special_tag_strs]

all_tag_strs = special_tag_strs + stat_tag_strs + print_tag_strs + supertag_strs

_tag_regex = re.compile(r"^--?\w+$")
def isTag(s: str) -> bool:
    """Returns whether or not the given string is a possible tag."""
    return not _tag_regex.match(s) is None

class Tag:
    """A superclass for all tags. All tags have an associated content (usually just True, but could also be a formula or another tag)"""
    def __init__(self, keystr, contents=True):
        self.contents = contents
        self.keystr = keystr

    def clone(self):
        return Tag(self.keystr, contents=self.contents)


_formulae = {MEAN:mean, TOTAL:total, STD:std, MEDIAN:median, MIN:minimum, MAX:maximum, RANGE:range, MODE:mode}
class Statistic(Tag):
    """A tag that corresponds to a statistical value."""
    def __init__(self, keystr):
        super().__init__(keystr, contents=_formulae[keystr])
    
    def calculate(self, ls: list):
        self.__value, self.output = self.contents(ls)
    
    def print(self):
        print(self.output)
    
    def value(self):
        return self.__value
    
    def clone(self):
        return Statistic(self.keystr)

def get_tag(keystr: str, remaining_args: list) -> Tag:
    if not isTag(keystr):
        return None
    
    if keystr in special_tag_strs:
        if not remaining_args:
            raise ParseException("Arg missing after '{}' tag".format(keystr))
        if keystr == YIELD:
            nextarg = remaining_args[0]
            if nextarg not in stat_tag_strs:
                raise ParseException("Unable to yield arg: {}. Arg must be a valid stat tag, such as '{}' or '{}'.".format(nextarg, MEAN, TOTAL))
            return Tag(keystr, contents=nextarg)
    if keystr in stat_tag_strs:
        return Statistic(keystr)
    if keystr in all_tag_strs:
        return Tag(keystr)
    
    raise ParseException("Invalid tag: {}".format(keystr))