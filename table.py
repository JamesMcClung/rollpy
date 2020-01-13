import re
import util

# table syntax: {key1=val1;key2=val2}=key
_table_regex = re.compile(r"{(?P<items>(?:\w*=\w*[;}])+)=(?P<key>\d+)$")
_item_regex = re.compile(r"(?P<item>\w*=\w*)[;}]")

def is_table(arg: str) -> bool:
    return _table_regex.match(arg)

class Table(dict):
    def __init__(self, arg: str):
        if match := _table_regex.match(arg):
            items = match.group("items")
            self.key = match.group('key')
        else:
            raise util.ParseException("Failure: invalid table string '{}'".format(arg))
        
        for itemstr in _item_regex.finditer(items):
            item = itemstr.group('item').split('=')
            self[item[0]] = item[1]
    
    def execute(self, print_output: bool = False):
        result = self[self.key]
        if print_output:
            print("Outcome of table: " + result)
        return result
    
