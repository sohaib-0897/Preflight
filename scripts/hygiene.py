"""Check tracked source for accidental secrets/large generated artifacts."""
import pathlib
import re
import subprocess
import sys
files=subprocess.run(['git','ls-files','-z'],check=True,capture_output=True).stdout.decode().split('\0')
failures=[]
for name in filter(None,files):
 p=pathlib.Path(name)
 if p.stat().st_size>2*1024*1024:failures.append(f'{name}: unexpectedly large tracked file')
 if p.suffix in {'.sqlite','.whl','.tgz','.pem'} or any(part in {'.venv','node_modules','.local'} for part in p.parts):failures.append(f'{name}: forbidden generated/secret path')
 try:text=p.read_text()
 except UnicodeDecodeError:continue
 if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',text):failures.append(f'{name}: private key marker')
 if re.search(r'(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_]{20,}',text):failures.append(f'{name}: probable credential')
print('\n'.join(failures) if failures else f'Hygiene check passed for {len(list(filter(None,files)))} tracked paths; this pattern check is not exhaustive secret detection.')
sys.exit(bool(failures))
