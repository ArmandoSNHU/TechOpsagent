# Local AI adapter
Author: Armando Gomez

## Safe default
The application does not start a runtime, download a model, or perform inference. The preview endpoint and default CLI are offline. Ticket context is omitted from the model prompt; evidence is redacted and labeled untrusted. No tools or actions are offered to the model.

```powershell
.\.venv\Scripts\python.exe -m techops.ai --dry-run --scenario api_error
```

The output lists the system instructions, evidence JSON, and allowed evidence IDs. `GET /api/incidents/{id}/ai-preview` builds the same preview for a saved incident.

## Approval-gated local execution
Only after explicit approval, `--probe` can query an already-running Ollama service at 127.0.0.1:11434 for installed local models. The adapter never starts the service. `--enable-inference --model <approved-installed-model>` permits one inference request using an installed model. Models identified as remote/cloud are excluded; no download endpoint exists. Choose a model compatible with the available 8 GB GPU before enabling it.

The adapter uses /api/tags and /api/chat, nonstreaming JSON-schema output, a two-second inventory timeout and thirty-second generation timeout, bounded response size, and keep_alive 0. Protocol reference: [official Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md).

## Output validation and limitations
Output must contain only summary and evidence_ids. Every cited ID must exist in the input. Unknown citations, empty citations, unexpected fields, or malformed JSON are rejected. Citation membership does not prove factual accuracy; accepted output always requires human review and never overwrites observed evidence or the rule-based cause.

Offline tests use mocked transport and cover the disabled default, missing models, cloud-model exclusion, payload generation, and citation checks. Approved local testing is documented in MODEL-EVALUATION.md. llama3.2:3b completed six cases in 4.77–5.49 seconds with a sampled peak of 3432 MiB total GPU use. One unsupported suggestion was flagged; output still requires review. Normal app startup and preview endpoints do not perform inference.
