# Post-Quantum Readiness for a Synthetic Clinic

Student project for the IBM Quantum Qiskit Hackathon at Miami-Dade College (Qiskit Fall Fest 2026).

**This repository uses synthetic examples only.** The fictional organization is called Bayside Community Clinic. Nothing here describes Miami-Dade College or any real clinic, patient, host, certificate, or network.

## Problem

Small organizations keep data that may need to stay private for years, but they often do not have a list of where RSA and elliptic-curve cryptography are used. That leaves them exposed to **harvest now, decrypt later**: someone can copy encrypted data today and try to decrypt it in the future if a much more capable quantum computer becomes available.

This project asks a practical question: *which uses of cryptography should a small clinic review first, and why?*

It does **not** claim that real encryption can be broken today, that a quantum computer has an advantage on this task, or that anyone knows when a cryptographically relevant quantum computer will exist.

## Approach

1. Build a labeled, 12-row **synthetic crypto inventory**.
2. Rank each row with a **transparent team rule** (not an official NIST or CISA score) using four visible factors: whether the algorithm is quantum-vulnerable, how long the data must stay secret, who can reach the system, and whether the crypto is used for key exchange or signatures. Ties go to the asset that looks easier to migrate.
3. Map the ranked list to a **Now / Next / Later** roadmap and to NIST's August 13, 2024 standards: [FIPS 203 (ML-KEM)](https://csrc.nist.gov/pubs/fips/203/final) for key establishment, [FIPS 204 (ML-DSA)](https://csrc.nist.gov/pubs/fips/204/final) for signatures, and [FIPS 205 (SLH-DSA)](https://csrc.nist.gov/pubs/fips/205/final) as a conservative signature backup. A hybrid classical-plus-post-quantum setup is allowed by NIST.
4. Run a small **Shor period-finding** teaching demo for N = 15, a = 7, on a simulator and on real IBM hardware, to show the mechanism behind the public-key threat and the gap to real RSA.

**AES is not treated the same way as RSA.** Grover's algorithm can speed up brute-force guessing against symmetric ciphers; a longer key such as AES-256 is the usual response. This project does not call AES-256 "quantum-proof," and it does not recommend swapping AES-256 for ML-KEM the way it recommends migrating RSA or elliptic-curve key exchange.

## Results

The Qiskit notebook is `pqc_readiness_qiskit.ipynb` (Qiskit 2.x). The circuit uses 8 qubits: 4 counting qubits and 4 work qubits, a compiled multiply-modulo-15 step made from swap and X gates, and an inverse `QFTGate`. Both runs used 1,024 shots.

The "expected outcomes" are the four ideal period-finding peaks: `0000`, `0100`, `1000`, and `1100`. Three of those give the factors 3 × 5 after a classical step. `0000` is an expected miss and does not yield a factor. So "100%" and "36%" are about landing on those four peaks, not about every shot factoring 15.

| Run | Device | Shots | Share of shots on the 4 expected outcomes | Notes |
| --- | --- | --- | --- | --- |
| Simulator | Qiskit `AerSimulator` | 1,024 | **100%** | Only four outcomes, each about 250 times. `0100`, `1000`, and `1100` factored as 3 × 5. |
| Real hardware | IBM `ibm_fez` | 1,024 | **36%** (vs about **25%** for a random guess among 16 bit strings) | Open Plan, `QiskitRuntimeService` with `channel="ibm_quantum_platform"`, `SamplerV2`, preset pass manager at `optimization_level=3`. Compiled depth **4,194**. Job ID **`dbpvbbtt7fqc738a2o0g`**. |

Visible hardware counts (other strings were present but not all were visible in the saved screenshot): `0100` 100, `1100` 92, `1000` 92, `0000` 87, `1001` 75, `1101` 70, `1011` 60, `0001` 58, `1111` 57. The four expected answers were still the top four, but they only barely stood out from the noise.

**Honest reading:** a tiny compiled demo for 15 already strains current hardware. Real RSA is still far out of reach. Organizations should still start planning, because data collected today may need to stay secret for a long time.

The inventory cell ranks the fictional **patient portal TLS** first (score 8, Now). Other **Now** items are the lab partner gateway, the staff VPN, and S/MIME email. AES-only storage lands in **Later**, which is intentional: the rule can tell RSA/elliptic-curve uses apart from AES.

## How to run

### Simulator-only (enough to reproduce the 100% result)

1. Open `pqc_readiness_qiskit.ipynb` in [Google Colab](https://colab.research.google.com/).
2. If needed, run `!pip install qiskit qiskit-aer qiskit-ibm-runtime` and restart the session when Colab asks.
3. Run the inventory cell (pandas is already available in Colab), the circuit-build cell, and the `AerSimulator` cell.
4. You can also run `synthetic_inventory.py` locally if you have pandas installed.

### Hardware (optional; this repo already includes one completed run)

1. Create a free account at the [IBM Quantum Platform](https://quantum.cloud.ibm.com/registration), then an **Open Plan** instance in **us-east**: [Instances](https://quantum.cloud.ibm.com/instances).
2. Create an API key from the [dashboard](https://quantum.cloud.ibm.com/). IBM shows the key only once. Store it in a password manager, not in this repository.
3. In Colab, open **Secrets**, create a secret named `IBM_API_KEY`, paste the key, and turn on **Notebook access**.
4. Run the hardware cell. It uses `channel="ibm_quantum_platform"` (the older `channel="ibm_quantum"` setting is retired and will fail).
5. If the original output is missing, retrieve job `dbpvbbtt7fqc738a2o0g` instead of submitting a new job, when that job is still available on the account.

**Do not commit API keys, Colab secret values, or screenshots that show a key.**

## Limitations

- Synthetic data only; no real systems were inventoried or scanned.
- The ranking formula is a team heuristic. Mid-ranked order can change if a factor is dropped.
- The N = 15 circuit is a known compiled teaching example. The modular-multiplication step is hand-built for 15 and uses knowledge of that special case. It is not a general implementation of Shor's algorithm.
- Factoring 15 does not imply that real RSA or ECC can be broken on current devices.
- No quantum-advantage claim, and no forecast of when a cryptographically relevant quantum computer will exist.
- Hardware noise is expected at compiled depth 4,194.
- Do not shut off RSA or elliptic-curve cryptography without a tested replacement. Prefer a planned migration, hybrid where a vendor supports it.
- NIST IR 8547 says quantum-vulnerable public-key cryptography (including RSA, ECDSA, and EdDSA) is **deprecated after 2030** and **disallowed after 2035 under NIST standards**. Federal high-impact systems have earlier dates for key establishment (December 31, 2030) and signatures (December 31, 2031). Those federal dates are background only, not requirements for the fictional clinic.

## Sources

- DeepStation event page (submission): https://deepstation.ai/hackathons/dj31ld8d96fuj1yi97ph4c4c
- Event README: https://github.com/robertloredo/Qiskit-Fallfest-Hackathon-2026---Miami-Dade-College/blob/main/README.md
- Participant handbook: https://github.com/robertloredo/Qiskit-Fallfest-Hackathon-2026---Miami-Dade-College/blob/main/PARTICIPANT_HANDBOOK.md
- NIST FIPS 203 (ML-KEM), final, August 13, 2024: https://csrc.nist.gov/pubs/fips/203/final
- NIST FIPS 204 (ML-DSA), final, August 13, 2024: https://csrc.nist.gov/pubs/fips/204/final
- NIST FIPS 205 (SLH-DSA), final, August 13, 2024: https://csrc.nist.gov/pubs/fips/205/final
- NIST IR 8547, *Transition to Post-Quantum Cryptography Standards*, final, October 27, 2026: https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8547.pdf
- NIST news release for IR 8547, October 27, 2026: https://www.nist.gov/news-events/news/2026/10/nist-report-provides-guidelines-transition-post-quantum-cryptography
- IBM Quantum tutorial, *Shor's algorithm* (includes compiled N = 15 examples): https://quantum.cloud.ibm.com/docs/en/tutorials/shors-algorithm
- IBM Quantum Platform: https://quantum.cloud.ibm.com/
