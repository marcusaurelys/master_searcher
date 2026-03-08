import numpy as np
from collections import deque
from algos.counter import Counter


def _build_column_ids(pattern: np.array, is_equal):
    p_height, p_width = pattern.shape

    col_map = {}
    unique_cols = []
    ids = []

    for j in range(p_width):
        col_tuple = tuple(pattern[:, j])

        if col_tuple not in col_map:
            col_map[col_tuple] = len(unique_cols)
            unique_cols.append(col_tuple)

        ids.append(col_map[col_tuple])

    return ids, unique_cols


def _build_ac_goto(unique_cols, p_height):
    goto = [{}]
    output = {0: -1}
    fail = [0]

    for col_id, col in enumerate(unique_cols):

        state = 0

        for r in range(p_height):
            val = col[r]

            if val not in goto[state]:

                next_state = len(goto)

                goto.append({})
                output[next_state] = -1
                fail.append(0)

                goto[state][val] = next_state

            state = goto[state][val]

        output[state] = col_id

    queue = deque()

    for val, s in goto[0].items():
        fail[s] = 0
        queue.append(s)

    while queue:

        r = queue.popleft()

        for val, s in goto[r].items():

            queue.append(s)

            f = fail[r]

            while f != 0 and val not in goto[f]:
                f = fail[f]

            fail[s] = goto[f].get(val, 0)

    return goto, output, fail


def _ac_next(goto, fail, output, state, val):

    while state != 0 and val not in goto[state]:
        state = fail[state]

    state = goto[state].get(val, 0)

    return state, output[state]


def _build_C_row(C, i):
    return C[i]

def _build_C_matrix(text, p_height, goto, fail, output):
    t_height, t_width = text.shape

    C = [[-1] * t_width for _ in range(t_height)]

    for j in range(t_width):
        state = 0

        for i in range(t_height):

            val = text[i, j]

            while state != 0 and val not in goto[state]:
                state = fail[state]

            state = goto[state].get(val, 0)

            match = output[state]

            if match != -1:
                row = i - p_height + 1
                if row >= 0:
                    C[row][j] = match

    return C

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


def _get_bad_char_ids(pattern_ids):

    table = {}

    for i, val in enumerate(pattern_ids):
        table[val] = i

    return table


def bird_kmp(text: np.array, pattern: np.array):

    is_equal = Counter(lambda x, y: x == y)

    t_height, t_width = text.shape
    p_height, p_width = pattern.shape

    if p_height > t_height or p_width > t_width:
        return is_equal.count, None

    pat_col_ids, unique_cols = _build_column_ids(pattern, is_equal)

    goto, output, fail = _build_ac_goto(unique_cols, p_height)

    lps = _compute_lps_ids(pat_col_ids, is_equal)

    C = _build_C_matrix(text, p_height, goto, fail, output)

    for i in range(t_height - p_height + 1):

        c_row = _build_C_row(C, i)

        j = 0
        k = 0

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

    is_equal = Counter(lambda x, y: x == y)

    t_height, t_width = text.shape
    p_height, p_width = pattern.shape

    if p_height > t_height or p_width > t_width:
        return is_equal.count, None

    pat_col_ids, unique_cols = _build_column_ids(pattern, is_equal)
    goto, output, fail = _build_ac_goto(unique_cols, p_height)
    bad_char = _get_bad_char_ids(pat_col_ids)
    C = _build_C_matrix(text, p_height, goto, fail, output)


    for i in range(t_height - p_height + 1):

        c_row = _build_C_row(C, i)

        s = 0

        while s <= t_width - p_width:

            j = p_width - 1

            while j >= 0 and is_equal(c_row[s + j], pat_col_ids[j]):
                j -= 1

            if j < 0:

                return is_equal.count, (i, s)

            bad_val = c_row[s + j]

            last_occ = bad_char.get(bad_val, -1)

            s += max(1, j - last_occ)



    return is_equal.count, None