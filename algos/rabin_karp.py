import numpy as np
from algos.counter import Counter

def rabin_karp_search(text: np.array, pattern: np.array):
    is_equal = Counter(lambda x, y: x == y)
    
    p_height, p_width = pattern.shape
    t_height, t_width = text.shape
    
    if p_height > t_height or p_width > t_width:
        return 0, None

    # Constants for hashing
    X_BASE, Y_BASE = 3, 5
    MOD = 10**9 + 7

    # 1. Precompute Pattern Hash
    p_hash = 0
    for i in range(p_height):
        row_h = 0
        for j in range(p_width):
            row_h = (row_h * Y_BASE + pattern[i, j]) % MOD
        p_hash = (p_hash * X_BASE + row_h) % MOD

    row_hashes = np.zeros((t_height, t_width - p_width + 1), dtype=int)
    y_pow = pow(Y_BASE, p_width, MOD)

    for i in range(t_height):
        curr_h = 0
        for j in range(t_width):
            curr_h = (curr_h * Y_BASE + text[i, j]) % MOD
            if j >= p_width:
                curr_h = (curr_h - text[i, j - p_width] * y_pow) % MOD
            if j >= p_width - 1:
                row_hashes[i, j - p_width + 1] = curr_h

    x_pow = pow(X_BASE, p_height, MOD)
    
    for j in range(t_width - p_width + 1):
        curr_v_h = 0
        for i in range(t_height):
            curr_v_h = (curr_v_h * X_BASE + row_hashes[i, j]) % MOD
            if i >= p_height:
                curr_v_h = (curr_v_h - row_hashes[i - p_height, j] * x_pow) % MOD
            
            if i >= p_height - 1:
                if curr_v_h == p_hash:
                    start_i = i - p_height + 1
                    match = True
                    # Verification loop using is_equal
                    for r in range(p_height):
                        for c in range(p_width):
                            if not is_equal(pattern[r, c], text[start_i + r, j + c]):
                                match = False
                                break
                        if not match: break
                    
                    if match:
                        return is_equal.count, (start_i, j)

    return is_equal.count, None