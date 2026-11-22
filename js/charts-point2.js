import { calculateLinearStatistics } from './stats.js';

const SVG_NS = 'http://www.w3.org/2000/svg';
const labels = { 'Hot rolled': 'Laminado en caliente', 'Cold drawn': 'Estirado en frío', 'Cold drawn + Annealed': 'Estirado en frío + recocido', 'Annealed': 'Recocido', 'Normalized': 'Normalizado', 'Quenched and tempered': 'Templado y revenido', unclassified: 'Sin clasificar' };

// Hierarchy from 2.4_Tratamiento.py; the mechanical condition takes precedence.
export function classifyProcessing(record) {
  const mechanical = record['Mechanical Conditions'], thermal = record['Heat Treatment'];
  if (mechanical === 'Cold drawn' && thermal === 'Annealed') return 'Cold drawn + Annealed';
  if (mechanical === 'Hot rolled') return 'Hot rolled';
  if (mechanical === 'Cold drawn') return 'Cold drawn';
  if (['Annealed', 'Normalized', 'Quenched and tempered'].includes(thermal)) return thermal;
  return 'unclassified';
}
export function gradeParts(grade) {
  if (grade === null || grade === undefined || !/^\d+$/.test(String(grade))) return null;
  const value = String(grade).padStart(4, '0');
  return { main: value[0], family: value.slice(0, 2) };
}
export function selectRecords(records, {series, processing, minCarbon, maxCarbon}) {
  return records.filter(record => {
    const grade = gradeParts(record['SAE Grade']);
    if (series !== 'all') {
      const [kind, value] = series.split(':');
      if (!grade || grade[kind] !== value) return false;
    }
    if (processing !== 'all' && classifyProcessing(record) !== processing) return false;
    const carbon = record['C (%)'];
    if (minCarbon !== null && (!Number.isFinite(carbon) || carbon < minCarbon)) return false;
    if (maxCarbon !== null && (!Number.isFinite(carbon) || carbon > maxCarbon)) return false;
    return true;
  });
}
function element(name, attributes = {}, text = '') {
  const node = document.createElementNS(SVG_NS, name);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
  if (text) node.textContent = text;
  return node;
}
function format(value) { return value === null || !Number.isFinite(value) ? 'No definible' : new Intl.NumberFormat('es-MX', { maximumFractionDigits: 4 }).format(value); }
export function formatEquation(slope, intercept) {
  if (!Number.isFinite(slope) || !Number.isFinite(intercept)) return 'No definible';
  const coefficient = value => (Math.abs(value) < 0.005 ? 0 : value).toFixed(2).replace('-', '−');
  const sign = intercept <= -0.005 ? '−' : '+';
  return `y = ${coefficient(slope)}x ${sign} ${coefficient(Math.abs(intercept))}`;
}
function extent(values) {
  const low = Math.min(...values), high = Math.max(...values);
  const pad = high === low ? Math.max(Math.abs(low) * .1, 1) : (high - low) * .08;
  return [low - pad, high + pad];
}
function describe(record, property) {
  const mechanical = record['Mechanical Conditions'] ?? 'Sin dato';
  const thermal = record['Heat Treatment'] ?? 'Sin dato';
  return `SAE ${record['SAE Grade'] ?? 'Sin dato'} · Carbono nominal: ${record['C (%)']} % · ${property}: ${record[property]} · Grupo: ${labels[classifyProcessing(record)]} · Condición mecánica: ${mechanical} · Tratamiento térmico: ${thermal}`;
}
function drawChart(svg, tooltip, pairs, property, stats) {
  svg.replaceChildren();
  const left = 83, right = 792, top = 24, bottom = 370;
  const [xmin, xmax] = pairs.length ? extent(pairs.map(row => row['C (%)'])) : [0, 1];
  const [ymin, ymax] = pairs.length ? extent(pairs.map(row => row[property])) : [0, 1];
  const x = value => left + (value - xmin) / (xmax - xmin) * (right - left);
  const y = value => bottom - (value - ymin) / (ymax - ymin) * (bottom - top);
  for (let i = 0; i <= 4; i++) {
    const xv = xmin + (xmax - xmin) * i / 4, yv = ymin + (ymax - ymin) * i / 4;
    svg.append(element('line', {x1:x(xv), y1:top, x2:x(xv), y2:bottom, class:'plot-grid'}));
    svg.append(element('line', {x1:left, y1:y(yv), x2:right, y2:y(yv), class:'plot-grid'}));
    svg.append(element('text', {x:x(xv), y:bottom+22, 'text-anchor':'middle', class:'plot-tick'}, format(xv)));
    svg.append(element('text', {x:left-10, y:y(yv)+4, 'text-anchor':'end', class:'plot-tick'}, format(yv)));
  }
  svg.append(element('line', {x1:left,y1:bottom,x2:right,y2:bottom,class:'plot-axis'}), element('line',{x1:left,y1:top,x2:left,y2:bottom,class:'plot-axis'}));
  if (stats.slope !== null) {
    const min = Math.min(...pairs.map(row => row['C (%)'])), max = Math.max(...pairs.map(row => row['C (%)']));
    const defs = element('defs');
    const clip = element('clipPath', {id:'plot-clip'});
    clip.append(element('rect', {x:left, y:top, width:right-left, height:bottom-top}));
    defs.append(clip); svg.append(defs);
    svg.append(element('line', {x1:x(min), y1:y(stats.intercept+stats.slope*min), x2:x(max), y2:y(stats.intercept+stats.slope*max), class:'regression-line', 'clip-path':'url(#plot-clip)'}));
  }
  for (const record of pairs) {
    const description = describe(record, property);
    const point = element('circle', {cx:x(record['C (%)']),cy:y(record[property]),r:5,class:'data-point',tabindex:0,role:'img','aria-label':description});
    point.append(element('title', {}, description));
    const show = () => { tooltip.textContent = description; };
    point.addEventListener('focus', show); point.addEventListener('mouseenter', show); point.addEventListener('click', show);
    svg.append(point);
  }
  // Prefer the upper-right corner unless the upper-left covers fewer observations.
  const boxWidth = 250, boxHeight = 100, inset = 8;
  const boxTop = top + inset;
  const leftBox = left + inset, rightBox = right - inset - boxWidth;
  const countCovered = boxX => pairs.filter(record => {
    const px = x(record['C (%)']), py = y(record[property]);
    return px >= boxX - 5 && px <= boxX + boxWidth + 5 && py >= boxTop - 5 && py <= boxTop + boxHeight + 5;
  }).length;
  const boxX = countCovered(rightBox) <= countCovered(leftBox) ? rightBox : leftBox;
  const annotation = element('g', {class:'plot-annotation', role:'group', 'aria-label':'Resumen de regresión de la selección activa'});
  annotation.append(element('rect', {x:boxX, y:boxTop, width:boxWidth, height:boxHeight, rx:7, class:'annotation-background'}));
  const lines = [`n = ${format(stats.n)}`, `r = ${format(stats.r)}`, `R² = ${format(stats.r2)}`, formatEquation(stats.slope, stats.intercept)];
  lines.forEach((line, index) => {
    const attributes = {x:boxX + 12, y:boxTop + 21 + index * 23, class:'annotation-text'};
    // Long coefficients fit inside the box without truncating the displayed equation.
    if (index === 3 && line.length > 28) { attributes.textLength = boxWidth - 24; attributes.lengthAdjust = 'spacingAndGlyphs'; }
    annotation.append(element('text', attributes, line));
  });
  svg.append(annotation);
  svg.append(element('text', {x:(left+right)/2,y:425,'text-anchor':'middle',class:'plot-label'}, 'Carbono nominal, C (%)'));
  svg.append(element('text', {x:18,y:(top+bottom)/2,transform:`rotate(-90 18 ${(top+bottom)/2})`,'text-anchor':'middle',class:'plot-label'}, property));
}
const propertyNotes = {
  'UTS (MPa)': 'La resistencia última caracteriza el esfuerzo máximo alcanzado en el ensayo de tracción.',
  'YS (MPa)': 'El esfuerzo de cedencia caracteriza el inicio de la deformación plástica en tracción.',
  'Hardness (HB)': 'La dureza Brinell caracteriza la oposición a la deformación plástica localizada bajo un indentador.',
  'Elongation (%)': 'La elongación tras la fractura expresa cuánto se alargó la probeta respecto a su longitud inicial de referencia.'
};

export function initializeCarbonChart(records) {
  const form = document.querySelector('#carbon-filters'), series = form.elements.series;
  const parts = records.map(record => gradeParts(record['SAE Grade'])).filter(Boolean);
  for (const [kind, title, values, suffix] of [['main','Series principales', [...new Set(parts.map(p=>p.main))].sort(),'XXX'], ['family','Familias de dos dígitos',[...new Set(parts.map(p=>p.family))].sort(),'XX']]) {
    const group = document.createElement('optgroup'); group.label = title;
    for (const value of values) { const option = document.createElement('option'); option.value = `${kind}:${value}`; option.textContent = `${value}${suffix}`; group.append(option); }
    series.append(group);
  }
  const svg = document.querySelector('#carbon-chart'), tooltip = document.querySelector('#chart-tooltip');
  const propertyNote = document.querySelector('#carbon-property-note');
  function update() {
    const field = name => form.elements[name];
    const minCarbon = field('minCarbon').value === '' ? null : Number(field('minCarbon').value);
    const maxCarbon = field('maxCarbon').value === '' ? null : Number(field('maxCarbon').value);
    const invalid = minCarbon !== null && maxCarbon !== null && minCarbon > maxCarbon;
    const filtered = invalid ? [] : selectRecords(records, {series:series.value, processing:field('processing').value, minCarbon, maxCarbon});
    const property = field('property').value;
    propertyNote.textContent = propertyNotes[property];
    const stats = calculateLinearStatistics(filtered, 'C (%)', property);
    document.querySelector('#chart-scope').textContent = `${series.selectedOptions[0].textContent} · ${field('processing').selectedOptions[0].textContent} · ${property} · ${stats.n} observaciones válidas de ${filtered.length} registros seleccionados`;
    const messages = [];
    if (invalid) messages.push('El mínimo de carbono debe ser menor o igual que el máximo.');
    else if (stats.n === 0) messages.push('No hay observaciones válidas para esta selección.');
    else if (stats.n === 1) messages.push('Una observación no permite calcular correlación ni regresión.');
    else {
      if (stats.n <= 5) messages.push('Con cinco pares válidos o menos, las estimaciones pueden ser inestables.');
      if (stats.r === null) messages.push('Pearson requiere variación tanto en el carbono nominal como en la propiedad seleccionada. Al menos una variable es constante.');
    }
    document.querySelector('#chart-message').textContent = messages.join(' ');
    for (const [id, value] of Object.entries({n:stats.n,r:stats.r,slope:stats.slope,intercept:stats.intercept,r2:stats.r2})) document.querySelector(`#stat-${id}`).textContent = format(value);
    tooltip.textContent = 'Selecciona un punto para ver sus datos.';
    drawChart(svg, tooltip, stats.pairs, property, stats);
  }
  form.addEventListener('input', update); form.addEventListener('change', update);
  form.addEventListener('reset', () => setTimeout(update, 0));
  update();
}
