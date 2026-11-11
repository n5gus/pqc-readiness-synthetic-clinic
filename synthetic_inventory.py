
# SYNTHETIC inventory and a transparent priority rule.
# This cell does not describe any real clinic, patient, or MDC system.
# The scores below are our team's ranking rule, not an official NIST or CISA score.

import pandas as pd

print(
    "SYNTHETIC DATA DISCLAIMER: Every row is a made-up example for a student "
    "hackathon project about a fictional clinic named Bayside Community Clinic. "
    "It does not describe Miami-Dade College or any real organization, patient, or system."
)
print()
print("Our ranking rule (not an official score)")
print("  Quantum-vulnerable: No=0, Partly=1 (for example AES plus RSA key wrap), Yes=2")
print("  How long the data must stay secret: under 2 years=0, 2 to 7 years=1, over 7 years=2")
print("  Who can reach it: Internal=0, Partner=1, Internet=2")
print("  What the crypto is doing: Other=0, Signature=1, Key exchange or key transport=2")
print("  Priority score = the four numbers added together (0 to 8).")
print("  If two assets tie, the one that looks easier to migrate is listed first.")
print("  Tiers: Now = 7 or 8, Next = 4 to 6, Later = 0 to 3.")
print()

# confidentiality_years and other values are invented assumptions, not legal retention rules.
rows = [
    {
        "asset": "Patient portal (TLS)",
        "purpose": "Establish a secure web connection",
        "algorithm": "ECDHE + RSA certificate",
        "quantum_vulnerable": "Yes",
        "confidentiality_years": 10,
        "exposure": "Internet",
        "role": "Key exchange",
        "migration_ease": "Medium",
        "migration_notes": "Ask the vendor about hybrid TLS with ML-KEM (FIPS 203).",
    },
    {
        "asset": "Staff VPN",
        "purpose": "Protect remote staff access",
        "algorithm": "RSA-2048 (IKE)",
        "quantum_vulnerable": "Yes",
        "confidentiality_years": 5,
        "exposure": "Internet",
        "role": "Key exchange",
        "migration_ease": "Medium",
        "migration_notes": "Check the VPN vendor's post-quantum or hybrid roadmap.",
    },
    {
        "asset": "Lab partner gateway (TLS)",
        "purpose": "Share lab results with partner labs",
        "algorithm": "ECDHE + RSA certificate",
        "quantum_vulnerable": "Yes",
        "confidentiality_years": 10,
        "exposure": "Partner",
        "role": "Key exchange",
        "migration_ease": "Medium",
        "migration_notes": "Coordinate with the lab vendor; hybrid ML-KEM if supported.",
    },
    {
        "asset": "Email (S/MIME)",
        "purpose": "Encrypt and sign clinical email",
        "algorithm": "RSA-2048",
        "quantum_vulnerable": "Yes",
        "confidentiality_years": 7,
        "exposure": "Internet",
        "role": "Key transport",
        "migration_ease": "Hard",
        "migration_notes": "The encryption part is the harvest-now concern; plan signatures too.",
    },
    {
        "asset": "Insurance claims connection",
        "purpose": "Send claims to a payer",
        "algorithm": "RSA-2048 (TLS)",
        "quantum_vulnerable": "Yes",
        "confidentiality_years": 7,
        "exposure": "Partner",
        "role": "Key exchange",
        "migration_ease": "Medium",
        "migration_notes": "Depends on the payer's TLS support for ML-KEM.",
    },
    {
        "asset": "Patient document signing",
        "purpose": "Sign discharge and consent forms",
        "algorithm": "RSA-2048",
        "quantum_vulnerable": "Yes",
        "confidentiality_years": 7,
        "exposure": "Internet",
        "role": "Signature",
        "migration_ease": "Hard",
        "migration_notes": "Move new signatures to ML-DSA (FIPS 204); keep a way to check old ones.",
    },
    {
        "asset": "Telehealth sessions",
        "purpose": "Encrypt live video visits",
        "algorithm": "ECDHE",
        "quantum_vulnerable": "Yes",
        "confidentiality_years": 1,
        "exposure": "Internet",
        "role": "Key exchange",
        "migration_ease": "Medium",
        "migration_notes": "Sessions are short-lived, but the service is still internet-facing.",
    },
    {
        "asset": "Backup storage",
        "purpose": "Encrypt stored backups and wrap the keys",
        "algorithm": "AES-256 with RSA key wrap",
        "quantum_vulnerable": "Partly",
        "confidentiality_years": 10,
        "exposure": "Internal",
        "role": "Key transport",
        "migration_ease": "Medium",
        "migration_notes": "AES-256 can stay; migrate the RSA wrap to ML-KEM (FIPS 203).",
    },
    {
        "asset": "Intranet app code signing",
        "purpose": "Verify an internal app has not been altered",
        "algorithm": "ECDSA P-256",
        "quantum_vulnerable": "Yes",
        "confidentiality_years": 2,
        "exposure": "Internal",
        "role": "Signature",
        "migration_ease": "Hard",
        "migration_notes": "Internal only; plan how older signed builds will still verify.",
    },
    {
        "asset": "Admin SSH to Wi-Fi controllers",
        "purpose": "Authenticate administrators",
        "algorithm": "Ed25519",
        "quantum_vulnerable": "Yes",
        "confidentiality_years": 1,
        "exposure": "Internal",
        "role": "Signature",
        "migration_ease": "Easy",
        "migration_notes": "Short-lived internal access, but Ed25519 is still quantum-vulnerable.",
    },
    {
        "asset": "EHR database at rest",
        "purpose": "Encrypt stored medical records",
        "algorithm": "AES-256",
        "quantum_vulnerable": "No",
        "confidentiality_years": 10,
        "exposure": "Internal",
        "role": "Other",
        "migration_ease": "Easy",
        "migration_notes": "Not the same threat as RSA or elliptic-curve crypto; keep AES-256 and review key management.",
    },
    {
        "asset": "Staff laptop disk encryption",
        "purpose": "Encrypt data if a laptop is lost or stolen",
        "algorithm": "AES-256",
        "quantum_vulnerable": "No",
        "confidentiality_years": 5,
        "exposure": "Internal",
        "role": "Other",
        "migration_ease": "Easy",
        "migration_notes": "Control row: AES-256 is not treated as a post-quantum algorithm swap.",
    },
]

QV = {"No": 0, "Partly": 1, "Yes": 2}
EXPOSURE = {"Internal": 0, "Partner": 1, "Internet": 2}
EASE_RANK = {"Easy": 0, "Medium": 1, "Hard": 2}  # lower means easier; used only to break ties


def secrecy_score(years):
    if years < 2:
        return 0
    if years <= 7:
        return 1
    return 2


def role_score(role):
    # Key transport is grouped with key exchange because both can leak data later
    # if today's ciphertext is stored and decrypted in the future.
    if role in ("Key exchange", "Key transport"):
        return 2
    if role == "Signature":
        return 1
    return 0


def suggested_path(row):
    if row["quantum_vulnerable"] == "No":
        return "Keep AES-256; review how keys are stored. No FIPS 203/204/205 swap for the bulk cipher."
    if "S/MIME" in row["asset"]:
        return "FIPS 203 (ML-KEM) for the encryption part; FIPS 204 (ML-DSA) for signatures. Hybrid allowed."
    if row["role"] in ("Key exchange", "Key transport"):
        return "FIPS 203 (ML-KEM); a hybrid classical-plus-PQC setup is allowed."
    if row["role"] == "Signature":
        return "FIPS 204 (ML-DSA); FIPS 205 (SLH-DSA) is a conservative backup."
    return "Review case by case."


def tier_for(score):
    if score >= 7:
        return "Now"
    if score >= 4:
        return "Next"
    return "Later"


def reason(row):
    qv = row["quantum_vulnerable"]
    years = row["confidentiality_years"]
    if years < 2:
        secret = f"data is assumed to need secrecy for under 2 years ({years})"
    elif years <= 7:
        secret = f"data is assumed to need secrecy for 2 to 7 years ({years})"
    else:
        secret = f"data is assumed to need secrecy for more than 7 years ({years})"
    bits = [
        f"quantum-vulnerable crypto: {qv} ({row['algorithm']})",
        secret,
        f"exposure: {row['exposure']}",
        f"role: {row['role']}",
    ]
    return (
        f"Score {row['priority_score']} ({row['tier']}). "
        f"Reasons: {'; '.join(bits)}. "
        f"Suggested path: {row['suggested_path']}"
    )


df = pd.DataFrame(rows)
df["s_qv"] = df["quantum_vulnerable"].map(QV)
df["s_secret"] = df["confidentiality_years"].map(secrecy_score)
df["s_exposure"] = df["exposure"].map(EXPOSURE)
df["s_role"] = df["role"].map(role_score)
df["priority_score"] = df["s_qv"] + df["s_secret"] + df["s_exposure"] + df["s_role"]
df["tier"] = df["priority_score"].map(tier_for)
df["ease_rank"] = df["migration_ease"].map(EASE_RANK)
df["suggested_path"] = df.apply(suggested_path, axis=1)
df["reason"] = df.apply(reason, axis=1)

ranked = df.sort_values(
    by=["priority_score", "ease_rank", "asset"],
    ascending=[False, True, True],
).reset_index(drop=True)
ranked.insert(0, "rank", range(1, len(ranked) + 1))

show = ranked[
    [
        "rank",
        "asset",
        "algorithm",
        "priority_score",
        "tier",
        "migration_ease",
        "suggested_path",
    ]
]
print(show.to_string(index=False))
print()
print("Why each asset received its score")
for _, row in ranked.iterrows():
    print(f"{row['rank']}. {row['asset']}: {row['reason']}")

# A simple check: if we ignored exposure, would the top 3 change?
alt = df.copy()
alt["alt_score"] = alt["s_qv"] + alt["s_secret"] + alt["s_role"]
alt_ranked = alt.sort_values(
    by=["alt_score", "ease_rank", "asset"],
    ascending=[False, True, True],
)
top_default = list(ranked.head(3)["asset"])
top_alt = list(alt_ranked.head(3)["asset"])
print()
print("Sensitivity check (not a second official ranking)")
print("Top 3 with our full rule:", ", ".join(top_default))
print("Top 3 if we ignore exposure:", ", ".join(top_alt))
if top_default == top_alt:
    print("The top 3 stayed the same in this check.")
else:
    print(
        "The very top items are close, but mid-ranked order can change if we drop a factor. "
        "That is expected, and it is a reason to show the rule instead of hiding it."
    )
