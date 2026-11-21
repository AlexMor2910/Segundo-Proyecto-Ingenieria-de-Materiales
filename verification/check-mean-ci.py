"""Independently check the stored t intervals using csv and statistics."""
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from scipy.stats import t

root = Path(__file__).resolve().parents[1]
path = root / 'data/steels.csv'
intervals = json.loads((root / 'data/mean-ci.json').read_text(encoding='utf-8'))
assert intervals['input_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
with path.open(encoding='utf-8-sig', newline='') as file:
    records = list(csv.DictReader(file))
for row in intervals['groups']:
    values = []
    for r in records:
        main = r['SAE Grade'].zfill(4)[0]
        if (main == '1') != (row['mode'] == '1xxx'): continue
        m, h = r['Mechanical Conditions'], r['Heat Treatment']
        group = ('Cold drawn + Annealed' if m == 'Cold drawn' and h == 'Annealed' else m if m in ('Hot rolled', 'Cold drawn') else None) if row['mode'] == '1xxx' else h
        if group == row['group'] and r[row['property']]: values.append(float(r[row['property']]))
    assert len(values) == row['n'] and len(values) > 1
    mean = statistics.mean(values)
    margin = t.isf(.025, len(values)-1) * statistics.stdev(values) / math.sqrt(len(values))
    assert math.isclose(row['mean'], mean, rel_tol=1e-12, abs_tol=1e-10)
    assert math.isclose(row['low'], mean-margin, rel_tol=1e-12, abs_tol=1e-10)
    assert math.isclose(row['high'], mean+margin, rel_tol=1e-12, abs_tol=1e-10)
print('24 intervalos contrastados con csv y statistics.')
