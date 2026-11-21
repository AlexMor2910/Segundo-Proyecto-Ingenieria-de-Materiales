import { inferenceP } from './inference.js';
import { propertyNames } from './charts-point3.js';

const keys = { '1xxx':['Hot rolled','Cold drawn','Cold drawn + Annealed'], other:['Annealed','Normalized','Quenched and tempered'] };
const names = {'Hot rolled':'Laminado en caliente','Cold drawn':'Estirado en frío','Cold drawn + Annealed':'Estirado en frío + recocido','Annealed':'Recocido','Normalized':'Normalizado','Quenched and tempered':'Templado y revenido'};
const ns='http://www.w3.org/2000/svg';
const num=v=>Number(v).toLocaleString('es-MX',{minimumFractionDigits:2,maximumFractionDigits:2});
function svgNode(tag, attrs={}, text='') { const el=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));if(text)el.textContent=text;return el; }
function cell(tag,value){const el=document.createElement(tag);el.textContent=value;return el;}

export function selectMeanIntervals(intervals, verified, mode, property) {
  if(!intervals || !Array.isArray(intervals.groups) || intervals.input_sha256!==verified.metadata.input_sha256) return null;
  const rows=keys[mode]?.map(group=>intervals.groups.find(r=>r.mode===mode&&r.property===property&&r.group===group));
  if(!rows || rows.some(row=>!row || !Number.isFinite(row.mean) || !Number.isFinite(row.low) || !Number.isFinite(row.high) || row.low>row.mean || row.high<row.mean || !verified.groups.some(g=>g.mode===mode&&g.property===property&&g.group===row.group&&g.n===row.n&&Math.abs(g.mean-row.mean)<1e-9)))return null;
  return rows;
}
export function selectPosthoc(verified,mode,property) {
  if(mode==='other'&&property!=='YS (MPa)') return verified.tukey.filter(r=>r.mode===mode&&r.property===property).map(r=>({first:r.group1,second:r.group2,p:r.p_adjusted,method:'Tukey'}));
  return verified.games_howell.filter(r=>r.mode===mode&&r.Property===property).map(r=>({first:r['Group 1'],second:r['Group 2'],p:r['p-adjusted'],method:'Games–Howell'}));
}
export async function initializeMeanInference(verified) {
  if(!verified) return;
  let intervals;
  try {const response=await fetch(new URL('../data/mean-ci.json',import.meta.url));if(!response.ok)return;intervals=await response.json();}catch{return;}
  const section=document.querySelector('#mean-inference'),form=document.querySelector('#processing-filters'),chart=document.querySelector('#mean-chart');
  function update(){
    const mode=form.elements.mode.value,property=form.elements.property.value,rows=selectMeanIntervals(intervals,verified,mode,property);
    if(!rows){section.hidden=true;return;}section.hidden=false;chart.replaceChildren();
    const min=Math.min(...rows.map(r=>r.low)),max=Math.max(...rows.map(r=>r.high)),pad=(max-min)*.12||1,left=260,right=780,lo=min-pad,hi=max+pad;
    const x=v=>left+(v-lo)/(hi-lo)*(right-left);
    for(let i=0;i<=4;i++){const v=lo+(hi-lo)*i/4;chart.append(svgNode('line',{x1:x(v),y1:25,x2:x(v),y2:204,class:'plot-grid'}),svgNode('text',{x:x(v),y:227,'text-anchor':'middle',class:'plot-tick'},num(v)));}
    const body=document.querySelector('#mean-values');body.replaceChildren();
    rows.forEach((r,i)=>{const y=52+i*62,desc=`${names[r.group]}: n = ${r.n}, media ${num(r.mean)}, intervalo del 95 % de ${num(r.low)} a ${num(r.high)}, ${propertyNames[property]}`;
      chart.append(svgNode('text',{x:left-14,y:y+5,'text-anchor':'end',class:'mean-group-label'},names[r.group]));
      const line=svgNode('g',{role:'img','aria-label':desc,tabindex:0,class:`mean-interval group-${i}`});
      line.append(svgNode('title',{},desc),svgNode('line',{x1:x(r.low),x2:x(r.high),y1:y,y2:y,class:'mean-ci-line'}),svgNode('line',{x1:x(r.low),x2:x(r.low),y1:y-7,y2:y+7,class:'mean-ci-line'}),svgNode('line',{x1:x(r.high),x2:x(r.high),y1:y-7,y2:y+7,class:'mean-ci-line'}),svgNode('circle',{cx:x(r.mean),cy:y,r:6,class:'mean-ci-point'}));chart.append(line);
      const tr=cell('tr',''),th=cell('th',names[r.group]);th.scope='row';tr.append(th,...[r.n,num(r.mean),num(r.low),num(r.high)].map(v=>cell('td',String(v))));body.append(tr);
    });
    chart.append(svgNode('text',{x:(left+right)/2,y:258,'text-anchor':'middle',class:'plot-label'},propertyNames[property]));
    const posthoc=document.querySelector('#mean-posthoc');posthoc.replaceChildren();
    for(const result of selectPosthoc(verified,mode,property)){const tr=cell('tr','');for(const value of [`${names[result.first]} / ${names[result.second]}`,result.method,inferenceP(result.p),result.p == null?'No disponible':result.p<.05?'Diferencia significativa':'Sin evidencia de diferencia significativa'])tr.append(cell('td',value));posthoc.append(tr);}
  }
  form.addEventListener('change',update);form.addEventListener('reset',()=>setTimeout(update,0));update();
}
