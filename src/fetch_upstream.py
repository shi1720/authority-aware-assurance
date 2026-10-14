"""Fetch exact audited vendor source and check recorded byte hashes."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'results/upstream_audit.json').read_text())
target=Path(sys.argv[1]).resolve()
if not target.exists():
 subprocess.run(['git','clone','--no-checkout','https://github.com/NVIDIA/nvtrust.git',str(target)],check=True)
subprocess.run(['git','-C',str(target),'checkout','--detach',manifest['pin']],check=True)
for row in manifest['source_files']+manifest['root_certificates']:
 actual=hashlib.sha256((target/row['path']).read_bytes()).hexdigest()
 if actual!=row['sha256']:raise RuntimeError('Source hash mismatch: '+row['path'])
print('Verified pinned revision and nine file hashes.')
