const {test}=require('node:test');
const assert=require('node:assert/strict');
const {assess,report,books}=require('../techops/static/toolkit/investigation.js');
const now=Date.parse('2026-09-26T12:00:00Z');
const sample=(tool,status='observed',extra={})=>({tool,status,mode:'local',collected_at:new Date(now).toISOString(),summary:'A snapshot only.',readings:[{value:1}],...extra});
test('all four symptoms have ordered checks and explicit evidence gaps',()=>{
 assert.equal(Object.keys(books).length,4);
 for(const key of Object.keys(books)){const a=assess(key,[],'local',now);assert.equal(a.usable,0);assert.equal(a.missing,a.steps.length);assert.ok(a.gaps.length);}
});
test('latest failed attempt supersedes an older usable result',()=>{
 const a=assess('network',[sample('network'),sample('network','unavailable')],'local',now);
 assert.equal(a.steps[0].state,'unavailable');assert.equal(a.usable,0);
});
test('synthetic readings never count as local evidence',()=>{
 const a=assess('network',[sample('network','observed',{mode:'demo'})],'local',now);
 assert.equal(a.steps[0].state,'missing');
});
test('old, invalid and future timestamps are not current evidence',()=>{
 for(const collected_at of ['2020-01-01','invalid','2027-01-01']) {
 const a=assess('health',[sample('health','observed',{collected_at})],'local',now);
 assert.equal(a.steps[0].state,'stale');assert.equal(a.usable,0);
 }
});
test('empty readings cannot become successful evidence',()=>{
 const a=assess('health',[sample('health','observed',{readings:[]})],'local',now);
 assert.equal(a.steps[0].state,'not_checked');
});
test('DNS failure remains reviewable despite no returned records',()=>{
 const a=assess('network',[sample('dns','issue',{readings:[],hostname:'missing.example.invalid'})],'local',now);
 assert.equal(a.review,1);assert.equal(a.steps[1].result.hostname,'missing.example.invalid');
});
test('complete snapshots never assert root cause or recovery',()=>{
 const a=assess('health',[sample('health'),sample('services')],'local',now);
 assert.equal(a.usable,2);assert.match(a.conclusion,/not establish.*root cause.*recovery/i);
});
test('handoff preserves evidence, mode and limitations and escapes untrusted notes',()=>{
 const a=assess('network',[sample('dns','issue',{hostname:'missing.example.invalid',readings:[]})],'local',now);
 const out=report(a,{impact:'<img src=x> [click](https://example.com)',change:'unknown'},now);
 assert.match(out,/missing.example.invalid/);assert.match(out,/LOCAL/);assert.match(out,/Not verified/);
 assert.ok(!out.includes('<img'));assert.ok(!out.includes('[click]('));assert.match(out,/Armando Gomez/);
});
test('demo timestamps are explicitly synthetic and do not expire',()=>{
 const a=assess('health',[sample('health','observed',{mode:'demo',collected_at:'Synthetic example'})],'demo',now);
 assert.equal(a.usable,1);assert.match(report(a,{},now),/SYNTHETIC/);
});
