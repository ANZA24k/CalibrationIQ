# Verification evidence

## Automated checks

- `evidence/tests.txt`: 51 passing tests against the real GenLayer Python SDK, using mocked LLM I/O and serialization checking for nondeterministic closures.
- `evidence/genvm-check.txt`: AST lint and SDK semantic validation passed.
- `evidence/typecheck.txt`: no type errors.
- `evidence/abi.json`: machine-readable ABI, one constructor, two write methods and four views.

Coverage includes every outcome, integer tolerance/uncertainty boundaries, stale certificates, malformed inputs, duplicate JSON keys, forged quotations, independent validator disagreement, audit rejection, separate lab/organization authorization and immutable bounded receipt history.

## Live Studionet deployment

Contract: [CalibrationIQ](https://explorer-studio.genlayer.com/address/0xc78F2f9237860308e3D0F9d2219f51e59329265a).

`evidence/deployment.json` identifies the built-in Studio account and transaction hashes. `scripts/export_live.mjs` reads only public chain data. It requires FINALIZED status, MAJORITY_AGREE, full consensus, successful execution and byte-for-byte equality between the deployed code and the repository contract. A saved verification receipt and its canonical SHA-256 must also match. It refuses to label a finalized-but-disagreed transaction as successful verification.

```bash
npm ci --ignore-scripts
npm run evidence
python scripts/verify_receipt.py evidence/receipt-1.json
```

The live example returned **CALIBRATED**. Deployment, submission and evaluation all finalized with MAJORITY_AGREE and successful execution, in full-consensus mode. Three validators agreed on the evaluation. The stored receipt hash is `b33d5bd4b62d8a051131101a94af2f803519b0a4b25e0087de884dae06c8cd0c`.

- [Deployment transaction](https://explorer-studio.genlayer.com/transactions/0xb4dac6ab66a0c73837ed8dcc928b992c768b0b85f4240ddf84c832efc3ded556)
- [Submission transaction](https://explorer-studio.genlayer.com/transactions/0x17357281fa246ab57db56a78fb380a0a684045bc198734acc2786a2c3e9cdfcf)
- [Evaluation transaction](https://explorer-studio.genlayer.com/transactions/0xbb761816f08e13b87d2d9afd20a7b63509f308b008b838129f1c11186eeffb0c)
- [Finalized chain export](evidence/verified.json), [stored receipt](evidence/receipt-1.json), [independent validation](evidence/validation.json) and [Studio screenshot](evidence/live-proof.jpg).

The certificate and maintenance record are synthetic. CALIBRATED means documented compliance of this synthetic example; no real industrial instrument was calibrated.

## Earlier development attempts

`evidence/pre-release/` preserves the initial deployment and submitted records. `evidence/issuer-name-release/` preserves the subsequent version and its unsuccessful evaluation (FINALIZED with MAJORITY_DISAGREE). These are not successful end-to-end demonstrations. They motivated explicit certificate issuer naming and removing contradictory instructions from the separate quotation audit. The historical contracts remain publicly inspectable; the deployment linked above is the corrected source.

The receipt is historical. Consumers must also check the certificate expiry at their own current time. No external accreditation, signature PKI or revocation registry was used. This is not an independent security audit.
