# Five-minute demonstration
Author: Armando Gomez

## 1. Set the context (30 seconds)
“This lab demonstrates my approach to support investigations: collect evidence, separate observations from assumptions, recommend verification, and document the incident.” Explain the three modes: measured local fault-lab evidence, saved synthetic fixtures, and unverified imported JSONL. Analysis is rule-based; no live model inference has been evaluated.

## 2. Investigate checkout failure (90 seconds)
Select Checkout API failure. Enter “Synthetic ticket: checkout began failing after a configuration change.” Run the investigation. Explain why the HTTP 500 and missing TAX_REGION log suggest an application configuration problem; the passing inventory check is supporting context, not proof that all dependencies are healthy. The suspected cause remains unverified.

## 3. Compare another failure (60 seconds)
Select Inventory dependency timeout and investigate. Point out the HTTP 504, upstream timeout, and successful DNS fixture. Explain the proposed next checks and why remediation requires approval.

## 4. Export the work (60 seconds)
Download the incident report. Show impact, evidence, suspected cause, next steps, prevention, and limitations. Reopen an older incident from history to demonstrate persistence. Show the credential scenario if time permits.

## 5. Show engineering discipline (60 seconds)
Run `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`. Explain input validation, same-origin write checks, explicit database connection cleanup, and the docs/API contract test. Show imported JSONL analysis and the offline local-model prompt preview, then explain the approval gate for live model evaluation.

## Interview discussion
- Why deterministic fixtures first? They make the workflow testable without a service account or model.
- Why label causes as suspected? A plausible explanation needs independent verification.
- Why FastAPI? Typed request validation and a generated API schema make the contract easier to inspect and extend. The application remains a local demo, not a public production deployment.
- What does AI eventually add? Evidence-grounded explanations and summaries, evaluated against the repeatable scenarios, without permission to execute arbitrary actions.
- What does this version not prove? Production network diagnosis, scalability, model quality, or enterprise integration behavior.
