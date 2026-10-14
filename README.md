# Who Gets to Certify the AI Stack?

Research artifact for **Authority-Aware Verification and U.S. Alliance Strategy**, by Shivam Gupta (Independent Researcher).

This is a policy research and finite assurance-design artifact. It is not a GPU verifier, a new consensus protocol, a legal-compliance engine, or an implementation of a treaty. The paper distinguishes observed public software dependencies from constructed international arrangements. Boolean access structures and correlated-failure analysis have established prior work, credited in the paper.

## Results

- A two-supplier/two-jurisdiction constructed example admits a Boolean acceptance rule but no scalar or nonnegative weighted threshold.
- The example fails under simultaneous capture and withdrawal. A three-supplier/two-jurisdiction grid restores feasibility under the specified assumptions.
- Exhaustive checks: 7,371 specifications and 11,502 compiled decisions; zero mismatches.
- 200 structured budget scenarios match the analytical formulas.
- A nonrepresentative seeded synthetic corpus contains 2,000 assignments. 60 admit general but not scalar rules; 17 of those also defeat weighted rules.
- 19 software tests pass, including 11 upstream utility-boundary tests with documented mocks. No GPU hardware attestation is run.

## Reproduce

Use Python 3.12. Commands are from this repository root. Third-party source is downloaded into `work/` and ignored by Git.

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.lock
.venv/bin/python src/fetch_upstream.py work/nvtrust
.venv/bin/python src/audit_upstream.py work/nvtrust
NVTRUST_SOURCE="$PWD/work/nvtrust" .venv/bin/python -m pytest tests -q
.venv/bin/python src/experiments.py
.venv/bin/python src/figures.py
.venv/bin/python src/cli.py data/crossed_example.json
cd paper
tectonic manuscript.tex
tectonic abstract.tex
```

The original run used Python 3.12.14, macOS ARM64 and Tectonic 0.17.0. Core compiler calculations use Python's standard library; weighted-rule comparisons use SciPy/HiGHS. The complete installed package versions are in `requirements.lock`. A separate exhaustive checker enumerates all Boolean truth tables for n <= 3, then tests monotonicity and acceptance requirements without invoking the compiler. Synthetic cases use Python's standard `random.Random(20261014)` and independent uniform nonempty capture/denial subsets of five authorities. They have no empirical calibration or prevalence interpretation.

### Upstream audit

`src/fetch_upstream.py` checks exact revision `858ada9a17f58c482f578414ea2455498fa51e17` and nine file hashes. `results/upstream_audit.json` records seven source files, endpoint defaults, and two root certificates. `data/evidence_ledger.csv` links specific findings to sources and locators. The test suite executes upstream RIM retrieval and OCSP utility functions. Transport is mocked. OCSP branch tests stub chain appraisal, generate real signed synthetic status responses, and execute signature verification. This is not an end-to-end production certificate-chain or GPU security test.

### Threat semantics

A bad set is a maximal set of paths permitted to approve a false version of ONE specified predicate. A live set is a guaranteed set of HONEST paths approving a valid version within the declared epoch and timing requirements. Authentication, correct policy binding, predicate equivalence, and evidence freshness are prerequisites. Different predicates must not be voted together. Supplier association does not establish a compromise edge: it requires evidence or a labeled conservative scenario assumption.

Default examples test capture OR withdrawal. To test capture AND withdrawal, remove each allowed capture set from each allowed surviving set. Common upstream signing, policy, or membership authority must be modeled if relevant. Failure witnesses identify a live set contained in a bad set. Explicit families and portfolio enumeration may be exponential; no scalability claim is made.

## Contents

- `paper/manuscript.pdf` and `.tex`: full paper, three original figures, tables, proofs and appendices.
- `paper/abstract.pdf` and `.tex`: exactly two-page AWC proposal.
- `src/`: original compiler, weighted baseline, experiments, source extractor, fetcher, figures, and CLI.
- `tests/`: original-specification and mocked upstream-boundary checks.
- `results/`: complete aggregate and case-level derived outputs, source hashes and test receipt.
- `data/`: evidence ledger, literature/novelty review, declared example, venue requirements.

All research artifacts are as of 14 October 2026. Full-stack AI exports are the policy context; present export-license status is not evaluated. The proposal does not claim an existing international coalition deploys the constructed design.

## Citation

Gupta, Shivam. 2026. *Who Gets to Certify the AI Stack? Authority-Aware Verification and U.S. Alliance Strategy*. Independent research manuscript. https://github.com/shi1720/authority-aware-assurance.

## License

Original code: MIT. Original manuscript and figures: CC BY 4.0. Third-party code, documents, and trademarks retain their own terms; this repository includes metadata and retrieval instructions, not the vendor code. No endorsement by NVIDIA, AWC, or a government is implied.
