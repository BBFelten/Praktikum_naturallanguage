class SExp:
    def __init__(self, atom=None, sexpr=None):
        self.atom = atom
        self.sexpr = sexpr

class Tree:
    def __init__(self, root=None, children=[], level=0, index=0):
        self.root = root
        self.children = children

class Rule:
    def __init__(self, n=None, t=None):
        self.n = n
        self.t = t
        self.lexical = isinstance(t, str)

class Grammar:
    def __init__(self, n=None, t=None, w=0):
        self.initial = n
        if n:
            self.rules = {Rule(n, t), w}
        else:
            self.rules = {}
        self.nonterminals = None
        self.isnormalized = False
    
    def insert_rule(self, rule):
        for r, w in self.rules.items():
            if rule.n == r.n and rule.t == r.t:
                self.rules[r] += 1
                return 0

        self.rules[rule] = 1
        return 0
    
    def get_nonterminals(self):
        if not self.nonterminals:
            nonterminals = set([r.n for r, _ in self.rules.items()])
            self.nonterminals = nonterminals
        return self.nonterminals

    def normalize(self):
        if not self.isnormalized:
            nonterminals_counts = {}
            for r, w in self.rules.items():
                if r.n not in nonterminals_counts.keys():
                    nonterminals_counts[r.n] = w
                else:
                    nonterminals_counts[r.n] += w
            
            for r, w in self.rules.items():
                self.rules[r] = w/nonterminals_counts[r.n]
            
            self.normalized = True
        
        return self
