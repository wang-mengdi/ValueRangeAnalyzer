import collections
from LexicalAnalyzer import *
from Parser import *

def parse_cfg(filename):
    fin = open(filename)
    lines = delete_empty_lines(fin.readlines())
    token_lines=list(map(get_tokens,lines))
    c_graph=CFGraph()
    c_graph.parse_from(token_lines)
    return c_graph
    #get_tokens("".join(lines))
    #print(lines)
    #print(get_tokens("".join(lines)))

if __name__=="__main__":
    CFG=parse_cfg(sys.argv[1])
    #print(CFG.functions["foo"])
    CST=CFG.build_cst_graph()
    CST.read_arg_bound(sys.argv[2])
    #print(CST)
    CST.analyze()
