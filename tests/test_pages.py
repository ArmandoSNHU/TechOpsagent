"""Public demo artifact isolation and fixture/report contracts."""
import json
from pathlib import Path
import tempfile
import unittest

from tools.build_pages import build
from techops.engine import SCENARIOS


class PagesTests(unittest.TestCase):
    def test_demo_never_collects_local_readings(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory, patch('techops.toolkit.collect', side_effect=AssertionError('Private collector called')):
            output = Path(directory) / 'public'
            build(output)
            self.assertIn('data-mode="demo"', (output / 'index.html').read_text(encoding='utf-8'))
            fixtures = json.loads((output / 'demo.json').read_text(encoding='utf-8'))
            self.assertEqual(set(fixtures), {'network', 'connections', 'health', 'services', 'dns', 'dns_failure'})
            self.assertTrue(all(item['mode'] == 'demo' for item in fixtures.values()))

    def test_only_allowlisted_files_are_published(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'public'
            build(output)
            self.assertEqual({p.name for p in output.iterdir()},
                             {'index.html', 'incidents.html', 'toolkit.css', 'toolkit.js', 'investigation.js', 'catalog.json', 'demo.json', 'style.css', 'app.js', 'scenarios.json', '.nojekyll', 'reports'})
            self.assertEqual(len(list((output / 'reports').glob('*.md'))), 3)

    def test_fixture_reports_are_consistent_and_synthetic(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'public'
            build(output)
            scenarios = json.loads((output / 'scenarios.json').read_text(encoding='utf-8'))
            self.assertEqual(set(scenarios), set(SCENARIOS))
            for key, scenario in scenarios.items():
                self.assertEqual(scenario, SCENARIOS[key])
                report = (output / 'reports' / f'{key}.md').read_text(encoding='utf-8')
                self.assertIn('synthetic fixtures', report)
                self.assertIn('suspected — not verified', report)
                self.assertIn('Author: Armando Gomez', report)
                for evidence in scenario['evidence']:
                    self.assertIn(evidence['signal'], report)

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / 'a', Path(directory) / 'b'
            build(a)
            build(b)
            for file in a.rglob('*'):
                if file.is_file():
                    self.assertEqual(file.read_bytes(), (b / file.relative_to(a)).read_bytes())

    def test_refuses_existing_output_to_avoid_publishing_stale_private_files(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'public'
            output.mkdir()
            private = output / '.env'
            private.write_text('synthetic sentinel', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                build(output)
            self.assertEqual(private.read_text(), 'synthetic sentinel')
