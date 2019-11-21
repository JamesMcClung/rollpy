import sys
import re
from random import randint
from macros import macros

def strikethrough(s: str) -> str:
    return "".join([c + '\u0336' for c in s])

class Roll:
    count_regex = re.compile(r"(?P<take>(?P<val>\d*)d)")                  # finds the count, or number of dice to roll
    die_regex = re.compile(r"(?:d|^)(?P<take>(?P<val>\d+))(?!d|\d)")      # finds the die (type) to roll
    bonus_regex = re.compile(r"(?P<take>(?P<val>[\+-]\d+))")              # finds the bonus or penalty to the roll
    reroll_regex = re.compile(r"(?P<take>r(?P<val>\d*))")                 # finds the threshold for rerolling
    ceil_regex = re.compile(r"(?P<take>h(?P<val>\d*))")                   # finds the top n dice to take
    floor_regex = re.compile(r"(?P<take>l(?P<val>\d*))")                  # finds the bottom n dice to take

    def __init__(self, s: str):
        self.count, counttake = Roll.get_val(Roll.count_regex, s, 1, 1)
        self.die, dietake = Roll.get_val(Roll.die_regex, s, 20)
        self.bonus, bonustake = Roll.get_val(Roll.bonus_regex, s, 0)
        self.reroll, rerolltake = Roll.get_val(Roll.reroll_regex, s, 0, 1)
        self.ceil, ceiltake = Roll.get_val(Roll.ceil_regex, s, 0, 1)
        self.floor, floortake = Roll.get_val(Roll.floor_regex, s, 0, 1)

        self.input = s
        self.badinput = False
        takes = [counttake, dietake, bonustake, rerolltake, ceiltake, floortake]
        for take in takes:
            if take in s:
                s = s.replace(take, "")
            else:
                self.badinput = True
        if s:
            self.badinput = True

    @staticmethod
    def get_val(regex, s: str, default_if_absent: int, default_if_empty: int = 0) -> (int, str):
        """Finds a value in a string s. If no value exists, returns default.
        Return: a tuple (val, take) where take is the part of the given string that was actually used."""
        m = regex.search(s)
        if m is None:
            return default_if_absent, ""
        return int(m.group("val") or default_if_empty), m.group("take")
    
    def do_roll(self, print_output=True) -> int:
        """Executes the roll. Results are returned and the procedure is printed."""
        if self.badinput:
            print("invalid input: {}".format(self.input))
            return 0

        # find sum of dice and preliminary result string
        results = []
        result_strs = []
        for _ in range(self.count):
            first, rerolled = self.get_die_roll()
            results.append(rerolled or first)
            result_strs.append(strikethrough(str(first)) + " " + str(rerolled) if rerolled else str(first))
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
                result_strs[rri] = strikethrough(result_strs[rri])

        total = die_sum + self.bonus

        # convert to string
        if print_output:
            print_str = "Rolling {}: {}".format(str(self), die_sum)
            if self.bonus:
                print_str += " -> " + str(total)
            if self.count > 1 or self.reroll:
                print_str += " ({})".format(", ".join(result_strs))
            print(print_str)
        return total
    
    def get_die_roll(self) -> (int, int):
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
            s += ",l{}".format(self.ceil)
        return s

# Execution

# get user input
args = sys.argv[1:]

separator = ","

def intersperse(ls: list, sep):
    result = [sep] * (len(ls) * 2 - 1)
    result[0::2] = ls
    return result

# handle separators (","), macros (e.g. "stat"), and tags(e.g. "-mean")
tag_strs = ["-mean", "-verbose", "-std", "-min", "-max", "-range", "-median", "-mode"]
tag_strs += ["-" + tag for tag in tag_strs] # these are the tags that compare totals from all groups
tags = {tag:False for tag in tag_strs}

stillmacros = True
while stillmacros:
    stillmacros = False
    i = 0
    while i < len(args):
        if args[i] in tags:
            tags[args[i]] = True
            del args[i]
            continue
    
        if separator in args[i] and separator != args[i]:
            stillmacros = True
            splitargs = args[i].split(separator)
            t = [el for el in intersperse(splitargs, separator) if el]
            args[i:i+1] = t
        if args[i] in macros:
            stillmacros = True
            args[i:i+1] = macros[args[i]].split()
        i += 1

# apply multipliers (e.g. "x3" to execute everything before it 3 times)
multiplierRegex = re.compile(r"^x(\d+)$")
i = 0
while i < len(args):
    match = multiplierRegex.search(args[i])
    if match:
        stillmultipliers = True
        factor = int(match.group(1))
        args[:i+1] = args[:i] * factor
        i = factor * i
    else:
        i += 1

# separate rolls into groups according to separator
# group totals are calculated independently of each other
groups = [[]] # list of groups (lists of rolls)
for arg in args:
    if arg == separator:
        groups.append([])
    else:
        groups[-1].append(Roll(arg))

groups = [sr for sr in groups if sr] # remove empty groups

# execute rolls
for group in groups:
    if group:
        results = []
        verbose = tags["-verbose"] or not sum(tags.values())
        for roll in group:
            results.append(roll.do_roll(verbose))

        results.sort()
        total = sum(results)
        mean = total / len(results)

        if verbose and (len(groups) > 1 or len(group) > 1):
            print("Total: " + str(total))
        if tags["-mean"]:
            print("Mean: " + str(mean))
        if tags["-std"]:
            std = (sum([(result - mean) ** 2 for result in results]) / (len(results) - 1)) ** .5 if len(results) > 1 else "n/a"
            print("Standard Deviation: {:0.2f}".format(std))
        if tags["-min"]:
            print("Min: {}".format(results[0]))
        if tags["-max"]:
            print("Max: {}".format(results[-1]))
        if tags["-range"]:
            print("Range: {}".format(results[-1] - results[0]))
        if tags["-median"]:
            print("Median: {}".format((results[int(len(results)/2)] + results[int((len(results) - 1)/2)])/2))
        if tags["-mode"]:
            counts = {}
            for result in results:
                counts[result] = counts[result] + 1 if result in counts else 1
            max_count = max(counts.values())
            modes = set([str(result) for result in results if counts[result] == max_count])
            print("Mode{}: {} ({} occurence{})".format("" if len(modes) == 1 else "s", ", ".join(modes), max_count, "" if max_count == 1 else "s"))

        if not group is groups[-1]:
            print()