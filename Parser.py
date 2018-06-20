import collections
from LexicalAnalyzer import *
from ConstraintGraph import *

index = 0

#class Variable(object):
#    def __init__(self,typ,name):
#        self.typ=typ
#        self.name=name

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

class Jump(object):
    def __init__(self,dst):
        self.dst=dst

class Phi(object):
    def __init__(self,src1,src2,dst):
        self.src1=src1
        self.src2=src2

class Block(object):
    def __init__(self,name):
        self.name=name
        self.goto=None
        self.ists=[]

#    def parse(self,):

class Function(object):

    def __init__(self):
        #self.jumpmap={}
        #self.name=name
        self.blocks={}
        #self.entry=None
    
    def get_name(self,tokens):
        self.name=tokens[0]

    def new_variable(self,typ,name):
        s=self.name+'_'+name
        v = Variable(typ,s)
        self.ast.variables[s]=v
        return v

    def get_arglist(self,line_tokens):
        self.arglist = []
        n = len(line_tokens)
        #print("get_arglist: ",line_tokens)
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

    def get_jumpdst(self,line_tokens):
        assert(line_tokens[0]=='goto')
        return line_tokens[1]

    def get_condition(self,line_tokens):
        assert(line_tokens[1]=='(')
        #print("get_condition: ",line_tokens)
        n=len(line_tokens)
        c=Expression()
        for i in range(2,n):
            t=line_tokens[i]
            if t==')':
                break
            elif t=='<' or t=='>' or t=='<=' or t=='>=' or t=='==' or t=='!=':
                c.opt=t
            else:
                c.ops.append(t)
        return c

    def get_return(self,line_tokens):
        return Return(line_tokens[1])

    def get_assignment(self,line_tokens):
        #print("get_assignment: ",line_tokens)
        a=Assignment()
        n=len(line_tokens)
        a.dst=line_tokens[0]
        assert(line_tokens[1]=='=')
        for i in range(2,n):
            t=line_tokens[i]
            if t=='+' or t=='-' or t=='*' or t=='/':
                a.opt=t
            else:
                a.ops.append(t)
        return a

    def deal_PHI(tokens):
        assert(tokens[2]=='=')
        assert(tokens[3]=='PHI')
        assert(tokens[4]=='<')
        #src1=tokens[]
        assert(tokens[9]==',')
        assert(tokens[14]=='>')
        

    def parse_from(self,lines): # lines is a collections.deque
        is_bb=lambda t:t[0][-1]==':'
        #print("function: {}, lines:{}".format(self.name,lines))
        bbs=list(filter(is_bb,zip(lines,range(len(lines)))))
        bbs=bbs+[(None,-1),] # to deal with the final block
        bn=len(bbs)
        B=[]
        for i in range(bn-1):
            lid,rid=bbs[i][1],bbs[i+1][1]
            tokens=lines[lid]
            print(tokens)
            assert(tokens[0]=='<' and tokens[-2]=='>' and tokens[-1]==':')
            b=Block("".join(tokens[:-1]))
            b.lines=lines[lid:rid]
            B.append(b)
            #self.blocks[b.name]=b
        for i in range(len(B)-1):
            B[i].natural_goto=B[i+1].name
            self.blocks[B[i].name]=B[i]
        self.entry,self.out=B[0],B[-1]
        return
        global index
        self.ast=ast
        while len(lines) > 0:
            tokens = get_tokens(lines.popleft())
            #print("index: {}, tokens:{}".format(index,tokens))
            cur_block = None
            if tokens[0]=='<': # a jump label
                assert(tokens[1]=='bb' or tokens[1][0]=='L')
                assert(tokens[-2]=='>')
                assert(tokens[-1]==':')
                if cur_block != None:
                    self.blocks[cur_block.name]=cur_block
                    if len(self.blocks)==1:
                        self.entry=self.blocks[cur_block.name]
                cur_block=Block(int(tokens[2]))
                #self.jumpmap['bb'+tokens[2]]=index
            elif tokens[0]=='#': # PHI operation
                tgt,src1,src2=tokens[1],tokens[5],tokens[10]
                map(self.ast.add_var,[tgt,src1,src2])
                ast.csts[index]=Phi(src1,src2,tgt)
                index += 1
            elif tokens[0]==self.name: # definition of this function
                self.get_arglist(tokens)
            elif tokens[0]=='{' or tokens[0]=='}': # the line after function definition
                pass
            elif tokens[0]=='int' or tokens[0]=='float': # definition of a variable
                self.new_variable(tokens[0],tokens[1])
                index += 1
            elif tokens[0]=='if':
                ist=IfJump(self.get_condition(tokens))
                ist.jump_true=self.get_jumpdst(get_tokens(lines.popleft()))
                if get_tokens(lines[0])[0]=='else':
                    lines.popleft()
                    ist.jump_false=self.get_jumpdst(get_tokens(lines.popleft()))
                self.ast.jumps[index]=ist
                index += 1
            elif tokens[0]=='goto':
                ist=Jump(tokens[1])
                self.ast.jumps[index]=ist
                index += 1
            elif tokens[0]=='return':
                r=self.get_return(tokens)
                self.return_ist=r
                index += 1
            else: # an assignment
                ist=self.get_assignment(tokens)
                self.ast.assignments[index]=ist
                if(len(ist.ops)==1):
                    index += 1


class CFGraph(object):

    def __init__(self):
        #self.vars = {}
        #self.csts = {} # constraints
        #self.var_names={}
        self.functions={}
        #self.variables={}
        #self.jumps={}
        #self.assignments={}

    def add_var(self,name):
        if not name in self.vars:
            self.vars[name]=Variable(name)

    def parse_from(self, lines): # lines is a list, its every element is a list of tokens
        is_brace=lambda t:t[0][0] in ["{","}"]
        braces=list(filter(is_brace,zip(lines,range(len(lines)))))
        fn=len(braces)
        for i in range(0,fn,2):
            lid=braces[i][1]
            f=Function()
            f.get_name(lines[lid-1])
            rid=braces[i+1][1]
            f.parse_from(lines[lid+1:rid])
        return
        global index
        index = 0
        while len(lines) > 0:
            tokens = get_tokens(lines.popleft())
            if tokens[0]=='#': # comment
                index += 1
                pass
            elif tokens[0]==';;': # function prototype
                assert(tokens[1]=='Function')
                nm=tokens[2]
                f = Function(nm)
                f.parse_from(lines,self)
                self.functions[nm]=f


