# STANDARD OPERATING PROCEDURE (SOP-PCS-001 Rev. 3.5.1)
### Procedura Operativa Standardizzata per l'Attuazione, la Verifica Empirica e l'Audit del Protocollo Colomba Serpente (PCS 4.5)

```text
+------------------------------------------------------------------------------+
|                         DOCUMENT CONTROL BLOCK                               |
+------------------------------------------------------------------------------+
| Document ID         : SOP-PCS-001                                            |
| Revision            : Rev. 3.5.1 (Definitive Sealed Production Standard)     |
| Normative Reference : PROTOCOLLO COLOMBA SERPENTE (PCS 4.5 Core)             |
| Status              : APPROVED / SEALED / IMMUTABLE                          |
| Classification      : Standard Tecnico di Ingegneria Difensiva e Audit       |
| Effective Date      : 2026-08-27                                             |
| Supersedes          : SOP-PCS-001 Rev. 3.5, Rev. 3.4.2, Rev. 3.4 e prec.     |
+------------------------------------------------------------------------------+
```

```text
+------------------------------------------------------------------------------+
|               INDICE DELLE SPECIFICHE PROCEDURALI (SOP-PCS-001 Rev. 3.5.1)   |
+------------------------------------------------------------------------------+
|  1. Scopo, Ambito, Tassonomia dei Requisiti e Matrice di Tracciabilita (RTM) |
|  2. Procedura 01: Classificazione del Rischio (R, S, IR) e Calcolo di K      |
|  3. Procedura 02: Determinazione del Livello Minimo di Controllo (C_min)     |
|  4. Procedura 03: Universal Threat Model (6 Threat Classes * 5 Assur. Stages)|
|  5. Procedura 04: Definizione degli Explicit Non-Purposes e Clausola Legale  |
|  6. Procedura 05: Gestione della Supply-Chain e Deserializzazione (DTM-L/R)  |
|  7. Procedura 06: Data Governance, Privacy, Tassonomia Secret, GDPR Art. 9/10|
|  8. Procedura 07: Verifica Gabbia FSM, Isolamento LLM e Process Privileges   |
|  9. Procedura 08: Validazione degli Output Contracts e Gestione del Drift    |
| 10. Procedura 09: Falsification Testing e Domain Failure Coverage           |
| 11. Procedura 10: Collaudo Kill-Switch, Quiescenza DAG e Statistica Trial    |
| 12. Procedura 11: Protocollo di Audit e Technical Verification Attestation   |
| 13. Procedura 12: Pre-Flight Gate con Pipeline a 5 Fasi e Deny Precedence    |
| 14. Procedura 13: Gestione Modifiche, Configuration Identity e TTL           |
| 15. Procedura 14: Incident Response, Logical Context Purge e Post-Mortem T0  |
| 16. Appendice: State Registry, Schema RFC 8785, Merkle v1 e Trust Registry   |
+------------------------------------------------------------------------------+
```

---

## 1. SCOPO, AMBITO, TASSONOMIA DEI REQUISITI E MATRICE DI TRACCIABILITA (RTM)

### 1.1 Finalita Operativa
La presente Procedura Operativa Standardizzata (**SOP-PCS-001 Rev. 3.5.1**) formalizza i metodi di collaudo deterministico, le metriche quantitative di misura empirica, i protocolli crittografici di prova e la pipeline di gating a 5 fasi necessari per attestare la conformita deterministica di un artefatto software ai vincoli del **Protocollo Colomba Serpente (PCS 4.5)**.

### 1.2 Principio di Non-Invenzione Normativa e Tassonomia delle Clausole
La presente SOP opera come specifica procedurale subordinata al PCS 4.5 Core:
* **`[PCS-REQ]` -- Requisito Normativo Cogente:** Obbligo primario derivato direttamente dal testo normativo di PCS 4.5.
* **`[SOP-METRIC]` -- Metrica Operativa di Collaudo (Safety Envelope):** Soglia quantitativa, tolleranza temporale o procedura di misura stabilita dalla SOP per verificare empiricamente un requisito `[PCS-REQ]`.
  * *Direzione della Restrittivita:*
    * `LOWER_IS_STRICTER`: Valori inferiori impongono vincoli piu restrittivi (es. timeout massimi, soglie errori del Circuit Breaker, timeout canary). Valori operativi in Sez. 6.3 e 11.2.
    * `HIGHER_IS_STRICTER`: Valori superiori impongono vincoli piu restrittivi (es. tempi minimi di quarantena, percentuali di copertura UTM, trial statistici). Valori operativi in Sez. 4.2, 6.3 e 11.2.
* **`[SOP-IMPL]` -- Specifica di Implementazione ed Esecuzione:** Standard tecnico, formato di serializzazione o convenzione formale adottata per garantire l'eseguibilita agnostica, la ripetibilita e l'auditabilita del processo.

### 1.3 Requirement Traceability Matrix (RTM Granulare a Livello Requisito)

```text
+--------------+------------------+------------------+-----------------------+-----------+--------------------+-------------------+-----------------+
| REQUISITO ID | CLAUSOLA PCS     | CLAUSOLA SOP     | CONTROLLO / ARCHITETT.| CARDIN.   | TEST ID            | EVIDENZA ATTESA   | PREDICATO GATE  |
+--------------+------------------+------------------+-----------------------+-----------+--------------------+-------------------+-----------------+
| PCS-REQ-01   | PCS 4.5 Sez. 2.1 | SOP Sez. 2.1     | Domain & Scope Gating | 1:1       | TS-SC-01           | Scheda Ambito     | P_SCOPE_OK      |
| PCS-REQ-02   | PCS 4.5 Sez. 2.2 | SOP Sez. 2.2     | Worst-Case Harm (S)   | 1:1       | TS-SC-02           | Scoring Rubric S  | P_K_CALC        |
| PCS-REQ-03   | PCS 4.5 Sez. 2.3 | SOP Sez. 2.3     | Recovery Cost (IR, K) | 1:1       | TS-SC-03           | Scoring Rubric IR | P_K_CALC        |
| PCS-REQ-04   | PCS 4.5 Sez. 2.4 | SOP Sez. 3.1     | Poset Controlli (C)   | 1:1       | TS-CT-01           | Tabella Controlli | P_CTRL_MATCH    |
| PCS-REQ-05   | PCS 4.5 Sez. 3.1 | SOP Sez. 3.2     | Risoluzione C_min     | 1:1       | TS-CT-02           | Risoluzione Matr. | P_NO_BLOCK      |
| PCS-REQ-06   | PCS 4.5 Sez. 1   | SOP Sez. 4.1-4.2 | UTM 6 Threat Classes  | 1:N (6)   | TS-UT-01..06       | Matrice UTM (A5)  | P_THREAT_MOD    |
| PCS-REQ-06b  | PCS 4.5 Sez. 1,11| SOP Sez. 4.2, 10 | T0 Adversarial Test   | 1:1       | TS-T0-01           | Test Avversariali | P_T0_TEST       |
| PCS-REQ-07   | PCS 4.5 Sez. 6   | SOP Sez. 5.1-5.2 | Clausola PCS-L4.5     | 1:1       | TS-LG-01           | Testo Licenza/Doc | P_LEGAL_DOC     |
| PCS-REQ-08   | PCS 4.5 Sez. 4.1 | SOP Sez. 6.1-6.2 | DTM-L Lock & Formati  | 1:1       | TS-LC-01           | Lockfile + Digest | P_DTM_LOCAL     |
| PCS-REQ-09   | PCS 4.5 Sez. 4.2 | SOP Sez. 6.3     | DTM-R Circuit Breaker | 1:N (7)   | CB-01..05,GEN,IDEMP| Log Breaker & CAS | P_DTM_REMOTE    |
| PCS-REQ-10   | PCS 4.5 Sez. 5   | SOP Sez. 7.1-7.2 | Data Gov & Privacy    | 1:1       | TS-DG-01           | Scansione Git/Net | P_DATA_GOV      |
| PCS-REQ-11   | PCS 4.5 Sez. 5   | SOP Sez. 7.1     | Repository Metadata   | 1:1       | TS-MD-01           | Git Full History  | P_METADATA      |
| PCS-REQ-12   | PCS 4.5 Sez. 7   | SOP Sez. 8.1-8.2 | Closed-World FSM      | 1:1       | TF-01              | Test Allowlist    | P_ALLOWLIST     |
| PCS-REQ-13   | PCS 4.5 Sez. 0A6 | SOP Sez. 8.2     | Isolamento LLM No-Tool| 1:1       | TS-LL-01           | Ispezione Codice  | P_LLM_ISOL      |
| PCS-REQ-14   | PCS 4.5 Sez. 7.1 | SOP Sez. 9.1-9.2 | Output Contracts      | 1:1       | TF-02              | Schema Validation | P_CONTRACT      |
| PCS-REQ-15   | PCS 4.5 Sez. 7.2 | SOP Sez. 15.1    | Dual Fail & Purge     | 1:1       | TF-04              | Log Context Purge | P_DUAL_FAIL     |
| PCS-REQ-16   | PCS 4.5 Sez. 2.4 | SOP Sez. 12.1    | Independent Audit C4  | 1:1       | TS-AU-01           | TVR Firmato (PKI) | P_C4_AUDIT      |
| PCS-REQ-17   | PCS 4.5 Sez. 10.1| SOP Sez. 11.1-3  | Kill-Switch Quiescence| 1:1       | TF-03              | Log Quiescenza DAG| P_ABORT_OFF     |
+--------------+------------------+------------------+-----------------------+-----------+--------------------+-------------------+-----------------+
```

Regole di Tracciabilita della RTM:
1. FOR ALL req IN PCS_REQ ==> (>= 1 Controllo Architetturale) AND (>= 1 Test_ID) AND (>= 1 Predicato Gate).
2. FOR ALL p IN P_required ==> (>= 1 Evidence Record formalmente verificabile).

### 1.4 Precondizione di Validita Normativa e Binding Crittografico `[SOP-IMPL]`
Il Blueprint di progetto deve registrare obbligatoriamente i seguenti metadati normativi immutabili:
* `pcs_version`: `"4.5"`
* `pcs_document_hash`: Impronta SHA-256 del testo normativo PCS 4.5 (`sha256:[a-f0-9]{64}`).
* `sop_version`: `"3.5.1"`
* `sop_document_hash`: Impronta SHA-256 del presente testo procedurale (`sha256:[a-f0-9]{64}`).

---

## 2. PROCEDURA 01: CLASSIFICAZIONE DEL RISCHIO (R, S, IR) E CALCOLO DI K
*(Attuazione PCS 4.5 -- Sezioni 2.1, 2.2, 2.3)*

### 2.1 Dominio Tassonomico e Ambito Ammissibile (R) `[PCS-REQ Sez. 2.1]`
1. **Dominio Tassonomico Formale:**
   `R_domain = {R0: Negligible, R1: Informational, R2: Functional, R3: Assistive, R4: Critical}`
2. **Ambito Ammissibile al Rilascio PCS:**
   `R_admissible = {R0, R1, R2, R3}`
3. **Fase 0 di Validazione Schema / Input Parsing:**  
   Se R dichiarato e omesso, nullo o `R NOT IN R_domain`, il Gate abortisce immediatamente con esito **`PARSE_ERROR`**.
4. **Regola di Esclusione R4 `[PCS-REQ Sez. 0 Assioma 8, Sez. 2.1]`:**  
   R4 delimita i sistemi critici **fuori perimetro**. Se il progetto ricade in R4 (dispositivi medici, infrastrutture critiche, automazione con impatto fisico, decisioni legali cogenti), il collaudo si arresta con esito `OUT OF SCOPE / BLOCKED`. Nessun livello C puo autorizzare un rilascio in classe R4.

### 2.2 Scoring della Severita (S) e dell'Irreversibilita (IR) `[PCS-REQ Sez. 2.2, Sez. 2.3]`
Registrare nel Blueprint con provenienza `HUMAN`:
* `S IN S_domain = {S0, S1, S2, S3}`: Magnitudo del danno potenziale nello scenario peggiore.
* `IR IN IR_domain = {IR0, IR1, IR2, IR3}`: Onere di ripristino dell'integrita precedente.
* *Controllo Input:* `(S NOT IN S_domain) OR (IR NOT IN IR_domain)` innesca istantaneamente `PARSE_ERROR`.

### 2.3 Calcolo dell'Indice Deterministico di Gating (K) `[PCS-REQ Sez. 2.3]`
1. **Calcolo di K:**
   `K = max(S, IR)   con K IN {0, 1, 2, 3}`
   *Definizione Epistemica `[SOP-METRIC]`:* K e una **funzione deterministica di gating conservativa** e non una stima probabilistica.
2. **Regola di Contraddizione e Vincolo di Immutabilita `[PCS-REQ Sez. 2.1, Sez. 2.4]`:**
   Se un progetto censito come R0, R1, R2 manifesta uno scenario di guasto con `K == 3`, il Pre-Flight Gate assume lo stato `CONTRADDIZIONE / BLOCKED`.
   * **Divieto di Riqualificazione Fittizia:** E vietato forzare lo sblocco incrementando nominalmente C_impl o riclassificando burocraticamente l'ambito in R3. R puo essere modificato unicamente a fronte di una documentata variazione della destinazione d'uso effettiva.

---

## 3. PROCEDURA 02: DETERMINAZIONE DEL LIVELLO MINIMO DI CONTROLLO (C_min)
*(Attuazione PCS 4.5 -- Sezione 3)*

### 3.1 Ordinamento Formale dei Livelli di Controllo (C_set) `[SOP-IMPL]`
L'insieme dei controlli e una struttura totalmente ordinata (poset a catena stretta):
`C_set = ({C0, C1, C2, C3, C4}, <=)   con C0 < C1 < C2 < C3 < C4`
Definita la funzione rango `ord(C_i) = i`, la condizione di superamento e:
`C_impl >= C_min <==> ord(C_impl) >= ord(C_min)`

### 3.2 Matrice Tabellare dei Controlli C_min(R, K) `[PCS-REQ Sez. 3.1]`

```text
+-----------+---------------+-------------------+---------------------------+
|           |     K <= 1    |       K = 2       |           K = 3           |
|           | (S<=1 AND IR<=1)| (max(S, IR) = 2)|     (S=3 OR IR=3)         |
+-----------+---------------+-------------------+---------------------------+
| R0 (Negl) |      C0       |        C1         |  CONTRADDIZIONE / BLOCKED |
| R1 (Info) |      C1       |        C2         |  BLOCKED                  |
| R2 (Func) |      C2       |        C3         |  BLOCKED                  |
| R3 (Asst) |      C3       |        C3         |  C4 (Audit Indipendente)  |
| R4 (Crit) |    FUORI      |      FUORI        |  FUORI PERIMETRO (BLOCKED)|
|           |  PERIMETRO    |    PERIMETRO      |                           |
+-----------+---------------+-------------------+---------------------------+
```

### 3.3 Derivazione Vincolante di C4 e Audit Indipendente `[SOP-IMPL]`
```text
C4_MIN_REQUIRED <==> (R == R3 AND K == 3) <==> (C_min == C4)
AUDIT_REQUIRED  <==> (C_min == C4) OR (C_impl == C4)
AUDIT_SATISFIED <==> (TVR_Signed == TRUE) AND 
                     (RegistryIntegrityValid == TRUE) AND 
                     (AuditorInTrustRegistry == TRUE) AND 
                     (IndependenceConfirmed == TRUE)
```

---

## 4. PROCEDURA 03: UNIVERSAL THREAT MODEL (6 THREAT CLASSES * 5 ASSURANCE STAGES)
*(Attuazione PCS 4.5 -- Sezione 1)*

### 4.1 Definizione dei 5 Stadi di Assurance (A1 ... A5) `[SOP-IMPL]`
`A1 (IDENTIFIED) -> A2 (MITIG_DEF) -> A3 (CTRL_IMPL) -> A4 (CTRL_TEST) -> A5 (CTRL_PASS)`

### 4.2 Matrice Canonica dei Test Vettoriali e Copertura `[PCS-REQ Sez. 1]` `[SOP-METRIC]`

```text
+---------+----------------------------+---------------------------------------+---------------------------------------------+
| CLASSE  | DENOMINAZIONE MINACCIA     | VETTORE AVVERSARIALE MINIMO           | CRITERIO DI ACCETTAZIONE (PASS ASSERT)      |
+---------+----------------------------+---------------------------------------+---------------------------------------------+
| UTM-T0  | Protocol/Logical Failure   | Iniezione input sintatticamente validi| Transizione corretta a fallback; assenza di |
|         | e Compliance Illusion      | ma semanticamente ambigui o avversari | esecuzioni implicite fuori allowlist.       |
+---------+----------------------------+---------------------------------------+---------------------------------------------+
| UTM-T1  | Legal Asymmetric / SLAPP   | Audit clausole contrattuali e licenza | Testo PCS-L4.5 e Licenza open source        |
|         | e Proprieta Intellettuale  | su repository e distribution root     | presenti, visibili e integri nella root.    |
+---------+----------------------------+---------------------------------------+---------------------------------------------+
| UTM-T2  | Regulatory & Compliance    | Scansione flussi payload verso DTM-R  | 0 dati Art. 9/10 inoltrati al cloud;        |
|         | (GDPR, AI Act)             | e verifica policy di minimizzazione   | pseudonimizzazione/minimizzazione applicata.|
+---------+----------------------------+---------------------------------------+---------------------------------------------+
| UTM-T3  | Correlation & Personal     | Scansione automatica cronologia Git,  | 0 percorsi host assoluti, 0 secret attivi,  |
|         | Maintainer De-anonimiz.    | metadati commit e intestazioni di rete| relay email configurato per tutti i commit. |
+---------+----------------------------+---------------------------------------+---------------------------------------------+
| UTM-T4  | Malfunctioning & Errors    | Iniezione fault: timeout >=30s, HTTP  | Circuit breaker commuta a OPEN; forzatura   |
|         | su Soggetti Fragili        | 500, payload JSON schema-corrotto     | a SAFE-DEGRADED senza hanging o unhandled.  |
+---------+----------------------------+---------------------------------------+---------------------------------------------+
| UTM-T5  | Social & Reputational      | Ispezione relazioni tecniche, issue   | Tono notarile-metrologico rispettato;       |
|         | Exposure / Media Backlash  | pubbliche e manifest di benchmark     | assenza di giudizi soggettivi o illazioni.  |
+---------+----------------------------+---------------------------------------+---------------------------------------------+
```

*Metrica di Copertura (ThreatCoverage) `[SOP-METRIC]`:*
`ThreatCoverage == (100% classi UTM) AND (100% requisiti di controllo) AND (100% vettori negativi)`

*Regola Deterministica di Derivazione A5 (`CTRL_PASS`) `[SOP-METRIC]`:*
```text
CTRL_PASS(T_i) <==>
  (IDENTIFIED(T_i) == TRUE) AND 
  (MITIG_DEF(T_i) == TRUE) AND 
  (CTRL_IMPL(T_i) == TRUE) AND
  (CTRL_TEST(T_i) == TRUE) AND 
  (ObservedResult(T_i) satisfies AcceptanceCriteria(T_i)) AND
  (EvidenceIntegrityValid(EVIDENCE_ID(T_i)) == TRUE)
```

---

## 5. PROCEDURA 04: DEFINIZIONE DEGLI EXPLICIT NON-PURPOSES E CLAUSOLA LEGALE
*(Attuazione PCS 4.5 -- Sezione 6)*

### 5.1 Redazione dei Non-Scopi Espliciti `[PCS-REQ Sez. 6]`
Nei progetti di classe R3, la redazione degli Explicit Non-Purposes impone l'inclusione formale e non modificata delle delimitazioni di ambito stabilite dalla Sezione 2 della Clausola Modello PCS-L4.5 (esclusione categorica di consulenza medica, diagnosi, prescrizioni, gestione emergenze, pericolo di vita e sicurezza fisica).

### 5.2 Verifica della Clausola PCS-L4.5 `[PCS-REQ Sez. 6]`
Verificare la presenza integrale, visibile e non alterata del testo formale `PCS-L4.5` (come definito in PCS 4.5 Sez. 6) all'interno dei file di radice della release (`LICENSE`, `README.md`, `NOTICE`).

---

## 6. PROCEDURA 05: GESTIONE DELLA SUPPLY-CHAIN E DESERIALIZZAZIONE (DTM-L E DTM-R)
*(Attuazione PCS 4.5 -- Sezione 4)*

### 6.1 DTM-L: Dipendenze Software Locali `[PCS-REQ Sez. 4.1]`
1. Lockfile crittografico autorevole (`Cargo.lock`, `package-lock.json`, `poetry.lock`, `go.sum`, hash-pinned `requirements.txt`).
2. Verifica checksum SHA-256/512 contro il manifest approvato.
3. Disattivazione forzata script post-install (`--ignore-scripts`, `--no-plugins`).

### 6.2 DTM-L: Deserializzazione Sicura degli Artefatti AI `[PCS-REQ Sez. 4.1]` `[SOP-IMPL]`
1. **Formati Primari Obbligatori:** Uso esclusivo di formati privi di capacita di esecuzione codice (`safetensors`, `gguf`) con hash SHA-256 pinnato.
2. **Presidi per Checkpoint Legacy (PyTorch `torch.load`):**
   * *Asserzione Negativa:* Il flag `weights_only=True` NON costituisce da solo prova sufficiente di sicurezza.
   * Attivazione congiunta di `weights_only=True`, runtime supportato, allowlist tipi primitivi via `torch.serialization.add_safe_globals` e verifica preventiva SHA-256 del file.

### 6.3 DTM-R: Circuit Breaker FSM con Isolamento Generazionale Rigido e Persistenza Fail-Closed `[PCS-REQ Sez. 4.2]` `[SOP-METRIC]`

#### 6.3.1 Definizione della Macro REMOTE_TRANSPORT_FAILURE `[SOP-METRIC]`
```text
REMOTE_TRANSPORT_FAILURE <==>
  (HTTP_STATUS IN {408, 429, 500, 502, 503, 504}) OR
  (EXCEPTION IN {DNS_RESOLUTION_FAILED, TCP_CONN_REFUSED, TCP_RESET,
                 TLS_HANDSHAKE_TIMEOUT, CONNECT_TIMEOUT, READ_TIMEOUT,
                 MALFORMED_HTTP_PAYLOAD})
```

#### 6.3.2 Modello a Due Fasi: Admission Gate ed Execution Completion con Isolation Check Immediato e Idempotenza Lineare [SOP-IMPL]

```text
Struttura dello Stato Interno FSM:
  - CurrentState                  IN {CLOSED, OPEN, HALF_OPEN, FAIL_CLOSED_HALTED}
  - CurrentFsmGeneration          IN [1, +Infinity) (Intero monotonico)
  - canary_lease_generation       IN [0, +Infinity) (Intero, associato al lease attivo)
  - quarantine_backoff_level      IN [1, 5] (Intero 'k', default = 1)
  - consecutive_failure_count     IN [0, N_threshold]
  - total_transport_failure_count IN [0, +Infinity)
  - active_admission_tokens       Set di stringhe (UUIDv4 request_id attivi non completati)
  - in_flight_remote_requests     IN [0, +Infinity) (Invariante: in_flight_remote_requests == len(active_admission_tokens))
  - canary_lease_active           IN {TRUE, FALSE}
  - canary_lease_expiry           Timestamp monotonico
  - quarantine_timer              Timer di scadenza monotonico

Invarianti di Coerenza Strutturale:
  canary_lease_active == TRUE ==> canary_lease_generation == CurrentFsmGeneration
  len(active_admission_tokens) == in_flight_remote_requests

Struttura AdmissionToken:
  - request_id                    Stringa UUIDv4
  - generation_id                 Intero (ereditato da CurrentFsmGeneration al rilascio)
  - is_canary                     Booleano {TRUE, FALSE}
  - admission_timestamp           Timestamp monotonico


FASE 1: RICHIESTA DI AMMISSIONE LINEARIZZABILE (REMOTE_ADMISSION_GATE)
REMOTE_ADMISSION(request):
  ACQUIRE_MUTEX()
  try:
    if CurrentState == FAIL_CLOSED_HALTED:
      return REJECT_INTERNAL_CORRUPTION

    # 1. Transizione automatica OPEN -> HALF_OPEN su scadenza timer
    if CurrentState == OPEN:
      if MonotonicClock() >= quarantine_timer:
        CurrentState := HALF_OPEN
        CurrentFsmGeneration := CurrentFsmGeneration + 1
      else:
        return REJECT_SAFE_DEGRADED

    # 2. Gestione Stato HALF_OPEN (Singola Sonda Canary con Lease Timeout)
    if CurrentState == HALF_OPEN:
      if canary_lease_active == TRUE:
        if MonotonicClock() < canary_lease_expiry:
          return REJECT_SAFE_DEGRADED
        else:
          # Canary scaduto per timeout: retrocessione e incremento generazione
          CurrentState := OPEN
          CurrentFsmGeneration := CurrentFsmGeneration + 1
          quarantine_backoff_level := min(quarantine_backoff_level + 1, 5)
          quarantine_timer := MonotonicClock() + T_cooldown(quarantine_backoff_level)
          canary_lease_active := FALSE
          canary_lease_generation := 0
          return REJECT_SAFE_DEGRADED
      
      canary_lease_active := TRUE
      canary_lease_generation := CurrentFsmGeneration
      canary_lease_expiry := MonotonicClock() + 30000 ms  # Hard timeout 30s
      token := AllocateLeaseToken(request.id, generation_id=CurrentFsmGeneration, is_canary=TRUE)
      active_admission_tokens.insert(token.request_id)
      in_flight_remote_requests := in_flight_remote_requests + 1
      return ADMITTED(token)

    # 3. Gestione Stato CLOSED
    token := AllocateLeaseToken(request.id, generation_id=CurrentFsmGeneration, is_canary=FALSE)
    active_admission_tokens.insert(token.request_id)
    in_flight_remote_requests := in_flight_remote_requests + 1
    return ADMITTED(token)
  finally:
    RELEASE_MUTEX()


FASE 2: COMPLETAMENTO ED AGGIORNAMENTO STATO (COMPLETE_REMOTE_EXECUTION)
COMPLETE_EXECUTION(token, response_event):
  ACQUIRE_MUTEX()
  try:
    # 0.1 CONTROLLO DI COERENZA DELL'INVARIANTE CONTABILE (Freeze preventivo pre-mutazione)
    if in_flight_remote_requests != len(active_admission_tokens):
      CurrentState := FAIL_CLOSED_HALTED
      PERSIST_FAIL_CLOSED_STATE_ATOMIC("INVARIANT_VIOLATION: accounting_mismatch")
      TRIGGER_FATAL_TRAP("FATAL: admission_accounting_mismatch")
      return STATE_CORRUPTION_FAIL_CLOSED

    # 0.2 GUARDIA DI IDEMPOTENZA / ANTI-DUPLICATE TOKEN (Pre-mutazione)
    if token.request_id NOT IN active_admission_tokens:
      return DUPLICATE_OR_STALE_TOKEN_COMPLETION_REJECTED

    # 0.3 TRANSIZIONE ATOMICA DI RILASCIO RISORSA
    active_admission_tokens.remove(token.request_id)
    in_flight_remote_requests := in_flight_remote_requests - 1

    # 1. BLOCCO DI ISOLAMENTO GENERAZIONALE RIGIDO (Eseguito PRIMA di mutare il canary state)
    if token.generation_id != CurrentFsmGeneration:
      return STALE_GENERATION_COMPLETION_DROPPED

    # 2. Aggiornamento Lease Canary (solo per token della generazione corrente)
    if token.is_canary == TRUE:
      if canary_lease_generation == token.generation_id:
        canary_lease_active := FALSE
        canary_lease_generation := 0

    # 3. Elaborazione Esito e Transizioni FSM
    if RemoteFailure(response_event):
      total_transport_failure_count := total_transport_failure_count + 1

      if CurrentState == CLOSED:
        consecutive_failure_count := consecutive_failure_count + 1
        if consecutive_failure_count >= N_threshold:
          CurrentState := OPEN
          CurrentFsmGeneration := CurrentFsmGeneration + 1
          quarantine_backoff_level := 1
          quarantine_timer := MonotonicClock() + T_cooldown(quarantine_backoff_level)

      elif CurrentState == HALF_OPEN:
        CurrentState := OPEN
        CurrentFsmGeneration := CurrentFsmGeneration + 1
        quarantine_backoff_level := min(quarantine_backoff_level + 1, 5)
        quarantine_timer := MonotonicClock() + T_cooldown(quarantine_backoff_level)

    else:
      # Successo chiamata remota
      if CurrentState == CLOSED:
        consecutive_failure_count := 0

      elif CurrentState == HALF_OPEN:
        if (response_event.status_code IN SUCCESS_STATUS_SET) AND ValidateContract(response_event.payload):
          CurrentState := CLOSED
          CurrentFsmGeneration := CurrentFsmGeneration + 1
          consecutive_failure_count := 0
          quarantine_backoff_level := 1
        else:
          CurrentState := OPEN
          CurrentFsmGeneration := CurrentFsmGeneration + 1
          quarantine_backoff_level := min(quarantine_backoff_level + 1, 5)
          quarantine_timer := MonotonicClock() + T_cooldown(quarantine_backoff_level)
  finally:
    RELEASE_MUTEX()

Invarianti di Non-Bypass, Fail-Closed ed Epoch Isolation:
1. Invariante di Chiusura e Linearizzazione:
   CurrentState == OPEN ==> (FOR ALL req: LinearizationPoint(req) > LinearizationPoint(OPEN_TRANSITION) ==> req.admission == REJECT_SAFE_DEGRADED)
2. Invariante di Isolamento Epoch (Anti-Stale Poisoning):
   token.generation_id != CurrentFsmGeneration ==> (StateCountersMutation(token) == FORBIDDEN) AND (CanaryLeaseMutation(token) == FORBIDDEN)
3. Invariante di Consistenza In-Flight e Persistenza:
   in_flight_remote_requests < 0 ==> (PERSIST_FAIL_CLOSED_STATE_ATOMIC() == TRUE) AND (CurrentState == FAIL_CLOSED_HALTED)
4. Invariante di Idempotenza e Linearizzazione del Token (Anti-Double-Spend):
   FOR ALL token : ExactLinearCompletion(token) <= 1
   token.request_id NOT IN active_admission_tokens ==> (Mutation(token) == FORBIDDEN) AND (in_flight_remote_requests_mutation == FORBIDDEN)
```

---

#### 6.3.3 Soglie Operative e Tempi di Quarantena `[SOP-METRIC]` (`LOWER_IS_STRICTER`)
* `N_threshold_default = 5` (Safety Envelope: `1 <= N_threshold <= 5`).
* `SUCCESS_STATUS_SET = {200, 204}`.
* `T_cooldown(k) = min(60 s * (2^(k - 1)), 600 s) con k IN {1, 2, 3, 4, 5}`.

---

#### 6.3.4 Requisiti di Accettazione Formali dei Test CB-05, CB-05-GEN e CB-IDEMPOTENCY [SOP-METRIC]
1. Test Concorrenza CB-05: M=50 failure concorrenti contro FSM in stato CLOSED.
   - Esattamente una transizione lineare da CLOSED a OPEN;
   - consecutive_failure_count == N_threshold al momento del passaggio a OPEN;
   - Nessuna richiesta post-OPEN ottiene ADMITTED;
   - Assenza totale di data race o underflow.
2. Test Isolamento Generazionale CB-05-GEN:
   - Inizializzazione FSM in stato HALF_OPEN a generazione G;
   - Ammissione canary token A con generation_id = G (canary_lease_active = TRUE);
   - Forzatura timeout lease: transizione HALF_OPEN(G) -> OPEN(G+1);
   - Decorso del quarantine timer: transizione OPEN(G+1) -> HALF_OPEN(G+2);
   - Ammissione nuovo canary token B con generation_id = G+2 (canary_lease_active = TRUE);
   - Iniezione completion tardiva del token A (generation_id = G);
   - Criterio di Accettazione (CB-05-GEN PASS):
     1. in_flight_remote_requests decrementato esattamente di 1;
     2. completion di token A classificata come STALE_GENERATION_COMPLETION_DROPPED;
     3. canary_lease_active di generazione G+2 rimane invariato a TRUE;
     4. canary_lease_generation di generazione G+2 rimane invariato a G+2;
     5. Nessun contatore di errore o timer della generazione G+2 viene alterato.
3. Requisito di Idempotenza e Protezione Duplicate Completion (CB-IDEMPOTENCY):
   - Scenario A (Sequenziale): Iniezione di N completion duplicate sequenziali per un medesimo request_id gia completato;
   - Scenario B (Concorrente): Esecuzione simultanea su M thread concorrenti di COMPLETE_EXECUTION con il medesimo request_id valido;
   - Criterio di Accettazione (CB-IDEMPOTENCY PASS):
     1. Esattamente 1 thread/chiamata ottiene la contabilizzazione del completamento;
     2. Il token viene rimosso esattamente 1 volta da active_admission_tokens;
     3. in_flight_remote_requests subisce esattamente 1 solo decremento unitario;
     4. Tutte le rimanenti chiamate concorrenti/duplicate (M - 1) restituiscono DUPLICATE_OR_STALE_TOKEN_COMPLETION_REJECTED;
     5. Nessun disallineamento contabile, race condition o trap di underflow rilevata.

---

## 7. PROCEDURA 06: DATA GOVERNANCE, PRIVACY, TASSONOMIA DEI SECRET E GDPR ART. 9/10
*(Attuazione PCS 4.5 -- Sezione 5)*

### 7.1 Bonifica Repository, Igiene Percorsi Host e Tassonomia Secret `[PCS-REQ Sez. 5]` `[SOP-METRIC]`
1. **Scansione Percorsi Host e Dati Personali Versionati (`P_METADATA`):** Eseguita su `git log --all --full-history` per attestare zero percorsi assoluti host (`/home/...`, `C:\...`) e zero metadati anagrafici diretti (relay email obbligatorio).
2. **Tassonomia Secret (`P_DATA_GOV`):**
   * Active Secret Exposed -> FAIL (Revoca e rotazione immediata);
   * Historical Secret Valido -> FAIL (Revoca + riscrittura cronologia);
   * Historical Secret Revocato -> WARNING (Risolto a TRUE solo se presente record formale EV-XXXX comprovante la revoca/rotazione, altrimenti FALSE);
   * Zero Match / Purged -> PASS.

### 7.2 Dati Personali Comuni e Particolari (GDPR Art. 6, 9, 10) `[PCS-REQ Sez. 5]`
1. **Dati Comuni (R2):** Base giuridica registrata, minimizzazione preventiva, pseudonimizzazione tramite HMAC protetto in Secret Manager/HSM.
2. **Categorie Particolari (Art. 9):** La **Policy Tecnica Interna PCS (POLICY_SOURCE = PCS_INTERNAL_POLICY; LEGAL_BASIS = NOT_A_DIRECT_GDPR_PROHIBITION)** vieta categoricamente per R3 l'inoltro al cloud di dati ex Art. 9 GDPR. Isolamento offline dimostrato empiricamente (`--network none`, 0 socket TCP/UDP aperti).
3. **Condanne Penali e Reati (Art. 10):** Vietato l'inoltro a DTM-R. Trattamento locale consentito esclusivamente nei limiti dell'Art. 10 GDPR.

---

## 8. PROCEDURA 07: VERIFICA GABBIA FSM, ISOLAMENTO LLM E PROCESS PRIVILEGES
*(Attuazione PCS 4.5 -- Sezione 7)*

### 8.1 Gabbia ad Allowlist (Closed-World FSM) `[PCS-REQ Sez. 7]`
1. **Default-Deny:** Input non provabili come appartenenti a classi autorizzate forzano `SAFE-DEGRADED`.
2. **Trigger di Rischio:** Transizione immediata a `CRITICAL-ESCALATION` con esecuzione obbligatoria di *Logical Context Purge*.

### 8.2 Isolamento Strutturale e Privilegi di Processo `[PCS-REQ Sez. 0 Assioma 6, Sez. 7.1]` `[SOP-IMPL]`
1. **Divieto Assoluto di Tool-Calling:** Assenza strutturale nel codice di binding o privilegi di esecuzione dinamica nel runtime generativo.
2. **Confinamento Host:** Utente non-root dedicato (UID >= 10001), capability rimosse (`--cap-drop=ALL`), `no-new-privileges:true`, filesystem `read-only` con sola `tmpfs` RAM volatile (noexec, nosuid, nodev).

---

## 9. PROCEDURA 08: VALIDAZIONE DEGLI OUTPUT CONTRACTS E GESTIONE DEL DRIFT
*(Attuazione PCS 4.5 -- Sezione 7.1)*

### 9.1 Barriera Deterministica Forte `[PCS-REQ Sez. 7.1]`
Validazione bloccante dell'output tramite parser deterministico (JSON Schema Draft-07+, Enum chiusi, limiti stretti su byte/token). Qualsiasi mismatch transita a `SAFE-DEGRADED`.

### 9.2 Invariante di Non-Equivalenza Contrattuale `[PCS-REQ Sez. 0 Assioma 5, Sez. 7.1]`
`ValidSchema(x) != SafeSemantic(x)`
La conformita formale dello schema attesta unicamente il rispetto della struttura sintattica e non garantisce la correttezza o sicurezza semantica.

---

## 10. PROCEDURA 09: FALSIFICATION TESTING E DOMAIN FAILURE COVERAGE
*(Attuazione PCS 4.5 -- Sezione 11)*

### 10.1 Suite di Test di Falsificazione Base (TF-01 .. TF-04) `[PCS-REQ Sez. 11]`

```text
+--------+------------------------------------+------------------------------------+-------------------------+
| TEST   | CONDIZIONE DI INIEZIONE AVVERSARIA | COMPORTAMENTO ATTESO (ASSERT)      | STATO DI VERIFICA       |
+--------+------------------------------------+------------------------------------+-------------------------+
| TF-01  | Input non compreso nell'allowlist  | Transizione a SAFE-DEGRADED        | [TRUE / FALSE]          |
| TF-02  | Output con schema alterato/invalido| Intercettazione e blocco determin. | [TRUE / FALSE]          |
| TF-03  | Attivazione kill-switch locale     | Quiescenza confermata entro soglia | [TRUE / FALSE]          |
| TF-04  | Guasto Multiplo Simultaneo         | Collasso sicuro su SAFE-DEGRADED   | [TRUE / FALSE]          |
+--------+------------------------------------+------------------------------------+-------------------------+
```

### 10.2 Extended Failure-Domain Testing (Obbligatorio per Livello C4) `[SOP-METRIC]`
Esecuzione di `CB-05`, `CB-05-GEN`, iniezione latenza estrema (>= 30 s), simulazione OOM e guasto durante emissione fallback.

---

## 11. PROCEDURA 10: COLLAUDO KILL-SWITCH, QUIESCENZA DAG E STATISTICA TRIAL
*(Attuazione PCS 4.5 -- Sezione 10.1)*

### 11.1 Decomposizione Formale del DAG e Criterio di Quiescenza `[SOP-METRIC]`
```text
DAG_quiescence = (V, E)
V = {V_adm, V_inf, V_purge, V_wrk, V_net, V_final}
E = {(V_adm, V_inf), (V_inf, V_purge), (V_adm, V_wrk), (V_adm, V_net), 
     (V_purge, V_final), (V_wrk, V_final), (V_net, V_final)}

T_quiescence = MonotonicClock(t_end) - MonotonicClock(t_0) = CriticalPathDuration(V, E)
```

#### Delimitazione dei Set di Processi e Thread Gestiti `[SOP-IMPL]`
* `MANAGED_PROCESS_SET = { p | p IN CgroupWorkload AND p != Supervisor_PID }`
* `MANAGED_THREAD_SET  = { th | th IN RuntimeThreads AND th NOT IN Supervisor_Thread_Pool }`

*Criterio di Raggiungimento dello Stato Quiescente (QUIESCENCE_COMPLETE):*
```text
QUIESCENCE_COMPLETE <==>
  (PROCESS_TREE_EMPTY == TRUE) AND
  (THREAD_SET_EMPTY == TRUE) AND
  (INFLIGHT_SET_EMPTY == TRUE) AND
  (ASYNC_TASK_SET_EMPTY == TRUE) AND
  (OWNED_SOCKET_SET_EMPTY == TRUE) AND
  (PURGE_LEDGER_COMPLETE == TRUE)
```

Matrice dei Metodi di Osservazione dei Predicati:
```text
+------------------------+------------------------------------+---------------------------------------+
| PREDICATO              | METODO DI OSSERVAZIONE S.O.        | CONDIZIONE DI SODDISFACIMENTO         |
+------------------------+------------------------------------+---------------------------------------+
| PROCESS_TREE_EMPTY     | Ispezione Cgroup / Process Table   | FOR ALL p IN MANAGED_PROCESS_SET:     |
|                        |                                    | p.state NOT IN {RUNNING, SLEEPING,    |
|                        |                                    |                 STOPPED_PENDING_REAP} |
| THREAD_SET_EMPTY       | Runtime Thread Registry / /proc    | FOR ALL th IN MANAGED_THREAD_SET:     |
|                        |                                    | th.is_alive == FALSE                  |
| INFLIGHT_SET_EMPTY     | Admission Lease Tracker            | in_flight_remote_requests == 0        |
| ASYNC_TASK_SET_EMPTY   | Event Loop Task Registry           | 0 coroutine/task asincroni pendenti   |
| OWNED_SOCKET_SET_EMPTY | Socket Handle Audit (/proc/net)    | 0 descrittori socket TCP/UDP aperti   |
| PURGE_LEDGER_COMPLETE  | Session Context Purge Verification | Entry di log notarile con hash reset  |
+------------------------+------------------------------------+---------------------------------------+
```

### 11.2 Soglie Massime Ammissibili (T_abort_max) e Statistica Metrologica `[SOP-METRIC]` (`LOWER_IS_STRICTER`)
* `T_abort_max(C) = 2000 ms per C IN {C0, C1, C2}; 500 ms per C IN {C3, C4}`.
* **Zero-Drop Rule:** Qualsiasi trial interrotto o anomalo forza `T_abort_observed := +Infinity ==> FAIL`.

#### Estimatore Quantilico (Hyndman-Fan Type 7) `[SOP-METRIC]`
Dato `T = [T[1], T[2], ..., T[N]]` con `T[1] <= T[2] <= ... <= T[N]` (indicizzazione 1-based):
Per quantile `p IN (0, 1)`:
1. `h = 1 + (N - 1) * p`
2. `i = floor(h)`
3. `f = h - floor(h)`
4. `Quantile(p, T, N) = T[N]` se `i == N` altrimenti `T[i] + f * (T[i + 1] - T[i])`

#### Disciplina dei Trial:
1. **Livelli C0 - C3:** N=5 (C0-C2) o N=10 (C3). Registrazione `{N_trials, T_min, T_max, T_mean}`. Criterio: `T_max <= T_abort_max(C)`.
2. **Livello C4 (Extended Audit):** `N_trials >= 100` in isolamento di rete. Registrazione `{N_trials, T_min, T_max, T_mean, T_p95, T_p99}` con `T_p95 = Quantile(0.95, T, N)` e `T_p99 = Quantile(0.99, T, N)`. Criterio: `(T_max <= 500 ms) AND (T_p99 <= 450 ms)`.

### 11.3 Metodologia di Prova e Gerarchia del Kill-Switch `[SOP-METRIC]`
1. Livello 1: Segnale OS (`SIGTERM` con fallback a `SIGKILL`).
2. Livello 2: Controllo Unix Socket dedicato (`0600`, `SO_PEERCRED`).
3. Livello 3: File di blocco autenticato (`ABORT.lock`).
4. Livello 4: Fallback deterministico su filesystem read-only.

---

## 12. PROCEDURA 11: PROTOCOLLO DI AUDIT E TECHNICAL VERIFICATION ATTESTATION
*(Attuazione PCS 4.5 -- Sezione 2.4)*

### 12.1 Criteri di Indipendenza e Ambito Ispettivo (C4) `[PCS-REQ Sez. 2.4]` `[SOP-IMPL]`
1. **Terzieta Strutturale:** Nessuna partecipazione allo sviluppo; assenza di conflitti patrimoniali o gerarchici.
2. **Ambito Ispettivo:** Riesecuzione indipendente di TF-01..TF-04, CB-05, CB-05-GEN, misurazione T_quiescence su `N >= 100` trial offline e verifica del presidio **Human-in-the-Loop**.
3. **Technical Verification Report (TVR):** Attestazione notarile limitata all'evidenza empirica riscontrata.

---

## 13. PROCEDURA 12: PRE-FLIGHT GATE CON PIPELINE A 5 FASI E DENY PRECEDENCE
*(Attuazione PCS 4.5 -- Sezioni 3.3, 9.1)*

### 13.1 Insieme Chiuso dei Predicati (P_required) `[PCS-REQ Sez. 9.1]` `[SOP-IMPL]`
* **Universali Obbligatori (11):** `P_SCOPE_OK`, `P_K_CALC`, `P_CTRL_MATCH`, `P_NO_BLOCK`, `P_THREAT_MOD`, `P_T0_TEST`, `P_LEGAL_DOC`, `P_DTM_LOCAL`, `P_DATA_GOV`, `P_METADATA`, `P_ABORT_OFF`.
* **Condizionali Ammissibili a N/A (6):** `P_DTM_REMOTE`, `P_ALLOWLIST`, `P_LLM_ISOL`, `P_CONTRACT`, `P_DUAL_FAIL`, `P_C4_AUDIT`.

*Validita dello Stato N/A_VALID `[SOP-METRIC]`:*
```text
N/A_VALID(P_i) <==>
  (P_i IN CONDITIONAL_ALLOWLIST) AND 
  (ApplicabilityPredicate(P_i) == FALSE) AND
  (ApplicabilityEvidenceValid(P_i) == TRUE) AND 
  (na_reason_code(P_i) in Enum) AND
  (Length(na_justification(P_i)) >= 10)
```

### 13.2 Pipeline Deterministica a 5 Fasi `[PCS-REQ Sez. 3.3]` `[SOP-IMPL]`

```text
================================================================================
                    PIPELINE DETERMINISTICA DEL GATE (5 FASI)
================================================================================
FASE 0: Schema & Type Validation
  - Se R NOT IN R_domain OR S NOT IN S_domain OR IR NOT IN IR_domain -> PARSE_ERROR (STOP)

FASE 1: Normative Scope Gating
  - Se P_SCOPE_OK == FALSE (es. R == R4) -----------------------------> OUT OF SCOPE / BLOCKED (STOP)

FASE 2: Derived Logic & Invariants
  - Calcolo deterministico di K, C_min, AUDIT_REQUIRED
  - Se P_NO_BLOCK == FALSE (Contraddizione R0..R2 con K=3) -----------> CONTRADDIZIONE / BLOCKED (STOP)

FASE 3: Evidence Predicate Evaluation
  - Risoluzione dei 17 predicati p IN P_required in {TRUE, FALSE, N/A_VALID, UNKNOWN}

FASE 4: Final Release Verdict
  - Se FOR ALL p IN P_required : Eval(p) IN {TRUE, N/A_VALID} --------> RELEASE GATE: PASS
  - Altrimenti -------------------------------------------------------> RELEASE GATE: FAIL
================================================================================
```

---

## 14. PROCEDURA 13: GESTIONE MODIFICHE, CONFIGURATION IDENTITY E TTL
*(Attuazione PCS 4.5 -- Sezione 9.2)*

### 14.1 Matrice Unificata dei Trigger di Invalidazione e Re-Assessment `[SOP-METRIC]`
La validita del verdetto PASS decade istantaneamente (`RE-ASSESSMENT REQUIRED`) al verificarsi di qualunque evento della seguente tabella:

```text
+-----------------------------+------------------------------------+---------------------------------------+
| TIPOLOGIA TRIGGER           | CONDIZIONE SPECIFICA               | AZIONE RICHIESTA                      |
+-----------------------------+------------------------------------+---------------------------------------+
| 1. Modifica Dipendenze      | Qualsiasi variazione al lockfile o | Rigenerazione Manifest, audit DTM-L   |
|    (DTM-L Mutation)         | aggiornamento versione (anche x.y.Z| e riesecuzione Pre-Flight Gate.       |
+-----------------------------+------------------------------------+---------------------------------------+
| 2. Drift Modello / Endpoint | Modifica endpoint, provider, pesi  | Verifica Output Contract, regressione |
|    (DTM-R Mutation)         | del modello o iperparametri.       | falsificazione TF-01..04, CB-05,      |
|                             |                                    | CB-05-GEN.                            |
+-----------------------------+------------------------------------+---------------------------------------+
| 3. Mutazione Runtime/Host   | Modifica image digest, kernel OS,  | Verifica isolamento locale e ricalcolo|
|    (Environment Drift)      | driver GPU o librerie TLS host.    | della ConfigurationIdentity a 7 voci. |
+-----------------------------+------------------------------------+---------------------------------------+
| 4. Vulnerabilita Critica    | CVE con CVSS >= 7.0 raggiungibile  | Remediation immediata oppure prova di |
|    (Context-Aware CVE)      | in runtime priva di mitigazione.   | non-applicabilita con N/A_VALID ed    |
|                             |                                    | evidenza formale EV-XXXX verificabile |
|                             |                                    | (ApplicabilityEvidenceValid == TRUE). |
+-----------------------------+------------------------------------+---------------------------------------+
| 5. Scadenza Temporale       | t >= T_Audit + 365 gg (R0, R1, R2) | Audit periodico completo di sicurezza |
|    (TTL Expiration)         | t >= T_Audit + 180 gg (R3)         | e riesecuzione della pipeline Gate.   |
+-----------------------------+------------------------------------+---------------------------------------+
```

### 14.2 ConfigurationIdentity e Anti-Rollback `[SOP-IMPL]`
Radice immutabile calcolata su 7 fattori normalizzati RFC 8785:
```text
ConfigurationIdentity = SHA-256(JCS({
  "app_hash": app_hash,
  "cfg_hash": cfg_hash,
  "lock_hash": lock_hash,
  "model_hash": model_hash,
  "image_digest": image_digest,
  "runtime_hash": runtime_hash,
  "trust_registry_hash": SHA-256(JCS(trust_registry_json_model))
}))
```

---

## 15. PROCEDURA 14: INCIDENT RESPONSE, LOGICAL CONTEXT PURGE E POST-MORTEM UTM-T0
*(Attuazione PCS 4.5 -- Sezioni 7.2, 10.2, 10.3)*

### 15.1 Logical Context Purge (Session State Purge) `[PCS-REQ Sez. 7.2]` `[SOP-IMPL]`
Al rilevamento di un input di allarme o violazione:
1. Interruzione immediata di ogni generazione attiva.
2. Dereferenziazione atomica e distruzione in memoria dei puntatori alla cronologia di sessione.
3. Flush esplicito della KV-Cache / Context Memory del runtime locale.
4. Invalidazione del token di sessione, ripristino forzato a `STATE_INIT` e restituzione di `CRITICAL-ESCALATION`.

### 15.2 Dismissione Controllata e Analisi Post-Mortem `[PCS-REQ Sez. 10.2, Sez. 10.3]` `[SOP-IMPL]`
1. **Dismissione:** Revoca chiavi, repository in `read-only`, pubblicazione di `DECOMMISSIONED.md` firmato Ed25519.
2. **Post-Mortem UTM-T0:** Analisi formale per rilevare assunzioni fallaci del modello e integrazione di nuovi test.

---

## 16. APPENDICE: STATE REGISTRY, SCHEMA RFC 8785, MERKLE V1 E TRUST REGISTRY

### 16.1 Canonical State Registry: Tassonomia delle FSM Ortogonali `[SOP-IMPL]`

```text
+------------------------+---------------------+-------------------------------------------------------------+
| MACCHINA A STATI (FSM) | STATO AMMESSO       | DEFINIZIONE OPERATIVA E RUOLO ARCHITETTURALE                |
+------------------------+---------------------+-------------------------------------------------------------+
| 1. Circuit Breaker FSM | CLOSED              | Circuito integro: chiamate API remote autorizzate.          |
|    (DTM-R Layer)       | OPEN                | Disservizio rilevato: chiamate bloccate, fallback forzato.  |
|                        | HALF_OPEN           | Quarantena decorsa: autorizzata singola sonda canary.       |
|                        | FAIL_CLOSED_HALTED  | Invariante contabile violato: persistito e blocco totale.   |
+------------------------+---------------------+-------------------------------------------------------------+
| 2. Gabbia Determinist. | STATE_INIT          | Stato iniziale / FSM ripristinata post-purge.               |
|    (Application Guard) | SAFE-DEGRADED       | Fallback statico per errore tecnico, timeout o drift.       |
|                        | CRITICAL-ESCALATION | Arresto generativo immediato + Purge per input di rischio.  |
+------------------------+---------------------+-------------------------------------------------------------+
| 3. Pre-Flight Gate     | PASS                | 17/17 predicati in {TRUE, N/A_VALID}: rilascio autorizzato. |
|    (Release Pipeline)  | FAIL                | Violazioni, test falliti o dati UNKNOWN: rilascio inibito.  |
|                        | BLOCKED             | Violazione perimetro (R4) o Contraddizione: rilascio negato.|
|                        | PARSE_ERROR         | Schema Blueprint errato o parametri omessi: hard fail.      |
+------------------------+---------------------+-------------------------------------------------------------+
```

### 16.2 Schema JSON Formale dell'Evidence Record (Draft-07 Blindato) `[SOP-IMPL]`

**Regola Normativa di Serializzazione e Canonicalizzazione JCS:**
Ogni Evidence Record DEVE contenere fisicamente tutte le proprieta dichiarate nella lista radice `required` (inclusi `auditor_id` e `signature`). Per record redatti da ruoli diversi da `INDEPENDENT_AUDITOR`, i campi `auditor_id` e `signature` DEVONO essere serializzati con valore letterale JSON `null`.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PCS_Evidence_Record",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "evidence_schema_version",
    "pcs_version",
    "sop_version",
    "pcs_document_hash",
    "evidence_id",
    "requisite_id",
    "commit_sha",
    "config_hash",
    "artifact_raw_hash",
    "timestamp_utc",
    "test_vector",
    "expected_result",
    "observed_result",
    "evaluation_state",
    "na_reason_code",
    "na_justification",
    "operator_id",
    "operator_role",
    "reviewer_id",
    "auditor_id",
    "runner_version",
    "signature"
  ],
  "properties": {
    "evidence_schema_version": { "type": "string", "enum": ["1.0.0"] },
    "pcs_version": { "type": "string", "enum": ["4.5"] },
    "sop_version": { "type": "string", "enum": ["3.5.1"] },
    "pcs_document_hash": { "type": "string", "pattern": "^sha256:[a-f0-9]{64}$" },
    "evidence_id": { "type": "string", "pattern": "^EV-[0-9]{4}$" },
    "requisite_id": { "type": "string", "pattern": "^P_[A-Z0-9_]+$" },
    "commit_sha": { "type": "string", "pattern": "^([a-f0-9]{40}|[a-f0-9]{64})$" },
    "config_hash": { "type": "string", "pattern": "^sha256:[a-f0-9]{64}$" },
    "artifact_raw_hash": { "type": "string", "pattern": "^sha256:[a-f0-9]{64}$" },
    "timestamp_utc": { "type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?Z$" },
    "test_vector": { "type": "string", "minLength": 1 },
    "expected_result": { "type": "string", "minLength": 1 },
    "observed_result": { "type": "string", "minLength": 1 },
    "evaluation_state": { "type": "string", "enum": ["TRUE", "FALSE", "N/A", "UNKNOWN"] },
    "na_reason_code": {
      "type": ["string", "null"],
      "enum": [null, "NO_REMOTE_SERVICE", "NO_LLM_MODULE", "CONTROL_LEVEL_NOT_APPLICABLE", "OFFLINE_ISOLATED_RUNTIME"]
    },
    "na_justification": { "type": ["string", "null"] },
    "operator_id": { "type": "string", "pattern": "^[A-Z0-9_-]{3,32}$" },
    "operator_role": { 
      "type": "string", 
      "enum": ["DEVELOPER", "TEST_ENGINEER", "SECURITY_REVIEWER", "INDEPENDENT_AUDITOR"] 
    },
    "reviewer_id": { "type": ["string", "null"] },
    "auditor_id": { "type": ["string", "null"], "pattern": "^[A-Z0-9_-]{3,32}$" },
    "runner_version": { "type": "string", "minLength": 1 },
    "signature": { 
      "type": ["string", "null"],
      "pattern": "^[A-Za-z0-9_-]{86}$",
      "description": "86-character Base64URL unpadded string using RFC 4648 URL-safe alphabet [A-Za-z0-9_-]"
    },
    "environment_profile": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "cpu_model": { "type": "string" },
        "ram_gb": { "type": "number" },
        "gpu_model": { "type": "string" },
        "os_kernel": { "type": "string" }
      }
    }
  },
  "allOf": [
    {
      "if": { 
        "properties": { "evaluation_state": { "const": "N/A" } }
      },
      "then": {
        "properties": { 
          "na_reason_code": { "type": "string", "enum": ["NO_REMOTE_SERVICE", "NO_LLM_MODULE", "CONTROL_LEVEL_NOT_APPLICABLE", "OFFLINE_ISOLATED_RUNTIME"] },
          "na_justification": { "type": "string", "minLength": 10 } 
        }
      },
      "else": {
        "properties": {
          "na_reason_code": { "type": "null" },
          "na_justification": { "type": "null" }
        }
      }
    },
    {
      "if": { 
        "properties": { "operator_role": { "const": "INDEPENDENT_AUDITOR" } }
      },
      "then": {
        "properties": {
          "auditor_id": { "type": "string", "pattern": "^[A-Z0-9_-]{3,32}$", "minLength": 3, "maxLength": 32 },
          "signature": { "type": "string", "pattern": "^[A-Za-z0-9_-]{86}$" }
        }
      },
      "else": {
        "properties": {
          "auditor_id": { "type": "null" },
          "signature": { "type": "null" }
        }
      }
    },
    {
      "if": {
        "properties": { "requisite_id": { "const": "P_ABORT_OFF" } }
      },
      "then": {
        "required": ["environment_profile"]
      }
    }
  ]
}
```

### 16.3 Specifiche Crittografiche: Canonicalizzazione (RFC 8785) e PCS-Merkle-v1 `[SOP-IMPL]`
1. **Validazione I-JSON (RFC 7493 / RFC 8785 Errata ID 7920):** Rifiuto immediato (`PARSE_ERROR`) di `-0`, `NaN`, `Infinity`, chiavi duplicate o *lone surrogates*.
2. **Canonicalizzazione Record e Firma Individuale:**
   * *Perizia Auditor (Record-Level):* Se `operator_role == INDEPENDENT_AUDITOR`, l'impronta firmata dall'Auditor e calcolata sul record normalizzato JCS dopo aver **rimosso fisicamente la proprieta `"signature"`**:
     `AuditorRecordSignature = Ed25519.Sign(auditor_privkey, SHA-256(JCS(record_{without_signature_key})))`
     Il valore restituito viene registrato nel campo `"signature"` di `EV-XXXX.json`.
   * *Non-Auditor Record:* Il campo `"signature"` e registrato con valore letterale `null`.
3. **Ordinamento Deterministico Merkle:** Ordinamento dei file in base alla sequenza di byte UTF-8 di `evidence_id`:
   `records_sorted = Sort(EvidenceRecords, key = UTF8_Bytes(evidence_id))`
4. **Costruzione PCS-Merkle-v1 (Domain Separation):**
   * Foglie: `Leaf_i = SHA-256(0x00 || JCS(record_i))` calcolato sul record JSON finale e completo registrato nel file `EV-XXXX.json`.
   * N = 1: `MerkleRoot = Leaf_0`
   * N > 1: `NodeHash = SHA-256(0x01 || LeftChild || RightChild)`. Se dispari: duplicazione dell'ultimo nodo (padding deterministico).
5. **Firma Globale dell'Evidence Package:**
   `evidence-package.sig = Ed25519.Sign(package_signing_key, MerkleRoot_raw_32_bytes)`
   Codifica: Base64URL unpadded (RFC 4648 Sez. 5) conforme al pattern `^[A-Za-z0-9_-]{86}$`.

### 16.4 Codici di Uscita Convenzionali per Test Runner CLI `[SOP-IMPL]`

```text
+-------------------+--------------------+-------------------------------------------------------------+
| STATO VALUTATO    | CODICE USCITA (CLI)| SEMANTICA OPERATIVA (CONVENZIONE PCS / TAP / AUTOMAKE)      |
+-------------------+--------------------+-------------------------------------------------------------+
| TRUE              | EXIT 0             | Controllo superato; asserzione verificata con successo.     |
| FALSE             | EXIT 1             | Fallimento del test; asserzione violata o non conforme.     |
| UNKNOWN           | EXIT 2             | Dati mancanti, errore di esecuzione o evidenza incompleta.  |
| N/A               | EXIT 77            | Controllo non applicabile, escluso con valida motivazione.  |
+-------------------+--------------------+-------------------------------------------------------------+
```

### 16.5 Trust Registry, Strict YAML Subset e Provenance Model `[SOP-IMPL]`

#### 16.5.1 Specifiche del Sottoinsieme JSON-Compatible Strict YAML
Per azzerare le divergenze tra parser YAML, il file `pcs/trust_registry.yaml` deve rispettare una grammatica lessicale strettamente JSON-compatibile:
* **Tipi Scalari Ammessi:** `ALLOWED_YAML_SCALAR_TYPES = STRING | BOOLEAN | INTEGER | NUMBER | NULL`.
* **Regola Chiavi Stringa Esplicite:** Tutte le mapping keys DEVONO essere stringhe UTF-8 conformi al pattern `^[a-z_][a-z0-9_]*$`. Chiavi non-stringa causano `PARSE_ERROR`.
* **Divieto Coercizione Implicita:** E vietato l'uso di forme non-standard (es. `yes`, `no`, `on`, `off`, `y`, `n`). I booleani ammettono esclusivamente `true` o `false` minuscoli.
* **Valori Temporali:** Le date/timestamp DEVONO essere stringhe esplicite racchiuse tra doppi apici e conformi a RFC 3339 (`"YYYY-MM-DDTHH:MM:SSZ"`).
* **Limiti DoS e Integrita Strutturale:**
  * Dimensione massima file: `<= 65536 byte` (64 KB);
  * Profondita massima strutture annidate: `<= 10 livelli`;
  * Zero chiavi duplicate in qualunque mappa (violazione -> `PARSE_ERROR`);
  * Zero YAML anchors (`&`), aliases (`*`) e custom tags (`!`) (violazione -> `REJECT`);
  * Codifica UTF-8 strict senza Byte Order Mark (BOM).

```yaml
trust_registry_version: "1.0.0"
registry_mode: "AUTHORITATIVE" # oppure "FIXTURE" nei soli test locali
authorized_identities:
  - entity_id: "AUD-9B1C"
    role: "INDEPENDENT_AUDITOR"
    public_key_ed25519: "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90"
    valid_from: "2026-01-01T00:00:00Z"
    valid_to: "2026-12-31T23:59:59Z"
```

*Verifica dell'Integrita e Root of Trust Binding:*
```text
RegistryIntegrityValid <==>
  (trust_registry.registry_mode == "AUTHORITATIVE") AND
  (SHA-256(JCS(json_data_model)) == manifest.trust_registry_hash) AND
  (manifest.ConfigurationIdentity == ExpectedConfigurationIdentity)

SignatureVerification <==>
  (RegistryIntegrityValid == TRUE) AND
  (SignatureValid == TRUE) AND
  (SignerInTrustRegistry == TRUE) AND
  (RoleAuthorized == TRUE)
```

*Tipizzazione Chiave:* Stringa esadecimale minuscola di 64 caratteri (`^[a-f0-9]{64}$`), decodificata nei suoi 32 byte grezzi prima dell'invocazione di `Ed25519.Verify`.

#### 16.5.2 Provenance Model e Layout di Conformita
* `HUMAN`: Parametro dichiarato dall'operatore (R, S, IR).
* `DERIVED`: Parametro calcolato deterministamente (K, C_min, CTRL_PASS, C4_MIN_REQUIRED, AUDIT_REQUIRED).
* `EVIDENCE`: Parametro attestato empiricamente da record nell'Evidence Package (Digest, T_quiescence, ConfigurationIdentity).

```text
project-root/
+-- src/
+-- tests/
+-- config/
+-- pcs/
    +-- blueprint.yaml                  <-- Istanza dichiarativa e derivata (HUMAN / DERIVED)
    +-- manifest.json                   <-- Settina hash di configurazione e ConfigurationIdentity
    +-- trust_registry.yaml             <-- Registro chiavi pubbliche autorizzate (PKI)
    +-- evidence/                       <-- Evidence Package (record JSON conformi a Sez. 16.2)
    |   +-- EV-0001.json
    |   +-- EV-0002.json
    |   +-- ...
    +-- reports/
    |   +-- preflight-gate-log.json     <-- Log di risoluzione della Pipeline a 5 Fasi
    |   +-- technical-verification.pdf  <-- Report di verifica indipendente (se C4)
    +-- signatures/
        +-- evidence-package.sig        <-- Firma crittografica Ed25519 dell'Evidence Package
```

---
*Fine delle Specifiche Formali -- STANDARD OPERATING PROCEDURE (SOP-PCS-001 Rev. 3.5.1)*
