#python3
__author__ = 'Ian'

import sys


node_count = -1

def increase_node_count():
    global node_count
    node_count += 1


def reset_node_count():
    global node_count
    node_count = 0


class SuffixNode():
    def __init__(self):
        self.children = {}
        self.parent = None
        self.string_depth = 0
        self.edge_start = 0
        self.edge_end = 0
        self.is_leaf = True
        increase_node_count()
        self.id = node_count

    def create_new_leaf(self, text, suffix):
        leaf = SuffixNode()
        leaf.parent = self
        leaf.string_depth = len(text) - suffix
        leaf.edge_start = suffix + self.string_depth
        leaf.edge_end = len(text) - 1
        self.children[text[leaf.edge_start]] = leaf
        return leaf

    def break_edge(self, text, start, offset):
        start_char = text[start]
        mid_char = text[start + offset]
        mid_node = SuffixNode()
        mid_node.parent = self
        mid_node.string_depth = self.string_depth + offset
        mid_node.edge_start = start
        mid_node.edge_end = start + offset - 1
        mid_node.children[mid_char] = self.children[start_char]
        mid_node.is_leaf = False
        self.children[start_char].parent = mid_node
        self.children[start_char].edge_start = start + offset
        self.children[start_char] = mid_node
        self.is_leaf = False
        return mid_node


def build_result(nodes, edges, node=0, depth=0):
    if node:
        yield '%d %d' % nodes[node]

    for edge in edges[node]:
        yield from build_result(nodes, edges, node=edge, depth=depth + 1)


def suffix_tree_from_suffix_array(text, suffix_array, lcp_array):
    root = SuffixNode()
    root.edge_end = -1
    root.edge_start = -1
    lcp_prev = 0
    cur_node = root
    text_length = len(text)
    for i in range(text_length):
        suffix = suffix_array[i]
        while cur_node.string_depth > lcp_prev:
            cur_node = cur_node.parent
        if cur_node.string_depth == lcp_prev:
            cur_node = cur_node.create_new_leaf(text, suffix)
        else:
            edge_start = suffix_array[i - 1] + cur_node.string_depth
            offset = lcp_prev - cur_node.string_depth
            mid_node = cur_node.break_edge(text, edge_start, offset)
            cur_node = mid_node.create_new_leaf(text, suffix)
        if i < text_length - 1:
            lcp_prev = lcp_array[i]
    reset_node_count()
    return root


def debug():
    text = "AAA$"
    sa = build_suffix_array(text)
    lcp = compute_lcp_array_kasai(text, sa)
    root = suffix_tree_from_suffix_array(text, sa, lcp)
    print(root)
    stack = [(root, 0)]
    result_edges = []
    while len(stack) > 0:
        (node, edge_index) = stack[-1]
        stack.pop()
        if node.is_leaf:
            continue
        edges = node.children
        edge_keys = sorted(edges.keys())
        if edge_index + 1 < len(edges):
            stack.append((node, edge_index + 1))
        print(
            '%d %d' % (edges[edge_keys[edge_index]].edge_start, edges[edge_keys[edge_index]].edge_end + 1))
        stack.append((edges[edge_keys[edge_index]], 0))


class TransformPatternMatcher():
    def __init__(self, transform):
        self.transform = transform
        self.alphabet = sorted(set(self.transform))
        self.total_count_array = self.build_total_count_array()
        self.ooc_array = self.build_occ_array()

    def count_occurrence(self, pattern):
        c = pattern[-1]
        i = len(pattern) - 1
        tca = self.total_count_array
        ooc_array = self.ooc_array
        sp = tca[1][tca[0].index(c)] + 1
        try:
            ep = tca[1][tca[0].index(c) + 1]
        except:
            ep = len(self.transform)
        while sp <= ep and i >= 1:
            c = pattern[i - 1]
            sp = tca[1][tca[0].index(c)] + occ_value_retriever(c, sp - 1, ooc_array) + 1
            ep = tca[1][tca[0].index(c)] + occ_value_retriever(c, ep, ooc_array)
            i -= 1
        if ep < sp:
            return 0
        else:
            return ep - sp + 1

    def find_start_and_end_positions(self, pattern):
        c = pattern[-1]
        i = len(pattern) - 1
        tca = self.total_count_array
        ooc_array = self.ooc_array
        sp = tca[1][tca[0].index(c)] + 1
        try:
            ep = tca[1][tca[0].index(c) + 1]
        except:
            ep = len(self.transform)
        while sp <= ep and i >= 1:
            c = pattern[i - 1]
            sp = tca[1][tca[0].index(c)] + occ_value_retriever(c, sp - 1, ooc_array) + 1
            ep = tca[1][tca[0].index(c)] + occ_value_retriever(c, ep, ooc_array)
            i -= 1
        if ep < sp:
            return 0
        else:
            return sp, ep

    def build_total_count_array(self):
        array = [sorted(self.alphabet)]
        a2 = {}
        for letter in self.alphabet:
            a2[letter] = 0
        for character in self.transform:
            for letter in self.alphabet:
                if character < letter:
                    a2[letter] += 1
        array.append([value for key, value in sorted(a2.items())])
        return array

    def build_occ_array(self):
        array = [sorted(self.alphabet), [0] * len(self.alphabet)]
        row_occ = {}
        for letter in self.alphabet:
            row_occ[letter] = 0
        for letter in self.transform:
            row_occ[letter] += 1
            array.append([value for key, value in sorted(row_occ.items())])
        return array


def occ_value_retriever(letter, position, c_array):
    column = c_array[0].index(letter)
    return c_array[position + 1][column]


def compute_prefix_function(text):
    s = [0]
    border = 0
    count = 0
    for i in range(1, len(text)):
        while border > 0 and text[i] != text[border]:
            border = s[border - 1]
        if text[i] == text[border]:
            border += 1
        else:
            border = 0
        s.append(border)
    return s


def find_pattern_count(pattern, text):
    s = pattern + "$" + text
    pf = compute_prefix_function(s)
    result = []
    pattern_length = len(pattern)
    for i in range(pattern_length, len(pf)):
        if pf[i] == pattern_length:
            result.append(i - 2 * pattern_length)
    return result


def find_all_occurrences(pattern, text):
    s = pattern + "$" + text
    pf = compute_prefix_function(s)
    result = []
    for i in range(len(pattern), len(pf)):
        if pf[i] == len(pattern):
            result.append(i - 2 * len(pattern))
    return result


def sort_characters(text):
    text_length = len(text)
    order = [0] * text_length
    alphabet = sorted(set(text))
    count = {}
    for letter in alphabet:
        count[letter] = 0
    for letter in text:
        count[letter] += 1
    for letter in alphabet[1:]:
        previous_letter_index = alphabet.index(letter) - 1
        previous_letter = alphabet[previous_letter_index]
        count[letter] = count[letter] + count[previous_letter]
    for i in range(text_length - 1, -1, -1):
        c = text[i]
        count[c] -= 1
        order[count[c]] = i
    return order


def compute_char_classes(text, order):
    equivalence_class = [0] * len(text)
    smallest_character = order[0]
    equivalence_class[smallest_character] = 0
    text_length = len(text)
    for i in range(1, text_length):
        string_in_order = text[order[i]]
        previous_string_in_order = text[order[i - 1]]
        if string_in_order != previous_string_in_order:
            equivalence_class[order[i]] = equivalence_class[order[i - 1]] + 1
        else:
            equivalence_class[order[i]] = equivalence_class[order[i - 1]]
    return equivalence_class


def sort_doubled(text, cyclic_shift_length, order, equivalence_class):
    text_length = len(text)
    new_order = [0] * text_length
    count = [0] * text_length
    for i in range(text_length):
        count[equivalence_class[i]] += 1
    for j in range(1, text_length):
        count[j] += count[j - 1]
    for i in range(text_length - 1, -1, -1):
        start = (order[i] - cyclic_shift_length + text_length) % text_length
        cl = equivalence_class[start]
        count[cl] -= 1
        new_order[count[cl]] = start
    return new_order


def updateClasses(new_order, equivalence_class, l):
    n = len(new_order)
    new_class = [0] * n
    new_class[new_order[0]] = 0
    for i in range(1, n):
        cur = new_order[i]
        prev = new_order[i - 1]
        mid = (cur + l) % n
        midPrev = (prev + l) % n
        if equivalence_class[cur] != equivalence_class[prev] or \
                        equivalence_class[mid] != equivalence_class[midPrev]:
            new_class[cur] = new_class[prev] + 1
        else:
            new_class[cur] = new_class[prev]
    return new_class


def build_suffix_array(s):
    string_length = len(s)
    order = sort_characters(s)
    equivalence_class = compute_char_classes(s, order)
    length = 1
    while length < string_length:
        order = sort_doubled(s, length, order, equivalence_class)
        equivalence_class = updateClasses(order, equivalence_class, length)
        length *= 2
    return order


def lcp_of_suffixes(string, i, j, equal):
    lcp = equal
    while i + lcp < len(string) and j + lcp < len(string):
        if string[i + lcp] == string[j + lcp]:
            lcp += 1
        else:
            break
    return lcp


def invert_suffix_array(suffix_array):
    pos = [0] * len(suffix_array)
    for i in range(len(pos)):
        pos[suffix_array[i]] = i
    return pos


def compute_lcp_array_coursera(string, order):
    lcp_array = [0] * (len(string) - 1)
    lcp = 0
    pos_in_order = invert_suffix_array(order)
    suffix = order[0]
    for i in range(len(string)):
        order_index = pos_in_order[suffix]
        if order_index == len(string) - 1:
            lcp = 0
            suffix = (suffix + 1) % len(string)
            continue
        next_suffix = order[order_index + 1]
        if lcp > 0:
            lcp -= 1
        lcp = lcp_of_suffixes(string, suffix, next_suffix, lcp)
        lcp_array[order_index] = lcp
        suffix = (suffix + 1) % len(string)
    return lcp_array


def compute_lcp_array_slow(string, order):
    lcp_array = []
    for i in range(len(string) - 1):
        lcp = 0
        suffix_1 = string[order[i]:]
        suffix_2 = string[order[i + 1]:]
        for j in range(len(suffix_2)):
            if suffix_2[j] == suffix_1[j]:
                lcp += 1
            else:
                break
        lcp_array.append(lcp)
    return lcp_array


def compute_lcp_array_kasai(string, suffix_array):
    lcp_array = [0] * (len(string) - 1)
    lcp = 0
    pos_in_order = invert_suffix_array(suffix_array)
    for i in range(len(string)):
        order_index = pos_in_order[i]
        if order_index == 0:
            lcp_array[order_index] = 0
        else:
            j = suffix_array[order_index - 1]
            while i + lcp < len(string) and j + lcp < len(string) and string[i + lcp] == string[j + lcp]:
                lcp += 1
            lcp_array[order_index - 1] = lcp
        if lcp > 0:
            lcp -= 1
    return lcp_array


def pattern_matching_with_suffix_array_coursera(text, pattern, sa):
    min_index = 0
    max_index = len(text)
    lp = len(pattern)
    lt = len(text)
    while min_index < max_index:
        mid_index = int((min_index + max_index) / 2)
        if pattern > text[sa[mid_index]:]:
            min_index += 1
        else:
            max_index = mid_index
    start = min_index
    max_index = lt
    while min_index < max_index:
        mid_index = int((min_index + max_index) / 2)
        if pattern < text[sa[mid_index]:]:
            max_index = mid_index
        else:
            min_index += 1
    end = max_index
    if start > end:
        print("Pattern does not appear in text")
    else:
        return start


def match_all_patterns_in_text(text, patterns):
    sa = build_suffix_array(text)
    starting_positions = [pattern_matching_with_suffix_array_coursera(text, pattern, sa) for pattern in patterns]
    print(starting_positions)


def bwt_from_suffix_array(string, sa):
    len_text = len(string)
    bwt = "".join([string[(sa[i] + len_text - 1) % len_text] for i in range(len_text)])
    return bwt


def match_all_patterns(text, patterns):
    sa = build_suffix_array(text)
    bwt = bwt_from_suffix_array(text, sa)
    pattern_finder = TransformPatternMatcher(bwt)
    pattern_starts = [match_pattern_fast_bwt(pattern, sa, pattern_finder) for pattern in patterns]
    deduped_lists = list(set([item for sublist in pattern_starts if sublist is not None for item in sublist]))
    return deduped_lists


def find_patterns_in_text(text, patterns):
    sa = build_suffix_array(text)
    bwt = bwt_from_suffix_array(text, sa)
    pattern_finder = TransformPatternMatcher(bwt)
    pattern_starts = [match_pattern_fast_bwt(pattern, sa, pattern_finder) for pattern in patterns]
    deduped_lists = list(set([item for sublist in pattern_starts if sublist is not None for item in sublist]))
    return deduped_lists


def match_pattern_fast_bwt(pattern, sa, pattern_counter):
    try:
        start_and_end_positions = pattern_counter.find_start_and_end_positions(pattern)
        if start_and_end_positions != 0:
            start = start_and_end_positions[0]
            end = start_and_end_positions[1]
            text_index = []
            while start <= end:
                text_index.append(sa[start - 1])
                start += 1
            return text_index
    except ValueError:
        pass


def list_substrings(text):
    text += "$"
    text_sa = build_suffix_array(text)
    text_lcp = compute_lcp_array_kasai(text, text_sa)
    prefixes = []
    for index, lcp in enumerate(text_lcp):
        second_suffix = text[text_sa[index + 1]:]
        for i in range(lcp + 1, len(second_suffix)):
            prefixes.append(text[text_sa[index + 1]:text_sa[index + 1] + i])
    return prefixes

def hacker_rank(strings):
    list_of_lists = [list_substrings(text) for text in strings]
    sorted_set = [item for sublist in list_of_lists  for item in sublist]
    result = sorted(set(sorted_set))
    return result

