async () => {
  // Evaluate after a LOCAL toolkit catalog loads. DNS calls are mocked.
  const $=id=>document.getElementById(id);
  const assert=(value,message)=>{if(!value)throw Error(message);};
  const original=window.fetch, originalURL=URL.createObjectURL, originalClick=HTMLAnchorElement.prototype.click;
  let requests=[], saved;
  const wait=async()=>{const end=Date.now()+3000;while($('run-tool').disabled&&Date.now()<end)await new Promise(r=>setTimeout(r,20));assert(!$('run-tool').disabled,'Run did not finish');};
  try {
    assert(document.body.dataset.mode==='local','Requires local mode');
    window.fetch=async(...args)=>{
      if(!String(args[0]).includes('/api/tools/run'))return original(...args);
      const request=JSON.parse(args[1].body);requests.push(request);
      await new Promise(r=>setTimeout(r,100));
      return new Response(JSON.stringify({tool:'dns',mode:'local',hostname:request.hostname,elapsed_ms:7,collected_at:'Synthetic browser test',status:'observed',summary:'Synthetic result; no DNS query sent.',readings:[{name:request.hostname,type:'A',answer:'192.0.2.20',ttl_seconds:60}],truncated:false}),{status:200});
    };
    document.querySelector('[data-category="network"]').click();
    [...document.querySelectorAll('.tool-card')].find(n=>n.querySelector('h2').textContent==='Test DNS resolution').querySelector('button').click();
    $('hostname').value='https://example.com';$('run-tool').click();
    assert(requests.length===0&&$('run-status').textContent.includes('ASCII hostname'),'Invalid target was submitted');
    $('hostname').value='Example.COM.';$('run-tool').click();$('hostname').value='changed.example.com';await wait();
    assert(requests.length===1&&requests[0].hostname==='example.com','Normalization incorrect');
    assert($('result-target').textContent.includes('example.com')&&!$('result-target').textContent.includes('changed'),'Wrong target in result');
    $('explain').click();assert(!$('explanation').hidden,'Explanation missing');
    URL.createObjectURL=blob=>{saved=blob;return 'blob:dns-test';};HTMLAnchorElement.prototype.click=()=>{};
    $('export').click();assert(JSON.parse(await saved.text()).hostname==='example.com','Export target changed');
    document.querySelector('[data-category="reports"]').click();
    const entry=[...document.querySelectorAll('.history-item')].find(n=>n.textContent.includes('example.com'));
    assert(entry,'DNS target absent from history');entry.click();assert($('hostname').value==='example.com','History did not restore target');
    return {passed:5,checks:['invalid URL blocked','normalized hostname sent','in-flight edit cannot relabel result','export retains queried hostname','history reopens queried hostname']};
  } finally {window.fetch=original;URL.createObjectURL=originalURL;HTMLAnchorElement.prototype.click=originalClick;}
}
