"""Execute pinned upstream functions with synthetic certs and mocked transport.
Chain verification is explicitly stubbed in OCSP branch tests; signatures are real.
No hardware, NRAS integration, or production certificate validation is tested.
"""
import os,sys,json,base64
from pathlib import Path
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
import pytest
from cryptography import x509
from cryptography.x509 import ocsp
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from OpenSSL import crypto
upstream=Path(os.environ['NVTRUST_SOURCE']).resolve()
sys.path.insert(0,str(upstream/'guest_tools/gpu_verifiers/local_gpu_verifier/src'))
from verifier.cc_admin_utils import CcAdminUtils
from verifier.config import BaseSettings
from verifier.exceptions import RIMFetchError

class Response:
 def __init__(self,body):self.body=body
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self):return self.body

@pytest.mark.parametrize('endpoint',['https://rim.attestation.nvidia.com/v1/rim/','https://cache.example.invalid/rim/'])
def test_rim_transport_override(endpoint):
 BaseSettings.RIM_SERVICE_BASE_URL=endpoint;BaseSettings.service_key=None
 payload=json.dumps({'rim':base64.b64encode(b'fixture-manifest').decode()}).encode()
 with patch('urllib.request.urlopen',return_value=Response(payload)) as transport:
  assert CcAdminUtils.fetch_rim_file('abc')=='fixture-manifest'
  assert transport.call_args[0][0].full_url==endpoint+'abc'

@pytest.mark.parametrize('endpoint',['https://rim.attestation.nvidia.com/v1/rim/','https://cache.example.invalid/rim/'])
def test_rim_withdrawal(endpoint):
 BaseSettings.RIM_SERVICE_BASE_URL=endpoint;BaseSettings.service_key=None
 from urllib.error import HTTPError
 with patch('urllib.request.urlopen',side_effect=HTTPError(endpoint,503,'fixture failure',None,None)):
  with pytest.raises(RIMFetchError):CcAdminUtils.fetch_rim_file('abc')

def fixture_response(status,reason=None,nonce=True):
 now=datetime.now(timezone.utc);issuer_key=ec.generate_private_key(ec.SECP384R1());leaf_key=ec.generate_private_key(ec.SECP384R1())
 issuer_name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Synthetic issuer')])
 leaf_name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Synthetic device')])
 issuer=x509.CertificateBuilder().subject_name(issuer_name).issuer_name(issuer_name).public_key(issuer_key.public_key()).serial_number(1).not_valid_before(now-timedelta(days=1)).not_valid_after(now+timedelta(days=1)).sign(issuer_key,hashes.SHA384())
 leaf=x509.CertificateBuilder().subject_name(leaf_name).issuer_name(issuer_name).public_key(leaf_key.public_key()).serial_number(2).not_valid_before(now-timedelta(days=1)).not_valid_after(now+timedelta(days=1)).sign(issuer_key,hashes.SHA384())
 builder=ocsp.OCSPResponseBuilder().add_response(leaf,issuer,hashes.SHA384(),status,now,now+timedelta(hours=1),now if status==ocsp.OCSPCertStatus.REVOKED else None,reason)
 builder=builder.responder_id(ocsp.OCSPResponderEncoding.HASH,issuer).certificates([issuer])
 if nonce:builder=builder.add_extension(x509.OCSPNonce(b'x'*32),False)
 response=builder.sign(issuer_key,hashes.SHA384())
 chain=[crypto.X509.from_cryptography(leaf),crypto.X509.from_cryptography(issuer)]
 return chain,response

@pytest.mark.parametrize('status,reason,allow,expected',[
 (ocsp.OCSPCertStatus.GOOD,None,False,True),
 (ocsp.OCSPCertStatus.UNKNOWN,None,False,False),
 (ocsp.OCSPCertStatus.REVOKED,x509.ReasonFlags.key_compromise,False,False),
 (ocsp.OCSPCertStatus.REVOKED,x509.ReasonFlags.certificate_hold,False,False),
 (ocsp.OCSPCertStatus.REVOKED,x509.ReasonFlags.certificate_hold,True,True),
])
def test_ocsp_branch(status,reason,allow,expected):
 chain,response=fixture_response(status,reason)
 BaseSettings.allow_hold_cert=allow;BaseSettings.OCSP_NONCE_DISABLED=False
 assert CcAdminUtils.verify_ocsp_signature(response)
 with patch.object(CcAdminUtils,'generate_nonce',return_value=b'x'*32),patch('verifier.cc_admin_utils.function_wrapper_with_timeout',return_value=response),patch.object(CcAdminUtils,'verify_certificate_chain',return_value=(True,False,None)):
  result=CcAdminUtils.ocsp_certificate_chain_validation(chain,None,BaseSettings.Certificate_Chain_Verification_Mode.DRIVER_RIM_CERT)
 assert result[0] is expected

def test_missing_nonce_rejected():
 chain,response=fixture_response(ocsp.OCSPCertStatus.GOOD,nonce=False)
 BaseSettings.allow_hold_cert=False;BaseSettings.OCSP_NONCE_DISABLED=False
 with patch.object(CcAdminUtils,'generate_nonce',return_value=b'x'*32),patch('verifier.cc_admin_utils.function_wrapper_with_timeout',return_value=response),patch.object(CcAdminUtils,'verify_certificate_chain',return_value=(True,False,None)):
  assert CcAdminUtils.ocsp_certificate_chain_validation(chain,None,BaseSettings.Certificate_Chain_Verification_Mode.DRIVER_RIM_CERT)[0] is False

def test_ocsp_withdrawal_raises():
 BaseSettings.OCSP_URL='https://ocsp.ndis.nvidia.com/';BaseSettings.service_key=None
 with patch('urllib.request.urlopen',side_effect=OSError('synthetic outage')):
  with pytest.raises(Exception,match='OCSP request failed'):CcAdminUtils.send_ocsp_request(b'fixture')
