class Interval:
    def __init__(self,l='-',r='+'):
        if(l!='-' and r!='+'):
            assert(l<=r)
        self.l=l
        self.r=r
    def __str__(self):
        return "({},{})".format(self.l,self.r)

class Variable:
    def __init__(self,name,itv=Interval()):#itv=interval
        self.name=name
        self.itv=itv
        self.to=[]
    def __str__(self):
        return "{} in itv {}".format(self.name,self.itv)+"  to=("+",".join(self.to)+")"

class SCComponent:
    def __init__(self,name,nodenames):
        self.name=name
        self.nodenames=tuple(nodenames)

class CSTGraph:
    def __init__(self):
        self.vars={}
        self.csts={}
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
    def all_names(self):
        return [m for (m,v) in self.vars.items()]+[m for (m,c) in self.csts.items()]
    def all_vars(self):
        return [v for (m,v) in self.vars.items()]
    def all_csts(self):
        return [c for (m,c) in self.csts.items()]
    def all_nodes(self):
        return self.all_vars()+self.all_csts()
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
            assert(p.typ=="IST") # unary assignments
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
    
    def analyze(self):
        self.apply_unary()
        self.get_SCC()
        for c in self.sccs:
            print(c.nodenames)
