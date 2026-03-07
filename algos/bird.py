import numpy as np
from algos.counter import Counter



def _build_column_ids(pattern: np.array, is_equal):
    p_height, p_width = pattern.shape
    ids = []
    unique_cols = []

    for j in range(p_width):
        col = pattern[:, j]
        found = -1
        for uid, ucol in enumerate(unique_cols):
            if all(is_equal(col[r], ucol[r]) for r in range(p_height)):
                found = uid
                break
        if found == -1:
            found = len(unique_cols)
            unique_cols.append(col)
        ids.append(found)

    return ids, unique_cols          # ids[j] = ID of pattern column j


def _build_ac_goto(unique_cols, p_height, is_equal):
    goto = [{}]          # state 0 = root
    output = {0: -1}
    fail = [0]

    for col_id, col in enumerate(unique_cols):
        state = 0
        for r in range(p_height):
            val = col[r]
            # find a matching transition (values compared via Counter)
            next_state = None
            for key, ns in goto[state].items():
                if is_equal(key, val):
                    next_state = ns
                    break
            if next_state is None:
                next_state = len(goto)
                goto.append({})
                output[next_state] = -1
                fail.append(0)
                goto[state][val] = next_state
            state = next_state
        output[state] = col_id   # accepting state

    from collections import deque
    queue = deque()

    for val, s in goto[0].items():
        fail[s] = 0
        queue.append(s)

    while queue:
        r = queue.popleft()
        for val, s in goto[r].items():
            queue.append(s)
            state = fail[r]
            # follow fail links until we find a matching transition or root
            while state != 0:
                matched = None
                for key, ns in goto[state].items():
                    if is_equal(key, val):
                        matched = ns
                        break
                if matched is not None:
                    state = matched
                    break
                state = fail[state]
            # check root itself
            matched_root = None
            for key, ns in goto[0].items():
                if is_equal(key, val):
                    matched_root = ns
                    break
            if matched_root is not None and state == 0:
                fail[s] = matched_root if matched_root != s else 0
            else:
                fail[s] = state

    return goto, output, fail


def _ac_next(goto, fail, output, state, val, is_equal):
    while state != 0:
        matched = None
        for key, ns in goto[state].items():
            if is_equal(key, val):
                matched = ns
                break
        if matched is not None:
            state = matched
            break
        state = fail[state]
    else:
        matched = None
        for key, ns in goto[0].items():
            if is_equal(key, val):
                matched = ns
                break
        if matched is not None:
            state = matched

    return state, output[state]


def _build_C_row(text_col_slice, p_height, goto, fail, output,
                 is_equal, t_width):
    """
    Run AC automaton down a single text column (height p_height cells)
    and return the matched column-ID (-1 = no match).
    """
    state = 0
    for r in range(p_height):
        state, match = _ac_next(goto, fail, output, state,
                                 text_col_slice[r], is_equal)
    return match   # ID of matched pattern column, or -1


def _compute_lps_ids(pattern_ids, is_equal):
    m = len(pattern_ids)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if is_equal(pattern_ids[i], pattern_ids[length]):
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


def _get_bad_char_ids(pattern_ids, is_equal):
    table = {}
    for i, val in enumerate(pattern_ids):
        # mark last occurrence of each ID
        found = False
        for k in table:
            if is_equal(k, val):
                table[k] = i
                found = True
                break
        if not found:
            table[val] = i
    return table



def bird_kmp(text: np.array, pattern: np.array):
    is_equal = Counter(lambda x, y: x == y)

    t_height, t_width = text.shape
    p_height, p_width = pattern.shape

    if p_height > t_height or p_width > t_width:
        return is_equal.count, None

    pat_col_ids, unique_cols = _build_column_ids(pattern, is_equal)
    goto, output, fail = _build_ac_goto(unique_cols, p_height, is_equal)

    lps = _compute_lps_ids(pat_col_ids, is_equal)

    for i in range(t_height - p_height + 1):

        c_row = []
        for j in range(t_width):
            col_slice = text[i:i + p_height, j]
            c_row.append(_build_C_row(col_slice, p_height,
                                       goto, fail, output, is_equal, t_width))

        j = 0   # index into c_row
        k = 0   # index into pat_col_ids
        while j < t_width:
            if is_equal(c_row[j], pat_col_ids[k]):
                j += 1
                k += 1
                if k == p_width:
                    return is_equal.count, (i, j - k)
            else:
                if k != 0:
                    k = lps[k - 1]
                else:
                    j += 1

    return is_equal.count, None


def bird_bm(text: np.array, pattern: np.array):
    """
    Bird (1977) 2-D pattern matching using:
      - Aho-Corasick      to identify pattern columns in each text column
      - Boyer-Moore (bad char) to search the resulting C-matrix rows
    Returns (comparison_count, (row, col)) or (comparison_count, None).
    """
    is_equal = Counter(lambda x, y: x == y)

    t_height, t_width = text.shape
    p_height, p_width = pattern.shape

    if p_height > t_height or p_width > t_width:
        return is_equal.count, None

    pat_col_ids, unique_cols = _build_column_ids(pattern, is_equal)
    goto, output, fail = _build_ac_goto(unique_cols, p_height, is_equal)

    bad_char = _get_bad_char_ids(pat_col_ids, is_equal)

    for i in range(t_height - p_height + 1):

        # Build one C-row
        c_row = []
        for j in range(t_width):
            col_slice = text[i:i + p_height, j]
            c_row.append(_build_C_row(col_slice, p_height,
                                       goto, fail, output, is_equal, t_width))

        # BM search for pat_col_ids in c_row (right-to-left, bad-char only)
        s = 0
        while s <= t_width - p_width:
            j = p_width - 1

            while j >= 0 and is_equal(c_row[s + j], pat_col_ids[j]):
                j -= 1

            if j < 0:
                return is_equal.count, (i, s)

            # bad-character shift using column IDs
            bad_val = c_row[s + j]
            last_occ = -1
            for k in bad_char:
                if is_equal(k, bad_val):
                    last_occ = bad_char[k]
                    break
            s += max(1, j - last_occ)

    return is_equal.count, None