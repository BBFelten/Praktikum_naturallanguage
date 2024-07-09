from .helpers.helpers import tree_from_str, nested_tuple_to_str

def basic_unking(corpus, threshold, smooth=False):
    wordcounts = {}
    lines = []
    for line in corpus:
        lines.append(line)
        _, terminal_list = tree_from_str(line, get_terminal_list=True)
        for terminal in terminal_list:
            count = 1 + wordcounts.get(terminal, 0)
            wordcounts[terminal] = count
        
    to_be_replaced = [k for k,v in wordcounts.items() if v <= threshold]

    modified_corpus = ""
    for line in lines:
        tree = tree_from_str(line, get_terminal_list=False, unking=True, unk_list=set(to_be_replaced), smoothing=smooth)
        tree_str = nested_tuple_to_str(tree)

        modified_corpus += tree_str + "\n"
        print(tree_str)
    
    modified_corpus = modified_corpus.strip()
    return modified_corpus

if __name__ == "__main__":
    basic_unking(["(ROOT (S (NP-SBJ (NP (NNP Pierre) (NNP Vinken)) (, ,) (ADJP (NP (CD 61) (NNS years)) (JJ old)) (, ,)) (VP (MD will) (VP (VB join) (NP (DT the) (NN board)) (PP-CLR (IN as) (NP (DT a) (JJ nonexecutive) (NN director))) (NP-TMP (NNP Nov.) (CD 29)))) (. .)))", "(ROOT (S (NP-SBJ (NNP Mr.) (NNP Vinken)) (VP (VBZ is) (NP-PRD (NP (NN chairman)) (PP (IN of) (NP (NP (NNP Elsevier) (NNP N.V.)) (, ,) (NP (DT the) (NNP Dutch) (VBG publishing) (NN group)))))) (. .)))"], 10, smooth=True)