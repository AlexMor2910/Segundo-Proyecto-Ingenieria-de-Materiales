import assert from 'node:assert/strict';
import fs from 'node:fs';
import { parseCSV } from '../js/data.js';
import { correlationColor, initializePoint3, point3Population, properties, propertyNames, rankPairs } from '../js/charts-point3.js';
class Element {constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.attributes={};this.style={};this.value='';this.textContent=''}setAttribute(k,v){this.attributes[k]=String(v)}append(...items){this.children.push(...items)}replaceChildren(...items){this.children=items}addEventListener(k,f){this.listeners[k]=f}focus(){this.focused=true}}
const ids={};for(const id of ['p3-controls','p3-population','p3-matrix','p3-ranking','p3-summary','p3-scatter','p3-tooltip','p3-explanation','p3-comparison','p3-partial'])ids[id]=new Element(id);
const form=ids['p3-controls'];form.elements={method:new Element('select'),group:new Element('select'),sign:new Element('select'),x:new Element('select'),y:new Element('select')};form.elements.method.value='spearman';form.elements.group.value='all';form.elements.sign.value='all';
globalThis.document={querySelector:q=>ids[q.slice(1)],createElement:t=>new Element(t),createElementNS:(_,t)=>new Element(t)};
const rows=parseCSV(fs.readFileSync(new URL('../data/steels.csv',import.meta.url),'utf8')),headers=rows.shift();
const data=rows.map(row=>Object.fromEntries(headers.map((h,i)=>[h,row[i]===''?null:properties.includes(h)||h==='C (%)'?Number(row[i]):row[i]])));
initializePoint3(data);
function checkRanking(method, symbol) {
  const expected = rankPairs(point3Population(data), method);
  const buttons = ids['p3-ranking'].children.map(row => row.children[0]);
  assert.equal(buttons.length, 10);
  buttons.forEach((button, i) => {
    const { x, y, value, n } = expected[i];
    const pair = `${propertyNames[x]} — ${propertyNames[y]}`;
    const signed = `${value < 0 ? '−' : '+'}${Math.abs(value).toFixed(4)}`;
    assert.equal(button.tag, 'button');
    assert.equal(button.type, 'button');
    assert.deepEqual(button.children.map(child => child.textContent), [pair, `${symbol} = ${signed}`]);
    assert.ok(button.attributes['aria-label'].includes(`n = ${n}`));
    assert.equal(button.style.backgroundColor, correlationColor(value));
  });
  return buttons;
}
let buttons = checkRanking('spearman', 'ρ');
assert.equal(buttons[0].children[1].textContent, 'ρ = +0.9914');
buttons[1].listeners.click();assert.ok(ids['p3-summary'].textContent.includes('Spearman ρ'));assert.ok(ids['p3-summary'].textContent.includes('n = 138'));assert.ok(ids['p3-summary'].textContent.includes(' y '));assert.equal(ids['p3-summary'].focused,true);
form.elements.method.value='pearson';
form.listeners.change({target:form.elements.method});
buttons = checkRanking('pearson', 'r');
assert.equal(buttons[0].children[1].textContent, 'r = +0.9946');
form.elements.group.value='Cold drawn';form.listeners.change({target:form.elements.group});assert.ok(ids['p3-ranking'].children[0].children[0].attributes['aria-label'].includes('Pearson'));assert.ok(ids['p3-summary'].textContent.includes('n = 52'));
console.log('Ranking labels, selection and filter synchronization passed.');
