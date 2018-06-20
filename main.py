import collections
from LexicalAnalyzer import *
from Parser import *


def parse(lines):
    for i in range(len(lines)):
        L = lines[i]

def parse_ast(filename):
    fin = open(filename)
    lines = delete_comments(fin.readlines())
    token_lines=list(map(get_tokens,lines))
    a=CFGraph()
    a.parse_from(token_lines)
    return a
    #get_tokens("".join(lines))
    #print(lines)
    #print(get_tokens("".join(lines)))

if __name__=="__main__":
    ast=parse_ast(sys.argv[1])
