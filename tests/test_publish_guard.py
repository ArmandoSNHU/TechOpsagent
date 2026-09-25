import unittest
from tools.publish_guard import inspect_file

class PublishGuardTests(unittest.TestCase):
    def test_blocks_private_files_even_if_force_added(self):
        for path in ['.env','.env.local','data/tickets.json','backup.sqlite3','server.log','keys/client.pem','config/integrations.local.json']:
            with self.subTest(path=path):self.assertTrue(inspect_file(path,b''))
    def test_detects_tokens_without_echoing_values(self):
        token='gh'+'p_'+'a'*36
        findings=inspect_file('example.py',token.encode())
        self.assertTrue(findings);self.assertNotIn(token,str(findings))
    def test_no_test_directory_exemption(self):
        self.assertTrue(inspect_file('tests/fixture.py',('sk-'+'a'*40).encode()))
    def test_empty_template_allowed_but_populated_template_blocked(self):
        self.assertFalse(inspect_file('.env.example',b'GITHUB_TOKEN=\n'))
        self.assertTrue(inspect_file('.env.example',b'GITHUB_TOKEN=anything\n'))
    def test_private_key_and_personal_email_detected(self):
        self.assertTrue(inspect_file('readme.md',('-----BEGIN '+'PRIVATE KEY-----').encode()))
        self.assertTrue(inspect_file('readme.md',('user'+'@'+'gmail.com').encode()))
    def test_generic_examples_allowed(self):
        self.assertFalse(inspect_file('README.md',b'owner/repo user@example.com'))

    def test_generic_token_assignment_detected(self):
        self.assertTrue(inspect_file('config.py',('API_KEY="'+'randomValue0123456789'+'"').encode()))
    def test_tracked_secret_in_deleted_history_blocks(self):
        import os, subprocess, sys, tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            def git(*args):
                subprocess.run(['git',*args],cwd=directory,check=True,capture_output=True)
            git('init');git('config','user.name','Fixture');git('config','user.email','fixture@example.com')
            p=Path(directory)/'example.txt';p.write_text('gh'+'p_'+'z'*36)
            git('add','.');git('commit','-m','fixture');git('rm','example.txt');git('commit','-m','remove fixture')
            env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[1]))
            result=subprocess.run([sys.executable,'-m','tools.publish_guard','--history'],cwd=directory,env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,1)
            self.assertIn('credential signature',result.stdout)
            self.assertNotIn('z'*36,result.stdout)
