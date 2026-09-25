async () => {
  // Run in a freshly loaded LOCAL toolkit tab after the catalog loads.
  // All diagnostic responses below are synthetic; no collector is invoked.
  const $ = id => document.getElementById(id);
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const originalFetch = window.fetch;
  const originalCreate = URL.createObjectURL;
  const originalClick = HTMLAnchorElement.prototype.click;
  let fail = false, saved;
  const results = [];
  const wait = async () => {
    const deadline = Date.now() + 3000;
    while ($('run-tool').disabled && Date.now() < deadline) await new Promise(r => setTimeout(r, 20));
    assert(!$('run-tool').disabled, 'Run remained disabled');
  };
  const open = (category, title) => {
    document.querySelector(`[data-category="${category}"]`).click();
    [...document.querySelectorAll('.tool-card')].find(c => c.querySelector('h2').textContent === title).querySelector('button').click();
  };
  assert(document.body.dataset.mode === 'local', 'Use a local-mode tab');
  try {
    window.fetch = async (...args) => {
      if (!String(args[0]).includes('/api/tools/run')) return originalFetch(...args);
      const tool = JSON.parse(args[1].body).tool;
      await new Promise(r => setTimeout(r, 100));
      if (fail) return new Response('{}', {status:503});
      return new Response(JSON.stringify({tool,mode:'local',collected_at:'Synthetic browser test',status:'observed',summary:'Synthetic test; no device inspected.',readings:[{adapter:'<img src=x onerror=alert(1)>',ipv4:['192.0.2.10'],gateway:[],dns:[]}],truncated:false}), {status:200});
    };
    open('network', 'Check my network');
    assert(document.activeElement.id === 'tool-title', 'Navigation must focus the tool heading');
    $('run-tool').click(); await wait();
    assert(!$('result-panel').hidden && $('readings').querySelectorAll('tbody tr').length === 1, 'Result missing');
    assert(!$('readings').querySelector('img'), 'Reading became HTML');
    $('explain').click(); assert(!$('explanation').hidden, 'Explanation missing');
    results.push('result, text-only rendering, explanation, navigation focus');
    URL.createObjectURL = blob => { saved = blob; return 'blob:synthetic-test'; };
    HTMLAnchorElement.prototype.click = () => {};
    $('export').click();
    assert(JSON.parse(await saved.text()).tool === 'network', 'Export belongs to wrong tool');
    results.push('JSON export matches displayed tool');
    const before = Number($('session-count').textContent.match(/\d+/)[0]);
    $('run-tool').click(); document.querySelector('[data-category="reports"]').click(); await wait();
    assert(document.querySelectorAll('.history-item').length === before + 1, 'Visible history was not refreshed');
    assert($('global-status').textContent.includes('finished'), 'Background completion hidden');
    results.push('history refresh during background completion');
    open('network', 'Check my network'); $('run-tool').click(); open('computer','Check computer health'); await wait();
    assert($('result-panel').hidden && $('tool-title').textContent === 'Check computer health', 'Result mislabeled after tool switch');
    results.push('in-flight results cannot overwrite a different tool');
    fail = true; $('run-tool').click(); document.querySelector('[data-category="reports"]').click(); await wait();
    assert($('global-status').textContent.includes('could not complete'), 'Background failure was hidden');
    results.push('background failure visible without success result');
    return {passed:results.length, checks:results};
  } finally {
    window.fetch = originalFetch;
    URL.createObjectURL = originalCreate;
    HTMLAnchorElement.prototype.click = originalClick;
  }
}
