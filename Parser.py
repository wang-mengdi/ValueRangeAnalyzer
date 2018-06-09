import collections
from LexicalAnalyzer import *

index = 0

class Variable(object):
    def __init__(self,typ,name):
        self.typ=typ
        self.name=name

class Expression:
    def __init__(self):
        self.ops=[]
        self.opt=[]

class Assignment(object):
    def __init__(self):
        self.ops = []

class Return(object):
    def __init__(self,var):
        self.var=var

class IfJump(object):
    def __init__(self,cnd):
        self.cnd=cnd

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

    def get_jumpdst(line_tokens):
        assert(line_tokens[0]=='goto')
        return line_tokens[1]

    def get_condition(line_tokens):
        assert(line_tokens[1]=='(')
        n=len(line_tokens)
        i=2
        c=Expression()
        while i<n:
            t=line_tokens[i]
            if t==')':
                break
            elif t=='<' or t=='>' or t=='<=' or t=='>=' or t=='==' or t=='!=':
                c.opt=t
            else:
                t.ops.append(t)
        return c

    def get_return(line_tokens):
        return Return(line_tokens[1])

    def get_assignment(line_tokens):
        a=Assignment()
        n=len(line_tokens)
        a.dst=line_tokens[0]
        assert(line_tokens[1]=='=')
        i=2
        while i<n:
            t=line_tokens[i]
            if t=='+' or t=='-' or t=='*' or t=='/':
                a.opt=t
            else:
                a.ops.append(t)
        return a

    def parse_from(lines,ast): # lines is a collections.deque
        self.ast=ast
        while len(lines) > 0:
            tokens = get_tokens(lines.popleft())
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
            elif tokens[0]=='int' or tokens[0]=='float': # definition of a variable
                new_variable(tokens[0],tokens[1])
                indesx += 1
            elif tokens[0]=='if':
                ist=IfJump(get_condition())
                ist.jump_true=get_jumpdst(get_tokens(lines.popleft()))
                if get_tokens(lines[0])[0]=='else':
                    lines.popleft()
                    ist.jump_false=get_jumpdst(get_tokens(lines.popleft()))
                global index
                self.ifjumps[index]=ist
                index += 1
            elif tokens[0]=='return':
                r=get_return(tokens)
                self.return_ist=r
                global index
                index += 1
            else:
                ist=get_assignment(tokens)
                global index
                self.ast.assignments[index]=ist
                index += 1


class AST(object):

    def __init__(self):
        self.functions={}
        self.variables={}
        self.ifjumps={}
        self.assignments={}

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


