# DNS resolution tool
Author: Armando Gomez

Continue the accepted toolkit roadmap with one complete next tool: Network â†’ Test DNS resolution. Windows performs A/AAAA queries through configured DNS using a fixed Resolve-DnsName script, with DNS-only resolution, no hosts-file lookup, and a 12-second process limit. A validated hostname is passed as JSON on stdin, never inserted into command text. No website fetch, port scan, custom DNS server, model or remediation is added.

- [x] Add failing tests for hostname validation, command/data separation, response validation, timeouts, empty answers, lookup failure, unsupported OS and strict API fields.
- [x] Implement collector, request schema and catalog. Use up to 64 validated records, elapsed query time, explicit success/failure/no-address distinctions and safe error text.
- [x] Add hostname input locally, a fixed synthetic success/failure selector publicly, result target metadata, history/export correctness, next-step link from network configuration and five-tool overview.
- [x] Verify mock tests before live example.com and reserved .invalid lookups; test browser input/errors/history, both themes, mobile and public deployment. Update button guide, screenshots, API contract and STATE.

Public fixtures use documentation-only addresses and cannot relay user-entered names to a resolver. DNS success does not prove a website works, and DNS failure does not uniquely diagnose its cause. Browser and exported results identify the hostname that actually ran, even if the input changes afterward.
