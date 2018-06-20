class Interval:
    def __init__(self,l='-',r='+'):
        if(l!='-' and r!='+'):
            assert(l<=r)
        self.l=l
        self.r=r

class Variable:
    def __init__(self,name,itv):#itv=interval
        self.name=name
        self.itv=itv

class Affine: # something like: tgt=a*src + (b and itv)
    def __init__(self,src,tgt,a=0,b=1,itv=Interval('-','+')):
        self.src=src
        self.tgt=tgt
        self.a=a
        self.b=b
        self.itv=itv

class Plus: # tgt=src1+src2
    def __init__(self,src1,src2,tgt):
        self.src1=src1
        self.src2=src2
        self.tgt=tgt

class Phi: # tgt=phi(src1,src2)
    def __init__(self,src,src2,tgt):
        self.src1=src
        self.src2=src2
        self.tgt=tgt

class CGraph:
    def __init__(self):
        self.vars={}
        self.ops={}
