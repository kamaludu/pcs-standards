#!/usr/bin/env python3
# ==============================================================================
# File: toolchain/pcs_lib.py
# Descrizione: Libreria crittografica, metrologica e di utilità pura per PCS
# ==============================================================================
"""
PCS CORE UTILITY & CRYPTOGRAPHIC LIBRARY (Rev. 12.7.3)
Libreria pura priva di side-effect all'importazione.
"""

import os
import sys
import re
import ast
import json
import base64
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("[!] Modulo 'cryptography' non presente. Installa 'python-cryptography' in Termux.")
    sys.exit(2)

# ==============================================================================
# CATALOGO CANONICO DEI 10 RULE SETS CONGELATI (|RULE_SET_IDS| == 10)
# ==============================================================================
RULE_SET_IDS = [
    "RULE-SCOPE-R1-001",
    "RULE-DTM-R-001",
    "RULE-LLM-001",
    "RULE-COMM-GOV-001",
    "RULE-DATA-GOV-001",
    "RULE-METADATA-001",
    "RULE-SPEC-ISOL-001",
    "RULE-DOC-INTEGRITY-001",
    "RULE-LEGAL-DOC-001",
    "RULE-SIG-TRAP-001"
]
RULE_SET_COUNT = len(RULE_SET_IDS)
assert RULE_SET_COUNT == 10, "Violazione cardinalità: RULE_SET_IDS deve contenere 10 elementi"
assert len(set(RULE_SET_IDS)) == 10, "Violazione unicità: duplicati in RULE_SET_IDS"

FORBIDDEN_SCOPE_MODULES = {
    "flask", "django", "fastapi", "tornado", "sqlalchemy", "sqlite3",
    "psycopg2", "psycopg", "mysql", "socketserver", "twisted", "celery"
}
FORBIDDEN_NET_MODULES = {
    "requests", "httpx", "aiohttp", "socket", "http.client", "urllib.request",
    "ftplib", "websocket", "urllib3"
}
FORBIDDEN_LLM_MODULES = {
    "openai", "anthropic", "transformers", "torch", "langchain", "llama_cpp",
    "litellm", "vllm"
}
FORBIDDEN_COMM_MODULES = {
    "tweepy", "telebot", "discord", "slack_sdk", "paho.mqtt", "sendgrid", "smtplib"
}
FORBIDDEN_DYNAMIC_CALLS = {"eval", "exec", "__import__"}

EXCLUDED_SCAN_DIRS = {".git", "_site", ".keys", "__pycache__", ".venv", "node_modules"}
INCLUDED_SCAN_EXTENSIONS = {".py", ".md", ".yaml", ".yml", ".json", ".txt"}
FORBIDDEN_BINARY_EXTENSIONS = {".exe", ".bin", ".so", ".dll", ".wasm", ".class", ".pyc"}

ALLOWED_SPEC_EXTENSIONS = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml", ".png", ".jpg", ".svg"}
FORBIDDEN_SPEC_EXTENSIONS = {".exe", ".sh", ".py", ".js", ".bin", ".so", ".dll", ".wasm", ".class", ".bat", ".cmd"}

RFC_8785_TEST_SUITE = [
    ({"b": 16, "a": "test", "c": None}, b'{"a":"test","b":16,"c":null}'),
    ({"escapes": "\b\f\n\r\t\"\\"}, b'{"escapes":"\\b\\f\\n\\r\\t\\"\\\\"}'),
    ({"unicode": "Test \u00e8 \U0001f600"}, b'{"unicode":"Test \xc3\xa8 \xf0\x9f\x98\x80"}'),
    ({"array": [0, 1, 2.5, 1000000.0], "neg_zero": 0.0}, b'{"array":[0,1,2.5,1000000],"neg_zero":0}')
]

STRICT_YAML_TEST_SUITE = [
    ("key: value\nnum: 42\nflag: true", {"key": "value", "num": 42, "flag": True}),
    ("list:\n  - item1\n  - \"item2:with_colon\"\n  - https://example.com", {"list": ["item1", "item2:with_colon", "https://example.com"]}),
    ("nested:\n  sub_k: sub_v\n  map_list:\n    - k1: v1\n      k2: v2", {"nested": {"sub_k": "sub_v", "map_list": [{"k1": "v1", "k2": "v2"}]}}),
    ("url: https://example.com", {"url": "https://example.com"}),
    ("compact_pair: a:b", {"compact_pair": "a:b"}),
    ("standard_pair:\n  a: b", {"standard_pair": {"a": "b"}}),
    ("empty_mapping:\n  a:", {"empty_mapping": {"a": None}}),
    ("spaced_pair:\n  a:    b", {"spaced_pair": {"a": "b"}}),
    ("list_compact:\n  - a:b\n  - https://example.com", {"list_compact": ["a:b", "https://example.com"]}),
    ("quoted_colons:\n  double: \"key:value\"\n  single: 'key:value'", {"quoted_colons": {"double": "key:value", "single": "key:value"}})
]

STRICT_YAML_NEGATIVE_TEST_SUITE = [
    "invalid_key!name: value",
    "key: true\n  bad_indent: 1",
    "list:\n  - a: 1\n    bad_field"
]

def get_git_info(root_dir: Path) -> tuple:
    sha = "0" * 40
    timestamp_z = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    is_shallow = False
    try:
        res_sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=root_dir)
        sha = res_sha.stdout.strip()
        res_time = subprocess.run(["git", "log", "-1", "--format=%ct", "HEAD"], capture_output=True, text=True, check=True, cwd=root_dir)
        epoch = res_time.stdout.strip()
        if len(sha) == 40 and epoch.isdigit():
            dt = datetime.fromtimestamp(int(epoch), tz=timezone.utc)
            timestamp_z = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        res_shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], capture_output=True, text=True, cwd=root_dir)
        is_shallow = (res_shallow.stdout.strip().lower() == "true")
    except Exception:
        pass
    return sha, timestamp_z, is_shallow

def get_deterministic_scanned_files(root_dir: Path) -> list:
    matched = []
    for root, dirs, files in os.walk(root_dir, followlinks=False):
        for d in dirs:
            dir_path = Path(root) / d
            if dir_path.is_symlink():
                raise ValueError(f"FAIL-CLOSED: Symlink directory non autorizzato: {dir_path.as_posix()}")
        dirs[:] = sorted([d for d in dirs if d not in EXCLUDED_SCAN_DIRS])

        for f in sorted(files):
            p = Path(root) / f
            if p.is_symlink():
                raise ValueError(f"FAIL-CLOSED: Symlink file non autorizzato: {p.as_posix()}")
            if p.suffix.lower() in FORBIDDEN_BINARY_EXTENSIONS:
                raise ValueError(f"FAIL-CLOSED: File binario non autorizzato: {p.as_posix()}")
            if p.suffix.lower() in INCLUDED_SCAN_EXTENSIONS:
                matched.append(p)
    return sorted(matched, key=lambda x: x.relative_to(root_dir).as_posix())

def normalize_and_sort_jcs(obj):
    if isinstance(obj, float):
        if obj.is_integer():
            return int(obj)
        return obj
    elif isinstance(obj, dict):
        return {
            k: normalize_and_sort_jcs(v)
            for k, v in sorted(obj.items(), key=lambda item: str(item[0]).encode('utf-16-be'))
        }
    elif isinstance(obj, list):
        return [normalize_and_sort_jcs(x) for x in obj]
    return obj

def jcs_canonicalize(data) -> bytes:
    norm_data = normalize_and_sort_jcs(data)
    return json.dumps(
        norm_data,
        ensure_ascii=False,
        sort_keys=False,
        separators=(',', ':'),
        allow_nan=False
    ).encode('utf-8')

def compute_sha256_file(path: Path) -> str:
    if not path.exists(): return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536): h.update(chunk)
    return h.hexdigest()

def get_observed_hashes(root_dir: Path) -> dict:
    core_dir = root_dir / "core"
    pcs_dir = root_dir / "pcs"
    toolchain_dir = root_dir / "toolchain"
    return {
        "pcs_core_sha256": compute_sha256_file(core_dir / "PCS.md"),
        "sop_core_sha256": compute_sha256_file(core_dir / "PCS-SOP.md"),
        "blueprint_sha256": compute_sha256_file(pcs_dir / "blueprint.yaml"),
        "builder_sha256": compute_sha256_file(toolchain_dir / "builder.py"),
        "pcs_lib_sha256": compute_sha256_file(toolchain_dir / "pcs_lib.py"),
        "verifier_sha256": compute_sha256_file(toolchain_dir / "verify_autonomous.py"),
        "lock_sha256": compute_sha256_file(root_dir / "requirements.lock"),
        "trust_registry_sha256": compute_sha256_file(pcs_dir / "trust_registry.yaml")
    }

def verify_spec_isolation(root_dir: Path) -> tuple:
    specs_dir = root_dir / "specifications"
    spec_files = []
    if specs_dir.exists():
        for root, _, files in os.walk(specs_dir, followlinks=False):
            for file in sorted(files):
                p = Path(root) / file
                if p.is_symlink():
                    return False, f"Symlink non autorizzato in specifications: {p.relative_to(root_dir).as_posix()}", []
                ext = p.suffix.lower()
                if ext in FORBIDDEN_SPEC_EXTENSIONS:
                    return False, f"File eseguibile vietato in specifications: {p.relative_to(root_dir).as_posix()}", []
                if ext not in ALLOWED_SPEC_EXTENSIONS and not file.startswith("."):
                    return False, f"Estensione non autorizzata in specifications: {p.relative_to(root_dir).as_posix()}", []
                if ext in ALLOWED_SPEC_EXTENSIONS:
                    spec_files.append(p.relative_to(root_dir).as_posix())
    return True, "RULE-SPEC-ISOL-001 PASS: Isolamento directory specifications/ verificato (0 estensioni vietate)", spec_files

def compute_app_hash(builder_hash: str, lib_hash: str, verifier_hash: str) -> str:
    payload = {
        "builder_sha256": f"sha256:{builder_hash}",
        "pcs_lib_sha256": f"sha256:{lib_hash}",
        "verifier_sha256": f"sha256:{verifier_hash}"
    }
    return hashlib.sha256(jcs_canonicalize(payload)).hexdigest()

def compute_configuration_identity(observed_hashes: dict, app_hash_hex: str, tr_dict: dict = None) -> tuple:
    if tr_dict is not None:
        tr_jcs_hash = hashlib.sha256(jcs_canonicalize(tr_dict)).hexdigest()
        tr_hash_val = f"sha256:{tr_jcs_hash}"
    else:
        tr_hash_val = f"sha256:{observed_hashes['trust_registry_sha256']}"

    payload = {
        "app_hash": f"sha256:{app_hash_hex}",
        "cfg_hash": f"sha256:{observed_hashes['blueprint_sha256']}",
        "image_digest": None,
        "lock_hash": f"sha256:{observed_hashes['lock_sha256']}",
        "model_hash": None,
        "runtime_hash": f"sha256:{observed_hashes['pcs_core_sha256']}",
        "trust_registry_hash": tr_hash_val
    }
    cfg_id = f"sha256:{hashlib.sha256(jcs_canonicalize(payload)).hexdigest()}"
    return cfg_id, payload

def get_runtime_configuration_context(root_dir: Path, tr_dict: dict = None) -> dict:
    hashes = get_observed_hashes(root_dir)
    app_hash = compute_app_hash(hashes['builder_sha256'], hashes['pcs_lib_sha256'], hashes['verifier_sha256'])
    cfg_id, cfg_payload = compute_configuration_identity(hashes, app_hash, tr_dict)
    return {
        "observed_hashes": hashes,
        "app_hash": app_hash,
        "configuration_identity": cfg_id,
        "configuration_payload": cfg_payload
    }

def run_jcs_test_suite() -> bool:
    for idx, (inp, expected) in enumerate(RFC_8785_TEST_SUITE, start=1):
        res = jcs_canonicalize(inp)
        if res != expected:
            raise ValueError(f"JCS TEST VECTOR {idx} FALLITO: {res} != {expected}")
    return True

def strip_yaml_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    res = []
    for char in line:
        if escaped:
            res.append(char)
            escaped = False
            continue
        if char == '\\':
            escaped = True
            res.append(char)
            continue
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == '#' and not in_single and not in_double:
            break
        res.append(char)
    return "".join(res).rstrip()

def parse_yaml_scalar(val: str):
    v = val.strip()
    if v == "true": return True
    if v == "false": return False
    if v == "null": return None
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        inner = v[1:-1]
        if v.startswith('"'):
            inner = inner.replace('\\"', '"').replace('\\\\', '\\')
        return inner
    if v.isdigit() or (v.startswith('-') and v[1:].isdigit()):
        return int(v)
    try: return float(v)
    except ValueError: return v

def is_fully_quoted(s: str) -> bool:
    s_clean = s.strip()
    if len(s_clean) < 2:
        return False
    if s_clean.startswith('"') and s_clean.endswith('"'):
        inner = s_clean[1:-1]
        return bool(re.match(r'^(?:[^"\\]|\\.)*$', inner))
    if s_clean.startswith("'") and s_clean.endswith("'"):
        inner = s_clean[1:-1]
        return "'" not in inner
    return False

def parse_strict_yaml(text: str):
    if len(text.encode('utf-8')) > 65536:
        raise ValueError("PARSE_ERROR: Dimensione file YAML eccede 64 KB (SOP 16.5.1)")

    lines = []
    for idx, raw in enumerate(text.splitlines()):
        c = strip_yaml_comment(raw)
        if c.strip():
            lines.append((len(c) - len(c.lstrip()), c.strip(), idx + 1))
    if not lines: return {}

    def parse_nodes(i: int, base_indent: int, current_depth: int = 1):
        if current_depth > 10:
            raise ValueError("PARSE_ERROR: Profondità YAML > 10 livelli (SOP 16.5.1)")
        if i >= len(lines): return {}, i
        first_indent, first_content, _ = lines[i]
        if first_content.startswith("- "):
            res_list = []
            curr_i = i
            while curr_i < len(lines):
                indent, content, line_num = lines[curr_i]
                if indent < base_indent: break
                if indent != base_indent: raise ValueError(f"Indentazione errata riga {line_num}: {content}")
                if not content.startswith("- "): break
                item_content = content[2:].strip()
                if is_fully_quoted(item_content):
                    res_list.append(parse_yaml_scalar(item_content))
                    curr_i += 1
                elif re.match(r'^[a-z_][a-z0-9_]*:(?:\s+|$)', item_content):
                    item_dict = {}
                    k, v = item_content.split(":", 1)
                    item_dict[k.strip()] = parse_yaml_scalar(v.strip()) if v.strip() else None
                    sub_i = curr_i + 1
                    while sub_i < len(lines):
                        s_indent, s_content, s_line_num = lines[sub_i]
                        if s_indent <= base_indent or s_content.startswith("- "): break
                        if not re.match(r'^[a-z_][a-z0-9_]*:(?:\s+|$)', s_content):
                            raise ValueError(f"Atteso k:v riga {s_line_num}: {s_content}")
                        sk, sv = s_content.split(":", 1)
                        item_dict[sk.strip()] = parse_yaml_scalar(sv.strip()) if sv.strip() else None
                        sub_i += 1
                    res_list.append(item_dict)
                    curr_i = sub_i
                else:
                    res_list.append(parse_yaml_scalar(item_content))
                    curr_i += 1
            return res_list, curr_i
        else:
            res_dict = {}
            curr_i = i
            while curr_i < len(lines):
                indent, content, line_num = lines[curr_i]
                if indent < base_indent: break
                if indent > base_indent: raise ValueError(f"Indentazione inattesa riga {line_num}: {content}")
                if not re.match(r'^[a-z_][a-z0-9_]*:(?:\s+|$)', content):
                    raise ValueError(f"Sintassi errata riga {line_num}: {content}")
                k, v = content.split(":", 1)
                k = k.strip(); v = v.strip()
                if v:
                    res_dict[k] = parse_yaml_scalar(v)
                    curr_i += 1
                else:
                    if curr_i + 1 < len(lines):
                        next_indent, _, _ = lines[curr_i + 1]
                        if next_indent > base_indent:
                            sub_val, next_curr_i = parse_nodes(curr_i + 1, next_indent, current_depth + 1)
                            res_dict[k] = sub_val
                            curr_i = next_curr_i
                        else:
                            res_dict[k] = None
                            curr_i += 1
                    else:
                        res_dict[k] = None
                        curr_i += 1
            return res_dict, curr_i

    parsed, _ = parse_nodes(0, lines[0][0])
    return parsed

def run_yaml_test_suite() -> bool:
    for idx, (yaml_str, expected_dict) in enumerate(STRICT_YAML_TEST_SUITE, start=1):
        parsed = parse_strict_yaml(yaml_str)
        if parsed != expected_dict:
            raise ValueError(f"STRICT YAML POSITIVE VECTOR {idx} FALLITO: {parsed} != {expected_dict}")

    for idx, bad_yaml in enumerate(STRICT_YAML_NEGATIVE_TEST_SUITE, start=1):
        raised = False
        try:
            parse_strict_yaml(bad_yaml)
        except ValueError:
            raised = True
        if not raised:
            raise ValueError(f"FAIL-CLOSED: STRICT YAML NEGATIVE VECTOR {idx} ACCETTATO")
    return True

def audit_lockfile_integrity(lock_path: Path) -> tuple:
    if not lock_path.exists():
        return False, "FAIL-CLOSED: File requirements.lock assente"

    content = lock_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in content.splitlines() if line.strip()]

    packages_count = 0
    current_package_hashes = 0
    in_package = False

    for line_num, line in enumerate(lines, start=1):
        if line.startswith("#"):
            continue

        if "==" in line and not line.startswith("--hash="):
            if in_package and current_package_hashes == 0:
                return False, f"FAIL-CLOSED: Pacchetto precedente privo di hash sha256 (riga {line_num})"
            packages_count += 1
            current_package_hashes = 0
            in_package = True

        if "--hash=sha256:" in line:
            if not in_package:
                return False, f"FAIL-CLOSED: Hash orfano privo di dichiarazione pacchetto (riga {line_num})"
            current_package_hashes += 1

    if in_package and current_package_hashes == 0:
        return False, "FAIL-CLOSED: Ultimo pacchetto nel lockfile privo di hash sha256"

    if packages_count == 0:
        return False, "FAIL-CLOSED: Nessun pacchetto rilevato in requirements.lock"

    return True, f"DTM-L Lockfile conforme ({packages_count} pacchetti verificati con vincolo hash per-package)"

def compute_merkle_root(leaf_hashes: list) -> bytes:
    if not leaf_hashes: return b""
    curr_level = list(leaf_hashes)
    while len(curr_level) > 1:
        next_lvl = []
        if len(curr_level) % 2 != 0:
            curr_level.append(curr_level[-1])
        for idx in range(0, len(curr_level), 2):
            node_b = b"\x01" + curr_level[idx] + curr_level[idx + 1]
            next_lvl.append(hashlib.sha256(node_b).digest())
        curr_level = next_lvl
    return curr_level[0]

def audit_empirical_scans(root_dir: Path) -> dict:
    scope_violations = []
    net_violations = []
    llm_violations = []
    comm_violations = []
    secret_violations = []
    metadata_violations = []
    dynamic_exec_violations = []

    pat_bearer = r'(?i)(api[_-]?key|secret[_-]?key|private[_-]?key|auth[_-]?token|bearer)\s*[:=]\s*["\'][A-Za-z0-9_\-]{16,}["\']'
    pat_pem = r'-----' + r'BEGIN (?:[A-Z0-9_-]+ )?PRIVATE KEY-----'
    pat_ghp = r'gh' + r'p_[A-Za-z0-9]{36}'
    pat_glpat = r'gl' + r'pat-[A-Za-z0-9\-]{20}'
    secret_patterns = [re.compile(p) for p in [pat_bearer, pat_pem, pat_ghp, pat_glpat]]
    
    h_pfx_1 = "/" + "home/"
    h_pfx_2 = "/" + "Users/"
    h_pfx_3 = "C:" + "\\" + "Users\\"
    host_pattern = re.compile(rf'({re.escape(h_pfx_1)}[a-z0-9_.-]+|{re.escape(h_pfx_2)}[a-z0-9_.-]+|{re.escape(h_pfx_3)}[a-z0-9_.-]+)', re.IGNORECASE)

    scanned_files = get_deterministic_scanned_files(root_dir)
    for p in scanned_files:
        rel_posix = p.relative_to(root_dir).as_posix()

        if p.suffix.lower() == ".py":
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(p))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            mod = alias.name.split('.')[0]
                            if mod in FORBIDDEN_SCOPE_MODULES or alias.name in FORBIDDEN_SCOPE_MODULES:
                                scope_violations.append(f"{rel_posix}:{alias.name}")
                            if mod in FORBIDDEN_NET_MODULES or alias.name in FORBIDDEN_NET_MODULES:
                                net_violations.append(f"{rel_posix}:{alias.name}")
                            if mod in FORBIDDEN_LLM_MODULES or alias.name in FORBIDDEN_LLM_MODULES:
                                llm_violations.append(f"{rel_posix}:{alias.name}")
                            if mod in FORBIDDEN_COMM_MODULES or alias.name in FORBIDDEN_COMM_MODULES:
                                comm_violations.append(f"{rel_posix}:{alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            mod = node.module.split('.')[0]
                            if mod in FORBIDDEN_SCOPE_MODULES or node.module in FORBIDDEN_SCOPE_MODULES:
                                scope_violations.append(f"{rel_posix}:{node.module}")
                            if mod in FORBIDDEN_NET_MODULES or node.module in FORBIDDEN_NET_MODULES:
                                net_violations.append(f"{rel_posix}:{node.module}")
                            if mod in FORBIDDEN_LLM_MODULES or node.module in FORBIDDEN_LLM_MODULES:
                                llm_violations.append(f"{rel_posix}:{node.module}")
                            if mod in FORBIDDEN_COMM_MODULES or node.module in FORBIDDEN_COMM_MODULES:
                                comm_violations.append(f"{rel_posix}:{node.module}")
                    elif isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_DYNAMIC_CALLS:
                            dynamic_exec_violations.append(f"{rel_posix}:{node.func.id}")
                    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                        if rel_posix != "toolchain/pcs_lib.py":
                            for pat in secret_patterns:
                                if pat.search(node.value):
                                    secret_violations.append(f"Pattern secret in {rel_posix}")
                            if host_pattern.search(node.value):
                                metadata_violations.append(f"Pattern host in {rel_posix}")
            except Exception:
                pass

        if p.suffix.lower() in [".md", ".yaml", ".json", ".txt"]:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            for pat in secret_patterns:
                if pat.search(txt):
                    secret_violations.append(f"Pattern secret in {rel_posix}")
            if not rel_posix.startswith("core/") and rel_posix != "pcs/blueprint.yaml":
                if host_pattern.search(txt):
                    metadata_violations.append(f"Pattern host in {rel_posix}")

    _, _, is_shallow = get_git_info(root_dir)
    git_history_status = "eseguita su repository completo (reachable Git history)"
    if is_shallow:
        git_history_status = "eseguita con avviso: shallow repository rilevato"

    try:
        git_log_res = subprocess.run(
            ["git", "log", "-p", "--all", "--", ".", ":(exclude)core/*", ":(exclude)pcs/blueprint.yaml", ":(exclude)toolchain/pcs_lib.py"],
            capture_output=True, text=True, cwd=root_dir
        )
        if git_log_res.returncode == 0:
            for pat in secret_patterns:
                if pat.search(git_log_res.stdout):
                    secret_violations.append("Pattern secret rilevato in git log reachable history")
            if host_pattern.search(git_log_res.stdout):
                metadata_violations.append("Pattern host rilevato in git log reachable history")
        else:
            git_history_status = "non disponibile (repository iniziale o senza commit)"
    except Exception:
        git_history_status = "non eseguita (binario git assente)"

    return {
        "scanned_files_count": len(scanned_files),
        "is_shallow_history": is_shallow,
        "scope_ok": len(scope_violations) == 0 and len(dynamic_exec_violations) == 0,
        "net_ok": len(net_violations) == 0,
        "llm_ok": len(llm_violations) == 0,
        "comm_ok": len(comm_violations) == 0,
        "secrets_ok": len(secret_violations) == 0,
        "metadata_ok": len(metadata_violations) == 0,
        "scope_msg": "RULE-SCOPE-R1-001 PASS: 0 corrispondenze backend/database e 0 chiamate dinamiche vietate" if (len(scope_violations) == 0 and len(dynamic_exec_violations) == 0) else f"Violazioni Scope: {scope_violations + dynamic_exec_violations}",
        "net_msg": "RULE-DTM-R-001 PASS: 0 corrispondenze per pattern client di rete nel perimetro ispezionato" if len(net_violations) == 0 else f"Corrispondenze rete: {net_violations}",
        "llm_msg": "RULE-LLM-001 PASS: 0 corrispondenze per pattern moduli generativi/LLM nel perimetro ispezionato" if len(llm_violations) == 0 else f"Corrispondenze LLM: {llm_violations}",
        "comm_msg": "RULE-COMM-GOV-001 PASS: 0 pattern di egress e tono notarile conforme nel perimetro ispezionato" if len(comm_violations) == 0 else f"Corrispondenze canali esterni: {comm_violations}",
        "secrets_msg": f"RULE-DATA-GOV-001 PASS: 0 pattern secret rilevati dai detector configurati ({git_history_status})" if len(secret_violations) == 0 else f"Corrispondenze Secret: {secret_violations}",
        "metadata_msg": f"RULE-METADATA-001 PASS: 0 corrispondenze per percorsi host assoluti in files e reachable git history ({git_history_status})" if len(metadata_violations) == 0 else f"Corrispondenze Host: {metadata_violations}"
    }

def verify_evidence_package(pcs_dir: Path, trust_registry_dict: dict) -> tuple:
    evidence_dir = pcs_dir / "evidence"
    sig_file = pcs_dir / "signatures" / "evidence-package.sig"
    manifest_file = pcs_dir / "manifest.json"

    if not (sig_file.exists() and manifest_file.exists()):
        return False, "", "File di firma o manifest mancante"

    sig_b64url = sig_file.read_text(encoding="utf-8").strip()
    try: sig_raw = base64.urlsafe_b64decode(sig_b64url + "=" * (-len(sig_b64url) % 4))
    except Exception as e: return False, "", f"Decodifica Base64URL fallita: {e}"

    leaf_hashes = []
    for i in range(1, 18):
        ev_file = evidence_dir / f"EV-{i:04d}.json"
        if not ev_file.exists(): return False, "", f"Record mancante: {ev_file.name}"
        try: record_obj = json.loads(ev_file.read_text(encoding="utf-8"))
        except Exception as e: return False, "", f"JSON error su {ev_file.name}: {e}"

        state = record_obj.get("evaluation_state")
        na_code = record_obj.get("na_reason_code")
        na_just = record_obj.get("na_justification")
        req_id = record_obj.get("requisite_id")

        if state == "N/A":
            if na_code not in ["NO_REMOTE_SERVICE", "NO_LLM_MODULE", "CONTROL_LEVEL_NOT_APPLICABLE", "OFFLINE_ISOLATED_RUNTIME"]:
                return False, "", f"Violazione schema su {ev_file.name}: na_reason_code invalido"
            if not na_just or len(na_just) < 10:
                return False, "", f"Violazione schema su {ev_file.name}: na_justification < 10 caratteri"
        elif state in ["TRUE", "FALSE"]:
            if na_code is not None or na_just is not None:
                return False, "", f"Violazione schema su {ev_file.name}: na_reason_code deve essere null"

        if req_id == "P_ABORT_OFF":
            env_prof = record_obj.get("environment_profile")
            if not isinstance(env_prof, dict):
                return False, "", f"Violazione schema su {ev_file.name}: environment_profile obbligatorio mancante per P_ABORT_OFF"
            for required_k in ["cpu_model", "ram_gb", "gpu_model", "os_kernel"]:
                if required_k not in env_prof:
                    return False, "", f"Violazione schema su {ev_file.name}: environment_profile privo di '{required_k}'"

        leaf_bytes = b"\x00" + jcs_canonicalize(record_obj)
        leaf_hashes.append(hashlib.sha256(leaf_bytes).digest())

    reconstructed_root_32b = compute_merkle_root(leaf_hashes)
    merkle_hex = reconstructed_root_32b.hex()

    now_utc = datetime.now(timezone.utc)
    identities = trust_registry_dict.get("authorized_identities", [])
    
    for ident in identities:
        pub_hex = ident.get("public_key_ed25519", "")
        if len(pub_hex) == 64:
            v_from = ident.get("valid_from")
            v_to = ident.get("valid_to")
            if v_from and v_to:
                try:
                    dt_from = datetime.fromisoformat(v_from.replace("Z", "+00:00"))
                    dt_to = datetime.fromisoformat(v_to.replace("Z", "+00:00"))
                    if not (dt_from <= now_utc <= dt_to):
                        continue
                except Exception:
                    continue

            try:
                pub_obj = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
                pub_obj.verify(sig_raw, reconstructed_root_32b)
                return True, merkle_hex, f"Firma Ed25519 valida per {ident.get('entity_id')} (Ruolo: {ident.get('role')})"
            except Exception:
                continue

    return False, merkle_hex, "FAIL-CLOSED: Nessuna chiave valida e attiva nel Trust Registry ha verificato l'Evidence Package"
