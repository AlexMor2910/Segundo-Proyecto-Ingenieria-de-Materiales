import { describeValues } from './stats.js';
import { gradeParts } from './charts-point2.js';

const NS = 'http://www.w3.org/2000/svg';
const configs = {
  '1xxx': [['Hot rolled', 'Laminado en caliente'], ['Cold drawn', 'Estirado en frío'], ['Cold drawn + Annealed', 'Estirado + recocido']],
  other: [['Annealed', 'Recocido'], ['Normalized', 'Normalizado'], ['Quenched and tempered', 'Templado y revenido']]
};
export function processingGroup(record, mode) {
  const parts = gradeParts(record['SAE Grade']);
  if (!parts || (mode === '1xxx' ? parts.main !== '1' : parts.main === '1')) return null;
  if (mode === 'other') return configs.other.some(([key]) => key === record['Heat Treatment']) ? record['Heat Treatment'] : null;
  if (record['Mechanical Conditions'] === 'Cold drawn' && record['Heat Treatment'] === 'Annealed') return 'Cold drawn + Annealed';
  if (record['Mechanical Conditions'] === 'Hot rolled') return 'Hot rolled';
  if (record['Mechanical Conditions'] === 'Cold drawn') return 'Cold drawn';
  return null;
}
export function comparisonGroups(records, mode, property) {
  const population = records.filter(record => { const grade = gradeParts(record['SAE Grade']); return grade && (mode === '1xxx' ? grade.main === '1' : grade.main !== '1'); });
  const groups = configs[mode].map(([key, label]) => {
    const members = population.filter(record => processingGroup(record, mode) === key);
    const valid = members.filter(record => Number.isFinite(record[property]));
    return { key, label, members, valid, stats: describeValues(valid.map(record => record[property])) };
  });
  const excludedRecords = population.filter(record => !processingGroup(record, mode));
  return { groups, total: population.length, excluded: excludedRecords.length, excludedRecords, unknownGrade: records.filter(record => !gradeParts(record['SAE Grade'])).length };
}
function el(name, attrs = {}, text = '') {
  const node = document.createElementNS(NS, name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, String(value));
  if (text !== '') node.textContent = text;
  return node;
}
function number(value) { return value == null || !Number.isFinite(value) ? 'No definible' : new Intl.NumberFormat('es-MX', { maximumFractionDigits: 2 }).format(value); }
function renderChart(svg, tooltip, groups, property) {
  svg.replaceChildren();
  const values = groups.flatMap(group => group.valid.map(record => record[property]));
  if (!values.length) return;
  const min = Math.min(...values), max = Math.max(...values), pad = max === min ? Math.max(Math.abs(min) * .1, 1) : (max - min) * .08;
  const low = min - pad, high = max + pad, top = 24, bottom = 352;
  const y = value => bottom - (value - low) / (high - low) * (bottom - top);
  for (let i = 0; i <= 4; i++) {
    const value = low + (high - low) * i / 4;
    svg.append(el('line', {x1:75,y1:y(value),x2:798,y2:y(value),class:'plot-grid'}), el('text', {x:66,y:y(value)+4,'text-anchor':'end',class:'plot-tick'}, number(value)));
  }
  svg.append(el('line',{x1:75,y1:top,x2:75,y2:bottom,class:'plot-axis'}), el('line',{x1:75,y1:bottom,x2:798,y2:bottom,class:'plot-axis'}));
  groups.forEach((group, index) => {
    const center = 195 + index * 235, s = group.stats;
    if (s.n) {
      svg.append(el('line',{x1:center,y1:y(s.lowerWhisker),x2:center,y2:y(s.upperWhisker),class:'box-whisker'}));
      for (const v of [s.lowerWhisker,s.upperWhisker]) svg.append(el('line',{x1:center-22,y1:y(v),x2:center+22,y2:y(v),class:'box-whisker'}));
      svg.append(el('rect',{x:center-48,y:y(s.q3),width:96,height:Math.max(1,y(s.q1)-y(s.q3)),class:`box-body group-${index}`}));
      svg.append(el('line',{x1:center-48,y1:y(s.median),x2:center+48,y2:y(s.median),class:'box-median'}));
      group.valid.forEach((record, i) => {
        // Deterministic display-only horizontal offset; the value remains on the vertical axis.
        const offset = ((i * 37) % 81) - 40, value = record[property];
        const outlier = value < s.lowerWhisker || value > s.upperWhisker;
        const description = `SAE ${record['SAE Grade']} · ${property}: ${value} · ${group.label} · Condición mecánica: ${record['Mechanical Conditions'] ?? 'Sin dato'} · Tratamiento térmico: ${record['Heat Treatment'] ?? 'Sin dato'}${outlier ? ' · Valor atípico' : ''}`;
        const point = el('circle',{cx:center+offset,cy:y(value),r:4.5,class:`processing-point group-${index}${outlier ? ' processing-outlier' : ''}`,tabindex:0,role:'img','aria-label':description});
        point.append(el('title',{},description));
        const show = () => { tooltip.textContent = description; };
        point.addEventListener('focus',show); point.addEventListener('mouseenter',show); point.addEventListener('click',show);
        svg.append(point);
      });
      svg.append(el('path',{d:`M ${center} ${y(s.mean)-7} l 7 7 l -7 7 l -7 -7 Z`,class:'box-mean'}));
      // Keep the mean label outside the box and within the plotting area.
      const labelX = index === 2 ? center - 172 : center + 54;
      const labelY = Math.max(top + 17, Math.min(bottom - 6, y(s.mean) - 10));
      svg.append(el('rect',{x:labelX-3,y:labelY-14,width:116,height:19,rx:4,class:'mean-label-bg'}));
      svg.append(el('text',{x:labelX,y:labelY,class:'mean-label'},`Media: ${s.mean.toFixed(2)}`));
    }
    svg.append(el('text',{x:center,y:bottom+23,'text-anchor':'middle',class:'plot-label'},group.label));
    svg.append(el('text',{x:center,y:bottom+43,'text-anchor':'middle',class:'plot-tick'},`n = ${s.n}`));
  });
  svg.append(el('text',{x:18,y:188,transform:'rotate(-90 18 188)','text-anchor':'middle',class:'plot-label'},property));
}
export function initializeProcessingChart(records) {
  const form = document.querySelector('#processing-filters'), svg = document.querySelector('#processing-chart'), tooltip = document.querySelector('#processing-tooltip');
  function update() {
    const mode = form.elements.mode.value, property = form.elements.property.value;
    const {groups,total,excluded,excludedRecords,unknownGrade} = comparisonGroups(records,mode,property);
    document.querySelector('#mechanical-interpretation').hidden = mode !== '1xxx';
    document.querySelector('#thermal-interpretation').hidden = mode !== 'other';
    groups.forEach((group, index) => { document.querySelector(`#group-legend-${index}`).textContent = group.label; });
    const included = total - excluded, missing = groups.reduce((sum, group) => sum + group.members.length - group.valid.length, 0);
    document.querySelector('#processing-scope').textContent = `Población: ${total} registros · ${included} clasificados · ${excluded} excluidos por condición no clasificada · ${missing} sin la propiedad seleccionada${unknownGrade ? ` · ${unknownGrade} sin grado SAE válido, fuera de ambas poblaciones` : ''}.`;
    document.querySelector('#processing-excluded').textContent = excluded ? `Registros excluidos de esta población: ${excludedRecords.map(record => `SAE ${record['SAE Grade']} (condición mecánica: ${record['Mechanical Conditions'] ?? 'sin dato'}; tratamiento térmico: ${record['Heat Treatment'] ?? 'sin dato'})`).join(' · ')}.` : 'No hay registros excluidos por clasificación en esta población.';
    document.querySelector('#processing-message').textContent = groups.every(group => !group.stats.n) ? 'No hay observaciones válidas para esta selección.' : groups.some(group => group.stats.n < 2) ? 'Al menos un grupo tiene menos de dos observaciones válidas; su dispersión muestral no es definible.' : '';
    const body = document.querySelector('#processing-table tbody');
    body.replaceChildren(...groups.map(group => {
      const row = document.createElement('tr'), heading = document.createElement('th'); heading.scope = 'row'; heading.textContent = group.label; row.append(heading);
      for (const [index, value] of [group.members.length,group.stats.n,group.stats.mean,group.stats.median,group.stats.sd,group.stats.min,group.stats.q1,group.stats.q3,group.stats.max].entries()) { const cell = document.createElement('td'); cell.textContent = index === 2 && Number.isFinite(value) ? value.toFixed(2) : number(value); row.append(cell); }
      return row;
    }));
    tooltip.textContent = 'Selecciona una observación para ver sus datos.';
    renderChart(svg,tooltip,groups,property);
  }
  form.addEventListener('change',update); form.addEventListener('reset',() => setTimeout(update,0)); update();
}
