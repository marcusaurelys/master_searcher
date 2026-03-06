import numpy as np
from algos.counter import Counter

def compute_lps(pattern_row, is_equal):
    m = len(pattern_row)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        # Use counter for the preprocessing too if you want total accuracy
        if is_equal(pattern_row[i], pattern_row[length]):
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def greedy_kmp_search(text: np.array, pattern: np.array):
    is_equal = Counter(lambda x, y: x == y)
    t_height, t_width = text.shape
    p_height, p_width = pattern.shape

    if p_height > t_height or p_width > t_width:
        return 0, None

    # Precompute LPS for the first row of the pattern
    first_row_pattern = pattern[0]
    lps = compute_lps(first_row_pattern, is_equal)

    # Search through each row of the text
    for i in range(t_height - p_height + 1):
        j = 0  # index for text row
        k = 0  # index for pattern row
        
        while j < t_width:
            if is_equal(text[i, j], first_row_pattern[k]):
                j += 1
                k += 1

            if k == p_width:
                # Potential match found for the first row!
                # Start greedy verification for the remaining rows
                start_j = j - k
                full_match = True
                
                for r in range(1, p_height):
                    for c in range(p_width):
                        if not is_equal(text[i + r, start_j + c], pattern[r, c]):
                            full_match = False
                            break
                    if not full_match: break
                
                if full_match:
                    return is_equal.count, (i, start_j)
                
                # If verification failed, continue KMP search
                k = lps[k - 1]
            
            elif j < t_width and not is_equal(text[i, j], first_row_pattern[k]):
                if k != 0:
                    k = lps[k - 1]
                else:
                    j += 1

    return is_equal.count, None


def get_bad_char_table(pattern_row):
    # Since values are 0s and 1s, we use a simple dict or array
    table = {val: i for i, val in enumerate(pattern_row)}
    return table

def greedy_bm_search(text: np.array, pattern: np.array):
    is_equal = Counter(lambda x, y: x == y)
    t_height, t_width = text.shape
    p_height, p_width = pattern.shape

    if p_height > t_height or p_width > t_width:
        return 0, None

    first_row_p = pattern[0]
    bad_char = get_bad_char_table(first_row_p)

    for i in range(t_height - p_height + 1):
        s = 0  # shift of the pattern with respect to text
        while s <= (t_width - p_width):
            j = p_width - 1
            
            # Right-to-left comparison for the first row
            while j >= 0 and is_equal(first_row_p[j], text[i, s + j]):
                j -= 1

            if j < 0:
                # Match found for the first row! Trigger greedy verification
                full_match = True
                for r in range(1, p_height):
                    for c in range(p_width):
                        if not is_equal(text[i + r, s + c], pattern[r, c]):
                            full_match = False
                            break
                    if not full_match: break
                
                if full_match:
                    return is_equal.count, (i, s)
                
                # Shift pattern to find next potential first-row match
                s += (p_width - bad_char.get(text[i, s + p_width], -1) 
                      if s + p_width < t_width else 1)
            else:
                # Mismatch: shift based on the bad character rule
                bad_val = text[i, s + j]
                s += max(1, j - bad_char.get(bad_val, -1))

    return is_equal.count, None