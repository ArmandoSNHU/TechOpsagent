# Security and data handling
Author: Armando Gomez

## Intended environment
Single-user, loopback-only portfolio lab. No authentication, TLS, multi-user isolation, or public deployment hardening is provided. Do not expose the server to the internet or a shared LAN.

## Controls
- Bind to 127.0.0.1; validate the Host header and require both the actual ASGI peer and local endpoint to be loopback IP addresses. Missing endpoint information fails closed. The supported launcher disables proxy-header rewriting.
- Reject cross-origin browser writes and require JSON content type.
- Restrict request sizes and ticket lengths; reject unexpected request fields.
- Serve only explicitly named static assets; never translate request paths into arbitrary file reads.
- Parameterize SQLite statements and close every connection.
- Render dynamic browser text through textContent; no ticket HTML execution.
- Treat ticket content as data; it cannot fetch URLs, execute commands, or influence scenario selection.
- Redact common bearer-token, api-key, password, token, and secret forms before storing tickets.
- Ignore runtime data, logs, virtual environments, and .env files in Git.

## Limitations
Redaction is best-effort, not a comprehensive data-loss-prevention system. Arbitrary personal data or unusual secret formats may remain. Download buttons produce sanitized structural summaries and omit free-text notes, raw readings, hostnames, process metadata, identifiers and source timestamps. Full details remain visible in the local API/workspace; sanitization is an export boundary, not storage encryption. No raw-download toggle is provided. Use synthetic input for public demos and screenshots. Data is stored in plaintext SQLite with the operating system's existing file permissions. No automated retention or deletion is included. A local process with filesystem access can read the database.

FastAPI/Uvicorn serves this local demo. A five-second request-body timeout and byte limit are enforced, but rate limits, authentication, authorization, audit policy, and deployment hardening are still required before any wider exposure.

## Future side effects
Integrations must begin with fixtures, capability checks, and a dry-run path. Explicit authorization is required before model downloads or startup, paid API calls, remote writes, or corrective actions. Never let ticket/log content supply tool instructions or network targets.

## Reporting
Report issues directly to the project owner through an established private channel. Do not include secrets or personal tickets in a public issue.

## Publication checks
Local operator settings belong in ignored `.env` or process environment variables. The committed `.env.example` must contain only empty values. Never store customer tickets, raw logs, exports, private service addresses, or screenshots containing credentials in tracked files. Example reports and the committed model evaluation use synthetic data.

Enable the pre-push guard with `git config core.hooksPath .githooks`; hooks do not install automatically on clone. It checks the index and all locally available Git history, including deleted files, for private artifacts, common credential signatures, credential-like assignments, and personal email addresses. Findings report filenames and categories, never matched values. The one reviewed dummy credential in tests/test_connectors.py is narrowly exempted; test directories are otherwise scanned. Historical public repository identity is permitted only for the original known empty integration configuration.

The CI workflow repeats checks and tests after upload. CI cannot prevent the initial disclosure from a push; use the local hook before sending. Neither check detects every secret format or sensitive prose. Images require visual review. Hooks can be bypassed. Main branch protection and GitHub scanning are now enabled; see [Security hardening](docs/SECURITY-HARDENING.md) for the verified configuration and limitations. Check staged content before each push. If a real credential is ever published, revoke/rotate it; deleting the latest file does not remove history or other copies.

The setup prompt hides token entry but does not encrypt `.env`. On Windows, protect your user account and project directory permissions; avoid shared folders and screenshots of the file. The app never serves .env, configuration files, or its database through static routes.

## Local trust boundary and export scope
The runtime has no authentication. Same-machine users/processes and a local proxy can access it; loopback checks do not authenticate those callers. Do not tunnel, reverse-proxy, or publicly host the runtime. Public hosting requires a separate authentication/authorization and transport design. GitHub Pages serves only synthetic static artifacts.

Tool JSON exports include only allowlisted tool/mode/status values, a reading count and a truncation flag. Guided handoffs retain workflow steps, evidence states and generic next steps; notes, result summaries and hostnames are omitted in both local and demo modes. Incident download responses retain only severity from a fixed vocabulary, evidence count and generic limitations. Full synthetic sample RCA files in the Pages artifact are separately built from committed fixtures with empty ticket context. Direct API record reads and manually copied screenshots may contain private information: they are not sanitized exports. Review any content before sharing.
