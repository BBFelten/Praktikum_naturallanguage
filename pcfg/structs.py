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
        self.isnormalized = False
    
    def insert_rule(self, rule):
        # add rule to ruleset if it is not there, otherwise increase count
        for r, w in self.rules.items():
            if rule.n == r.n and rule.t == r.t:
                self.rules[r] += 1
                return 0

        self.rules[rule] = 1
        return 0

    def normalize(self):
        if not self.isnormalized: # will lead to errors if applied several times
            # First, get count of non-terminals on left side of rules
            nonterminals_counts = {}
            for r, w in self.rules.items():
                if r.n not in nonterminals_counts.keys():
                    nonterminals_counts[r.n] = w
                else:
                    nonterminals_counts[r.n] += w
            
            for r, w in self.rules.items():
                self.rules[r] = w/nonterminals_counts[r.n] # divide count of each rule by total count of non-terminal on left side
            
            self.normalized = True # calling method again should have no effect
        
        return self
