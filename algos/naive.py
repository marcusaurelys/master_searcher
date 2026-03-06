import numpy as np
from algos.counter import Counter

#compares two patterns
def naive_compare(x, y, height, width, comp):
    for i in range(height):
        for j in range(width):
            if not comp(x[i, j], y[i, j]):
                return False
    return True

def naive_search(text: np.array, pattern: np.array):

    #instantiate comp counter
    is_equal = Counter(lambda x, y: x==y)

    pattern_height, pattern_width = pattern.shape
    text_height, text_width = text.shape

    #while pattern is within bound of text
    for cur_i in range(text_height-pattern_height+1):
        for cur_j in range(text_width-pattern_width+1):
            text_slice = text[cur_i:cur_i+pattern_height, cur_j:cur_j+pattern_width]
            if naive_compare(pattern, text_slice, pattern_height, pattern_width, is_equal):
                return is_equal.count, (cur_i, cur_j)

    return is_equal.count, None