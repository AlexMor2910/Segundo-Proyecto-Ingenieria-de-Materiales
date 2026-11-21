"""Calculate descriptive 95% t intervals without changing verified inference."""
import hashlib
import json
import math
from pathlib import Path

import pandas as pd
import scipy
from scipy.stats import t

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / 'data' / 'steels.csv'
VERIFIED = ROOT / 'data' / 'statistical-results.json'
OUTPUT = ROOT / 'data' / 'mean-ci.json'

def main():
    digest = hashlib.sha256(CSV.read_bytes()).hexdigest()
    verified = json.loads(VERIFIED.read_text(encoding='utf-8'))
    if digest != verified['metadata']['input_sha256']:
        raise ValueError('La base no coincide con los resultados inferenciales verificados.')
    data = pd.read_csv(CSV, dtype={'SAE Grade': str})
    series = data['SAE Grade'].str.zfill(4).str[0]
    def mechanical(row):
        m, h = row['Mechanical Conditions'], row['Heat Treatment']
        if m == 'Cold drawn' and h == 'Annealed': return 'Cold drawn + Annealed'
        if m in ('Hot rolled', 'Cold drawn'): return m
        return None
    data['group1'] = data.apply(mechanical, axis=1)
    populations = {
        '1xxx': (data[(series == '1') & data['group1'].notna()], 'group1'),
        'other': (data[(series != '1') & data['Heat Treatment'].isin(['Annealed', 'Normalized', 'Quenched and tempered'])], 'Heat Treatment')
    }
    intervals = []
    for reference in verified['groups']:
        frame, column = populations[reference['mode']]
        values = frame.loc[frame[column] == reference['group'], reference['property']].dropna()
        n = len(values)
        if n != reference['n'] or not math.isclose(values.mean(), reference['mean'], rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError('Los registros no coinciden con las medias verificadas.')
        mean = float(values.mean())
        margin = float(t.ppf(.975, n - 1) * values.std(ddof=1) / math.sqrt(n)) if n > 1 else None
        intervals.append({'mode': reference['mode'], 'property': reference['property'], 'group': reference['group'], 'n': n, 'mean': mean, 'low': mean-margin if margin is not None else None, 'high': mean+margin if margin is not None else None})
    result = {'input_sha256': digest, 'method': 'mean ± t(0.975, n − 1) × sample standard deviation / √n', 'confidence': .95, 'scipy': scipy.__version__, 'groups': intervals}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    print(f'{len(intervals)} intervalos descriptivos guardados en {OUTPUT.relative_to(ROOT)}')

if __name__ == '__main__': main()
