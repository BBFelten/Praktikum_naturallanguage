from .helpers.helpers import tree_from_str, nested_tuple_to_str

def add_parents(node, ancestors, lvl, v):
    """Add parent nodes to node
    Parameters:
        node: current node
        ancestors: list of ancestors of length <= v
    Returns:
        node with ancestors
    """
    if lvl == 0:
        return node
    
    ancestors_lst = []
    parent = node.split("|")[0]
    for i in range(v-1):
        if lvl-i > 0:
            parent = ancestors[(lvl-i, parent)].split("|")[0]
            ancestors_lst.append(parent)

    if len(ancestors_lst) < 1:
        return node

    return node + "^<{}>".format(",".join(ancestors_lst))

def build_backtraces(tree, lvl=1, ancestors={}):
    """Recursively build dictionary of ancestors from the original tree
    Parameters:
        tree: list of lists, input tree
        lvl: int, the current level in the tree counted from the top
        ancestors: dictionary of the form (lvl, node) -> node
    Returns:
        dictionary of the form (lvl, node) -> node
    """
    if isinstance(tree, str):
        return ancestors
    
    left = tree[0]
    right = tree[1:]

    if len(right) <= 2 and isinstance(right[-1], str):
        return ancestors

    for subtree in right:
        ancestors[(lvl, subtree[0])] = left
        ancestors = build_backtraces(subtree, lvl+1, ancestors)
    
    return ancestors


def marcovise(tree, h, v, ancestors, lvl=0):
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
    
    if len(right) == 1:
        if isinstance(right[0], str):
            return tree
        return (add_parents(left, ancestors, lvl, v), marcovise(right[0], h, v, ancestors, lvl+1))
    
    if len(right) == 2:
        return (add_parents(left, ancestors, lvl, v), marcovise(right[0], h, v, ancestors, lvl+1), marcovise(right[1], h, v, ancestors, lvl+1))
    
    neighbors = [elem[0] for elem in right[1:]]
    neighbors = neighbors[:h]
    new_node = left.split("|")[0] + "|<{}>".format(",".join(neighbors))
    
    return (add_parents(left, ancestors, lvl, v), marcovise(right[0], h, v, ancestors, lvl+1), marcovise([new_node] + list(right[1:]), h, v, ancestors, lvl))


def run_marcovise(trees, horizontal, vertical):
    """Function to binarise and marcovise a list of trees
    Parameters:
        trees: list of strings representing trees
        horizontal: int or None, number of horizontal left neighbors that are stored in nodes. If None, all neighbors are stored.
        vertical: int or None, number of ancestors that are stored in nodes. None: store all ancestors
    """
    for tree_str in trees:
        tree = tree_from_str(tree_str)
        backtraces = build_backtraces(tree)
        print(nested_tuple_to_str(marcovise(tree, horizontal, vertical, backtraces)))


if __name__ == "__main__":
    run_marcovise(["(ROOT (S (NP-SBJ (PRP It)) (VP (VBZ has) (NP (NP (DT no) (NN bearing)) (PP-DIR (IN on) (NP (NP (PRP$ our) (NN work) (NN force)) (NP-TMP (NN today)))))) (. .)))"], 999, 3)