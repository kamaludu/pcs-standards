#!/usr/bin/env python3
# ==============================================================================
# File: toolchain/init_project.py
# Descrizione: Bootstrap crittografico Ed25519 e congelamento Trust Registry
# ==============================================================================
"""
PCS PROJECT INITIALIZER (Rev. 12.7.3 - PRE-COMMIT A BOOTSTRAP)
Genera la coppia Ed25519 e congela il Trust Registry e Blueprint prima di Commit A.
"""

import sys
import re
import stat
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "toolchain"))

from pcs_lib import compute_sha256_file
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

CORE_DIR = ROOT_DIR / "core"
PCS_DIR = ROOT_DIR / "pcs"
KEYS_DIR = ROOT_DIR / ".keys"
GITIGNORE_FILE = ROOT_DIR / ".gitignore"

BLUEPRINT_FILE = PCS_DIR / "blueprint.yaml"
TRUST_REGISTRY_FILE = PCS_DIR / "trust_registry.yaml"
PCS_CORE_FILE = CORE_DIR / "PCS.md"
SOP_CORE_FILE = CORE_DIR / "PCS-SOP.md"

def main():
    print("=================================================================")
    print(" PCS PROJECT INITIALIZER - PRE-COMMIT A BOOTSTRAP (Rev. 12.7.3)  ")
    print("=================================================================")

    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    gi = GITIGNORE_FILE.read_text(encoding="utf-8") if GITIGNORE_FILE.exists() else ""
    entries = [".keys/", "*.pem", "*.key"]
    to_add = [e for e in entries if e not in gi]
    if to_add:
        with open(GITIGNORE_FILE, "a", encoding="utf-8") as f:
            f.write("\n# Protezione chiavi private PCS\n" + "\n".join(to_add) + "\n")

    priv_key_path = KEYS_DIR / "maintainer_ed25519.pem"
    if not priv_key_path.exists():
        priv_key = ed25519.Ed25519PrivateKey.generate()
        pem = priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        priv_key_path.write_bytes(pem)
        try: priv_key_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except Exception: pass
    else:
        priv_key = serialization.load_pem_private_key(priv_key_path.read_bytes(), password=None)

    pub_hex = priv_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()
    print(f"[+] Chiave Pubblica Maintainer generata: {pub_hex}")

    tr_content = f"""# TRUST REGISTRY UFFICIALE (SOP-PCS-001 Rev. 3.5.1 Sez. 16.5.1)
# Delimitazione: Trust Anchor interno a Commit A; richiede ancoraggio esterno per trust di terzi.
trust_registry_version: "1.0.0"
registry_mode: "AUTHORITATIVE"
authorized_identities:
  - entity_id: "MAINTAINER-ROOT-01"
    role: "DEVELOPER"
    public_key_ed25519: "{pub_hex}"
    valid_from: "2026-08-28T00:00:00Z"
    valid_to: "2036-08-28T23:59:59Z"
"""
    TRUST_REGISTRY_FILE.write_text(tr_content, encoding="utf-8")

    pcs_hash = compute_sha256_file(PCS_CORE_FILE)
    sop_hash = compute_sha256_file(SOP_CORE_FILE)
    bp_text = BLUEPRINT_FILE.read_text(encoding="utf-8")
    
    # Sostituzioni ancorate e sicure
    bp_text = re.sub(r'(?m)^(\s*pcs_document_hash:\s*)["\']?[^"\']*["\']?', rf'\1"sha256:{pcs_hash}"', bp_text)
    bp_text = re.sub(r'(?m)^(\s*sop_document_hash:\s*)["\']?[^"\']*["\']?', rf'\1"sha256:{sop_hash}"', bp_text)
    BLUEPRINT_FILE.write_text(bp_text, encoding="utf-8")

    print(f"[+] Configurazioni sigillate in {BLUEPRINT_FILE.as_posix()} e {TRUST_REGISTRY_FILE.as_posix()}")
    print("[*] Pronto per Commit A (Frozen Source Snapshot)")

if __name__ == "__main__":
    main()
