from pathlib import Path
from techops.engine import SCENARIOS, investigate, render_report

def main():
    target = Path(__file__).resolve().parent.parent / 'examples'
    target.mkdir(exist_ok=True)
    for scenario in SCENARIOS:
        (target / (scenario + '.md')).write_text(render_report(investigate(scenario)), encoding='utf-8')
    print('Exported 3 synthetic incident reports to examples/')
if __name__ == '__main__': main()
