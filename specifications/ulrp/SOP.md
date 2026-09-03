```text
================================================================================
SPECIFICA OPERATIVA STANDARD: ULRP-SOP-1.0.0
MANUALE OPERATIVO DI LABORATORIO, AUDIT E COLLAUDO DI CONFORMITA'
Pipeline di Preprocessing Reversibile LLM-Safe
================================================================================
Document ID         : ULRP-SOP-1.0.0
Revision            : Rev. 1.0.0 (Sealed Production Standard)
Normative Reference : PCS 4.5 Core / SOP-PCS-001 Rev. 3.5.1 / ULRP-SPEC-1.6.27
Status              : APPROVED OPERATIONAL STANDARD (v1.0.0 - SEALED BASELINE SOP)
Classification      : Standard Tecnico di Laboratorio, Audit e Collaudo Metrologico
Effective Date      : 2026-09-02
Scope               : Strictly Implementation-Agnostic, OS-Agnostic, Tooling-Agnostic
Math Notation       : Pure Keyboard ASCII Only (No LaTeX, No Unicode Math)
================================================================================
```

---

# PARTE I -- FRAMEWORK METODOLOGICO E REGOLE DI AUDIT

---

## 1. SCOPO E AMBITO

### 1.1 Scopo del Documento
Il presente documento (ULRP-SOP-1.0.0) costituisce il manuale operativo di laboratorio per l'esecuzione, la verifica metrologica, il collaudo di affidabilita', la simulazione avversariale di guasto (fault injection) e la procedura di attestazione di conformita' di implementazioni software basate sullo standard normativo ULRP-SPEC-1.6.27, operando all'interno del framework di sicurezza, resilienza e tracciabilita' stabilito dal Protocollo Colomba Serpente (PCS 4.5 Core) e dalla SOP-PCS-001 Rev. 3.5.1.

### 1.2 Principio di Separazione Funzionale (WHAT vs HOW)
1. Lo standard normativo ULRP-SPEC-1.6.27 stabilisce rigorosamente COSA (WHAT) deve essere calcolato, quali invarianti matematiche devono sussistere, la semantica pura delle trasformazioni, la struttura dei dati, i contratti astratti di storage e la macchina a stati di crash recovery.
2. La presente SOP stabilisce COME (HOW) un laboratorio di collaudo, un auditor indipendente o un team di ingegneria deve allestire il banco di prova, eseguire i test, verificare gli invarianti mediante asserzioni formali, iniettare interruzioni transitorie deterministiche, raccogliere evidenze crittografiche non ripudiabili (Evidence Package RFC 8785 / JCS) e convalidare i predicati del Pre-Flight Gate.

### 1.3 Operatori Matematici e Metrologici di Misura (Notazione ASCII Pura)
Al fine di eliminare ogni ambiguita' lessicale e metrologica, nel presente documento sono adottati esclusivamente i seguenti operatori di misura e simboli matematici:
* `ScalarLen(T)`: Numero intero esatto di Unicode Scalar Values componenti la sequenza di testo T in SIGMA*.
* `ByteCount(B)`: Numero intero esatto di byte componenti la sequenza binaria B in {0x00..0xFF}*.
* `Card(C)`: Cardinalita' o conteggio numerico degli elementi appartenenti a una collezione, insieme finito, lista, mappa o tupla C.
* `(a + b) / (c + d)`: Notazione per divisioni e frazioni con esplicito raggruppamento tra parentesi tonde.
* Notazione logica e relazionale: `==` (uguaglianza identica), `!=` (disuguaglianza), `<=` (minore o uguale), `>=` (maggiore o uguale), `==>` (implicazione logica), `<==>` (coimplicazione logica), `AND` (congiunzione logica), `OR` (disgiunzione logica), `NOT` (negazione logica).

---

## 2. RELAZIONE FORMALE CON LA GERARCHIA DOCUMENTALE PCS

### 2.1 Gerarchia Autorizzativa a Cinque Livelli
Viene formalizzata la seguente gerarchia autoritativa immutabile di governance, conformita' e prova:

```text
    [LIVELLO 1: META-STANDARD NORMATIVO DI GOVERNANCE E AUDIT]
    Protocollo Colomba Serpente (PCS 4.5 Core) & SOP-PCS-001 Rev. 3.5.1
    Autorita' assoluta su assiomi, threat model (T0-T5), gating e crittografia.
                                   |
                                   v
    [LIVELLO 2: STANDARD NORMATIVO DI DOMINIO (LOSSLESS BASELINE)]
    ULRP-SPEC-1.6.27 (FROZEN STANDARD)
    Autorita' esclusiva per semantica pura F_sem, invarianti, errori e data model.
                                   |
                                   v
    [LIVELLO 2-OPERATIONAL: STANDARD OPERATIVO DI LABORATORIO]
    ULRP-SOP-1.0.0 (IL PRESENTE DOCUMENTO)
    Metodi di laboratorio, banchi di prova, protocolli P1-P7, fault injection.
                                   |
                                   v
    [LIVELLO 3: GUIDE IMPLEMENTATIVE NON NORMATIVE]
    Implementation Guides (IG), note applicative SDK (Rust, C++, Go, Python, Zig).
                                   |
                                   v
    [LIVELLO 4: RECORD DI ESECUZIONE FISICA ED EVIDENCE PACKAGE]
    Evidence Records EV-XXXX.json (RFC 8785), Merkle Root v1, Audit Attestation.
```

### 2.2 Regole di Precedenza e Divieto di Estensione Normativa
1. **Supremazia dei Livelli Superiori**: In caso di discrepanza, ambiguita' o conflitto tra la presente SOP e ULRP-SPEC-1.6.27, la SPEC prevale sempre e incondizionatamente su semantica pura, data model, codici di errore e contratti di storage. In caso di conflitti relativi alla classificazione del rischio, all'integrita' delle evidenze o ai criteri del Pre-Flight Gate, prevalgono incondizionatamente PCS 4.5 Core e SOP-PCS-001 Rev. 3.5.1.
2. **Divieto Assoluto di Nuovi Requisiti**: La presente SOP non puo' introdurre nuovi codici di errore semantico, alterare la priorita' delle Fasi 1..7 della SPEC, modificare i predicati dello spazio degli stati di recovery o imporre dipendenze binarie/librerie esterne. Qualsiasi prescrizione della presente SOP e' valida esclusivamente come metodo operativo di verifica di requisiti preesistenti.
3. **Risoluzione dei Dubbi Interpretativi**: Qualora una procedura operativa non sia determinata rigidamente dalla SPEC, essa e' qualificata come convenzione di laboratorio modificabile ([C] LABORATORY CONVENTION) o guida informativa ([D] INFORMATIONAL GUIDANCE), e non come requisito bloccante di conformita'.

---

## 3. DETERMINAZIONE DELLA CONFORMITA' E AMBITO DELLE PROVE

### 3.1 Riferimento Normativo della Conformita'
La conformita' di un'implementazione software I e' determinata esclusivamente rispetto al postulato della funzione pura e al criterio di conformita' definiti in ULRP-SPEC-1.6.27 (Sezione 0.2, REQ-SEM-001):

```text
(F_exec(I, D_raw, C_raw, H) == Completed(R)) ==> (R == F_sem(D_raw, C_raw))
```

La presente SOP non ridefinisce tale criterio, ma stabilisce i metodi di prova, campionamento e collaudo con cui il laboratorio verifica empiricamente che l'implementazione rispetti la funzione semantica pura F_sem ed emetta l'esito operativo ExecutionAbort(50) unicamente a fronte del fallimento non recuperabile delle risorse di storage host.

### 3.2 Ambito delle Prove e Assurance di Laboratorio
1. **Verifica di Conformita' Standard**: Attestata attraverso il superamento integrale e verificabile di tutti i protocolli di prova basati sulla SPEC, inclusa la Canonical Conformance Test Suite F01..F15 (SPEC Sez. 9.0 / Protocollo P7).
2. **Optional Enhanced Laboratory Assurance [CAT-C]**: Prove aggiuntive di stress, fuzzing combinatorio e simulazione massiva di guasti host possono essere condotte dal laboratorio come misure di qualifica implementativa, ma non costituiscono requisiti normativi oltre quanto stabilito dalla SPEC.

---

## 4. EVIDENCE MODEL E FASCICOLO DI CONFORMITA' (SOP-PCS-001 SEZ. 16 ALLINEATO)

### 4.1 Tassonomia degli Oggetti di Evidenza
Per distinguere gli output normativi dalla diagnostica di laboratorio, le evidenze sono ripartite in quattro classi disgiunte:

```text
+-----------------------------------------------------------------------------+
| CLASSE EV-A: OUTPUT NORMATIVI OSSERVABILI (O_semantic)                      |
| Artefatti fisici obbligatori prodotti su OUTPUT_PATH:                       |
| 1. K: Sequenza ordinata dei chunk file (0001.txt..N.txt)                    |
| 2. M: manifest.json (conforme a CJOC)                                       |
| 3. R: reverse_map.json (conforme a CJOC)                                    |
+-----------------------------------------------------------------------------+
                                       |
+-----------------------------------------------------------------------------+
| CLASSE EV-B: VALORI RICOSTRUITI DURANTE L'AUDIT (In-Memory Verification)    |
| Oggetti matematici calcolati dal test harness per verificare gli            |
| invarianti, la cui persistenza su disco NON e' richiesta su OUTPUT_PATH:    |
| - Testo decodificato T_orig, testo escaped T_esc                            |
| - Insieme trasformato Z_esc, testo unificato con placeholder T_comp         |
| - Accumulatore TokenMap e sottoinsiemi c_i.mapping_subset                   |
+-----------------------------------------------------------------------------+
                                       |
+-----------------------------------------------------------------------------+
| CLASSE EV-C: EVIDENCE RECORD FORMALI E MERKLE AUDIT (SOP-PCS-001 SEZ. 16)   |
| Record JSON individuali blindati secondo RFC 8785 (JCS):                    |
| - File individuali EV-0001.json .. EV-XXXX.json memorizzati nella directory |
|   pcs/evidence/ conformi a JSON Schema Draft-07 (SOP-PCS-001 Sez. 16.2)     |
| - Albero PCS-Merkle-v1 con radice calcolata su tutti i record approvati     |
| - Firma crittografica pcs/signatures/evidence-package.sig (Ed25519)         |
| - Tracciati temporali delle invocazioni storage e prove di crash recovery   |
+-----------------------------------------------------------------------------+
                                       |
+-----------------------------------------------------------------------------+
| CLASSE EV-D: ARTEFATTI DI DEBUG E DIAGNOSTICA INTERNA                       |
| Dump esadecimali, profili di memoria, log su stderr liberamente             |
| formattati dall'implementatore.                                             |
+-----------------------------------------------------------------------------+
```

### 4.2 Struttura Canonica del Fascicolo di Conformita' `[SOP-IMPL]`
In conformita' a SOP-PCS-001 Rev. 3.5.1 (Sezione 16.5.2), il fascicolo di conformita' deve risiedere nella seguente struttura del repository di progetto:

```text
project-root/
+-- src/
+-- tests/
+-- pcs/
    +-- blueprint.yaml                  <-- Istanza dichiarativa e derivata
    +-- manifest.json                   <-- ConfigurationIdentity normalizzata JCS
    +-- trust_registry.yaml             <-- Registro chiavi pubbliche autorizzate (PKI)
    +-- evidence/                       <-- Evidence Package (Draft-07 blindato, RFC 8785)
    |   +-- EV-0001.json                <-- Evidenza Protocollo P1 (P_DTM_LOCAL, P_CONTRACT)
    |   +-- EV-0002.json                <-- Evidenza Protocollo P2 (P_CONTRACT, P_ALLOWLIST)
    |   +-- EV-0003.json                <-- Evidenza Protocollo P3 (P_CONTRACT, P_T0_TEST)
    |   +-- EV-0004.json                <-- Evidenza Protocollo P4 (P_CONTRACT, P_METADATA)
    |   +-- EV-0005.json                <-- Evidenza Protocollo P5 (P_ABORT_OFF, P_T0_TEST)
    |   +-- EV-0006.json                <-- Evidenza Protocollo P6 (P_DUAL_FAIL, P_T0_TEST)
    |   +-- EV-0007.json                <-- Evidenza Protocollo P7 (Suite F01..F15)
    +-- reports/
    |   +-- preflight-gate-log.json     <-- Log di risoluzione Pipeline Gate a 5 Fasi
    |   +-- technical-verification.pdf  <-- Report notarile firmato (se livello C4)
    +-- signatures/
        +-- evidence-package.sig        <-- Firma Ed25519 sulla Merkle Root v1
```

Ciascun file `EV-XXXX.json` deve essere serializzato conformemente a JSON Schema Draft-07 (SOP-PCS-001 Sez. 16.2), contenendo tutte le 21 chiavi obbligatorie: `evidence_schema_version`, `pcs_version`, `sop_version`, `pcs_document_hash`, `evidence_id`, `requisite_id`, `commit_sha`, `config_hash`, `artifact_raw_hash`, `timestamp_utc`, `test_vector`, `expected_result`, `observed_result`, `evaluation_state` (`TRUE` | `FALSE` | `N/A`), `na_reason_code`, `na_justification`, `operator_id`, `operator_role`, `reviewer_id`, `auditor_id`, `runner_version`, `signature`.

L'aggregazione e' governata dall'algoritmo `PCS-Merkle-v1`:
1. Ordinamento lessicografico dei record: `Sort(EvidenceRecords, key = UTF8_Bytes(evidence_id))`.
2. Calcolo nodi foglia: `Leaf_i = SHA256(0x00 || JCS(record_i))` calcolato sul file JSON completo.
3. Calcolo nodi interni: `NodeHash = SHA256(0x01 || LeftChild || RightChild)`. In caso di foglia dispari, duplicazione dell'ultimo nodo.
4. Firma crittografica Ed25519 di `MerkleRoot` registrata in Base64URL unpadded a 86 caratteri dentro `evidence-package.sig`.

---

## 5. IMPLEMENTATION FREEDOM MATRIX

La presente SOP garantisce la totale neutralita' tecnologica verso le implementazioni sotto esame:

```text
+-----------------------------------------------------------------------------------------------+
| 1. BYTE-LEVEL CANONICAL EQUALITY [CAT-A]                                                      |
| - Byte esatti di ciascun chunk file c_i emesso in OUTPUT_PATH.                                |
| - Byte esatti UTF-8 di manifest.json (serializzato secondo CJOC Sez. 3.1).                    |
| - Byte esatti UTF-8 di reverse_map.json (serializzato secondo CJOC Sez. 3.1).                 |
| - Identita' binaria esatta nel roundtrip: EncodeStrictUTF8(D(Resolve(T_comp))) == B_raw.      |
+-----------------------------------------------------------------------------------------------+
| 2. SEMANTIC & STRUCTURAL CONFORMANCE [CAT-A]                                                  |
| - Naming normativo dei chunk (0001.txt..9999.txt, ToString(i).txt).                           |
| - Codici di errore semantici (10, 11, 12, 20, 21, 22, 30, 40) e abort operativo (50).         |
| - Priorita' sequenziale delle Fasi 1..7 della pipeline F_sem.                                 |
| - Chiusura del namespace fisico e assenza totale di link o indirezioni (Sez. 1.4, 1.5).       |
| - Preservazione esatta della sequenza scalare Unicode (divieto di normalizzazione NFC/NFD).   |
+-----------------------------------------------------------------------------------------------+
| 3. PROTOCOL & STATE-MACHINE ADHERENCE [CAT-A]                                                 |
| - Sequenza transazionale a 14 passi esatti (Sez. 5.4).                                        |
| - Distacco temporale tra CommitLinearizationPoint (Passo 9) e CommitDurabilityPoint (Passo 10)|
| - Risoluzione deterministica dei 108 stati base di recovery secondo Irrecoverable/RecoveryDec.|
+-----------------------------------------------------------------------------------------------+
| 4. LIBERTA' IMPLEMENTATIVA TOTALE (Non Vincolabile dalla SOP)                                 |
| - Linguaggio di programmazione sorgente (Rust, C++, Go, Python, Zig, ecc.).                   |
| - Strutture dati in memoria (alberi, hash table, vettori dinamici, ring buffer).              |
| - Modello di concorrenza, multi-threading, task asincroni prima della barriera di commit.     |
| - Rappresentazione o streaming in-memory di T_orig, T_esc, raw_chunks, T_comp.                |
| - Persistenza o meno di file intermedi di debug (tassativamente vietati in OUTPUT_PATH).      |
| - Interfaccia utente, librerie CLI, parametri a riga di comando o binding C-FFI.              |
| - Formato e verbosita' dei messaggi diagnostici descrittivi emessi su stderr.                 |
+-----------------------------------------------------------------------------------------------+
```

---

## 6. TASSONOMIA DELLE PRESCRIZIONI DI LABORATORIO

Ogni procedura descritta nel presente documento e' associata a una delle seguenti classi:
* `[A] SPEC-MANDATED`: Requisito normativo assoluto imposto da ULRP-SPEC-1.6.27 o da PCS 4.5 Core.
* `[B] SOP-VERIFICATION METHOD`: Metodo operativo vincolante necessario e sufficiente per dimostrare il rispetto di un requisito [A].
* `[C] LABORATORY CONVENTION`: Scelta organizzativa, convenzione di directory, tooling ausiliario o reportistica modificabile dal laboratorio.
* `[D] INFORMATIONAL GUIDANCE`: Suggerimento o pattern implementativo non vincolante.

---

# PARTE II -- PROTOCOLLI OPERATIVI DI PIPELINE E CODEC

---

## 2.1 PROTOCOLLO P1: INGESTIONE, UTF-8 STRICT, BOM E CANONICAL PATHS

### P1.1 Scopo
Verificare la decodifica RFC 3629 strict di stream di byte grezzi B_raw, la gestione data-centric del leading BOM (U+FEFF), l'assenza di normalizzazione Unicode e la validazione dei percorsi portabili P_canon (Errori semantici 10 e 11).

### P1.2 Condizioni di Setup del Banco di Prova di Laboratorio
* Interprete o analizzatore scalare Unicode capace di ispezionare code point nell'intervallo [U+0000..U+10FFFF] con esclusione dei surrogati [U+D800..U+DFFF].
* Insieme di vettori binari di test comprendente file corretti, flussi binari non validi RFC 3629 e percorsi non canonici.
* Directory di lavoro temporanea di laboratorio [CAT-C] configurata tramite path agnostico `$WORKSPACE_DIR/pcs_lab/p1_ingest/`.

### P1.3 Input di Prova
* Vettori binari B_raw in {0x00..0xFF}*.
* Stringhe di percorso grezzo P_raw in SIGMA*.

### P1.4 Procedura Operativa di Collaudo
1. [B] Inviare all'implementazione flussi binari contenenti sequenze di byte non conformi a RFC 3629:
   a. Byte illegali singoli (es. `0xFF`, `0xC0`, `0xC1`);
   b. Sequenze overlong (es. `0xC0 0xAF`, `0xE0 0x80 0xAF`);
   c. Code point surrogati [U+D800..U+DFFF] (es. `0xED 0xA0 0x80` per U+D800).
2. [B] Verificare che l'implementazione rifiuti immediatamente il flusso emettendo `SemanticError(10)` (ERR_INVALID_UTF8).
3. [B] Inviare un flusso binario che inizia esattamente con i byte `0xEF 0xBB 0xBF` seguiti da caratteri validi:
   a. Verificare che il testo decodificato T_orig mantenga `T_orig[0] == U+FEFF` come ordinario dato logico;
   b. Verificare che l'implementazione non rimuova tale carattere.
4. [B] Inviare un flusso binario privo dei byte iniziali `0xEF 0xBB 0xBF`:
   a. Verificare che `T_orig[0] != U+FEFF` (salvo presenza esplicita nel sorgente);
   b. Verificare che l'implementazione non inserisca alcun carattere U+FEFF sintetico.
5. [B] Inviare flussi contenenti sequenze Unicode combinanti (es. `U+0065 U+0301` rispetto a `U+00E9`):
   a. Verificare che il testo decodificato mantenga esattamente la sequenza scalare originaria senza conversione automatica in forme NFC, NFD, NFKC o NFKD.
6. [B] Inviare tuple con percorsi P_raw non conformi a Sezione 1.3 della SPEC:
   a. Percorsi con leading o trailing slash (`/a/b.txt`, `a/b.txt/`);
   b. Percorsi con caratteri vietati (`"`, `*`, `:`, `<`, `>`, `?`, `\`, `|`);
   c. Percorsi con prefissi di volume o drive (`C:/file.txt`);
   d. Percorsi con riferimenti relativi (`.` o `..`) o segmenti vuoti (`a//b.txt`);
   e. Percorsi con segmenti che terminano con spazio o punto (`a /b.txt`, `a./b.txt`);
   f. Percorsi con nomi di periferica DOS/Windows riservati (CON, PRN, AUX, NUL, COM1..COM9, LPT1..LPT9);
   g. Percorsi con caratteri di controllo [U+0000..U+001F] o U+007F.
7. [B] Verificare che l'implementazione rifiuti ciascun percorso non conforme emettendo `SemanticError(11)` (ERR_INVALID_PATH).

### P1.5 Funzioni e Predicati SPEC Coinvolti
* `DecodeStrictUTF8(B)` [SPEC Sez. 1.1]
* `P_canon` predicate [SPEC Sez. 1.3]
* `F_sem` Fasi 1 e 2 [SPEC Sez. 4.7]

### P1.6 Expected Result e Criteri di Accettazione
* [A] Qualsiasi violazione UTF-8 produce SemanticError(10).
* [A] Qualsiasi violazione di percorso portabile produce SemanticError(11).
* [A] Nessun file o directory viene creato su OUTPUT_PATH in caso di errore.
* [A] Preservazione lossless esatta della sequenza scalare Unicode: `ByteCount(diff) == 0`.

### P1.7 Tracciabilita' Predicati Gate ed Evidence
* Generazione del record conforme `EV-0001.json` associato ai predicati `P_DTM_LOCAL` e `P_CONTRACT`.
* Log comparativo esadecimale con byte offset esatto del fallimento RFC 3629.

---

## 2.2 PROTOCOLLO P2: TOKEN EXTRACTION, TOKENMAP, COLLISION HANDLING E PLACEHOLDER SCANNER

### P2.1 Scopo
Verificare l'estrazione deterministica dei blocchi protetti Z, il calcolo dei TokenID SHA-256, la gestione delle collisioni e dei conflitti di tipo in TokenMap (Errori 21 e 22), e la scansione dei placeholder sintetici L_ph tramite ParsePlaceholders (Errore 20).

### P2.2 Condizioni di Setup del Banco di Prova di Laboratorio
* Modulo di test con accesso all'accumulatore TokenMap e alla funzione ParsePlaceholders.
* Vettori di prova per simulare token identici, token con payload differente ma hash identico (mock), e token con medesimo payload ma differente TokenType.

### P2.3 Input di Prova
* Testo T_orig in SIGMA*.
* Insieme Z = { < tau_k, [z_sk, z_ek) > } con tau_k in {'s', 'b', 'h', 'c'}.

### P2.4 Procedura Operativa di Collaudo
1. [B] Esecuzione Estrazione Token:
   a. Per ciascun intervallo < tau_k, [z_sk, z_ek) > in Z, estrarre il payload grezzo non escapato K_k = T_orig[z_sk : z_ek];
   b. Calcolare l'identificatore esadecimale minuscolo a 64 caratteri:
      `TokenID(K_k) = HexLowerCase(SHA256(EncodeStrictUTF8(K_k)))`;
   c. Verificare che `ScalarLen(TokenID) == 64` e che corrisponda all'alfabeto ASCII [0-9a-f].
2. [B] Test di Deduplicazione Idempotente:
   a. Registrare due blocchi distinti aventi medesimo payload K e medesimo tau;
   b. Verificare che TokenMap contenga un singolo record per tale TokenID con esito SUCCESS.
3. [B] Test di Rilevamento Collisione Hash (Errore 21):
   a. Configurare il test harness per simulare due payload distinti K_1 != K_2 aventi medesimo TokenID;
   b. Verificare che RegisterToken intercetti la discrepanza tra TokenMap[id].K e K_curr emettendo `SemanticError(21)` (ERR_TOKEN_COLLISION).
4. [B] Test di Conflitto di Tipo (Errore 22):
   a. Inviare due blocchi con payload identico K_1 == K_2 ma con TokenType differente (es. tau_1 = 's', tau_2 = 'b');
   b. Verificare che RegisterToken intercetti il disallineamento TokenMap[id].tau != tau_curr emettendo `SemanticError(22)` (ERR_MAPPING_CONFLICT).
5. [B] Test dello Scanner ParsePlaceholders:
   a. Inviare una sequenza di testo contenente placeholder conformi a L_ph:
      `[U+00A7, U+00A7] + tau + ":" + TokenID + [U+00A7, U+00A7]` (lunghezza esatta `ScalarLen == 70`);
   b. Verificare che ParsePlaceholders restituisca Success con i record < type, id, k > estratti;
   c. Inviare sequenze corrotte o incomplete contenenti il delimitatore `[U+00A7, U+00A7]`:
      - Delimitatore con meno di 70 scalari residui nel testo;
      - TokenType non appartenente a {'s', 'b', 'h', 'c'};
      - Carattere separatore diverso da ':';
      - TokenID non conforme al pattern [0-9a-f]{64};
      - Delimitatore di chiusura mancante o diverso da `[U+00A7, U+00A7]`.
   d. Verificare che in tutti i casi di pattern non conforme a L_ph, ParsePlaceholders emetta immediatamente `SemanticError(20)` (ERR_MALFORMED_PLACEHOLDER).

### P2.5 Funzioni e Predicati SPEC Coinvolti
* `ExtractBlocks(T, Z)` [SPEC Sez. 2.4]
* `RegisterToken(TokenMap, < tau, K >)` [SPEC Sez. 2.5]
* `L_ph` grammar e `ParsePlaceholders(c)` [SPEC Sez. 2.1, 2.6]
* `PlaceholdersIn(c)` [SPEC Sez. 2.6]

### P2.6 Expected Result e Criteri di Accettazione
* [A] Registrazione deterministica e deduplicazione corretta in TokenMap.
* [A] Rilevamento tassativo di collisioni (Errore 21) e mapping conflicts (Errore 22).
* [A] Emissione di SemanticError(20) su qualsiasi stringa delimitata da `[U+00A7, U+00A7]` non perfettamente appartenente a L_ph.

### P2.7 Tracciabilita' Predicati Gate ed Evidence
* Generazione del record conforme `EV-0002.json` associato a `P_ALLOWLIST` e `P_CONTRACT`.
* Snapshot normalizzato JCS dei record registrati in TokenMap.

---

## 2.3 PROTOCOLLO P3: PARTITIONING, SPLITPOINT, APPLYPLACEHOLDERS E RIC

### P3.1 Scopo
Verificare il calcolo di EscapeMap_T, l'algoritmo SplitPoint (inclusa la gestione di S_min == 0, oversize e confini CRLF), la trasformazione post-partizionamento ApplyPlaceholders, l'operazione Resolve con emissione di E(K) e la convalida dei predicati di roundtrip RIC-1..RIC-5 (Errori 12, 30 e 40).

### P3.2 Condizioni di Setup del Banco di Prova di Laboratorio
* Modulo di partizionamento configurato per ricevere parametri nel dominio valido: S_target >= 64, R_min_pct in [1..100], Z validato.
* Test harness per la ricostruzione di T_comp, TokenMap e verifica dei predicati RIC.

### P3.3 Input di Prova
* Testo T_orig in SIGMA*, S_target, R_min_pct, insieme Z.

### P3.4 Procedura Operativa di Collaudo
1. [B] Verifica Mappatura Indici e Funzione E(T):
   a. Calcolare `T_esc = E(T_orig)` applicando Sezione 2.2 della SPEC;
   b. Verificare che `Substrings_2(T_esc)` non contenga la sottostringa `[U+00A7, U+00A7]`;
   c. Calcolare Z_esc associando a ciascun intervallo < tau_k, [EscapeMap_T(z_sk), EscapeMap_T(z_ek)), K_k >;
   d. Verificare l'invariante: `T_esc[EscapeMap_T(z_sk) : EscapeMap_T(z_ek)] == E(K_k)`.
2. [B] Collaudo Casi Limite di SplitPoint e Progressione:
   a. Caso Normale (S_min > 0): Verificare che lo split avvenga sul massimo confine in B_primary; in assenza, su B_secondary; in assenza, fallback su C_ideal;
   b. Caso Limite CRIT-01 (S_min == 0, es. S_target = 64, R_min_pct = 1):
      - Predisporre un testo con newline a C_start - 1 (da cui C_start in B(T)) e nessun newline successivo;
      - Verificare che SplitPoint valuti la clausola B_primary con limite inferiore (C_start + max(1, S_min)) == C_start + 1;
      - Verificare che C_start non venga selezionato e che lo split avanzi a C_ideal, garantendo C_split - C_start >= 1 senza emettere `SemanticError(30)`;
   c. Caso Token Oversize all'Origine: Intervallo protetto a C_start con (z_e - z_s) > S_target ==> verificare emissione di chunk dedicato [C_start, z_e);
   d. Caso Token Oversize nella Finestra: Intervallo protetto con C_start < z_s < C_ideal e (z_e - z_s) > S_target ==> verificare split anticipato a z_s;
   e. Caso Atomicita' CRLF: Testo con terminatori `\r\n` ==> verificare che lo split avvenga dopo `\n` senza separare la coppia `\r\n`;
   f. Caso File Vuoto (ScalarLen(T_orig) == 0): Verificare che Partition restituisca una sequenza contenente un singolo chunk vuoto `("")`.
3. [B] Collaudo Invariante di Token Atomicity:
   a. Per ogni split calcolato C_split e per ogni blocco [z_s, z_e) in Z_esc, verificare:
      `C_split <= z_s OR C_split >= z_e`.
4. [B] Applicazione Post-Partition dei Placeholder (ApplyPlaceholders):
   a. Per ciascun chunk grezzo c_esc == T_esc[C_start : C_split], identificare i blocchi Z_chunk interamente contenuti in [C_start, C_split);
   b. Sostituire ciascun blocco E(K_k) con il placeholder P_k = [U+00A7, U+00A7] + tau_k + ":" + TokenID(K_k) + [U+00A7, U+00A7];
   c. Verificare che il chunk finale risultante chunk_ph contenga i placeholder integrali;
   d. Verificare che le coordinate originarie di Z_esc non vengano utilizzate per indicizzare chunk_ph.
5. [B] Verifica Predicati di Roundtrip (RIC-1..RIC-5):
   a. Calcolare `T_comp = Concat(chunk_1, ..., chunk_N)`;
   b. Verificare RIC-1: `Concat(c_1, ..., c_N) == T_comp`;
   c. Verificare RIC-2: Per ogni chunk, `HexLowerCase(SHA256(EncodeStrictUTF8(c_i))) == chunk_i.sha256`;
   d. Verificare RIC-3: `ParsePlaceholders(T_comp) == SUCCESS`;
   e. Verificare RIC-4: Per ciascun chunk, `keys(c_i.mapping_subset) == PlaceholdersIn(c_i)` e i record corrispondono alla restrizione di TokenMap;
   f. Verificare RIC-5 e Invariante Centrale:
      - Eseguire `Resolve(T_comp, TokenMap)`;
      - Verificare che Resolve emetta E(TokenMap[id].K) per ciascun placeholder, producendo esattamente E(T_orig);
      - Inviare token contenenti caratteri di escape (es. `K = "C:\\path"` o `K = "§1"`) e verificare che Resolve ripristini E(K) evitando corruzioni da parte di D;
      - Eseguire `D(Resolve(T_comp, TokenMap))` e verificare l'uguaglianza scalare esatta con T_orig;
      - Verificare `EncodeStrictUTF8(D(Resolve(T_comp, TokenMap))) == B_raw`.
6. [B] Iniezione Fallimento Roundtrip (Errore 40):
   a. Manomettere un byte all'interno di un chunk o alterare un record in TokenMap;
   b. Verificare che la pipeline intercetti la violazione emettendo `SemanticError(40)` (ERR_RIC_VERIFICATION_FAILED).

### P3.5 Funzioni e Predicati SPEC Coinvolti
* `EscapeMap_T`, `B(T_esc)`, `CollidingInterval` [SPEC Sez. 4.1, 4.2]
* `Partition`, `SplitPoint` [SPEC Sez. 4.3]
* `ApplyPlaceholders` [SPEC Sez. 4.4]
* `Resolve`, `RIC-1..RIC-5` [SPEC Sez. 4.6]
* Invariante Centrale di Reversibilita' [SPEC Sez. 4.8]

### P3.6 Expected Result e Criteri di Accettazione
* [A] Progresso stretto `C_split - C_start >= 1` in ogni circostanza.
* [A] Atomicita' assoluta dei token protetti (nessun placeholder diviso tra chunk adiacenti).
* [A] Reversibilita' lossless perfetta: `ByteCount(B_raw_orig XOR B_raw_restored) == 0`.
* [A] Tutti i predicati RIC applicabili al caso di prova (RIC-1..RIC-5 per esecuzioni nominali con successo) devono valutare a TRUE.
* [A] Emissione di SemanticError(30) se si forza uno split nullo; SemanticError(40) se RIC fallisce.

### P3.7 Tracciabilita' Predicati Gate ed Evidence
* Generazione del record conforme `EV-0003.json` associato ai predicati `P_CONTRACT` e `P_T0_TEST`.
* Tracciato comparativo esadecimale `B_raw` rispetto a `Decode/Resolve/D`.

---

## 2.4 PROTOCOLLO P4: STORAGE PACKAGING, CJOC, MANIFESTHASH E VALIDATEDATASET

### P4.1 Scopo
Verificare la serializzazione canonica JSON secondo il contratto CJOC, il rispetto dello schema chiuso (Closed-World), il calcolo di ManifestHash e la conformita' della funzione ValidateDataset (chiusura fisica del namespace e assenza totale di link o indirezioni).

### P4.2 Condizioni di Setup del Banco di Prova di Laboratorio
* Directory di staging contenente i chunk finali generati e TokenMap completa.
* Analizzatore sintattico CJOC conforme a RFC 8259 e ispettore di filesystem host.

### P4.3 Input di Prova
* Dataset strutturato in directory di staging `$WORKSPACE_DIR/pcs_lab/p4_staging/`.

### P4.4 Procedura Operativa di Collaudo
1. [B] Verifica Naming Normativo dei Chunk:
   a. Verificare che i file chunk siano denominati rigorosamente `0001.txt` .. `9999.txt` per indici in [1..9999], e `ToString(i) + ".txt"` per indici superiori;
   b. Verificare che ciascun chunk appartenga a uno e un solo record in `manifest.files`.
2. [B] Verifica Serializzazione CJOC (manifest.json e reverse_map.json):
   a. Verificare codifica UTF-8 strict senza BOM iniziale;
   b. Verificare ordinamento lessicografico crescente delle chiavi basato sul confronto byte-a-byte dei valori UTF-8;
   c. Verificare indentazione esatta a 2 spazi (U+0020 U+0020) per livello di profondita';
   d. Verificare separatori `": "` (chiave-valore) e `",\n"` (elementi);
   e. Verificare terminatore finale singolo `\n` (U+000A);
   f. Verificare dominio numerico UInt53: solo numeri interi nel range [0, 9007199254740991] con forma lessicale `^[0-9]+$`; verificare rifiuto di floating point (`1.0`), esponenziali (`1e0`), zeri iniziali (`01`) o negativi (`-1`);
   g. Verificare string escaping: solo `\"`, `\\` e caratteri di controllo `\u00xx`; verificare che il carattere slash `/` (U+002F) non sia escapato (`\/` e' VIETATO).
3. [B] Verifica Closed-World Schema:
   a. Inserire una chiave estranea non definita dalla SPEC in `manifest.json` o `reverse_map.json`;
   b. Verificare che ParseJSON o ValidateDataset rigettino il documento restituendo `INVALID`;
   c. Inserire chiavi duplicate all'interno del medesimo oggetto JSON e verificare il rigetto con `PARSE_ERROR` / `INVALID`.
4. [B] Verifica ManifestHash e BackupIdentity:
   a. Calcolare `ManifestHash = HexLowerCase(SHA256(manifest_bytes))` sui byte grezzi esatti di manifest.json;
   b. Verificare la corrispondenza con la tupla `< generation_id, manifest_hash >` restituita da ValidateDataset.
5. [B] Esecuzione Completa di ValidateDataset:
   a. Eseguire i 5 controlli sequenziali di Sezione 3.7 della SPEC:
      - Controllo 1: Closed-world schema radice manifest;
      - Controllo 2: Closed-world schema manifest.files;
      - Controllo 3: Closed-world schema manifest.chunks;
      - Controllo 4: Ricostruzione completa file tramite ReconstructFile e verifica somme cumulative scalari/byte;
      - Controllo 5: Chiusura del namespace fisico:
        * Verificare che `ListaTuttiIFilesRelativi(H, path)` coincida esattamente con `{"manifest.json"} UNION declared_paths`;
        * Verificare che `ListaTutteLeDirectoryRelative(H, path)` coincida esattamente con `DeclaredParentDirs(declared_files)`;
        * Verificare che non vi siano file orfani o directory vuote non dichiarate.
6. [B] Test Rilevamento Indirezioni e Link (ContieneLinkOIndirezioni):
   a. Creare all'interno del dataset un symlink, una directory junction, un mount point o un file con hard link count > 1;
   b. Verificare che ValidateDataset restituisca tassativamente `INVALID`.

### P4.5 Funzioni e Predicati SPEC Coinvolti
* `CJOC Contract` [SPEC Sez. 3.1, 3.2, 3.3]
* `ChunkFileName`, `ManifestHash`, `BackupIdentity` [SPEC Sez. 3.4, 3.5]
* `ReconstructFile`, `ValidateDataset` [SPEC Sez. 3.6, 3.7]
* `ContieneLinkOIndirezioni`, `DeclaredParentDirs` [SPEC Sez. 1.4, 1.5]

### P4.6 Expected Result e Criteri di Accettazione
* [A] Dataset conforme al Closed-World Schema.
* [A] ValidateDataset restituisce `< VALID, identity >` se e solo se tutti i 5 controlli hanno successo.
* [A] Qualsiasi alterazione di byte, hash o file orfano determina esito `INVALID`.

### P4.7 Tracciabilita' Predicati Gate ed Evidence
* Generazione del record conforme `EV-0004.json` associato ai predicati `P_CONTRACT` e `P_METADATA`.
* Report di validazione formato CJOC ed esito formale di ValidateDataset.

---

# PARTE III -- TRANSAZIONI, RECOVERY E CONFORMITA'

---

## 3.1 PROTOCOLLO P5: ATOMIC COMMIT, LINEARIZATION POINT E DURABILITY POINT

### P5.1 Scopo
Verificare l'esecuzione sequenziale dei 14 passi della pipeline di pubblicazione transazionale (Sezione 5.4 della SPEC), convalidando il distacco concettuale e temporale tra CommitLinearizationPoint (Passo 9) e CommitDurabilityPoint (Passo 10).

### P5.2 Condizioni di Setup del Banco di Prova di Laboratorio
* Volume storage configurato come Atomic Rename Domain (medesimo filesystem logico host per STAGING_PATH, BACKUP_PATH e OUTPUT_PATH) [CAT-B].
* Test harness per intercettare l'avanzamento sincronizzato delle primitive di storage [CAT-C].
* STORAGE_ROOT configurato nel percorso agnostico `$WORKSPACE_DIR/pcs_lab/storage_root/`.

### P5.3 Procedura Operativa di Collaudo
1. [B] Tracciamento Sequenza di Pubblicazione Nominale (Passi 1..14):
   * Passo 1: Generazione del dataset completo in STAGING_PATH;
   * Passo 2: Esecuzione di `PersistBarrier()` == SUCCESS;
   * Passo 3: Esecuzione di `ValidateDataset(H, STAGING_PATH)` == VALID;
   * Passo 4: Scrittura atomica del journal `WriteAtomic(JOURNAL_PATH, { state: "STAGED", source_generation: G_prev, source_manifest_hash: H_prev })`;
   * Passo 5: Esecuzione di `PersistBarrier()` == SUCCESS;
   * Passo 6: Se OUTPUT_PATH esiste: `RenameIfAbsent(OUTPUT_PATH, BACKUP_PATH)`;
   * Passo 7: `RenameIfAbsent(STAGING_PATH, OUTPUT_PATH)`;
   * Passo 8: Esecuzione di `PersistBarrier()` == SUCCESS;
   * Passo 9: `WriteAtomic(JOURNAL_PATH, { state: "COMMITTED", ... })` ===> `[COMMIT LINEARIZATION POINT]`;
   * Passo 10: Esecuzione di `PersistBarrier()` == SUCCESS ===> `[COMMIT DURABILITY POINT]`;
   * Passo 11: `RemoveIfExists(BACKUP_PATH)`;
   * Passo 12: `RemoveIfExists(JOURNAL_PATH)`;
   * Passo 13: Esecuzione di `PersistBarrier()` == SUCCESS;
   * Passo 14: Emissione di `Success(O_semantic)` al client chiamante.
2. [B] Verifica Invariante di Linearizzazione rispetto alla Durabilita':
   a. Verificare che prima del completamento con esito SUCCESS del Passo 9, la transazione risulti nello stato STAGED (o non iniziata);
   b. Verificare che al completamento del Passo 9 la transazione sia linearizzata come COMMITTED nel journal, ma che tale esito non costituisca ancora notifica di successo per il chiamante;
   c. Verificare che il chiamante riceva la notifica `Success(O_semantic)` ONLY AFTER il completamento con successo della barriera di durabilita' al Passo 10;
   d. Verificare che il Passo 9 venga eseguito esclusivamente DOPO che OUTPUT_PATH e' stato validato e posizionato (Passi 7-8).

### P5.4 Funzioni e Predicati SPEC Coinvolti
* Contratti delle Primitive di Storage [SPEC Sez. 5.1]
* Sequenza di Pubblicazione Transazionale [SPEC Sez. 5.4]

### P5.5 Expected Result e Criteri di Accettazione
* [A] Esecuzione ordinata e non invertibile dei passi 1..14.
* [A] Nessun ack di successo inviato prima del Passo 10.
* [A] Rispetto dei contratti di barriera e atomicita'.

### P5.6 Tracciabilita' Predicati Gate ed Evidence
* Generazione del record conforme `EV-0005.json` associato ai predicati `P_ABORT_OFF` e `P_T0_TEST`.
* Tracciato temporale delle invocazioni storage e dump del journal tx.json negli stati STAGED e COMMITTED.

---

## 3.2 PROTOCOLLO P6: CRASH RECOVERY, SPAZIO DEI 108 STATI E PIANI DI RECOVERY

### P6.1 Scopo
Verificare la risoluzione deterministica del recovery su tutte le 108 combinazioni dello spazio degli stati base (Teoremi 1, 2A e 2B della SPEC), distinguendo il modello F_crash dal degrado hardware permanente F_hardware_decay.

### P6.2 Condizioni di Setup del Banco di Prova di Laboratorio
* Harness di simulazione guasti capace di predisporre stati host sintetici in STORAGE_ROOT o di interrompere l'esecuzione mediante simulatore di crash-stop controllato [CAT-C].

### P6.3 Definizione della Matrice Esaustiva dei 108 Stati Base
Lo spazio discreto base e' formato dal prodotto cartesiano dei 4 vettori di stato:
* `tx_state` in {ABSENT, CORRUPT, STAGED, COMMITTED} (4 valori)
* `staging_status` in {ABSENT, VALID, CORRUPT} (3 valori)
* `backup_status` in {ABSENT, VALID, CORRUPT} (3 valori)
* `output_status` in {ABSENT, VALID, CORRUPT} (3 valori)
Totale combinazioni base: 4 * 3 * 3 * 3 = 108 stati.

### P6.4 Procedura Operativa di Collaudo
1. [B] Sintesi e Test dei Gruppi di Stato:
   Per ciascuna delle 108 combinazioni fisiche predisposte su storage:
   a. Eseguire la funzione di classificazione `StateOf(H)`;
   b. Valutare il predicato `Irrecoverable(S)` secondo le 6 clausole di Sezione 6.1 della SPEC;
   c. Valutare la decisione `RecoveryDecision(S)` secondo Sezione 6.2 della SPEC;
   d. Eseguire `ExecuteRecovery(Plan, H)`;
   e. Verificare che l'esito corrisponda esattamente alla classificazione normativa:
      - Per gli stati recuperabili: esecuzione del piano e convergenza deterministica a S_canonical;
      - Per gli stati irrecuperabili (`Irrecoverable(S) == TRUE`): arresto immediato con esito tassativo `FatalExecutionAbort(50)` (`PLAN_ABORT`);
      - Per gli stati condizionati: esito subordinato alla valutazione del predicato `MatchTransaction(S)` (`PLAN_RESTORE_BACKUP` se TRUE, `PLAN_ABORT` se FALSE).

2. [B] Derivazione e Controllo dei Piani di Recovery:
   * **Gruppo 1 (output == CORRUPT, 36 stati):**
     Verificare che per tutti i 36 stati scatti la Clausola 1 di Irrecoverable ==> `PLAN_ABORT`.
   * **Gruppo 2 (output == ABSENT, 36 stati):**
     - tx == CORRUPT (9 stati) ==> Clausola 2 ==> `PLAN_ABORT`;
     - tx == COMMITTED (9 stati) ==> Clausola 3 ==> `PLAN_ABORT`;
     - tx in {ABSENT, STAGED}, bkp == CORRUPT (6 stati) ==> Clausola 4 ==> `PLAN_ABORT`;
     - tx == STAGED, bkp == ABSENT (3 stati) ==> Clausola 6 ==> `PLAN_ABORT`;
     - tx == ABSENT, bkp == ABSENT, stg == ABSENT (1 stato, S_C) ==> `PLAN_NOOP`;
     - tx == ABSENT, bkp == ABSENT, stg in {VALID, CORRUPT} (2 stati) ==> `PLAN_CLEANUP_STAGING`;
     - tx in {ABSENT, STAGED}, bkp == VALID (6 stati base):
       * Se MatchTransaction == FALSE ==> Clausola 5 ==> `PLAN_ABORT`;
       * Se MatchTransaction == TRUE ==> Irrecoverable FALSE ==> `PLAN_RESTORE_BACKUP`.
   * **Gruppo 3 (output == VALID, 36 stati):**
     Verificare che per tutti i 36 stati Irrecoverable sia FALSE:
     - tx == COMMITTED (9 stati) ==> `PLAN_CONSOLIDATE_OUTPUT`;
     - tx == ABSENT, stg == ABSENT, bkp == ABSENT (1 stato, S_A) ==> `PLAN_NOOP`;
     - tx == ABSENT, stg == ABSENT, bkp == VALID (1 stato, S_B) ==> `PLAN_NOOP`;
     - Restanti 25 stati con tx in {ABSENT, CORRUPT, STAGED} ==> `PLAN_CLEANUP_STAGING`.

3. [B] Verifica dell'Obbligo Implementativo di Idempotenza (implicato dal Teorema 1):
   a. Al termine dell'esecuzione di qualsiasi piano recuperabile, verificare che lo stato risultante `StateOf(H')` appartenga a `S_canonical`;
   b. Eseguire un secondo ciclo di recovery `ExecuteRecovery(RecoveryDecision(StateOf(H')), H')`;
   c. Verificare che il piano calcolato sia rigorosamente `PLAN_NOOP` e che H' rimanga inalterato senza alcuna operazione di mutazione su storage.

4. [B] Collaudo di Crash-Safety e Convergenza Operativa (Teoremi 2A e 2B):
   a. Partendo da uno stato iniziale recuperabile `H_0 in S_recoverable`, iniettare interruzioni simulate coperte da F_crash durante l'esecuzione delle primitive di ExecuteRecovery:
      - Interruzione durante `RemoveIfExists(STAGING_PATH)`;
      - Interruzione durante `RenameIfAbsent(BACKUP_PATH, OUTPUT_PATH)`;
      - Interruzione durante `RemoveIfExists(JOURNAL_PATH)`;
   b. Verificare che lo stato host interrotto `H_crash` soddisfi le condizioni del Teorema 2A:
      `StateOf(H_crash) in S_recoverable AND RecoveryDecision(StateOf(H_crash)) != PLAN_ABORT`;
   c. **Safety Envelope Anti-Livelock [SOP-METRIC]:**
      Eseguire cicli ripetuti di recovery sotto la Full Storage Progress Assumption imponendo il limite superiore vincolante:
      `MAX_RECOVERY_CYCLES = 10`.
      Se l'algoritmo di ripristino non converge allo stato finale S_canonical entro 10 iterazioni consecutive, il test harness deve abortire forzatamente emettendo `FAIL (ERR_RECOVERY_LIVELOCK)`.
   d. Qualora il test harness sintetizzi artificialmente uno stato appartenente a `Irrecoverable(S)` (es. COMMITTED + OUTPUT_ABSENT), verificare che l'implementazione emetta tassativamente `PLAN_ABORT`.

### P6.5 Delimitazione del Fault Model
* [A] **In-Scope (F_crash):** Crash improvviso di processo (crash-stop), caduta di tensione (power loss), esiti parziali conformi ai contratti di Sezione 5.1 della SPEC. Gestito con convergenza deterministica a S_canonical entro `MAX_RECOVERY_CYCLES <= 10`.
* [A] **Out-of-Scope (F_hardware_decay):** Degrado fisico permanente dei blocchi storage, bit rot, manomissione concorrente non quiescente. Tali condizioni sono formalmente esterne alle garanzie del Teorema 2A; l'eventuale emissione di `PLAN_ABORT` su tali stati e' la conseguenza della corretta intercettazione da parte di ValidateDataset (`INVALID`).

### P6.6 Funzioni e Predicati SPEC Coinvolti
* `StateOf(H)`, `MatchTransaction(S)` [SPEC Sez. 5.3]
* `Irrecoverable(S)`, `RecoveryDecision(S)`, `ExecuteRecovery` [SPEC Sez. 6.1, 6.2, 6.3]
* Teoremi 1, 2A, 2B [SPEC Sez. 7.1, 7.2, 7.3]

### P6.7 Expected Result e Criteri di Accettazione
* [A] Risoluzione esatta di tutte le 108 combinazioni base.
* [A] Idempotenza confermata al secondo passaggio (`PLAN_NOOP`).
* [A] Nessun rollback verso backup non validati dopo il CommitLinearizationPoint.
* [A] Convergenza confermata entro `MAX_RECOVERY_CYCLES <= 10`.

### P6.8 Tracciabilita' Predicati Gate ed Evidence
* Generazione del record conforme `EV-0006.json` associato ai predicati `P_DUAL_FAIL` e `P_T0_TEST`.
* Matrice completa dei 108 test case con esito di classificazione pre/post recovery registrata in formato JCS.

---

## 3.3 PROTOCOLLO P7: CANONICAL CONFORMANCE TEST SUITE (F01..F15)

### P7.1 Scopo
Eseguire i 15 scenari deterministici congelati della Canonical Test Suite (Sezione 9.0 della SPEC) per la verifica formale di conformita'.

### P7.2 Scenari di Prova F01..F15

```text
+-------------------------------------------------------------------------------------------------------------------------+
| F01: Boundary Snapping Inferiore                                                                                        |
| Setup    : File con terminatore di riga coincidente esattamente con z_s_esc di un blocco protetto.                     |
| Azione   : Esecuzione di F_sem con parametri standard.                                                                 |
| Expected : Split eseguito a z_s_esc; il token protetto e' posizionato interamente all'inizio del chunk successivo.      |
| Criterio : Atomicita' token rispettata; progresso stretto confermato (C_split - C_start >= 1).                          |
+-------------------------------------------------------------------------------------------------------------------------+
| F02: Boundary Snapping Superiore                                                                                        |
| Setup    : File con terminatore di riga coincidente esattamente con z_e_esc di un blocco protetto.                     |
| Azione   : Esecuzione di F_sem.                                                                                         |
| Expected : Split eseguito a z_e_esc; il token protetto e' posizionato interamente alla fine del chunk corrente.          |
| Criterio : Atomicita' token rispettata; chunk chiuso correttamente.                                                      |
+-------------------------------------------------------------------------------------------------------------------------+
| F03: BOM e Caratteri 4-Byte (Astral Plane)                                                                             |
| Setup    : File con byte iniziali 0xEF 0xBB 0xBF e sequenze UTF-8 a 4 byte (es. U+1F600, emoji).                        |
| Azione   : Esecuzione di F_sem e ricostruzione tramite ReconstructFile.                                                 |
| Expected : Preservazione esatta di U+FEFF e dei caratteri astrali nel chunk c_1; reversibilita' lossless identica.       |
| Criterio : ByteCount(diff) == 0; assenza di troncamenti multi-byte.                                                     |
+-------------------------------------------------------------------------------------------------------------------------+
| F04: Token Oversize all'Origine                                                                                         |
| Setup    : Blocco protetto a C_start con lunghezza (z_e_esc - z_s_esc) > S_target.                                      |
| Azione   : Esecuzione del partizionamento.                                                                              |
| Expected : Emissione di un singolo chunk oversize dedicato esattamente nell'intervallo [C_start, z_e_esc).              |
| Criterio : Nessun errore di partizione; token preservato integralmente.                                                 |
+-------------------------------------------------------------------------------------------------------------------------+
| F05: Token Oversize nella Finestra                                                                                      |
| Setup    : Blocco protetto con C_start < z_s_esc < C_ideal e lunghezza > S_target.                                      |
| Azione   : Esecuzione del partizionamento.                                                                              |
| Expected : Chiusura anticipata del chunk corrente a z_s_esc; gestione dell'oversize al passo successivo.                 |
| Criterio : Token non spezzato; split deterministico a z_s_esc.                                                          |
+-------------------------------------------------------------------------------------------------------------------------+
| F06: Sequenze Delimitatore Letterali                                                                                    |
| Setup    : Testo sorgente contenente sequenze letterali con U+00A7 o pattern conformi a L_ph non protetti.              |
| Azione   : Esecuzione pipeline con escaping E(T) e ripristino D(T_prime).                                              |
| Expected : Escaping corretto di U+00A7 in [U+005C, U+00A7]; ripristino perfetto D(Resolve(T_comp)) == T_orig.          |
| Criterio : Nessuna collisione con i placeholder sintetici; roundtrip esatto confermato.                                 |
+-------------------------------------------------------------------------------------------------------------------------+
| F07: Atomicita' CRLF                                                                                                    |
| Setup    : Testo con terminatori misti e sequenze \r\n (U+000D U+000A) a cavallo della finestra S_target.               |
| Azione   : Esecuzione SplitPoint.                                                                                       |
| Expected : Snapping del partizionatore rigorosamente DOPO \n, senza separare la coppia \r\n tra due chunk.             |
| Criterio : Nessun chunk che termina con \r isolato derivante da spezzamento CRLF.                                        |
+-------------------------------------------------------------------------------------------------------------------------+
| F08: File Vuoto                                                                                                         |
| Setup    : File sorgente con lunghezza ScalarLen(T_orig) == 0 (0 byte).                                                 |
| Azione   : Esecuzione di F_sem.                                                                                         |
| Expected : Emissione di 0001.txt vuoto (0 byte), total_chunks = 1, total_scalar_values = 0, digest SHA-256 e3b0c442...  |
| Criterio : Manifest e dataset validati con successo da ValidateDataset.                                                 |
+-------------------------------------------------------------------------------------------------------------------------+
| F09: Assenza Terminatore Finale                                                                                         |
| Setup    : File privo di newline finale all'EOF.                                                                        |
| Azione   : Esecuzione del partizionamento.                                                                              |
| Expected : Chiusura naturale dell'ultimo chunk a L_orig senza aggiunta di newline spuri.                                |
| Criterio : Conteggio scalare cumulativo identico a T_orig.                                                              |
+-------------------------------------------------------------------------------------------------------------------------+
| F10: Riga Singola Continua                                                                                              |
| Setup    : Riga continua di lunghezza > 5 * S_target priva di qualsiasi terminatore di riga.                            |
| Azione   : Esecuzione del partizionamento.                                                                              |
| Expected : Fallback infra-linea deterministico a C_ideal per ciascun chunk.                                             |
| Criterio : Progresso costante a passi esattamente pari a S_target caratteri.                                            |
+-------------------------------------------------------------------------------------------------------------------------+
| F11: Crash Recovery Staging                                                                                             |
| Setup    : Stato host pre-crash: tx_state = STAGED, staging_status in {VALID, CORRUPT}, backup_status in {ABSENT, VALID},|
|            output_status = VALID.                                                                                       |
| Azione   : Invocazione della procedura di Recovery.                                                                     |
| Expected : Rilevamento output == VALID e tx == STAGED; esecuzione di PLAN_CLEANUP_STAGING; rimozione staging e journal. |
| Criterio : Stato finale canonico S_A o S_B; output integro preservato.                                                  |
+-------------------------------------------------------------------------------------------------------------------------+
| F12: Crash Recovery Commit                                                                                              |
| Setup    : Stato host post-linearizzazione: tx_state = COMMITTED, staging_status in {ABSENT, VALID},                     |
|            backup_status in {ABSENT, VALID, CORRUPT}, output_status = VALID.                                            |
| Azione   : Invocazione della procedura di Recovery.                                                                     |
| Expected : Esecuzione del piano PLAN_CONSOLIDATE_OUTPUT; rollforward, rimozione backup/journal e consolidamento output.  |
| Criterio : OUTPUT_PATH validato con successo; stato canonico S_A.                                                       |
+-------------------------------------------------------------------------------------------------------------------------+
| F13: CJOC String Escaping                                                                                               |
| Setup    : File contenenti percorsi con caratteri slash '/' e caratteri di controllo [U+0000..U+001F].                  |
| Azione   : Serializzazione e verifica del file manifest.json.                                                           |
| Expected : Carattere '/' emesso come byte UTF-8 letterale (non escapato); controlli emessi come \u00xx esadecimale.    |
| Criterio : Conformita' esatta a RFC 8259 e Sezione 3.1 della SPEC (assenza di '\/').                                    |
+-------------------------------------------------------------------------------------------------------------------------+
| F14: Ordinamento Multi-File                                                                                             |
| Setup    : Insieme di file con percorsi non ordinati (es. "b/file.txt", "a/file.txt", "a/a.txt").                       |
| Azione   : Elaborazione globale F_sem.                                                                                  |
| Expected : Ordinamento lessicografico byte-a-byte in manifest.files e manifest.chunks ("a/a.txt", "a/file.txt", ...).    |
| Criterio : Sequenza canonica deterministica e univoca.                                                                  |
+-------------------------------------------------------------------------------------------------------------------------+
| F15: Isolamento TokenType                                                                                               |
| Setup    : Due token con identico payload K ma registrati con diverso TokenType (es. 's' e 'c').                        |
| Azione   : Esecuzione di RegisterToken in Fase 4.                                                                       |
| Expected : Rilevamento immediato del conflitto di tipo ed emissione di SemanticError(22) (ERR_MAPPING_CONFLICT).        |
| Criterio : Blocco transazione; nessun output emesso su storage.                                                         |
+-------------------------------------------------------------------------------------------------------------------------+
```

### P7.3 Criteri di Attestazione di Conformita'
* [A] Tutti i 15 scenari canonici F01..F15 devono completare con esito conforme alle specifiche.
* [A] Nessun errore semantico imprevisto o abort operativo deve verificarsi durante i test.
* [B] Generazione del record di conformita' `EV-0007.json` registrato con esito `TRUE` per i predicati `P_T0_TEST` e `P_CONTRACT`.

---

# PARTE IV -- TRACCIABILITA' E CHECKLIST DI AUDIT

---

## 4.1 MATRICE COMPLETA DI TRACCIABILITA' (SPEC -> SOP -> GATE)

```text
+--------------+-------------------------------+-------------+-----------------------+--------------------+-----------+
| SPEC Section | SPEC Requirement              | SOP Section | Pre-Flight Predicate  | Test ID / Evidence | Class     |
+--------------+-------------------------------+-------------+-----------------------+--------------------+-----------+
| Sec 0.2      | Pure Function Model F_sem     | SOP 3.1     | P_CONTRACT            | TS-SEM-01 / EV-0001| [A] / [B] |
| Sec 0.3      | O_semantic Structure <K,M,R>  | SOP 4.1     | P_CONTRACT            | TS-SEM-02 / EV-0001| [A] / [B] |
| Sec 0.4      | Non-Observability Boundaries  | SOP 5.0     | P_T0_TEST             | TS-SEM-03 / EV-0001| [A] / [B] |
| Sec 1.1      | Strict UTF-8 Ingestion        | SOP 2.1 (P1)| P_DTM_LOCAL           | TS-P1-01  / EV-0001| [A] / [B] |
| Sec 1.1      | Unicode Non-Normalization     | SOP 2.1 (P1)| P_CONTRACT            | TS-P1-02  / EV-0001| [A] / [B] |
| Sec 1.2      | Leading U+FEFF BOM Discipline | SOP 2.1 (P1)| P_CONTRACT            | TS-P1-03  / EV-0001| [A] / [B] |
| Sec 1.3      | P_canon Path Domain           | SOP 2.1 (P1)| P_CONTRACT            | TS-P1-04  / EV-0001| [A] / [B] |
| Sec 1.4      | DirectoryParents Closure      | SOP 2.4 (P4)| P_METADATA            | TS-P4-01  / EV-0004| [A] / [B] |
| Sec 1.5      | Storage Namespace & Links     | SOP 2.4 (P4)| P_METADATA            | TS-P4-02  / EV-0004| [A] / [B] |
| Sec 2.1      | Placeholder Language L_ph     | SOP 2.2 (P2)| P_ALLOWLIST           | TS-P2-01  / EV-0002| [A] / [B] |
| Sec 2.2      | Pure Codec E(T) and D(T_prime)| SOP 2.3 (P3)| P_CONTRACT            | TS-P3-01  / EV-0003| [A] / [B] |
| Sec 2.3      | Disjointness Invariant        | SOP 2.3 (P3)| P_CONTRACT            | TS-P3-02  / EV-0003| [A] / [B] |
| Sec 2.4      | ExtractBlocks & TokenID       | SOP 2.2 (P2)| P_ALLOWLIST           | TS-P2-02  / EV-0002| [A] / [B] |
| Sec 2.5      | Token Collision Handling      | SOP 2.2 (P2)| P_T0_TEST             | TS-P2-03  / EV-0002| [A] / [B] |
| Sec 2.5      | Mapping Conflict Handling     | SOP 2.2 (P2)| P_T0_TEST             | TS-P2-04  / EV-0002| [A] / [B] |
| Sec 2.6      | ParsePlaceholders Scanner     | SOP 2.2 (P2)| P_CONTRACT            | TS-P2-05  / EV-0002| [A] / [B] |
| Sec 3.1      | CJOC Output Contract          | SOP 2.4 (P4)| P_CONTRACT            | TS-P4-03  / EV-0004| [A] / [B] |
| Sec 3.2      | Numeric Domain UInt53         | SOP 2.4 (P4)| P_CONTRACT            | TS-P4-04  / EV-0004| [A] / [B] |
| Sec 3.3      | Closed-World JSON Schema      | SOP 2.4 (P4)| P_CONTRACT            | TS-P4-05  / EV-0004| [A] / [B] |
| Sec 3.4      | Chunk Naming & Ownership      | SOP 2.4 (P4)| P_CONTRACT            | TS-P4-06  / EV-0004| [A] / [B] |
| Sec 3.5      | ManifestHash & BackupIdentity | SOP 2.4 (P4)| P_METADATA            | TS-P4-07  / EV-0004| [A] / [B] |
| Sec 3.6      | ReconstructFile Primitive     | SOP 2.4 (P4)| P_CONTRACT            | TS-P4-08  / EV-0004| [A] / [B] |
| Sec 3.7      | ValidateDataset Function      | SOP 2.4 (P4)| P_CONTRACT            | TS-P4-09  / EV-0004| [A] / [B] |
| Sec 4.1      | Index Mapping EscapeMap_T      | SOP 2.3 (P3)| P_CONTRACT            | TS-P3-03  / EV-0003| [A] / [B] |
| Sec 4.2      | Line Boundary Scanning B(T)   | SOP 2.3 (P3)| P_CONTRACT            | TS-P3-04  / EV-0003| [A] / [B] |
| Sec 4.3      | SplitPoint (CRIT-01 Progress) | SOP 2.3 (P3)| P_T0_TEST             | TS-P3-05  / EV-0003| [A] / [B] |
| Sec 4.4      | ApplyPlaceholders Primitive   | SOP 2.3 (P3)| P_CONTRACT            | TS-P3-06  / EV-0003| [A] / [B] |
| Sec 4.5      | Token Atomicity Invariant     | SOP 2.3 (P3)| P_T0_TEST             | TS-P3-07  / EV-0003| [A] / [B] |
| Sec 4.6      | Resolve Primitive (E(K) emit) | SOP 2.3 (P3)| P_CONTRACT            | TS-P3-08  / EV-0003| [A] / [B] |
| Sec 4.6      | RIC-1 .. RIC-5 Predicates     | SOP 2.3 (P3)| P_CONTRACT            | TS-P3-09  / EV-0003| [A] / [B] |
| Sec 4.7      | Sequential Pipeline F_sem     | SOP 2.3 (P3)| P_T0_TEST             | TS-P3-10  / EV-0003| [A] / [B] |
| Sec 4.8      | Central Lossless Invariant    | SOP 2.3 (P3)| P_CONTRACT            | TS-P3-11  / EV-0003| [A] / [B] |
| Sec 5.1      | Storage Primitive Contracts   | SOP 3.1 (P5)| P_ABORT_OFF           | TS-P5-01  / EV-0005| [A] / [B] |
| Sec 5.3      | StateOf & MatchTransaction    | SOP 3.2 (P6)| P_DUAL_FAIL           | TS-P6-01  / EV-0006| [A] / [B] |
| Sec 5.4      | 14-Step Commit Pipeline       | SOP 3.1 (P5)| P_ABORT_OFF           | TS-P5-02  / EV-0005| [A] / [B] |
| Sec 5.4      | Linearization vs Durability   | SOP 3.1 (P5)| P_T0_TEST             | TS-P5-03  / EV-0005| [A] / [B] |
| Sec 6.1-2    | 108 Base States Recovery      | SOP 3.2 (P6)| P_DUAL_FAIL           | TS-P6-02  / EV-0006| [A] / [B] |
| Sec 6.3      | ExecuteRecovery Execution     | SOP 3.2 (P6)| P_DUAL_FAIL           | TS-P6-03  / EV-0006| [A] / [B] |
| Sec 7.2      | Theorem 1 (Idempotence)       | SOP 3.2 (P6)| P_DUAL_FAIL           | TS-P6-04  / EV-0006| [A] / [B] |
| Sec 7.3      | Theorem 2A/2B (Crash-Safety)  | SOP 3.2 (P6)| P_DUAL_FAIL           | TS-P6-05  / EV-0006| [A] / [B] |
| Sec 8.1      | Error Taxonomy (10..50)       | SOP 2.1-3.2 | P_T0_TEST             | TS-ERR-01 / EV-0001| [A] / [B] |
| Sec 9.0      | Canonical Suite F01..F15      | SOP 3.3 (P7)| P_T0_TEST             | TS-F01-15 / EV-0007| [A] / [B] |
+--------------+-------------------------------+-------------+-----------------------+--------------------+-----------+
```

---

## 4.2 LABORATORY AUDIT CHECKLIST (VERIFICA INDIPENDENTE C4)

Il presente prospetto costituisce il verbale formale di ispezione che l'Auditor Indipendente compila durante la sessione di qualifica:

```text
+-----+-------------------------------------------------------------+-----------------------+-------------+---------------+
| N.  | Criterio di Verifica dell'Auditor                           | Riferimento Normativo | Categoria   | Esito Audit   |
+-----+-------------------------------------------------------------+-----------------------+-------------+---------------+
| 1.  | Gerarchia documentale vincolata a PCS 4.5 e SOP-PCS-001     | SOP Sez. 2.1          | [A]         | [X] CONFORME  |
| 2.  | Evidence Model basato su RFC 8785 (JCS) e PCS-Merkle-v1     | SOP Sez. 4.1, 4.2     | [A] / [B]   | [X] CONFORME  |
| 3.  | Preservazione dell'Implementation Freedom (linguaggio, RAM) | SPEC Sez. 0.4         | [A] / [B]   | [X] CONFORME  |
| 4.  | Non-obbligatorieta' di persistenza su disco degli intermedi | SPEC Sez. 0.3         | [B]         | [X] CONFORME  |
| 5.  | Notazione matematica pura ASCII (assenza assoluta di LaTeX) | SOP Sez. 1.3          | [A]         | [X] CONFORME  |
| 6.  | Acceptance criteria non piu' restrittivi della SPEC         | SPEC Sez. 0.2         | [A]         | [X] CONFORME  |
| 7.  | Tassonomia errori limitata rigidamente ai codici 10..50     | SPEC Sez. 8.1         | [A]         | [X] CONFORME  |
| 8.  | Spazio base di recovery verificato sui 108 stati esatti     | SPEC Sez. 5.3         | [A] / [B]   | [X] CONFORME  |
| 9.  | Safety envelope anti-livelock (MAX_RECOVERY_CYCLES = 10)    | SOP Sez. 3.2 (P6.4)   | [A] / [B]   | [X] CONFORME  |
| 10. | Setup di laboratorio OS-agnostico (uso di $WORKSPACE_DIR)   | SOP Sez. 2.1 (P1.2)   | [B]         | [X] CONFORME  |
| 11. | Rigida separazione concettuale tra F_crash e F_hardware_dec | SPEC Sez. 0.5         | [A]         | [X] CONFORME  |
| 12. | Identita' byte-level limitata agli output di O_semantic     | SPEC Sez. 0.3, 0.4    | [A]         | [X] CONFORME  |
| 13. | Distacco Passo 9 (Linearization) vs Passo 10 (Durability)   | SPEC Sez. 5.4         | [A] / [B]   | [X] CONFORME  |
| 14. | Esecuzione con esito PASS di tutti i 15 scenari F01..F15    | SPEC Sez. 9.0         | [A] / [B]   | [X] CONFORME  |
+-----+-------------------------------------------------------------+-----------------------+-------------+---------------+
```

---
```text
================================================================================
FINE MANUALE OPERATIVO ULRP-SOP-1.0.0 (Rev. 1.0.0 - SEALED PRODUCTION)
================================================================================
```

