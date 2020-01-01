import re
from roll import Roll
import util
import tags
import modifier

multiplier_regex = re.compile(r"^x(\d+)$")
left_sep = util.LEFT_PAREN
right_sep = util.RIGHT_PAREN

class Group(list):

    def __init__(self, args, layer=0):
        if len(args) == 0:
            raise util.ParseException("Unable to parse empty group.")
        self.depth = layer

        self.all_tags = {t:None for t in tags.all_tag_strs}
        self.askedForStat = False

        i = 0
        firstStatFound = None
        while i < len(args):
            arg = args[i]

            # handle tags
            tag = tags.get_tag(arg, args[i+1:])
            if tag:
                self.all_tags[arg] = tag
                if arg in tags.stat_tag_strs:
                    firstStatFound = firstStatFound or arg
                    self.askedForStat = True
                if arg in tags.supertag_strs:
                    args.insert(i+1, arg[1:])
            elif modifier.is_modifier(arg):
                if self:
                    modifier.modify(self[-1], arg)
                else:
                    raise util.ParseException("Modifier '{}' requires something to modify.".format(arg))
            else:
                # handle multipliers
                multiplier_match = multiplier_regex.search(arg)
                if multiplier_match:
                    # parse multiplier
                    self[-1:] = [self[-1]] * int(multiplier_match.group(1))
                elif arg == left_sep:
                    # parse grouping symbol
                    layer = 1
                    for j, arg2 in enumerate(args[i+1:]):
                        j += i+1
                        layer += 1 if arg2 == left_sep else (-1 if arg2 == right_sep else 0)
                        if layer == 0:
                            self.append(Group(args[i+1:j], self.depth + 1))
                            i = j # hacky way to get around the increment later in the loop
                            break
                    if layer > 0:
                        raise util.ParseException("Unable to parse group from '{}' due to missing '{}'".format(" ".join(args), right_sep))
                else:
                    # parse roll
                    self.append(Roll(arg))
            i += 1
        
        if not self.all_tags[tags.YIELD]:
            self.__set_yield(firstStatFound or tags.TOTAL)

        self.__apply_supertags(self.all_tags)
    
    def __set_yield(self, stat: str):
        self.all_tags[tags.YIELD] = tags.Tag(tags.YIELD, stat)
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