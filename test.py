import os
import sys

if __name__=='__main__':
    os.system("python3 main.py benchmark/t{}.ssa benchmark/t{}.arg".format(sys.argv[1],sys.argv[1]))
