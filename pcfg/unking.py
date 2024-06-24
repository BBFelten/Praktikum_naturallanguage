from .helpers.helpers import tree_from_str

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
        for word in to_be_replaced:
            line = line.replace(word, "UNK").strip()
        modified_corpus += line + "\n"
        print(line)
    
    modified_corpus = modified_corpus.strip()
    return modified_corpus

if __name__ == "__main__":
    basic_unking(["(A (B (A a)))"], 10)