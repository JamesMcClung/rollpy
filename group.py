import re
from roll import Roll
import util
import tags
import modifier

multiplier_regex = re.compile(r"^x(\d+)$")
left_sep = util.LEFT_PAREN
right_sep = util.RIGHT_PAREN

class Group(list):

    def __init__(self, args, depth=0):
        if len(args) == 0:
            raise util.ParseException("Unable to parse empty group.")
        self.depth = depth

        self.all_tags = {t:None for t in tags.all_tag_strs}
        self.askedForStat = False

        i = 0
        firstStatFound = None
        while i < len(args):
            arg = args[i]

            # handle tags
            if tag := tags.get_tag(arg, args[i+1:]):
                self.all_tags[arg] = tag
                if arg in tags.stat_tag_strs:
                    firstStatFound = firstStatFound or arg
                    self.askedForStat = True
                if arg in tags.supertag_strs:
                    args.insert(i+1, arg[1:])
            
            # handle modifiers
            elif modifier.is_modifier(arg):
                if self: # if there is anything to modify
                    modifier.modify(self[-1], arg)
                else:
                    raise util.ParseException("Error: modifier '{}' requires something to modify.".format(arg))

            # handle multipliers
            elif multiplier_match := multiplier_regex.search(arg):
                if self: # if there is anything to modify
                    self[-1:] = [self[-1]] * int(multiplier_match.group(1))
                else:
                    raise util.ParseException("Error: multiplier '{}' requires something to multiply.".format(arg))
            
            # handle separators for grouping
            elif arg == left_sep:
                depth = 1 # relative depth
                j = i+1
                while depth > 0:
                    j += 1
                    if j == len(args):
                        raise util.ParseException("Unable to parse group from '{}' due to missing '{}'".format(" ".join(args), right_sep))

                    if args[j] == right_sep:
                        depth -= 1
                    elif args[j] == left_sep:
                        depth += 1
                self.append(Group(args[i+1:j], self.depth + 1))
                i = j

            # assume it is a normal roll
            else:
                self.append(Roll(arg))
            
            # last line of code in the loop
            i += 1
        
        if not self.all_tags[tags.YIELD]:
            self.__set_yield(firstStatFound or tags.TOTAL)

        self.__apply_supertags(self.all_tags)
    
    def __set_yield(self, stat: str):
        """Determines what the group returns upon execution"""
        self.all_tags[tags.YIELD] = tags.Tag(tags.YIELD, contents=stat)
        self.all_tags[stat] = tags.get_tag(stat, [])
    
    def __apply_supertags(self, _tags:list):
        """Applies corresponding tag of each supertag to this group and all its descendents."""
        for sts in tags.supertag_strs:
            st = _tags[sts]
            if st:
                nsts = sts[1:]
                self.all_tags[nsts] = _tags[nsts].clone()
                if nsts == tags.YIELD:
                    self.all_tags[_tags[tags.YIELD].value()] = _tags[_tags[tags.YIELD].value()].clone()
                
        for item in self:
            if isinstance(item, Group):
                item.__apply_supertags(_tags)
    
    def __align_next_print(self):
        """Prints a number of spaces proportional to depth, but no newline, so that the next call to print() is aligned."""
        print("  " * self.depth, end = '')

    def execute(self, print_rolls: bool=True) -> int:
        """Executes every member (group or roll) in this group and prints according to tags.
        Returns the sum of the outcomes of each member by default."""

        outcomes = []
        print_rolls = self.all_tags[tags.VERBOSE] or (not self.askedForStat and (len(self) == 1 or self.depth == 0))
        print_stats = not (self.all_tags[tags.HIDE] or len(self) == 1)
        lastitemwasgroup = False

        # execute elements of group
        for item in self:
            if isinstance(item, Roll) and print_rolls:
                self.__align_next_print()
            if isinstance(item, Group) and not item.all_tags[tags.HIDE]:
                if lastitemwasgroup:
                    print()
                lastitemwasgroup = True
            else:
                lastitemwasgroup = False
            outcomes.append(item.execute(print_rolls))

        # calculate and print statistics as needed
        for stat in tags.stat_tag_strs:
            if self.all_tags[stat]:
                self.all_tags[stat].calculate(outcomes)
                if print_stats:
                    self.__align_next_print()
                    self.all_tags[stat].print()
            
        if self.all_tags[tags.NICE]:
            print("Good job!")
 
        return self.all_tags[self.all_tags[tags.YIELD].contents].value()