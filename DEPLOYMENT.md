# Deployment

1. Open https://studio.genlayer.com/contracts using Studio's built-in account. Import `contracts/calibration_iq.py`.
2. Choose Run and Debug and **Normal (Full Consensus)**. No MetaMask is required.
3. Set `policy_json` to the complete contents of `fixtures/policy.json`. Verify `lab` is the intended lab address, not an example address. Deploy.
4. Wait for deployment status FINALIZED with successful execution. Record the contract address, transaction hash, network and source SHA-256 in `evidence/deployment.json`.
5. With the authorized lab account, call `submit` with the contents of `fixtures/submission.json` (synthetic demonstration only). Wait for FINALIZED/SUCCESS.
6. With the original deployment owner, call `evaluate` with no arguments. Wait for FINALIZED/SUCCESS, read `get_receipt(1)` and save it. Never treat a returned transaction hash alone as completed execution.
7. Read all views, independently verify receipt hashes using `scripts/verify_receipt.py`, and preserve explorer contract/transaction links.

Use current issue/expiry dates for a new synthetic example and update the certificate text plus SHA-256 consistently. Do not submit an authentic private certificate as public fixture data. For a new calibration period deploy a new immutable policy contract.
