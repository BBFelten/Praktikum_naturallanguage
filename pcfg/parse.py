def unary_closure(rules, queue):
    weights = {}
    result = {}
    for c in queue:
        weights[c[0]] = 0.

    backtraces = {}
    while len(queue) > 0:
        current = max(queue, key=lambda x: x[1])
        queue.remove(current)
        if weights[current[0]] < current[1]:
            weights[current[0]] = current[1]

            for left, right in rules:
                if len(right) == 1 and current[0] == right[0]:
                    w = rules[(left, right)] * current[1]
                    queue.append((left, w))
                    weights[left] = w
                    result[left] = w
                    backtraces[left] = right[0]
            
    return result, backtraces


def cyk_parse(sentence, id_dict, lex_left, lex_wgts, N, R, initial="ROOT"):
    words = [w.strip() for w in sentence.split(' ')]
    words = [w for w in words if w != '']
    n = len(words)
    done = False

    tbl = {}
    backtraces = {}
    for i in range(1,n+1):
        word_int = id_dict[words[i-1]]
        A = lex_left[word_int]
        w = lex_wgts[word_int]
        tbl[(i-1, i, A)] = w
        backtraces[(i-1, i, A)] = [word_int]
        unary_weights, _ = unary_closure(R, [(A, w)])
        for nonterminal, weight in unary_weights.items():
            if weight > 0:
                tbl[(i-1, i, nonterminal)] = weight
                backtraces[(i-1, i, nonterminal)] = [word_int]

    for r in range(2,n):
        for i in range(n-r):
            j = i+r
            for m in range(i+1, j):
                queue = []
                for A in N:
                    for rule in R:
                        if len(rule[1]) == 2 and A == rule[0]:
                            B, C = rule[1]
                            if (i,m,B) in tbl and (m,j,C) in tbl:
                                w = R[rule] * tbl[(i,m,B)] * tbl[(m,j,C)]
                                if (i,j, A) in tbl:
                                    if w > tbl[(i,j,A)]: 
                                        queue.remove((A, tbl[(i,j,A)]))
                                        queue.append((A, w))
                                        tbl[(i,j,A)] = w
                                        backtraces[(i,j,A)] = [B, C, m]
                                        # if A == initial and j == n:
                                        if A == initial:
                                            root_id = [i,j]
                                            done = True
                                else:
                                    tbl[(i,j,A)] = w
                                    backtraces[(i,j,A)] = [B, C, m]
                                    queue.append((A, w))
                                    # if A == initial and j == n:
                                    if A == initial:
                                        root_id = [i,j]
                                        done = True

                    if done:
                        # print("FOUND!")
                        return tbl, root_id, backtraces
                
                unary_weights, unary_backtraces = unary_closure(R, queue)
                for nonterminal, weight in unary_weights.items():
                    if weight > 0:
                        tbl[(i,j,nonterminal)] = weight
                        backtraces[(i,j,nonterminal)] = [unary_backtraces[nonterminal]]
                    # if nonterminal == initial and j == n:
                    if nonterminal == initial:
                        root_id = [i,j]
                        done = True
    
    # print("NOT FOUND!")
    return False, (), {}


def best_tree(backtraces, root, word_dict):
    if isinstance(root[3], int):
        return (root[2], word_dict[root[3]])
    elif len(root) < 6:
        i, j, A, B = root[:4]
        next = tuple([i, j, B] + backtraces[(i, j, B)])
        return (A, B), best_tree(backtraces, next, word_dict)
    else:
        i, j, A, B, C, m = root
        left = tuple([i, m, B] + backtraces[(i, m, B)])
        right = tuple([m, j, C] + backtraces[(m, j, C)])
        return (A, B, C), best_tree(backtraces, left, word_dict), best_tree(backtraces, right, word_dict)


def get_lexicon(lexicon):
    words = []
    lex_left = []
    lex_wgts = []
    N = set()
    with open(lexicon, 'r') as lex_file:
        for l in lex_file:
            l_splt = [elem.strip() for elem in l.split(' ')]
            words.append(l_splt[1])
            lex_left.append(l_splt[0])
            lex_wgts.append(float(l_splt[2]))
            N.add(l_splt[0])
    
    id_dict = {}
    word_dict = {}
    for i, w in enumerate(words):
        id_dict[w] = i
        word_dict[i] = w
    
    return lex_left, lex_wgts, N, id_dict, word_dict


def get_rules(rules, N):
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


def run_cyk_parse(rules, lexicon, sentences, initial="ROOT"):
    lex_left, lex_wgts, N, id_dict, word_dict = get_lexicon(lexicon)
    rls, N = get_rules(rules, N)

    trees = []
    for sentence in sentences:
        sentence = sentence.strip()
        result, root_id, backtraces = cyk_parse(sentence, id_dict, lex_left, lex_wgts, N, rls, initial)
        
        if result:
            root_bt = backtraces[tuple(root_id + [initial])]
            root = tuple(root_id + [initial] + root_bt)
            tree = best_tree(backtraces, root, word_dict)
            # print(tree)
            trees.append(tree)
        
        else:
            trees.append(('NOPARSE ' + sentence))
    
    for t in trees:
        print(t)
    return trees


if __name__ == "__main__":
    # sentence = "The proposed holding company 's primary purpose would be to allow Great American to continue engaging in real estate development activities , it said ."
    sentence = "A Lorillard spokewoman said , `` This is an old story ."
    run_cyk_parse("./material/small/grammar.rules", "./material/small/grammar.lexicon", [sentence], initial="ROOT")