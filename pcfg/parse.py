import heapq

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
            weights[c[0]] = 0.

        while len(queue) > 0:
            current = heapq.heappop(queue)
            current_weight = -current[0]
            current_nt = current[1]
            if not current_nt in weights:
                weights[current_nt] = 0
            if weights[current_nt] <= current_weight:
                weights[current_nt] = current_weight

                for left, right in rules:
                    right = [right] if isinstance(right, int) else right
                    if len(right) == 1 and current_nt == right[0]:
                        w = rules[(left, right)] * current_weight
                        if left not in weights or w > weights[left]:
                            heapq.heappush(queue, (-w, left))
                            weights[left] = w
                            result[left] = w
                            backtraces[left] = right[0]

    return result, backtraces


def cyk_parse(sentence, id_dict, lex_rules, N, R, initial="ROOT"):
    """Function that implements the cyk-parse algorithm
    Parameters:
        sentence: str
        id_dict: dictionary that maps words to indices
        lex_rules: dictionary of lexicon rules of the form (non-terminal, word index) -> weight
        N: set of non-terminals
        R: dictionary of grammar rules in the form (left side of rule, (right side of rule)) -> weight
        initial: str that represents root of tree
    returns:
        tbl: dictionary of the form (i, j, non-terminal) -> weight
        root_id: tuple of indices that contain the root
        backtraces: dictionary containing backtraces of the form (i, j, non-terminal) -> [right side of rule, m]
    """
    words = [w.strip() for w in sentence.split(' ')]
    words = [w for w in words if w != '']
    n = len(words)
    found = False

    tbl = {}
    backtraces = {}
    # iterate over indices and get lexicon rules
    for i in range(1,n+1):
        word_int = id_dict[words[i-1]]
        nonterminals = set()
        for (A, wi) in lex_rules:
            if wi == word_int:
                w = lex_rules[(A, wi)]
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
        unary_weights, unary_backtraces = unary_closure({**R, **lex_rules}, queue)
        for nonterminal, weight in unary_weights.items():
            if weight > 0:
                tbl[(i-1, i, nonterminal)] = weight
                backtraces[(i-1, i, nonterminal)] = [unary_backtraces[nonterminal]]
    
    # width of span
    for r in range(2,n+1):
        queue_dict = {}
        # left limit
        for i in range(n+1-r):
            # right limit
            j = i+r
            # split of span
            for m in range(i+1, j):
                # add binary rules
                for A in N:
                    for rule in R:
                        if len(rule[1]) == 2 and A == rule[0]:
                            B, C = rule[1]
                            if (i,m,B) in tbl and (m,j,C) in tbl:
                                w = R[rule] * tbl[(i,m,B)] * tbl[(m,j,C)]
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
                    if weight > 0:
                        tbl[(i,j,nonterminal)] = weight
                        backtraces[(i,j,nonterminal)] = [unary_backtraces[nonterminal]]
                    # check if the root was reached
                    if nonterminal == initial and i == 0 and j == n:
                        root_id = [i,j]
                        found = True
    
    if found:
        return tbl, root_id, backtraces
    
    return False, (), {}


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
        lex_rules: dictionary of lexicon rules of the form (non-terminal, word index) -> weight
        N: Set of non-terminals
        id_dict: dictionary that maps words to indices
        word_dict: dictionary that maps indices to words
    """
    words = []
    lex_rules = {}
    id_dict = {}
    word_dict = {}
    N = set()
    with open(lexicon, 'r') as lex_file:
        for i,l in enumerate(lex_file):
            l_splt = [elem.strip() for elem in l.split(' ')]
            words.append(l_splt[1])
            if l_splt[1] not in id_dict:
                id = i
            else:
                id = id_dict[l_splt[1]]
            
            id_dict[l_splt[1]] = id
            word_dict[id] = l_splt[1]
            lex_rules[(l_splt[0], (id))] = float(l_splt[2])
            N.add(l_splt[0])
    
    return lex_rules, N, id_dict, word_dict


def get_rules(rules, N):
    """Get rules from grammar file
    Parameters:
        rules: path to grammar file
        N: list of non-terminals
    returns:
        rls: dictionary of (left side of rule, (right side of rule)) -> weight
        N: completed set of non-terminals
    """
    rls = {}
    with open(rules, 'r') as rls_file:
        for r in rls_file:
            left, right = r.split(' -> ')
            left = left.strip()
            right = [elem for elem in right.split(' ') if elem != '']
            if len(right) > 3 or len(right) < 2:
                raise Exception("The grammar is not in binarized PCFG format!")
            right_rule = right[0:-1]
            rls[(left, tuple(right_rule))] = float(right[-1].strip())
            N.add(left)
    
    return rls, N


def nested_tuple_to_str(t):
    """Helper function to turn a nested tuple to string without quotes and commas
    Parameters:
        t: tuple
    """
    if isinstance(t, tuple):
        return '(' + ' '.join(nested_tuple_to_str(item) for item in t) + ')'
    else:
        return str(t)


def run_cyk_parse(rules, lexicon, sentences, initial="ROOT"):
    """Run the cyk parse algorithm
    Parameters:
        rules: path to file containing grammar rules
        lexicon: path to file containing lexicon
        sentences: list of strings
        initial(str): root symbol of the parse tree
    """
    lex_rules, N, id_dict, word_dict = get_lexicon(lexicon)
    rls, N = get_rules(rules, N)

    for sentence in sentences:
        sentence = sentence.strip()
        result, root_id, backtraces = cyk_parse(sentence, id_dict, lex_rules, N, rls, initial)
        
        if result:
            root_bt = backtraces[tuple(root_id + [initial])]
            root = tuple(root_id + [initial] + root_bt)
            tree = best_tree(backtraces, root, word_dict)
            print(nested_tuple_to_str(tree))
        
        else:
            print('(NOPARSE {})'.format(sentence))


if __name__ == "__main__":
    sentence = "Pierre Vinken , 61 years old , will join the board as a nonexecutive director Nov. 29 ."
    run_cyk_parse("./material/small/grammar.rules", "./material/small/grammar.lexicon", [sentence], initial="ROOT")

    # sentence = "The new real estate unit would have a separate capital structure to comply with the law ."
    # run_cyk_parse("./material/large/grammar.rules", "./material/large/grammar.lexicon", [sentence], initial="ROOT")

    # sentences = ["a b", "a a b b b", "b a", "a a", "b" ]
    # run_cyk_parse("./tests/data/test.rules", "./tests/data/test.lexicon", sentences)

    # sentence = "a a b b b"
    # run_cyk_parse("tests/data/parsing-testcli.rules", "tests/data/parsing-testcli.lexicon", [sentence], "WURZEL")