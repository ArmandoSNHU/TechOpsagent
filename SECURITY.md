# Security and data handling
Author: Armando Gomez

## Intended environment
Single-user, loopback-only portfolio lab. No authentication, TLS, multi-user isolation, or public deployment hardening is provided. Do not expose the server to the internet or a shared LAN.

## Controls
- Bind to 127.0.0.1; validate the Host header.
- Reject cross-origin browser writes and require JSON content type.
- Restrict request sizes and ticket lengths; reject unexpected request fields.
- Serve only explicitly named static assets; never translate request paths into arbitrary file reads.
- Parameterize SQLite statements and close every connection.
- Render dynamic browser text through textContent; no ticket HTML execution.
- Treat ticket content as data; it cannot fetch URLs, execute commands, or influence scenario selection.
- Redact common bearer-token, api-key, password, token, and secret forms before storing tickets.
- Ignore runtime data, logs, virtual environments, and .env files in Git.

## Limitations
Redaction is best-effort, not a comprehensive data-loss-prevention system. Arbitrary personal data or unusual secret formats may remain. Markdown downloads contain quoted user text; treat downloaded reports as untrusted content. Use only synthetic input. Data is stored in plaintext SQLite with the operating system's existing file permissions. No automated retention or deletion is included. A local process with filesystem access can read the database.

FastAPI/Uvicorn serves this local demo. A five-second request-body timeout and byte limit are enforced, but rate limits, authentication, authorization, audit policy, and deployment hardening are still required before any wider exposure.

## Future side effects
Integrations must begin with fixtures, capability checks, and a dry-run path. Explicit authorization is required before model downloads or startup, paid API calls, remote writes, or corrective actions. Never let ticket/log content supply tool instructions or network targets.

## Reporting
Before the repository is public, report issues directly to the project owner through an established private channel. Do not include secrets or personal tickets in a public issue.
