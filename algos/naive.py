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



def naive_compare_v2(pattern, text_slice, height, width, comp):
    """
    Returns (Match_Status, Last_I, Last_J) 
    to help the caller know where the mismatch happened.
    """
    for i in range(height):
        for j in range(width):
            if not comp(pattern[i, j], text_slice[i, j]):
                return False, i, j
    return True, None, None


def naive_search_v2(text: np.array, pattern: np.array):
    is_equal = Counter(lambda x, y: x == y)
    
    ph, pw = pattern.shape
    th, tw = text.shape

    cur_i = 0
    while cur_i <= th - ph:
        cur_j = 0
        while cur_j <= tw - pw:
            # Grab the current window
            text_slice = text[cur_i : cur_i + ph, cur_j : cur_j + pw]
            
            match, fail_i, fail_j = naive_compare_v2(pattern, text_slice, ph, pw, is_equal)
            
            if match:
                return is_equal.count, (cur_i, cur_j)
            
            # THE SKIP LOGIC:
            # If we failed at (fail_i, fail_j), we know the text at 
            # [cur_i + fail_i, cur_j + fail_j] is the 'bad' character.
            # This skips 'fail_j + 1' positions.
            skip = fail_j + 1
            cur_j += skip
            
        cur_i += 1 # Standard row increment

    return is_equal.count, None