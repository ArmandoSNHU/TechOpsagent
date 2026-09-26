async () => {
  const $=id=>document.getElementById(id);
  const assert=(ok,text)=>{if(!ok)throw Error(text);};
  const wait=async()=>{const end=Date.now()+4000;while($('run-tool').disabled&&Date.now()<end)await new Promise(r=>setTimeout(r,20));assert(!$('run-tool').disabled,'Check did not finish');};
  const local=document.body.dataset.mode==='local';
  const original=window.fetch, create=URL.createObjectURL, click=HTMLAnchorElement.prototype.click;
  let saved, fail=false, requests=0;
  try {
    if(local)window.fetch=async(...args)=>{
      if(!String(args[0]).includes('/api/tools/run'))return original(...args);
      requests++;await new Promise(r=>setTimeout(r,60));
      if(fail)throw Error('Synthetic transport failure');
      const body=JSON.parse(args[1].body);
      return new Response(JSON.stringify({tool:body.tool,hostname:body.hostname,mode:'local',collected_at:new Date().toISOString(),status:'observed',summary:'Synthetic browser test; no machine collection.',readings:[{value:1}]}));
    };
    $('home').click();document.querySelectorAll('.shortcut')[0].click();
    assert($('guide-counts').textContent.startsWith('0/3'),'Fresh investigation not empty');
    $('guide-impact').value='<img src=x> [link](https://example.com)';
    document.querySelector('#guide-steps button').click();$('run-tool').click();await wait();$('return-guide').click();
    assert($('guide-counts').textContent.startsWith('1/3'),'Result missing from brief');
    assert($('guide-impact').value.includes('<img'),'Context lost on navigation');
    document.querySelectorAll('#guide-steps button')[1].click();
    if(local)$('hostname').value='example.com';else $('dns-example').value='dns_failure';
    $('run-tool').click();await wait();$('return-guide').click();
    assert($('guide-counts').textContent.startsWith('2/3'),'DNS result not counted');
    if(!local)assert($('guide-counts').textContent.includes('1 need review'),'DNS failure hidden');
    URL.createObjectURL=blob=>{saved=blob;return 'blob:synthetic-test';};HTMLAnchorElement.prototype.click=function(){};
    $('save-handoff').click();const text=await saved.text();
    assert(text.includes('Recovery: Not verified.')&&text.includes('E2: dns'),'Handoff missing uncertainty/evidence');
    assert(!text.includes('<img')&&!text.includes('[link]('),'Unescaped note in report');
    if(local){fail=true;document.querySelector('#guide-steps button').click();$('run-tool').click();await wait();$('return-guide').click();assert(document.querySelector('.investigation-step').textContent.includes('Unavailable'),'Failed request retained old success');}
    $('guide-home').click();document.querySelectorAll('.shortcut')[1].click();
    assert($('guide-counts').textContent.startsWith('0/2')&&!$('guide-impact').value,'New investigation leaked old evidence/context');
    assert(!document.querySelector('#investigation-view img'),'Notes executed as HTML');
    return {mode:local?'local (mocked collectors)':'demo',checks:7,passed:true,requests,overflow:document.documentElement.scrollWidth>innerWidth};
  }finally{window.fetch=original;URL.createObjectURL=create;HTMLAnchorElement.prototype.click=click;}
}
