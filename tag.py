

class Statistic:
    def __init__(self, formula):
        self.format_name = format_name
        self.formula = formula
    
    def calculate(self, ls: list):
        self.value, self.output = self.formula(ls)
    
    def print(self):
        print(self.output)
    
    def value(self):
        return self.value


def mean(ls):
    mean = sum(ls) / len(ls)
    return mean, "Mean: {}".format(mean)

def total(ls):
    total = sum(ls)
    return total, "Total: {}".format(total)

def std(ls):
    if len(ls) < 1:
        return -1, "Unable to find standard deviation of length-1 list."
    std = (sum([(outcome - mean) ** 2 for outcome in ls]) / (len(ls) - 1)) ** .5
    return std, "Standard Deviation: {:0.2f}".format(std)

def median(ls):
    median = (ls[int(len(ls)/2)] + ls[int((len(ls) - 1)/2)])/2
    return median, "Median: {}".format(median)

def min(ls):
    min = min(ls)
    return min, "Minimum: {}".format(min)

def max(ls):
    max = max(ls)
    return max, "Maximum: {}".format(max)

def range(ls):
    range = max(ls) - min(ls)
    return range, "Range: {}".format(range)

def mode(ls):
    counts = {}
    for el in ls:
        counts[el] = counts[el] + 1 if el in counts else 1
    max_count = max(counts.values())
    modes = set([el for el in ls if counts[el] == max_count])
    return modes, "Mode{}: {} ({} occurence{})".format("" if len(modes) == 1 else "s", ", ".join(map(str, modes)), max_count, "" if max_count == 1 else "s")