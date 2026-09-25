const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('techops/static/toolkit/toolkit.js', 'utf8');
function load(saved, blocked=false) {
  const nodes = new Map(), writes = [];
  const document = {body:{dataset:{mode:'demo'}},documentElement:{dataset:{}},getElementById(id){
    if(!nodes.has(id))nodes.set(id,{value:'light',listeners:{},addEventListener(event,fn){this.listeners[event]=fn;}});
    return nodes.get(id);
  }};
  vm.runInNewContext(source,{document,localStorage:{getItem(){if(blocked)throw Error('blocked');return saved;},setItem(key,value){if(blocked)throw Error('blocked');writes.push([key,value]);}},fetch:()=>new Promise(()=>{}),console});
  return {document,nodes,writes};
}
test('restores Neon Night before loading diagnostic data',()=>{
  const app=load('neon');
  assert.equal(app.document.documentElement.dataset.theme,'neon');
  assert.equal(app.nodes.get('theme-select').value,'neon');
});
test('unknown preference falls back to Light',()=>{
  assert.equal(load('unexpected').document.documentElement.dataset.theme,'light');
});
test('theme selector switches both ways and stores only preference',()=>{
  const app=load(null), select=app.nodes.get('theme-select');
  for(const value of ['neon','light']) {select.value=value;select.listeners.change();assert.equal(app.document.documentElement.dataset.theme,value);}
  assert.deepEqual(app.writes,[['techops-theme','neon'],['techops-theme','light']]);
});
test('blocked storage does not break switching or startup',()=>{
  const app=load(null,true),select=app.nodes.get('theme-select');
  select.value='neon';select.listeners.change();
  assert.equal(app.document.documentElement.dataset.theme,'neon');
});
