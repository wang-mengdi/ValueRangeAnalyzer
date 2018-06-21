import collections
from LexicalAnalyzer import *
from ConstraintGraph import *

#unified format: ops=(op1, op2, output), out="+" or "/" or ">"...

def not_num(name):
    return not (name[0].isdigit() or name[0] in ('+','-'))

def replace_list(A,replace_dict):
    n=len(A)
    for i in range(n):
        if A[i] in replace_dict:
            A[i]=replace_dict[A[i]]
    return A

def replace_ist(ist,replace_dict):
    ist.ops=replace_list(ist.ops,replace_dict)

def condition_revert(t): # a t b iff b revert(t) a, i.e. converse
    D={'<':'>','<=':'>=','>':'<','>=':'<='}
    assert(t in D)
    return D[t]

def condition_not(t): # a t b==False iff a not(t) b, i.e. inverse
    D={'<':'>=','<=':'>','>':'<=','>=':'<'}
    assert(t in D)
    return D[t]

class Condition:
    def __init__(self,name="CND",ops=(),opt=""):
        self.typ="CND"
        self.name=name
        self.ops=ops
        self.opt=opt
        self.to=[]
    def __str__(self):
        return self.name+" "+self.opt+"("+",".join(self.ops)+")  to=("+",".join(self.to)+")"
        #return "CND# "+self.opt+",".join(self.ops)
    def build_cst_graph(self,name_pref,var_dict,cst_dict):
        for v in self.ops:
            if not_num(v):
                if not v in var_dict:
                    var_dict[v]=Variable(v)
        #print(self.ops)
        assert(len(self.ops)==2)
        v1,v2=self.ops
        t=self.opt
        if not_num(v1):
            #true branch of v1
            if not v1+"@t" in var_dict:
                var_dict[v1+'@t']=Variable(v1+'@t')
            ct1=Condition(name_pref+"#t1$CND",[v1,v2,v1+"@t"],t)
            cst_dict[ct1.name]=ct1
            #false branch of v1
            if not v1+"@f" in var_dict:
                var_dict[v1+'@f']=Variable(v1+'@f')
            cf1=Condition(name_pref+"#f1$CND",[v1,v2,v1+'@f'],condition_not(t))
            cst_dict[cf1.name]=cf1
        if not_num(v2):
            #true branch of v2
            if not v2+"@t" in var_dict:
                var_dict[v2+'@t']=Variable(v2+'@t')
            ct2=Condition(name_pref+"#t2$CND",[v2,v1,v2+"@t"],condition_revert(t))
            cst_dict[ct2.name]=ct2
            #false branch of v2
            if not v2+"@f" in var_dict:
                var_dict[v2+'@f']=Variable(v2+'@f')
            cf2=Condition(name_pref+"#f2$CND",[v2,v1,v2+'@f'],condition_not(condition_revert(t)))
            cst_dict[cf2.name]=cf2


class Assignment(object):
    def __init__(self,name="IST",ops=(),opt=""):
        self.typ="IST"
        self.name,self.ops,self.opt=name,ops,opt
        self.to=[]
    def __str__(self):
        return self.name+" "+self.opt+"("+",".join(self.ops)+")"+"  to=("+",".join(self.to)+")"
        #$return "IST# "+self.dst+"="+self.opt+",".join(self.ops)
    def build_cst_graph(self,name_pref,var_dict,cst_dict):
        for v in self.ops:
            if not_num(v):
                if not v in var_dict:
                    var_dict[v]=Variable(v)
        a=Assignment(name_pref+"$IST",self.ops,self.opt)
        cst_dict[a.name]=a

class Phi(object):
    def __init__(self,name="PHI",ops=[]):
        self.typ="PHI"
        self.name,self.ops,self.opt=name,ops,"phi"
        self.to=[]
    def __str__(self):
        return self.name+" "+self.opt+"("+",".join(self.ops)+")  to=("+",".join(self.to)+")"
        #return "PHI# "+self.dst+"=phi("+self.src1+","+self.src2+")"
    def build_cst_graph(self,name_pref,var_dict,cst_dict):
        for v in self.ops:
            if not_num(v):
                if not v in var_dict:
                    var_dict[v]=Variable(v)
        p=Phi(name_pref+"$PHI",self.ops)
        cst_dict[p.name]=p

class Block(object):

    def __init__(self,name):
        self.name=name
        self.goto=None
        self.natural_goto=()
        self.ists=[]
        self.parsed=False

    def __str__(self):
        S=self.name+":\n"+"\n".join(map(str,self.ists))
        if len(self.goto)>1:
            assert(len(self.goto)==2)
            S=S+"\n"+str(self.jmp_cnd)
        return S+"\n$GOTO "+str(self.goto)

    def build_cst_graph(self,name_pref,var_dict,cst_dict):
        name_pref=name_pref+self.name
        n=len(self.ists)
        for k in range(n):
            i=self.ists[k]
            i.build_cst_graph("{}{:0>2d}".format(name_pref,k),var_dict,cst_dict)
        if len(self.goto)==2:
            self.jmp_cnd.build_cst_graph("{}{:0>2d}".format(name_pref,n),var_dict,cst_dict)

    def get_condition(self,line_tokens):
        assert(line_tokens[1]=='(')
        #print("get_condition: ",line_tokens)
        n=len(line_tokens)
        ops,opt=[],None
        for i in range(2,n):
            t=line_tokens[i]
            if t==')':
                break
            elif t=='<' or t=='>' or t=='<=' or t=='>=' or t=='==' or t=='!=':
                opt=t
            else:
                ops.append(t)
        assert(opt!=None)
        return Condition(ops=tuple(ops),opt=opt)

    def get_assignment(self,line_tokens):
        n=len(line_tokens)
        dst=line_tokens[0]
        assert(line_tokens[1]=='=')
        ops,opt=[],"" # this may be a unary operate, thus without opt
        for i in range(2,n-1):
            t=line_tokens[i]
            if t=='+' or t=='-' or t=='*' or t=='/':
                opt=t
            else:
                ops.append(t)
        ops.append(dst)
        return Assignment(ops=tuple(ops),opt=opt)

    def get_goto(self,tokens,blocks):
        assert(tokens[-1]==';')
        jump_to="".join(tokens[1:-1])
        assert(jump_to in blocks)
        return jump_to

    def replace(self,D):
        for i in self.ists:
            replace_ist(i,D)

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
                self.ists.append(Phi(ops=[src1,src2,dst]))
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

    def __str__(self):
        return "\n".join(map(str,[b for (m,b) in self.blocks.items()]))

    def build_cst_graph(self,var_dict,cst_dict):
        for (name,b) in self.blocks.items():
            b.build_cst_graph(self.name,var_dict,cst_dict)
    
    def get_name(self,tokens):
        self.name=tokens[0]

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
        #self.replace_if()
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
    def __str__(self):
        return "=================\n".join(map(str,[f for (m,f) in self.functions.items()]))

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
            self.functions[f.name]=f

    def build_cst_graph(self):
        G=CSTGraph()
        assert(len(self.functions)==1)
        for name,f in self.functions.items():
            f.build_cst_graph(G.vars,G.csts)
        for name,c in G.csts.items():
            c.to=(c.ops[-1],)
            O=c.ops[:-1]
            if c.typ=="CND":
                assert(len(c.ops)==3)
                O=c.ops[:1]
                c.future=(c.ops[1],)
            for v in O:
                if not_num(v):
                    G.vars[v].to.append(name)
        return G


