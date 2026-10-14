"""Exhaustive specification check plus declared scenario comparisons."""
import itertools,json,random
from pathlib import Path
from assurance import *
from weighted import weighted_rule,infeasibility_certificate
ROOT=Path(__file__).resolve().parents[1]

def oracle(bad,live,n):
    # Independent direct constraints on Boolean functions; no compiler call.
    forced0={s for s in range(1<<n) if any(s & b == s for b in bad)}
    forced1={s for s in range(1<<n) if any(s & t == t for t in live)}
    return not (forced0 & forced1), forced0, forced1

def monotone_functions(n):
    out=[]
    for truth in range(1<<(1<<n)):
      if all(not(truth>>s&1) or (truth>>t&1) for s in range(1<<n) for t in range(1<<n) if s&t==s):out.append(truth)
    return out

def verify():
    cases=decisions=0
    for n in range(1,4):
      functions=monotone_functions(n)
      # All independent assignments of nonempty denial/capture sets over 2 authorities.
      for tup in itertools.product(range(1,4),repeat=2*n):
       c,d=tup[:n],tup[n:]
       for cb in range(3):
        for db in range(3):
         b,t=threat_families(c,d,2,cb,db);r=compile_rule(b,t)
         possible,z,o=oracle(b,t,n)
         brute=any(all(not(truth>>s&1) for s in z) and all(truth>>s&1 for s in o) for truth in functions)
         assert r['feasible']==possible==brute
         if possible:
          for s in range(1<<n):
           actual=accepts(r,s);assert actual==(s in o)
           assert not(actual and s in z);decisions+=1
         else:
          w=r['witness'];assert w['live']&w['bad']==w['live']
         qs=thresholds(b,t,n)
         direct=[q for q in range(1,n+1) if all(x.bit_count()<q for x in z) and all(x.bit_count()>=q for x in o)]
         assert qs==direct;cases+=1
    return {'cases':cases,'compiled_decisions_checked':decisions,'mismatches':0}

def grid(vendors,sites,shared=False):
    n=vendors*sites
    # Split authority indices: vendor compromise vs site denial.
    c=[1<<v for v in range(vendors) for s in range(sites)]
    d=[1<<(vendors+s) for v in range(vendors) for s in range(sites)]
    if shared:c=[x | (1<<(vendors+sites)) for x in c];d=[x | (1<<(vendors+sites)) for x in d]
    return c,d,vendors+sites+int(shared)

def run():
    result={'verification':verify(),'grid':[],'random':{},'canonical':{}}
    for v in range(2,6):
     for s in range(2,6):
      c,d,a=grid(v,s);b,t=threat_families(c,d,a)
      r=compile_rule(b,t)
      result['grid'].append({'vendors':v,'sites':s,'n':v*s,'general':r['feasible'],'thresholds':thresholds(b,t,v*s),'clauses':len(r['clauses'])})
    c,d,a=grid(2,2);b,t=threat_families(c,d,a);r=compile_rule(b,t)
    assert weighted_rule(b,t,4) is None
    result['canonical']={'capture':c,'denial':d,'bad':antichain(b,False),'live':antichain(t),'rule':r,'thresholds':thresholds(b,t,4)}
    costs=[1,1,1,1]
    result['canonical']['cheapest_general']=cheapest_portfolio(b,t,costs)
    result['canonical']['weighted_infeasibility_certificate']=infeasibility_certificate(b,t,4)
    result['canonical']['cheapest_threshold']=cheapest_portfolio(b,t,costs,'threshold')
    rng=random.Random(20261014);counts={'neither':0,'general_only':0,'both':0};records=[]
    # Synthetic, nonrepresentative population. Two independently sampled dependencies per node.
    for j in range(2000):
      n=6;a=5;c=[rng.randrange(1,1<<a) for _ in range(n)];d=[rng.randrange(1,1<<a) for _ in range(n)]
      b,t=threat_families(c,d,a);r=compile_rule(b,t);qs=thresholds(b,t,n)
      possible,z,o=oracle(b,t,n);assert possible==r['feasible']
      category='both' if qs else 'general_only' if possible else 'neither';counts[category]+=1
      records.append({'id':j,'capture':c,'denial':d,'category':category,'clauses':r['clauses'],'witness':r['witness']})
    for record in records:
      if record['category']=='general_only':
        b,t=threat_families(record['capture'],record['denial'],5)
        record['weighted_rule']=weighted_rule(b,t,6)
        if record['weighted_rule'] is None:record['weighted_infeasibility_certificate']=infeasibility_certificate(b,t,6)
    result['random']={'seed':20261014,'n':6,'authorities':5,'samples':2000,'counts':counts}
    result['random']['weighted_feasible_among_general_only']=sum(x.get('weighted_rule') is not None for x in records if x['category']=='general_only')
    grid_cases=grid_mismatch=0;grid_budget_rows=[]
    for v in range(2,6):
     for s in range(2,6):
      for cb in range(1,v):
       for db in range(1,s):
        c,d,a=grid(v,s);bad=[closure(c,x) for x in subsets(v) if x.bit_count()<=cb];live=[((1<<(v*s))-1)^closure(d,x<<v) for x in subsets(s) if x.bit_count()<=db]
        for joint in [False,True]:
         l=[t & ~b for t in live for b in bad] if joint else live
         rule=compile_rule(bad,l);expected=(v>2*cb if joint else v>cb) and s>db
         assert rule['feasible']==expected;grid_cases+=1
         qs=thresholds(bad,l,v*s)
         expected_q=list(range(cb*s+1, ((v-cb) if joint else v)*(s-db)+1))
         assert qs==expected_q
         grid_budget_rows.append({'vendors':v,'sites':s,'capture_budget':cb,'denial_budget':db,'simultaneous':joint,'general_feasible':expected,'thresholds':qs})
    result['grid_budget_verification']={'cases':grid_cases,'mismatches':grid_mismatch}
    (ROOT/'results'/'grid_budgets.json').write_text(json.dumps(grid_budget_rows,indent=2)+'\n')
    # Shared authority sensitivity and simultaneous capture+withdrawal.
    c,d,a=grid(2,2,True);b,t=threat_families(c,d,a);result['common_authority']=compile_rule(b,t)
    c,d,a=grid(2,2);b,t=threat_families(c,d,a)
    joint=[l & ~f for l in t for f in b]
    result['simultaneous_2x2']=compile_rule(b,joint)
    c,d,a=grid(3,2);b,t=threat_families(c,d,a);joint=[l & ~f for l in t for f in b]
    result['simultaneous_3x2']=compile_rule(b,joint)
    (ROOT/'results'/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'results'/'synthetic_cases.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':run()
