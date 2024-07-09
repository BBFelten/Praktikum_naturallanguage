def get_signature(word, i):
    if len(word) == 0:
        return "UNK"
    
    letter_suffix = "-S"
    number_suffix = "-EPS"
    dash_suffix = "-EPS"
    period_suffix = "-EPS"
    comma_suffix = "-EPS"
    word_suffix = "-EPS"

    if word[0].isupper():
        if len([l for l in word if l.islower()]) == 0:
            letter_suffix = "-AC"
        elif i == 0:
            letter_suffix = "-SC"
        else:
            letter_suffix = "-C"
    
    if word.isdigit():
        number_suffix = "-N"
    elif len([l for l in word if l.isdigit()]) > 0:
        number_suffix = "-n"
    
    if "-" in word:
        dash_suffix = "-H"
    
    if "." in word:
        period_suffix = "-P"

    if "," in word:
        comma_suffix = "-C"
    
    if len(word) > 3 and word[-1].isalpha():
        word_suffix = "-" + word[-1].lower()
    
    return "UNK" + letter_suffix + number_suffix + dash_suffix + period_suffix + comma_suffix + word_suffix


def tree_from_str(input, get_terminal_list=False, unking=False, unk_list=[], smoothing=False, unk_signatures=["UNK"]):
    l = input.rstrip()
    stack = [] # save the previous levels
    current = [] # save rules at current level
    w = '' # save characters which are not separated by parentheses as a single string
    terminal_list = []
    i = 0

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
                    if unking:
                        if split[1] in unk_signatures:
                            terminal = unk_list.pop(0)
                        elif split[1] in unk_list:
                            if smoothing:
                                terminal = get_signature(split[1], i)
                                i += 1
                            else:
                                terminal = "UNK"
                        else:
                            terminal = split[1]
                    else:
                        terminal = split[1]
                    
                    current.append(terminal)
                    if get_terminal_list:
                        terminal_list.append(terminal)
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
                elif len(split) == 2: # if there is one space in w, it is a lexical rule and should be saved separately
                    current.append(split[0])
                    if unking:
                        if split[1] in unk_signatures:
                            terminal = unk_list.pop(0)
                        elif split[1] in unk_list:
                            if smoothing:
                                terminal = get_signature(split[1], i)
                                i += 1
                            else:
                                terminal = "UNK"
                        else:
                            terminal = split[1]
                    else:
                        terminal = split[1]
                    current.append(terminal)
                    terminal_list.append(terminal)
                else:
                    raise Exception("{} is not a valid string in PTB format!".format(l))
                w = ''
            last = stack.pop() # go one level up
            last.append(current)
            current = last

    result = current[0] # due to the given format, there is one level too much

    if get_terminal_list:
        return result, terminal_list

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