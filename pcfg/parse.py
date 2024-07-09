import heapq
import time

from .helpers.helpers import nested_tuple_to_str, tree_from_str, get_signature

def unary_closure(rules, queue):
    """Function that finds unary rules for each cell
    Parameters:
        rules: dictionary of rules in the form (left side of rule, (right side of rule)) -> weight
        queue: priority queue containing tuples of (negative) weights and non-terminals
    """
    weights = {}
    result = {}
    backtraces = {}
    
    if queue:
        for c in queue:
            weights[c[1]] = 0.

        while len(queue) > 0:
            current = heapq.heappop(queue)
            current_weight = -current[0]
            current_nt = current[1]
            if not current_nt in weights:
                weights[current_nt] = 0
            if weights[current_nt] <= current_weight:
                weights[current_nt] = current_weight

                for left, rights in rules.items():
                    for right in rights:
                        right_rl = [right[0]] if isinstance(right[0], int) else right[0]
                        if len(right_rl) == 1 and current_nt == right_rl[0]:
                            w = right[1] * current_weight
                            if left not in weights or w > weights[left]:
                                heapq.heappush(queue, (-w, left))
                                weights[left] = w
                                result[left] = w
                                backtraces[left] = right_rl[0]

    return result, backtraces


def prune_threshold_beam(tbl, i, j, nonterminals, theta):
    """Implement pruning with threshold beam
    Parameters:
        tbl: dictionary of the form (i, j, non-terminal) -> weight
        i, j: current indices
        nonterminals: list of nonterminals at current cell
        theta: threshold for pruning
    returns:
        pruned dictionary of the form (i, j, non-terminal) -> weight
    """
    m = max(tbl[(i,j,a)] for a in nonterminals)
    
    thresh = theta*m
    for A in nonterminals:
        if tbl[(i,j,A)] < thresh:
            tbl[(i,j,A)] = 0
    return tbl


def prune_fixed_size_beam(tbl, i, j, nonterminals, n):
    """Implement pruning with fixed beam
    Parameters:
        tbl: dictionary of the form (i, j, non-terminal) -> weight
        i, j: current indices
        nonterminals: list of nonterminals at current cell
        n: number of best entries that will be kept
    returns:
        pruned dictionary of the form (i, j, non-terminal) -> weight
    """
    current = [tbl[(i,j,a)] for a in nonterminals]
    if len(current) <= n:
        return tbl

    current.sort(reverse=True)
    thresh = current[n-1]
    for A in nonterminals:
        if tbl[(i,j,A)] < thresh:
            tbl[(i,j,A)] = 0
    return tbl


def cyk_parse(sentence, id_dict, lex_rules, R, R_binary, initial="ROOT", unking=False, threshold_beam=0, rank_beam=0, smoothing=False):
    """Function that implements the cyk-parse algorithm
    Parameters:
        sentence: str
        id_dict: dictionary that maps words to indices
        lex_rules: dictionary of lexicon rules of the form (non-terminal, word index) -> weight
        R: dictionary of grammar rules in the form (left side of rule, (right side of rule)) -> weight
        initial: str that represents root of tree
        unking: bool, apply basic unking
        smoothing: bool, apply smoothing
    returns:
        tbl: dictionary of the form (i, j, non-terminal) -> weight
        root_id: tuple of indices that contain the root
        backtraces: dictionary containing backtraces of the form (i, j, non-terminal) -> [right side of rule, m]
    """
    words_orig = [w.strip() for w in sentence.split(' ')]
    words_orig = [w for w in words_orig if w != '']

    # basic unking
    words_unk = []
    unk_signatures = set()
    if unking or smoothing:
        words = []
        for word_index, word in enumerate(words_orig):
            if word in id_dict:
                words.append(word)
            else:
                words_unk.append(word)
                if smoothing:
                    signature = get_signature(word, word_index)
                    words.append(signature)
                    unk_signatures.add(signature)
                else:
                    words.append("UNK")
    else:
        words = words_orig

    n = len(words)
    found = False

    tbl = {}
    backtraces = {}
    # iterate over indices and get lexicon rules
    for i in range(1,n+1):
        if words[i-1] not in id_dict:
            return False, (), {}, [], set()
        word_int = id_dict[words[i-1]]
        nonterminals = set()
        for A, lex in lex_rules.items():
            A_lex = [elem for elem in lex if elem[0] == word_int]
            for wi, w in A_lex:
                if (i-1, i, A) in tbl:
                    if w > tbl[(i-1, i, A)]:
                        tbl[(i-1, i, A)] = w
                        backtraces[(i-1, i, A)] = [word_int]                        
                else:
                    tbl[(i-1, i, A)] = w
                    backtraces[(i-1, i, A)] = [word_int]
                    nonterminals.add(A)

        queue = [(-tbl[(i-1, i, a)], a) for a in nonterminals]
        heapq.heapify(queue)
        combined_d = R.copy()
        for k, v in lex_rules.items():
            lst  = combined_d.get(k, [])
            lst.extend(v)
            combined_d[k] = lst
        unary_weights, unary_backtraces = unary_closure(combined_d, queue)
        for nonterminal, weight in unary_weights.items():
            if weight > 0:
                nonterminals.add(nonterminal)
                tbl[(i-1, i, nonterminal)] = weight
                backtraces[(i-1, i, nonterminal)] = [unary_backtraces[nonterminal]]
        
        if threshold_beam > 0:
            if len(nonterminals) > 0:
                tbl = prune_threshold_beam(tbl, i-1, i, nonterminals, threshold_beam)
        if rank_beam > 0:
            if len(nonterminals) > 0:
                tbl = prune_fixed_size_beam(tbl, i-1, i, nonterminals, rank_beam)
    
    # width of span
    for r in range(2,n+1):
        # left limit
        for i in range(n+1-r):
            # right limit
            j = i+r
            nonterminals = set()
            queue_dict = {}
            # split of span
            for m in range(i+1, j):
                for (B,C), BC_lst in R_binary.items():
                    for A, rule_w in BC_lst:
                        if tbl.get((i,m,B), 0) > 0 and tbl.get((m,j,C), 0) > 0:
                            nonterminals.add(A)
                            w = rule_w * tbl[(i,m,B)] * tbl[(m,j,C)]
                            if w > tbl.get((i,j,A), 0): 
                                queue_dict[A] = w
                                tbl[(i,j,A)] = w
                                backtraces[(i,j,A)] = [B, C, m]
                
                                if A == initial and i == 0 and j == n:
                                    root_id = [i,j]
                                    found = True
                
            # add unary rules
            queue = [(-v, k) for k, v in queue_dict.items()]
            heapq.heapify(queue)
            unary_weights, unary_backtraces = unary_closure(R, queue)
            for nonterminal, weight in unary_weights.items():
                nonterminals.add(nonterminal)
                if weight > 0:
                    tbl[(i, j, nonterminal)] = weight
                    backtraces[(i,j,nonterminal)] = [unary_backtraces[nonterminal]]
                # check if the root was reached
                if nonterminal == initial and i == 0 and j == n:
                    root_id = [i,j]
                    found = True

            if threshold_beam > 0:
                if len(nonterminals) > 0:
                    tbl = prune_threshold_beam(tbl, i, j, nonterminals, threshold_beam)
            if rank_beam > 0:
                if len(nonterminals) > 0:
                    tbl = prune_fixed_size_beam(tbl, i, j, nonterminals, rank_beam)
    
    if found:
        return tbl, root_id, backtraces, words_unk, unk_signatures
    
    return False, (), {}, [], set()


def best_tree(backtraces, root, word_dict):
    """Get the best solution from the backtraces
    Parameters:
        backtraces: dictionary containing backtraces of the form (i, j, non-terminal) -> [right side of rule, m]
        root: str that marks the root of the tree
        word_dict: dictionary that maps indices to words
    """
    if isinstance(root[3], int):
        return (root[2], word_dict[root[3]])
    elif len(root) < 6:
        i, j, A, B = root[:4]
        next = tuple([i, j, B] + backtraces[(i, j, B)])
        return (A, best_tree(backtraces, next, word_dict))
    else:
        i, j, A, B, C, m = root
        left = tuple([i, m, B] + backtraces[(i, m, B)])
        right = tuple([m, j, C] + backtraces[(m, j, C)])
        return (A, best_tree(backtraces, left, word_dict), best_tree(backtraces, right, word_dict))


def get_lexicon(lexicon):
    """Get non-terminal rules from lexicon file
    Parameters:
        lexicon: path to lexicon file
    returns:
        lex_rules: dictionary of lexicon rules of the form non-terminal -> (word index, weight)
        id_dict: dictionary that maps words to indices
        word_dict: dictionary that maps indices to words
    """
    words = []
    lex_rules = {}
    id_dict = {}
    word_dict = {}
    i = 0
    with open(lexicon, 'r') as lex_file:
        for l in lex_file:
            l_splt = [elem.strip() for elem in l.split(' ')]
            words.append(l_splt[1])
            if l_splt[1] not in id_dict:
                id = i
                i += 1
            else:
                id = id_dict[l_splt[1]]
            
            id_dict[l_splt[1]] = id
            word_dict[id] = l_splt[1]
            lex_rls_lst = lex_rules.get(l_splt[0], [])
            lex_rls_lst.append((id, float(l_splt[2])))
            lex_rules[l_splt[0]] = lex_rls_lst
    
    return lex_rules, id_dict, word_dict


def get_rules(rules):
    """Get rules from grammar file
    Parameters:
        rules: path to grammar file
        N: list of non-terminals
    returns:
        rls: dictionary of left side of rule -> [(right side of rule, weight)]
        rls_bi: dictionary of binary rules with right side of rule -> [(left side of rule, weight)]
        N: completed set of non-terminals
    """
    rls = {}
    rls_bi = {}
    with open(rules, 'r') as rls_file:
        for r in rls_file:
            left, right = r.split(' -> ')
            left = left.strip()
            right = [elem for elem in right.split(' ') if elem != '']
            if len(right) > 3 or len(right) < 2:
                raise Exception("The grammar is not in binarized PCFG format!")
            right_rule = right[0:-1]
            right_tpl = tuple(right_rule)
            w = float(right[-1].strip())
            rls_lst = rls.get(left, [])
            rls_lst.append((right_tpl, w))
            rls[left] = rls_lst
            if len(right_tpl) == 2:
                rls_bi_lst = rls_bi.get(right_tpl, [])
                rls_bi_lst.append((left, w))
                rls_bi[right_tpl] = rls_bi_lst
    
    return rls, rls_bi


def run_cyk_parse(rules, lexicon, sentences, initial="ROOT", unking=False, threshold_beam=0, rank_beam=0, smoothing=False):
    """Run the cyk parse algorithm
    Parameters:
        rules: path to file containing grammar rules
        lexicon: path to file containing lexicon
        sentences: list of strings
        initial(str): root symbol of the parse tree
        unking: bool, apply basic unking
    """
    lex_rules, id_dict, word_dict = get_lexicon(lexicon)
    rls, bi_rls = get_rules(rules)

    for sentence in sentences:
        sentence = sentence.strip()
        result, root_id, backtraces, words_unk, unk_signatures = cyk_parse(sentence, id_dict, lex_rules, rls, bi_rls, initial, unking, threshold_beam, rank_beam, smoothing)
        
        if result:
            root_bt = backtraces[tuple(root_id + [initial])]
            root = tuple(root_id + [initial] + root_bt)
            bt = best_tree(backtraces, root, word_dict)
            tree_str = nested_tuple_to_str(bt)
            
            if unking or smoothing:
                # get original words back
                if smoothing:
                    tree = tree_from_str(tree_str, get_terminal_list=False, unking=True, unk_list=words_unk, unk_signatures=unk_signatures)
                else:
                    tree = tree_from_str(tree_str, get_terminal_list=False, unking=True, unk_list=words_unk, unk_signatures=["UNK"])
                tree_str = nested_tuple_to_str(tree)
            
            print(tree_str)
        
        else:
            print('(NOPARSE {})'.format(sentence))


if __name__ == "__main__":
    # sentence = "Pierre Vinken , 61 years old , will join the board as a nonexecutive director Nov. 29 ."
    # run_cyk_parse("./material/small/grammar.rules", "./material/small/grammar.lexicon", [sentence], initial="ROOT")

    # sentence = "The new real estate unit would have a separate capital structure to comply with the law ."
    # run_cyk_parse("./material/large/grammar.rules", "./material/large/grammar.lexicon", [sentence], initial="ROOT")

    # sentence = "a a"
    # run_cyk_parse("tests/data/test.rules", "tests/data/test.lexicon", [sentence])

    # sentences = ["He is a brilliant deipnosophist ."]
    # rules = "test.rules"
    # lexicon = "test.lexicon"

    rules = "material/small/grammar.rules"
    lexicon = "material/small/grammar.lexicon"
    sentences_file = "material/small/sentences"

    # sentences = ["The decision was announced after trading ended ."]

    sentences = []
    with open(sentences_file, "r") as sf:
        for line in sf:
            sentences.append(line)
    
    tb = 0.01

    start_time = time.time()
    run_cyk_parse(rules, lexicon, sentences, unking=False, threshold_beam=tb, rank_beam=15)
    
    # run_cyk_parse("./tests/data/test.rules", "./tests/data/test.lexicon", sentences, threshold_beam=0.2)
    
    print("--- %s seconds ---" % (time.time() - start_time))