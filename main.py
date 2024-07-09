import sys
import argparse

from pcfg.induce import induce_grammar
from pcfg.parse import run_cyk_parse
from pcfg.debinarise import run_debinarise
from pcfg.unking import basic_unking
from pcfg.binarise import run_marcovise


def main(command, input, grammar=None, rules=None, lexicon=None, paradigma=None, initial_nonterminal=None, unking=False,
         smoothing=False, threshold_beam=0, rank_beam=None, astar=None,
         horizontal=None, vertical=None, threshold=None):

    if command == "induce":
        return induce_grammar(grammar=grammar, corpus=input)
    
    elif command == "parse":
        if not rules or not lexicon:
            raise Exception("parse requires grammar and lexicon!")
        if paradigma == "deductive" or astar:
            sys.exit(22)
        else:
            sentences = input.read().strip().split('\n')
            # print(lexicon)
            return(run_cyk_parse(rules=rules, lexicon=lexicon, sentences=sentences, initial=initial_nonterminal, unking=unking, threshold_beam=threshold_beam, rank_beam=rank_beam, smoothing=smoothing))
    
    elif command == "binarise":
        if horizontal:
            horizontal = int(horizontal)
        if vertical:
            vertical = int(vertical)
        return run_marcovise(input, horizontal, vertical)
    
    elif command == "debinarise":
        return(run_debinarise(input))
    
    elif command == "unk":
        return basic_unking(input, float(threshold))
    
    elif command == "smooth":
        return basic_unking(input, float(threshold), smooth=True)
    
    elif command == "outside":
        sys.exit(22)
    
    else:
        raise Exception("ERROR: Unknown command")


def parse_arguments():
    main_parser = argparse.ArgumentParser(
        description=("Argument parser for pcfg_tool"), add_help=False
    )
    subparsers = main_parser.add_subparsers(dest="command")

    induce_parser = subparsers.add_parser("induce")
    # Optional positional argument
    induce_parser.add_argument("grammar", nargs='?', default=None)

    # Required positional arguments
    parse_parser = subparsers.add_parser("parse")
    parse_parser.add_argument("rules", type=str)
    parse_parser.add_argument("lexicon", type=str)

    # Optional arguments
    parse_parser.add_argument('-p', '--paradigma', type=str, choices=['cyk', 'deductive'], default='cyk',
                              help='Parser paradigm (cyk or deductive). Default: cyk.')
    parse_parser.add_argument('-i', '--initial-nonterminal', type=str, default='ROOT',
                              help='Initial non-terminal. Default: ROOT.')
    parse_parser.add_argument('-u', '--unking', action='store_true',
                              help='Replace unknown words by UNK (3b).')
    parse_parser.add_argument('-s', '--smoothing', action='store_true',
                              help='Replace unknown words according to the Smoothing-Implementierung (3d).')
    parse_parser.add_argument('-t', '--threshold-beam', type=float, default=0,
                              help='Apply Beam-Search with Threshold (4a).')
    parse_parser.add_argument('-r', '--rank-beam', type=int, default=0,
                              help='Apply Beam-Search with constant Beam (4a).')
    parse_parser.add_argument('-a', '--astar', type=str,
                              help='Apply A*-search (4b). Load Outside weights from file PATH.')

    binarise_parser = subparsers.add_parser("binarise", add_help=False)
    binarise_parser.add_argument('-h', '--horizontal', default=None, required=False)
    binarise_parser.add_argument('-v', '--vertical', default=None, required=False)
    
    debinarise_parser = subparsers.add_parser("debinarise")
    
    unk_parser = subparsers.add_parser("unk")
    unk_parser.add_argument('-t', '--threshold', required=False, default=None)
    
    smooth_parser = subparsers.add_parser("smooth")
    smooth_parser.add_argument('-t', '--threshold', required=False, default=None)
    
    outside_parser = subparsers.add_parser("outside")
    outside_parser.add_argument('-i', '--initial-nonterminal', type=str, required=False, default='ROOT')

    # Parse die Argumente
    return main_parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    input = sys.stdin

    main(input=input, **vars(args))

