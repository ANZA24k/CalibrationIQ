"""Synthetic data only. Dates and lab address must match the intended demo."""
from pathlib import Path
import json, hashlib
root = Path(__file__).resolve().parents[1] / 'fixtures'
p = {'equipment_id':'PRESSURE-P17','unit':'kPa','scale':1000,'lab':'0x67Da51Fd9AC1d52F34F5d01d06da8548979fC514','lab_name':'Demo Calibration Lab','procedure':'CP-17: compare at 0, 50 and 100 kPa after 15-minute warmup; record uncertainty.','maintenance_rule':'Document inspection with no leaks or unresolved defects.','max_age_seconds':31536000,'points':[{'reference':v,'tolerance':500} for v in [0,50000,100000]]}
evidence = '''SYNTHETIC DEMONSTRATION: no real instrument was calibrated.
Certificate DEMO-001: PRESSURE-P17, laboratory Demo Calibration Lab.
Issued Unix 1794960000; expires Unix 1826496000. Scale 1000 integer units per kPa.
CP-17 performed: 15-minute warmup then comparison at 0, 50 and 100 kPa.
Reference STD-42, SI traceability certificate REF-42 valid until 1830000000.
Inspection and maintenance: no leaks or unresolved defects.
Results (reference, measured, uncertainty) in scaled kPa integers:
(0, 100, 50); (50000, 50100, 50); (100000, 100100, 50).
'''
s={'equipment_id':p['equipment_id'],'certificate_id':'DEMO-001','issued_at':1794960000,'expires_at':1826496000,'measurements':[{'reference':v,'measured':v+100,'uncertainty':50} for v in [0,50000,100000]],'evidence':evidence,'evidence_sha256':hashlib.sha256(evidence.encode()).hexdigest()}
quotes={'identity':'Certificate DEMO-001: PRESSURE-P17, laboratory Demo Calibration Lab.','procedure':'CP-17 performed: 15-minute warmup then comparison at 0, 50 and 100 kPa.','traceability':'Reference STD-42, SI traceability certificate REF-42 valid until 1830000000.','maintenance':'Inspection and maintenance: no leaks or unresolved defects.','results':'(0, 100, 50); (50000, 50100, 50); (100000, 100100, 50).'}
review={k:{'status':'SUPPORTED','quote':v} for k,v in quotes.items()}
for name,data in [('policy.json',p),('submission.json',s),('review.mock.json',review)]:
    (root/name).write_text(json.dumps(data,indent=2)+'\n')
