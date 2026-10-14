"""Nonnegative weighted-rule feasibility via linear programming.
Acceptance is sum(weights of signers) >= threshold. Unit strict-rejection
margin is wlog for a finite feasible strict-separation problem, by scaling.
"""
import numpy as np
from scipy.optimize import linprog

def weighted_rule(bad,live,n):
    def row(s):return [int(s>>i&1) for i in range(n)]
    A=[row(s)+[-1] for s in bad]+[[-x for x in row(s)]+[1] for s in live]
    rhs=[-1]*len(bad)+[0]*len(live)
    res=linprog([0]*(n+1),A_ub=A,b_ub=rhs,bounds=[(0,None)]*(n+1),method='highs')
    if not res.success:
        if res.status!=2:raise RuntimeError(res.message)
        return None
    weights=res.x[:n];threshold=res.x[n]
    assert max((sum(weights[i] for i in range(n) if s>>i&1)-threshold for s in bad),default=-1)<=-1+1e-7
    assert min((sum(weights[i] for i in range(n) if s>>i&1)-threshold for s in live),default=0)>=-1e-7
    return {'weights':weights.tolist(),'threshold':float(threshold)}

def infeasibility_certificate(bad,live,n):
    """Exact rational convex-combination witness against nonnegative weights.
    E_bad[incidence] >= E_live[incidence], with each mixture summing to one.
    Strict bad rejection then contradicts live acceptance at any threshold.
    """
    from fractions import Fraction
    rows=lambda masks: np.array([[int(s>>i&1) for s in masks] for i in range(n)],dtype=float)
    A=np.concatenate([-rows(bad),rows(live)],axis=1)
    equal=np.zeros((2,len(bad)+len(live)));equal[0,:len(bad)]=1;equal[1,len(bad):]=1
    res=linprog([0]*(len(bad)+len(live)),A_ub=A,b_ub=np.zeros(n),A_eq=equal,b_eq=[1,1],bounds=(0,None),method='highs')
    if not res.success:raise RuntimeError('No weighted infeasibility witness')
    coeff=[Fraction(float(x)).limit_denominator(100000) for x in res.x]
    pb=coeff[:len(bad)];pt=coeff[len(bad):]
    assert sum(pb)==sum(pt)==1 and all(x>=0 for x in coeff)
    differences=[sum(w for w,s in zip(pb,bad) if s>>i&1)-sum(w for w,s in zip(pt,live) if s>>i&1) for i in range(n)]
    assert all(x>=0 for x in differences)
    return {'bad_mixture':[[s,str(w)] for s,w in zip(bad,pb) if w],'live_mixture':[[s,str(w)] for s,w in zip(live,pt) if w],'coordinate_differences':[str(x) for x in differences]}
