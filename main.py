import collections
from LexicalAnalyzer import *
from Parser import *


def parse(lines):
    for i in range(len(lines)):
        L = lines[i]

def work(filename):
    fin = open(filename)
    lines = delete_comments(fin.readlines())
    #get_tokens("".join(lines))
    #print(lines)
    print(get_tokens("".join(lines)))

if __name__=="__main__":
    work(sys.argv[1])
