"""Run the unmodified research scripts in a temporary directory and export results."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import matplotlib
import numpy as np
import pandas as pd
import scipy
import statsmodels
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.oneway import anova_oneway

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'steels.csv'
OUTPUT = ROOT / 'verification' / 'results'
PROPERTIES = ['UTS (MPa)', 'YS (MPa)', 'Hardness (HB)', 'Elongation (%)']

def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating, float)): return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_,)): return bool(value)
    return value

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='steel-verification-') as temp:
        folder = Path(temp)
        shutil.copyfile(INPUT, folder / 'Cleansed_Treatment_Carbon_Steel_Summary_Fixed.csv')
        env = dict(os.environ, MPLBACKEND='Agg', MPLCONFIGDIR=str(folder / 'mpl'))
        for name in ['2.6_Tratamiento_4.py', '2.7_Tratamiento_4.py']:
            script = ROOT / 'python' / 'tratamiento' / name
            run = subprocess.run([sys.executable, str(script)], cwd=folder, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
            (OUTPUT / (name + '.log')).write_text(run.stdout + '\n' + run.stderr, encoding='utf-8')
            if run.returncode: raise RuntimeError(f'{name} failed; see verification/results/{name}.log')
        generated = folder / 'Resultados_ANOVA'
        anovas = []
        for filename, mode in [('ANOVA_Serie_1XXX.csv','1xxx'),('ANOVA_Otras_Series.csv','other')]:
            frame = pd.read_csv(generated / filename)
            for row in frame.to_dict(orient='records'): anovas.append(dict(row, mode=mode))
        data = pd.read_csv(INPUT)
        main_series = data['SAE Grade'].astype(str).str.zfill(4).str[0]
        def group(row):
            if row['Mechanical Conditions']=='Cold drawn' and row['Heat Treatment']=='Annealed': return 'Cold drawn + Annealed'
            if row['Mechanical Conditions'] in ['Hot rolled','Cold drawn']: return row['Mechanical Conditions']
            return None
        data['group1'] = data.apply(group, axis=1)
        populations = {'1xxx':data[(main_series=='1') & data['group1'].notna()].copy(), 'other':data[(main_series!='1') & data['Heat Treatment'].isin(['Annealed','Normalized','Quenched and tempered'])].copy()}
        summaries=[]; tukey=[]
        for mode, frame in populations.items():
            group_column = 'group1' if mode=='1xxx' else 'Heat Treatment'
            for prop in PROPERTIES:
                subset=frame[[group_column,prop]].dropna()
                grouped=[g[prop].to_numpy() for _,g in subset.groupby(group_column) if len(g)>=2]
                welch=anova_oneway(grouped,use_var='unequal')
                for row in anovas:
                    if row['mode']==mode and row['Property']==prop: row.update({'Welch df numerator':welch.df_num,'Welch df denominator':welch.df_denom,'Conventional df numerator':len(grouped)-1,'Conventional df denominator':sum(map(len,grouped))-len(grouped)})
                for name, group_data in subset.groupby(group_column):
                    vals=group_data[prop]; summaries.append({'mode':mode,'property':prop,'group':name,'n':len(vals),'mean':vals.mean(),'variance':vals.var(ddof=1)})
                if mode=='other' and prop!='YS (MPa)':
                    test=pairwise_tukeyhsd(subset[prop],subset[group_column],alpha=.05)
                    a,b=test._multicomp.pairindices
                    for i,(left,right) in enumerate(zip(a,b)):
                        tukey.append({'mode':mode,'property':prop,'group1':str(test.groupsunique[left]),'group2':str(test.groupsunique[right]),'mean_difference':test.meandiffs[i],'p_adjusted':test.pvalues[i],'ci_low':test.confint[i][0],'ci_high':test.confint[i][1]})
        games=[]
        for filename, mode in [('Games_Howell_1XXX.csv','1xxx'),('Games_Howell_Otras_Series_YS.csv','other')]:
            games.extend(dict(row,mode=mode) for row in pd.read_csv(generated / 'Games_Howell' / filename).to_dict(orient='records'))
        metadata={'python':sys.version.split()[0], 'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'statsmodels':statsmodels.__version__,'matplotlib':matplotlib.__version__,'input_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),'scope':'Fixed original processing populations; no interactive subset filtering.'}
        result=clean({'metadata':metadata,'groups':summaries,'anova':anovas,'tukey':tukey,'games_howell':games})
        (OUTPUT / 'statistical-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
        print(json.dumps(metadata,indent=2)); print('ANOVA rows:',len(anovas),'Tukey:',len(tukey),'Games–Howell:',len(games))
if __name__=='__main__': main()
