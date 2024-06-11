def tree_from_str(input):
    l = input.rstrip()
    stack = [] # save the previous levels
    current = [] # save rules at current level
    w = '' # save characters which are not separated by parentheses as a single string

    for char in l:
        if char not in [')', '(']:
            w += char # add to current string
        elif char == '(': # reach the next left parenthesis, save what came before
            w = w.strip()
            if w != '': 
                split = [c for c in w.split(' ') if c != ''] 
                if len(split) == 1: # if w has no space, it is a non-terminal
                    current.append(w)
                elif len(split) == 2: # if there is one space in w, it is a lexical rule and should be saved separately
                    current.append(split[0])
                    current.append(split[1])
                else:
                    raise Exception("{} is not a valid string in PTB format!".format(l))
                w = ''
            stack.append(current) # add new rule to the stack -> go one level lower
            current = []
        elif char == ')': # reach right parenthesis, save what came before
            w = w.strip()
            if w != '':
                split = [c for c in w.split(' ') if c != '']
                if len(split) == 1:
                    current.append(w)
                elif len(split) == 2:
                    current.append(split[0])
                    current.append(split[1])
                else:
                    raise Exception("{} is not a valid string in PTB format!".format(l))
                w = ''
            last = stack.pop() # go one level up
            last.append(current)
            current = last

    result = current[0] # due to the given format, there is one level too much

    return result


def nested_tuple_to_str(t):
    """Helper function to turn a nested tuple to string without quotes and commas
    Parameters:
        t: tuple
    """
    if isinstance(t, tuple) or isinstance(t, list):
        return '(' + ' '.join(nested_tuple_to_str(item) for item in t) + ')'
    else:
        return str(t)