import assert from 'node:assert/strict';
import fs from 'node:fs';
import { selectMeanIntervals, selectPosthoc, initializeMeanInference } from '../js/charts-anova.js';
const verified=JSON.parse(fs.readFileSync(new URL('../data/statistical-results.json',import.meta.url),'utf8'));
const intervals=JSON.parse(fs.readFileSync(new URL('../data/mean-ci.json',import.meta.url),'utf8'));
const props=['UTS (MPa)','YS (MPa)','Hardness (HB)','Elongation (%)'];
assert.equal(intervals.groups.length,24);
for(const mode of ['1xxx','other'])for(const property of props){const rows=selectMeanIntervals(intervals,verified,mode,property);assert.equal(rows.length,3);assert.equal(selectPosthoc(verified,mode,property).length,3);assert.ok(selectPosthoc(verified,mode,property).every(r=>r.method===(mode==='other'&&property!=='YS (MPa)'?'Tukey':'Games–Howell')));}
const anchor=selectMeanIntervals(intervals,verified,'1xxx','UTS (MPa)')[0];
assert.ok(Math.abs(anchor.low-502.26086493497627)<1e-8);assert.ok(Math.abs(anchor.high-575.4314427573313)<1e-8);
assert.equal(selectMeanIntervals({...intervals,input_sha256:'incorrecto'},verified,'1xxx','UTS (MPa)'),null);
assert.equal(selectMeanIntervals({...intervals,groups:[]},verified,'1xxx','UTS (MPa)'),null);
assert.ok(selectPosthoc(verified,'1xxx','YS (MPa)').some(r=>r.p===0));

class Element {constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.listeners={};this.textContent='';this.hidden=false;}setAttribute(k,v){this.attributes[k]=String(v)}append(...children){this.children.push(...children)}replaceChildren(...children){this.children=children}addEventListener(k,f){this.listeners[k]=f}}
const ids={};for(const id of ['mean-inference','processing-filters','mean-chart','mean-values','mean-posthoc'])ids[id]=new Element(id);
const form=ids['processing-filters'];form.elements={mode:{value:'1xxx'},property:{value:'UTS (MPa)'}};
globalThis.document={querySelector:q=>ids[q.slice(1)],createElement:t=>new Element(t),createElementNS:(_,t)=>new Element(t)};
globalThis.fetch=async()=>({ok:true,json:async()=>intervals});await initializeMeanInference(verified);
assert.equal(ids['mean-inference'].hidden,false);assert.equal(ids['mean-values'].children.length,3);assert.equal(ids['mean-posthoc'].children.length,3);
assert.equal(ids['mean-chart'].children.filter(x=>x.tag==='g').length,3);
assert.ok(ids['mean-posthoc'].children.some(row=>row.children.some(c=>c.textContent==='Sin evidencia de diferencia significativa')));
form.elements.mode.value='other';form.elements.property.value='YS (MPa)';form.listeners.change();
assert.equal(ids['mean-values'].children[0].children[0].textContent,'Recocido');
assert.equal(ids['mean-posthoc'].children[0].children[1].textContent,'Games–Howell');
form.elements.property.value='UTS (MPa)';form.listeners.change();assert.equal(ids['mean-posthoc'].children[0].children[1].textContent,'Tukey');
console.log('Mean intervals, scope checks, post hoc selection and control synchronization passed.');
