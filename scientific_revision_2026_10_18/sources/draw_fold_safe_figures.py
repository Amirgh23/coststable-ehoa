from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
OUT=Path(__file__).resolve().parent/'fold_safe_revision_2026_10_12'
(OUT/'figures').mkdir(exist_ok=True)
M=['EHOA','random','cheapest','mi','stable_lcb']
L=['EHOA','Random/cost','Cheapest','MI/cost','Resamp./cost']
mean=pd.read_csv(OUT/'analysis/primary_overall.csv').set_index('method').loc[M]
freq=pd.read_csv(OUT/'analysis/breast_selection_frequencies.csv')
top=freq[freq.method=='stable_lcb'].sort_values(['selected_count','feature'],ascending=[False,True]).head(8)
colors=['#505050','#b48125','#387e67','#356ba7','#9a3758']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(2,1,figsize=(3.35,2.6))
for i,m in enumerate(M):
    axs[0].scatter(mean.loc[m,'cost_ratio'],mean.loc[m,'balanced_accuracy'],color=colors[i],s=26)
    offset=[(4,4),(4,4),(-12,4),(14,4),(14,-9)][i]
    axs[0].annotate(str(i+1),(mean.loc[m,'cost_ratio'],mean.loc[m,'balanced_accuracy']),xytext=offset,textcoords='offset points',fontsize=6,arrowprops={'arrowstyle':'-','lw':.4,'color':colors[i]} if i in [2,3,4] else None)
axs[0].axvline(.3,ls='--',color='gray',lw=.5)
axs[0].set(xlabel='Selected / total synthetic cost',ylabel='Balanced accuracy')
axs[0].set_ylim(.778,.7985)
axs[0].text(.98,.03,'1 EHOA; 2 Random; 3 Cheapest\n4 MI; 5 Resampled',transform=axs[0].transAxes,ha='right',fontsize=5.5)
axs[1].barh(L,mean.nogueira_stability,color=colors)
axs[1].set(xlabel='Nogueira stability')
axs[1].tick_params(axis='y',labelsize=6)
fig.tight_layout(pad=.3,h_pad=1)
for ext in ['pdf','svg','png']:fig.savefig(OUT/f'figures/eligible_comparison.{ext}',dpi=500,bbox_inches='tight',pad_inches=.08)
plt.close(fig)
fig,ax=plt.subplots(figsize=(3.35,1.65))
plot=top.sort_values('selected_count')
ax.barh(plot.feature,plot.selected_count,color=colors[-1])
ax.set(xlabel='Selected in n of 9 masks',xlim=(0,9.7))
ax.set_xticks([0,3,6,9])
ax.tick_params(axis='y',labelsize=6)
fig.tight_layout(pad=.3)
for ext in ['pdf','svg','png']:fig.savefig(OUT/f'figures/breast_top_frequencies.{ext}',dpi=500,bbox_inches='tight',pad_inches=.08)
plt.close(fig)
for stem in ['eligible_comparison','breast_top_frequencies']:Image.open(OUT/f'figures/{stem}.png').save(OUT/f'figures/{stem}.tiff',compression='tiff_lzw',dpi=(500,500))
