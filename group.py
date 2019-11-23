import re
from roll import Roll
from util import ParseException

tag_strs = ["-mean", "-verbose", "-std", "-min", "-max", "-range", "-median", "-mode", "-total", "-hide", "-nice"]
supertag_strs = ["-" + tag for tag in tag_strs] # these are tags that apply to all subgroups of a group
special_tag_strs = ["-yield"]

multiplierRegex = re.compile(r"^x(\d+)$")
left_sep = "["
right_sep = "]"

class Group(list):
    """A group is a list of rolls or other groups. It can be assigned properties using tags."""

    def __init__(self, args, depth=0):
        if len(args) == 0:
            raise Exception()
        self.tags = {tag:False for tag in tag_strs}
        self.supertags = {supertag:False for supertag in supertag_strs}
        self.special_tags = {special_tag:None for special_tag in special_tag_strs}
        self.vals = {tag:0 for tag in tag_strs}
        self.depth = depth
        del depth

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in self.tags:
                # parse tag
                self.tags[arg] = True
            elif arg in self.supertags:
                # parse supertag
                self.supertags[arg] = True
            elif arg in self.special_tags:
                if arg == "-yield":
                    if i+1 == len(args):
                        raise ParseException("Arg missing after yield.")
                    elif args[i+1] in self.tags:
                        self.special_tags[arg] = args[i+1]
                    else:
                        raise ParseException("Unable to yield arg: {}. Arg must be a valid tag, such as '-mean' or 'total'.".format(args[i+1]))
            else: 
                match = multiplierRegex.search(arg)
                if match:
                    # parse multiplier
                    self[-1:] = [self[-1]] * int(match.group(1))
                elif arg == left_sep:
                    # parse grouping symbol
                    depth = 1
                    for j, arg2 in enumerate(args[i+1:]):
                        j += i+1
                        depth += 1 if arg2 == left_sep else (-1 if arg2 == right_sep else 0)
                        if depth == 0:
                            self.append(Group(args[i+1:j], self.depth + 1))
                            i = j # hacky way to get around the increment later in the loop
                            break
                    if depth > 0:
                        raise ParseException("Unable to parse group from '{}' due to missing '{}'".format(" ".join(args), right_sep))
                else:
                    # parse roll
                    self.append(Roll(arg))
            i += 1

        self.__apply_supertags([supertag[1:] for supertag in self.supertags if self.supertags[supertag]])
    
    def __apply_supertags(self, tags:list):
        """Applies corresponding tag of each supertag to this group and all its descendents."""
        for tag in tags:
            self.tags[tag] = True
        for item in self:
            if isinstance(item, Group):
                item.__apply_supertags(tags)
    
    def __align_next_print(self):
        """Prints a number of spaces proportional to depth, but no newline, so that the next call to print() is aligned."""
        print("  " * self.depth, end = '')

    def execute(self, verbose: bool=True) -> int:
        """Executes every member (group or roll) in this group and prints according to tags.
        Returns the sum of the outcomes of each member by default."""

        outcomes = []
        verbose = self.tags["-verbose"] or not sum(self.tags.values())
        lastitemwasgroup = False


        # execute elements of group
        for item in self:
            if isinstance(item, Roll) and verbose:
                self.__align_next_print()
            if isinstance(item, Group) and not item.tags["-hide"]:
                if lastitemwasgroup:
                    print()
                lastitemwasgroup = True
            else:
                lastitemwasgroup = False
            outcomes.append(item.execute(verbose))

        total = sum(outcomes)
        mean = total / len(outcomes)
        issorted = False

        if not self.tags["-hide"]:
            if self.tags["-total"]:
                self.print_aligned("Total: " + str(total))
            if self.tags["-mean"]:
                self.print_aligned("Mean: " + str(mean))
            if self.tags["-std"]:
                std = "{:0.2f}".format((sum([(outcome - mean) ** 2 for outcome in outcomes]) / (len(outcomes) - 1)) ** .5) if len(outcomes) > 1 else "n/a"
                self.print_aligned("Standard Deviation: {}".format(std))
            if self.tags["-median"]:
                outcomes.sort()
                issorted = True
                self.print_aligned("Median: {}".format((outcomes[int(len(outcomes)/2)] + outcomes[int((len(outcomes) - 1)/2)])/2))
            if self.tags["-min"]:
                self.print_aligned("Min: {}".format(outcomes[0] if issorted else min(outcomes)))
            if self.tags["-max"]:
                self.print_aligned("Max: {}".format(outcomes[-1] if issorted else max(outcomes)))
            if self.tags["-range"]:
                self.print_aligned("Range: {}".format(outcomes[-1] - outcomes[0] if issorted else max(outcomes) - min(outcomes)))
            if self.tags["-mode"]:
                counts = {}
                for outcome in outcomes:
                    counts[outcome] = counts[outcome] + 1 if outcome in counts else 1
                max_count = max(counts.values())
                modes = set([str(outcome) for outcome in outcomes if counts[outcome] == max_count])
                print_aligned("Mode{}: {} ({} occurence{})".format("" if len(modes) == 1 else "s", ", ".join(modes), max_count, "" if max_count == 1 else "s"))
        
        if self.tags["-nice"]:
            print("Good job!")
        return total
    
    def print_aligned(self, label: str):
        """Prints the given string, aligned using __align_next_print"""
        self.__align_next_print()
        print(label)

    

