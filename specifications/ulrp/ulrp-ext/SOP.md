```text
================================================================================
SPECIFICA OPERATIVA STANDARD: ULRP-EXT-SOP-1.1.0
MANUALE OPERATIVO DI LABORATORIO, AUDIT E COLLAUDO DI CONFORMITA' ESTESA
Pipeline di Preprocessing Semantico, Budgeting e Gabbia Generativa LLM-Safe
================================================================================
Document ID         : ULRP-EXT-SOP-1.1.0
Revision            : Rev. 1.1.0 (Definitive Sealed Operational Extension Standard)
Base Specification  : ULRP-EXT-SPEC-1.1.0 (Frozen Standard)
Baseline Manual     : ULRP-SOP-1.0.0 (Procedura Operativa Base - Frozen)
Meta-Governance Ref : PCS 4.5 Core / SOP-PCS-001 Rev. 3.5.1
Classification      : Standard Tecnico di Ingegneria Difensiva e Audit
Status              : APPROVED / SEALED / OPERATIONAL EXTENSION STANDARD
Effective Date      : 2026-09-03
Scope               : Strictly Language-Agnostic, Runtime-Agnostic, OS-Agnostic, Tooling-Agnostic
Math Notation       : Pure Keyboard ASCII Only (No LaTeX, No Unicode Math)
================================================================================
```

```text
+------------------------------------------------------------------------------+
|               INDICE DELLE SPECIFICHE PROCEDURALI (ULRP-EXT-SOP-1.1.0)   |
+------------------------------------------------------------------------------+
|  1. Scopo, Ambito, Gerarchia Documentale, Precedenza ed Ereditarieta'        |
|  2. Evidence Model Esteso, Ancoraggio di Livello 1 e Governance Namespace    |
|  3. Extended Protocols (Delta Operativo di Laboratorio EP1 .. EP8)           |
|     3.1 Protocollo EP1: Upstream AST Selection & Grammar Adapter             |
|     3.2 Protocollo EP2: Tokenizer Adapter Axiomatic Testing & Pi_budget      |
|     3.3 Protocollo EP3: Controlled Lossy Reduction & Mutation Normalization  |
|     3.4 Protocollo EP4: CJDC Delta Document Generation & 3-Stage Audit       |
|     3.5 Protocollo EP5: Extended Storage Packaging & ValidateDatasetExt      |
|     3.6 Protocollo EP6: Compact Token Indirection & Framing PCS_FRAME_V1     |
|     3.7 Protocollo EP7: Extended Fault Injection & Dual Fallback FSM         |
|     3.8 Protocollo EP8: Canonical Conformance Suite EXT-F01 .. EXT-F36       |
|  4. Matrice Completa di Tracciabilita' Estesa (RTM)                          |
|  5. Extended Laboratory Audit Checklist (Template CAT-C)                     |
|  6. Registro Formale di Change Request (CR-Registry)                         |
+------------------------------------------------------------------------------+
```

---

# PARTE I -- FRAMEWORK METODOLOGICO, EREDITARIETÀ E GOVERNANCE

---

## 1. SCOPO, AMBITO, GERARCHIA DOCUMENTALE, PRECEDENZA ED EREDITARIETÀ

### 1.1 Finalità Operativa
Il presente manuale operativo di laboratorio (**ULRP-EXT-SOP-1.1.0**) formalizza i metodi di collaudo empirico, le metriche quantitative di conformità, i banchi di prova per adapter esterni (parser sintattici AST e modelli di tokenizzazione) e i protocolli di audit indipendenti necessari per attestare la conformità deterministica di un'implementazione software alla specifica tecnica normativa congelata **ULRP-EXT-SPEC-1.1.0**.

Tutte le espressioni matematiche, logiche e algoritmiche adottano rigorosamente la notazione scalare ASCII pura priva di codice LaTeX, comandi di formattazione a barra rovesciata o simboli Unicode non compresi nell'intervallo standard da tastiera [U+0020..U+007E]. Le frazioni sono rigorosamente raggruppate con parentesi esplicite: `(a + b) / (c + d)`.

### 1.2 Gerarchia Documentale Sistemica e Clausola di Precedenza Formale
La struttura autoritativa del sistema documentale è formalizzata come segue:

```text
[LIVELLO 1: METANORMATIVA E GOVERNANCE DI SISTEMA]
PCS 4.5 Core + SOP-PCS-001 Rev. 3.5.1
(Threat Model T0..T5, Risk Poset, PKI, Merkle v1, Pipeline Pre-Flight Gate a 5 Fasi)
       |
       +---------------------------------------+
       | governa                               | governa
       v                                       v
[LIVELLO 2: STANDARD LOSSLESS (BASE)]   [LIVELLO 3: STANDARD ESTESO (EXT)]
ULRP-SPEC-1.6.27 (Frozen Standard)  ULRP-EXT-SPEC-1.1.0 (Frozen Standard)
       |                                       |
       | specifica COSA (base pura)            | specifica COSA (delta esteso)
       v                                       v
ULRP-SOP-1.0.0                      ULRP-EXT-SOP-1.1.0
(HOW base: Protocolli P1..P7)           (HOW esteso: Delta Operativo EP1..EP8)
                                        * Eredita per incorporazione P1..P7
                                        * Innesta esclusivamente il delta EXT
```

#### Nota di Raccordo Gerarchico Sistemico
La qualifica di "Livello 3" (Standard Esteso) descrive la collocazione architetturale dell'estensione all'interno dell'intero ecosistema sistemico PCS-ULRP, operando come specifica subordinata e delta modulare rispetto al Livello 2 (Standard Lossless Base). Tale classificazione sistemica non altera, non estende e non contraddice la gerarchia interna dei deliverable descritta nella documentazione della Base (`ULRP-SOP-1.0.0 Sez. 2.1`), la quale rimane invariata, congelata e circoscritta al proprio perimetro operativo.

#### Clausola Normativa di Precedenza Formale
1. **Supremazia della Specifica (SPEC over SOP):** In caso di discrepanza, ambiguità o conflitto diretto o indiretto tra `ULRP-EXT-SPEC-1.1.0` e il presente manuale operativo, la SPEC prevale incondizionatamente. Il presente manuale non ha il potere di introdurre nuovi vincoli architetturali, alterare codici di errore o estendere le funzioni pure della specifica.
2. **Ambito di Prevalenza dell'Estensione:** Le disposizioni esplicitamente qualificate come EXT nel presente documento prevalgono sulle procedure di `ULRP-SOP-1.0.0` esclusivamente all'interno dell'ambito operativo dell'estensione (modalità lossy, AST selection, budgeting dinamico, delta packaging e prompt framing).
3. **Invarianza della Baseline Base:** Nessuna disposizione del presente manuale modifica, estende o reinterpreta implicitamente `ULRP-SPEC-1.6.27` o `ULRP-SOP-1.0.0`.

### 1.3 Principio di Ereditarietà Normativa e Non-Duplicazione
[NORMATIVE REQUIREMENT]
Se una procedura di collaudo, un metodo di verifica o una convenzione di laboratorio è già formalmente definita in `ULRP-SOP-1.0.0` e non risulta esplicitamente sostituita, modificata o integrata da `ULRP-EXT-SOP-1.1.0`, il testo della procedura base si applica integralmente per incorporazione e non viene riprodotto nel presente manuale.
Il presente standard opera rigorosamente come **delta operativo modulare**.

### 1.4 Dependency & Inheritance Matrix (Matrice di Ereditarietà e Delta Operativo)

```text
+------------------------------+--------------------+-------------------------+-----------------------------------------+
| AREA FUNZIONALE              | ORIGINE NORMATIVA  | TRATTAMENTO OPERATIVO   | DOCUMENTO / PROCEDURA APPLICABILE       |
+------------------------------+--------------------+-------------------------+-----------------------------------------+
| Ingestione UTF-8 Strict      | ULRP-1.6.27 Sez. 1 | Ereditata integrale     | ULRP-SOP-1.0.0 Sez. 2.1 (P1)        |
| Spazio Percorsi P_canon      | ULRP-1.6.27 Sez. 1 | Ereditata integrale     | ULRP-SOP-1.0.0 Sez. 2.1 (P1)        |
| Escaping E(T) e D(T_prime)   | ULRP-1.6.27 Sez. 2 | Ereditata integrale     | ULRP-SOP-1.0.0 Sez. 2.3 (P3)        |
| TokenMap e Collisioni (21/22)| ULRP-1.6.27 Sez. 2 | Ereditata integrale     | ULRP-SOP-1.0.0 Sez. 2.2 (P2)        |
| Partizionamento Base         | ULRP-1.6.27 Sez. 4 | Ereditata integrale     | ULRP-SOP-1.0.0 Sez. 2.3 (P3)        |
| CJOC Base (manifest.json)    | ULRP-1.6.27 Sez. 3 | Ereditata integrale     | ULRP-SOP-1.0.0 Sez. 2.4 (P4)        |
| Transazioni Storage 14 Passi | ULRP-1.6.27 Sez. 5 | Ereditata integrale     | ULRP-SOP-1.0.0 Sez. 3.1 (P5)        |
| Recovery 108 Stati Base      | ULRP-1.6.27 Sez. 6 | Ereditata integrale     | ULRP-SOP-1.0.0 Sez. 3.2 (P6)        |
| Conformance Lossless F01..F15| ULRP-1.6.27 Sez. 9 | Ereditata integrale     | ULRP-SOP-1.0.0 Sez. 3.3 (P7)        |
+------------------------------+--------------------+-------------------------+-----------------------------------------+
| Selettore AST (F_select)     | EXT-1.1.0 Sez. 1   | Nuova procedura (DELTA) | ULRP-EXT-SOP-1.1.0 Sez. 3.1 (EP1)   |
| Token Budgeting (Pi_budget)  | EXT-1.1.0 Sez. 2   | Nuova procedura (DELTA) | ULRP-EXT-SOP-1.1.0 Sez. 3.2 (EP2)   |
| Riduzione Lossy (Phi_red)    | EXT-1.1.0 Sez. 3   | Nuova procedura (DELTA) | ULRP-EXT-SOP-1.1.0 Sez. 3.3 (EP3)   |
| Generazione Delta CJDC       | EXT-1.1.0 Sez. 3   | Nuova procedura (DELTA) | ULRP-EXT-SOP-1.1.0 Sez. 3.4 (EP4)   |
| Storage Esteso & .pcs/       | EXT-1.1.0 Sez. 3.8 | Nuova procedura (DELTA) | ULRP-EXT-SOP-1.1.0 Sez. 3.5 (EP5)   |
| Compact Tokens & Frame V1    | EXT-1.1.0 Sez. 4   | Nuova procedura (DELTA) | ULRP-EXT-SOP-1.1.0 Sez. 3.6 (EP6)   |
| Dual Fallback FSM            | EXT-1.1.0 Sez. 5.2 | Nuova procedura (DELTA) | ULRP-EXT-SOP-1.1.0 Sez. 3.7 (EP7)   |
| Extended Suite EXT-F01..F36  | EXT-1.1.0 Sez. 6   | Nuova procedura (DELTA) | ULRP-EXT-SOP-1.1.0 Sez. 3.8 (EP8)   |
+------------------------------+--------------------+-------------------------+-----------------------------------------+
```

### 1.5 Tassonomia Rigorosa delle Prescrizioni
Ogni enunciato del presente manuale appartiene univocamente a una delle seguenti quattro classi:
* `[A] SPEC-MANDATED`: Requisito normativo assoluto imposto direttamente da `ULRP-EXT-SPEC-1.1.0` o da `ULRP-SPEC-1.6.27`.
* `[B] SOP-VERIFICATION METHOD`: Metodo operativo vincolante, procedura di misura o protocollo di test standardizzato necessario e sufficiente per dimostrare il rispetto di un requisito `[A]`.
* `[C] LABORATORY CONVENTION`: Convenzione di setup del banco di prova, struttura delle directory di lavoro o formato dei tracciati di log liberamente adottabile o modificabile dal laboratorio senza alterare la conformità.
* `[D] INFORMATIONAL GUIDANCE`: Nota esplicativa, suggerimento implementativo o chiarimento non vincolante.

### 1.6 Epistemologia del Collaudo: Separazione tra Prova Analitica e Verifica Empirica
[NORMATIVE REQUIREMENT]
Il laboratorio di collaudo e gli auditor indipendenti devono mantenere la rigorosa separazione epistemica stabilita dall'Assioma 5 PCS:
1. **Proprietà Matematicamente Provate (`PROVEN_ANALYTIC`):** I teoremi e i lemmi dimostrati analiticamente nella specifica (es. Lemma 2.3 per la monotonicità di `U_T(S)` e soundness del prompt, il Teorema di decrescenza stretta degli offset Delta in Sez. 3.4, e il Lemma di preservazione semantica di `MaterializeLossy` in Sez. 3.2) possiedono validità deduttiva universale sotto le ipotesi dichiarate. L'esecuzione dei test di laboratorio su tali proprietà **non costituisce la fonte della loro verità**, ma opera come controllo empirico contro difetti di implementazione software o violazioni delle precondizioni.
2. **Proprietà di Bounding Condizionale (`CONDITIONAL_PROVEN`):** Proprietà la cui correttezza dipende dal rispetto dei contratti da parte di adapter esterni (es. Upper-Bound Soundness dell'adapter tokenizer o parsing deterministico dell'AST). Il collaudo verifica la tenuta del bound sui vettori di test, mentre la garanzia universale esige la formale conformità dell'adapter host.
3. **Test di Conformità e Falsificazione (`CONFORMANCE_TEST`):** Esecuzione della suite congelata `EXT-F01 .. EXT-F36`. Il superamento dei test attesta che l'implementazione risponde conformemente ai casi limite prescritti, senza che ciò costituisca induzione logica di assenza assoluta di difetti su input infiniti non testati.

---

## 2. EVIDENCE MODEL ESTESO, ANCORAGGIO DI LIVELLO 1 E GOVERNANCE NAMESPACE

### 2.1 Tassonomia degli Artefatti di Evidenza EXT
Le evidenze generate durante il collaudo dell'estensione sono classificate secondo quattro categorie disgiunte:

```text
+------------------------------------------------------------------------------+
| CLASSE EV-EXT-A: OUTPUT NORMATIVI OSSERVABILI (O_ext_semantic)              |
| Artefatti persistiti su STORAGE_ROOT/OUTPUT_PATH o emessi formalmente:       |
| 1. K_compact: Sequenza dei chunk file (0001.txt..N.txt)                      |
| 2. M_ext: manifest.json conforme a CJOC (modalita' lossless o lossy)         |
| 3. R_ext: reverse_map.json conforme a CJOC                                   |
| 4. Delta_package: .pcs/delta.json conforme a CJDC (esclusivo per lossy)      |
| 5. Prompt_envelope: Frame PCS_FRAME_V1 length-prefixed emesso in memoria     |
+------------------------------------------------------------------------------+
                                       |
+------------------------------------------------------------------------------+
| CLASSE EV-EXT-B: VALORI RICOSTRUITI DURANTE L'AUDIT (In-Memory Verification) |
| Oggetti calcolati dal test harness la cui persistenza non e' prescritta:     |
| - Z_candidates, Z_unique e Z_ext post-sweep-line                             |
| - Valori intermedi di bisezione Pi_budget (S_mid, max_bound, B_effective)   |
| - Candidati grezzi e mutazioni normalizzate NormalizeMutations               |
| - Mappa biiettiva sigma_local e short-ID estratti da L_compact               |
+------------------------------------------------------------------------------+
                                       |
+------------------------------------------------------------------------------+
| CLASSE EV-EXT-C: LOG DI LABORATORIO E TRACCIATI DI PROVA EXT                 |
| Record generati dal framework di test per attestare l'audit:                 |
| - Vettori di asserzione dei predicati di reversibilita' lossy Psi_rec        |
| - Log di verifica dei vincoli closed-world (Card(lines) == 7 in Frame V1)    |
| - Tracciati di fault injection su Dual Fallback FSM                          |
| - Registrazione del tempo di quiescenza T_quiescence per ContextStateReset   |
+------------------------------------------------------------------------------+
                                       |
+------------------------------------------------------------------------------+
| CLASSE EV-EXT-D: ARTEFATTI DI DIAGNOSTICA E PROFILATURA INTERNA              |
| Dump intermedi, tracciati AST di Tree-Sitter/ANTLR, allocazioni token.       |
+------------------------------------------------------------------------------+
```

### 2.2 Ancoraggio di Livello 1 nel Manifest e Conformità Rigida allo Schema JSON
[NORMATIVE REQUIREMENT]
Per preservare la rigorosa compatibilità con il meta-standard di Livello 1 (`SOP-PCS-001 Rev. 3.5.1 Sez. 16.2`) ed evitare qualsiasi violazione della regola `"additionalProperties": false`:

1. **Invarianza dello Schema dell'Evidence Record:** I file individuali `EV-XXXX.json` emessi per documentare le prove del presente manuale **MUST NOT** contenere proprietà radice addizionali oltre alle 22 formalmente definite nello schema JSON Draft-07 di `SOP-PCS-001 Sez. 16.2`. L'identificatore del requisito EXT viene registrato nel campo conforme `requisite_id` (es. `P_CONTRACT`, `P_LLM_ISOL`, `P_DUAL_FAIL`).
2. **Ancoraggio dei Metadati EXT nel Manifest di Progetto:** L'identità di specifica e SOP EXT viene vincolata all'interno del file di radice `pcs/manifest.json` (che partecipa al calcolo RFC 8785 della `ConfigurationIdentity` a 7 fattori conforme a `SOP-PCS-001 Sez. 14.2`), registrando la sezione normativa:
   ```json
   {
     "extension_profile": {
       "ext_spec_version": "1.1.0",
       "ext_spec_document_hash": "sha256:[a-f0-9]{64}",
       "ext_sop_version": "1.1.0",
       "ext_sop_document_hash": "sha256:[a-f0-9]{64}",
       "ext_status": "FROZEN_STANDARD"
     }
   }
   ```
3. **Tracciabilità nei Vettori di Test:** All'interno del singolo record `EV-XXXX.json`, l'identificatore del test EXT (es. `EXT-F01`) e i parametri di configurazione estesa sono serializzati esclusivamente all'interno del campo stringa standardizzato `test_vector` e verificati in `observed_result`.

### 2.3 Mappatura verso i Predicati del Pre-Flight Gate (SOP-PCS-001 Sez. 13.1)
Le evidenze generate dai protocolli estesi `EP1 .. EP8` risolvono i predicati normativi del Gate di Livello 1 secondo la corrispondenza univoca:

```text
+-----------------------+-----------------------------+----------------------------------------------------+
| PREDICATO GATE PCS    | PROTOCOLLI EXT COINVOLTI    | REQUISITO / SCENARIO VERIFICATO                    |
+-----------------------+-----------------------------+----------------------------------------------------+
| P_CONTRACT            | EP3, EP4, EP5, EP6          | CJDC schema, BuildCanonicalDelta, ValidateDatasetExt|
| P_LLM_ISOL            | EP1, EP6                    | Confinamento PCS_FRAME_V1, zero tool-calling      |
| P_DATA_GOV            | EP1, EP5                    | Isolamento HARD_SECRET e dati GDPR Art. 9/10       |
| P_DUAL_FAIL           | EP7                         | Dual Fallback FSM, ContextStateReset, Abort 80     |
| P_ALLOWLIST           | EP1, EP3, EP6               | Allowlist Closed-World FSM, L_compact, sigma_local |
| P_T0_TEST             | EP2, EP3, EP4, EP6          | Falsification tests (EXT-F01..EXT-F36) anti-T0     |
+-----------------------+-----------------------------+----------------------------------------------------+
```

### 2.4 Struttura del Repository e Politica Deterministica del Namespace Evidence Record
In conformità al modello strutturale unificato di `SOP-PCS-001 Rev. 3.5.1 Sez. 16.5.2`, gli artefatti di prova del progetto risiedono esclusivamente nel percorso di radice standardizzato:

```text
project-root/
+-- src/
+-- tests/
+-- pcs/
    +-- blueprint.yaml                  <-- Istanza dichiarativa e derivata
    +-- manifest.json                   <-- ConfigurationIdentity normalizzata JCS
    +-- trust_registry.yaml             <-- Registro chiavi pubbliche autorizzate (PKI)
    +-- evidence/                       <-- Evidence Package (Draft-07 blindato, RFC 8785)
    |   +-- EV-XXXX.json                <-- Record di evidenza conformi a Sez. 16.2
    +-- reports/
    |   +-- preflight-gate-log.json     <-- Log di risoluzione Pipeline Gate a 5 Fasi
    |   +-- ext_conformance_report.json <-- Report di conformita' estesa EXT-F01..F36
    +-- signatures/
        +-- evidence-package.sig        <-- Firma Ed25519 sulla Merkle Root v1
```

#### Politica Deterministica di Allocazione degli Evidence Record `[SOP-IMPL]`
In `SOP-PCS-001 Sez. 16.3`, l'albero crittografico `PCS-Merkle-v1` impone l'ordinamento deterministico delle foglie in base ai byte UTF-8 del campo `evidence_id`:
`records_sorted = Sort(EvidenceRecords, key = UTF8_Bytes(evidence_id))`

Qualora `SOP-PCS-001 §16` non specifichi un tie-breaker per record aventi la medesima chiave `evidence_id`, l'unicità degli identificatori costituisce una condizione progettuale sufficiente per eliminare qualsiasi ambiguità nell'ordinamento Merkle.
Pertanto, il test harness del progetto deve adottare una politica deterministica di allocazione che garantisca l'assenza di ambiguità:
1. **Regola di Disgiunzione nel Package Condiviso:** Quando i record della Base (`EV-0001..EV-0007`) e i record dell'Estensione coesistono nella medesima directory `project-root/pcs/evidence/`, gli identificatori generati dai test EXT **MUST NOT** utilizzare le stringhe già riservate dai file di evidenza della Base.
2. **Modello di Mappatura Consigliato:** Il framework di test di laboratorio può implementare:
   * *Modello per Predicato:* Allocazione di 6 record dedicati ai predicati estesi (`P_CONTRACT`, `P_LLM_ISOL`, `P_DATA_GOV`, `P_DUAL_FAIL`, `P_ALLOWLIST`, `P_T0_TEST`), registrando i singoli test vettoriali `EXT-F01..F36` all'interno dei campi `test_vector` e `observed_result`; oppure
   * *Modello per Procedura / Scenario:* Allocazione di record univoci sequenziali non incidenti sui record base (es. a partire da `EV-0008` in avanti).

---

# PARTE II -- EXTENDED LABORATORY PROTOCOLS (DELTA EP1 .. EP8)

---

## 3.1 PROTOCOLLO EP1: UPSTREAM AST SELECTION & GRAMMAR ADAPTER VERIFICATION
*(Attuazione ULRP-EXT-SPEC-1.1.0 -- Sezione 1)*

### EP1.1 Scopo
Verificare l'integrazione del `ParseGrammarAdapter`, l'algoritmo di unificazione e classificazione `MergeTagsHighestRank`, la risoluzione deterministica delle sovrapposizioni tramite l'algoritmo `Resolve` (sweep-line sotto le policy `OUTERMOST_WINS` e `INNERMOST_WINS`), e l'invariante di disgiunzione assoluta su Z_ext (Errori 11, 61 e 62).

### EP1.2 Condizioni di Setup del Banco di Prova `[C]`
* Runtime host configurato con il modulo parser grammaticale del linguaggio bersaglio.
* Generatore di vettori AST capaci di simulare sovrapposizioni parziali, annidamenti concentrici e coordinate coincidenti.
* Convenzione di percorso: `$WORKSPACE_DIR/pcs_lab/ep1_ast/` (convenzione agnostica rispetto al sistema operativo host).

### EP1.3 Procedura Operativa di Collaudo
1. `[B]` **Verifica della Funzione MergeTagsHighestRank:**
   a. Inviare a `Resolve` due o più nodi candidati aventi identiche coordinate scalari `[z_s, z_e)` ma attributi divergenti:
      * Caso 1: `Cand_A = < 's', "PERSONAL_DATA" >`, `Cand_B = < 'h', "HARD_SECRET" >`;
      * Caso 2: `Cand_A = < 'b', "CRIMINAL_OFFENCE_DATA" >`, `Cand_B = < 'c', "SPECIAL_CATEGORY_DATA" >`.
   b. Verificare che il record unificato mantenga esattamente:
      * `tau_merged == 'h'` nel Caso 1 (poiché `TypeRank('h') == 3 > TypeRank('s') == 2`);
      * `tag_merged == "HARD_SECRET"` nel Caso 1 (poiché `PrivacyRank("HARD_SECRET") == 4 > PrivacyRank("PERSONAL_DATA") == 1`);
      * `tau_merged == 'b'` nel Caso 2; `tag_merged == "CRIMINAL_OFFENCE_DATA"` nel Caso 2.
2. `[B]` **Collaudo Sweep-Line per OUTERMOST_WINS:**
   a. Configurare `G_grammar` con `DisambiguationPolicy == "OUTERMOST_WINS"`;
   b. Inviare un insieme di nodi con annidamento: blocco genitore `[0, 10)` e blocchi figli `[1, 4)` e `[6, 9)`;
   c. Verificare che l'algoritmo ordini i nodi secondo `<_outer` (privilegiando a parità di inizio lo span più esteso) e selezioni unicamente il blocco `[0, 10)`, scartando i blocchi interni;
   d. Inviare nodi con sovrapposizione parziale: blocco `A = [0, 5)` e blocco `B = [2, 8)`;
   e. Verificare che venga selezionato unicamente il blocco `[0, 5)` in conformità alla regola *Leftmost-Wins* (test `EXT-F03`).
3. `[B]` **Collaudo Sweep-Line per INNERMOST_WINS:**
   a. Configurare `G_grammar` con `DisambiguationPolicy == "INNERMOST_WINS"`;
   b. Inviare il medesimo insieme di nodi con annidamento (`[0, 10)` contenente `[1, 4)` e `[6, 9)`);
   c. Verificare che l'algoritmo ordini secondo `<_canonical`, estragga ed effettui il pop del genitore `[0, 10)`, restituendo la sequenza disgiunta dei due blocchi interni `[1, 4)` e `[6, 9)`;
   d. Inviare annidamento multiplo a tre livelli (`[0, 20)` contenente `[2, 15)` contenente `[4, 8)`) e verificare che la sequenza risultante contenga unicamente il blocco più interno `[4, 8)`.
4. `[B]` **Verifica della Disgiunzione Assoluta:**
   Per ogni sequenza Z_ext prodotta da `F_select`, eseguire la verifica formale:
   ```text
   FORALL i da 0 a Card(Z_ext) - 2:
     ASSERT Z_ext[i].z_e <= Z_ext[i + 1].z_s
   ```
5. `[B]` **Iniezione Fallimento Parser AST (Errore 61):**
   Iniettare uno stream non analizzabile o un mock con coordinate eccedenti `ScalarLen(T)` (es. `z_e > ScalarLen(T)` o `z_s >= z_e`); verificare l'emissione tassativa di `SemanticError(61)`.

### EP1.4 Criteri di Accettazione `[A]`
* Disgiunzione assoluta garantita al 100% su qualsiasi sequenza Z_ext emessa con successo.
* Risoluzione conforme a `OUTERMOST_WINS` e `INNERMOST_WINS` senza regressioni.
* Proiezione `ProjectBaseZ(Z_ext)` conforme a `IsValidZ` di ULRP-1.6.27.

---

## 3.2 PROTOCOLLO EP2: TOKENIZER ADAPTER AXIOMATIC TESTING & Pi_budget VERIFICATION
*(Attuazione ULRP-EXT-SPEC-1.1.0 -- Sezione 2)*

### EP2.1 Scopo
Verificare che l'adapter del tokenizer host rispetti i tre assiomi di `mu_tok` con riserva `delta_join in [0, 4]`, verificare empiricamente le proprietà dell'inviluppo conservativo `mu_tok_seg`, e collaudare l'algoritmo dicotomico di allocazione del contesto `Pi_budget` sotto la Policy B (Quality Target non bloccante) (Errore 60).

### EP2.2 Condizioni di Setup del Banco di Prova `[C]`
* Adapter di tokenizzazione registrato (Classe A, Classe B o Classe C conforme a Sez. 2.2 della SPEC EXT).
* Suite di stringhe di test comprendente: stringa vuota, caratteri ASCII singoli, caratteri multi-byte UTF-8, sequenze di codice sorgente e delimitatori.

### EP2.3 Procedura Operativa di Collaudo
1. `[B]` **Verifica Assiomatica su Insieme di Prova Finito (Property Testing):**
   a. **Assioma 1 (Non-Negatività e Nullità):**
      Verificare che `mu_tok("") == 0` e che per ogni stringa T non vuota del set di prova `mu_tok(T) >= 1`;
   b. **Assioma 2 (Monotonia del Prefisso):**
      Per ogni coppia di stringhe (A, B) del set, verificare che `mu_tok(A) <= mu_tok(A + B)`;
   c. **Assioma 3 (Sub-Additività a Giunzione Limitata):**
      Dichiarata la costante contrattuale `delta_join in [0, 4]`, calcolare per ogni coppia (A, B):
      ```text
      cost_concat = mu_tok(A + B)
      cost_sum    = mu_tok(A) + mu_tok(B)
      ASSERT cost_concat <= (cost_sum + delta_join)
      ASSERT (cost_concat + delta_join) >= cost_sum
      ```
      Qualora un adapter violi tale limite sul set di prova, il laboratorio attesta la non conformità dell'adapter (`SemanticError(60)`).
2. `[B]` **Verifica del Contratto dell'Inviluppo mu_tok_seg:**
   a. **Upper-Bound Soundness:** Per ogni tripla `(T, k, S) in D_valid` campionata, verificare:
      `ActualCost(T[k : k + S]) <= mu_tok_seg(T, k, S)`;
   b. **Bounded Subsegment Monotonicity:** Per ogni sotto-intervallo `[a, b) subset_of [c, d)`, verificare:
      `mu_tok_seg(T, a, b - a) <= mu_tok_seg(T, c, d - c)`.
3. `[B]` **Collaudo dell'Algoritmo Pi_budget (Bisezione e Policy B):**
   a. **Caso Base Vuoto (`L_esc == 0`):** Invocare `Pi_budget` con testo vuoto e verificare la restituzione deterministica di `Success(0)` (test `EXT-F29`);
   b. **Caso Sentinella Testo Completo:** Configurare B_effective sufficientemente capiente da accogliere l'intero testo (`L_esc <= S_target_max`) e verificare la restituzione immediata di `Success(L_esc)` senza esecuzione del ciclo dicotomico;
   c. **Caso Dicotomico e Calcolo Aritmetico:** Configurare un budget ristretto; verificare che B_effective sia calcolato in pura aritmetica intera priva di floating point:
      ```text
      Q = floor(B_chunk_max / 100)
      R = B_chunk_max mod 100
      B_effective = (U_budget_pct * Q) + floor((U_budget_pct * R) / 100)
      ```
      Verificare che la ricerca binaria converga esattamente a S_optimal tale che:
      `max(k, mu_tok_seg(T_esc, k, S_optimal)) <= B_effective` e che per `S_optimal + 1` la condizione fallisca;
   d. **Verifica della Natura Non Bloccante di S_target_min:**
      Configurare un testo e un budget per cui `S_optimal < S_target_min` (es. `S_target_min == 64` ma `S_optimal == 16`, test `EXT-F17`). Verificare che `Pi_budget` **non fallisca**, ma restituisca con successo `Success(16)` (fallback proporzionale).
4. `[B]` **Iniezione Condizioni di Overflow e Budget Insufficiente (Errore 60):**
   a. Impostare `B_context <= (B_overhead + delta_join)`; verificare emissione di `SemanticError(60)`;
   b. Configurare un contesto in cui persino per `S == 1` il costo superi B_effective; verificare che `S_optimal == 0` determini `SemanticError(60)`.

### EP2.4 Criteri di Accettazione `[A]`
* Soundness del prompt completo: `mu_tok(P_full) <= B_context` garantito analiticamente dal Lemma 2.3.
* Nessun overflow nei registri UInt53.
* Determinismo assoluto: ripetute esecuzioni con identici parametri producono il medesimo S_optimal.

---

## 3.3 PROTOCOLLO EP3: CONTROLLED LOSSY REDUCTION (Phi_red) & MUTATION NORMALIZATION
*(Attuazione ULRP-EXT-SPEC-1.1.0 -- Sezione 3.1, 3.2)*

### EP3.1 Scopo
Verificare il parsing e la validazione a schema chiuso di `RedProfile`, l'algoritmo di estrazione candidati `GenerateCandidates` sulla sestupla ad unione discriminata `RuleSpec`, l'ordinamento deterministico `prec_select`, e la normalizzazione in componenti connesse massimali `NormalizeMutations` con eliminazione dei no-op (Errori 12, 62 e 71).

### EP3.2 Condizioni di Setup del Banco di Prova `[C]`
* File di profilo `RedProfile` contenente regole con discriminatori: `EXACT_LITERAL`, `DELIMITED_COMMENT`, `WHITESPACE_RUN`, `NEWLINE_RUN`.
* Test harness per l'ispezione della lista candidati pre e post normalizzazione.

### EP3.3 Procedura Operativa di Collaudo
1. `[B]` **Validazione di RedProfile (ValidateRedProfile):**
   a. Inviare un profilo contenente `EXACT_LITERAL` con pattern vuoto `""` (test `EXT-F33`); verificare reiezione con `INVALID`;
   b. Inviare un profilo con chiavi sconosciute o `rule_id` duplicati; verificare reiezione con `INVALID`;
   c. Verificare che `NormalizeRedProfile` ordini l'array delle regole per `rule_id` strettamente crescente, mentre `GenerateCandidates` le valuti ordinando per `rule_priority` decrescente e `rule_id` crescente.
2. `[B]` **Verifica della Scansione Non-Greedy di DELIMITED_COMMENT:**
   a. Predisporre un testo contenente sequenze contigue di commenti con delimitatori multipli (es. `"/*/*/*/"`, test `EXT-F34`);
   b. Verificare che `ExecuteDeterministicScan` trovi la prima occorrenza di `EndDelim` successiva a `StartDelim`, avanzando il cursore subito dopo `EndDelim` senza matching greedy espansivo.
3. `[B]` **Verifica dell'Ordinamento di Selezione prec_select:**
   a. Predisporre candidati con span sovrapposti e differenti combinazioni di priorità;
   b. Verificare che l'ordinamento rispetti rigidamente i 5 criteri a cascata definiti in Sez. 3.2 della SPEC EXT.
4. `[B]` **Collaudo Disgiunzione Inserzioni Zero-Width (AreMutationsDisjoint):**
   a. Iniettare due candidati `INSERT` aventi identico offset z (span `[z, z)`);
   b. Verificare che `AreMutationsDisjoint` restituisca `FALSE`, determinando la selezione greedy della sola inserzione con precedenza maggiore e scartando la seconda (test `EXT-F36`).
5. `[B]` **Collaudo della Normalizzazione (NormalizeMutations e ApplyComponent):**
   a. Iniettare tre mutazioni contigue o toccanti (es. `DELETE` + `INSERT` + `DELETE`, test `EXT-F35`);
   b. Verificare che vengano raggruppate in un'unica componente connessa massimale `[a, b)`;
   c. Verificare che `ApplyComponent` valuti la sostituzione cumulativa su `orig_span = T_orig[a : b]`;
   d. Verificare che se il testo risultante è identico a `orig_span`, la mutazione venga eliminata (no-op elimination);
   e. Altrimenti, verificare che venga emessa una singola mutazione canonica (`INSERT`, `DELETE` o `REPLACE`).
6. `[B]` **Verifica Empirica dell'Invariante di Equivalenza su Test Set Finito:**
   Per ogni testo del banco di prova, verificare l'uguaglianza scalare:
   `ASSERT MaterializeLossy(T_orig, SelectedMutations) == MaterializeLossy(T_orig, NormalizeMutations(SelectedMutations, T_orig))`.

### EP3.4 Criteri di Accettazione `[A]`
* Generazione candidati conforme alla sestupla discriminata `RuleSpec`.
* Assoluta assenza di sovrapposizioni o ambiguità nell'emissione canonica normalizzata.

---

## 3.4 PROTOCOLLO EP4: CJDC DELTA DOCUMENT GENERATION, SERIALIZATION & AUDIT
*(Attuazione ULRP-EXT-SPEC-1.1.0 -- Sezione 3.3, 3.4, 3.6, 3.7)*

### EP4.1 Scopo
Verificare la corretta costruzione del documento Delta tramite `BuildCanonicalDelta`, la conformità della decrescenza stretta degli offset su T_lossy, la validazione gerarchica a tre stadi (`ValidateDeltaSchema`, `ValidateDeltaStructure`, `ValidateDeltaSemantics`), e la reversibilità binaria esatta mediante Psi_rec (Errori 69, 70 e 71).

### EP4.2 Condizioni di Setup del Banco di Prova `[C]`
* Generatore di documenti `.pcs/delta.json` conformi e corrotti.
* Calcolatore crittografico SHA-256 e analizzatore di schema CJOC/CJDC.

### EP4.3 Procedura Operativa di Collaudo
1. `[B]` **Verifica della Ricorrenza degli Offset Decrescenti (BuildCanonicalDelta):**
   a. Applicare mutazioni normalizzate `(C_1, ..., C_K)`;
   b. Verificare che gli offset associati a ciascuna operazione sul testo compresso T_lossy rispettino la ricorrenza di Sezione 3.4 della SPEC EXT:
      `op_1.offset = a_1`
      `op_{i+1}.offset = op_i.offset + length_i + gap_i`
   c. Verificare che `BuildCanonicalDelta` serializzi le operazioni nell'array `operations` in ordine **strettamente decrescente**:
      `ASSERT op_K.offset > op_{K-1}.offset > ... > op_1.offset >= 0`.
2. `[B]` **Verifica Gerarchica a Tre Stadi:**
   a. **Stadio 1 (ValidateDeltaSchema):**
      * Verificare conformità a CJOC (2 spazi, chiavi ordinate, nessun escape spurio per `/`);
      * Verificare presenza esclusiva delle chiavi ammesse nello schema chiuso;
      * Verificare che `doc.delta_schema_version == "1.0.0"` e `doc.generator == "ULRP-EXT-SPEC-1.1"`;
      * Iniettare una chiave estranea o duplicata; verificare reiezione con `INVALID` / `SemanticError(69)` (test `EXT-F12`).
   b. **Stadio 2 (ValidateDeltaStructure):**
      * Verificare che `curr.offset <= succ.offset` causi il rifiuto immediato (tassatività ordine decrescente);
      * Iniettare un'operazione con `offset` e `length` eccedenti i limiti dell'aritmetica antiribaltamento UInt53 (`offset > (9007199254740991 - length)`, test `EXT-F19`); verificare reiezione;
      * Iniettare una `DELETE` a lunghezza zero con offset che interseca un intervallo `REPLACE` (test `EXT-F11`); verificare reiezione con `INVALID` / `SemanticError(69)`.
   c. **Stadio 3 (ValidateDeltaSemantics):**
      * Iniettare un Delta con `lossy_sha256` non corrispondente ai byte reali dei chunk su disco (test `EXT-F18`); verificare reiezione con `INVALID` / `SemanticError(70)`;
      * Iniettare un Delta con `original_byte_length` errata (test `EXT-F27`); verificare reiezione con `INVALID` / `SemanticError(70)`.
3. `[B]` **Collaudo della Ricostruzione Reversibile (Psi_rec):**
   a. Ricostruire il testo lossy T_lossy concatenando i chunk estratti dal filesystem;
   b. Eseguire `Psi_rec(T_lossy, Delta_file)`;
   c. Verificare che il testo restituito T_orig_restored soddisfi:
      * `ScalarLen(T_orig_restored) == Delta_file.original_code_point_count`;
      * `ByteLenUTF8(T_orig_restored) == Delta_file.original_byte_length`;
      * `HexLowerCase(SHA256(EncodeStrictUTF8(T_orig_restored))) == Delta_file.original_sha256`;
      * Identità binaria esatta: differenza in byte pari a zero rispetto al file sorgente non ridotto.
4. `[B]` **Collaudo Metrica di Churn Scalare e Soglia MaxDistPct:**
   a. Calcolare `Delta_mutation_impact_pct` su un file vuoto; verificare restituzione deterministica di 0% (test `EXT-F06`);
   b. Applicare mutazioni con churn superiore a `RedProfile.max_dist_pct`; verificare che la pipeline emetta tassativamente `SemanticError(71)`.

### EP4.4 Criteri di Accettazione `[A]`
* Reversibilità esatta a 0 byte su qualsiasi dataset lossy conforme.
* Validazione strutturale e semantica infallibile su Delta manomessi o corrotti.

---

## 3.5 PROTOCOLLO EP5: EXTENDED STORAGE PACKAGING & VALIDATEDATASETEXT
*(Attuazione ULRP-EXT-SPEC-1.1.0 -- Sezione 3.8)*

### EP5.1 Scopo
Verificare il packaging su filesystem host per dataset sia in modalità lossless che lossy tramite la funzione `ValidateDatasetExt`, certificando la corretta inclusione o rimozione della cartella `.pcs/`, la chiusura fisica del namespace e l'assenza di indirezioni (symlink, reparse point).

### EP5.2 Condizioni di Setup del Banco di Prova `[C]`
* Directory di destinazione `STORAGE_ROOT/OUTPUT_PATH` su volume controllato.
* Strumento di ispezione fisica del filesystem host (`ListaTuttiIFilesRelativi`, `ListaTutteLeDirectoryRelative`).

### EP5.3 Procedura Operativa di Collaudo
1. `[B]` **Collaudo Modalità Lossless (Delega a ValidateDataset):**
   a. Predisporre un dataset valido in modalità `lossless` (`manifest.mode == "lossless"`);
   b. Verificare che `ValidateDatasetExt` deleghi a `ValidateDataset` di ULRP-1.6.27;
   c. Creare artificialmente la directory `.pcs/` all'interno di `OUTPUT_PATH`;
   d. Eseguire `ValidateDatasetExt` e verificare che restituisca tassativamente `INVALID` (violazione chiusura namespace fisico).
2. `[B]` **Collaudo Modalità Lossy:**
   a. Predisporre un dataset in modalità `lossy` (`manifest.mode == "lossy"`);
   b. Verificare che il manifest contenga l'oggetto `lossy_profile` con chiave `delta_manifest_hash`;
   c. Verificare che il file `.pcs/delta.json` esista fisicamente e che il suo hash SHA-256 coincida esattamente con `delta_manifest_hash`;
   d. Eseguire il controllo di chiusura del namespace:
      * `ListaTuttiIFilesRelativi(H, path) == {"manifest.json", ".pcs/delta.json"} UNION declared_chunk_paths`;
      * `ListaTutteLeDirectoryRelative(H, path) == DeclaredParentDirs(declared_files)`;
   e. Verificare che la presenza di qualsiasi file orfano o directory non dichiarata restituisca `INVALID`.
3. `[B]` **Verifica Assenza di Indirezioni (ContieneLinkOIndirezioni):**
   a. Creare all'interno di `OUTPUT_PATH` o `.pcs/` un symlink, junction o hard-link con count > 1;
   b. Verificare che `ValidateDatasetExt` restituisca tassativamente `INVALID`.

### EP5.4 Criteri di Accettazione `[A]`
* Validazione superata con emissione di `< VALID, BackupIdentity >` se e solo se il dataset rispetta i 6 stadi di verifica.

---

## 3.6 PROTOCOLLO EP6: COMPACT TOKEN INDIRECTION (sigma_local) & FRAMING PCS_FRAME_V1
*(Attuazione ULRP-EXT-SPEC-1.1.0 -- Sezione 4)*

### EP6.1 Scopo
Verificare la biiezione short-ID `sigma_local` sullo spazio ristretto `Domain_compact`, la conformità a schema chiuso dell'header a esattamente 7 righe in `ParseFrameHeaderFields`, l'isolamento byte-exact del payload in `StripPromptEnvelope` (anti-troncamento), e il risolutore generativo `F_resolve_gen` con preservazione letterale dei backslash (Errori 40, 72, 73 e 74).

### EP6.2 Condizioni di Setup del Banco di Prova `[C]`
* Modulo di test con accesso all'accumulatore `TokenMap` e alle funzioni `ToCompact` e `FromCompact`.
* Test harness per la generazione di frame `PCS_FRAME_V1`.

### EP6.3 Procedura Operativa di Collaudo
1. `[B]` **Collaudo della Biiezione su Domain_compact (EXT-F07):**
   a. Popolare `TokenMap` con 10.000 token univoci;
   b. Generare testi appartenenti a `Domain_compact` (segmenti non protetti privi della sequenza non escapata `[U+00A7, U+00A7]`);
   c. Eseguire la traduzione: `T_compact = ToCompact(T_comp, sigma_local).value`;
   d. Eseguire l'inversa: `T_restored = FromCompact(T_compact, sigma_local).value`;
   e. Verificare l'identità: `ASSERT T_restored == T_comp`;
   f. Verificare il caso limite `K_total == 0`: `sigma_local` vuota, `L_compact == EMPTY_SET`, e traduzione deterministica senza errori.
2. `[B]` **Reiezione Delimitatori Non Conformi (Errore 72):**
   a. Inviare a `FromCompact` una stringa contenente la sequenza letterale `[U+00A7, U+00A7]` non formattata come placeholder compatto;
   b. Verificare che `FromCompact` emetta tassativamente `SemanticError(72)`.
3. `[B]` **Verifica a Schema Chiuso di ParseFrameHeaderFields (Card == 7):**
   a. Inviare un header valido conforme a `PCS_FRAME_V1` (esattamente 7 righe); verificare parsing con esito `Success(FrameMeta)`;
   b. Inviare un header con 8 righe contenente un campo estraneo (es. `EVIL_FIELD:x`, test `EXT-F25`);
   c. Verificare che la guardia `Card(lines) != 7` scatti immediatamente emettendo `SemanticError(74)`;
   d. Inviare un header con 6 righe (campo mancante, test `EXT-F26`); verificare emissione immediata di `SemanticError(74)`.
4. `[B]` **Collaudo Anti-Troncamento in StripPromptEnvelope (EXT-F14):**
   a. Confezionare un payload che include deliberatamente la sottostringa letterale `"\n<<<END_PAYLOAD>>>\n"`;
   b. Inviare il frame a `StripPromptEnvelope`;
   c. Verificare che il parser determini il confine del payload mediante il campo numerico `PAYLOAD_BYTE_COUNT` e non tramite scansione superficiale di stringa, estraendo il payload integro senza troncamenti spuri;
   d. Verificare la corrispondenza dell'hash crittografico `PAYLOAD_SHA256` sui byte grezzi del payload.
5. `[B]` **Verifica Preservazione Letterale Backslash (F_resolve_gen, EXT-F09):**
   a. Confezionare una generazione contenente percorsi con backslash singoli (es. `"C:\dir\file.txt"`);
   b. Invocare `F_resolve_gen`;
   c. Verificare che la stringa finale preservi esattamente il carattere `\` senza de-escaping o duplicazione spurio (`"C:\dir\file.txt"`).

### EP6.4 Criteri di Accettazione `[A]`
* Chiusura totale del frame header (`Card(lines) == 7`).
* Estrazione byte-exact del payload con tolleranza d'errore a 0 byte.
* Preservazione integrale dei token protetti e risoluzione priva di corruzione.

---

## 3.7 PROTOCOLLO EP7: EXTENDED FAULT INJECTION & DUAL FALLBACK FSM TESTING
*(Attuazione ULRP-EXT-SPEC-1.1.0 -- Sezione 5.2)*

### EP7.1 Scopo
Verificare la macchina a stati deterministica del Dual Fallback (`SAFE_DEGRADED` vs `LOSSLESS`), l'isolamento del contesto tramite `ContextStateReset`, la bonifica atomica della directory di staging (inclusa la rimozione di `.pcs/`), e la precedenza degli errori operativi (Errore 80).

### EP7.2 Condizioni di Setup del Banco di Prova `[C]`
* Harness di iniezione guasti capace di intercettare le primitive di filesystem e simulare permessi negati.
* Modulo di ispezione della memoria volatile dell'adapter generativo.

### EP7.3 Procedura Operativa di Collaudo
1. `[B]` **Collaudo Fallback SAFE_DEGRADED:**
   a. Configurare `Fallback_mode == SAFE_DEGRADED`;
   b. Iniettare un errore semantico esteso (es. Errore 61 o 71);
   c. Verificare l'esecuzione di `ContextStateReset()`: verificare che nessun dato della sessione precedente sia accessibile a livello di protocollo (test `EXT-F28`);
   d. Verificare la transizione della FSM a `STATE_INIT` e la restituzione del messaggio statico sicuro di PCS 4.5.
2. `[B]` **Collaudo Fallback LOSSLESS con Bonifica Staging (EXT-F10):**
   a. Configurare `Fallback_mode == LOSSLESS`;
   b. Generare artefatti intermedi in `STAGING_PATH` (inclusa la sottodirectory `.pcs/`);
   c. Iniettare un errore semantico esteso;
   d. Verificare che la FSM esegua atomica rimozione di `STAGING_PATH` e confermi `ClassifyPath(H, STAGING_PATH) == ABSENT`;
   e. Verificare la proiezione automatica dei parametri su `ProjectBaseConfig` e l'invocazione trasparente del kernel puro F_sem di ULRP;
   f. Verificare che il dataset finale emesso su `OUTPUT_PATH` sia un dataset lossless valido al 100% privo di cartella `.pcs/`.
3. `[B]` **Iniezione Fallimento Bonifica Staging (EXT-F16, EXT-F21):**
   a. Bloccare i permessi di rimozione su `STAGING_PATH` durante la commutazione a fallback lossless;
   b. Verificare che la FSM rilevi `ClassifyPath != ABSENT`;
   c. Verificare che l'invocazione di F_sem sia rigorosamente inibita e che il sistema collassi immediatamente restituendo `ExecutionAbort(80)` (`ERR_EXTENSION_FALLBACK_FAILURE`).

### EP7.4 Criteri di Accettazione `[A]`
* Transizione a stato sicuro priva di stati intermedi corrotti o file orfani.
* Precedenza assoluta di `ExecutionAbort(80)` su qualsiasi tentativo di pubblicazione non bonificato.

---

## 3.8 PROTOCOLLO EP8: CANONICAL CONFORMANCE SUITE EXT-F01 .. EXT-F36
*(Attuazione ULRP-EXT-SPEC-1.1.0 -- Sezione 6)*

### EP8.1 Scopo
Eseguire formalmente i 36 scenari di conformità congelati di `ULRP-EXT-SPEC-1.1.0` per rilasciare l'attestazione di conformità tecnica.

### EP8.2 Matrice di Esecuzione dei 36 Scenari Canonici

```text
+----------+----------------------------------------------+-------------------------+-----------------------------------------+
| TEST ID  | DENOMINAZIONE SCENARIO CANONICO              | REQUISITO COPERTO       | CRITERIO DI ACCETTAZIONE (ASSERT)       |
+----------+----------------------------------------------+-------------------------+-----------------------------------------+
| EXT-F01  | Dynamic Token Budget Adaptation & Policy B   | REQ-EXT-BUDGET-01       | S_optimal calcolato con riserva delta   |
| EXT-F02  | Tokenizer Axioms Property Test               | REQ-EXT-BUDGET-02       | Assiomi 1, 2, 3 rispettati su set prova |
| EXT-F03  | AST Selector Conflict & Leftmost-Wins        | REQ-EXT-SELECT-01       | Risoluzione deterministica sweep-line   |
| EXT-F04  | Privacy & Hard-Secret Isolation              | REQ-EXT-PRIVACY-01      | Blocco lossy e SemanticError(62)        |
| EXT-F05  | Multi-File Lossy Reduction & Byte Reversible | REQ-EXT-DELTA-01        | Reversibilita' esatta a 0 byte diff     |
| EXT-F06  | Mutation Churn Metric & MaxDistPct Threshold | REQ-EXT-DELTA-01        | 0% su vuoto; SemanticError(71) su over  |
| EXT-F07  | Compact Short-ID Bijective Translation       | REQ-EXT-FRAME-01        | Roundtrip identico su 10.000 token      |
| EXT-F08  | PCS_FRAME_V1 Length-Prefixed Frame Parsing   | REQ-EXT-FRAME-01        | Estrazione conforme header a 7 campi    |
| EXT-F09  | Generative Literal Backslash Preservation    | REQ-EXT-FRAME-01        | Preservazione letterale di '\'          |
| EXT-F10  | Dual Fallback Lossless Degradation           | REQ-EXT-FALLBACK-01     | Staging bonificato; output lossless     |
| EXT-F11  | Zero-Width DELETE Isolation Trap             | REQ-EXT-DELTA-04        | Rilevamento in ValidateDeltaStructure   |
| EXT-F12  | CJDC Closed-World Schema Enforcement         | REQ-EXT-DELTA-04        | Reiezione chiavi spurie con Errore 69   |
| EXT-F13  | Tokenizer State Streaming Interface Conform. | REQ-EXT-BUDGET-03       | Complessita' ammortizzata O(1) verific. |
| EXT-F14  | Prompt Framing Security Payload Arbitrario   | REQ-EXT-FRAME-01        | Zero troncamento su marker interno      |
| EXT-F15  | Reserved Namespace Trap                      | REQ-EXT-PRIVACY-01      | Reiezione .pcs/ utente con Errore 11    |
| EXT-F16  | Precedenza Errori Fallback su Storage Fail   | REQ-EXT-FALLBACK-01     | Emissione prioritaria di Abort 80       |
| EXT-F17  | Infeasible Short Chunk Budgeting             | REQ-EXT-BUDGET-01       | S_target_min non bloccante; S_opt = 16  |
| EXT-F18  | Delta Semantic Hash Mismatch                 | REQ-EXT-DELTA-01        | Mismatch hash rilevato con Errore 70    |
| EXT-F19  | Bounds Arithmetic Anti-Overflow Trap         | REQ-EXT-DELTA-04        | Reiezione pre-aritmetica con Errore 69  |
| EXT-F20  | Arbitrary Payload Frame Roundtrip            | REQ-EXT-FRAME-01        | Coerenza perfetta code point / byte     |
| EXT-F21  | Cleanup Staging Failure on Fallback          | REQ-EXT-FALLBACK-01     | Staging bloccato -> Abort 80 immediato  |
| EXT-F22  | AST Identical Candidates Highest-Rank Merge  | REQ-EXT-SELECT-01       | Fusione conservativa corretta tag/tau   |
| EXT-F23  | mu_tok_seg Conservative-Bound Soundness      | REQ-EXT-BUDGET-03       | ActualCost <= mu_tok_seg su set prova   |
| EXT-F24  | Subsegment Monotonicity Verification         | REQ-EXT-BUDGET-02       | Monotonia inclusiva provata su set      |
| EXT-F25  | Frame Unknown-Field Rejection Trap           | REQ-EXT-FRAME-02        | Riga spura respinta con Errore 74       |
| EXT-F26  | Frame Header Line Count Enforcement          | REQ-EXT-FRAME-02        | Card(lines) != 7 genera Errore 74       |
| EXT-F27  | Delta Byte-Length Mismatch Trap              | REQ-EXT-DELTA-03        | Lunghezza byte errata genera Errore 70  |
| EXT-F28  | ContextStateReset Observable Isolation       | REQ-EXT-PURGE-01        | Zero retention memoria post-reset       |
| EXT-F29  | Empty Text Budgeting Behavior                 | REQ-EXT-BUDGET-01       | L_esc = 0 produce Success(0)            |
| EXT-F30  | Delta Canonicality on Identical Inputs        | REQ-EXT-DELTA-02        | Identita' binaria byte-exact del Delta   |
| EXT-F31  | End-to-End Binary Conformance Chain          | REQ-EXT-CONFORM-01      | Catena a 6 passi validata al 100%       |
| EXT-F32  | Canonical Candidate Precedence Ordering      | REQ-EXT-RED-01          | Ordinamento prec_select verificato      |
| EXT-F33  | RuleSpec Sestupla & Non-Empty Literal Trap    | REQ-EXT-RED-01          | Pattern vuoto respinto con INVALID      |
| EXT-F34  | Delimited Comment Non-Greedy Scan            | REQ-EXT-RED-01          | Scansione non-greedy corretta su /*/*/  |
| EXT-F35  | Contiguous Mutation Fusion Verification      | REQ-EXT-DELTA-02        | Tre mutazioni fuse in un'unica REPLACE  |
| EXT-F36  | Zero-Width Insert Uniqueness Enforcement      | REQ-EXT-RED-02          | Singola inserzione a priorita' massima   |
+----------+----------------------------------------------+-------------------------+-----------------------------------------+
```

### EP8.3 Criterio di Attestazione di Conformità `[A]`
Il laboratorio rilascia esito **CONFORME** se e solo se **36/36 scenari** completano con esito `PASS`, registrando zero asserzioni violate e zero errori non deterministici.

---

# PARTE III -- TRACCIABILITÀ, AUDIT E REGISTRO MODIFICHE

---

## 4. MATRICE COMPLETA DI TRACCIABILITÀ ESTESA (RTM)

```text
+---------------------+-----------------------+-------------+-----------------------+------------------+------------------------------------+-----------+
| SPEC EXT SECTION    | SPEC REQUIREMENT ID   | SOP SECTION | GATE PREDICATE        | TEST ID          | CRITERIO DI ACCETTAZIONE NORMATIVO | CLASSE    |
+---------------------+-----------------------+-------------+-----------------------+------------------+------------------------------------+-----------+
| EXT Sez. 1.1 - 1.4  | REQ-EXT-SELECT-01     | SOP EP1     | P_CONTRACT, P_LLM_ISOL| EXT-F03, EXT-F22 | Z_ext disgiunto; sweep-line esatta | [A] / [B] |
| EXT Sez. 1.5 - 1.6  | REQ-EXT-PRIVACY-01    | SOP EP1/EP5 | P_DATA_GOV            | EXT-F04, EXT-F15 | Zero leak secret; Errore 62 / 11   | [A] / [B] |
| EXT Sez. 2.1 - 2.2  | REQ-EXT-BUDGET-02/03  | SOP EP2     | P_CONTRACT, P_T0_TEST | EXT-F02, EXT-F24 | Assiomi 1..3 tenuti; Bound sound   | [A] / [B] |
| EXT Sez. 2.3        | REQ-EXT-BUDGET-01     | SOP EP2     | P_CONTRACT            | EXT-F01, EXT-F17 | S_optimal sound entro B_effective  | [A] / [B] |
| EXT Sez. 2.4        | REQ-EXT-FRAME-01      | SOP EP6     | P_CONTRACT            | EXT-F08, EXT-F20 | Decodifica length-prefixed esatta  | [A] / [B] |
| EXT Sez. 3.1 - 3.2  | REQ-EXT-RED-01 / 02   | SOP EP3     | P_CONTRACT            | EXT-F32, EXT-F36 | Componenti connesse e no-op purge  | [A] / [B] |
| EXT Sez. 3.3 - 3.4  | REQ-EXT-DELTA-01 / 02 | SOP EP4     | P_CONTRACT            | EXT-F30, EXT-F35 | op_K.offset > op_{K-1}.offset >= 0 | [A] / [B] |
| EXT Sez. 3.6        | REQ-EXT-DELTA-01      | SOP EP4     | P_CONTRACT            | EXT-F06          | SemanticError(71) su over max_dist | [A] / [B] |
| EXT Sez. 3.7        | REQ-EXT-DELTA-03 / 04 | SOP EP4     | P_CONTRACT            | EXT-F11, EXT-F19 | Reiezione manomissioni e overflow  | [A] / [B] |
| EXT Sez. 3.8        | REQ-EXT-CONFORM-01    | SOP EP5     | P_CONTRACT            | EXT-F05, EXT-F31 | ValidateDatasetExt == VALID        | [A] / [B] |
| EXT Sez. 4.1 - 4.2  | REQ-EXT-FRAME-01      | SOP EP6     | P_ALLOWLIST           | EXT-F07          | Roundtrip esatto; Errore 72 su §§  | [A] / [B] |
| EXT Sez. 4.3        | REQ-EXT-FRAME-02      | SOP EP6     | P_CONTRACT, P_LLM_ISOL| EXT-F25, EXT-F26 | SemanticError(74) su spuri/mancanti| [A] / [B] |
| EXT Sez. 4.4 - 4.5  | REQ-EXT-FRAME-01      | SOP EP6     | P_LLM_ISOL            | EXT-F09          | Preservazione letterale backslash  | [A] / [B] |
| EXT Sez. 5.1 - 5.2  | REQ-EXT-FALLBACK-01   | SOP EP7     | P_DUAL_FAIL           | EXT-F10, EXT-F21 | Staging ABSENT; Abort 80 su blocco | [A] / [B] |
| EXT Sez. 5.2        | REQ-EXT-PURGE-01      | SOP EP7     | P_DUAL_FAIL           | EXT-F28          | Zero retention memoria post-reset  | [A] / [B] |
| EXT Sez. 6.0        | REQ-EXT-CONFORM-01    | SOP EP8     | P_T0_TEST             | EXT-F01..EXT-F36 | 36/36 Scenari PASS                 | [A] / [B] |
+---------------------+-----------------------+-------------+-----------------------+------------------+------------------------------------+-----------+
```

---

## 5. EXTENDED LABORATORY AUDIT CHECKLIST (TEMPLATE CAT-C)

Il presente prospetto deve essere compilato e firmato dall'Auditor Indipendente per il rilascio dell'attestazione di conformità tecnica:

```text
+-----+-------------------------------------------------------------+-----------------------+-------------+---------------+
| N.  | Criterio di Verifica dell'Auditor                           | Riferimento SPEC EXT  | Categoria   | Esito Audit   |
+-----+-------------------------------------------------------------+-----------------------+-------------+---------------+
| 1.  | Non-duplicazione delle procedure base di ULRP-SOP-1.0.0 | SOP EXT Sez. 1.3      | [A] / [B]   | [ ] CONFORME  |
| 2.  | Rispetto della sestupla discriminata di RuleSpec            | SPEC EXT Sez. 3.1     | [A] / [B]   | [ ] CONFORME  |
| 3.  | Separazione tra prova analitica (Lemma 2.3) e collaudo test | SOP EXT Sez. 1.6      | [B]         | [ ] CONFORME  |
| 4.  | Reversibilità esatta a zero byte diff in Psi_rec            | SPEC EXT Sez. 3.3     | [A] / [B]   | [ ] CONFORME  |
| 5.  | Rigida decrescenza degli offset op_K > op_{K-1} nel Delta   | SPEC EXT Sez. 3.4     | [A] / [B]   | [ ] CONFORME  |
| 6.  | Card(lines) == 7 applicata rigidamente in PCS_FRAME_V1      | SPEC EXT Sez. 4.3     | [A] / [B]   | [ ] CONFORME  |
| 7.  | Invariante biiettivo delimitato a Domain_compact            | SPEC EXT Sez. 4.1-4.2 | [A] / [B]   | [ ] CONFORME  |
| 8.  | S_target_min non bloccante confermato da EXT-F17            | SPEC EXT Sez. 2.3     | [A] / [B]   | [ ] CONFORME  |
| 9.  | Bonifica staging confermata prima del Fallback Lossless     | SPEC EXT Sez. 5.2     | [A] / [B]   | [ ] CONFORME  |
| 10. | Emissione vincolante di ExecutionAbort(80) su fail bonifica | SPEC EXT Sez. 5.2     | [A] / [B]   | [ ] CONFORME  |
| 11. | Riconoscimento identificatore "ULRP-EXT-SPEC-1.1"       | SPEC EXT Sez. 3.7     | [A] / [B]   | [ ] CONFORME  |
| 12. | Copertura 100% dei 36 scenari canonici EXT-F01..EXT-F36     | SPEC EXT Sez. 6.0     | [A] / [B]   | [ ] CONFORME  |
| 13. | Integrità schema JSON EV-XXXX.json (SOP-PCS-001 Sez. 16.2)  | SOP EXT Sez. 2.2      | [A] / [B]   | [ ] CONFORME  |
| 14. | Notazione matematica pura ASCII (zero LaTeX, zero Unicode)  | SOP EXT Sez. 1.1      | [A]         | [ ] CONFORME  |
| 15. | Politica deterministica per evidence_id conforme a Merkle   | SOP EXT Sez. 2.4      | [A] / [B]   | [ ] CONFORME  |
+-----+-------------------------------------------------------------+-----------------------+-------------+---------------+
```

---

## 6. REGISTRO FORMALE DI CHANGE REQUEST (CR-REGISTRY)

Qualora durante l'esecuzione fisica o l'audit di laboratorio emerga un'ambiguità, una lacuna informativa o la necessità di un nuovo requisito, è **severamente vietato modificare la specifica tecnica congelata** o introdurre requisiti impliciti nel presente manuale.
Ogni richiesta deve essere registrata formalmente nel seguente modulo per essere sottoposta al comitato normativo per la futura revisione:

```text
+------------------------------------------------------------------------------+
|                     CHANGE REQUEST REGISTRATION FORM                         |
+------------------------------------------------------------------------------+
| CR Identifier     : CR-ULRP-EXT-YYYY-XXXX                                    |
| Target Document   : ULRP-EXT-SPEC-1.1.0 (Frozen Standard)                |
| Requesting Entity : [Auditor ID / Laboratory ID]                             |
| Date Submitted    : [YYYY-MM-DD]                                             |
| Affected Clause   : [Sezione SPEC]                                           |
| Nature of Defect  : [Ambiguità / Omissione / Ottimizzazione]                 |
| Rationale         : [Motivazione tecnica e impatto sull'interoperabilità]    |
| Proposed Wording  : [Testo normativo proposto per revisione successiva]      |
| Resolution Status : SUBMITTED / UNDER_REVIEW / REJECTED / DEFERRED_TO_V1.2   |
+------------------------------------------------------------------------------+
```

```text
================================================================================
FINE MANUALE OPERATIVO ULRP-EXT-SOP-1.1.0 (APPROVED OPERATIONAL STANDARD)
================================================================================
```

