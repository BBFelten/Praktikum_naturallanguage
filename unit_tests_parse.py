import unittest
from pcfg.parse import *

grammar_rules = {('S', ('NP', 'VP')): 1., 
            ('VP', ('V', 'NP')): 0.5, 
            ('VP', ('V', 'VP1')): 0.5, 
            ('VP1', ('NP', 'PP')): 1.,
            ('PP', ('P', 'NP')): 1.,
            ('NP', ('Det', 'N')): 0.8,
            ('NP', ('NP1', 'PP')): 0.2,
            ('NP1', ('Det', 'N')): 1.}

lex_left_test = ['Det', 'Det', 'N', 'N', 'V', 'P']
lex_wgts_test = [0.6, 0.4, 0.5, 0.5, 1., 1.]


class TestParser(unittest.TestCase):
    def test_get_rules(self):
        lex_left, lex_wgts, N, id_dict, word_dict = get_lexicon('./unittest_files/grammar.lexicon')
        self.assertEqual(lex_left, lex_left_test)
        self.assertEqual(lex_wgts, lex_wgts_test)
        
        rls, N = get_rules('./unittest_files/grammar.rules', N)
        self.assertEqual(rls, grammar_rules)
    
    def test_cyk_parse(self):
        sentence = 'the cat chased the dog with the cat'
        result = run_cyk_parse('./unittest_files/grammar.rules', './unittest_files/grammar.lexicon', [sentence], 'S')
        print(result)


if __name__ == '__main__':
    unittest.main()
