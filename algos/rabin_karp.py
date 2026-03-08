import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from algos.counter import Counter

def rabin_karp_search(text: np.array, pattern: np.array):
    is_equal = Counter(lambda x, y: x == y)
    
    p_height, p_width = pattern.shape
    t_height, t_width = text.shape
    
    if p_height > t_height or p_width > t_width:
        return 0, None

    # Constants for hashing
    X_BASE, Y_BASE = 31, 37
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

   # row rolling hash
    for i in range(t_height):
        curr_h = 0
        for j in range(t_width):
            curr_h = (curr_h * Y_BASE + int(text[i, j])) % MOD
            if j >= p_width:
                curr_h = (curr_h - int(text[i, j - p_width]) * y_pow % MOD + MOD) % MOD
            if j >= p_width - 1:
                row_hashes[i, j - p_width + 1] = curr_h


    x_pow = pow(X_BASE, p_height, MOD)
    
    # column rolling hash
    for j in range(t_width - p_width + 1):
        curr_v_h = 0
        for i in range(t_height):
            curr_v_h = (curr_v_h * X_BASE + row_hashes[i, j]) % MOD
            if i >= p_height:
                curr_v_h = (curr_v_h - row_hashes[i - p_height, j] * x_pow % MOD + MOD) % MOD
            
            if i >= p_height - 1:
                if is_equal(curr_v_h, p_hash):
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


def vectorized_rabin_karp(text: np.array, pattern: np.array):
    is_equal = Counter(lambda x, y: x == y)
    t_height, t_width = text.shape
    p_height, p_width = pattern.shape
    
    if p_height > t_height or p_width > t_width:
        return 0, None

    Y_BASE, X_BASE = 31, 37
    MOD = 2**61 - 1

    # 1. Precompute Pattern Hash
    y_exponents = np.arange(p_width)[::-1]
    y_powers = np.array([pow(int(Y_BASE), int(e), int(MOD)) for e in y_exponents])
    
    x_exponents = np.arange(p_height)[::-1]
    x_powers = np.array([pow(int(X_BASE), int(e), int(MOD)) for e in x_exponents])
    
    row_hashes = np.sum((pattern * y_powers) % MOD, axis=1) % MOD
    p_hash = np.sum((row_hashes * x_powers) % MOD) % MOD

    # 2. Vectorized Text Hashing
    windows = sliding_window_view(text, (p_height, p_width))

    # Calculate hashes for ALL windows at once using NumPy matrix math
    h_hashes = np.sum((windows * y_powers) % MOD, axis=-1) % MOD
    
    # Vertical hash: apply x_powers across the remaining pattern-height dimension
    v_hashes = np.sum((h_hashes * x_powers) % MOD, axis=-1) % MOD

    v_h, v_w = v_hashes.shape
    for i in range(v_h):
        for j in range(v_w):
            # Fair comparison: comparing the window's hash to the pattern's hash
            if is_equal(v_hashes[i, j], p_hash):
                # Greedy verification: check the actual characters immediately
                match = True
                for r in range(p_height):
                    for c in range(p_width):
                        if not is_equal(pattern[r, c], text[i + r, j + c]):
                            match = False
                            break
                    if not match: break
                
                if match:
                    return is_equal.count, (i, j)

    return is_equal.count, None