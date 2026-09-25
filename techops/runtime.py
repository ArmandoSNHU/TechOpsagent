"""Public source fingerprint to identify stale preview processes; excludes private data."""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def build_id(root=ROOT):
    digest=hashlib.sha256()
    files=list((root/'techops').rglob('*.py'))+list((root/'techops/static').glob('*'))
    if (root/'requirements.txt').exists():files.append(root/'requirements.txt')
    for path in sorted(set(p for p in files if p.is_file())):
        digest.update(path.relative_to(root).as_posix().encode());digest.update(b'\0');digest.update(path.read_bytes())
    return digest.hexdigest()[:16]
