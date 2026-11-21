// Online centered sums avoid subtracting large raw sums when estimating covariance.
export function calculateLinearStatistics(records, xKey, yKey) {
  const pairs = records.filter(record => Number.isFinite(record[xKey]) && Number.isFinite(record[yKey]));
  let n = 0, meanX = 0, meanY = 0, sxx = 0, syy = 0, sxy = 0;
  for (const record of pairs) {
    const x = record[xKey], y = record[yKey];
    n++;
    const dx = x - meanX, dy = y - meanY;
    meanX += dx / n; meanY += dy / n;
    sxx += dx * (x - meanX); syy += dy * (y - meanY); sxy += dx * (y - meanY);
  }
  // A constant response has a valid horizontal OLS line, but undefined r and R².
  const slope = n >= 2 && sxx > 0 ? sxy / sxx : null;
  const intercept = slope === null ? null : meanY - slope * meanX;
  const r = n >= 2 && sxx > 0 && syy > 0 ? Math.max(-1, Math.min(1, sxy / Math.sqrt(sxx * syy))) : null;
  return { pairs, n, r, slope, intercept, r2: r === null ? null : r * r };
}

// Linear interpolation at (n - 1) * p, as in pandas' default quantile method.
export function describeValues(values) {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  const n = sorted.length;
  if (!n) return { n: 0 };
  const quantile = p => {
    const position = (n - 1) * p, lower = Math.floor(position), fraction = position - lower;
    return sorted[lower] + (sorted[Math.ceil(position)] - sorted[lower]) * fraction;
  };
  const mean = sorted.reduce((sum, value) => sum + value, 0) / n;
  const sd = n > 1 ? Math.sqrt(sorted.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (n - 1)) : null;
  const q1 = quantile(.25), median = quantile(.5), q3 = quantile(.75), iqr = q3 - q1;
  const inside = sorted.filter(value => value >= q1 - 1.5 * iqr && value <= q3 + 1.5 * iqr);
  return { n, mean, median, sd, min: sorted[0], q1, q3, max: sorted[n - 1], lowerWhisker: inside[0], upperWhisker: inside[inside.length - 1] };
}

// Correlations use pairwise complete observations and the reference minimum n = 3.
export function correlation(records, xKey, yKey, method = 'pearson') {
  const pairs = records.filter(r => Number.isFinite(r[xKey]) && Number.isFinite(r[yKey]));
  if (pairs.length < 3) return { n: pairs.length, value: null, pairs };
  let xs = pairs.map(r => r[xKey]), ys = pairs.map(r => r[yKey]);
  if (method === 'spearman') { xs = averageRanks(xs); ys = averageRanks(ys); }
  const data = xs.map((x, i) => ({ x, y: ys[i] }));
  return { n: pairs.length, value: calculateLinearStatistics(data, 'x', 'y').r, pairs };
}
export function averageRanks(values) {
  const sorted = values.map((value, index) => ({ value, index })).sort((a,b) => a.value-b.value);
  const ranks = Array(values.length);
  for (let i = 0; i < sorted.length;) {
    let j = i + 1; while (j < sorted.length && sorted[j].value === sorted[i].value) j++;
    const rank = (i + 1 + j) / 2;
    for (let k = i; k < j; k++) ranks[sorted[k].index] = rank;
    i = j;
  }
  return ranks;
}

// Residualize with group intercepts and a common carbon slope (equivalent to
// OLS with an intercept, carbon, and two group indicators via FWL).
export function partialPearson(records, properties, xKey, yKey, groupKey = 'processingGroup') {
  const complete = records.filter(r => Number.isFinite(r['C (%)']) && properties.every(p => Number.isFinite(r[p])) && r[groupKey]);
  const groupNames = [...new Set(complete.map(r => r[groupKey]))];
  if (complete.length < groupNames.length + 3) return { n: complete.length, raw: null, partial: null };
  const residual = key => {
    const means = new Map(groupNames.map(group => {
      const subset = complete.filter(r => r[groupKey] === group);
      return [group, {c:subset.reduce((s,r)=>s+r['C (%)'],0)/subset.length, v:subset.reduce((s,r)=>s+r[key],0)/subset.length}];
    }));
    const centered = complete.map(r => ({ c:r['C (%)']-means.get(r[groupKey]).c, v:r[key]-means.get(r[groupKey]).v }));
    const ss = centered.reduce((s,r)=>s+r.c*r.c,0);
    if (ss <= 1e-20) return null;
    const slope = centered.reduce((s,r)=>s+r.c*r.v,0)/ss;
    return centered.map(r => r.v-slope*r.c);
  };
  const x = residual(xKey), y = residual(yKey);
  const raw = correlation(complete, xKey, yKey).value;
  if (!x || !y) return { n:complete.length, raw, partial:null };
  const residuals = x.map((v,i)=>({x:v,y:y[i]}));
  return { n:complete.length, raw, partial:correlation(residuals,'x','y').value };
}
