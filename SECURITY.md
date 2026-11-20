# Security model

Deploy only after independently verifying the lab address and equipment policy. The organization and lab keys are separate authorities even though the synthetic demonstration uses one Studio account. There are no upgrades, account replacements, fund transfers, external URL fetches or arbitrary contract calls.

Evidence is public on-chain plaintext; remove personal and confidential information before submission. SHA-256 prevents unnoticed changes to submitted bytes but does not authenticate a real-world document. Authorized lab transactions attest the entire bundle, including measurements and certificate text. No PKI, accreditation registry or revocation oracle is integrated.

Prompt injection is addressed by fixed task instructions, JSON data boundaries, independent model execution, explicit exact-status comparison and a second quotation grounding audit. Evidence text remains adversarial; AI agreement is not a guarantee of correctness. The organization must still perform physical calibration and operational safety decisions.

Bounded inputs: policy 10KB; submission JSON 24KB; inline text 16KB; 16 measurement points; 3 submissions per contract; model review 6KB; audit 1KB; source quotes 8–600 characters. No automatic retry loops execute in the contract. Model failures revert; client retries should be limited to two. Corrections cannot erase past receipts, but no adjudicator or escrow is provided.

A missing/contradictory finding takes priority over submitted arithmetic because untrusted measurement claims cannot establish physical failure or success. Numeric uncertainty overlap produces CONDITIONAL only after full documentary support. Stale historical receipts must be checked against current certificate expiry and later maintenance outside the chain.

Report vulnerabilities privately to the repository owner through GitHub before publishing exploit details. This project has not had an independent audit.
