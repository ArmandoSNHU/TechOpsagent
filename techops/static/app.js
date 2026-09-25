"use strict";
const $ = id => document.getElementById(id);
let selected = "api_error";
async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
function el(tag, text, cls) {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = text;
  if (cls) item.className = cls;
  return item;
}
function showIncident(r) {
  $("empty").hidden = true; $("result").hidden = false;
  $("result-badge").textContent = "SUSPECTED";
  $("result-service").textContent = r.service + " / " + r.id.slice(0, 8);
  $("incident-title").textContent = r.title; $("severity").textContent = r.severity;
  $("evidence-mode").textContent = r.environment === "local_fault_lab" ? "OBSERVED · LOCAL LAB" : r.environment === "imported_logs" ? "IMPORTED · UNVERIFIED" : "SIMULATED FIXTURES";
  $("hypotheses").replaceChildren(...(r.hypotheses || []).map(h => el("p", h.cause + " · rule score " + h.score + " · " + h.evidence_ids.join(", "), "hypothesis")));
  $("cause").textContent = r.cause; $("impact").textContent = r.impact;
  $("evidence").replaceChildren(...r.evidence.map(e => {
    const row = el("div", undefined, "evidence-item");
    const detail = el("div"); detail.append(el("strong", e.signal), el("p", e.source + " · " + e.detail));
    row.append(el("span", e.state === "passed" ? "✓" : "!", "check " + e.state), detail);
    return row;
  }));
  $("steps").replaceChildren(...r.next_steps.map(s => el("li", s)));
  $("download").href = "/api/incidents/" + encodeURIComponent(r.id) + "/report";
}
async function loadHistory() {
  const records = await api("/api/incidents");
  $("count").replaceChildren(document.createTextNode(String(records.length).padStart(2, "0") + " "), el("small", "saved locally"));
  if (!records.length) return;
  $("history-items").replaceChildren(...records.map(r => {
    const button = el("button", undefined, "history-row");
    const detail = el("div"); detail.append(el("strong", r.title), el("small", r.service + " · " + new Date(r.created_at).toLocaleString()));
    button.append(el("span", r.severity, "severity"), detail, el("span", "Suspected ↗", "record-status"));
    button.addEventListener("click", () => { showIncident(r); $("result").scrollIntoView({behavior:"auto", block:"start"}); $("status").textContent = "Loaded saved investigation " + r.id.slice(0, 8) + "."; });
    return button;
  }));
}
$("run").addEventListener("click", async () => {
  $("run").disabled = true; $("status").textContent = "Collecting and reviewing evidence…";
  try {
    const mode = $("analysis-mode").value;
    const path = mode === "lab" ? "/api/lab/investigate" : mode === "logs" ? "/api/analyze" : "/api/investigate";
    const payload = mode === "logs" ? {log_text:$("log-text").value,ticket:$("ticket").value} : {scenario:selected,ticket:$("ticket").value};
    const result = await api(path, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)});
    showIncident(result); $("status").textContent = "Investigation saved. Review the suspected cause and evidence.";
    try { await loadHistory(); } catch (error) { $("status").textContent = "Investigation saved; history refresh failed. " + error.message; }
  } catch (error) { $("status").textContent = "Unable to investigate: " + error.message; }
  finally { $("run").disabled = false; }
});
$("analysis-mode").addEventListener("change", () => {
  const mode = $("analysis-mode").value;
  $("log-input").hidden = mode !== "logs";
  $("scenarios").hidden = mode === "logs";
  $("intake-badge").textContent = mode === "lab" ? "LIVE LOCAL LAB" : mode === "logs" ? "UNVERIFIED LOGS" : "FIXTURE DATA";
  $("status").textContent = mode === "lab" ? "Runs bounded checks against a disposable local fault service." : mode === "logs" ? "Paste structured JSONL; log content never executes commands." : "Uses saved synthetic fixture evidence.";
});
async function init() {
  try {
    const scenarios = await api("/api/scenarios");
    $("scenarios").replaceChildren(...scenarios.map((s,i) => {
      const button = el("button", undefined, "scenario" + (s.id === selected ? " selected" : ""));
      button.type = "button"; button.setAttribute("aria-pressed", String(s.id === selected));
      const text = el("span"); text.append(el("strong", s.title), el("small", s.service));
      button.append(el("span", String(i+1).padStart(2,"0"), "number"), text, el("span", "↗", "arrow"));
      button.addEventListener("click", () => {
        selected = s.id;
        document.querySelectorAll(".scenario").forEach(b => {b.classList.remove("selected"); b.setAttribute("aria-pressed","false");});
        button.classList.add("selected"); button.setAttribute("aria-pressed","true");
        $("status").textContent = s.description;
      });
      return button;
    }));
    $("run").disabled = false; $("status").textContent = "Ready. Select a scenario to begin.";
    await loadHistory();
  } catch (error) { $("status").textContent = "Could not load workspace: " + error.message; }
}
init();

async function loadIntegrationStatus() {
  try {
    const config = await api("/api/integrations");
    $("integration-summary").textContent = "GitHub: " + (config.github.repository || "not configured") + " · Grafana: " + (config.grafana.configured ? "configured" : "not configured") + " · Loki: " + (config.loki.configured ? "configured" : "not configured");
    $("github-read").disabled = !config.github.configured;
    $("grafana-health").disabled = !config.grafana.configured;
    $("loki-controls").hidden = !config.loki.configured;
  } catch (error) { $("integration-status").textContent = error.message; }
}
$("github-read").addEventListener("click", async () => {
  $("github-read").disabled = true;
  $("integration-status").textContent = "Reading one page of open GitHub issues…";
  try {
    const result = await api("/api/integrations/github/read", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({page:1})});
    $("github-tickets").replaceChildren(...result.tickets.map(ticket => {
      const item=el("div",undefined,"ticket");
      const use=el("button","Use as ticket context","secondary");
      use.addEventListener("click",() => {$("ticket").value=(ticket.title+"\n"+ticket.body).slice(0,4000);$("status").textContent="GitHub context loaded. Select independent evidence before investigating.";$("ticket").focus();});
      item.append(el("strong","#"+ticket.number+" · "+ticket.title),el("p",ticket.body.slice(0,240)),use);
      return item;
    }));
    $("integration-status").textContent = result.tickets.length ? result.tickets.length+" tickets loaded. Ticket text is untrusted context; no remote changes made."+(result.next_page ? " More pages are available through the API." : "") : "Connected successfully. No open issues on this page; no remote changes made.";
  } catch (error) { $("integration-status").textContent = "GitHub read failed: "+error.message; }
  finally { $("github-read").disabled=false; }
});
$("grafana-health").addEventListener("click", async () => {
  try {const result=await api("/api/integrations/grafana/health");$("integration-status").textContent="Grafana database: "+result.database+" · version "+result.version;}
  catch(error){$("integration-status").textContent="Grafana: "+error.message;}
});
$("loki-read").addEventListener("click", async () => {
  $("loki-read").disabled=true;
  try {
    const result=await api("/api/integrations/loki/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({service:$("loki-service").value,minutes:15})});
    showIncident(result);await loadHistory();$("integration-status").textContent="Loki evidence analyzed and saved locally.";
  } catch(error){$("integration-status").textContent="Loki: "+error.message;}
  finally {$("loki-read").disabled=false;}
});
loadIntegrationStatus();
