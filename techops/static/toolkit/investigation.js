'use strict';
// Pure evidence assessment shared by the browser and offline regression tests.
((root) => {
  const books = {
    network: {title:'Internet is not working', steps:[['network','Check adapter, gateway and DNS configuration.'],['dns','Resolve the affected hostname; another name does not test the same service.'],['connections','Inspect the current TCP snapshot for context.']], gaps:['Gateway reachability, Wi-Fi quality and HTTPS are not measured.','Confirm whether other devices and sites are affected; check required VPN access.']},
    health: {title:'Computer is slow', steps:[['health','Look for CPU, memory or disk pressure. Repeat unusual readings.'],['services','Compare the four selected service states with the affected feature.']], gaps:['Per-process resource use and long-term trends are not measured.','Record when the slowdown began and whether it follows a recent change.']},
    services: {title:'Application will not open', steps:[['health','Check system resource pressure before blaming the application.'],['services','Inspect selected Windows services; this is not an application-service inventory.']], gaps:['Application logs, permissions and dependencies still need inspection.','Use the incident workspace for structured logs; capture the exact error and affected version.']},
    connections: {title:'Connection keeps dropping', steps:[['network','Record which adapter and gateway are configured.'],['connections','Capture TCP state while the symptom occurs.'],['dns','Check resolution for the affected hostname.']], gaps:['Packet loss, Wi-Fi signal and disconnect trends are not measured.','Compare readings during and outside the failure; a TCP snapshot cannot prove stability.']}
  };
  function assess(key, evidence, mode, now=Date.now()) {
    const book=books[key];
    if(!book || !['local','demo'].includes(mode)) throw Error('Unknown investigation');
    const steps=book.steps.map(([tool,why])=>{
      const result=evidence.filter(r=>r.tool===tool && r.mode===mode).at(-1);
      let state=result?.status || 'missing';
      if(result){
        const age=now-Date.parse(result.collected_at);
        if(mode==='local' && (!Number.isFinite(age)||age<0||age>600000)) state='stale';
        else if(!['observed','issue','not_checked','unavailable'].includes(state)) state='unavailable';
        else if(state==='observed' && !result.readings?.length) state='not_checked';
      }
      return {tool,why,state,result};
    });
    return {title:book.title,mode,steps,gaps:book.gaps,
      usable:steps.filter(s=>s.state==='observed'||s.state==='issue').length,
      review:steps.filter(s=>s.state==='issue').length,
      missing:steps.filter(s=>s.state==='missing').length,
      conclusion:'These snapshots do not establish a root cause or verify recovery. Confirm the original user task after any approved fix.'};
  }
  const safe=value=>String(value ?? 'Not recorded').slice(0,4000).replace(/[\x00-\x08\x0b-\x1f]/g,'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/[\\`*_[\]#|]/g,'\\$&');
  function report(a, context={}, now=Date.now()) {
    const lines=['# Technical operations handoff','Author: Armando Gomez',`Generated: ${new Date(now).toISOString()}`,`Mode: ${a.mode==='demo'?'SYNTHETIC DEMO — not device readings':'LOCAL — private details may be included'}`,'',`## Symptom: ${safe(a.title)}`,
      `Impact / affected users: ${safe(context.impact || 'Not recorded')}`,`Started / recent changes: ${safe(context.change || 'Not recorded')}`,'Priority: Not assigned; confirm business impact and urgency.','Recovery: Not verified.','Root cause: Not established.','','## Evidence'];
    a.steps.forEach((s,i)=>{
      lines.push(`### E${i+1}: ${s.tool} — ${s.state}`,s.why);
      if(s.result){lines.push(`Collected: ${safe(s.result.collected_at)}`);if(s.result.hostname)lines.push(`Queried hostname: ${safe(s.result.hostname)}`);lines.push(safe(s.result.summary));if(s.result.truncated)lines.push('Partial snapshot: readings were truncated.');}
      else lines.push('No matching result collected for this investigation.');
    });
    lines.push('','## Evidence gaps and next steps',...a.gaps.map(g=>'- '+g),'','## Handoff and recovery verification','- Assign an owner and agree the next update time.','- Escalate ongoing widespread outages or suspected data/security impact through your organization\'s incident process.','- Record any approved change, then repeat the original user task and relevant checks.','- Keep suspected causes separate from confirmed evidence; record follow-up prevention work.',a.conclusion,'','Privacy: review before sharing. Notes and diagnostic summaries are not automatically redacted. Raw reading tables are excluded; export individual checks when needed.');
    return lines.join('\n')+'\n';
  }
  const api={books,assess,report};
  if(typeof module!=='undefined' && module.exports) module.exports=api;
  else root.TechOpsInvestigation=api;
})(globalThis);
