"""Verify a receipt's canonical hash; optionally check its predecessor hash."""
import hashlib
import json
import sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text())
actual=r.pop('receipt_hash')
expected=hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
if actual != expected:
    raise SystemExit('Invalid receipt hash')
if len(sys.argv)>2:
    previous=json.loads(Path(sys.argv[2]).read_text())
    if r['previous_hash'] != previous['receipt_hash'] or r['sequence'] != previous['sequence']+1 or r['contract'] != previous['contract'] or r['chain_id'] != previous['chain_id']:
        raise SystemExit('Invalid receipt chain')
print('Receipt hash verified:',actual)
