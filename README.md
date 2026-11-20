# CalibrationIQ

Standalone GenLayer Intelligent Contract for industrial instrument calibration evidence. One deployment locks one instrument, its authorized laboratory, certificate issuer name, required procedure, maintenance rule, integer units and test points. No frontend or custody of funds is required.

The lab attests the complete submission by sending the transaction from its locked address. The organization deploying the contract evaluates it. GenLayer validators independently examine the same immutable records; integer arithmetic then derives the outcome. This verifies documented calibration, **not physical accuracy, laboratory accreditation or authenticity of a real-world signature**.

[Studionet contract](https://explorer-studio.genlayer.com/address/0xc78F2f9237860308e3D0F9d2219f51e59329265a) · Chain ID 61999 · [Verification evidence](EVIDENCE.md)

Live synthetic example: **CALIBRATED**, with all three lifecycle transactions finalized under full consensus. Deployed source and receipt SHA-256 independently verified. **51 SDK tests pass**, plus GenVM lint, semantic validation and type checking.

## Outcomes

Priority is deliberately conservative:

| Outcome | Rule |
|---|---|
| INCONCLUSIVE | Any documentary check is UNKNOWN/CONTRADICTED, or certificate expired at evaluation time |
| OUT_OF_TOLERANCE | All documents supported and at least one absolute measurement error exceeds its locked tolerance |
| CONDITIONAL | Errors within tolerance, but error + stated expanded uncertainty exceeds tolerance at any point |
| CALIBRATED | All documentary checks supported; certificate current; error + uncertainty within tolerance at every point |

Tolerance equality passes. Expiry equality fails. CONDITIONAL does not authorize equipment use; the organization must assess the uncertainty overlap. Expired certificates never imply physical out-of-tolerance.

## Lifecycle

1. Deploy `contracts/calibration_iq.py` with `policy_json` from `fixtures/policy.json`; use the intended laboratory's address. All policy fields are immutable.
2. Authorized lab calls `submit(submission_json)`. Exactly one measured result and nonnegative uncertainty are required per locked reference, in the same order. Hash the exact UTF-8 evidence text with SHA-256.
3. Deployment owner calls `evaluate()`. Real `gl.nondet.exec_prompt` calls run inside `gl.vm.run_nondet_unsafe`.
4. Each validator repeats the documentary assessment independently, requires identical check statuses, then separately audits the leader's exact source quotations. Quotes must also pass deterministic substring validation. Free-form quotes may differ between validators.
5. Read `get_receipt(sequence)`, `get_submission(sequence)`, `get_policy()` and `get_status()`.
6. Up to three sequential, lab-attested submissions support a bounded correction/challenge cycle. Each requires a new evaluation, preserves the previous record and links to its receipt hash. No overwrite, delete, policy edits or authority transfers exist. Deploy a new cycle for subsequent calibration periods.

Checks cover identity/certificate dates, procedure compliance, reference-standard traceability, maintenance and agreement of **every** numeric result/unit/scale with the certificate. Missing or contradictory documents produce INCONCLUSIVE. Malformed model output or validator disagreement fails the transaction and creates no receipt; do not mistake a failed transaction for INCONCLUSIVE. Applications should make at most two retries and surface a failed consensus operation.

## Evidence and trust

`evidence` is inline UTF-8 certificate/maintenance text, bounded to 16,000 bytes and bound by `evidence_sha256`. Its exact bytes are already in immutable transaction calldata, avoiding mutable URLs, redirects and SSRF. The full submission and policy use canonical JSON (`sort_keys=True`, compact separators, ASCII escaping); receipts hash their complete canonical object excluding `receipt_hash`. Chain ID and contract address prevent cross-deployment receipt ambiguity.

Only the locked lab account can attest measurements and records. Account control is the authentication boundary; a hash alone is not proof of issuer identity. Vet that lab off-chain before deployment. The demo intentionally uses the Studio account as both organization and demo lab. It uses synthetic records only.

All values are integers. `physical_value = integer / scale`, with a common unit and scale for reference, measured, tolerance and uncertainty. Uncertainty is a submitted expanded uncertainty already expressed in these units; coverage factor interpretation belongs in the locked procedure. No floating-point arithmetic, automatic unit conversion or silent rounding occurs.

Receipts are historical findings at `evaluated_at`; a saved CALIBRATED result does not remain valid forever. Check the submission's expiry against current time when consuming a receipt. Revocations, later damage, compromised lab keys and unsubmitted maintenance changes are outside this contract's knowledge.

## Verification

```bash
python -m pip install -r requirements-dev.txt
pytest -q
# Real SDK lint, semantic validation and ABI extraction:
genvm-lint check contracts/calibration_iq.py
genvm-lint typecheck contracts/calibration_iq.py
genvm-lint schema contracts/calibration_iq.py
python scripts/verify_receipt.py evidence/receipt-1.json
```

Direct tests use the actual GenLayer Python SDK (GenVM release v0.2.16) and mocked model responses, with nondeterministic closure serialization checked. They cover all four outcomes, boundary errors, expiry, authorized callers, malformed records/model output, grounding audit rejection, independent validator disagreement and append-only history. Mock tests demonstrate logic, not real-world certificate authenticity. `fixtures/review.mock.json` is never imported by the deployed contract.

See [DEPLOYMENT.md](DEPLOYMENT.md), [EVIDENCE.md](EVIDENCE.md), [SECURITY.md](SECURITY.md) and [SUBMISSION.md](SUBMISSION.md).

## Official references

- [Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- [Calling LLMs](https://docs.genlayer.com/developers/intelligent-contracts/features/calling-llms)
- [GenLayer SDK](https://sdk.genlayer.com/v0.2.7/api/genlayer.html)
- [Direct testing](https://docs.genlayer.com/api-references/genlayer-test/direct)

MIT licensed. No claim of regulatory certification, safety approval or independent security audit.
