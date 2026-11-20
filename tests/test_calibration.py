import copy
import hashlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
def fixture(name):
    return json.loads((ROOT/'fixtures'/name).read_text())

@pytest.fixture
def setup(direct_vm,direct_deploy,direct_owner):
    p=fixture('policy.json'); p['lab']='0x'+direct_owner.hex()
    direct_vm.warp('2026-11-18T15:00:00Z')
    s=fixture('submission.json')
    review=fixture('review.mock.json')
    direct_vm.check_pickling=True
    c=direct_deploy(str(ROOT/'contracts/calibration_iq.py'),json.dumps(p),sdk_version='v0.2.16')
    direct_vm.mock_llm(r'^CALIBRATION_REVIEW:',json.dumps(review))
    direct_vm.mock_llm(r'^CALIBRATION_GROUNDING:','{"grounded":true}')
    return direct_vm,c,p,s,review

def evaluate(setup):
    vm,c,p,s,r=setup
    c.submit(json.dumps(s))
    return json.loads(c.evaluate())

def test_calibrated_and_consensus(setup):
    r=evaluate(setup)
    assert r['result']['outcome']=='CALIBRATED'
    assert setup[0].run_validator() is True
    h=r.pop('receipt_hash')
    assert h==hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

@pytest.mark.parametrize('measured,uncertainty,outcome',[(500,0,'CALIBRATED'),(500,1,'CONDITIONAL'),(501,0,'OUT_OF_TOLERANCE'),(-501,0,'OUT_OF_TOLERANCE'),(100,401,'CONDITIONAL'),(0,500,'CALIBRATED')])
def test_tolerance_boundaries(setup,measured,uncertainty,outcome):
    setup[3]['measurements'][0].update(measured=measured,uncertainty=uncertainty)
    assert evaluate(setup)['result']['outcome']==outcome

@pytest.mark.parametrize('name',['identity','procedure','traceability','maintenance','results'])
@pytest.mark.parametrize('status',['UNKNOWN','CONTRADICTED'])
def test_missing_or_conflicting_documentation(setup,name,status):
    vm,c,p,s,r=setup
    r[name]['status']=status
    if status=='UNKNOWN': r[name]['quote']=''
    vm.clear_mocks(); vm.mock_llm(r'^CALIBRATION_REVIEW:',json.dumps(r))
    vm.mock_llm(r'^CALIBRATION_GROUNDING:','{"grounded":true}')
    assert evaluate(setup)['result']['outcome']=='INCONCLUSIVE'

def test_validator_independent_disagreement(setup):
    evaluate(setup)
    vm,c,p,s,r=setup; r['results']={'status':'UNKNOWN','quote':''}
    vm.clear_mocks(); vm.mock_llm(r'^CALIBRATION_REVIEW:',json.dumps(r))
    assert vm.run_validator() is False

@pytest.mark.parametrize('audit',['{"grounded":false}','{"grounded":1}','{"grounded":true,"extra":1}','invalid'])
def test_grounding_audit_rejects(setup,audit):
    evaluate(setup)
    vm,c,p,s,r=setup
    vm.clear_mocks(); vm.mock_llm(r'^CALIBRATION_REVIEW:',json.dumps(r))
    vm.mock_llm(r'^CALIBRATION_GROUNDING:',audit)
    assert vm.run_validator() is False

@pytest.mark.parametrize('field,value',[('scale',True),('scale',0),('lab','0x'+'0'*40),('max_age_seconds',31536001),('unit',''),('lab_name',''),('points',[]),('points',[{'reference':True,'tolerance':5}])])
def test_invalid_policy(direct_deploy,field,value):
    p=fixture('policy.json'); p[field]=value
    with pytest.raises(Exception): direct_deploy(str(ROOT/'contracts/calibration_iq.py'),json.dumps(p),sdk_version='v0.2.16')

@pytest.mark.parametrize('mutation',['hash','equipment','future','expiry','period','missing','reorder','bool','uncertainty','extra','oversize'])
def test_invalid_submission(setup,mutation):
    vm,c,p,s,r=setup
    if mutation=='hash': s['evidence_sha256']='0'*64
    if mutation=='equipment': s['equipment_id']='OTHER'
    if mutation=='future': s['issued_at']=1900000000
    if mutation=='expiry': s['expires_at']=s['issued_at']
    if mutation=='period': s['expires_at']=1900000000
    if mutation=='missing': s['measurements'].pop()
    if mutation=='reorder': s['measurements'].reverse()
    if mutation=='bool': s['measurements'][0]['measured']=True
    if mutation=='uncertainty': s['measurements'][0]['uncertainty']=-1
    if mutation=='extra': s['outcome']='CALIBRATED'
    if mutation=='oversize': s['evidence']='x'*16001
    with pytest.raises(Exception): c.submit(json.dumps(s))

def test_unauthorized(setup,direct_bob):
    vm,c,p,s,r=setup
    with vm.prank(direct_bob):
        with pytest.raises(Exception,match='authorized lab'): c.submit(json.dumps(s))
    c.submit(json.dumps(s))
    with vm.prank(direct_bob):
        with pytest.raises(Exception,match='owner only'): c.evaluate()

def test_immutable_bounded_history(setup):
    vm,c,p,s,r=setup
    c.submit(json.dumps(s))
    with pytest.raises(Exception): c.submit(json.dumps(s))
    first=json.loads(c.evaluate())
    with pytest.raises(Exception): c.evaluate()
    c.submit(json.dumps(s)); second=json.loads(c.evaluate())
    assert second['previous_hash']==first['receipt_hash']
    assert json.loads(c.get_receipt(1))==first
    assert json.loads(c.get_submission(1))==s
    c.submit(json.dumps(s)); c.evaluate()
    with pytest.raises(Exception): c.submit(json.dumps(s))
    assert json.loads(c.get_status())['pending'] is False

def test_expired(setup):
    setup[3].update(issued_at=1700000000,expires_at=1731536000)
    assert evaluate(setup)['result']['outcome']=='INCONCLUSIVE'

@pytest.mark.parametrize('mutation',['quote','status','extra','missing','unknown_quote'])
def test_malformed_model_reverts_without_receipt(setup,mutation):
    vm,c,p,s,r=setup
    if mutation=='quote': r['results']['quote']='Invented source quotation'
    if mutation=='status': r['results']['status']='PASS'
    if mutation=='extra': r['extra']=True
    if mutation=='missing': del r['identity']
    if mutation=='unknown_quote': r['results']['status']='UNKNOWN'
    vm.clear_mocks(); vm.mock_llm(r'^CALIBRATION_REVIEW:',json.dumps(r))
    c.submit(json.dumps(s))
    with pytest.raises(Exception): c.evaluate()
    assert json.loads(c.get_status())['pending'] is True

def test_duplicate_json_and_unknown_views(setup):
    c=setup[1]
    with pytest.raises(Exception): c.submit('{"a":1,"a":2}')
    for method in [lambda:c.get_submission(1),lambda:c.get_receipt(1),lambda:c.get_receipt(True),lambda:c.evaluate()]:
        with pytest.raises(Exception): method()

def test_separate_organization_and_lab(direct_vm,direct_deploy,direct_bob):
    p=fixture('policy.json'); p['lab']='0x'+direct_bob.hex()
    direct_vm.warp('2026-11-18T15:00:00Z')
    c=direct_deploy(str(ROOT/'contracts/calibration_iq.py'),json.dumps(p),sdk_version='v0.2.16')
    submission=json.dumps(fixture('submission.json'))
    with pytest.raises(Exception,match='authorized lab'): c.submit(submission)
    with direct_vm.prank(direct_bob):
        assert c.submit(submission)==1
        with pytest.raises(Exception,match='owner only'): c.evaluate()
    direct_vm.mock_llm(r'^CALIBRATION_REVIEW:',json.dumps(fixture('review.mock.json')))
    direct_vm.mock_llm(r'^CALIBRATION_GROUNDING:','{"grounded":true}')
    assert json.loads(c.evaluate())['result']['outcome']=='CALIBRATED'
