import os
import sys
from LexicalAnalyzer import *


def parse(lines):
    for i in range(len(lines)):
        L = lines[i]

def work(filename):
    fin = open(filename)
    lines = fin.readlines()
    print(lines)
    GetTokens("".join(lines))

if __name__=="__main__":
    work(sys.argv[1])
