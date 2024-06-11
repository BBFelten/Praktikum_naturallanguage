from .helpers.helpers import tree_from_str, nested_tuple_to_str

def debinarise(tree):
    """Debinarise and de-markovise trees
    Parameters:
        tree: str, binarised tree
    """
    right = tree[-1]
    if isinstance(tree, str):
        if "|" in tree:
            return tree.split("|")[0]
        if "^" in tree:
            return tree.split("^")[0]
        return tree
    
    elif isinstance(right, str):
        nt, t = tree
        if "|" in nt:
            return [nt.split("|")[0], t]
        if "^" in nt:
            return [nt.split("^")[0], t]
        return tree

    right_root = right[0]
    if "|" in right_root:
        return debinarise(tree[:-1] + right[1:])
    else:
        return [debinarise(elem) for elem in tree]


def run_debinarise(input):
    """Run debinarisation on a list of trees 
    Parameters:
        input: list of binarised trees (str)
    """
    for line in input:
        tree = tree_from_str(line)
        print(nested_tuple_to_str(debinarise(tree)))


if __name__ == "__main__":
    # test = ["(ROOT (S (S-TPC (NP-SBJ (NP (DT The) (NN percentage)) (NP-SBJ|<PP,PP-LOC> (PP (IN of) (NP (NN lung) (NP|<NN,NNS> (NN cancer) (NNS deaths)))) (PP-LOC (IN among) (S-NOM (NP-SBJ (NP (DT the) (NNS workers)) (PP (IN at) (NP (DT the) (NP|<NAC-LOC,NN,NN> (NAC-LOC (NNP West) (NAC-LOC|<NNP,,,NNP,,> (NNP Groton) (NAC-LOC|<,,NNP,,> (, ,) (NAC-LOC|<NNP,,> (NNP Mass.) (, ,))))) (NP|<NN,NN> (NN paper) (NN factory)))))) (VP (VBZ appears) (VP (TO to) (VP (VB be) (VP|<NP,PP-DIR> (NP (DT the) (JJS highest)) (PP-DIR (IN for) (NP (DT any) (NP|<NN,NNS> (NN asbestos) (NNS workers)))))))))))) (VP (VBN studied) (PP-LOC (IN in) (NP (JJ Western) (NP|<VBN,NNS> (VBN industrialized) (NNS countries)))))) (S|<,,NP-SBJ,VP,.> (, ,) (S|<NP-SBJ,VP,.> (NP-SBJ (PRP he)) (S|<VP,.> (VP (VBD said)) (. .))))))"]
    test = ["(ROOT (FRAG^<ROOT> ((RB Not) (FRAG|<NP-TMP,.>^<ROOT> (NP-TMP^<FRAG,ROOT> ((DT this) (NN year)) (. .))))))"]
    run_debinarise(test)