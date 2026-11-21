import { parseCSV } from './data.js';
import { gradeParts, classifyProcessing } from './charts-point2.js';
import { comparisonGroups } from './charts-processing.js';
import { point3Population, properties, propertyNames } from './charts-point3.js';
import { correlation, partialPearson } from './stats.js';
import { inferenceRows } from './inference.js';

const groupLabels = {'Hot rolled':'Laminado en caliente','Cold drawn':'Estirado en frío','Cold drawn + Annealed':'Estirado y recocido','Annealed':'Recocido','Normalized':'Normalizado','Quenched and tempered':'Templado y revenido','unclassified':'Sin clasificar'};
const groupKeys = ['Hot rolled','Cold drawn','Cold drawn + Annealed'];
const make = (tag,text='') => { const e=document.createElement(tag); e.textContent=text; return e; };
export function csvText(headers,rows) {
  const escape = value => `"${String(value ?? '').replaceAll('"','""')}"`;
  return '\ufeff'+[headers,...rows].map(row=>row.map(escape).join(',')).join('\r\n');
}
export function filterRecordRows(rows, {query='',series='all',processing='all'}) {
  return rows.filter(({record})=>{
    const parts=gradeParts(record['SAE Grade']);
    return String(record['SAE Grade'] ?? '').toLowerCase().includes(query.toLowerCase().trim()) && (series==='all'||(parts && parts[series.split(':')[0]]===series.split(':')[1])) && (processing==='all'||classifyProcessing(record)===processing);
  });
}
export function buildTableData(records) {
  const descriptive=[];
  for(const mode of ['1xxx','other']) for(const property of properties.slice(0,4)) for(const g of comparisonGroups(records,mode,property).groups) {
    const s=g.stats; descriptive.push([mode==='1xxx'?'SAE 1XXX':'Otras series',g.label,propertyNames[property],s.n,s.mean,s.median,s.sd,s.min,s.q1,s.q3,s.max]);
  }
  const population=point3Population(records),correlations=[],partial=[];
  for(const [index,x] of properties.entries()) for(const y of properties.slice(index+1)) {
    for(const g of ['all',...groupKeys]) {const subset=g==='all'?population:population.filter(r=>r.processingGroup===g);const p=correlation(subset,x,y,'pearson'),s=correlation(subset,x,y,'spearman');correlations.push([propertyNames[x],propertyNames[y],g==='all'?'Todos los grupos 1XXX':groupLabels[g],p.n,p.value,s.value,s.value===null?null:Math.abs(s.value)]);}
    const p=partialPearson(population,properties,x,y);partial.push([propertyNames[x],propertyNames[y],p.n,p.raw,p.partial]);
  }
  return {descriptive,correlations,partial};
}
export async function initializeTables(records,columns,inference = null) {
  const root=document.querySelector('#tables-explorer');
  try {
    const response=await fetch(new URL('../data/steels.csv',import.meta.url)); if(!response.ok)throw Error('CSV');
    const raw=parseCSV(await response.text()); const rawHeaders=raw.shift();
    if(raw.length!==records.length||rawHeaders.join('\0')!==columns.join('\0'))throw Error('estructura');
    const source=records.map((record,index)=>({record,raw:raw[index]}));
    const calculated=buildTableData(records);
    const views={records:{label:'Registros de aceros',headers:columns},descriptive:{label:'Estadísticos descriptivos',headers:['Población','Grupo','Propiedad','n','Media','Mediana','Desv. estándar','Mínimo','Q1','Q3','Máximo'],rows:calculated.descriptive},correlations:{label:'Correlaciones',headers:['Propiedad 1','Propiedad 2','Población','n','Pearson r','Spearman ρ','|ρ|'],rows:calculated.correlations},partial:{label:'Correlaciones parciales',headers:['Propiedad 1','Propiedad 2','n','Pearson sin ajustar','Pearson parcial'],rows:calculated.partial}};
    if(inference){const partial=views.partial;delete views.partial;views.inference={label:'ANOVA y comparaciones post hoc',headers:['Población','Propiedad','Método','Comparación','n','F o q','gl 1','gl 2','p ajustado o p del modelo','η²','Diferencia de medias','IC inferior','IC superior'],rows:inferenceRows(inference)};views.partial=partial;}
    root.replaceChildren();
    const viewLabel=make('label','Vista de datos '),view=make('select');for(const [key,v] of Object.entries(views)){const o=make('option',v.label);o.value=key;view.append(o)}viewLabel.append(view);
    const searchLabel=make('label','Buscar grado SAE '),search=make('input');search.type='search';searchLabel.append(search);
    const seriesLabel=make('label','Serie o familia '),series=make('select');seriesLabel.append(series);
    const seriesOptions=[['all','Todas las series']];for(const kind of ['main','family']){const vals=[...new Set(records.map(r=>gradeParts(r['SAE Grade'])?.[kind]).filter(Boolean))].sort();for(const v of vals)seriesOptions.push([`${kind}:${v}`,v+(kind==='main'?'XXX':'XX')]);}for(const [v,t] of seriesOptions){const o=make('option',t);o.value=v;series.append(o)}
    const processLabel=make('label','Procesamiento '),process=make('select');processLabel.append(process);for(const [v,t] of [['all','Todas las condiciones'],...Object.entries(groupLabels)]){const o=make('option',t);o.value=v;process.append(o)}
    const corrLabel=make('label','Población de correlación '),corrFilter=make('select');corrLabel.append(corrFilter);for(const t of ['Todas las poblaciones','Todos los grupos 1XXX',...groupKeys.map(g=>groupLabels[g])]){const option=make('option',t);option.value=t;corrFilter.append(option)}
    const sortLabel=make('label','Ordenar por '),sort=make('select');sortLabel.append(sort);const directionLabel=make('label','Dirección '),direction=make('select');for(const [v,t] of [['asc','Ascendente'],['desc','Descendente']]){const o=make('option',t);o.value=v;direction.append(o)}directionLabel.append(direction);
    const reset=make('button','Restablecer filtros');reset.type='button';const exportButton=make('button','Descargar CSV');exportButton.type='button';const controls=make('div');controls.className='filter-grid table-controls';controls.append(viewLabel,searchLabel,seriesLabel,processLabel,corrLabel,sortLabel,directionLabel,reset,exportButton);
    const note=make('p');note.className='scope-note';const status=make('p');status.setAttribute('role','status');status.setAttribute('aria-live','polite');const scroll=make('div');scroll.className='table-scroll';scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label','Tabla de resultados desplazable horizontalmente');const table=make('table');scroll.append(table);
    const pagination=make('div');pagination.className='pagination';const previous=make('button','Anterior'),next=make('button','Siguiente'),pageInfo=make('span');previous.type=next.type='button';pagination.append(previous,pageInfo,next);root.append(controls,note,status,scroll,pagination);
    let page=0,currentRows=[];const pageSize=15;
    function updateSort(){sort.replaceChildren(...views[view.value].headers.map((h,i)=>{const o=make('option',h);o.value=String(i);return o}));}
    function render(){const key=view.value,v=views[key],isRecords=key==='records';for(const el of [searchLabel,seriesLabel,processLabel])el.hidden=!isRecords;corrLabel.hidden=key!=='correlations';
      note.textContent=key==='partial'?'Pearson parcial controla carbono nominal y procesamiento mediante residualización; ambos coeficientes usan los mismos casos completos. No implica causalidad.':key==='descriptive'?'Estadísticos de las poblaciones originales; cuartiles con interpolación lineal y desviación estándar muestral.':key==='correlations'?'Correlaciones por pares completos; |ρ| corresponde a Spearman.':key==='inference'?'Resultados de las poblaciones originales fijas, no recalculados por los filtros. Intervalos simultáneos de 95 %. Diferencia: segundo menos primero en Tukey; primero menos segundo en Games–Howell.':'La búsqueda y los filtros de esta tabla no modifican las gráficas.';
      let rows=isRecords?filterRecordRows(source,{query:search.value,series:series.value,processing:process.value}).map(v=>v.raw):v.rows.slice();if(key==='correlations'&&corrFilter.value!=='Todas las poblaciones')rows=rows.filter(r=>r[2]===corrFilter.value);
      const index=Number(sort.value||0);rows.sort((a,b)=>{const av=a[index],bv=b[index];if(av==null||av==='')return bv==null||bv===''?0:1;if(bv==null||bv==='')return -1;const an=Number(av),bn=Number(bv);const cmp=Number.isFinite(an)&&Number.isFinite(bn)?an-bn:String(av).localeCompare(String(bv),'es',{numeric:true});return direction.value==='desc'?-cmp:cmp});currentRows=rows;const pages=Math.max(1,Math.ceil(rows.length/pageSize));page=Math.min(page,pages-1);
      status.textContent=`${rows.length} registros encontrados.`;pageInfo.textContent=`Página ${page+1} de ${pages}`;previous.disabled=page===0;next.disabled=page>=pages-1;
      const head=make('thead'),tr=make('tr');v.headers.forEach(h=>{const th=make('th',h);th.scope='col';tr.append(th)});head.append(tr);const body=make('tbody');for(const row of rows.slice(page*pageSize,(page+1)*pageSize)){const tr=make('tr');row.forEach(value=>{const display=value===null||value===undefined||value===''?'—':typeof value==='number'?Number(value.toPrecision(6)).toString():String(value);tr.append(make('td',display))});body.append(tr)}table.replaceChildren(head,body);
    }
    view.addEventListener('change',()=>{page=0;updateSort();render()});for(const input of [search,series,process,corrFilter,sort,direction])input.addEventListener(input===search?'input':'change',()=>{page=0;render()});
    previous.addEventListener('click',()=>{page--;render()});next.addEventListener('click',()=>{page++;render()});reset.addEventListener('click',()=>{search.value='';series.value='all';process.value='all';corrFilter.selectedIndex=0;direction.value='asc';page=0;updateSort();render()});
    exportButton.addEventListener('click',()=>{const blob=new Blob([csvText(views[view.value].headers,currentRows)],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=make('a');a.href=url;a.download=`aceros-${view.value}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});
    updateSort();render();
  } catch {root.textContent='No fue posible cargar el explorador de tablas. Comprueba el archivo de datos y la conexión al servidor.';}
}
