from functools import reduce
from LexicalAnalyzer import *

def not_num(name):
    return not (name[0].isdigit() or name[0] in ('+','-'))

def is_integer(s):
    return s.isdigit() or (s[0]=='-' and s[1:].isdigit())

def smart_turn_number(s):
    return (int(s),"int") if is_integer(s) else (float(s),"float")

def ext_lt(a,b):
    assert '@' not in (a,b)
    if a==b:
        return False
    if a=='-' or b=='+':
        return True
    if a=='+' or b=='-':
        return False
    return a<b

def ext_gt(a,b):
    return ext_lt(b,a)

class Interval:
    def __init__(self,l='-',r='+'):
        if l=='@' or r=='@':
            self.l,self.r='@','@'
            return
        assert not ext_gt(l,r)
        self.l=l
        self.r=r
    def __str__(self):
        s="("
        if self.l in ('+','-','@'):
            s=s+self.l
        else:
            s=s+"{:0.2f}".format(self.l)
        s=s+','
        if self.r in ('+','-','@'):
            s=s+self.r
        else:
            s=s+"{:0.2f}".format(self.r)
        return s+')'
        #return "({:0.2f},{:0.2f})".format(self.l,self.r)


def turn_end(a,t):
    if a in ('@','+','-'):
        return a
    else:
        return int(a) if t=='int' else float(a)

def turn_data(itv,t): # t='int' or 'float'
    assert t in ('int','float')
    return Interval(turn_end(itv.l,t),turn_end(itv.r,t))

def ext_min(a,b): #a,b could be '-','+',or number
    assert '@' not in (a,b)
    if a=='-' or b=='-':
        return '-'
    if a=='+':
        return b
    if b=='+':
        return a
    return min(a,b)

def ext_max(a,b): #a,b could be '-','+',or number
    assert '@' not in (a,b)
    if a=='+' or b=='+':
        return '+'
    if a=='-':
        return b
    if b=='-':
        return a
    return max(a,b)

def ext_min_list(a):
    return reduce(ext_min,a)

def ext_max_list(a):
    return reduce(ext_max,a)

def ext_sgn(a):
    assert a!='@'
    if a=='-':
        return -1
    elif a=='+':
        return +1
    elif a==0:
        return 0
    elif a>0:
        return 1
    elif a<0:
        return -1

def ext_neg(a):
    assert a!='@'
    if a=='-':
        return '+'
    elif a=='+':
        return '-'
    else:
        return -a

def ext_add(a,b):
    assert '@' not in (a,b)
    assert(not ('+' in (a,b) and '-' in (a,b)))
    if '+' in (a,b):
        return '+'
    if '-' in (a,b):
        return '-'
    return a+b
def ext_sub(a,b):
    return ext_add(a,ext_neg(b))

def ext_mul(a,b):
    assert '@' not in (a,b)
    if 0 in (a,b): # note that out inf is not real inf, it's a number
        return 0
    if '+' in (a,b):
        if(b=='+'):
            a,b=b,a
        if ext_sgn(b)<0:
            return '-'
        else:
            return '+'
    if '-' in (a,b):
        if b=='-':
            a,b=b,a
        if ext_sgn(b)<0:
            return '+'
        else:
            return '-'
    return a*b

def phi_union(a,b): #a,b are two intervals, it is specially permitted for phi that a or b could be None
    if a==None or '@' in (a.l,a.r):
        return b
    elif b==None or '@' in (b.l,b.r):
        return a
    return Interval(ext_min(a.l,b.l),ext_max(a.r,b.r))

def cnd_intersect(a,b):
    if '@' in (a.l,a.r,b.l,b.r):
        return Interval('@','@')
    l=ext_max(a.l,b.l)
    r=ext_min(a.r,b.r)
    if ext_gt(l,r):
        return Interval('@','@')
    else:
        return Interval(l,r)

def itv_neg(a):
    if '@' in (a.l,a.r):
        return Interval('@','@')
    l1,r1=ext_neg(a.l),ext_neg(a.r)
    return Interval(ext_min(l1,r1),ext_max(l1,r1))

def itv_inv(a):
    if '@' in (a.l,a.r):
        return Interval('@','@')
    sl,sr=ext_sgn(a.l),ext_sgn(a.r)
    assert(sl*sr!=-1)
    if sl<=0 and sr<=0:
        l1='-' if a.r==0 else 1/a.r
        r1=0 if a.l=='-' else 1/a.l
        return Interval(l1,r1)
    else:
        l1=0 if a.r=='+' else 1/a.r
        r1='+' if a.l==0 else 1/a.l
    return Interval(l1,r1)

def calc_itv(a,b,opt):
    print("calc itv: {} {} {}".format(a,opt,b))
    if '@' in (a.l,a.r,b.l,b.r):
        return Interval('@','@')
    if opt=='+':
        return Interval(ext_add(a.l,b.l),ext_add(a.r,b.r))
    elif opt=='-':
        return calc_itv(a,itv_neg(b),'+')
    elif opt=='*':
        res=[ext_mul(i,j) for i in (a.l,a.r) for j in (b.l,b.r)]
        l,r=ext_min_list(res),ext_max_list(res)
        print("calc itv with *: a={},b={},res={}".format(a,b,Interval(l,r)))
        return Interval(l,r)
    elif opt=='/':
        return calc_itv(a,itv_inv(b),'*')

def widen_itv(a,a1): # return (result,stabled), stabled = True or False
    #print("widen {} to {}".format(a,a1))
    stabled=True
    if a==None:
        return (a1,False)
    assert '@' not in (a.l,a.r,a1.l,a1.r) # widening operation goes first, so cannot have '@'
    if ext_lt(a1.l,a.l):
        l='-'
        stabled=False
    else:
        l=a.l
    if ext_gt(a1.r,a.r):
        r='+'
        stabled=False
    else:
        r=a.r
    return (Interval(l,r),stabled)

def narrow_itv(a,a1): # return (result,stabled), just like widen
    if '@' in (a.l,a.r,a1.l,a1.r):
        it=Interval('@','@')
        if a.l=='@' and a.r=='@':
            return it,True
        else:
            return it,False
    print("narrow interval {} to {}".format(a,a1))
    stabled = True
    # it's after widening, so a cannot be None
    assert(a!=None)
    if ext_gt(a1.l,a.l):
        l=a1.l
        stabled=False
    else:
        l=a.l
    if ext_lt(a1.r,a.r):
        r=a1.r
        stabled=False
    else:
        r=a.r
    return (Interval(l,r),stabled)

class Variable:
    def __init__(self,phi_bname,name,data,itv=None):#itv=interval
        self.typ="VAR"
        self.phi_bname=phi_bname
        self.name=name
        self.itv=itv
        self.to=[]
        self.data=data
    def __str__(self):
        itv_str="None" if self.itv==None else str(self.itv)
        #return "{} in itv {}".format(self.name,itv_str)+"  to=("+",".join(self.to)+")"
        return "{} {} in itv {}".format(self.data,self.name,itv_str)
    def force_data(self):
        self.itv=turn_data(self.itv,self.data)


class SCComponent:

    def __init__(self,name,nodenames):
        self.name=name
        self.nodenames=tuple(nodenames)

    def DFS_propagate(self,x,G,visited,ignore_cnd):#x is a name string, G is the whole constraint graph
        G.propagated.add(x)
        if not x in self.nodenames or x in visited:
            return
        if G[x].typ!="VAR":
            G.propagate_node(x,ignore_cnd)
        visited.add(x)
        for y in G[x].to:
            self.DFS_propagate(y,G,visited,ignore_cnd)

    def save_old_range(self,G):
        for x in self.nodenames:
            p=G[x]
            if p.typ=='VAR':
                p.old_itv=p.itv

    def update_range(self,G,update_fun):
        stabled=True
        for x in self.nodenames:
            p=G[x]
            if p.typ=='VAR':
                I0=p.old_itv
                I1=p.itv
                In,s=update_fun(I0,I1)
                stabled=stabled and s
                p.itv=In
        return stabled


    def select_propagate_start(self,G):
        if len(self.nodenames)==1:
            return self.nodenames[0]
        else:
            #legal_starts=tuple(filter(lambda x:x in G.propagated, self.nodenames))
            legal_starts=tuple(filter(G.ready_to_propagate,self.nodenames))
            assert(len(legal_starts)>0)
            return legal_starts[0]

    def widen_range(self,G,ignore_cnd):
        while True:
            self.save_old_range(G)
            visited=set()
            x=self.select_propagate_start(G)
            self.DFS_propagate(x,G,visited,ignore_cnd)
            if self.update_range(G,widen_itv):
                break

    def select_narrow_start(self,G):
        if len(self.nodenames)==1:
            return self.nodenames[0]
        else:
            legal_starts=tuple(filter(lambda x:G[x].typ=='CND', self.nodenames))
            if len(legal_starts)>0:
                return legal_starts[0]
            else:
                return self.nodenames[0]

    def narrow_range(self,G):
        while True:
            self.save_old_range(G)
            visited=set()
            x=self.select_narrow_start(G)
            self.DFS_propagate(x,G,visited,ignore_cnd=False)
            if self.update_range(G,narrow_itv):
                break

class CSTGraph:
    def __init__(self):
        self.vars={}
        self.csts={}
        self.args=[]
    def __str__(self):
        var_names=[m for (m,v) in self.vars.items()]
        SV="\n".join(str(self.vars[m]) for m in sorted(var_names))
        cst_names=[m for (m,c) in self.csts.items()]
        SC="\n".join(str(self.csts[m]) for m in sorted(cst_names))
        return SV+"\n"+SC
    def __getitem__(self,name):
        if name in self.vars:
            return self.vars[name]
        else:
            return self.csts[name]

    def get_data(self,vname):
        if not_num(vname):
            return self[vname].data
        else:
            return 'int' if is_integer(vname) else 'float'

    def ready_to_propagate(self,x):
        if self[x].typ=='VAR':
            return False
        for op in self[x].ops[:-1]:
            if not_num(op):
                if self[op].typ=='VAR':
                    continue
                if self[op].itv==None:
                    return False
        return True

    def read_arg_bound(self,filename):
        fin=open(filename)
        lines=delete_empty_lines(fin.readlines())
        for t in lines:
            vname,l,r=t.rstrip('\n').split(' ')
            v=self.vars['~'+vname]
            if not l in ('-','+'):
                l=int(l) if v.data=='int' else float(l)
            if not r in ('-','+'):
                r=int(r) if v.data=='int' else float(l)
            v.itv=Interval(l,r)

    def all_cst_names(self):
        return [m for (m,c) in self.csts.items()]

    def all_names(self):
        return [m for (m,v) in self.vars.items()]+[m for (m,c) in self.csts.items()]
    def all_vars(self):
        return [v for (m,v) in self.vars.items()]
    def all_csts(self):
        return [c for (m,c) in self.csts.items()]
    def all_nodes(self):
        return self.all_vars()+self.all_csts()

    def dump_dot(self,filename):
        fout = open(filename,"wt")
        print("digraph g {",file=fout)
        ns=self.all_nodes()
        d={}
        for i in range(len(ns)):
            if ns[i].typ=="VAR":
                shp="ellipse"
            else:
                shp="box"
            print("n{}[shape={},label=\"{}\"]".format(i,shp,ns[i]),file=fout)
            d[ns[i].name]=i
        for x in ns:
            for y in x.to:
                print("n{}->n{}".format(d[x.name],d[y]),file=fout)
        print("}",file=fout)

    def get_itv(self,name):
        if not_num(name):
            return self[name].itv
        else:
            x,numtyp=smart_turn_number(name)
            #assert(numtyp=="int")
            return Interval(x,x)

    """
    TODO: here is a potential bug that if the value range degrades to empty interval what will happen?
    """
    def apply_node_future(self,xname):
        x=self[xname]
        if x.typ!='CND':
            return
        v1,v2,dst=x.ops
        itv1,itv2=self.get_itv(v1),self.get_itv(v2)
        opt=x.opt
        assert(opt in ('==','!=','<','>','<=','>='))
        #print("apply node future: {}".format(x))
        #print("itv1={},itv2={}".format(itv1,itv2))
        if opt=='==':
            itvn=cnd_intersect(itv1,Interval(itv2.l,itv2.r))
        elif opt=='!=':
            itvn=cnd_intersect(itv1,Interval('-','+'))
        elif opt=='<':
            eps = 1 if self.get_data(v2)=='int' else 0
            itvn=cnd_intersect(itv1,Interval('-',ext_sub(itv2.r,eps)))
        elif opt=='<=':
            itvn=cnd_intersect(itv1,Interval('-',itv2.r))
        elif opt=='>':
            eps = 1 if self.get_data(v2)=='int' else 0
            itvn=cnd_intersect(itv1,Interval(ext_add(itv2.l,eps),'+'))
        elif opt=='>=':
            itvn=cnd_intersect(itv1,Interval(itv2.l,'+'))
        self[dst].itv=itvn
        self[dst].force_data()
        #print("after applying, itv of k_1 is {}".format(self["k_1"].itv))

    def apply_future(self):
        for xname in self.all_cst_names():
            self.apply_node_future(xname)

    def propagate_node(self,xname,ignore_cnd):
        x=self[xname]
        print("propagate node {}, typ={}, ops={}".format(xname,x.typ,x.ops))
        if x.typ=="CND":
            v1,v2,dst=x.ops
            #print("propagate CND, v1={},v2={},dst={}".format(v1,v2,dst))
            if ignore_cnd:
                self[dst].itv=self[v1].itv
            else:
                self.apply_node_future(xname)
        elif x.typ=="PHI":
            assert(len(x.ops)==3)
            v1,v2,dst=x.ops
            self[dst].itv=phi_union(self[v1].itv,self[v2].itv)
        elif x.typ=='IST':
            assert(len(x.ops) in (2,3))
            if len(x.ops)==2: # unary
                src,dst=x.ops
                assert(x.opt=='') # no operator, just like a=b
                I=self.get_itv(src)
                self[dst].itv=I
            else: # binary
                src1,src2,dst=x.ops
                it1,it2=self.get_itv(src1),self.get_itv(src2)
                print("propagate binary IST, it1={}, it2={}".format(it1,it2))
                self[dst].itv=calc_itv(it1,it2,x.opt)
        else:
            assert(x.typ=='VAR')
        self[dst].force_data()
        print("afterwhile: {} in {}".format(dst,self[dst].itv))

    def mark_indeg(self):
        for p in self.all_nodes():
            p.indeg=0
        for p in self.all_nodes():
            for y in p.to:
                self[y].indeg+=1

    def apply_unary(self):
        self.mark_indeg()
        self.pure_innodes=tuple(filter(lambda t:t.indeg==0,self.all_nodes()))
        for p in self.pure_innodes:
            print("pure innode: ",p.name)
            assert(p.typ=="IST" or p.name in self.args) # unary assignments

    def Tarjan(self,u): # u is a name
        self.time_stamp+=1
        self.dfn[u],self.low[u]=self.time_stamp,self.time_stamp
        self.S.append(u)
        for v in self[u].to:
            if not v in self.dfn:
                self.Tarjan(v)
                self.low[u]=min(self.low[u],self.low[v])
            elif v in self.S:
                self.low[u]=min(self.low[u],self.dfn[v])
        if self.dfn[u]==self.low[u]:
            k=self.S.index(u)
            c=SCComponent(str(len(self.sccs)+1),self.S[k:])
            self.S=self.S[:k]
            self.sccs.append(c)

    def get_SCC(self):
        self.time_stamp=0
        self.dfn,self.low={},{}
        self.S,self.sccs=[],[]
        for p in self.pure_innodes:
            self.Tarjan(p.name)
        self.sccs=self.sccs[::-1]

    def widen_along_sccs(self):
        n=len(self.sccs)
        for i in range(n):
            self.sccs[i].widen_range(self,ignore_cnd=True)

    def narrow_along_sccs(self):
        n=len(self.sccs)
        for i in range(n):
            self.sccs[i].narrow_range(self)

    def analyze(self):
        self.apply_unary()
        self.get_SCC()
        for i in range(len(self.sccs)):
            print(self.sccs[i].nodenames)
        self.propagated=set()
        self.widen_along_sccs()
        print("applying future:")
        self.apply_future()
        print("narrowing:")
        self.narrow_along_sccs()
        for v in self.all_vars():
            print("{} now bound {}".format(v.name,v.itv))
        rtv=self.vars[self.rtn_var].itv
        print("result: [{},{}]".format(rtv.l,rtv.r))
        self.dump_dot("/home/cstdio/log.txt")
