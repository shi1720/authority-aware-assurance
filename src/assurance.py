"""Offline, finite-family assurance compiler. Not a hardware verifier."""
from itertools import combinations

def subsets(n):
    return range(1 << n)

def contained(a, b):
    return a & b == a

def antichain(family, minimal=True):
    f = set(family)
    return sorted(x for x in f if not any(x != y and (contained(y,x) if minimal else contained(x,y)) for y in f))

def compile_rule(bad, live):
    """Return minimal live clauses, or an exact impossibility witness."""
    bad = antichain(bad, minimal=False)
    live = antichain(live)
    for t in live:
        for b in bad:
            if contained(t,b):
                return {'feasible': False, 'witness': {'live': t, 'bad': b}, 'clauses': []}
    return {'feasible': True, 'witness': None, 'clauses': live}

def accepts(rule, signers):
    return rule['feasible'] and any(contained(t,signers) for t in rule['clauses'])

def thresholds(bad, live, n):
    lo = max(map(int.bit_count,bad),default=0)+1
    hi = min(map(int.bit_count,live),default=0)
    return list(range(max(1,lo),min(n,hi)+1))

def closure(dependencies, authority_mask):
    return sum(1<<i for i,d in enumerate(dependencies) if d & authority_mask)

def threat_families(capture, denial, authority_count, capture_budget=1, denial_budget=1):
    n = len(capture)
    bad = [closure(capture,a) for a in subsets(authority_count) if a.bit_count()<=capture_budget]
    live = [((1<<n)-1)^closure(denial,a) for a in subsets(authority_count) if a.bit_count()<=denial_budget]
    return bad,live

def project(family, selected):
    return [x & selected for x in family]

def cheapest_portfolio(bad,live,costs,kind='general'):
    candidates=[]
    n=len(costs)
    for s in range(1,1<<n):
        b,t=project(bad,s),project(live,s)
        rule=compile_rule(b,t)
        q=thresholds(b,t,n)
        ok=rule['feasible'] if kind=='general' else bool(q)
        if ok:candidates.append((sum(costs[i] for i in range(n) if s>>i&1),s,rule,q))
    return min(candidates,key=lambda x:(x[0],x[1])) if candidates else None
