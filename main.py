import sys

from pcfg.induce import induce_grammar

def main(command, options, input):
    if command == "induce":
        if options and len(options) > 0:
            return induce_grammar(grammar=options[0], corpus=input)
        else:
            return induce_grammar(grammar=None, corpus=input)
    elif command == "parse":
        sys.exit(22)
    elif command == "binarise":
        sys.exit(22)
    elif command == "debinarise":
        sys.exit(22)
    elif command == "unk":
        sys.exit(22)
    elif command == "smooth":
        sys.exit(22)
    elif command == "outside":
        sys.exit(22)
    else:
        raise Exception("ERROR: Unknown command")

if __name__ == "__main__":
    command = sys.argv[1]
    call = sys.argv[1:]
    input = sys.stdin

    if len(call) > 1:
        options = call[1:]
    else:
        options = None

    main(command, options, input)