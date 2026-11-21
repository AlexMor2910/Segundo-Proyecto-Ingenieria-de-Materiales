// Lightweight DOM simulation for table state transitions; browser layout is separate.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { parseCSV } from '../js/data.js';
import { initializeTables } from '../js/tables.js';
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.listeners={}; this.attributes={}; this.value=''; this.style={}; this.hidden=false; this.textContent=''; }
  setAttribute(k,v) { this.attributes[k]=v; }
  set selectedIndex(i) { this.value=this.children[i]?.value ?? ''; }
  append(...items) { for(const item of items) { this.children.push(item); if(this.tag==='select' && this.children.length===1) this.value=item.value; } }
  replaceChildren(...items) { this.children=[]; this.append(...items); }
  addEventListener(k,fn) { this.listeners[k]=fn; }
  click() { this.listeners.click?.(); }
}
const root=new Element('root');
globalThis.document={querySelector:()=>root,createElement:tag=>new Element(tag)};
const text=fs.readFileSync(new URL('../data/steels.csv',import.meta.url),'utf8');
globalThis.fetch=async()=>({ok:true,text:async()=>text});
const csv=parseCSV(text),headers=csv.shift(),numeric=new Set(['UTS (MPa)','YS (MPa)','Hardness (HB)','Elongation (%)','Reduction (%)','C (%)']);
const records=csv.map(row=>Object.fromEntries(headers.map((h,i)=>[h,row[i]===''?null:numeric.has(h)?Number(row[i]):row[i]])));
await initializeTables(records,headers);
const [controls,,status,scroll,pagination]=root.children;
const [viewLabel,searchLabel,seriesLabel,,corrLabel,sortLabel,directionLabel,reset]=controls.children;
const view=viewLabel.children[0],search=searchLabel.children[0],series=seriesLabel.children[0];
assert.equal(status.textContent,'190 registros encontrados.');
assert.equal(scroll.children[0].children[1].children.length,15);
pagination.children[2].click(); assert.equal(pagination.children[1].textContent,'Página 2 de 13');
search.value='1006';search.listeners.input();assert.equal(status.textContent,'2 registros encontrados.');
series.value='family:10';series.listeners.change();assert.equal(status.textContent,'2 registros encontrados.');
reset.click();assert.equal(status.textContent,'190 registros encontrados.');
view.value='correlations';view.listeners.change();assert.equal(status.textContent,'40 registros encontrados.');
const population=corrLabel.children[0];population.value='Laminado en caliente';population.listeners.change();assert.equal(status.textContent,'10 registros encontrados.');
sortLabel.children[0].value='4';sortLabel.children[0].listeners.change();directionLabel.children[0].value='desc';directionLabel.children[0].listeners.change();assert.equal(scroll.children[0].children[1].children.length,10);
console.log('Table state transitions passed.');
