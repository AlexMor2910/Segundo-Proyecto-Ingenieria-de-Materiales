import { propertyNames } from './charts-point3.js';
const names={'Hot rolled':'Laminado en caliente','Cold drawn':'Estirado en frío','Cold drawn + Annealed':'Estirado y recocido','Annealed':'Recocido','Normalized':'Normalizado','Quenched and tempered':'Templado y revenido'};
export const inferenceP = value => value===0?'Menor que la precisión numérica':value==null?'—':Number(value).toExponential(3);
export async function loadVerifiedInference() {
  try {
    if(!globalThis.crypto?.subtle) return null;
    const [resultsResponse,csvResponse]=await Promise.all([fetch(new URL('../data/statistical-results.json',import.meta.url)),fetch(new URL('../data/steels.csv',import.meta.url))]);
    if(!resultsResponse.ok||!csvResponse.ok) return null;
    const [results,bytes]=await Promise.all([resultsResponse.json(),csvResponse.arrayBuffer()]);
    const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
    return results.metadata?.input_sha256===hash?results:null;
  } catch {return null;}
}
export function inferenceRows(data) {
  const rows=[];
  for(const r of data.anova) {
    const welch=r['Selected test']==='ANOVA de Welch';
    rows.push([r.mode==='1xxx'?'SAE 1XXX':'Otras series',propertyNames[r.Property],r['Selected test'],'Todos los grupos',r.N,welch?r['Welch F']:r['ANOVA F'],welch?r['Welch df numerator']:r['Conventional df numerator'],welch?r['Welch df denominator']:r['Conventional df denominator'],inferenceP(r['Selected p']),r['Eta squared'],'','','']);
  }
  for(const r of data.tukey){const n1=data.groups.find(g=>g.mode==='other'&&g.property===r.property&&g.group===r.group1)?.n,n2=data.groups.find(g=>g.mode==='other'&&g.property===r.property&&g.group===r.group2)?.n;rows.push(['Otras series',propertyNames[r.property],'Tukey',`${names[r.group1]} / ${names[r.group2]}`,`${n1} / ${n2}`,'', '', '',inferenceP(r.p_adjusted),'',r.mean_difference,r.ci_low,r.ci_high]);}
  for(const r of data.games_howell)rows.push([r.mode==='1xxx'?'SAE 1XXX':'Otras series',propertyNames[r.Property],'Games–Howell',`${names[r['Group 1']]} / ${names[r['Group 2']]}`,`${r.n1} / ${r.n2}`,r['q statistic'],'',r['Degrees of Freedom'],inferenceP(r['p-adjusted']),'',r['Mean Difference'],r['CI Lower'],r['CI Upper']]);
  return rows;
}
export function initializeInference(data) {
  const target=document.querySelector('#verified-inference');if(!data||!target)return;
  const form=document.querySelector('#processing-filters');
  const update=()=>{
    const mode=form.elements.mode.value,property=form.elements.property.value,row=data.anova.find(r=>r.mode===mode&&r.Property===property);
    if(!row){target.hidden=true;return;} target.hidden=false;
    const isWelch=row['Selected test']==='ANOVA de Welch', f=isWelch?row['Welch F']:row['ANOVA F'], df1=isWelch?row['Welch df numerator']:row['Conventional df numerator'],df2=isWelch?row['Welch df denominator']:row['Conventional df denominator'];
    target.textContent=`${row['Selected test']} · F(${df1.toFixed(2)}, ${df2.toFixed(2)}) = ${f.toFixed(2)} · p = ${inferenceP(row['Selected p'])} · η² = ${row['Eta squared'].toFixed(3)} · n = ${row.N}. Levene: p = ${inferenceP(row['Levene p'])}. Población original fija; las comparaciones post hoc están en el explorador de datos.`;
  };
  form.addEventListener('change',update);form.addEventListener('reset',()=>setTimeout(update,0));update();
}
