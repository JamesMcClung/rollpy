import re
from random import randint
from util import make_strikethrough, ParseException, make_bold

class Roll:
    count_regex = re.compile(r"(?P<take>(?P<val>\d*)d)")                  # finds the count, or number of dice to roll
    die_regex = re.compile(r"(?:d|^)(?P<take>(?P<val>\d+))(?!d|\d)")      # finds the die (type) to roll
    bonus_regex = re.compile(r"(?P<take>(?P<val>[\+-]\d+))")              # finds the bonus or penalty to the roll
    reroll_regex = re.compile(r"\d(?P<take>r(?P<val>\d+))")                 # finds the threshold for rerolling
    ceil_regex = re.compile(r"\d(?P<take>h(?P<val>\d+))")                   # finds the top n dice to take
    floor_regex = re.compile(r"\d(?P<take>l(?P<val>\d+))")                  # finds the bottom n dice to take
    label_regex = re.compile(r"\d(?P<take>:(?P<val>.*))")                   # finds the label string

    def __init__(self, arg: str):
        """Initializes a new roll based on the given input string (e.g. "2d20h1")"""
        self.count, counttake = Roll.get_val(Roll.count_regex, arg, 1, 1)
        self.die, dietake = Roll.get_val(Roll.die_regex, arg, 20)
        self.bonus, bonustake = Roll.get_val(Roll.bonus_regex, arg, 0)
        self.reroll, rerolltake = Roll.get_val(Roll.reroll_regex, arg, 0, 1)
        self.ceil, ceiltake = Roll.get_val(Roll.ceil_regex, arg, 0, 1)
        self.floor, floortake = Roll.get_val(Roll.floor_regex, arg, 0, 1)
        self.label, labeltake = Roll.get_val(Roll.label_regex, arg, "", "", interpreter=str)

        self.is_valid = True
        # ensure that every part of the input string is used precisely once (i.e., that the string is valid)
        takes = [counttake, dietake, bonustake, rerolltake, ceiltake, floortake, labeltake]
        reduced_arg = arg
        for take in takes:
            if take in reduced_arg:
                reduced_arg = reduced_arg.replace(take, "", 1)
            else:
                self.is_valid = False
        if reduced_arg:
            self.is_valid = False
        if not self.is_valid:
            raise ParseException("Unable to parse '{}' as roll".format(arg))

    @staticmethod
    def get_val(regex, s: str, default_if_absent: int, default_if_empty: int = 0, interpreter = int) -> (str, str):
        """Finds a value in a string s. If no value exists, returns default.
        Return: a tuple (val, take) where take is the part of the given string that was actually used."""
        if (m := regex.search(s)) is None:
            return default_if_absent, ""
        return interpreter(m.group("val") or default_if_empty), m.group("take")
    
    def execute(self, print_output=True) -> int:
        """Executes the roll. Results are returned and the procedure is printed."""
        if not self.is_valid:
            return -1

        # find sum of dice and preliminary result string
        results = []
        result_strs = []
        for _ in range(self.count):
            first, rerolled = self.get_die_roll()
            results.append(rerolled or first)
            result_strs.append(make_strikethrough(str(first)) + " " + str(rerolled) if rerolled else str(first))
        die_sum = sum(results)

        # find highs and lows if needed
        removed_results = []
        if self.ceil:
            removed_results += sorted(results)[:-self.ceil]
        if self.floor:
            removed_results += sorted(results)[self.floor:]
        for rr in removed_results:
                rri = results.index(rr)
                results[rri] = 0 # change the value so it does not get indexed again
                die_sum -= rr
                result_strs[rri] = make_strikethrough(result_strs[rri])

        total = die_sum + self.bonus

        outcomestr = make_bold(str(total))

        # convert to string
        if print_output:
            print_str = "Rolling {}: {}".format(str(self), die_sum if self.bonus else outcomestr)
            if self.bonus:
                print_str += " -> " + outcomestr
            if self.label:
                print_str += " " + self.label
            if self.count > 1 or self.reroll:
                print_str += " ({})".format(", ".join(result_strs))
            print(print_str)
        return total
    
    def get_die_roll(self) -> (int, int):
        """Rolls a single die, rerolling if below the reroll threshhold.\n
        Returns a tuple of ints: (final number on die, number on die before reroll [or None])"""
        if self.die == 0:
            return 0, (0 if self.reroll else None)
        result = randint(1, self.die)
        if result <= self.reroll:
            return result, randint(1, self.die)
        return result, None
    
    def __str__(self):
        s = "{}d{}".format(self.count, self.die)
        if self.bonus > 0:
            s += "+" + str(self.bonus)
        elif self.bonus < 0:
            s += str(self.bonus)
        if self.reroll:
            s += ",r{}".format(self.reroll)
        if self.ceil:
            s += ",h{}".format(self.ceil)
        if self.floor:
            s += ",l{}".format(self.floor)
        return s
    
    def clone(self):
        """Clones the roll, returning an identical Roll."""
        newroll = Roll.__new__(Roll)
        fields = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        for field in fields:
            dir(newroll)[field] = dir(self)[field]
        return newroll