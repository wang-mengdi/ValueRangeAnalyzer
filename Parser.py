import collections
from LexicalAnalyzer import *

index = 0

class Variable(object):
    def __init__(self,typ,name):
        self.typ=typ
        self.name=name

def Assignment(object):
    def __init__(self,op1,op2,opt,dst):
        self.op1=op1
        self.op2=op2
        self.opt=opt
        self.dst=dst

class Function(object):

    def __init__(self,name):
        self.jumpmap={}
        self.name=name

    def new_variable(typ,name):
        s=self.name+'_'+name
        v = Variable(typ,s)
        self.ast.variables[s]=v
        return v

    def get_arglist(line_tokens):
        self.arglist = []
        n = len(line_tokens)
        assert(line_tokens[1]=='(')
        i = 2
        while i<n:
            t=line_tokens[i]
            if t=='int' or t=='float':
                self.arglist.append(new_variable(t,line_tokens[i+1]))
                i += 2
            elif t==',':
                i += 1
            elif t==')':
                break

    def parse_from(lines,ast): # lines is a collections.deque
        self.ast=ast
        while len(lines) > 0:
            tokens = GetTokens(lines.popleft())
            if tokens[0]=='#': # comment
                global index
                index += 1
            elif tokens[0]==self.name: # definition of this function
                get_arglist(tokens[0])
            elif tokens[0]=='<': # a jump label
                assert(tokens[1]=='bb')
                assert(tokens[3]=='>')
                global index
                self.jumpmap['bb'+tokens[2]]=index
            elif tokens[0]=='int'||tokens[0]=='float': # definition of a variable
                new_variable(tokens[0],tokens[1])
            elif tokens[0]=='if':
                assert(tokens[1])


class AST(object):

    def __init__(self):
        self.functions={}
        self.variables={}

    def parse_from(lines): # lines is a collection.deque
        global index
        index = 0
        while len(lines) > 0:
            tokens = GetTokens(lines.popleft())
            if tokens[0]=='#': # comment
                global index
                index += 1
                pass
            elif tokens[0]==';;': # function prototype
                assert(tokens[1]=='Function')
                nm=tokens[2]
                f = Function(nm)
                f.parse_from(lines,self)
                functions[nm]=f


