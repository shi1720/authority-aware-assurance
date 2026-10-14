"""Compile a named finite scenario file into a reviewable JSON receipt."""
import argparse,json
from assurance import compile_rule,thresholds,cheapest_portfolio
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('scenario');args=parser.parse_args()
data=json.load(open(args.scenario));paths=data['paths']
if len(set(paths))!=len(paths) or not paths:raise ValueError('Path names must be nonempty and unique')
if not data['bad'] or not data['live']:raise ValueError('Both scenario families must be nonempty')
def encode(group):
 if not set(group)<=set(paths):raise ValueError('Unknown path identity')
 return sum(1<<paths.index(x) for x in set(group))
def decode(mask):return [name for i,name in enumerate(paths) if mask>>i&1]
b=[encode(x) for x in data['bad']];t=[encode(x) for x in data['live']]
r=compile_rule(b,t)
receipt={'claim':data['claim'],'scope':data['scope'],'feasible':r['feasible'],'clauses':[decode(x) for x in r['clauses']],'thresholds':thresholds(b,t,len(paths)),'witness':{k:decode(v) for k,v in r['witness'].items()} if r['witness'] else None}
print(json.dumps(receipt,indent=2))
