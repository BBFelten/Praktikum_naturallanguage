from .structs import *
from .helpers.helpers import tree_from_str

def float_to_str(flt):
    """Function to transform a float to a string
    If the float is an integer, it is saved without extra decimals (1. -> 1)
    """
    if int(flt) == flt:
        return str(int(flt))
    return str(flt)

def get_rules(lst, grammar):
    """Function to extract rules from a given nested list derived from PTB-format
    Parameters:
        lst: Nested list of strings derived from PTB string
        grammar: instance of class Grammar() which will save the rules
    Returns:
        Grammar with rules from lst added
    """
    n = lst[0] # non-terminal
    ts = []
    for elem in lst[1:]:
        if isinstance(elem, str): # terminal
            ts = elem
        else:
            ts.append(elem[0]) # first non-terminal, one level below
            grammar = get_rules(elem, grammar) # recursively get rules from nested list, one level below
    
    grammar.insert_rule(Rule(n, ts))

    return grammar

def induce_grammar(corpus, grammar=None):
    """Exercise 1
    Derive rules and non-terminals from corpus in PTB-format and return lexical and non-lexical rules and terminals
    Parameters:
        corpus: String containing one or more trees in PTB-format separated by newline
        grammar: String (optional) prefix for outputs
    """
    grammar_obj = Grammar() # create instance of class Grammar() to save rules
    
    for line in corpus:
        result = tree_from_str(line)
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
            print(' '.join([r.n, r.t, float_to_str(w)]))
    
    # Output: grammar words
    words = set(r.t for r,_ in lexicon)
    if grammar:
        with open('{}.words'.format(grammar), 'w') as wrds:
            for word in words:
                wrds.write(word+'\n')
    else:
        for word in words:
            print(word)