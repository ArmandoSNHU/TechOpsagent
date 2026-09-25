# Progress gallery
Author: Armando Gomez
Date: 2026-09-24

These are captures of the running application, not mockups. All incident data shown is synthetic.

## Desktop — dependency investigation
The incident workspace presents the intake scenario, suspected cause, evidence trail, next steps, report export, and saved history.

![Desktop investigation](screenshots/progress-desktop.jpg)

## Phone layout — credential investigation
Captured with a 390 px emulated viewport. The layout stacks intake, evidence, and history. Phone network access is a separate future feature; this image verifies layout only.

![Mobile investigation](screenshots/progress-mobile.jpg)

## Focused capture — investigation panel
Captured directly with Chrome DevTools element screenshot support. This cropped PNG keeps the suspected cause, evidence, recommended steps, and report link together. Windows Snipping Tool was not used.

![Investigation panel snippet](screenshots/investigation-snippet.png)

## FastAPI migration
The restarted server reports framework fastapi. Report download returned 200, saved history reopened, and a 390 px viewport had no horizontal overflow.

![FastAPI workspace](screenshots/fastapi-desktop.jpg)

## Observed local evidence
The application now measures a controlled HTTP failure and ranks the observed evidence. This focused Chrome capture shows HTTP 500, the healthy comparison, local resolution, and the cited rule score.

![Observed evidence snippet](screenshots/live-evidence-snippet.png)

## Connected sources
Real Chrome element capture after the GitHub read completed. Grafana and Loki are visibly unconfigured.

![Connected sources snippet](screenshots/integrations-snippet.png)

## Connected sources
Real Chrome element capture after the GitHub read completed. Grafana and Loki are visibly unconfigured.

![Connected sources snippet](screenshots/integrations-snippet.png)

## Private local configuration
Fresh installs have no connected accounts. Local setup stores settings in ignored .env; tokens are entered with hidden prompts. Real Chrome capture of a clean settings profile:

![Private setup snippet](screenshots/private-setup-snippet.png)

## Live Grafana and Loki lab
Actual Chrome element capture from the local Grafana dashboard. All three events are synthetic and were ingested into the running Loki service.

![Grafana Loki synthetic events](screenshots/grafana-loki-snippet.png)
## Published interactive demo — 2026-09-24
The [public demo](https://armandosnhu.github.io/TechOpsagent/) runs entirely from synthetic static assets. These are actual Chrome captures of the deployed HTTPS site, not design mockups. Desktop shows the checkout investigation; mobile shows the dependency-timeout case. The snippet isolates the draft diagnosis and troubleshooting steps. No real tickets, credentials, or local dashboards appear.

![Published demo desktop](screenshots/pages-desktop.jpg)

![Published demo mobile](screenshots/pages-mobile.jpg)

![Draft diagnosis snippet](screenshots/pages-snippet.png)
## Category-based diagnostic toolkit — 2026-09-25
Actual Chrome captures from the generated public artifact served locally. All visible readings are synthetic; real Windows validation retained only status/count summaries for documentation. Full button walkthrough: [TOOL-GUIDE.md](TOOL-GUIDE.md).

![Toolkit home](screenshots/toolkit-overview.jpg)

![Network tool](screenshots/toolkit-network.jpg)

![Network result snippet](screenshots/toolkit-snippet.png)

![Mobile tool panel](screenshots/toolkit-mobile.jpg)

## Neon Night — 2026-09-25
Real Chrome capture of the synthetic dashboard with the new Theme selector. See TOOL-GUIDE.md for mobile capture and storage behavior.

![Neon Night](screenshots/neon-desktop.jpg)
