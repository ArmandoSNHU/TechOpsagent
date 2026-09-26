"""Build a public, synthetic-only site from an explicit file allowlist."""
import argparse
import json
from pathlib import Path
import shutil

from techops.engine import SCENARIOS, render_report
from techops.tool_catalog import CATALOG, DEMO

ROOT = Path(__file__).resolve().parents[1]


def build(output):
    output = Path(output)
    # Never merge with an old artifact: it might contain operator data.
    output.mkdir(parents=True, exist_ok=False)
    for name in ('index.html', 'style.css', 'app.js'):
        source = ROOT / 'site' / name
        if source.is_symlink():
            raise ValueError('Site sources must be regular files')
        shutil.copyfile(source, output / ('incidents.html' if name == 'index.html' else name))
    for name in ('index.html', 'toolkit.css', 'toolkit.js', 'investigation.js'):
        source = ROOT / 'techops' / 'static' / 'toolkit' / name
        if source.is_symlink():
            raise ValueError('Toolkit sources must be regular files')
        shutil.copyfile(source, output / name)
    for name, value in (('catalog.json', CATALOG), ('demo.json', DEMO)):
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / '.nojekyll').touch()
    (output / 'scenarios.json').write_text(
        json.dumps(SCENARIOS, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / 'reports').mkdir()
    for key, scenario in SCENARIOS.items():
        report = dict(scenario, id='DEMO-' + key, created_at='Static synthetic example',
                      environment='simulated', analysis_mode='deterministic', ticket='')
        (output / 'reports' / f'{key}.md').write_text(render_report(report), encoding='utf-8')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='data/pages', help='New, unused output directory')
    args = parser.parse_args()
    print('Built synthetic Pages demo:', build(args.output))
