import collections
import copy
from LexicalAnalyzer import *
from ConstraintGraph import *

entry_function="foo"
#unified format: ops=(op1, op2, output), out="+" or "/" or ">"...

def var_add_pref(pref,var):
    return pref+var if not_num(var) else var

def replace_list(A,replace_dict):
    A=list(A)
    n=len(A)
    for i in range(n):
        if A[i] in replace_dict:
            A[i]=replace_dict[A[i]]
    return A

def replace_ist(ist,replace_dict):
    ist.ops=replace_list(ist.ops,replace_dict)
    return ist

def condition_revert(t): # a t b iff b revert(t) a, i.e. converse
    D={'<':'>','<=':'>=','>':'<','>=':'<=',"==":'==','!=':'!='}
    assert(t in D)
    return D[t]

def condition_not(t): # a t b==False iff a not(t) b, i.e. inverse
    D={'<':'>=','<=':'>','>':'<=','>=':'<','==':'!=','!=':'=='}
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
        #print("name:{}".format(self.name))
        return self.name+" "+self.opt+"("+",".join(self.ops)+")  to=("+",".join(self.to)+")"
        #return "CND# "+self.opt+",".join(self.ops)
    def build_cst_graph(self,name_pref,var_dict,cst_dict):
        for v in self.ops:
            if not_num(v):
                if not v in var_dict:
                    var_dict[v]=Variable(v)
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

def get_real_var(tokens):
    return tokens[0].split('_')[0] if 'D' in tokens else tokens[0]


def get_expression(pref,tokens): # it's like ['a'] or ['a' '+' 'b'], tokens will be destroyed
    #print("get expression: {}".format(tokens))
    all_opts=['==','<','>','>=','<=','+','-','*','/']
    opt_lis=tuple(filter(lambda t:t in all_opts, tokens))
    assert(len(opt_lis)<=1)
    if len(opt_lis)==0:
        ops=(get_real_var(tokens),)
        opt=""
    else:
        opt=opt_lis[0]
        k=tokens.index(opt)
        s1,s2=tokens[:k],tokens[k+1:]
        src1,src2=get_real_var(s1),get_real_var(s2)
        ops=(src1,src2)
    ops=tuple(map(lambda t:var_add_pref(pref,t),ops))
    #print("expression ops={},opt={}".format(ops,opt))
    return ops,opt

class Block(object):

    def __init__(self,name):
        self.name=name
        self.goto=None
        self.natural_goto=""
        self.ists=[]
        self.parsed=False
        self.cross_func_jump=False

    def __str__(self):
        S=self.name+":\n"+"\n".join(map(str,self.ists))
        #print("turn str,name={},goto={}".format(self.name,self.goto))
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


    def get_condition(self,fun_pref,line_tokens):
        assert(line_tokens[1]=='(' and line_tokens[-1]==')')
        #print("get_condition: ",line_tokens)
        ops,opt=get_expression(fun_pref,line_tokens[2:-1])
        #print("get condition: tokens={},ops={},opt={} ".format(line_tokens,ops,opt))
        assert(len(ops)==2)
        assert(opt in ['==','<','>','>=','<='])
        return Condition(ops=tuple(ops),opt=opt)

    def get_assignment(self,fun_pref,line_tokens):
        print("get assignment from {},fun_pref={}".format(line_tokens,fun_pref))
        n=len(line_tokens)
        dst=var_add_pref(fun_pref,line_tokens[0])
        assert(line_tokens[1]=='=' and line_tokens[-1]==';')
        ops,opt=get_expression(fun_pref,line_tokens[2:-1])
        assert(opt=="" or opt in ['+','-','*','/'])
        ops=ops+(dst,)
        assert(len(ops) in [2,3])
        print("get assignment result ops={}".format(ops))
        return Assignment(ops=tuple(ops),opt=opt)


    def get_goto(self,pref,tokens,cfg):
        #print("get goto: ",tokens)
        assert(tokens[-1]==';')
        if '(' in tokens:
            k1,k2=tokens.index('(')+1,tokens.index(')')
        else:
            k1,k2=1,-1
        jump_to=pref+"".join(tokens[k1:k2])
        #print("parse to pref={} ,jump_to={} ".format(pref,tokens[k1:k2]))
        assert jump_to in cfg.blocks
        return jump_to

    def get_func_call_list(self,fun_pref,tokens): # tokens is like [a,b,c]...
        args=[]
        while ',' in tokens:
            k=tokens.index(',')
            s=tokens[:k]
            t=s[0]
            if 'D' in s:
                t=t.split('_')[0] # means it's from arg list
            args.append(fun_pref+t)
            tokens=tokens[k+1:]
        s=tokens
        t=s[0]
        if 'D' in s:
            t=t.split('_')[0] # means it's from arg list
        args.append(fun_pref+t)
        return args

    def replace(self,D):
        for i in self.ists:
            replace_ist(i,D)

    def DFS_replace(self,name,block_dict,rep_dict,visited):
        print("dfs replace if with {} of {},dict={}".format(self.name,name,rep_dict))
        if name in visited or len(rep_dict)==0:
            return
        visited.add(name)
        b=block_dict[name]
        n=len(b.ists)
        r1=rep_dict.copy()
        #b.replace(rep_dict)
        for k in range(n):
            ist=b.ists[k]
            if ist.ops[-1] in r1:
                r1.pop(ist.ops[-1])
            replace_ist(ist,r1)
        if not b.cross_func_jump:
            for nxt in b.goto:
                self.DFS_replace(nxt,block_dict,r1,visited)

    def start_replace_if(self,cfg):
        #print("start replace if: {}".format(self.name))
        #print("name={},goto={}".format(self.name,self.goto))
        if len(self.goto)!=2:
            return
        vis_true=set()
        vis_true.add(self.name)
        var_ops=list(filter(not_num,self.jmp_cnd.ops))
        ops_with_suf_zip=lambda ops,suf:zip(ops,list(map(lambda a:a+suf,ops)))
        D=dict(ops_with_suf_zip(var_ops,'@t'))
        self.DFS_replace(self.goto[0],cfg.blocks,D,vis_true)
        vis_false=set()
        vis_false.add(self.name)
        D=dict(ops_with_suf_zip(var_ops,'@f'))
        self.DFS_replace(self.goto[1],cfg.blocks,D,vis_false)
###########################################################################################
#TODO: does this assert bite?
        #assert(len(vis_true&vis_false)==1)

    def DFS_parse(self,cfg):
        if self.parsed:
            return
        self.parsed=True
        #print("DFS parse block:{}".format(self.name))
        #print("lines:{}".format(self.lines))
        fun=cfg.functions[self.fun_name]
        pref=fun.name
        assert(self.lines[0][-1]==':' or '|' in self.name) # defines the basic block
        self.goto=None
        i = 1
        while i<len(self.lines):
            tokens=self.lines[i]
            #print("get line {} tokens {}:".format(i,tokens))
            #print(tokens)
            if tokens[0]=='#': # PHI operation
                dst=var_add_pref(pref,tokens[1])
                assert(tokens[2]=='=' and tokens[3]=='PHI' and tokens[4]=='<')
                assert(tokens[-1]=='>')
                src1,src2=self.get_func_call_list(pref,tokens[5:-1])
                print("parse PHI: src1,src2,dst={},{},{}".format(src1,src2,dst))
                self.ists.append(Phi(ops=[src1,src2,dst]))
            elif tokens[0]=='goto':
                self.goto=(self.get_goto(pref,tokens,cfg),)
            elif tokens[0]=='if':
                self.jmp_cnd=self.get_condition(pref,tokens)
                jmp_true=self.get_goto(pref,self.lines[i+1],cfg)
                assert(self.lines[i+2][0]=='else')
                jmp_false=self.get_goto(pref,self.lines[i+3],cfg)
                self.goto=(jmp_true,jmp_false)
                i += 3
            elif tokens[0]=='return':
                #print("return spotted\n")
                fun.rtn_var=pref+tokens[1]
                if fun.rtn_save!=None: # return to another function point
                    self.cross_func_jump=True
                    ops=(fun.rtn_var,fun.rtn_save)
                    self.ists.append(Assignment(ops=ops,opt=""))
                    self.goto=(fun.rtn_goto,)
                else:
                    cfg.rtn_var=fun.rtn_var
            elif '=' in tokens:
                #print("parse general assign: ",tokens)
                assert(tokens[1]=='=' and tokens[-1]==';')
                if tokens[2] in cfg.functions:
                    dst=pref+tokens[0]
                    #split this basic block into 2
                    b2=copy.copy(self)
                    b2.parsed=False
                    b2.lines=b2.lines[i:] # the first line of block.lines is useless, just add a place
                    self.lines=self.lines[:i]
                    b2.name=b2.name+"|"
                    cfg.blocks[b2.name]=b2
                    fname=tokens[2]
                    fun=copy.copy(cfg.functions[fname])
                    cfg.call_cnt[fname] += 1
                    fcnt=cfg.call_cnt[fname]
                    fun.name=fun.name+str(fcnt)
                    call_pref=fun.name
                    fun.rtn_save=dst
                    fun.rtn_goto=b2.name
                    fun.register_function(cfg)
                    assert(tokens[3]=='(')
                    call_list=self.get_func_call_list(pref,tokens[4:-2])
                    for i in range(len(call_list)):
                        ops=(call_list[i],call_pref+fun.arglist[i])
                        opt=""
                        self.ists.append(Assignment(ops=tuple(ops),opt=opt))
                    self.goto=(call_pref+fun.entry,)
                    #self.lines.append(get_tokens("goto {};".format(call_pref+fun.entry)))
                    #print("manually add goto:",self.lines[-1])
                else: # an assignment
                    ist=self.get_assignment(pref,tokens)
                    self.ists.append(ist)
            i += 1
        if self.goto==None:
            #print("set natural: {}".format(self.natural_goto))
            if self.natural_goto=="":
                self.goto=()
            else:
                self.goto=(pref+self.natural_goto,)
            #print("dfs parse at block {}, goto={},natural={},dict_goto={}".format(self.name,self.goto,self.natural_goto,cfg.blocks[self.name].goto))
        #print("ready to goto:{} ".format(self.goto))
        for y in self.goto:
            cfg.blocks[y].DFS_parse(cfg)

class Function(object):

    def __init__(self):
        self.blocks={}
        self.rtn_var=None
        self.rtn_goto=None
        self.rtn_save=None

    def __str__(self):
        return "\n".join(map(str,[b for (m,b) in self.blocks.items()]))

    def register_function(self,cfg):
        for m,b in self.blocks.items():
            b=copy.copy(b)
            b.fun_name=self.name
            b.name=self.name+b.name
            b.parsed=False
            cfg.blocks[b.name]=b
        cfg.functions[self.name]=self

    def get_name(self,tokens):
        self.name=tokens[0]
        self.arglist = []
        n = len(tokens)
        #print("get_arglist: ",line_tokens)
        assert(tokens[1]=='(')
        i = 2
        while i<n:
            t=tokens[i]
            if t=='int' or t=='float':
                self.arglist.append(tokens[i+1])
                i += 2
            elif t==',':
                i += 1
            elif t==')':
                break

    def parse_from(self,lines): # lines is a collections.deque
        is_bb=lambda t:t[0][-1]==':'
        #print("function: {}, lines:{}".format(self.name,lines))
        bbs=list(filter(is_bb,zip(lines,range(len(lines)))))
        bbs=bbs+[(None,-1),] # to deal with the final block
        lines=lines+[[],]
        bn=len(bbs)
        B=[]
        for i in range(bn-1):
            lid,rid=bbs[i][1],bbs[i+1][1]
            tokens=lines[lid]
            assert(tokens[0]=='<' and tokens[-2]=='>' and tokens[-1]==':')
            b=Block("".join(tokens[:-1]))
            b.lines=lines[lid:rid]
            B.append(b)
            #self.blocks[b.name]=b
        for i in range(len(B)-1):
            B[i].natural_goto=B[i+1].name
        for b in B:
            self.blocks[b.name]=b
        self.entry,self.out=B[0].name,B[-1].name
        #self.dfs_parse_block(self.entry)
        #self.replace_if()
        #for (name,b) in self.blocks.items():
        #    print(b,"\n")

class CFGraph(object):

    def __init__(self):
        #self.vars = {}
        #self.csts = {} # constraints
        #self.var_names={}
        self.functions={}
        self.blocks={}
        self.call_cnt={}
        #self.variables={}
        #self.jumps={}
        #self.assignments={}
    def __str__(self):
        return "\n".join(map(str,[b for (m,b) in self.blocks.items()]))
        #return "=================\n".join(map(str,[f for (m,f) in self.functions.items()]))

    def replace_if(self):
        for (name,b) in self.blocks.items():
            b.start_replace_if(self)

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
            self.call_cnt[f.name]=0
        fun=self.functions[entry_function]
        fun.name=""
        fun.register_function(self)
        self.arglist=[fun.name+t for t in fun.arglist]
        self.out=fun.out
        self.blocks[fun.name+fun.entry].DFS_parse(self)
        print("basic parse completed:\n",self)
        self.replace_if()

    def build_cst_graph(self):
        G=CSTGraph()

        for v in self.arglist:
            if not v in G.vars:
                G.vars[v]=Variable(v)
                G.args.append(v)
        for (name,b) in self.blocks.items():
            b.build_cst_graph("",G.vars,G.csts)

        G.rtn_var=self.functions[entry_function].rtn_var

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


