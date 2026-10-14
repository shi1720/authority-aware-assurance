import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
R=Path(__file__).resolve().parents[1];summary=json.loads((R/'results/summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
blue='#234E70';red='#AD3D40';green='#2B7367'
def save(fig,name):
 fig.savefig(R/'figures'/f'{name}.pdf',bbox_inches='tight');fig.savefig(R/'figures'/f'{name}.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(7.1,3.5));ax.set_xlim(-.8,2.6);ax.set_ylim(-.7,2.6);ax.axis('off')
for v in range(2):
 for s in range(2):
  x=s*1.7;y=1.8-v*1.3
  ax.add_patch(FancyBboxPatch((x-.5,y-.3),1,.6,boxstyle='round,pad=.07',fc='#EDF3F6',ec=blue,lw=1.5))
  ax.text(x,y,f'{chr(65+v)}{s+1}',ha='center',va='center',fontweight='bold',fontsize=13)
ax.text(.85,2.4,'Jurisdiction 1                  Jurisdiction 2',ha='center',color=blue)
ax.text(-.65,1.8,'Supplier A',ha='right',va='center',color=red)
ax.text(-.65,.5,'Supplier B',ha='right',va='center',color=red)
ax.plot([-.48,2.18],[1.35,1.35],ls='--',color=red,alpha=.6)
ax.text(.85,-.05,'Capture: either supplier row can approve a false claim',ha='center',color=red,fontsize=9)
ax.text(.85,-.4,'Withdrawal: either jurisdiction column can stop responding',ha='center',color=blue,fontsize=9)
save(fig,'crossed_authorities')
fig,axes=plt.subplots(1,2,figsize=(7.2,3.0),gridspec_kw={'width_ratios':[1.1,1]})
qs=np.arange(1,5);axes[0].plot(qs,[1,1,0,0],'o-',color=red,label='False approval possible');axes[0].plot(qs,[1,1,0,0],'s--',color=blue,label='Valid approval available')
axes[0].set_xticks(qs);axes[0].set_yticks([0,1],['No','Yes']);axes[0].set_xlabel('Number of signatures required');axes[0].set_title('Every scalar threshold fails one goal',fontsize=10);axes[0].legend(fontsize=8,loc='center left')
labels=['Supplier A\nonly','Supplier B\nonly','Jurisdiction 1\nsurvives','Jurisdiction 2\nsurvives'];vals=[0,0,1,1]
axes[1].bar(range(4),vals,color=[red,red,green,green]);axes[1].set_xticks(range(4),labels,fontsize=8);axes[1].set_ylim(0,1.2);axes[1].set_yticks([0,1],['Reject','Accept']);axes[1].set_title('Typed rule: (A1 AND B1) OR (A2 AND B2)',fontsize=9)
fig.tight_layout();save(fig,'rule_comparison')
fig,ax=plt.subplots(figsize=(6.4,3.6))
values=np.zeros((4,4))
for x in summary['grid']:values[x['vendors']-2,x['sites']-2]=len(x['thresholds'])
im=ax.imshow(values,cmap='Blues',vmin=0,vmax=15)
for i in range(4):
 for j in range(4):ax.text(j,i,str(int(values[i,j])),ha='center',va='center',color='white' if values[i,j]>8 else blue)
ax.set_xticks(range(4),range(2,6));ax.set_yticks(range(4),range(2,6));ax.set_xlabel('Independent jurisdiction columns');ax.set_ylabel('Independent supplier rows');ax.set_title('Feasible scalar thresholds; typed rule feasible in all 16 grids',fontsize=10)
fig.colorbar(im,ax=ax,label='Number of feasible thresholds');fig.tight_layout();save(fig,'grid_frontier')
