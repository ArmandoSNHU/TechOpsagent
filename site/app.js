/* Public fixture viewer. No credentials, telemetry, storage, or backend calls. */
'use strict';
const $ = id => document.getElementById(id);
let scenarios;
let selected;
const keys = ['api_error', 'dependency_timeout', 'invalid_credential'];
const shortTitles = ['Checkout API failure', 'Inventory timeout', 'Credential rejected'];
const numbers = ['01', '02', '03'];

function selectCase(key) {
  selected = key;
  const item = scenarios[key];
  const index = keys.indexOf(key);
  $('case-id').textContent = `CASE ${numbers[index]} / SYNTHETIC`;
  for (const [id, field] of [['case-title', 'title'], ['description', 'description'], ['service', 'service'], ['severity', 'severity']]) {
    $(id).textContent = item[field];
  }
  document.querySelectorAll('.incident').forEach(button => {
    button.setAttribute('aria-pressed', String(button.dataset.case === key));
  });
  $('results').hidden = true;
  $('empty').hidden = false;
  $('reset').hidden = true;
  $('investigate').disabled = false;
  $('status').textContent = 'Ready to explore · bundled synthetic evidence';
  $('download').removeAttribute('href');
}

function investigate() {
  const item = scenarios[selected];
  $('evidence-list').replaceChildren(...item.evidence.map((evidence, index) => {
    const row = document.createElement('article');
    row.className = 'evidence-row';
    const state = document.createElement('span');
    state.className = `signal-state ${evidence.state}`;
    state.textContent = evidence.state === 'passed' ? '✓' : '!';
    state.setAttribute('aria-label', evidence.state === 'passed' ? 'Healthy observation' : 'Failure observation');
    const body = document.createElement('div');
    const source = document.createElement('p');
    source.className = 'evidence-source';
    source.textContent = `E0${index + 1} / ${evidence.source}`;
    const signal = document.createElement('h4');
    signal.textContent = evidence.signal;
    const detail = document.createElement('p');
    detail.textContent = evidence.detail;
    body.append(source, signal, detail);
    row.append(state, body);
    return row;
  }));
  for (const id of ['cause', 'impact', 'prevention']) $(id).textContent = item[id];
  $('next-steps').replaceChildren(...item.next_steps.map(step => {
    const li = document.createElement('li');
    li.textContent = step;
    return li;
  }));
  $('download').href = `./reports/${selected}.md`;
  $('download').download = `techops-${selected}-draft.md`;
  $('empty').hidden = true;
  $('results').hidden = false;
  $('reset').hidden = false;
  $('investigate').disabled = true;
  $('status').textContent = 'Investigation ready · 3 observations reviewed · draft RCA available';
}

$('investigate').addEventListener('click', investigate);
$('reset').addEventListener('click', () => { selectCase(selected); $('investigate').focus(); });

async function init() {
  try {
    const response = await fetch('./scenarios.json', {credentials: 'omit'});
    if (!response.ok) throw new Error('Fixture unavailable');
    scenarios = await response.json();
    if (keys.some(key => !scenarios[key] || scenarios[key].evidence.length !== 3)) throw new Error('Invalid fixture');
    $('scenarios').replaceChildren(...keys.map((key, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'incident';
      button.dataset.case = key;
      const meta = document.createElement('span');
      meta.className = 'incident-meta';
      meta.textContent = `INC ${numbers[index]} / ${scenarios[key].severity}`;
      const title = document.createElement('strong');
      title.textContent = shortTitles[index];
      const service = document.createElement('span');
      service.className = 'incident-service';
      service.textContent = scenarios[key].service;
      button.append(meta, title, service);
      button.addEventListener('click', () => selectCase(key));
      return button;
    }));
    selectCase(keys[0]);
  } catch {
    $('case-title').textContent = 'The demo could not load';
    $('description').textContent = 'Reload this page to try again, or open the project source using the link above.';
    $('status').textContent = 'Demo unavailable. No investigation was performed.';
    $('scenarios').textContent = 'Cases unavailable';
    $('empty').hidden = true;
  }
}
init();
