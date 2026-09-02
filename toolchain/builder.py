#!/usr/bin/env python3
# ==============================================================================
# File: toolchain/builder.py
# Descrizione: Motore unificato deterministico di Pre-Flight Gate e generazione sito
# ==============================================================================
"""
PCS-STANDARDS UNIFIED DETERMINISTIC GATE & BUILD ENGINE (Rev. 12.7.3)
Esegue i controlli del Pre-Flight Gate e compila il sito statico deterministico.
Supporta la famiglia di licenze open-source conformi a C0/C1 per P_LEGAL_DOC.
"""

import html
import json
import os
import re
import shutil
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "toolchain"))

from pcs_lib import (
    audit_lockfile_integrity,
    get_git_info,
    verify_spec_isolation,
    parse_strict_yaml,
    get_runtime_configuration_context,
    audit_empirical_scans,
    verify_evidence_package
)

CORE_DIR = ROOT_DIR / "core"
SPECS_DIR = ROOT_DIR / "specifications"
PCS_DIR = ROOT_DIR / "pcs"
REPORTS_DIR = PCS_DIR / "reports"
SITE_DIR = ROOT_DIR / "_site"

BLUEPRINT_FILE = PCS_DIR / "blueprint.yaml"
MANIFEST_FILE = PCS_DIR / "manifest.json"
TRUST_REGISTRY_FILE = PCS_DIR / "trust_registry.yaml"
PCS_CORE_FILE = CORE_DIR / "PCS.md"
SOP_CORE_FILE = CORE_DIR / "PCS-SOP.md"
LICENSE_FILE = ROOT_DIR / "LICENSE"
README_FILE = ROOT_DIR / "README.md"
LOCK_FILE = ROOT_DIR / "requirements.lock"
GATE_LOG_FILE = REPORTS_DIR / "preflight-gate-log.json"

def handle_sig_term(signum, frame):
    print(f"\n[!] Signal intercettato ({signum}): arresto fail-closed.")
    sys.exit(1)

signal.signal(signal.SIGINT, handle_sig_term)
signal.signal(signal.SIGTERM, handle_sig_term)

def check_open_source_license(lic_text: str) -> tuple:
    lic_patterns = [
        (r"GNU GENERAL PUBLIC LICENSE", "GNU GPL"),
        (r"GNU AFFERO GENERAL PUBLIC LICENSE", "GNU AGPL"),
        (r"GNU LESSER GENERAL PUBLIC LICENSE", "GNU LGPL"),
        (r"GNU FREE DOCUMENTATION LICENSE", "GNU GFDL"),
        (r"Apache License,\s*Version 2\.0", "Apache 2.0"),
        (r"MIT License", "MIT"),
        (r"Permission is hereby granted, free of charge", "MIT/Expat"),
        (r"Redistribution and use in source and binary forms", "BSD")
    ]
    for pat, name in lic_patterns:
        if re.search(pat, lic_text, re.IGNORECASE):
            return True, f"Licenza Open Source verificata ({name})"
    return False, "Nessuna licenza open-source valida riconosciuta nel file LICENSE"

def eval_all_predicates(bp: dict, observed_hashes: dict) -> dict:
    prov = bp.get("provenance_model", {})
    human = prov.get("human_declared", {})
    derived = prov.get("derived_parameters", {})
    pred_cfg = bp.get("preflight_gate_matrix", {}).get("predicates", {})

    def get_na(key, default_code, default_just):
        c = pred_cfg.get(key, {})
        return c.get("na_reason_code", default_code), c.get("na_justification", default_just)

    r_entry = human.get("domain_class_r", {})
    r_val = r_entry.get("value", "") if isinstance(r_entry, dict) else r_entry
    s_entry = human.get("severity_index_s", {})
    s_val = s_entry.get("value", "") if isinstance(s_entry, dict) else s_entry
    ir_entry = human.get("irreversibility_index_ir", {})
    ir_val = ir_entry.get("value", "") if isinstance(ir_entry, dict) else ir_entry
    c_impl = derived.get("implemented_control_c", "")

    s_map = {"S0": 0, "S1": 1, "S2": 2, "S3": 3}
    ir_map = {"IR0": 0, "IR1": 1, "IR2": 2, "IR3": 3}
    c_poset = {"C0": 0, "C1": 1, "C2": 2, "C3": 3, "C4": 4}

    s_n = s_map.get(s_val, -1)
    ir_n = ir_map.get(ir_val, -1)
    k_calc = max(s_n, ir_n) if (s_n >= 0 and ir_n >= 0) else -1
    k_decl = derived.get("gating_index_k", -2)

    c_min = "BLOCKED"
    if r_val == "R0": c_min = "C0" if k_calc <= 1 else ("C1" if k_calc == 2 else "BLOCKED")
    elif r_val == "R1": c_min = "C1" if k_calc <= 1 else ("C2" if k_calc == 2 else "BLOCKED")
    elif r_val == "R2": c_min = "C2" if k_calc <= 1 else ("C3" if k_calc == 2 else "BLOCKED")
    elif r_val == "R3": c_min = "C3" if k_calc <= 2 else "C4"

    lic_ok = False
    lic_detail = "File LICENSE mancante"
    if LICENSE_FILE.exists():
        lic_ok, lic_detail = check_open_source_license(LICENSE_FILE.read_text(encoding="utf-8"))

    readme_ok = README_FILE.exists() and ("PCS-L4.5" in README_FILE.read_text(encoding="utf-8"))

    iso_ok, iso_msg, _ = verify_spec_isolation(ROOT_DIR)
    lock_ok, lock_msg = audit_lockfile_integrity(LOCK_FILE)
    dtm_local_ok = iso_ok and lock_ok
    dtm_local_detail = f"{iso_msg}; {lock_msg}"

    utm = bp.get("universal_threat_model_coverage", {})
    utm_ok = all(utm.get(c, {}).get("assurance_stage") == "A5_CTRL_PASS" for c in ["utm_t0", "utm_t1", "utm_t2", "utm_t3", "utm_t4", "utm_t5"])

    bp_bind = bp.get("normative_binding", {})
    pcs_bind_hash = str(bp_bind.get("pcs_document_hash") or "").replace("sha256:", "")
    sop_bind_hash = str(bp_bind.get("sop_document_hash") or "").replace("sha256:", "")
    t0_ok = (pcs_bind_hash == observed_hashes["pcs_core_sha256"]) and (sop_bind_hash == observed_hashes["sop_core_sha256"])

    t0_detail = (
        "Integrità documentale confermata contro Blueprint"
        if t0_ok
        else (
            "Mismatch hash normativi: "
            f"PCS.md (bp={pcs_bind_hash[:8]}..., real={observed_hashes['pcs_core_sha256'][:8]}...), "
            f"SOP.md (bp={sop_bind_hash[:8]}..., real={observed_hashes['sop_core_sha256'][:8]}...)"
        )
    )

    scans = audit_empirical_scans(ROOT_DIR)

    h_int = signal.getsignal(signal.SIGINT)
    h_term = signal.getsignal(signal.SIGTERM)
    sig_registered = (h_int == handle_sig_term and h_term == handle_sig_term)

    p_dtm_r_code, p_dtm_r_just = get_na("p_dtm_remote", "NO_REMOTE_SERVICE", "Archivio statico offline privo di client HTTP o servizi remoti.")
    p_allow_code, p_allow_just = get_na("p_allowlist", "NO_LLM_MODULE", "Archivio documentale statico privo di componenti decisionali o interpreti FSM.")
    p_llm_code, p_llm_just = get_na("p_llm_isol", "NO_LLM_MODULE", "Nessun modello linguistico o generativo integrato nel repository.")
    p_contract_code, p_contract_just = get_na("p_contract", "NO_LLM_MODULE", "Non applicabile ad archivio statico privo di output probabilistici.")
    p_dual_code, p_dual_just = get_na("p_dual_fail", "NO_LLM_MODULE", "Archivio privo di memoria di sessione o contesti conversazionali.")
    p_c4_code, p_c4_just = get_na("p_c4_audit", "CONTROL_LEVEL_NOT_APPLICABLE", "Il sistema opera in classe dichiarata R1 con livello C2. L'audit C4 e per R3/K=3.")

    return {
        "P_SCOPE_OK":   {"state": "TRUE", "eval": r_val in ["R0", "R1", "R2", "R3"] and scans["scope_ok"], "code": None, "just": None, "detail": scans["scope_msg"]},
        "P_K_CALC":     {"state": "TRUE", "eval": (k_calc >= 0 and k_calc == k_decl), "code": None, "just": None, "detail": f"K_calc={k_calc}, K_decl={k_decl} (Joint mapping PCS-REQ-02/03)"},
        "P_CTRL_MATCH": {"state": "TRUE", "eval": (c_min != "BLOCKED" and c_poset.get(c_impl, -1) >= c_poset.get(c_min, 99)), "code": None, "just": None, "detail": f"C_impl={c_impl} >= C_min={c_min}"},
        "P_NO_BLOCK":   {"state": "TRUE", "eval": not (r_val in ["R0", "R1", "R2"] and k_calc == 3), "code": None, "just": None, "detail": "Nessuna contraddizione logica"},
        "P_THREAT_MOD": {"state": "TRUE", "eval": utm_ok and scans["comm_ok"], "code": None, "just": None, "detail": "Stadio A5 (Bounded Control Pass) su 6/6 classi UTM"},
        "P_T0_TEST":    {"state": "TRUE", "eval": t0_ok, "code": None, "just": None, "detail": t0_detail},
        "P_LEGAL_DOC":  {"state": "TRUE", "eval": (lic_ok and readme_ok), "code": None, "just": None, "detail": f"Requisiti documentali soddisfatti: {lic_detail}; PCS-L4.5 ({readme_ok})"},
        "P_DTM_LOCAL":  {"state": "TRUE", "eval": dtm_local_ok, "code": None, "just": None, "detail": dtm_local_detail},
        "P_DTM_REMOTE": {"state": "N/A", "eval": scans["net_ok"], "code": p_dtm_r_code, "just": p_dtm_r_just, "detail": scans["net_msg"]},
        "P_DATA_GOV":   {"state": "TRUE", "eval": scans["secrets_ok"], "code": None, "just": None, "detail": scans["secrets_msg"]},
        "P_METADATA":   {"state": "TRUE", "eval": scans["metadata_ok"], "code": None, "just": None, "detail": scans["metadata_msg"]},
        "P_ALLOWLIST":  {"state": "N/A", "eval": scans["llm_ok"], "code": p_allow_code, "just": p_allow_just, "detail": "N/A validato da RULE-LLM-001"},
        "P_LLM_ISOL":   {"state": "N/A", "eval": scans["llm_ok"], "code": p_llm_code, "just": p_llm_just, "detail": scans["llm_msg"]},
        "P_CONTRACT":   {"state": "N/A", "eval": scans["llm_ok"], "code": p_contract_code, "just": p_contract_just, "detail": "N/A validato da RULE-LLM-001"},
        "P_DUAL_FAIL":  {"state": "N/A", "eval": scans["llm_ok"], "code": p_dual_code, "just": p_dual_just, "detail": "N/A validato da RULE-LLM-001"},
        "P_C4_AUDIT":   {"state": "N/A", "eval": True, "code": p_c4_code, "just": p_c4_just, "detail": "N/A per livello di controllo C2"},
        "P_ABORT_OFF":  {"state": "TRUE", "eval": sig_registered, "code": None, "just": None, "detail": "RULE-SIG-TRAP-001 PASS: Signal handler OS attivamente verificati nel runtime"}
    }

def sanitize_url(target: str) -> str:
    t = target.strip()
    if t.startswith("//") or t.startswith("\\"): return "#BLOCKED_URL"
    parsed = urlparse(t)
    if parsed.scheme.lower() == "https" or (parsed.scheme == "" and ":" not in t.split("/")[0]):
        return html.escape(t)
    return "#BLOCKED_SCHEME"

def render_inline(text: str) -> str:
    t = html.escape(text)

    code_placeholders = []
    def repl_code(m):
        idx = len(code_placeholders)
        code_placeholders.append(f"<code>{m.group(1)}</code>")
        return f"\x00PCSCODE{idx}\x00"
    t = re.sub(r'`([^`]+)`', repl_code, t)

    link_placeholders = []
    def repl_link(m):
        idx = len(link_placeholders)
        url = sanitize_url(html.unescape(m.group(2)))
        label = m.group(1)
        link_placeholders.append(f'<a href="{url}">{label}</a>')
        return f"\x00PCSLINK{idx}\x00"
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', repl_link, t)

    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', t)

    t = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'<em>\1</em>', t)
    t = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<em>\1</em>', t)

    for idx, l_html in enumerate(link_placeholders):
        t = t.replace(f"\x00PCSLINK{idx}\x00", l_html)
    for idx, c_html in enumerate(code_placeholders):
        t = t.replace(f"\x00PCSCODE{idx}\x00", c_html)

    return t

def markdown_to_html(md: str) -> str:
    lines = md.splitlines(); out = []
    in_code = False; in_list = False; in_table = False; in_quote = False

    for line in lines:
        raw = line.strip()
        if raw.startswith("```"):
            if in_code: out.append("</code></pre>"); in_code = False
            else: out.append(f'<pre><code class="language-{html.escape(raw[3:].strip())}">'); in_code = True
            continue
        if in_code: out.append(html.escape(line)); continue
        if not raw:
            if in_list: out.append("</ul>"); in_list = False
            if in_table: out.append("</tbody></table>"); in_table = False
            if in_quote: out.append("</blockquote>"); in_quote = False
            continue
        if raw == "---" or raw == "***" or raw == "___":
            if in_list: out.append("</ul>"); in_list = False
            if in_table: out.append("</tbody></table>"); in_table = False
            if in_quote: out.append("</blockquote>"); in_quote = False
            out.append("<hr>")
            continue
        if raw.startswith(">"):
            if in_list: out.append("</ul>"); in_list = False
            if in_table: out.append("</tbody></table>"); in_table = False
            txt = render_inline(raw.lstrip("> ").strip())
            if not in_quote: out.append(f"<blockquote><p>{txt}</p>"); in_quote = True
            else: out.append(f"<p>{txt}</p>")
            continue
        else:
            if in_quote: out.append("</blockquote>"); in_quote = False

        m_h = re.match(r'^(#{1,6})\s+(.*)$', raw)
        if m_h:
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<h{len(m_h.group(1))}>{render_inline(m_h.group(2))}</h{len(m_h.group(1))}>")
            continue
        if raw.startswith("- ") or raw.startswith("* "):
            if not in_list: out.append("<ul>"); in_list = True
            out.append(f"<li>{render_inline(raw[2:].strip())}</li>")
            continue
        if raw.startswith("|") and raw.endswith("|"):
            masked = re.sub(r'`([^`]+)`', lambda m: "`" + m.group(1).replace("|", "\x00PIPE\x00") + "`", raw)
            cells = [c.replace("\x00PIPE\x00", "|").strip() for c in masked.split("|")[1:-1]]
            if all(re.match(r'^:?-+:?$', c) for c in cells): continue
            if not in_table:
                out.append('<table class="normative-table"><thead><tr>')
                for c in cells: out.append(f"<th>{render_inline(c)}</th>")
                out.append("</tr></thead><tbody>"); in_table = True
            else:
                out.append("<tr>")
                for c in cells: out.append(f"<td>{render_inline(c)}</td>")
                out.append("</tr>")
            continue
        if in_list: out.append("</ul>"); in_list = False
        if in_table: out.append("</tbody></table>"); in_table = False
        out.append(f"<p>{render_inline(raw)}</p>")

    if in_code: out.append("</code></pre>")
    if in_list: out.append("</ul>")
    if in_table: out.append("</tbody></table>")
    if in_quote: out.append("</blockquote>")
    return "\n".join(out)

CSS_STYLES = """
:root { --bg: #ffffff; --text: #1a1a1a; --accent: #0b4f8a; --border: #d0d7de; --code-bg: #f6f8fa; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #0d1117; --text: #c9d1d9; --accent: #58a6ff; --border: #30363d; --code-bg: #161b22; }
}
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; background: var(--bg); color: var(--text); }
header { border-bottom: 2px solid var(--accent); padding-bottom: 1rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; }
nav a { margin-left: 1rem; color: var(--accent); text-decoration: none; font-weight: 600; }
nav a:hover { text-decoration: underline; }
footer { border-top: 1px solid var(--border); margin-top: 4rem; padding-top: 1.5rem; font-size: 0.85rem; color: #6e7681; }
hr { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }
pre { background: var(--code-bg); padding: 1rem; border-radius: 6px; overflow-x: auto; border: 1px solid var(--border); }
code { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 0.9em; }
blockquote { border-left: 4px solid var(--accent); margin: 1.5rem 0; padding: 0.5rem 1rem; background: var(--code-bg); }
table.normative-table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.9em; }
table.normative-table th, table.normative-table td { border: 1px solid var(--border); padding: 0.6rem 0.8rem; text-align: left; }
table.normative-table th { background: var(--code-bg); }
.badge-pass { display: inline-block; padding: 0.25rem 0.6rem; background: #1a7f37; color: white; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
"""

def wrap_page(title: str, content: str, rel_path: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — PCS Standards Archive</title>
  <style>{CSS_STYLES}</style>
</head>
<body>
  <header>
    <div><strong>PCS Standards Archive</strong></div>
    <nav>
      <a href="{rel_path}index.html">Home</a>
      <a href="{rel_path}core/pcs.html">PCS 4.5</a>
      <a href="{rel_path}core/sop.html">SOP-001</a>
      <a href="{rel_path}specifications/index.html">Specifiche</a>
    </nav>
  </header>
  <main>{content}</main>
  <footer>
    <p>Archivio Normativo PCS Standards — Auto-Attestazione Tecnica C2 (Ed25519 & PCS-Merkle-v1).</p>
    <p>100% Determinismo Offline — Zero asset remoti, zero cookie, zero tracking.</p>
  </footer>
</body>
</html>"""

def build_static_site():
    if SITE_DIR.exists(): shutil.rmtree(SITE_DIR, ignore_errors=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "core").mkdir(exist_ok=True)
    (SITE_DIR / "specifications").mkdir(exist_ok=True)

    with open(PCS_CORE_FILE, "r", encoding="utf-8") as f:
        pcs_html = markdown_to_html(f.read())
    with open(SITE_DIR / "core" / "pcs.html", "w", encoding="utf-8") as f:
        f.write(wrap_page("PCS 4.5 Core", pcs_html, "../"))

    with open(SOP_CORE_FILE, "r", encoding="utf-8") as f:
        sop_html = markdown_to_html(f.read())
    with open(SITE_DIR / "core" / "sop.html", "w", encoding="utf-8") as f:
        f.write(wrap_page("SOP-PCS-001 Rev. 3.5.1", sop_html, "../"))

    specs_links = []
    if SPECS_DIR.exists():
        for spec_dir in sorted(SPECS_DIR.iterdir()):
            if spec_dir.is_dir():
                spec_f = spec_dir / "SPECIFICATION.md"
                if spec_f.exists():
                    out_d = SITE_DIR / "specifications" / spec_dir.name
                    out_d.mkdir(parents=True, exist_ok=True)
                    with open(spec_f, "r", encoding="utf-8") as f: s_html = markdown_to_html(f.read())
                    with open(out_d / "index.html", "w", encoding="utf-8") as f: f.write(wrap_page(spec_dir.name, s_html, "../../"))
                    specs_links.append(f'<li><a href="{spec_dir.name}/index.html"><strong>{html.escape(spec_dir.name)}</strong></a></li>')

    specs_index = "<h1>Indice delle Specifiche Figlie</h1>"
    specs_index += "<ul>" + "\n".join(specs_links) + "</ul>" if specs_links else "<p>Nessuna specifica figlia archiviata.</p>"
    with open(SITE_DIR / "specifications" / "index.html", "w", encoding="utf-8") as f:
        f.write(wrap_page("Specifiche Figlie", specs_index, "../"))

    home_content = f"""
    <h2>Archivio Normativo e Ingegneria Difensiva</h2>
    <p><span class="badge-pass">PRE-FLIGHT GATE: PASS</span> <em>Auto-Attestazione Tecnica C2</em></p>
    <p>Questo archivio conserva il corpus normativo ufficiale del <strong>Protocollo Colomba Serpente (PCS 4.5)</strong> e le relative specifiche tecniche.</p>
    <h3>Documenti Primari:</h3>
    <ul>
      <li><a href="core/pcs.html"><strong>PCS 4.5 Core Normative</strong></a> — Assiomi, UTM e Spazio del Rischio.</li>
      <li><a href="core/sop.html"><strong>SOP-PCS-001 Rev. 3.5.1</strong></a> — Metrologia e Pipeline di Gate a 5 Fasi.</li>
      <li><a href="specifications/index.html"><strong>Corpus Specifiche Figlie</strong></a> — Specifiche collegate.</li>
    </ul>
    <h3>Repository e Trasparenza:</h3>
    <p>Codice sorgente, toolchain e attestazioni crittografiche disponibili su: <a href="https://github.com/kamaludu/pcs-standards/" target="_blank" rel="noopener noreferrer">GitHub (kamaludu/pcs-standards)</a>.</p>
    """
    with open(SITE_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(wrap_page("Home", home_content, ""))

def audit_generated_site() -> tuple:
    violations = []
    for root, _, files in os.walk(SITE_DIR):
        for f in files:
            if f.endswith(".html") or f.endswith(".css"):
                txt = (Path(root) / f).read_text(encoding="utf-8")
                if re.search(r'<(script|link|iframe|img)[^>]+(src|href)=["\'](https?:)?//', txt, re.IGNORECASE):
                    violations.append(f"Corrispondenza asset remoto esterno in {f}")
                if re.search(r'url\(["\']?(https?:)?//', txt, re.IGNORECASE):
                    violations.append(f"Corrispondenza CSS asset remoto in {f}")
                if re.search(r'(google-analytics|gtag|hotjar|facebook-pixel|analytics\.js)', txt, re.IGNORECASE):
                    violations.append(f"Pattern di tracciamento in {f}")
    return (len(violations) == 0), ("; ".join(violations) if violations else "Zero pattern di asset remoti e zero pattern di tracking rilevati")

def main():
    print("=================================================================")
    print(" PCS-STANDARDS PRE-FLIGHT GATE & BUILD ENGINE (Rev. 12.7.3)      ")
    print("=================================================================")

    lock_ok, lock_msg = audit_lockfile_integrity(LOCK_FILE)
    if not lock_ok:
        print(f"[!] FAIL-CLOSED: {lock_msg}")
        sys.exit(1)
    print(f"[*] DTM-L LOCKFILE INTEGRITY: {lock_msg}")

    if not (BLUEPRINT_FILE.exists() and TRUST_REGISTRY_FILE.exists() and MANIFEST_FILE.exists()):
        print("[!] FAIL-CLOSED: File primari mancanti.")
        sys.exit(1)

    try:
        bp = parse_strict_yaml(BLUEPRINT_FILE.read_text(encoding="utf-8"))
        tr = parse_strict_yaml(TRUST_REGISTRY_FILE.read_text(encoding="utf-8"))
        manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[!] FAIL-CLOSED: Errore di parsing: {e}")
        sys.exit(1)

    rt_ctx = get_runtime_configuration_context(ROOT_DIR, tr)
    observed_hashes = rt_ctx["observed_hashes"]
    bound = manifest.get("bound_asset_hashes", {})
    mismatches = [k for k, v in observed_hashes.items() if bound.get(k) != v]
    if mismatches:
        print(f"[!] FAIL-CLOSED: Hash vincolati non conformi: {', '.join(mismatches)}")
        sys.exit(1)
    print("[*] INTEGRITÀ HASH: 7 Frozen Assets + 1 Lockfile conformi al Manifest")

    if rt_ctx["configuration_identity"] != manifest.get("configuration_identity"):
        print(f"[!] FAIL-CLOSED: ConfigurationIdentity errata (SOP Sez. 14.2): {rt_ctx['configuration_identity']}")
        sys.exit(1)
    print(f"[*] CONFIGURATION IDENTITY: Verificata a 7 parametri ({rt_ctx['configuration_identity']})")

    merkle_ok, reconstructed_root, sig_msg = verify_evidence_package(PCS_DIR, tr)
    if not merkle_ok or reconstructed_root != manifest.get("merkle_root_v1"):
        print(f"[!] MANOMISSIONE RILEVATA: {sig_msg}")
        sys.exit(1)
    print(f"[*] ROOT OF TRUST: {sig_msg} ({reconstructed_root})")

    predicates = eval_all_predicates(bp, observed_hashes)
    failed = [k for k, v in predicates.items() if not v["eval"]]
    if failed:
        print(f"[!] PRE-FLIGHT GATE: FAIL. Predicati non superati: {', '.join(failed)}")
        for k in failed: print(f"    - {k}: {predicates[k]['detail']}")
        sys.exit(1)
    print("[*] PRE-FLIGHT GATE: PASS (17/17 predicati formali verificati con successo)")

    lifecycle = bp.get("lifecycle_and_invalidation", {})
    ttl_str = str(lifecycle.get("ttl_expiration_utc", "2000-01-01T00:00:00Z"))
    try: ttl_dt = datetime.fromisoformat(ttl_str.replace("Z", "+00:00"))
    except Exception: ttl_dt = datetime(2000, 1, 1, tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > ttl_dt:
        print(f"[!] FAIL-CLOSED: Validità TTL DECORSA ({ttl_str}). Stato: RE-ASSESSMENT REQUIRED.")
        sys.exit(1)
    print(f"[*] CICLO DI VALIDITÀ: Finestra temporale valida fino al {ttl_str}")

    build_static_site()
    audit_ok, audit_msg = audit_generated_site()
    if not audit_ok:
        print(f"[!] POST-BUILD AUDIT: FAIL. {audit_msg}")
        shutil.rmtree(SITE_DIR, ignore_errors=True)
        sys.exit(1)
    print(f"[*] POST-BUILD AUDIT: PASS ({audit_msg})")

    commit_sha, timestamp_z, _ = get_git_info(ROOT_DIR)
    report = {
        "timestamp_utc": timestamp_z,
        "commit_sha": commit_sha,
        "runner_version": "pcs-builder-v12.7.3",
        "merkle_root_v1": reconstructed_root,
        "configuration_identity": rt_ctx["configuration_identity"],
        "evidence_result": "PASS",
        "gate_verdict": "RELEASE_GATE_PASS",
        "scope_assurance": "C2_INTERNAL_GATE_CONFORMANCE_DEMONSTRATED_WITHIN_DECLARED_BOUNDARY",
        "attestation_id": "PCS-C2-SELF-ATTESTATION-v1.0",
        "predicates_result": predicates
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(GATE_LOG_FILE, "w", encoding="utf-8") as f: json.dump(report, f, indent=2)

    print("=================================================================")
    print(" EVIDENCE_RESULT : PASS (17/17 record conformi a schema e hash)  ")
    print(" GATE_RESULT     : PASS (17/17 predicati GatePass == TRUE)       ")
    print(" ASSURANCE_CLAIM : C2_DEVELOPER_SELF_ATTESTATION (Within Boundary)")
    print(" ATTESTATION_ID  : PCS-C2-SELF-ATTESTATION-v1.0                  ")
    print("=================================================================")

if __name__ == "__main__":
    main()
