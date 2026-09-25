'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const local = document.body.dataset.mode === 'local';
  let catalog, fixtures, currentCategory, currentTool, currentResult, busy = false, activeView = 'overview';
  const history = [];
  const label = {observed:'Observed', issue:'Review needed', not_checked:'Not checked', unavailable:'Unavailable'};
  const incidentUrl = local ? './incidents' : './incidents.html';

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function button(text, className, action) {
    const node = element('button', text, className);
    node.type = 'button';
    node.addEventListener('click', action);
    return node;
  }
  function show(view, title) {
    activeView = view;
    for (const id of ['overview','category-view','tool-view']) $(id).hidden = id !== view;
    $('breadcrumb').textContent = title;
    document.querySelectorAll('.nav-item').forEach(node => node.classList.toggle('active', node.dataset.category === currentCategory && view !== 'overview'));
    $('home').classList.toggle('active', view === 'overview');
    document.querySelectorAll('.nav-item').forEach(node => {
      if (node.classList.contains('active')) node.setAttribute('aria-current', 'page');
      else node.removeAttribute('aria-current');
    });
    const heading = $(view).querySelector('h1');
    heading.tabIndex = -1;
    heading.focus({preventScroll:true});
    window.scrollTo({top:0, behavior:'instant'});
  }
  function home() { show('overview', 'Overview'); }
  function category(id) {
    currentCategory = id;
    const item = catalog.categories.find(c => c.id === id);
    $('category-title').textContent = item.title;
    $('category-description').textContent = item.description;
    $('tool-list').replaceChildren(...item.tools.map(key => {
      const tool = catalog.tools[key];
      const card = element('article', undefined, 'tool-card');
      const state = tool.availability === 'ready' ? (local ? 'AVAILABLE · WINDOWS' : 'AVAILABLE · DEMO') : tool.availability === 'link' ? 'OPEN WORKSPACE' : 'PLANNED';
      card.append(element('span', state, 'tool-state'), element('h2', tool.title), element('p', tool.description));
      if (tool.availability === 'ready') card.append(button('Open tool ↗', 'secondary', () => openTool(key)));
      else if (tool.availability === 'link') {
        const link = element('a', 'Open incident workspace ↗', 'secondary');
        link.href = incidentUrl + (key === 'history' && local ? '#history' : '');
        card.append(link);
      } else card.append(element('span', 'Not available in this release', 'planned-note'));
      return card;
    }));
    $('session-history').hidden = id !== 'reports';
    refreshHistory();
    show('category-view', item.title);
  }
  function refreshHistory() {
    $('history-list').replaceChildren(...(history.length ? history.slice().reverse().map((entry, index) => button(`${catalog.tools[entry.tool].title} · ${label[entry.status]} · #${history.length-index}`, 'history-item', () => { openTool(entry.tool); render(entry); })) : [element('p', 'No checks run in this session yet.', 'muted')]));
  }
  function openTool(id) {
    currentTool = id;
    const tool = catalog.tools[id];
    if (!currentCategory || !catalog.categories.find(c => c.id === currentCategory).tools.includes(id)) currentCategory = catalog.categories.find(c => c.tools.includes(id)).id;
    $('tool-category').textContent = catalog.categories.find(c => c.id === currentCategory).title.toUpperCase();
    $('tool-title').textContent = tool.title;
    $('tool-description').textContent = tool.description;
    $('tool-limit').textContent = tool.limit;
    $('tool-help').textContent = tool.help;
    $('next-tool').textContent = catalog.tools[tool.next].title + ' →';
    $('run-tool').textContent = local ? 'Run local check ↗' : 'Run demo check ↗';
    $('run-tool').disabled = busy;
    $('run-status').textContent = busy ? 'Another check is running. Wait for it to finish.' : local ? 'Ready. This reads your Windows computer when you click Run.' : 'Ready. This displays a synthetic example, not your computer.';
    $('result-panel').hidden = true;
    $('result-empty').hidden = false;
    $('explanation').hidden = true;
    currentResult = null;
    show('tool-view', `${$('tool-category').textContent} / ${tool.title}`);
  }
  function render(result) {
    currentResult = result;
    $('result-panel').hidden = false;
    $('result-empty').hidden = true;
    $('explanation').hidden = true;
    $('result-state').textContent = label[result.status] || 'Unknown';
    $('result-state').className = 'state ' + result.status;
    $('result-time').textContent = `${result.mode === 'demo' ? 'SYNTHETIC EXAMPLE' : 'LOCAL SNAPSHOT'} · ${result.collected_at}`;
    $('result-summary').textContent = result.summary;
    $('truncated').hidden = !result.truncated;
    $('readings').replaceChildren();
    if (result.readings.length) {
      const table = element('table');
      const header = element('thead');
      const tr = element('tr');
      const fields = Object.keys(result.readings[0]);
      fields.forEach(field => { const th = element('th', field.replaceAll('_',' ')); th.scope = 'col'; tr.append(th); });
      header.append(tr);
      const body = element('tbody');
      result.readings.forEach(row => {
        const line = element('tr');
        fields.forEach(field => { const value = row[field]; line.append(element('td', Array.isArray(value) ? value.join(', ') || 'Not reported' : value == null ? 'Not reported' : String(value))); });
        body.append(line);
      });
      table.append(header,body);
      $('readings').append(table);
    } else $('readings').append(element('p', 'No readings available. Do not treat this as a passed check.', 'muted'));
    $('export-note').textContent = local ? 'Saved reports can contain local IP addresses, DNS settings and process names. Review before sharing. Nothing is uploaded.' : 'The exported report contains only synthetic demo data.';
  }
  async function run() {
    if (busy) return;
    const tool = currentTool;
    busy = true;
    $('run-tool').disabled = true;
    $('result-panel').hidden = true;
    $('explanation').hidden = true;
    $('result-empty').hidden = false;
    currentResult = null;
    $('run-status').textContent = local ? 'Reading local Windows information… up to 12 seconds.' : 'Loading the synthetic example…';
    try {
      let result;
      if (local) {
        const response = await fetch('./api/tools/run', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({tool}), signal:AbortSignal.timeout(16000)});
        if (!response.ok) throw new Error(response.status === 409 ? 'Another check is running. Try again shortly.' : 'The local check could not complete. Verify the backend is running, then retry.');
        result = await response.json();
      } else result = structuredClone(fixtures[tool]);
      if (!result || result.tool !== tool || !Array.isArray(result.readings)) throw new Error('Unexpected result. No readings can be displayed.');
      history.push(result);
      if (history.length > 50) history.shift();
      $('session-count').replaceChildren(document.createTextNode(String(history.length).padStart(2,'0')+' '), element('small','checks retained'));
      refreshHistory();
      if (currentTool === tool && activeView === 'tool-view') { render(result); $('run-status').textContent = result.status === 'unavailable' ? 'Check unavailable. Review the details below.' : 'Check complete. Readings describe the recorded snapshot only.'; }
      else $('global-status').textContent = `${catalog.tools[tool].title} finished. Open Reports & history to review it.`;
    } catch (error) {
      const message = error.name === 'TimeoutError' ? 'The request timed out. No result was recorded; retry after the current check finishes.' : error.message;
      if (currentTool === tool && activeView === 'tool-view') $('run-status').textContent = message;
      else $('global-status').textContent = message;
    } finally {
      busy = false;
      $('run-tool').disabled = false;
      if (currentTool !== tool) $('run-status').textContent = 'Ready. Run this tool to collect its own readings.';
    }
  }
  $('home').addEventListener('click', home);
  $('category-back').addEventListener('click', home);
  $('tool-back').addEventListener('click', () => category(currentCategory));
  $('run-tool').addEventListener('click', run);
  $('next-tool').addEventListener('click', () => openTool(catalog.tools[currentTool].next));
  $('explain').addEventListener('click', () => {
    if (!currentResult) return;
    $('explanation-text').textContent = currentResult.summary + ' ' + catalog.tools[currentTool].help;
    $('explanation').hidden = false;
  });
  $('export').addEventListener('click', () => {
    if (!currentResult) return;
    const report = {author:'Armando Gomez', title:catalog.tools[currentTool].title, ...currentResult, limitations:catalog.tools[currentTool].limit};
    const url = URL.createObjectURL(new Blob([JSON.stringify(report,null,2)+'\n'], {type:'application/json'}));
    const link = element('a');
    link.href = url; link.download = `techops-${currentResult.mode}-${currentTool}.json`;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  async function init() {
    try {
      const response = await fetch(local ? './api/tools/catalog' : './catalog.json', {credentials:'omit'});
      if (!response.ok) throw new Error('Catalog unavailable');
      catalog = await response.json();
      if (!local) {
        const demoResponse = await fetch('./demo.json', {credentials:'omit'});
        if (!demoResponse.ok) throw new Error('Examples unavailable');
        fixtures = await demoResponse.json();
      }
      catalog.categories.forEach(item => {
        const nav = button(`${item.icon}  ${item.title}`, 'nav-item', () => category(item.id));
        nav.dataset.category = item.id;
        $('navigation').append(nav);
        const card = button('', 'category-card', () => category(item.id));
        card.append(element('span', item.icon, 'category-icon'), element('h3', item.title), element('p', item.description), element('span','Explore tools ↗','card-link'));
        $('category-cards').append(card);
      });
      catalog.shortcuts.forEach(item => $('shortcuts').append(button(item.title + ' →', 'shortcut', () => { currentCategory = 'troubleshoot'; openTool(item.tool); })));
      if (local) {
        $('rail-mode').textContent = 'LOCAL WORKSPACE';
        $('rail-description').textContent = 'Read-only Windows checks. Results stay in this tab unless you save a report.';
        $('mode-badge').textContent = 'LOCAL · WINDOWS TOOLS';
        $('scope-text').textContent = 'Checks run only when requested. Results stay in this tab’s memory. No remediation or AI inference runs. Some tools require Windows permissions.';
      }
      $('global-status').textContent = local ? 'Ready to collect local readings on demand.' : 'Interactive demo · All readings are synthetic. Your computer is not inspected.';
    } catch {
      $('global-status').textContent = 'The toolkit could not load. Reload to retry. No checks have been performed.';
      $('home').disabled = true;
    }
  }
  init();
})();
