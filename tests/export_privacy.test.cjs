const {test}=require('node:test');
const assert=require('node:assert/strict');
const {assess,report,exportDiagnostic}=require('../techops/static/toolkit/investigation.js');
const marker='PRIVATE_SENTINEL 10.4.5.6 host.internal C:\\Users\\Person';
test('diagnostic export drops arbitrary metadata and nested private readings',()=>{
 const input={tool:'dns',mode:'local',status:'observed',hostname:marker,summary:marker,collected_at:marker,notes:marker,readings:[{answer:marker,process:marker}],truncated:true};
 const out=exportDiagnostic(input);
 assert.equal(out.tool,'dns');assert.equal(out.reading_count,1);assert.equal(out.truncated,true);
 assert.ok(!JSON.stringify(out).includes('PRIVATE_SENTINEL'));assert.equal(input.hostname,marker);
});
test('unrecognized strings cannot bypass diagnostic export allowlist',()=>{
 const out=exportDiagnostic({tool:marker,status:marker,mode:marker,readings:[]});
 assert.ok(!JSON.stringify(out).includes('PRIVATE_SENTINEL'));
});
test('handoff excludes notes and all result free text in either mode',()=>{
 for(const mode of ['local','demo']){
  const a=assess('network',[{tool:'dns',mode,status:'issue',hostname:marker,summary:marker,collected_at:marker,readings:[]}],mode);
  const out=report(a,{impact:marker,change:marker});
  assert.ok(!out.includes('host.internal'));assert.ok(!out.includes('10.4.5.6'));assert.match(out,/omitted/);
 }
});
