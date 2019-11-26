
def mean(ls):
    mean = sum(ls) / len(ls)
    return mean, "Mean: {}".format(mean)

def total(ls):
    total = sum(ls)
    return total, "Total: {}".format(total)

def std(ls):
    if len(ls) < 1:
        return -1, "Unable to find standard deviation of length-1 list."
    mean = sum(ls) / len(ls)
    std = (sum([(outcome - mean) ** 2 for outcome in ls]) / (len(ls) - 1)) ** .5
    return std, "Standard Deviation: {:0.2f}".format(std)

def median(ls):
    median = (ls[int(len(ls)/2)] + ls[int((len(ls) - 1)/2)])/2
    return median, "Median: {}".format(median)

def minimum(ls):
    minv = min(ls)
    return minv, "Minimum: {}".format(minv)

def maximum(ls):
    maxv = max(ls)
    return maxv, "Maximum: {}".format(maxv)

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