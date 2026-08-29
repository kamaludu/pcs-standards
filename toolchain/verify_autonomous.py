#!/usr/bin/env python3
# ==============================================================================
# File: toolchain/verify_autonomous.py
# Descrizione: Verificatore deterministico a freddo (Cold Self-Verifier Rev. 12.7.3)
# ==============================================================================
"""
PCS DETERMINISTIC COLD SELF-VERIFIER (Rev. 12.7.3 - STANDALONE)
Esegue in modalità rigorosa e fail-closed:
1. Esecuzione esplicita delle suite di prova JCS (RFC 8785) e Strict YAML;
2. Audit sintattico e crittografico del lockfile DTM-L (requirements.lock);
3. Verifica di cardinalità del catalogo canonico dei 10 Rule Sets;
4. Dimostrazione formale di Exact Repository Corpus Equivalence (EXPECTED == ACTUAL);
5. Integrità degli hash vincolati nel Manifest (7 Frozen Assets + 1 Lockfile);
6. Verifica di discendenza Git (merge-base ancestor) e confinamento diff da Commit A;
7. Calcolo ConfigurationIdentity a 7 parametri conforme a SOP Sez. 14.2;
8. Ricostruzione dell'albero Merkle v1 e verifica crittografica Ed25519 con audit temporale.
"""

import os
import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "toolchain"))

from pcs_lib import (
    RULE_SET_IDS,
    RULE_SET_COUNT,
    run_jcs_test_suite,
    run_yaml_test_suite,
    audit_lockfile_integrity,
    verify_spec_isolation,
    parse_strict_yaml,
    get_runtime_configuration_context,
    verify_evidence_package
)

PCS_DIR = ROOT_DIR / "pcs"
MANIFEST_FILE = PCS_DIR / "manifest.json"
TRUST_REGISTRY_FILE = PCS_DIR / "trust_registry.yaml"
BLUEPRINT_FILE = PCS_DIR / "blueprint.yaml"
LOCK_FILE = ROOT_DIR / "requirements.lock"

def compute_expected_corpus(root_dir: Path) -> set:
    expected = {
        # 7 Frozen Project Assets
        "core/PCS.md",
        "core/PCS-SOP.md",
        "pcs/blueprint.yaml",
        "pcs/trust_registry.yaml",
        "toolchain/builder.py",
        "toolchain/pcs_lib.py",
        "toolchain/verify_autonomous.py",
        # 1 Pinned Dependency Lockfile
        "requirements.lock",
        # Artefatti di Bootstrap e Configurazione
        "toolchain/init_project.py",
        "toolchain/seal_archive.py",
        "LICENSE",
        "README.md",
        ".gitignore",
        ".github/workflows/deploy.yml",
        # Artefatti Derivati e Sigillati di Commit B
        "pcs/manifest.json",
        "pcs/signatures/evidence-package.sig",
        "pcs/reports/preflight-gate-log.json",
    }
    for i in range(1, 18):
        expected.add(f"pcs/evidence/EV-{i:04d}.json")

    iso_ok, iso_msg, spec_files = verify_spec_isolation(root_dir)
    if not iso_ok:
        raise ValueError(f"FAIL-CLOSED: {iso_msg}")
    for sf in spec_files:
        expected.add(sf)

    return expected

def get_actual_repository_corpus(root_dir: Path) -> tuple:
    actual = set()
    violations = []
    IGNORED_DIRS = {".git", ".keys", "__pycache__", ".venv", "node_modules", "_site"}

    for root, dirs, files in os.walk(root_dir, followlinks=False):
        for d in list(dirs):
            d_path = Path(root) / d
            if d_path.is_symlink():
                violations.append(f"FAIL-CLOSED: Symlink directory non autorizzato: {d_path.relative_to(root_dir).as_posix()}")

        dirs[:] = sorted([d for d in dirs if d not in IGNORED_DIRS and not (Path(root) / d).is_symlink()])

        for f in files:
            p = Path(root) / f
            rel_posix = p.relative_to(root_dir).as_posix()

            if p.is_symlink():
                violations.append(f"FAIL-CLOSED: Symlink file non autorizzato: {rel_posix}")
                continue
            if not p.is_file() or p.is_socket() or p.is_fifo() or p.is_block_device() or p.is_char_device():
                violations.append(f"FAIL-CLOSED: File speciale non-regular rilevato: {rel_posix}")
                continue

            actual.add(rel_posix)

    return actual, violations

def verify_exact_repository_corpus_equivalence(root_dir: Path) -> tuple:
    actual, forensic_violations = get_actual_repository_corpus(root_dir)
    if forensic_violations:
        return False, "; ".join(forensic_violations)

    try:
        expected = compute_expected_corpus(root_dir)
    except ValueError as ve:
        return False, str(ve)

    missing = expected - actual
    unaccounted = actual - expected

    if missing:
        missing_list = sorted(missing)
        diag = f"Elementi attesi mancanti: {missing_list}"
        if "pcs/reports/preflight-gate-log.json" in missing:
            diag += " (Suggerimento: eseguire prima 'python3 toolchain/builder.py' per generare il log di release)"
        return False, f"FAIL-CLOSED: {diag}"
    if unaccounted:
        return False, f"FAIL-CLOSED: Elementi estranei/non censiti nel corpus: {sorted(unaccounted)}"

    return True, f"Exact Repository Corpus Equivalence dimostrata: len(ACTUAL) == len(EXPECTED) == {len(actual)}"

def verify_commit_ancestry_and_diff(source_commit_sha: str, is_sealed_release: bool = True) -> tuple:
    if not source_commit_sha or len(source_commit_sha) != 40 or not re.match(r'^[a-f0-9]{40}$', source_commit_sha):
        if is_sealed_release:
            return False, f"FAIL-CLOSED: source_commit_sha non valido o assente nel Manifest ({source_commit_sha!r})"
        return True, "Ancestry check non applicabile in ambiente non sigillato"

    if source_commit_sha == "0" * 40:
        if is_sealed_release:
            return False, "FAIL-CLOSED: source_commit_sha non può essere nullo in una release sigillata"
        return True, "Ancestry check non applicabile su commit placeholder"

    try:
        res_anc = subprocess.run(["git", "merge-base", "--is-ancestor", source_commit_sha, "HEAD"], capture_output=True, text=True, cwd=ROOT_DIR)
        if res_anc.returncode != 0:
            return False, f"FAIL-CLOSED: Commit A ({source_commit_sha}) non è antenato raggiungibile di HEAD"

        res_diff = subprocess.run(["git", "diff", "--name-only", source_commit_sha, "HEAD"], capture_output=True, text=True, cwd=ROOT_DIR)
        if res_diff.returncode != 0:
            return False, f"FAIL-CLOSED: Impossibile calcolare il diff da Commit A ({source_commit_sha})"

        res_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=ROOT_DIR)
        uncommitted_files = [line[3:].strip().replace("\\", "/") for line in res_status.stdout.splitlines() if line.strip()]

        all_modified = set([f.strip().replace("\\", "/") for f in res_diff.stdout.splitlines() if f.strip()] + uncommitted_files)
        allowed_prefixes = ("pcs/manifest.json", "pcs/signatures/", "pcs/evidence/", "pcs/reports/")
        unauthorized = [df for df in all_modified if not any(df.startswith(pfx) for pfx in allowed_prefixes)]
        if unauthorized:
            return False, f"FAIL-CLOSED: Modifiche non autorizzate rispetto a Commit A: {unauthorized}"

        return True, f"Commit A confermato antenato raggiungibile; diff e working tree confinati su {len(all_modified)} artefatti autorizzati"
    except Exception as e:
        return False, f"FAIL-CLOSED: Errore esecuzione controlli Git: {e}"

def main():
    print("=================================================================")
    print(" PCS DETERMINISTIC COLD SELF-VERIFIER (Rev. 12.7.3 - STANDALONE) ")
    print(" Ambito: Internal C2 Gate & Cryptographic Chain Conformance      ")
    print("=================================================================")

    try:
        run_jcs_test_suite()
        print("[*] JCS RFC 8785 ENGINE: Test suite superata con successo")
        run_yaml_test_suite()
        print("[*] STRICT YAML ENGINE: Test suite superata su vettori positivi e negativi")
    except Exception as e:
        print(f"[!] FAIL-CLOSED: Fallimento motore di test: {e}")
        sys.exit(1)

    lock_ok, lock_msg = audit_lockfile_integrity(LOCK_FILE)
    if not lock_ok:
        print(f"[!] {lock_msg}")
        sys.exit(1)
    print(f"[*] DTM-L LOCKFILE INTEGRITY: {lock_msg}")

    if len(RULE_SET_IDS) != 10 or RULE_SET_COUNT != 10 or len(set(RULE_SET_IDS)) != 10:
        print(f"[!] FAIL-CLOSED: Inconsistenza cardinalità Rule Sets ({len(RULE_SET_IDS)} != 10)")
        sys.exit(1)
    print(f"[*] RULE SETS CATALOG: 10/10 Rule Sets canonici congelati e verificati")

    corpus_ok, corpus_msg = verify_exact_repository_corpus_equivalence(ROOT_DIR)
    if not corpus_ok:
        print(f"[!] {corpus_msg}")
        sys.exit(1)
    print(f"[*] CORPUS EQUIVALENCE: {corpus_msg}")

    if not MANIFEST_FILE.exists():
        print(f"[!] FAIL-CLOSED: File Manifest mancante: {MANIFEST_FILE.as_posix()}")
        sys.exit(1)

    try:
        manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        bp_dict = parse_strict_yaml(BLUEPRINT_FILE.read_text(encoding="utf-8"))
        tr_dict = parse_strict_yaml(TRUST_REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[!] ERRORE: Parsing fallito: {e}")
        sys.exit(1)

    ttl_str = str(bp_dict.get("lifecycle_and_invalidation", {}).get("ttl_expiration_utc", "2000-01-01T00:00:00Z"))
    try: ttl_dt = datetime.fromisoformat(ttl_str.replace("Z", "+00:00"))
    except Exception: ttl_dt = datetime(2000, 1, 1, tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > ttl_dt:
        print(f"[!] FAIL-CLOSED: Validità TTL DECORSA ({ttl_str}). Stato: RE-ASSESSMENT REQUIRED.")
        sys.exit(1)
    print(f"[*] CICLO DI VALIDITÀ: Finestra temporale valida fino al {ttl_str}")

    rt_ctx = get_runtime_configuration_context(ROOT_DIR, tr_dict)
    observed_hashes = rt_ctx["observed_hashes"]
    bound = manifest.get("bound_asset_hashes", {})
    for k, actual_v in observed_hashes.items():
        expected_v = bound.get(k)
        if expected_v != actual_v:
            print(f"[!] FAIL-CLOSED: Hash mismatch su {k}. Atteso: {expected_v}, Reale: {actual_v}")
            sys.exit(1)
    print("[*] HASH INTEGRITY: 7 Frozen Assets + 1 Lockfile conformi al Manifest (FrozenAssets != CompleteTCB)")

    source_commit = manifest.get("source_commit_sha", "")
    anc_ok, anc_msg = verify_commit_ancestry_and_diff(source_commit, is_sealed_release=True)
    if not anc_ok:
        print(f"[!] {anc_msg}")
        sys.exit(1)
    print(f"[*] COMMIT ANCESTRY & DIFF BOUNDARY: {anc_msg}")

    if rt_ctx["configuration_identity"] != manifest.get("configuration_identity"):
        print(f"[!] FAIL-CLOSED: ConfigurationIdentity non conforme (SOP Sez. 14.2 a 7 parametri): {rt_ctx['configuration_identity']} != {manifest.get('configuration_identity')}")
        sys.exit(1)
    print(f"[*] CONFIGURATION IDENTITY: Verificata su 7 parametri ex SOP Sez. 14.2 ({rt_ctx['configuration_identity']})")

    merkle_ok, merkle_hex, sig_msg = verify_evidence_package(PCS_DIR, tr_dict)
    if not merkle_ok or merkle_hex != manifest.get("merkle_root_v1"):
        print(f"[!] FAIL-CLOSED: Verifica crittografica fallita: {sig_msg}")
        sys.exit(1)

    print(f"[*] PCS-MERKLE-v1 ROOT: Confermato ({merkle_hex})")
    print(f"[*] CRITTOGRAFIA ED25519: {sig_msg}")
    print("=================================================================")
    print(" EVIDENCE_RESULT : PASS (17/17 record conformi a schema e hash)  ")
    print(" GATE_RESULT     : PASS (17/17 predicati GatePass == TRUE)       ")
    print(" ASSURANCE_CLAIM : C2_DEVELOPER_SELF_ATTESTATION (Within Boundary)")
    print(" ATTESTATION_ID  : PCS-C2-SELF-ATTESTATION-v1.0                  ")
    print("=================================================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
