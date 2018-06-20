import collections
from LexicalAnalyzer import *
from ConstraintGraph import *

index = 0

#class Variable(object):
#    def __init__(self,typ,name):
#        self.typ=typ
#        self.name=name

def replace_list(A,replace_dict):
    n=len(A)
    for i in range(n):
        if A[i] in replace_dict:
            A[i]=replace_dict[A[i]]
    return A

class Expression:
    def __init__(self):
        self.ops=[]
        self.opt=""
    def __str__(self):
        return "EXP# "+self.opt+",".join(self.ops)

class Assignment(object):
    def __init__(self):
        self.ops = []
        self.opt=""
        self.dst=""
    def replace(self,D):
        self.ops=replace_list(self.ops,D)
    def __str__(self):
        return "IST# "+self.dst+"="+self.opt+",".join(self.ops)

class Phi(object):
    def __init__(self,src1,src2,dst):
        self.src1=src1
        self.src2=src2
        self.dst=dst
    def replace(self,D):
        self.src1,self.src2,self.dst=tuple(replace_list([self.src1,self.src2,self.dst],D))
    def __str__(self):
        return "PHI# "+self.dst+"=phi("+self.src1+","+self.src2+")"

class Block(object):

    def __init__(self,name):
        self.name=name
        self.goto=None
        self.natural_goto=()
        self.ists=[]
        self.parsed=False

    def __str__(self):
        return self.name+":\n"+"\n".join(map(str,self.ists))+"\nGOTO# "+str(self.goto)

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

    def get_assignment(self,line_tokens):
        a=Assignment()
        n=len(line_tokens)
        a.dst=line_tokens[0]
        assert(line_tokens[1]=='=')
        for i in range(2,n-1):
            t=line_tokens[i]
            if t=='+' or t=='-' or t=='*' or t=='/':
                a.opt=t
            else:
                a.ops.append(t)
        return a

    def get_goto(self,tokens,blocks):
        assert(tokens[-1]==';')
        jump_to="".join(tokens[1:-1])
        assert(jump_to in blocks)
        return jump_to

    def replace(self,D):
        for i in self.ists:
            i.replace(D)

    def dfs_replace(self,name,blocks,rep_dict,visited):
        #print("dfs replace if with {} of {}".format(self.name,name))
        if name in visited:
            return
        b=blocks[name]
        b.replace(rep_dict)
        visited.add(name)
        for nxt in b.goto:
            self.dfs_replace(nxt,blocks,rep_dict,visited)

    def start_replace_if(self,blocks):
        #print("start replace if: {}".format(self.name))
        if len(self.goto)!=2:
            return
        vis_true=set()
        vis_true.add(self.name)
        var_ops=list(filter(lambda t:not t[0].isdigit(),self.jmp_cnd.ops))
        ops_with_suf_zip=lambda ops,suf:zip(ops,list(map(lambda a:a+suf,ops)))
        D=dict(ops_with_suf_zip(var_ops,'@t'))
        self.dfs_replace(self.goto[0],blocks,D,vis_true)
        vis_false=set()
        vis_false.add(self.name)
        D=dict(ops_with_suf_zip(var_ops,'@f'))
        self.dfs_replace(self.goto[1],blocks,D,vis_false)
        assert(len(vis_true&vis_false)==1)

    def parse(self,blocks):
        #print("parse block:{}".format(self.name))
        #print("lines:{}".format(self.lines))
        ln=len(self.lines)
        assert(self.lines[0][-1]==':') # defines the basic block
        self.goto=None
        i = 1
        while i<ln:
            tokens=self.lines[i]
            #print("get line {} tokens {}:".format(i,tokens))
            #print(tokens)
            if tokens[0]=='#': # PHI operation
                dst=tokens[1]
                assert(tokens[2]=='=' and tokens[3]=='PHI' and tokens[4]=='<')
                src1=tokens[5]
                assert(tokens[6]=='(' and tokens[8]==')' and tokens[9]==',')
                src2=tokens[10]
                self.ists.append(Phi(src1,src2,dst))
                #map(self.ast.add_var,[tgt,src1,src2])
                #ast.csts[index]=Phi(src1,src2,tgt)
                #index += 1
            elif tokens[0]=='goto':
                self.goto=(self.get_goto(tokens,blocks),)
            elif tokens[0]=='if':
                self.jmp_cnd=self.get_condition(tokens)
                jmp_true=self.get_goto(self.lines[i+1],blocks)
                assert(self.lines[i+2][0]=='else')
                jmp_false=self.get_goto(self.lines[i+3],blocks)
                self.goto=(jmp_true,jmp_false)
                i += 3
            elif tokens[0]=='return':
                self.rtn_var=tokens[1]
            else: # an assignment
                ist=self.get_assignment(tokens)
                self.ists.append(ist)
            i += 1
        if self.goto==None:
            #print("set natural: {}".format(self.natural_goto))
            self.goto=self.natural_goto
        self.parsed=True

class Function(object):

    def __init__(self):
        #self.jumpmap={}
        #self.name=name
        self.blocks={}
        self.entry,self.out=None,None
    
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

    def replace_if(self):
        for (name,b) in self.blocks.items():
            b.start_replace_if(self.blocks)

    def dfs_parse_block(self,bname):
        #print("dfs called: {}".format(bname))
        b=self.blocks[bname]
        if b.parsed:
            return
        b.parse(self.blocks)
        for nxt in b.goto:
            self.dfs_parse_block(nxt)

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
            #print(tokens)
            assert(tokens[0]=='<' and tokens[-2]=='>' and tokens[-1]==':')
            b=Block("".join(tokens[:-1]))
            b.lines=lines[lid:rid]
            B.append(b)
            #self.blocks[b.name]=b
        for i in range(len(B)-1):
            B[i].natural_goto=(B[i+1].name,)
        for b in B:
            self.blocks[b.name]=b
        self.entry,self.out=B[0].name,B[-1].name
        self.dfs_parse_block(self.entry)
        self.replace_if()
        #for (name,b) in self.blocks.items():
        #    print(b,"\n")

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


