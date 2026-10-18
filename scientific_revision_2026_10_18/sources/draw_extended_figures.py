from pathlib import Path

root=Path(__file__).resolve().parent
source=(root/'draw_fold_safe_figures.py').read_text(encoding='utf-8')
source=source.replace("/'fold_safe_revision_2026_10_12'","/'extended_revision_2026_10_12'")
source=source.replace('Selected in n of 9 masks','Selected in n of 15 masks').replace('xlim=(0,9.7)','xlim=(0,15.7)').replace('[0,3,6,9]','[0,5,10,15]')
source=source.replace('axs[0].set_ylim(.778,.7985)',"spread=max(.002,float(mean.balanced_accuracy.max()-mean.balanced_accuracy.min())); axs[0].set_ylim(float(mean.balanced_accuracy.min())-.12*spread,float(mean.balanced_accuracy.max())+.18*spread)")
exec(compile(source,'extended_scientific_figures','exec'))
