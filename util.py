def intersperse(ls: list, sep):
    result = [sep] * (len(ls) * 2 - 1)
    result[0::2] = ls
    return result

def strikethrough(s: str) -> str:
    return "".join([c + '\u0336' for c in s])

class ParseException(Exception):
    pass