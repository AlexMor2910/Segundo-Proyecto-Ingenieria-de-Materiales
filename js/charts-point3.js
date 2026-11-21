import { correlation, partialPearson } from './stats.js';
import { processingGroup } from './charts-processing.js';

export const properties = ['UTS (MPa)','YS (MPa)','Hardness (HB)','Elongation (%)','Reduction (%)'];
export const propertyNames = {'UTS (MPa)':'Resistencia última (MPa)','YS (MPa)':'Esfuerzo de cedencia (MPa)','Hardness (HB)':'Dureza Brinell (HB)','Elongation (%)':'Elongación (%)','Reduction (%)':'Reducción de área (%)'};
const short = ['UTS','YS','Dureza','Elongación','Reducción'];
const groups = ['Hot rolled','Cold drawn','Cold drawn + Annealed'];
const groupLabels = ['Laminado en caliente','Estirado en frío','Estirado y recocido'];
const NS = 'http://www.w3.org/2000/svg';
export function point3Population(records) {
  return records.map(record => ({...record, processingGroup: processingGroup(record,'1xxx')})).filter(record => record.processingGroup);
}
export function rankPairs(records, method, sign = 'all') {
  const result = [];
  properties.forEach((x,i) => properties.slice(i+1).forEach(y => {
    const {value,n} = correlation(records,x,y,method);
    if (value === null ? sign === 'all' : sign === 'all' || (sign === 'positive' ? value > 0 : value < 0)) result.push({x,y,value,n});
  }));
  return result.sort((a,b) => a.value === null ? (b.value === null ? 0 : 1) : b.value === null ? -1 : Math.abs(b.value)-Math.abs(a.value));
}
const fmt = v => v === null ? 'No definible' : v.toFixed(4).replace('-', '−');
function node(tag, attrs={}, text='') { const n=document.createElementNS(NS,tag); for(const [k,v] of Object.entries(attrs)) n.setAttribute(k,String(v)); if(text) n.textContent=text; return n; }
function html(tag, text='', cls='') { const n=document.createElement(tag); n.textContent=text; if(cls)n.className=cls; return n; }
export function correlationColor(value) {
  if (value === null) return '#edf1f4';
  const target = value < 0 ? [190,90,65] : [36,107,159], t = Math.abs(value)*.72;
  return `rgb(${target.map(c=>Math.round(255+(c-255)*t)).join(',')})`;
}
function extent(values) { const lo=Math.min(...values),hi=Math.max(...values),pad=lo===hi?Math.max(Math.abs(lo)*.1,1):(hi-lo)*.08; return [lo-pad,hi+pad]; }
function renderScatter(svg, tooltip, result, xKey, yKey, method) {
  svg.replaceChildren(); const pairs=result.pairs;
  if (!pairs.length) return;
  const [xmin,xmax]=extent(pairs.map(r=>r[xKey])), [ymin,ymax]=extent(pairs.map(r=>r[yKey]));
  const x=v=>85+(v-xmin)/(xmax-xmin)*700, y=v=>360-(v-ymin)/(ymax-ymin)*330;
  for(let i=0;i<=4;i++) { const xv=xmin+(xmax-xmin)*i/4,yv=ymin+(ymax-ymin)*i/4;
    svg.append(node('line',{x1:x(xv),y1:30,x2:x(xv),y2:360,class:'plot-grid'}),node('line',{x1:85,y1:y(yv),x2:785,y2:y(yv),class:'plot-grid'}),node('text',{x:x(xv),y:380,'text-anchor':'middle',class:'plot-tick'},xv.toFixed(1)),node('text',{x:75,y:y(yv)+4,'text-anchor':'end',class:'plot-tick'},yv.toFixed(1))); }
  svg.append(node('line',{x1:85,y1:360,x2:785,y2:360,class:'plot-axis'}),node('line',{x1:85,y1:30,x2:85,y2:360,class:'plot-axis'}));
  pairs.forEach(record=>{ const group=groups.indexOf(record.processingGroup), description=`SAE ${record['SAE Grade']} · ${propertyNames[xKey]}: ${record[xKey]} · ${propertyNames[yKey]}: ${record[yKey]} · ${groupLabels[group]}`;
    const point=node('circle',{cx:x(record[xKey]),cy:y(record[yKey]),r:5,class:`processing-point group-${group}`,tabindex:0,role:'img','aria-label':description});
    point.append(node('title',{},description)); const show=()=>{tooltip.textContent=description}; point.addEventListener('focus',show);point.addEventListener('mouseenter',show);point.addEventListener('click',show);svg.append(point); });
  const box=node('g',{class:'plot-annotation',role:'group','aria-label':'Resumen de correlación'});
  box.append(node('rect',{x:568,y:38,width:205,height:65,rx:7,class:'annotation-background'}),node('text',{x:580,y:63,class:'annotation-text'},`n = ${result.n}`),node('text',{x:580,y:88,class:'annotation-text'},`${method==='spearman'?'ρ':'r'} = ${fmt(result.value)}`));svg.append(box);
  svg.append(node('text',{x:435,y:425,'text-anchor':'middle',class:'plot-label'},propertyNames[xKey]),node('text',{x:20,y:195,transform:'rotate(-90 20 195)','text-anchor':'middle',class:'plot-label'},propertyNames[yKey]));
}
function explanation(x,y) {
  const p = new Set([x,y]);
  if(p.has(properties[0])&&p.has(properties[2])) return 'UTS y dureza se relacionan con la resistencia a la deformación plástica; mecanismos compartidos pueden contribuir a su asociación.';
  if(p.has(properties[1])&&p.has(properties[3])) return 'YS y elongación reflejan resistencia y ductilidad; el endurecimiento por deformación puede influir en ambas.';
  if(p.has(properties[0])&&p.has(properties[1])) return 'YS caracteriza el inicio de la deformación plástica; UTS es el esfuerzo máximo durante la tracción.';
  if(p.has(properties[3])&&p.has(properties[4])) return 'Elongación y reducción de área describen aspectos distintos de la ductilidad.';
  return 'La asociación es descriptiva y puede depender de la composición y el procesamiento; no demuestra causalidad.';
}
export function initializePoint3(records) {
  const population=point3Population(records), form=document.querySelector('#p3-controls'), fields=form.elements;
  for (const axis of ['x','y']) properties.forEach(p=>{const option=html('option',propertyNames[p]);option.value=p;fields[axis].append(option)});
  fields.x.value=properties[0]; fields.y.value=properties[2];
  const counts=groups.map(g=>population.filter(r=>r.processingGroup===g).length);
  document.querySelector('#p3-population').textContent=`${population.length} observaciones incluidas · ${new Set(population.map(r=>r['SAE Grade'])).size} grados distintos · grupos: ${counts.join(' / ')} registros.`;
  const svg=document.querySelector('#p3-scatter'),tooltip=document.querySelector('#p3-tooltip');
  function setPair(x,y) {fields.x.value=x;fields.y.value=y;update();document.querySelector('#p3-summary').focus();}
  function update() {
    const method=fields.method.value, group=fields.group.value, selected=group==='all'?population:population.filter(r=>r.processingGroup===group), x=fields.x.value,y=fields.y.value;
    const matrix=document.querySelector('#p3-matrix'); matrix.replaceChildren();
    const head=html('tr');head.append(html('th','Propiedad'));short.forEach(label=>{const th=html('th',label);th.scope='col';head.append(th)});matrix.append(head);
    properties.forEach((row,i)=>{const tr=html('tr'), th=html('th',short[i]);th.scope='row';tr.append(th);properties.forEach((col,j)=>{
      const result=correlation(selected,row,col,method),td=html('td');
      if(i===j){td.textContent=result.value===null?'—':'1.00';td.style.backgroundColor=correlationColor(result.value);} else {const b=html('button',result.value===null?'—':result.value.toFixed(2),'matrix-cell'); b.type='button';b.style.backgroundColor=correlationColor(result.value);b.setAttribute('aria-label',`${propertyNames[row]} y ${propertyNames[col]}: ${fmt(result.value)}, n ${result.n}`);b.setAttribute('aria-pressed',String((row===x&&col===y)||(row===y&&col===x)));b.addEventListener('click',()=>setPair(row,col));td.append(b);}tr.append(td);
    });matrix.append(tr);});
    const list=document.querySelector('#p3-ranking');list.replaceChildren();rankPairs(selected,method,fields.sign.value).forEach(item=>{const li=html('li'),direction=item.value===null?'Sin clasificación':item.value>0?'Positiva':item.value<0?'Negativa':'Sin asociación',b=html('button',item.value===null?'No definible':`${item.value>=0?'+':'−'}${Math.abs(item.value).toFixed(4)}`);if(item.value === null) li.style.listStyle='none';b.type='button';b.setAttribute('aria-label',`${propertyNames[item.x]} y ${propertyNames[item.y]}, ${method==='spearman'?'Spearman':'Pearson'} ${fmt(item.value)}, ${direction}, n = ${item.n}`);b.style.backgroundColor=correlationColor(item.value);b.style.borderColor=correlationColor(item.value===null?null:Math.max(-1,Math.min(1,item.value*1.3)));b.addEventListener('click',()=>setPair(item.x,item.y));li.append(b);list.append(li)});
    const result=correlation(selected,x,y,method);document.querySelector('#p3-summary').textContent=`${propertyNames[x]} y ${propertyNames[y]} · ${method==='spearman'?'Spearman ρ':'Pearson r'} = ${fmt(result.value)} · n = ${result.n}${result.value===null?' · Se necesitan al menos tres pares y variación en ambas propiedades.':''}`;
    tooltip.textContent='Selecciona un punto para ver sus datos.';renderScatter(svg,tooltip,result,x,y,method);document.querySelector('#p3-explanation').textContent=explanation(x,y);
    const comparison=document.querySelector('#p3-comparison');comparison.replaceChildren();groups.forEach((g,i)=>{const r=correlation(population.filter(v=>v.processingGroup===g),x,y,method),row=html('tr'),label=html('th',groupLabels[i]),n=html('td',String(r.n)),value=html('td',fmt(r.value));label.scope='row';value.style.backgroundColor=correlationColor(r.value);row.append(label,n,value);comparison.append(row)});
    const partial=partialPearson(population,properties,x,y);document.querySelector('#p3-partial').textContent=`Casos completos: n = ${partial.n} · Pearson sin ajustar: ${fmt(partial.raw)} · Pearson parcial: ${fmt(partial.partial)}. Resultado para toda la población analítica 1XXX, independiente del filtro de procesamiento.`;
  }
  form.addEventListener('change',event=>{if(fields.x.value===fields.y.value){if(event.target===fields.x)fields.y.value=properties.find(p=>p!==fields.x.value);else fields.x.value=properties.find(p=>p!==fields.y.value)}update()});update();
}
