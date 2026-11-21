import assert from 'node:assert/strict';
import fs from 'node:fs';
import { parseCSV } from '../js/data.js';
import { initializePoint3, properties } from '../js/charts-point3.js';
class Element {constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.attributes={};this.style={};this.value='';this.textContent=''}setAttribute(k,v){this.attributes[k]=String(v)}append(...items){this.children.push(...items)}replaceChildren(...items){this.children=items}addEventListener(k,f){this.listeners[k]=f}focus(){this.focused=true}}
const ids={};for(const id of ['p3-controls','p3-population','p3-matrix','p3-ranking','p3-summary','p3-scatter','p3-tooltip','p3-explanation','p3-comparison','p3-partial'])ids[id]=new Element(id);
const form=ids['p3-controls'];form.elements={method:new Element('select'),group:new Element('select'),sign:new Element('select'),x:new Element('select'),y:new Element('select')};form.elements.method.value='spearman';form.elements.group.value='all';form.elements.sign.value='all';
globalThis.document={querySelector:q=>ids[q.slice(1)],createElement:t=>new Element(t),createElementNS:(_,t)=>new Element(t)};
const rows=parseCSV(fs.readFileSync(new URL('../data/steels.csv',import.meta.url),'utf8')),headers=rows.shift();
const data=rows.map(row=>Object.fromEntries(headers.map((h,i)=>[h,row[i]===''?null:properties.includes(h)||h==='C (%)'?Number(row[i]):row[i]])));
initializePoint3(data);
let buttons=ids['p3-ranking'].children.map(row=>row.children[0]);assert.equal(buttons.length,10);
assert.ok(buttons.every(button=>/^[+−]\d\.\d{4}$/.test(button.textContent)));
assert.ok(buttons.every(button=>button.attributes['aria-label'].includes('n =')));
buttons[1].listeners.click();assert.ok(ids['p3-summary'].textContent.includes('Spearman ρ'));assert.ok(ids['p3-summary'].textContent.includes('n = 138'));assert.ok(ids['p3-summary'].textContent.includes(' y '));assert.equal(ids['p3-summary'].focused,true);
form.elements.method.value='pearson';form.elements.group.value='Cold drawn';form.listeners.change({target:form.elements.group});buttons=ids['p3-ranking'].children.map(row=>row.children[0]);assert.ok(buttons[0].attributes['aria-label'].includes('Pearson'));assert.ok(ids['p3-summary'].textContent.includes('n = 52'));
console.log('Ranking labels, selection and filter synchronization passed.');
