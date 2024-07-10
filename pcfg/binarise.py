from .helpers.helpers import tree_from_str, nested_tuple_to_str

def add_parents(node, ancestors):
    """Add parent nodes to node
    Parameters:
        node: current node
        ancestors: list of ancestors of length <= v
    Returns:
        node with ancestors
    """
    if len(ancestors) <= 1:
        return node

    return node + "^<{}>".format(",".join(ancestors[1:]))

def marcovise(tree, h, v, ancestors=[]):
    """Binarise and marcovise a tree recursively
    Parameters:
        tree: (list / tuple) non-binary tree
        h: int or None, number of horizontal left neighbors that are stored in nodes. If None, all neighbors are stored.
        v: int or None, number of ancestors that are stored in nodes. None: store all ancestors
        ancestors: current list of ancestor nodes
    Returns:
        binarised and marcovised tree
    """
    if isinstance(tree, str):
        return tree
    
    left = tree[0]
    right = tree[1:]
    
    new_ancestors = ancestors.copy()
    new_ancestors.append(left.split("|")[0])
    if v and len(new_ancestors) > v:
        new_ancestors = new_ancestors[-v:]
    
    if len(right) == 1:
        if isinstance(right[0], str):
            return tree
        return (add_parents(left, ancestors), marcovise(right[0], h, v, new_ancestors))
    
    if len(right) == 2:
        return (add_parents(left, ancestors), marcovise(right[0], h, v, new_ancestors), marcovise(right[1], h, v, new_ancestors))
    
    neighbors = [elem[0] for elem in right[1:]]
    if h:
        neighbors = neighbors[:h]
    new_node = tree[0].split("|")[0] + "|<{}>".format(",".join(neighbors))
    
    return (add_parents(left, ancestors), marcovise(right[0], h, v, new_ancestors), marcovise([new_node] + list(right[1:]), h, v, new_ancestors))


def run_marcovise(trees, horizontal, vertical):
    """Function to binarise and marcovise a list of trees
    Parameters:
        trees: list of strings representing trees
        horizontal: int or None, number of horizontal left neighbors that are stored in nodes. If None, all neighbors are stored.
        vertical: int or None, number of ancestors that are stored in nodes. None: store all ancestors
    """
    for tree_str in trees:
        tree = tree_from_str(tree_str)
        print(nested_tuple_to_str(marcovise(tree, horizontal, vertical)))


if __name__ == "__main__":
    run_marcovise(["(ROOT (S (NP-SBJ (PRP It)) (VP (VBZ has) (NP (NP (DT no) (NN bearing)) (PP-DIR (IN on) (NP (NP (PRP$ our) (NN work) (NN force)) (NP-TMP (NN today)))))) (. .)))"], 10, 3)