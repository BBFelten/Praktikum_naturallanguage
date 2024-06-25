from .helpers.helpers import tree_from_str, nested_tuple_to_str

def basic_unking(corpus, threshold):
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
        tree = tree_from_str(line, get_terminal_list=False, unking=True, unk_list=set(to_be_replaced))
        tree_str = nested_tuple_to_str(tree)

        modified_corpus += tree_str + "\n"
        print(tree_str)
    
    modified_corpus = modified_corpus.strip()
    return modified_corpus

if __name__ == "__main__":
    basic_unking(["(A (B (A a)))"], 10)