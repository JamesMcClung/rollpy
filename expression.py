import util
import re

_expression_regex = re.compile(r"(?P<label>\w*)=(?P<expr>[\d\.\*\+-/]+)$")

def is_expression(arg: str) -> bool:
    """Determines if the given string is an expression."""
    return _expression_regex.match(arg)

def parse_math(arg: str) -> float:
    """A basic parser for math. Evaluates a string like '3+2.5*-2' to be -11.0. Returns a float."""
    if match := _expression_regex.match(arg):
        arg = match.group('expr')
    else:
        raise util.ParseException("Failure: '{}' is not an expression.".format(arg))

    result = 0.0
    nextop = result.__add__
    num = ''
    # just do them in order, no PEMDAS
    for c in arg:
        if ('0' <= c and c <= '9') or c == '.':
            num += c
        elif not num and c == '-':
            num = '-'
        else:
            result = nextop(float(num))
            num = ''
            nextop = {'+':result.__add__, '-':result.__sub__, '*':result.__mul__, '/':result.__truediv__}[c]
    result = nextop(float(num))
    return result

class Expression:
    def __init__(self, arg: str):
        if match := _expression_regex.match(arg):
            self.label = match.group('label')
            self.value = int(parse_math(arg))
        else:
            raise util.ParseException("Failure: cannot parse '{}' as expression.".format(arg))
    
    def execute(self, print_output: bool = False) -> int:
        if print_output:
            print("{} = {}".format(self.label, self.value))
        return self.value

def get_expression(val: int, label: str = "") -> str:
    """Returns a valid expression string (with optional label) that evaluates to the given val."""
    return label + "=" + str(val)