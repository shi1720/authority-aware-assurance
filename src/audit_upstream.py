"""Pin-and-hash source audit; no inference of legal jurisdiction from hostname."""
import ast,hashlib,json,subprocess,sys
from pathlib import Path
from cryptography import x509
PIN='858ada9a17f58c482f578414ea2455498fa51e17'
repo=Path(sys.argv[1]).resolve()
assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==PIN
paths=[
'guest_tools/attestation_sdk/src/nv_attestation_sdk/utils/config.py',
'guest_tools/attestation_sdk/src/nv_attestation_sdk/gpu/attest_gpu_local.py',
'guest_tools/attestation_sdk/src/nv_attestation_sdk/gpu/attest_gpu_remote.py',
'guest_tools/gpu_verifiers/local_gpu_verifier/src/verifier/config.py',
'guest_tools/gpu_verifiers/local_gpu_verifier/src/verifier/cc_admin.py',
'guest_tools/gpu_verifiers/local_gpu_verifier/src/verifier/cc_admin_utils.py',
'guest_tools/gpu_verifiers/local_gpu_verifier/src/verifier/rim/__init__.py']
rows=[]
for rel in paths:
 p=repo/rel;content=p.read_bytes();rows.append({'path':rel,'sha256':hashlib.sha256(content).hexdigest(),'lines':len(content.splitlines())})
endpoints=[]
p=repo/paths[0];tree=ast.parse(p.read_text())
for node in ast.walk(tree):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='getenv' and len(node.args)>1:
  value=node.args[1]
  if isinstance(value,ast.Constant) and isinstance(value.value,str) and value.value.startswith('https://'):
   endpoints.append({'environment_variable':ast.literal_eval(node.args[0]),'default':value.value,'line':node.lineno,'path':paths[0]})
certs=[]
for p in sorted((repo/'guest_tools/gpu_verifiers/local_gpu_verifier/src/verifier/certs').glob('verifier*root.pem')):
 cert=x509.load_pem_x509_certificate(p.read_bytes())
 certs.append({'path':str(p.relative_to(repo)),'subject':cert.subject.rfc4514_string(),'issuer':cert.issuer.rfc4514_string(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
result={'pin':PIN,'source_files':rows,'endpoint_defaults':endpoints,'root_certificates':certs,'scope':'Static source extraction, plus separate mocked-boundary tests; no GPU attestation or service outage observed.'}
out=Path(__file__).resolve().parents[1]/'results'/'upstream_audit.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
