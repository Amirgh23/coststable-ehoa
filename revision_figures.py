from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
P=Path(__file__).resolve().parent/'revision_2026_10_12'
M=['EHOA','Budget-random','Budget-cheapest','Budget-mi','Budget-stable_lcb']
L=['EHOA','Random/cost','Cheapest','MI/cost','Resamp./cost']
C=['#505050','#b48125','#387e67','#356ba7','#9a3758']
a=pd.read_csv(P/'analysis/eligible_overall.csv').set_index('method').loc[M]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(2,1,figsize=(3.35,2.6),gridspec_kw={'height_ratios':[1,1]})
for i,m in enumerate(M):
    axs[0].scatter(a.loc[m,'cost_ratio'],a.loc[m,'balanced_accuracy'],s=28,color=C[i])
    offset=[(4,0),(4,-2),(14,-13),(30,-3),(8,8)][i]
    axs[0].annotate(L[i],(a.loc[m,'cost_ratio'],a.loc[m,'balanced_accuracy']),xytext=offset,textcoords='offset points',fontsize=5.5,arrowprops={'arrowstyle':'-','lw':.4,'color':C[i]} if i in [2,3,4] else None)
axs[0].axvline(.3,color='gray',ls='--',lw=.5);axs[0].set(xlabel='Selected / total synthetic cost',ylabel='Balanced accuracy',xlim=(.25,.6),ylim=(.802,.815))
axs[1].barh(L,a.nogueira_stability,color=C);axs[1].set(xlabel='Nogueira stability',xlim=(0,.31));axs[1].tick_params(axis='y',labelsize=6)
fig.tight_layout(pad=.3,h_pad=1)
for ext in ['pdf','svg','png']:fig.savefig(P/f'figures/eligible_comparison.{ext}',dpi=500,bbox_inches='tight',pad_inches=.08)
plt.close(fig)
f=pd.read_csv(P/'analysis/selection_frequencies.csv');f=f[(f.dataset=='breast_cancer')&(f.method=='Budget-stable_lcb')].sort_values(['selected_count','feature'],ascending=[False,True]).head(8).sort_values('selected_count')
fig,ax=plt.subplots(figsize=(3.35,1.65));ax.barh(f.feature,f.selected_count,color=C[-1]);ax.set(xlabel='Selected in n of 6 masks',xlim=(0,6.7));ax.set_xticks(range(7));ax.tick_params(axis='y',labelsize=6);fig.tight_layout(pad=.3)
for ext in ['pdf','svg','png']:fig.savefig(P/f'figures/breast_top_frequencies.{ext}',dpi=500,bbox_inches='tight',pad_inches=.08)
plt.close(fig)
for name in ['eligible_comparison','breast_top_frequencies']:
    Image.open(P/f'figures/{name}.png').save(P/f'figures/{name}.tiff',compression='tiff_lzw',dpi=(500,500))
print('Figures regenerated from audited eight-dataset means and stored masks.')
