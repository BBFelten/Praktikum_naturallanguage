from .structs import *

def float_to_str(flt):
    if int(flt) == flt:
        return str(int(flt))
    return str(flt)

def get_rules(lst, grammar):
    n = lst[0]
    ts = []
    for elem in lst[1:]:
        if isinstance(elem, str):
            ts = elem
        else:
            ts.append(elem[0])
            grammar = get_rules(elem, grammar)
    
    grammar.insert_rule(Rule(n, ts))

    return grammar

def induce_grammar(corpus, grammar=None):
    grammar_obj = Grammar()
    
    for line in corpus:
        l = line.rstrip()
        stack = []
        current = []
        w = ''

        for char in l:
            if char not in [')', '(']:
                w += char
            elif char == '(':
                if w not in ['', ' ']:
                    w = w.strip()
                    split = w.split(' ')
                    if len(w.split(' ')) == 1:
                        current.append(w)
                    else:
                        current.append(split[0])
                        current.append(split[1])
                    w = ''
                stack.append(current)
                current = []
            elif char == ')':
                if w not in ['', ' ']:
                    w = w.strip()
                    split = w.split(' ')
                    if len(w.split(' ')) == 1:
                        current.append(w)
                    else:
                        current.append(split[0])
                        current.append(split[1])
                    w = ''
                last = stack.pop()
                last.append(current)
                current = last
        
        result = current[0]
        # print(result)
        
        grammar_obj = get_rules(result, grammar_obj)
    
    grammar_obj = grammar_obj.normalize()

    lexicon = []
    # Output: grammar rules
    if grammar:
        with open('{}.rules'.format(grammar), 'w') as rules:
            for r, w in grammar_obj.rules.items():
                if r.lexical:
                    lexicon.append((r, w))
                else:
                    rules.write(r.n+' -> '+' '.join(r.t)+' '+float_to_str(w)+'\n')
    else:
        for r, w in grammar_obj.rules.items():
            if r.lexical:
                lexicon.append((r, w))
            else:
                print(r.n+' -> '+' '.join(r.t)+' '+float_to_str(w))
    
    # Output: grammar lexicon
    if grammar:
        with open('{}.lexicon'.format(grammar), 'w') as lex:
            for r, w in lexicon:
                lex.write(' '.join([r.n, r.t, float_to_str(w)])+'\n')
    else:
        for r, w in lexicon:
            print(' '.join([r.n, r.t, str(w)]))
    
    # Output: grammar words
    words = set(r.t for r,_ in lexicon)
    if grammar:
        with open('{}.words'.format(grammar), 'w') as wrds:
            for word in words:
                wrds.write(word+'\n')
    else:
        for word in words:
            print(word)