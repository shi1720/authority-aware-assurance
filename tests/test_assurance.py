import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from assurance import *

def test_rectangular_rule():
 r=compile_rule([3,12],[5,10]);assert r['feasible']
 assert accepts(r,5) and accepts(r,10)
 assert not accepts(r,3) and not accepts(r,12)
 assert thresholds([3,12],[5,10],4)==[]

def test_empty_live_impossible():
 assert not compile_rule([0],[0])['feasible']

def test_common_evidence_impossible():
 assert not compile_rule([15],[5,10])['feasible']

def test_portfolio_projection_rejects_lost_paths():
 assert cheapest_portfolio([3,12],[5,10],[1]*4)[0]==4
 assert cheapest_portfolio([3,12],[5,10],[1]*4,'threshold') is None

def test_antichain_reduction():
 assert antichain([1,3,5,7])==[1]
 assert antichain([1,3,5,7],False)==[7]

def test_monotone_all_masks():
 r=compile_rule([3,12],[5,10])
 for s in range(16):
  for t in range(16):
   if contained(s,t) and accepts(r,s):assert accepts(r,t)

def test_weighted_impossibility_and_positive_control():
 from weighted import weighted_rule
 assert weighted_rule([3,12],[5,10],4) is None
 assert weighted_rule([1,2,4],[3,5,6],3) is not None

def test_simultaneous_threat_requires_third_supplier():
 from experiments import grid
 for v,expected in [(2,False),(3,True)]:
  c,d,a=grid(v,2);b,t=threat_families(c,d,a)
  assert compile_rule(b,[x & ~y for x in t for y in b])['feasible']==expected
