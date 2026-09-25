"""Local incident persistence; one connection per operation."""
from contextlib import contextmanager
import json
import sqlite3
from pathlib import Path

class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, body TEXT NOT NULL)')
    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path)
        try:
            with connection:
                yield connection
        finally:
            connection.close()
    def save(self, incident):
        with self.connect() as db:
            db.execute('INSERT INTO incidents VALUES (?, ?, ?)', (incident['id'], incident['created_at'], json.dumps(incident)))
    def list(self):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute('SELECT body FROM incidents ORDER BY created_at DESC LIMIT 100')]
    def get(self, incident_id):
        with self.connect() as db:
            row = db.execute('SELECT body FROM incidents WHERE id = ?', (incident_id,)).fetchone()
            return json.loads(row[0]) if row else None
