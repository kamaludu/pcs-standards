```text
================================================================================
SPECIFICA TECNICA NORMATIVA: ULRP-EXT-SPEC-1.1.0
UNIVERSAL LLM SEMANTIC EXTENSION, ADAPTIVE TOKEN BUDGETING AND CONTEXT GOVERNANCE PROTOCOL
Estensione Normativa per Pipeline Preprocessing, Budgeting e Gabbia Generativa
================================================================================
Status    : APPROVED NORMATIVE EXTENSION (v1.1.0 - FROZEN STANDARD)
Reference : ULRP-SPEC-1.6.27 & Protocollo Colomba Serpente (PCS 4.5)
Scope     : Strictly Language-Agnostic, Runtime-Agnostic, OS-Agnostic, LLM-Agnostic
Supersedes: ULRP-EXT-SPEC-1.0.8, ULRP-EXT-SPEC-1.0.7, ULRP-EXT-SPEC-1.0.6,
            ULRP-EXT-SPEC-1.0.5, ULRP-EXT-SPEC-1.0.4, ULRP-EXT-SPEC-1.0.3,
            ULRP-EXT-SPEC-1.0.2, ULRP-EXT-SPEC-1.0.1, ULRP-EXT-SPEC-1.0.0
================================================================================
```

## 0. CONVENZIONI, GERARCHIA DI DIPENDENZA, ASSIOMATICA E AMBITO OSSERVABILE

### 0.1 Convenzioni Normative, Notazione e Operatori di Misura
Le parole chiave MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY e OPTIONAL nel presente documento devono essere interpretate conformemente a BCP 14 (RFC 2119 / RFC 8174) solo ed esclusivamente quando scritte in lettere maiuscole.
Tutte le formule matematiche e gli algoritmi adottano rigorosamente la notazione scalare ASCII pura priva di simboli tipografici non compresi nell'intervallo [U+0020..U+007E].

Per evitare qualsiasi ambiguita' tra byte, caratteri scalari, unita' di tokenizzazione e collezioni di record, il protocollo definisce i seguenti quattro operatori di misura normativi:

+-----------------------------+-----------------------+---------------------------------------------------------+
| OPERATORE DI MISURA         | SPAZIO DI RIFERIMENTO | DEFINIZIONE NORMATIVA ESATTA                            |
+-----------------------------+-----------------------+---------------------------------------------------------+
| ScalarLen(T)                | SIGMA*                | Numero esatto di Unicode Scalar Values nel testo T.     |
| ByteLenUTF8(T)              | SIGMA*                | Numero esatto di byte in EncodeStrictUTF8(T).           |
| TokenCost(T) / mu_tok(T)    | Integers_ge_0         | Costo astratto di tokenizzazione secondo il modello.    |
| Card(C)                     | Collezioni / Array    | Numero esatto di elementi cardinali nella collezione C. |
+-----------------------------+-----------------------+---------------------------------------------------------+

Tutti gli indici, intervalli e offset di partizionamento, selettori AST, mutazioni e documenti Delta sono espressi rigorosamente in ScalarLen (Unicode Scalar Values), salvo dove esplicitamente qualificato come ByteLenUTF8 per stringhe di testo o come conteggio esatto di byte su buffer binari grezzi.

### 0.2 Postulato di Dipendenza Unidirezionale e Subordinazione a ULRP 1.6.27 (REQ-EXT-001)
[NORMATIVE REQUIREMENT]
1. La presente specifica costituisce un'estensione modulare, facoltativa e formalmente subordinata a ULRP-SPEC-1.6.27.
2. ULRP-SPEC-1.6.27 costituisce il nucleo base di storage e partizionamento a dipendenze zero. Il kernel base non include alcuna dipendenza ne' riferimento verso la presente estensione.
3. La presente estensione dipende tassativamente dai contratti, invarianti e funzioni pure definiti in ULRP-SPEC-1.6.27:
   a. Dominio dei percorsi canonici P_canon e chiusura DirectoryParents (ULRP Sez. 1.3, 1.4);
   b. Funzioni pure di escaping e decodifica E(T) e D(T_prime) (ULRP Sez. 2.2);
   c. Linguaggio dei placeholder canonici L_ph e TokenID SHA-256 (ULRP Sez. 2.1, 2.4);
   d. Canonical JSON Output Contract (CJOC) (ULRP Sez. 3.1);
   e. Dominio numerico intero interoperabile UInt53 [0 .. 9007199254740991] e PosUInt53 [1 .. 9007199254740991] (ULRP Sez. 3.2);
   f. Funzione pura di partizionamento Partition e predicati RIC-1 .. RIC-5 (ULRP Sez. 4.3, 4.6);
   g. Pipeline transazionale a 14 passi e Recovery FSM sui 108 stati base (ULRP Sez. 5.4, 6.2).
4. Validazione di Storage e Reversibilita':
   Il kernel base ULRP 1.6.27 esegue ValidateDataset(H, path) per dataset in modalita' lossless. Quando l'estensione opera in modalita' lossy, la persistenza su storage include congiuntamente il dataset ridotto e il documento delta canonico archiviato nel namespace riservato STORAGE_ROOT/.pcs/delta.json, validati formalmente da ValidateDatasetExt(H, path) (Sez. 3.8).

### 0.3 Modello della Funzione Pura Estesa F_ext e Proiezione di Configurazione
[NORMATIVE REQUIREMENT]
La pipeline semantica dell'estensione e' formalizzata dalla funzione matematica pura:

    F_ext : D_raw x C_ext_raw -> ExtendedSemanticResult

dove:
* D_raw: Insieme finito di tuple grezze D_raw := { < P_raw, B_raw > } conforme a ULRP Sez. 0.2.
* C_ext_raw: Tupla dei parametri estesi:
    C_ext_raw := < B_context_raw, B_overhead_raw, U_budget_pct_raw, S_target_min_raw, S_target_max_raw, R_min_raw, mu_tok_raw, G_grammar_raw, Red_profile_raw, Z_policy_raw, Fallback_mode_raw >
  con B_context_raw in PosUInt53 [32 .. 9007199254740991], B_overhead_raw in UInt53 con B_overhead_raw < B_context_raw, U_budget_pct_raw intero in [50 .. 99] (Target Budget Utilization Percentage, default: 80), S_target_min_raw in PosUInt53 (Quality Target nominale non bloccante, default: 64), S_target_max_raw in PosUInt53 con S_target_max_raw >= S_target_min_raw, e R_min_raw intero in [1 .. 100] (default: 50).
* ExtendedSemanticResult: Unione disgiunta degli esiti:
    ExtendedSemanticResult := Success(O_ext_semantic) UNION SemanticError(e) UNION FallbackTriggered(F_sem_result)
  con O_ext_semantic := < K_compact, M_ext, R_ext, Delta_package, Prompt_envelope > e codice di errore esteso e in {10 .. 50} UNION {60 .. 80}.

Funzione Pura di Proiezione della Configurazione Base:
Quando l'estensione commuta su Fallback_mode == LOSSLESS, i parametri estesi C_ext_raw vengono proiettati deterministicamente nella tupla C_raw conforme a ULRP 1.6.27 Sez. 0.2 tramite la funzione pura:

    ProjectBaseConfig(C_ext_raw, Z_ext) -> C_raw:
      S_target_base = max(64, C_ext_raw.S_target_max_raw)
      R_min_base = C_ext_raw.R_min_raw
      Z_base = ProjectBaseZ(Z_ext)
      RETURN < S_target_base, R_min_base, Z_base >

Distinzione tra Output di Storage e Payload di Consumo In-Memory:
1. Storage Artifacts (Persistenza su Disco): Il manifest M_ext, la reverse map R_ext e i chunk persistiti contengono rigorosamente i placeholder canonici L_ph di lunghezza costante 70 scalari conformi a ULRP 1.6.27, preservando l'invarianza formale del repository.
2. In-Memory Generative Payload: Gli elementi K_compact e Prompt_envelope costituiscono strutture dati effimere in memoria, impiegate per la trasmissione verso modelli generativi esterni e la ricezione sicura di risposte conformi.

### 0.4 Allineamento Assiomatico con PCS 4.5
[NORMATIVE REQUIREMENT]
1. Assioma 4 (Closed-World Assumption): Ogni input sintattico, grammatica, parametro di budget o token compatto non provabile come appartenente alle allowlist definite nella presente specifica DEVE determinare il rifiuto immediato o la degradazione sicura.
2. Assioma 5 (Non-Equivalenza Contrattuale):
    ValidSchema(x) != SafeSemantic(x)
   La conformita' di un testo ridotto (lossy), di una grammatica AST o di un prompt generativo ai contratti di schema CJOC/CJDC attesta unicamente la correttezza strutturale della serializzazione e NON garantisce la correttezza semantica o l'assenza di allucinazioni cognitive nel modello generativo a valle.
3. Assioma 6 (Isolamento Strutturale): La presente specifica vieta binding dinamici o esecuzione di codice (tool-calling) a livello di preprocessing e confinamento prompt.
4. Assioma 7 (Prevalenza della Severita'): Il degrado dell'invariante di uguaglianza binaria (modalita' lossy) impone controlli di contenimento del danno (Delta document reversibile) indipendentemente dalla natura del testo elaborato.

### 0.5 Proprieta' NON Garantite dal Protocollo (Esclusioni Esplicite)
[NORMATIVE REQUIREMENT]
In conformita' all'epistemologia difensiva del PCS 4.5, la presente specifica dichiara formalmente che i seguenti aspetti rimangono ESTERNI alle garanzie fornite:
1. Correttezza Semantica e Veridicita' Fattuale: Nessun costrutto della presente specifica garantisce la veridicita' logica o la conformita' semantica dell'output prodotto da modelli LLM esterni.
2. Assenza di Allucinazioni Cognitive: Il layer di confinamento generativo garantisce esclusivamente la validita' sintattica e l'integrita' referenziale dei placeholder rispetto a TokenMap; non garantisce che il modello non scambi un token valido con un altro token valido o che non introduca affermazioni false nel testo libero.
3. Accuratezza Ontologica della Classificazione: L'isolamento di dati personali o chiavi crittografiche costituisce una garanzia condizionale di enforcement (Conditional Policy Enforcement Guarantee). La specifica garantisce l'isolamento dei blocchi contrassegnati da G_grammar, ma non garantisce la completezza o accuratezza dell'analizzatore sintattico o del modello di classificazione esterno.
4. Distinzione tra Integrita' Interna e Autenticita' Esterna: ValidateDatasetExt attesta la reversibilita' e consistenza crittografica interna del documento delta.json rispetto ai file locali. Non attesta ne' certifica l'identita' autoritativa del dataset rispetto a configurazioni esterne non ancorate a HostConfiguredTargetMeta (ULRP Sez. 5.3).

### 0.6 Normative Dependency Closure Table
[NORMATIVE REQUIREMENT]
Tutti i simboli utilizzati nella presente specifica appartengono tassativamente a una delle quattro classi formali:

```text
+-----------------------------+-----------+-----------------------------------+---------------------------------------------------+
| IDENTIFICATORE NORMATIVO    | CLASSE    | DEFINIZIONE / FONTE AUTORITATIVA  | CONTRATTO MATEMATICO / TIPO                       |
+-----------------------------+-----------+-----------------------------------+---------------------------------------------------+
| P_canon, DirectoryParents   | BASE      | ULRP-SPEC-1.6.27 Sez. 1.3-1.4 | Percorsi relativi portabili e chiusura directory  |
| E(T), D(T_prime)            | BASE      | ULRP-SPEC-1.6.27 Sez. 2.2     | E: SIGMA* -> SIGMA*, D: SIGMA* -> SIGMA*          |
| L_ph (70 scalari), TokenID  | BASE      | ULRP-SPEC-1.6.27 Sez. 2.1-2.4 | TokenID := HexLower(SHA256(EncodeStrictUTF8(K)))  |
| CJOC Contract               | BASE      | ULRP-SPEC-1.6.27 Sez. 3.1-3.3 | Serializzazione JSON canonica deterministica      |
| UInt53, PosUInt53           | BASE      | ULRP-SPEC-1.6.27 Sez. 3.2     | [0..9007199254740991], [1..9007199254740991]      |
| ChunkFileName               | BASE      | ULRP-SPEC-1.6.27 Sez. 3.4     | ChunkFileName(i) := PadZero4(i) + ".txt"          |
| ReconstructFile             | BASE      | ULRP-SPEC-1.6.27 Sez. 3.6     | Ricostruzione deterministica file da chunk        |
| ValidateDataset             | BASE      | ULRP-SPEC-1.6.27 Sez. 3.7     | Validazione 5-step dataset lossless               |
| F_sem                       | BASE      | ULRP-SPEC-1.6.27 Sez. 4.7     | Pipeline pura base D_raw x C_raw -> SemanticResult|
| Storage Primitives (Atomic) | BASE      | ULRP-SPEC-1.6.27 Sez. 5.1     | WriteAtomic, RemoveIfExists, RenameIfAbsent       |
| ContieneLinkOIndirezioni    | BASE      | ULRP-SPEC-1.6.27 Sez. 1.5     | Rilevamento symlink, junction e hard link > 1     |
| SemanticError(10..50)       | BASE      | ULRP-SPEC-1.6.27 Sez. 8.1     | Tassonomia codici di errore kernel base           |
+-----------------------------+-----------+-----------------------------------+---------------------------------------------------+
| F_ext, ProjectBaseConfig    | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 0.3  | Pipeline estesa e proiezione parametri            |
| F_select, Resolve           | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 1.3  | Selezione AST sweep-line deterministica           |
| MergeTagsHighestRank        | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 1.2  | Fusione conservativa privacy tag e token type     |
| F_filter (.pcs namespace)   | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 1.6  | Confinamento e riserva namespace STORAGE/.pcs/    |
| ActualCost, mu_tok, mu_tok_seg | EXT    | ULRP-EXT-SPEC-1.1.0 Sez. 2.1  | Costo isolato e inviluppo subsegmentale sound     |
| Pi_budget (Policy B)        | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 2.3  | Bisezione adattiva con riserva delta_join         |
| Lemma 2.3                   | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 2.3  | Monotonicita' di U_T e soundness del prompt       |
| Omega_pack, Omega_unpack    | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 2.4  | Framing multi-file length-prefixed in memoria     |
| ExtractHeaderField          | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 2.4  | Estrazione rigorosa campi header da testo frame   |
| SplitByNewline              | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 2.4  | Partizione deterministica linee (POSIX terminal)  |
| Phi_red, Psi_rec            | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.1  | Riduzione deterministica e ripristino reversibile |
| RuleSpec (Union Chiusa)     | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.1  | Sestupla a unione discriminata su match_pattern   |
| GenerateCandidates          | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.1  | Scansione deterministica candidati da RuleSpec    |
| ScanMaximalRun              | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.1  | Scansione sequenze contigue massimali             |
| AreMutationsDisjoint        | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.2  | Predicato disgiunzione con supporto span zero     |
| MaterializeLossy            | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.2  | Operatore puro di valutazione source-coordinate   |
| NormalizeMutations          | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.2  | Fusione canonica mutazioni contigue su T_orig     |
| ApplyComponent              | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.2  | Valutazione funzionale componente massimale       |
| BuildCanonicalDelta         | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.3  | Costruzione Delta con offset strettamente decresc.|
| Delta_mutation_impact_pct   | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.6  | Metrica di churn scalare esatta                   |
| ValidateRedProfile          | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.5  | Validazione closed-world schema del RedProfile    |
| NormalizeRedProfile         | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.5  | Ordinamento canonico rules per rule_id ASC        |
| CanonicalSerializeRedProfile| EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.5  | Serializzazione CJOC canonica del RedProfile      |
| ValidateDeltaSchema/Struct  | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.7  | Closed-world schema e bounds arithmetic Delta     |
| ValidateDeltaSemantics      | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.7  | Verifica hash e byte lengths UTF-8 esatte         |
| ValidateDatasetExt          | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 3.8  | Validazione estesa 6-passi (lossless e lossy)     |
| Domain_compact              | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 4.1  | Dominio canonico testi per compact encoding        |
| sigma_local, To/FromCompact | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 4.1  | Biiezione short-ID su L_compact                    |
| ParseFrameHeaderFields      | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 4.3  | Parsing chiuso header PCS_FRAME_V1 (Card == 7)    |
| StripPromptEnvelope         | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 4.3  | Context binding e byte isolation PCS_FRAME_V1     |
| F_resolve_gen               | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 4.5  | Risolutore generativo con preservazione backslash  |
| Dual Fallback FSM           | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 5.2  | Transizione atomica a F_sem con bonifica verificata|
| ScalarLen, ByteLenUTF8, Card| EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 0.1  | Operatori di misura scalare, binaria e insiemistica|
| SemanticError(60..80)       | EXT       | ULRP-EXT-SPEC-1.1.0 Sez. 5.1  | Tassonomia codici di errore estesi                |
+-----------------------------+-----------+-----------------------------------+---------------------------------------------------+
| TokenizerAdapter                   | EXTERNAL  | Runtime Host                      | MUST implementare RawEncodeCost e mu_tok_seg      |
| RawEncodeCost                      | EXTERNAL  | Runtime Host                      | RawEncodeCost(s) >= ActualCost(s)                 |
| ParseGrammarAdapter                | EXTERNAL  | Runtime Host (Tree-Sitter/ANTLR)  | MUST produrre AST deterministico con nodi esatti  |
| ContextStateReset                  | EXTERNAL  | Runtime Host                      | MUST garantire zero protocol-observable retention |
+-----------------------------+-----------+-----------------------------------+---------------------------------------------------+
```

---

# PARTE I -- UPSTREAM SEMANTIC EXTRACTION & COORDINATE GENERATION (Z)

---

## 1. SELETTORE ASTRATTO DI COORDINATE STRUTTURALI (F_select)

### 1.1 Modello di Grammatica Astratta G_grammar
[NORMATIVE REQUIREMENT]
Una grammatica astratta di selezione G_grammar e' definita come la quintupla:

    G_grammar := < V_nonterm, SIGMA_term, ProductionRules, SelectorRules, DisambiguationPolicy >

dove:
* V_nonterm: Insieme finito di simboli non terminali.
* SIGMA_term: Insieme dei terminali conforme allo spazio scalare Unicode SIGMA (ULRP Sez. 1.1).
* ProductionRules: Insieme finito di regole di derivazione context-free o ad automa a stati finiti deterministico.
* SelectorRules: Mappa finita che associa a specifici nodi di derivazione una tupla < tau, privacy_tag > con tau in {'s', 'b', 'h', 'c'} e privacy_tag in {"NONE", "PERSONAL_DATA", "SPECIAL_CATEGORY_DATA", "CRIMINAL_OFFENCE_DATA", "HARD_SECRET"}.
* DisambiguationPolicy: Criterio deterministico di risoluzione dei nodi sovrapposti in {"OUTERMOST_WINS", "INNERMOST_WINS"}.

### 1.2 Tassonomia della Riservatezza e Funzione MergeTagsHighestRank
[NORMATIVE REQUIREMENT]
La quadripartizione della riservatezza e la gerarchia dei tipi di token sono formalizzate dalle seguenti funzioni di rango:

    PrivacyRank(tag) -> Integer:
      CASE tag OF:
        "HARD_SECRET"            -> 4
        "CRIMINAL_OFFENCE_DATA"  -> 3
        "SPECIAL_CATEGORY_DATA"  -> 2
        "PERSONAL_DATA"          -> 1
        "NONE"                   -> 0
        OTHERWISE                -> 0

    TypeRank(tau) -> Integer:
      CASE tau OF:
        'h'       -> 3
        's'       -> 2
        'b'       -> 1
        'c'       -> 0
        OTHERWISE -> 0

    MergeTagsHighestRank(Cand_A, Cand_B) -> < tau_merged, tag_merged >:
      tau_merged = IF TypeRank(Cand_A.tau) >= TypeRank(Cand_B.tau) THEN Cand_A.tau ELSE Cand_B.tau
      tag_merged = IF PrivacyRank(Cand_A.tag) >= PrivacyRank(Cand_B.tag) THEN Cand_A.tag ELSE Cand_B.tag
      RETURN < tau_merged, tag_merged >

### 1.3 Ordinamento Canonico e Algoritmo di Risoluzione Disgiunta Resolve
[NORMATIVE REQUIREMENT]
Dati i blocchi candidati generati dall'AST, l'algoritmo Resolve elimina qualsiasi ciclo di ordinamento strutturando la selezione in due passate deterministiche: unificazione per coordinate canoniche e scansione topologica a sweep-line.

1. Ordinamento Canonico delle Coordinate (<_canonical):
    A <_canonical B <==> (A.z_s < B.z_s) OR (A.z_s == B.z_s AND A.z_e < B.z_e)

2. Algoritmo Deterministico Resolve(Z_raw, Policy):

    Resolve(Z_raw, Policy) -> Sequence(Block):
      (* Passo 1: Fusione a Rango Massimo delle Coordinate Identiche *)
      MappaCoord = EmptyMap()
      Per ciascun B in Z_raw:
        chiave = < B.z_s, B.z_e >
        IF chiave NOT IN keys(MappaCoord):
          MappaCoord[chiave] = < B.tau, B.tag >
        ELSE:
          MappaCoord[chiave] = MergeTagsHighestRank(MappaCoord[chiave], < B.tau, B.tag >)

      Z_unique = [ < MappaCoord[k].tau, [k.z_s, k.z_e), MappaCoord[k].tag > | k in keys(MappaCoord) ]

      (* Passo 2: Scansione Deterministica secondo la Policy *)
      IF Policy == "OUTERMOST_WINS":
        Ordina Z_unique:
          A <_outer B <==> (A.z_s < B.z_s) OR (A.z_s == B.z_s AND A.z_e > B.z_e)
        
        Z_selected = ()
        active = NULL
        Per ciascun C in Z_unique:
          IF active == NULL:
            active = C
          ELSE:
            IF C.z_s >= active.z_e:
              Z_selected.append(active)
              active = C
            ELSE:
              CONTINUE
        IF active != NULL:
          Z_selected.append(active)

      ELSE (* Policy == "INNERMOST_WINS" *):
        Ordina Z_unique secondo <_canonical

        Z_selected = ()
        Per ciascun C in Z_unique:
          IF Card(Z_selected) == 0:
            Z_selected.append(C)
          ELSE:
            prev = Z_selected.last()
            IF C.z_s >= prev.z_e:
              Z_selected.append(C)
            ELSE IF (prev.z_s <= C.z_s AND C.z_e <= prev.z_e):
              Z_selected.pop_last()
              Z_selected.append(C)
            ELSE:
              CONTINUE

      (* Passo 3: Ordinamento Canonico Finale *)
      Ordina Z_selected secondo <_canonical
      RETURN Z_selected

### 1.4 Algoritmo F_select e Invariante di Disgiunzione
[NORMATIVE REQUIREMENT]
    F_select(T, G_grammar) -> Result(Z_ext, ErrorCode):
      IF ScalarLen(T) == 0:
        RETURN Success(EMPTY_SET)
      AST = ParseGrammarAdapter(T, G_grammar)
      IF AST == PARSE_FAILED:
        RETURN SemanticError(61)                   [ERR_GRAMMAR_SELECTOR_FAILURE]
      
      Z_candidates = ()
      Per ciascun nodo N in AST per cui SelectorRules(N.symbol) != NULL:
        < tau, tag > = SelectorRules(N.symbol)
        z_s = N.start_scalar_offset
        z_e = N.end_scalar_offset
        IF z_s < 0 OR z_e > ScalarLen(T) OR z_s >= z_e:
          RETURN SemanticError(61)                 [ERR_GRAMMAR_SELECTOR_FAILURE]
        Z_candidates = Z_candidates + ( < tau, [z_s, z_e), tag > )
      
      IF Card(Z_candidates) == 0:
        RETURN Success(EMPTY_SET)

      Z_ext = Resolve(Z_candidates, G_grammar.DisambiguationPolicy)
      RETURN Success(Z_ext)

    ProjectBaseZ(Z_ext) -> Z_base:
      Z_base = EMPTY_SET
      Per ciascun < tau, [z_s, z_e), tag > in Z_ext:
        Z_base = Z_base UNION { < tau, [z_s, z_e) > }
      RETURN Z_base

[STRUCTURAL INVARIANT]
Invariante di Disgiunzione Assoluta:
Per ogni Z_ext restituito con Success da F_select:
    FORALL B_1, B_2 in Z_ext: (B_1 != B_2 => (B_1.z_e <= B_2.z_s OR B_2.z_e <= B_1.z_s))
Inoltre, ProjectBaseZ(Z_ext) soddisfa rigorosamente IsValidZ(ProjectBaseZ(Z_ext)) == TRUE (ULRP Sez. 4.7).

### 1.5 Policy di Isolamento Secret e Privacy (Conditional Policy Enforcement)
[NORMATIVE REQUIREMENT]
1. Definizione delle Categorie:
   * PERSONAL_DATA: Dati personali conformi all'Art. 4(1) GDPR;
   * SPECIAL_CATEGORY_DATA: Categorie particolari di dati personali conformi all'Art. 9 GDPR;
   * CRIMINAL_OFFENCE_DATA: Dati relativi a condanne penali e reati conformi all'Art. 10 GDPR;
   * HARD_SECRET: Categoria tecnica della presente specifica indicante chiavi crittografiche private, credenziali API, token bearer e segreti operativi.
2. Invariante di Trattamento Condizionale:
   Sotto la condizione che G_grammar assegni a un blocco un tag in {"HARD_SECRET", "CRIMINAL_OFFENCE_DATA", "SPECIAL_CATEGORY_DATA"}, la pipeline semantica GARANTISCE che:
   a. Il blocco non subisce alcuna operazione di riduzione lossy (Sez. 3);
   b. Il blocco non viene esposto in chiaro nei prompt generativi (Sez. 4);
   c. Il tentativo di alterare o esporre un blocco protetto genera tassativamente SemanticError(62) (ERR_PRIVACY_POLICY_VIOLATION).

### 1.6 Confinamento del Namespace Riservato .pcs/ e Filtro Percorsi (F_filter)
[NORMATIVE REQUIREMENT]
1. Riserva del Namespace .pcs/: Qualsiasi percorso canonico P in P_canon il cui primo segmento sia ".pcs" (es. ".pcs/delta.json", ".pcs/sub/file.txt") e' riservato all'infrastruttura dell'estensione e MUST NOT essere utilizzato per file utente in D_raw.
2. Filtro Percorsi:

    F_filter(D_raw, PathFilterRules) -> Result(D_filtered_raw, ErrorCode):
      D_out = EMPTY_SET
      Per ciascun < P_j, B_j > in D_raw:
        IF P_j NOT IN P_canon:
          RETURN SemanticError(11)                  [ERR_INVALID_PATH]
        IF P_j == ".pcs" OR StartsWith(P_j, ".pcs/"):
          RETURN SemanticError(11)                  [ERR_INVALID_PATH / RESERVED_SYSTEM_NAMESPACE]
        IF PathMatchesDenylist(P_j, PathFilterRules.denylist):
          CONTINUE
        IF PathFilterRules.allowlist != EMPTY_SET AND NOT PathMatchesAllowlist(P_j, PathFilterRules.allowlist):
          CONTINUE
        D_out = D_out UNION { < P_j, B_j > }
      IF D_out == EMPTY_SET:
        RETURN SemanticError(11)                    [ERR_INVALID_PATH / EMPTY_DATASET]
      RETURN Success(D_out)

---

# PARTE II -- ABSTRACT TOKEN METRIC & DYNAMIC CONTEXT BUDGETING

---

## 2. MISURA DEL COSTO DEI SIMBOLI (mu_tok) E BUDGETING (Pi_budget)

### 2.1 Assiomatica della Misura Astratta dei Token (mu_tok, mu_tok_seg)
[NORMATIVE REQUIREMENT]
Una funzione di misura del costo di tokenizzazione e' un operatore matematico puro:

    mu_tok : SIGMA* -> Integers_ge_0

soddisfacente i seguenti tre assiomi formali per ogni sequenza di caratteri scalari Unicode A, B in SIGMA*:

1. Assioma di Non-Negativita' e Nullita' della Stringa Vuota:
    mu_tok("") == 0
    FORALL T in SIGMA* : (ScalarLen(T) >= 1 => mu_tok(T) >= 1)

2. Assioma di Monotonia sull'Estensione (Prefix Monotonicity):
    FORALL A, B in SIGMA* : mu_tok(A) <= mu_tok(A + B)

3. Assioma di Sub-Additivita' a Giunzione Limitata (Bounded Sub-Additivity):
   Esiste una costante intera contrattuale delta_join in [0, 4] tale che:
    FORALL A, B in SIGMA* : mu_tok(A + B) <= (mu_tok(A) + mu_tok(B) + delta_join)
    FORALL A, B in SIGMA* : (mu_tok(A + B) + delta_join) >= (mu_tok(A) + mu_tok(B))

Qualsiasi funzione di costo o adapter che violi uno di questi tre assiomi DEVE essere rigettato con SemanticError(60) (ERR_TOKEN_BUDGET_OVERFLOW).

### 2.2 Contratto dell'Inviluppo di Segmento mu_tok_seg e Classi Adapter
[NORMATIVE REQUIREMENT]
La funzione pura di inviluppo superiore conservativo mu_tok_seg opera sul dominio valido D_valid:

    D_valid := { (T, k, S) in SIGMA* x UInt53 x UInt53 | 0 <= k <= ScalarLen(T) AND 0 <= S <= (ScalarLen(T) - k) }
    mu_tok_seg : D_valid -> UInt53

L'Host Adapter e' conforme se e solo se garantisce i due contratti normativi:
1. Upper-Bound Soundness:
    FORALL (T, k, S) in D_valid : ActualCost(T[k : k + S]) <= mu_tok_seg(T, k, S)
2. Bounded Subsegment Monotonicity:
    FORALL [a, b) SUBSET_OF [c, d) SUBSET_OF [0, ScalarLen(T)] :
      mu_tok_seg(T, a, b - a) <= mu_tok_seg(T, c, d - c)

Classificazione delle Realizzazioni dell'Adapter:
* Classe A (Inviluppo Analitico Lineare): mu_tok_seg(T, k, S) := ceil(S * MaxTokensPerScalar) con MaxTokensPerScalar in PosUInt53 certificato formalmente per il tokenizer.
* Classe B (Inviluppo Massimale Costruttivo): mu_tok_seg(T, k, S) := max { RawEncodeCost(T[a : b]) | k <= a <= b <= k + S } con RawEncodeCost("") == 0 e ActualCost(s) <= RawEncodeCost(s).
* Classe C (Profilo Certificato di Bounding): Adapter host verificato e certificato nel deployment profile.

### 2.3 Algoritmo Pi_budget ad Efficienza Prefissa (Policy B - Quality Target)
[NORMATIVE REQUIREMENT]
Dato il testo escapato T_esc in SIGMA* (L_esc = ScalarLen(T_esc)), la capacita' totale di contesto B_context, l'overhead stimato B_overhead, la costante certificata delta_join in [0, 4], la percentuale U_budget_pct in [50 .. 99], e i target S_target_min, S_target_max:

    Pi_budget(T_esc, B_context, B_overhead, U_budget_pct, S_target_min, S_target_max, mu_tok_seg, delta_join) -> Result(UInt53, ErrorCode):
      L_esc = ScalarLen(T_esc)
      IF L_esc == 0:
        RETURN Success(0)

      (* 1. Calcolo del budget massimo residuo con riserva esplicita di delta_join *)
      IF B_context <= (B_overhead + delta_join):
        RETURN SemanticError(60)                    [ERR_TOKEN_BUDGET_OVERFLOW]
      B_chunk_max = B_context - B_overhead - delta_join
      IF B_chunk_max <= 0:
        RETURN SemanticError(60)                    [ERR_TOKEN_BUDGET_OVERFLOW]

      (* 2. Calcolo Overflow-Safe di B_effective in pura aritmetica UInt53 *)
      Q = floor(B_chunk_max / 100)
      R = B_chunk_max mod 100
      B_effective = (U_budget_pct * Q) + floor((U_budget_pct * R) / 100)
      IF B_effective <= 0:
        RETURN SemanticError(60)                    [ERR_TOKEN_BUDGET_OVERFLOW]

      (* 3. Valutazione sentinella sul testo completo *)
      IF L_esc <= S_target_max:
        IF mu_tok_seg(T_esc, 0, L_esc) <= B_effective:
          RETURN Success(L_esc)

      (* 4. Ricerca Dicotomica dell'ottimo in [1 .. min(L_esc, S_target_max)] *)
      S_low = 1
      S_high = min(L_esc, S_target_max)
      S_optimal = 0

      Mentre S_low <= S_high:
        S_mid = floor((S_low + S_high) / 2)
        
        (* Valutazione della funzione inviluppo U_T(S_mid) *)
        max_bound = 0
        Per k da 0 a (L_esc - S_mid):
          cost_k = mu_tok_seg(T_esc, k, S_mid)
          IF cost_k > max_bound:
            max_bound = cost_k

        IF max_bound <= B_effective:
          S_optimal = S_mid
          S_low = S_mid + 1
        ELSE:
          S_high = S_mid - 1

      (* 5. Risoluzione della Policy B (Quality Target con Fallback Proporzionale) *)
      IF S_optimal == 0:
        RETURN SemanticError(60)                    [ERR_TOKEN_BUDGET_OVERFLOW]

      RETURN Success(S_optimal)

[STRUCTURAL INVARIANT]
Lemma 2.3 (Monotonicita' di U_T(S) e Soundness del Prompt Composto):
1. Monotonicita': Per l'Assioma di Monotonia Subsegmentale di mu_tok_seg, per ogni 1 <= S_1 <= S_2 <= L_esc si ha U_T(S_1) <= U_T(S_2). Pertanto Feasible(S_2) == TRUE implica Feasible(S_1) == TRUE.
2. Soundness: Sia P_full = Overhead + c_i. Per l'Assioma 3 di mu_tok e la riserva esatta di delta_join:
    mu_tok(P_full) <= mu_tok(Overhead) + mu_tok(c_i) + delta_join
                   <= B_overhead + B_chunk_max + delta_join = B_context
Il prompt generativo completo composto non eccede mai la capacita' fisica B_context.

### 2.4 Impacchettamento Length-Prefixed Epimero in Memoria (Omega_pack, Omega_unpack)
[NORMATIVE REQUIREMENT]
La funzione SplitByNewline suddivide deterministicamente un testo scalare T interpretando U+000A ('\n') come terminatore canonico di record:

    SplitByNewline(T) -> Sequence(String):
      lines = ()
      curr = ""
      Per ciascun c in T:
        IF c == U+000A:
          lines.append(curr)
          curr = ""
        ELSE IF c != U+000D:
          curr = curr + c
      IF ScalarLen(curr) > 0:
        lines.append(curr)
      RETURN lines

Omega_pack opera esclusivamente in memoria adottando il framing strutturato length-prefixed:

    Omega_pack( ( < P_1, T_prompt_1 >, ..., < P_M, T_prompt_M > ) ) -> String:
      V_out = ""
      Per j da 1 a M:
        P_bytes = EncodeStrictUTF8(T_prompt_j)
        N_bytes = ByteLenUTF8(T_prompt_j)
        Header_j = "<<<PCS_VIRTUAL_FILE_V1>>>\nPATH:" + P_j + "\nPAYLOAD_BYTE_COUNT:" + ToString(N_bytes) + "\n<<<BEGIN_VIRTUAL_PAYLOAD>>>\n"
        Footer_j = "\n<<<END_VIRTUAL_PAYLOAD>>>\n"
        V_out = V_out + Header_j + T_prompt_j + Footer_j
      RETURN V_out

    ExtractHeaderField(header_text, field_name) -> Result(String, ErrorCode):
      target_prefix = field_name + ":"
      lines = SplitByNewline(header_text)
      matched_value = NULL
      Per ciascuna line in lines:
        IF StartsWith(line, target_prefix):
          IF matched_value != NULL:
            RETURN SemanticError(74)                [ERR_PROMPT_ENVELOPE_BREACH]
          val = Substring(line, ScalarLen(target_prefix), ScalarLen(line))
          IF ScalarLen(val) > 0 AND val[0] == U+0020:
            val = Substring(val, 1, ScalarLen(val))
          matched_value = val
      IF matched_value == NULL:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      RETURN Success(matched_value)

    Omega_unpack(V_packed) -> Result( Sequence( < String, String > ), ErrorCode ):
      RawBytes = EncodeStrictUTF8(V_packed)
      result = ()
      curr = 0
      L_bytes = ByteCount(RawBytes)
      
      Mentre curr < L_bytes:
        h_tag = "<<<PCS_VIRTUAL_FILE_V1>>>\n"
        h_start = FindByteSubstring(RawBytes, h_tag, curr)
        IF h_start == -1:
          BREAK
        IF h_start != curr:
          RETURN SemanticError(74)                  [ERR_PROMPT_ENVELOPE_BREACH]
        
        p_marker = "\n<<<BEGIN_VIRTUAL_PAYLOAD>>>\n"
        p_pos = FindByteSubstring(RawBytes, p_marker, curr)
        IF p_pos == -1:
          RETURN SemanticError(74)                  [ERR_PROMPT_ENVELOPE_BREACH]
        
        header_bytes = RawBytes[curr : p_pos]
        IF NOT IsValidStrictUTF8(header_bytes):
          RETURN SemanticError(74)                  [ERR_PROMPT_ENVELOPE_BREACH]
        header_text = DecodeStrictUTF8(header_bytes)
        
        path_res = ExtractHeaderField(header_text, "PATH")
        IF path_res == SemanticError(e): RETURN SemanticError(e)
        p_path = path_res.value

        count_res = ExtractHeaderField(header_text, "PAYLOAD_BYTE_COUNT")
        IF count_res == SemanticError(e): RETURN SemanticError(e)
        IF NOT IsValidDigits(count_res.value): RETURN SemanticError(74)
        N_bytes = ParseUInt53(count_res.value)
        
        payload_start = p_pos + ByteCount(p_marker)
        IF payload_start > L_bytes:
          RETURN SemanticError(74)                  [ERR_PROMPT_ENVELOPE_BREACH]
        IF N_bytes > (L_bytes - payload_start):
          RETURN SemanticError(74)                  [ERR_PROMPT_ENVELOPE_BREACH]
        
        file_bytes = RawBytes[ payload_start : payload_start + N_bytes ]
        footer_expected = "\n<<<END_VIRTUAL_PAYLOAD>>>\n"
        footer_start = payload_start + N_bytes
        IF (footer_start + ByteCount(footer_expected)) > L_bytes:
          RETURN SemanticError(74)                  [ERR_PROMPT_ENVELOPE_BREACH]
        IF RawBytes[ footer_start : footer_start + ByteCount(footer_expected) ] != footer_expected:
          RETURN SemanticError(74)                  [ERR_PROMPT_ENVELOPE_BREACH]
        
        IF NOT IsValidStrictUTF8(file_bytes):
          RETURN SemanticError(74)                  [ERR_PROMPT_ENVELOPE_BREACH]
        file_content = DecodeStrictUTF8(file_bytes)
        result = result + ( < p_path, file_content > )
        curr = footer_start + ByteCount(footer_expected)

      RETURN Success(result)

---

# PARTE III -- CONTROLLED LOSSY REDUCTION & MULTI-FILE REVERSIBLE DELTA ALGEBRA

---

## 3. ALGEBRA DI RIDUZIONE LOSSY CON DELTA MULTI-FILE (Phi_red, Psi_rec)

### 3.1 Morfismo di Riduzione (Phi_red) e Pattern Language PCS-RED-PAT
[NORMATIVE REQUIREMENT]
La compressione lossy controllata associa a ciascun file originale T_orig in SIGMA* una tupla < T_lossy, Delta_file >:

    Phi_red : SIGMA* x RedProfile -> Result( < String, SingleFileDelta >, ErrorCode )

Struttura Chiusa di RuleSpec ad Unione Discriminata:
    RuleSpec := < rule_id, rule_priority, match_type, match_pattern, replacement_type, replacement_literal >
dove:
* rule_id: PosUInt53 univoco all'interno del profilo.
* rule_priority: UInt53.
* match_type in {"EXACT_LITERAL", "DELIMITED_COMMENT", "WHITESPACE_RUN", "NEWLINE_RUN"}.
* match_pattern e' rigidamente vincolato dal discriminatore match_type:
    CASE match_type OF:
      "EXACT_LITERAL":     match_pattern in SIGMA+
      "DELIMITED_COMMENT": match_pattern := < start_delim, end_delim > con start_delim in SIGMA+, end_delim in SIGMA+
      "WHITESPACE_RUN":    match_pattern in PosUInt53
      "NEWLINE_RUN":       match_pattern in PosUInt53
* replacement_type in {"EMIT_EMPTY", "EMIT_SINGLE_SPACE", "EMIT_SINGLE_NEWLINE", "EMIT_LITERAL"}.
* replacement_literal: in SIGMA+ se replacement_type == "EMIT_LITERAL", altrimenti esattamente "".

Funzioni di Proiezione Rigorosa su RuleSpec:
    PatternLiteral(Rule) := Rule.match_pattern
    StartDelim(Rule)     := Rule.match_pattern.start_delim
    EndDelim(Rule)       := Rule.match_pattern.end_delim
    MinLength(Rule)      := Rule.match_pattern

Algoritmo di Scansione Deterministica GenerateCandidates:
```text
GenerateCandidates(T_orig, RedProfile) -> Sequence(Candidate):
  RawList = ()
  RulesSorted = Ordina RedProfile.rules:
                Primario: rule_priority decrescente;
                Secondario: rule_id crescente.

  Per ciascuna Rule in RulesSorted:
    matches = ExecuteDeterministicScan(T_orig, Rule)
    Per ciascun m in matches:
      syn_text = ComputeReplacement(Rule)
      IF m.z_s == m.z_e AND ScalarLen(syn_text) > 0:
        RawList.append( < [m.z_s, m.z_e), "INSERT", syn_text, Rule.rule_priority, Rule.rule_id > )
      ELSE IF m.z_s < m.z_e AND ScalarLen(syn_text) == 0:
        RawList.append( < [m.z_s, m.z_e), "DELETE", "", Rule.rule_priority, Rule.rule_id > )
      ELSE IF m.z_s < m.z_e AND ScalarLen(syn_text) > 0:
        IF T_orig[ m.z_s : m.z_e ] != syn_text:
          RawList.append( < [m.z_s, m.z_e), "REPLACE", syn_text, Rule.rule_priority, Rule.rule_id > )

  RETURN RawList

ComputeReplacement(Rule) -> String:
  CASE Rule.replacement_type OF:
    "EMIT_EMPTY":          RETURN ""
    "EMIT_SINGLE_SPACE":   RETURN "\u0020"
    "EMIT_SINGLE_NEWLINE": RETURN "\u000A"
    "EMIT_LITERAL":        RETURN Rule.replacement_literal

ExecuteDeterministicScan(T, Rule) -> Sequence(Match):
  matches = ()
  curr = 0
  L = ScalarLen(T)
  
  Mentre curr < L:
    CASE Rule.match_type OF:
      "EXACT_LITERAL":
        pos = FindSubstring(T, PatternLiteral(Rule), curr)
        IF pos == -1:
          BREAK
        m_len = ScalarLen(PatternLiteral(Rule))
        matches.append( < [pos, pos + m_len), Rule.rule_id > )
        curr = pos + m_len

      "DELIMITED_COMMENT":
        start_pos = FindSubstring(T, StartDelim(Rule), curr)
        IF start_pos == -1:
          BREAK
        search_from = start_pos + ScalarLen(StartDelim(Rule))
        end_pos = FindSubstring(T, EndDelim(Rule), search_from)
        IF end_pos == -1:
          curr = search_from
        ELSE:
          m_len = (end_pos + ScalarLen(EndDelim(Rule))) - start_pos
          matches.append( < [start_pos, start_pos + m_len), Rule.rule_id > )
          curr = start_pos + m_len

      "WHITESPACE_RUN":
        < found, start_pos, end_pos > = ScanMaximalRun(T, curr, { U+0009, U+0020 }, MinLength(Rule))
        IF NOT found:
          BREAK
        matches.append( < [start_pos, end_pos), Rule.rule_id > )
        curr = end_pos

      "NEWLINE_RUN":
        < found, start_pos, end_pos > = ScanMaximalRun(T, curr, { U+000A, U+000D }, MinLength(Rule))
        IF NOT found:
          BREAK
        matches.append( < [start_pos, end_pos), Rule.rule_id > )
        curr = end_pos

  RETURN matches

ScanMaximalRun(T, curr, CharSet, min_length) -> < Boolean, Integer, Integer >:
  L = ScalarLen(T)
  idx = curr
  Mentre idx < L:
    Mentre idx < L AND T[idx] NOT IN CharSet:
      idx = idx + 1
    IF idx >= L:
      RETURN < FALSE, -1, -1 >
    start_pos = idx
    Mentre idx < L AND T[idx] IN CharSet:
      idx = idx + 1
    end_pos = idx
    run_len = end_pos - start_pos
    IF run_len >= min_length:
      RETURN < TRUE, start_pos, end_pos >
  RETURN < FALSE, -1, -1 >
```

### 3.2 Selezione Greedy, Normalizzazione e Preservazione Semantica
[NORMATIVE REQUIREMENT]
1. Relazione d'Ordine di Selezione (prec_select / prec_mut):
    A prec_select B <==>
      (A.z_s < B.z_s) OR
      (A.z_s == B.z_s AND (A.z_e - A.z_s) > (B.z_e - B.z_s)) OR
      (A.z_s == B.z_s AND (A.z_e - A.z_s) == (B.z_e - B.z_s) AND A.rule_priority > B.rule_priority) OR
      (A.z_s == B.z_s AND (A.z_e - A.z_s) == (B.z_e - B.z_s) AND A.rule_priority == B.rule_priority AND A.rule_id < B.rule_id) OR
      (A.z_s == B.z_s AND (A.z_e - A.z_s) == (B.z_e - B.z_s) AND A.rule_priority == B.rule_priority AND A.rule_id == B.rule_id AND CompareLexicographic(A.synthetic_text, B.synthetic_text) < 0)

2. Selezione Greedy Massimale Non-Sovrapposta:
```text
SelectGreedyMaximalNonOverlapping(CandidatesSorted) -> Sequence(Candidate):
  Selected = ()
  Per ciascun C in CandidatesSorted (in ordine prec_select crescente):
    conflict = FALSE
    Per ciascun S in Selected:
      IF NOT AreMutationsDisjoint(S, C):
        conflict = TRUE
        BREAK
    IF NOT conflict:
      Selected.append(C)
  Ordina Selected secondo prec_emit:
    A prec_emit B <==> (A.z_s < B.z_s) OR (A.z_s == B.z_s AND A.z_e < B.z_e)
  RETURN Selected

AreMutationsDisjoint(A, B) -> Boolean:
  IF (A.z_s < A.z_e) AND (B.z_s < B.z_e):
    RETURN (A.z_e <= B.z_s) OR (B.z_e <= A.z_s)
  ELSE IF (A.z_s < A.z_e) AND (B.z_s == B.z_e):
    RETURN (B.z_s <= A.z_s) OR (B.z_s >= A.z_e)
  ELSE IF (A.z_s == A.z_e) AND (B.z_s < B.z_e):
    RETURN (A.z_s <= B.z_s) OR (A.z_s >= B.z_e)
  ELSE:
    RETURN (A.z_s != B.z_s)
```

3. Algoritmo di Normalizzazione Funzionale NormalizeMutations:
```text
NormalizeMutations(SelectedMutations, T_orig) -> Sequence(CanonicalMutation):
  CanonicalList = ()
  Componenti = PartizionaInComponentiConnesseMassimali(SelectedMutations)

  Per ciascuna comp = (C_1, ..., C_k) in Componenti:
    a = C_1.z_s
    b = C_k.z_e
    orig_span = T_orig[ a : b ]

    replacement_text = ApplyComponent(orig_span, comp, a)

    IF a == b:
      IF replacement_text != "":
        CanonicalList.append( < [a, a), "INSERT", replacement_text, replacement_text > )
    ELSE:
      IF replacement_text == "":
        CanonicalList.append( < [a, b), "DELETE", "", orig_span > )
      ELSE IF replacement_text == orig_span:
        CONTINUE
      ELSE:
        CanonicalList.append( < [a, b), "REPLACE", replacement_text, orig_span > )

  RETURN CanonicalList

ApplyComponent(orig_span, comp, base_offset) -> String:
  out = ""
  curr = 0
  Per ciascun C in comp:
    rel_s = C.z_s - base_offset
    rel_e = C.z_e - base_offset
    out = out + orig_span[ curr : rel_s ]
    out = out + C.synthetic_text
    curr = rel_e
  out = out + orig_span[ curr : ScalarLen(orig_span) ]
  RETURN out
```

[STRUCTURAL INVARIANT]
Lemma di Preservazione Semantica di MaterializeLossy:
Definito l'operatore MaterializeLossy(T_orig, M) := Gap_0 + C_1.synthetic_text + Gap_1 + ... + C_m.synthetic_text + Gap_m, vale l'identita' esatta:
    MaterializeLossy(T_orig, SelectedMutations) == MaterializeLossy(T_orig, NormalizeMutations(SelectedMutations, T_orig))

### 3.3 Algoritmo Deterministico di Ricostruzione (Psi_rec), BuildCanonicalDelta e Contratto CJDC
[NORMATIVE REQUIREMENT]
La funzione pura BuildCanonicalDelta costruisce il descrittore normativo SingleFileDelta a partire dalle mutazioni selezionate:

    BuildCanonicalDelta(T_orig, SelectedMutations) -> SingleFileDelta:
      canonical_ops = NormalizeMutations(SelectedMutations, T_orig)
      ops_sorted = Ordina canonical_ops per op.offset decrescente
      T_lossy = MaterializeLossy(T_orig, canonical_ops)
      RETURN <
        lossy_sha256:              HexLowerCase(SHA256(EncodeStrictUTF8(T_lossy))),
        lossy_code_point_count:    ScalarLen(T_lossy),
        lossy_byte_length:         ByteLenUTF8(T_lossy),
        operations:                ops_sorted,
        original_sha256:           HexLowerCase(SHA256(EncodeStrictUTF8(T_orig))),
        original_code_point_count: ScalarLen(T_orig),
        original_byte_length:      ByteLenUTF8(T_orig)
      >

La funzione pura di ricostruzione reversibile Psi_rec opera come segue:

    Psi_rec(T_lossy, Delta_file) -> Result(SIGMA*, ErrorCode):
      IF HexLowerCase(SHA256(EncodeStrictUTF8(T_lossy))) != Delta_file.lossy_sha256:
        RETURN SemanticError(70)                   [ERR_LOSSY_DELTA_CORRUPT]
      IF ScalarLen(T_lossy) != Delta_file.lossy_code_point_count:
        RETURN SemanticError(70)                   [ERR_LOSSY_DELTA_CORRUPT]
      IF ByteLenUTF8(T_lossy) != Delta_file.lossy_byte_length:
        RETURN SemanticError(70)                   [ERR_LOSSY_DELTA_CORRUPT]

      T_work = T_lossy
      ops_sorted = Ordina Delta_file.operations per offset decrescente

      Per ciascuna op in ops_sorted:
        IF op.offset > ScalarLen(T_work):
          RETURN SemanticError(70)                 [ERR_LOSSY_DELTA_CORRUPT]

        CASE op.op_type OF:
          "DELETE":
            T_left = T_work[0 : op.offset]
            T_right = T_work[op.offset : ScalarLen(T_work)]
            T_work = T_left + op.payload + T_right

          "INSERT":
            IF (op.offset + op.length) > ScalarLen(T_work):
              RETURN SemanticError(70)             [ERR_LOSSY_DELTA_CORRUPT]
            IF T_work[op.offset : op.offset + op.length] != op.payload:
              RETURN SemanticError(70)             [ERR_LOSSY_DELTA_CORRUPT]
            T_left = T_work[0 : op.offset]
            T_right = T_work[op.offset + op.length : ScalarLen(T_work)]
            T_work = T_left + T_right

          "REPLACE":
            IF (op.offset + op.length) > ScalarLen(T_work):
              RETURN SemanticError(70)             [ERR_LOSSY_DELTA_CORRUPT]
            T_left = T_work[0 : op.offset]
            T_right = T_work[op.offset + op.length : ScalarLen(T_work)]
            T_work = T_left + op.payload + T_right

      IF HexLowerCase(SHA256(EncodeStrictUTF8(T_work))) != Delta_file.original_sha256:
        RETURN SemanticError(70)                   [ERR_LOSSY_DELTA_CORRUPT]
      IF ScalarLen(T_work) != Delta_file.original_code_point_count:
        RETURN SemanticError(70)                   [ERR_LOSSY_DELTA_CORRUPT]
      IF ByteLenUTF8(T_work) != Delta_file.original_byte_length:
        RETURN SemanticError(70)                   [ERR_LOSSY_DELTA_CORRUPT]

      RETURN Success(T_work)

[CJDC DELTA OPERATION SEMANTICS CONTRACT]
Nel documento delta.json le operazioni serializzate sono rigidamente quadruple con chiavi {"length", "offset", "op_type", "payload"}:
* op.offset: indice scalare in T_lossy pre-ricostruzione in cui inizia l'effetto della mutazione.
* op.length: numero esatto di Unicode Scalar Values occupati in T_lossy (ScalarLen(synthetic_text) per INSERT/REPLACE; 0 per DELETE).
* op.payload: stringa scalare del testo originale T_orig[a : b] da ripristinare per DELETE/REPLACE (con ScalarLen(payload) == b - a >= 1); stringa sintetica synthetic_text da verificare e rimuovere per INSERT (con ScalarLen(payload) == op.length).

### 3.4 Dimostrazione della Decrescenza Stretta degli Offset Delta
[STRUCTURAL INVARIANT]
Dato T_lossy = MaterializeLossy(T_orig, NormalizeMutations(SelectedMutations, T_orig)):
Siano (C_1, ..., C_K) le mutazioni normalizzate con span sorgente [a_i, b_i) e length_i = ScalarLen(C_i.synthetic_text).
Per la massimalita' delle componenti connesse vale b_i < a_{i+1}, con gap_i = a_{i+1} - b_i >= 1 di testo originale non modificato.
Gli offset scalari in T_lossy soddisfano la relazione di ricorrenza esatta:
    op_1.offset = ScalarLen(T_orig[0 : a_1]) = a_1 >= 0
    op_{i+1}.offset = op_i.offset + length_i + gap_i >= op_i.offset + 0 + 1 > op_i.offset
Invertendo la sequenza per la serializzazione Delta decrescente si ottiene:
    op_K.offset > op_{K-1}.offset > ... > op_1.offset >= 0
Tutti gli offset nel Delta sono strettamente decrescenti senza alcuna eccezione.

### 3.5 Canonicalizzazione e Validazione di RedProfile
[NORMATIVE REQUIREMENT]
1. ValidateRedProfile(R) -> Status (VALID | INVALID):
   Verifica che R.profile_id sia conforme a ^[a-z0-9_-]+$, R.max_dist_pct in [0 .. 100], e che R.rules sia un array di sestuple RuleSpec con rule_id unici in PosUInt53, match_pattern rigorosamente conforme al tipo associato a match_type e pattern non vuoti.
2. NormalizeRedProfile(R) -> RedProfile:
   Restituisce il profilo con l'array rules ordinato in modo strettamente crescente per rule_id.
3. CanonicalSerializeRedProfile(R) -> ByteString:
   Serializzazione esatta conforme a CJOC (ULRP Sez. 3.1) applicata a NormalizeRedProfile(R).
*Regola di Valutazione:* L'ordine di serializzazione (rule_id ASC) NON costituisce l'ordine di valutazione delle regole in GenerateCandidates, che avviene ordinando per rule_priority DESC e rule_id ASC.

### 3.6 Metrica di Churn Scalare Delta_mutation_impact_pct
[NORMATIVE REQUIREMENT]
La funzione pura f(op) definisce il costo di mutazione scalare:
    f(op) := IF op.op_type == "DELETE" THEN ScalarLen(op.payload)
             ELSE IF op.op_type == "INSERT" THEN op.length
             ELSE (ScalarLen(op.payload) + op.length)

    total_mutated_code_points := sum(op in Delta.operations, f(op))

    Delta_mutation_impact_pct(T_orig, Delta) :=
      IF ScalarLen(T_orig) == 0 THEN 0
      ELSE floor((Delta.total_mutated_code_points * 100) / ScalarLen(T_orig))

Se Delta_mutation_impact_pct(T_orig, Delta) > RedProfile.max_dist_pct, la pipeline abortisce emettendo SemanticError(71) (ERR_SEMANTIC_TOLERANCE_EXCEEDED).

### 3.7 Validazione Gerarchica del Delta (ValidateDeltaSchema, ValidateDeltaStructure, ValidateDeltaSemantics)
[NORMATIVE REQUIREMENT]
    ValidateDeltaSchema(delta_bytes) -> Status:
      IF NOT (IsValidStrictUTF8(delta_bytes) AND IsConformingCJOC(delta_bytes)):
        RETURN INVALID
      doc = ParseJSON(delta_bytes)
      IF doc == PARSE_ERROR OR NOT IsJSONObject(doc):
        RETURN INVALID

      expected_root_keys = { "delta_schema_version", "files", "generator", "total_mutated_code_points" }
      IF keys(doc) != expected_root_keys:
        RETURN INVALID

      IF NOT (doc.delta_schema_version == "1.0.0" AND
          doc.generator == "ULRP-EXT-SPEC-1.1" AND
          IsUInt53(doc.total_mutated_code_points) AND
          IsJSONObject(doc.files)):
        RETURN INVALID

      expected_file_keys = { "lossy_byte_length", "lossy_code_point_count", "lossy_sha256",
                             "operations", "original_byte_length", "original_code_point_count", "original_sha256" }
      FORALL f in keys(doc.files):
        IF NOT (f in P_canon):
          RETURN INVALID
        rec = doc.files[f]
        IF NOT (IsJSONObject(rec) AND keys(rec) == expected_file_keys):
          RETURN INVALID
        IF NOT (IsUInt53(rec.lossy_byte_length) AND
                IsUInt53(rec.lossy_code_point_count) AND
                IsHexLowerCase64(rec.lossy_sha256) AND
                IsJSONArray(rec.operations) AND
                IsUInt53(rec.original_byte_length) AND
                IsUInt53(rec.original_code_point_count) AND
                IsHexLowerCase64(rec.original_sha256)):
          RETURN INVALID

        expected_op_keys = { "length", "offset", "op_type", "payload" }
        FORALL op in rec.operations:
          IF NOT (IsJSONObject(op) AND keys(op) == expected_op_keys):
            RETURN INVALID
          IF NOT (IsUInt53(op.offset) AND
                  IsUInt53(op.length) AND
                  (op.op_type in { "DELETE", "INSERT", "REPLACE" }) AND
                  IsString(op.payload)):
            RETURN INVALID
      RETURN VALID

    ValidateDeltaStructure(delta_doc) -> Status:
      running_total_mutated = 0

      FORALL f in keys(delta_doc.files):
        ops = delta_doc.files[f].operations
        lossy_len = delta_doc.files[f].lossy_code_point_count

        FORALL op in ops:
          IF op.offset > (9007199254740991 - op.length):
            RETURN INVALID
          IF (op.offset + op.length) > lossy_len:
            RETURN INVALID

          term_payload_len = ScalarLen(op.payload)
          IF op.length > (9007199254740991 - term_payload_len):
            RETURN INVALID
          op_cost = IF op.op_type == "DELETE" THEN term_payload_len
                    ELSE IF op.op_type == "INSERT" THEN op.length
                    ELSE (op.length + term_payload_len)

          IF running_total_mutated > (9007199254740991 - op_cost):
            RETURN INVALID
          running_total_mutated = running_total_mutated + op_cost

          CASE op.op_type OF:
            "DELETE":
              IF op.length != 0 OR term_payload_len == 0: RETURN INVALID
            "INSERT":
              IF op.length == 0 OR op.length != term_payload_len: RETURN INVALID
            "REPLACE":
              IF op.length == 0 OR term_payload_len == 0: RETURN INVALID

        Per i da 0 a Card(ops) - 2:
          curr = ops[i]
          succ = ops[i + 1]
          IF curr.offset <= succ.offset:
            RETURN INVALID

        Per i da 0 a Card(ops) - 1:
          Per j da i + 1 a Card(ops) - 1:
            op_i = ops[i]
            op_j = ops[j]
            IF op_i.op_type == "DELETE" AND op_j.op_type == "DELETE":
              IF op_i.offset == op_j.offset:
                RETURN INVALID
            ELSE IF op_i.op_type == "DELETE" AND op_j.op_type != "DELETE":
              IF op_i.offset >= op_j.offset AND op_i.offset < (op_j.offset + op_j.length):
                RETURN INVALID
            ELSE IF op_i.op_type != "DELETE" AND op_j.op_type == "DELETE":
              IF op_j.offset >= op_i.offset AND op_j.offset < (op_i.offset + op_i.length):
                RETURN INVALID
            ELSE:
              IF NOT (op_i.offset >= (op_j.offset + op_j.length) OR op_j.offset >= (op_i.offset + op_i.length)):
                RETURN INVALID

      IF delta_doc.total_mutated_code_points != running_total_mutated:
        RETURN INVALID

      RETURN VALID

    ValidateDeltaSemantics(H, path, manifest, delta_doc) -> Status:
      FORALL f in keys(manifest.files):
        K_f = FiltraChunkPerFile(manifest.chunks, f)
        Ordina K_f per c.index crescente
        T_file_lossy = ""
        Per ciascun c in K_f:
          chunk_bytes = LeggiByte(H, path + "/" + c.relative_path)
          T_file_lossy = T_file_lossy + DecodeStrictUTF8(chunk_bytes)

        IF ScalarLen(T_file_lossy) != delta_doc.files[f].lossy_code_point_count:
          RETURN INVALID
        IF ByteLenUTF8(T_file_lossy) != delta_doc.files[f].lossy_byte_length:
          RETURN INVALID
        IF HexLowerCase(SHA256(EncodeStrictUTF8(T_file_lossy))) != delta_doc.files[f].lossy_sha256:
          RETURN INVALID

        res = Psi_rec(T_file_lossy, delta_doc.files[f])
        IF res == SemanticError(e):
          RETURN INVALID

        T_orig_restored = res.value
        IF ScalarLen(T_orig_restored) != delta_doc.files[f].original_code_point_count:
          RETURN INVALID
        IF ByteLenUTF8(T_orig_restored) != delta_doc.files[f].original_byte_length:
          RETURN INVALID
        IF HexLowerCase(SHA256(EncodeStrictUTF8(T_orig_restored))) != delta_doc.files[f].original_sha256:
          RETURN INVALID

      RETURN VALID

### 3.8 Validazione Estesa del Dataset (ValidateDatasetExt) e Chiusura Namespace .pcs
[NORMATIVE REQUIREMENT]
In modalita' lossless, la presenza di una directory '.pcs' all'interno di OUTPUT_PATH costituisce una violazione della chiusura fisica del namespace e determina l'esito INVALID. Il runtime DEVE garantire che la transizione o fallback a lossless elimini integralmente la directory '.pcs'.

    ValidateDatasetExt(H, path) -> < VALID, BackupIdentity > | INVALID:
      manifest_path = path + "/manifest.json"
      IF NOT (manifest_path esiste su H AND Leggibile(H, manifest_path)):
        RETURN INVALID

      manifest_bytes = LeggiByte(H, manifest_path)
      IF NOT (IsValidStrictUTF8(manifest_bytes) AND IsConformingCJOC(manifest_bytes)):
        RETURN INVALID
      manifest = ParseJSON(manifest_bytes)
      IF manifest == PARSE_ERROR OR NOT IsJSONObject(manifest):
        RETURN INVALID

      IF manifest.mode == "lossless":
        RETURN ValidateDataset(H, path)

      ELSE IF manifest.mode == "lossy":
        expected_root_keys = { "byte_length_utf8", "chunks", "files", "generation_id",
                               "generator", "language_profile", "lossy_profile", "mode",
                               "total_chunks", "total_scalar_values" }
        IF keys(manifest) != expected_root_keys:
          RETURN INVALID

        expected_lossy_keys = { "delta_manifest_hash" }
        IF NOT (IsJSONObject(manifest.lossy_profile) AND keys(manifest.lossy_profile) == expected_lossy_keys AND IsHexLowerCase64(manifest.lossy_profile.delta_manifest_hash)):
          RETURN INVALID

        IF NOT (manifest.generator == "ULRP-SPEC-1.6" AND
                manifest.mode == "lossy" AND
                manifest.language_profile == "default-closed-world" AND
                IsUInt53(manifest.generation_id) AND
                IsPosUInt53(manifest.total_chunks) AND
                IsUInt53(manifest.total_scalar_values) AND
                IsUInt53(manifest.byte_length_utf8) AND
                IsJSONArray(manifest.chunks) AND
                IsJSONObject(manifest.files) AND
                manifest.total_chunks == Card(manifest.chunks)):
          RETURN INVALID

        expected_file_keys = { "byte_length_utf8", "code_point_count", "sha256_full", "total_chunks" }
        FORALL f in keys(manifest.files):
          rec = manifest.files[f]
          IF NOT (IsJSONObject(rec) AND keys(rec) == expected_file_keys):
            RETURN INVALID
          IF NOT (f in P_canon AND
                  IsUInt53(rec.code_point_count) AND
                  IsUInt53(rec.byte_length_utf8) AND
                  IsHexLowerCase64(rec.sha256_full) AND
                  IsPosUInt53(rec.total_chunks)):
            RETURN INVALID

        expected_chunk_keys = { "byte_length_utf8", "code_point_count", "file_path", "index", "relative_path", "sha256" }
        declared_chunk_paths = EMPTY_SET
        FORALL c in manifest.chunks:
          IF NOT (IsJSONObject(c) AND keys(c) == expected_chunk_keys):
            RETURN INVALID
          IF NOT (c.file_path in keys(manifest.files) AND
                  IsPosUInt53(c.index) AND
                  IsUInt53(c.byte_length_utf8) AND
                  IsUInt53(c.code_point_count) AND
                  IsHexLowerCase64(c.sha256) AND
                  c.relative_path == c.file_path + "/" + ChunkFileName(c.index)):
            RETURN INVALID
          IF c.relative_path in declared_chunk_paths:
            RETURN INVALID
          declared_chunk_paths = declared_chunk_paths UNION { c.relative_path }

        total_scalars_calc = 0
        total_bytes_calc = 0
        FORALL f in keys(manifest.files):
          reconstructed = ReconstructFile(H, path, f, manifest)
          IF reconstructed == INVALID:
            RETURN INVALID
          IF reconstructed.total_chunks != manifest.files[f].total_chunks:
            RETURN INVALID
          IF reconstructed.code_point_count != manifest.files[f].code_point_count:
            RETURN INVALID
          IF reconstructed.byte_length_utf8 != manifest.files[f].byte_length_utf8:
            RETURN INVALID
          IF reconstructed.sha256_full != manifest.files[f].sha256_full:
            RETURN INVALID
          total_scalars_calc = total_scalars_calc + reconstructed.code_point_count
          total_bytes_calc = total_bytes_calc + reconstructed.byte_length_utf8

        IF total_scalars_calc != manifest.total_scalar_values:
          RETURN INVALID
        IF total_bytes_calc != manifest.byte_length_utf8:
          RETURN INVALID

        declared_files = { "manifest.json", ".pcs/delta.json" } UNION declared_chunk_paths
        IF ListaTuttiIFilesRelativi(H, path) != declared_files:
          RETURN INVALID
        IF ListaTutteLeDirectoryRelative(H, path) != DeclaredParentDirs(declared_files):
          RETURN INVALID
        IF ContieneLinkOIndirezioni(H, path):
          RETURN INVALID

        delta_path = path + "/.pcs/delta.json"
        IF NOT (delta_path esiste su H AND Leggibile(H, delta_path)):
          RETURN INVALID
        delta_bytes = LeggiByte(H, delta_path)
        IF HexLowerCase(SHA256(delta_bytes)) != manifest.lossy_profile.delta_manifest_hash:
          RETURN INVALID

        IF ValidateDeltaSchema(delta_bytes) != VALID:
          RETURN INVALID
        delta_doc = ParseJSON(delta_bytes)
        IF keys(delta_doc.files) != keys(manifest.files):
          RETURN INVALID
        IF ValidateDeltaStructure(delta_doc) != VALID:
          RETURN INVALID
        IF ValidateDeltaSemantics(H, path, manifest, delta_doc) != VALID:
          RETURN INVALID

        identity = < manifest.generation_id, ManifestHash(manifest_bytes) >
        RETURN < VALID, identity >

      ELSE:
        RETURN INVALID

---

# PARTE IV -- DOWNSTREAM SYNTACTIC CONFINEMENT & REFERENTIAL INTEGRITY CAGE

---

## 4. INDIREZIONE COMPATTA SHORT-ID E FRAMING LENGTH-PREFIXED

### 4.1 Biiezione di Indirezione Locale a Token Compatti (sigma_local) e Spazio Domain_compact
[NORMATIVE REQUIREMENT]
Sia TokenMap l'accumulatore globale di token di ULRP Sez. 2.5 contenente K_total elementi ordinati lessicograficamente per TokenID.
Se K_total == 0, keys(TokenMap) == EMPTY_SET e il dominio di sigma_local e' formalmente vuoto.

    sigma_local : [0 .. K_total - 1] <-> keys(TokenMap)
    sigma_local(idx) := SortedKeys(TokenMap)[idx]
    sigma_local_inverse(id_hex) :=
      idx = BinarySearch(SortedKeys(TokenMap), id_hex)
      IF idx != -1 THEN RETURN Success(idx)
      ELSE RETURN SemanticError(40)                 [ERR_RIC_VERIFICATION_FAILED]

Linguaggio dei Placeholder Compatti (L_compact):
    L_compact := { DELIM_SEQ + TokenType + ":" + ToString(idx) + DELIM_SEQ |
                   TokenType in {'s', 'b', 'h', 'c'} AND idx in Integers_ge_0 AND idx < K_total }
Se K_total == 0, L_compact == EMPTY_SET.

Definizione del Dominio Canonico Compattabile (Domain_compact):
    Domain_compact := { T in SIGMA* | T corrisponde a un flusso di chunk validamente emesso
                        dalla funzione Partition di ULRP-1.6.27 tale che:
                        1. Ogni placeholder sintetico presente in T appartiene a L_ph;
                        2. Per ogni segmento non protetto U compreso tra placeholder adiacenti
                           (o ai confini del flusso), il testo decodificato D(U) non contiene
                           la sequenza [U+00A7, U+00A7] }

### 4.2 Funzioni Pure di Traduzione (ToCompact, FromCompact)
[NORMATIVE REQUIREMENT]
    ToCompact(T_comp, sigma_local) -> Result(String, ErrorCode):
      T_out = ""
      k = 0
      L = ScalarLen(T_comp)
      curr_seg = ""
      Mentre k < L:
        IF (k + 70 <= L) AND (T_comp[k : k + 70] IN L_ph):
          IF ScalarLen(curr_seg) > 0:
            T_out = T_out + D(curr_seg)
            curr_seg = ""

          w = T_comp[k : k + 70]
          tau = w[2]
          id_hex = w[4 : 68]
          idx_res = sigma_local_inverse(id_hex)
          IF idx_res == SemanticError(e):
            RETURN SemanticError(e)
          idx = idx_res.value
          p_compact = [ U+00A7, U+00A7 ] + tau + ":" + ToString(idx) + [ U+00A7, U+00A7 ]
          T_out = T_out + p_compact
          k = k + 70
        ELSE:
          curr_seg = curr_seg + T_comp[k]
          k = k + 1
      
      IF ScalarLen(curr_seg) > 0:
        T_out = T_out + D(curr_seg)
      RETURN Success(T_out)

    FromCompact(T_prompt, sigma_local) -> Result(String, ErrorCode):
      T_out = ""
      k = 0
      L = ScalarLen(T_prompt)
      Mentre k < L:
        IF (k + 1 < L) AND (T_prompt[k] == U+00A7) AND (T_prompt[k + 1] == U+00A7):
          next_delim = FindBoundedDelim(T_prompt, k + 2, 25)
          IF next_delim == -1:
            RETURN SemanticError(72)                [ERR_COMPACT_PLACEHOLDER_CORRUPT]
          w = T_prompt[k : next_delim + 2]
          
          IF ScalarLen(w) < 7 OR w[3] != U+003A:
            RETURN SemanticError(72)                [ERR_COMPACT_PLACEHOLDER_CORRUPT]
          
          tau = w[2]
          IF tau NOT IN {'s', 'b', 'h', 'c'}:
            RETURN SemanticError(72)                [ERR_COMPACT_PLACEHOLDER_CORRUPT]
          
          idx_str = w[4 : ScalarLen(w) - 2]
          IF NOT IsValidDigits(idx_str):
            RETURN SemanticError(72)                [ERR_COMPACT_PLACEHOLDER_CORRUPT]
          
          idx = ParseUInt53(idx_str)
          IF idx >= K_total:
            RETURN SemanticError(72)                [ERR_COMPACT_PLACEHOLDER_CORRUPT]
          
          id_hex = sigma_local(idx)
          IF TokenMap[id_hex].tau != tau:
            RETURN SemanticError(72)                [ERR_COMPACT_PLACEHOLDER_CORRUPT]
          
          p_canonical = [ U+00A7, U+00A7 ] + tau + ":" + id_hex + [ U+00A7, U+00A7 ]
          T_out = T_out + p_canonical
          k = next_delim + 2
        ELSE:
          T_out = T_out + T_prompt[k]
          k = k + 1
      RETURN Success(T_out)

    FindBoundedDelim(T, start_idx, max_scan) -> Integer:
      L = ScalarLen(T)
      limit = min(start_idx + max_scan, L)
      Per i da start_idx a limit - 2:
        IF T[i] == U+00A7 AND T[i + 1] == U+00A7:
          RETURN i
      RETURN -1

[STRUCTURAL INVARIANT]
Biiezione Canonica e Trattamento dei Delimitatori Non Protetti:
1. Biiezione sul Dominio Valido:
    FORALL T in Domain_compact:
      FromCompact( (ToCompact(T, sigma_local)).value, sigma_local ) == Success(T)
    FORALL C in L_compact*:
      ToCompact( (FromCompact(C, sigma_local)).value, sigma_local ) == Success(C)

2. Trattamento di Sequenze Non Conformi:
   Qualora un testo in ingresso a FromCompact contenga la sequenza letterale [U+00A7, U+00A7] che non delimita un elemento valido di L_compact conforme a:
     [U+00A7, U+00A7] + tau + ":" + idx + [U+00A7, U+00A7]
   con tau in {'s', 'b', 'h', 'c'} e idx in [0 .. K_total - 1], la funzione FromCompact interrompe tassativamente l'elaborazione emettendo SemanticError(72) (ERR_COMPACT_PLACEHOLDER_CORRUPT), in stretta aderenza alla grammatica chiusa BNF.

### 4.3 Formato Length-Prefixed PCS_FRAME_V1 e StripPromptEnvelope
[NORMATIVE REQUIREMENT]
Il prompt generativo viene incapsulato nel formato testuale UTF-8 strutturato length-prefixed:

    <<<BEGIN_PCS_FRAME_V1>>>
    PATH: <P_canon>
    CHUNK_INDEX: <PosUInt53>
    TOTAL_CHUNKS: <PosUInt53>
    PAYLOAD_SCALAR_COUNT: <UInt53>
    PAYLOAD_BYTE_COUNT: <UInt53>
    PAYLOAD_SHA256: <64-hex lower-case SHA-256>
    <<<BEGIN_PAYLOAD>>>
    <c_compact UTF-8 raw bytes>
    <<<END_PAYLOAD>>>
    <<<END_PCS_FRAME_V1>>>

Parsing dei Campi di Header:

    ParseFrameHeaderFields(header_text) -> Result(FrameMeta, ErrorCode):
      lines = SplitByNewline(header_text)
      IF Card(lines) != 7:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      IF lines[0] != "<<<BEGIN_PCS_FRAME_V1>>>":
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      
      path_val = ExtractHeaderField(header_text, "PATH")
      IF path_val == SemanticError(e): RETURN SemanticError(e)
      IF path_val.value NOT IN P_canon:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      
      idx_val = ExtractHeaderField(header_text, "CHUNK_INDEX")
      IF idx_val == SemanticError(e): RETURN SemanticError(e)
      IF NOT IsValidDigits(idx_val.value): RETURN SemanticError(74)
      
      tot_val = ExtractHeaderField(header_text, "TOTAL_CHUNKS")
      IF tot_val == SemanticError(e): RETURN SemanticError(e)
      IF NOT IsValidDigits(tot_val.value): RETURN SemanticError(74)
      
      scal_val = ExtractHeaderField(header_text, "PAYLOAD_SCALAR_COUNT")
      IF scal_val == SemanticError(e): RETURN SemanticError(e)
      IF NOT IsValidDigits(scal_val.value): RETURN SemanticError(74)
      
      byte_val = ExtractHeaderField(header_text, "PAYLOAD_BYTE_COUNT")
      IF byte_val == SemanticError(e): RETURN SemanticError(e)
      IF NOT IsValidDigits(byte_val.value): RETURN SemanticError(74)
      
      sha_val = ExtractHeaderField(header_text, "PAYLOAD_SHA256")
      IF sha_val == SemanticError(e): RETURN SemanticError(e)
      IF NOT IsHexLowerCase64(sha_val.value): RETURN SemanticError(74)

      idx_num = ParseUInt53(idx_val.value)
      tot_num = ParseUInt53(tot_val.value)
      IF idx_num < 1 OR tot_num < 1 OR idx_num > tot_num:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]

      meta = < path_val.value, idx_num, tot_num,
               ParseUInt53(scal_val.value), ParseUInt53(byte_val.value), sha_val.value >
      RETURN Success(meta)

Parsing Byte-Exact di StripPromptEnvelope:

    StripPromptEnvelope(RawBytes, ExpectedPath, ExpectedChunkIdx, ExpectedTotalChunks) -> Result(String, ErrorCode):
      magic_header = "<<<BEGIN_PCS_FRAME_V1>>>\n"
      IF ByteCount(RawBytes) < ByteCount(magic_header):
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      IF RawBytes[ 0 : ByteCount(magic_header) ] != magic_header:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]

      header_marker = "<<<BEGIN_PAYLOAD>>>\n"
      h_pos = FindByteSubstring(RawBytes, header_marker)
      IF h_pos == -1:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      Offset_Payload_Start = h_pos + ByteCount(header_marker)
      
      header_bytes = RawBytes[0 : h_pos]
      IF NOT IsValidStrictUTF8(header_bytes):
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      header_text = DecodeStrictUTF8(header_bytes)

      meta_res = ParseFrameHeaderFields(header_text)
      IF meta_res == SemanticError(e):
        RETURN SemanticError(e)
      meta = meta_res.value

      IF meta.Path != ExpectedPath OR meta.ChunkIndex != ExpectedChunkIdx OR meta.TotalChunks != ExpectedTotalChunks:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]

      N = meta.PayloadByteCount
      IF Offset_Payload_Start > ByteCount(RawBytes):
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      IF N > (ByteCount(RawBytes) - Offset_Payload_Start):
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      
      Payload_Bytes = RawBytes[ Offset_Payload_Start : Offset_Payload_Start + N ]

      Offset_Footer = Offset_Payload_Start + N
      Expected_Footer = "\n<<<END_PAYLOAD>>>\n<<<END_PCS_FRAME_V1>>>\n"
      IF (ByteCount(RawBytes) - Offset_Footer) != ByteCount(Expected_Footer):
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      IF RawBytes[ Offset_Footer : ByteCount(RawBytes) ] != Expected_Footer:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]

      IF HexLowerCase(SHA256(Payload_Bytes)) != meta.PayloadSHA256:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      IF NOT IsValidStrictUTF8(Payload_Bytes):
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]
      Payload_Text = DecodeStrictUTF8(Payload_Bytes)
      IF ScalarLen(Payload_Text) != meta.PayloadScalarCount:
        RETURN SemanticError(74)                    [ERR_PROMPT_ENVELOPE_BREACH]

      RETURN Success(Payload_Text)

### 4.4 Grammatica BNF di Generazione Vincolata (Output BNF Contract)
[NORMATIVE REQUIREMENT]
Il delimitatore DELIM_CHAR corrisponde al code point Unicode U+00A7 (Section Sign). Il campionamento dell'LLM e' vincolato dalla grammatica BNF:

    <stream>              ::= <text_stream>
    <text_stream>         ::= <text_element> | <text_element> <text_stream>
    <text_element>        ::= <compact_placeholder> | <safe_char>
    <compact_placeholder> ::= <delim_seq> <token_type> ":" <digit_seq> <delim_seq>
    <delim_seq>           ::= "\u00A7\u00A7"
    <token_type>          ::= "s" | "b" | "h" | "c"
    <digit_seq>            ::= "0" | <non_zero_digit> <digits_opt>
    <digits_opt>           ::= "" | <digit> <digits_opt>
    <non_zero_digit>       ::= "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
    <digit>                ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
    <safe_char>           ::= [^\u00A7] | "\u00A7" [^\u00A7] | "\u00A7" <eof_char>
    <eof_char>            ::= ""

### 4.5 Risolutore di Modifiche Generative (F_resolve_gen)
[NORMATIVE REQUIREMENT]
    F_resolve_gen(RawBytes, ExpectedPath, ExpectedChunkIdx, ExpectedTotalChunks, TokenMap, sigma_local) -> Result(String, ErrorCode):
      strip_res = StripPromptEnvelope(RawBytes, ExpectedPath, ExpectedChunkIdx, ExpectedTotalChunks)
      IF strip_res == SemanticError(e):
        RETURN SemanticError(e)
      T_stripped = strip_res.value

      T_canon_res = FromCompact(T_stripped, sigma_local)
      IF T_canon_res == SemanticError(e):
        RETURN SemanticError(e)
      T_canon = T_canon_res.value

      T_out = ""
      k = 0
      L = ScalarLen(T_canon)
      Mentre k < L:
        IF (k + 70 <= L) AND (T_canon[k : k + 70] IN L_ph):
          w = T_canon[k : k + 70]
          id_hex = w[4 : 68]
          IF id_hex NOT IN keys(TokenMap):
            RETURN SemanticError(73)                [ERR_GENERATIVE_TOKEN_MUTATION]
          T_out = T_out + TokenMap[id_hex].K
          k = k + 70
        ELSE:
          T_out = T_out + T_canon[k]
          k = k + 1

      RETURN Success(T_out)

---

# PARTE V -- ERROR TAXONOMY, FALLBACK STATE MACHINE & CONFORMANCE

---

## 5. TASSONOMIA DEGLI ERRORI ESTESI ED FSM DI FALLBACK

### 5.1 Tassonomia dei Codici di Errore dell'Estensione (60 .. 80)
[NORMATIVE REQUIREMENT]

+-------+----------------------------------+---------------------+----------------------------------------------------+
| Cod.  | Identificatore Simbolico         | Categoria           | Condizione Normativa di Emissione Univoca          |
+-------+----------------------------------+---------------------+----------------------------------------------------+
| 60    | ERR_TOKEN_BUDGET_OVERFLOW        | SemanticError       | mu_tok non conforme o nessun S >= 1 feasible.      |
| 61    | ERR_GRAMMAR_SELECTOR_FAILURE     | SemanticError       | Parsing AST fallito o coordinate non valide.       |
| 62    | ERR_PRIVACY_POLICY_VIOLATION     | SemanticError       | Trasformazione lossy su secret/dati particolari.   |
| 63-68 | RESERVED_FOR_FUTURE_EXTENSIONS   | SemanticError       | Riservati per estensioni semantiche future.        |
| 69    | ERR_DELTA_SCHEMA_INVALID         | SemanticError       | Violazione schema CJDC o disgiunzione Delta.       |
| 70    | ERR_LOSSY_DELTA_CORRUPT          | SemanticError       | Mismatch crittografico hash o fallimento Psi_rec.  |
| 71    | ERR_SEMANTIC_TOLERANCE_EXCEEDED  | SemanticError       | Delta_mutation_impact supera MaxDistPct.           |
| 72    | ERR_COMPACT_PLACEHOLDER_CORRUPT  | SemanticError       | Pattern L_compact malformato o idx fuori range.    |
| 73    | ERR_GENERATIVE_TOKEN_MUTATION    | SemanticError       | TokenID non censito nell'accumulatore TokenMap.    |
| 74    | ERR_PROMPT_ENVELOPE_BREACH       | SemanticError       | Violazione framing, context mismatch o hash errato.|
| 75-79 | RESERVED_FOR_FUTURE_EXTENSIONS   | SemanticError       | Riservati per estensioni generative future.        |
| 80    | ERR_EXTENSION_FALLBACK_FAILURE   | ExecutionAbort      | Fallimento bonifica staging prima del fallback.    |
+-------+----------------------------------+---------------------+----------------------------------------------------+

### 5.2 Deterministic Dual Fallback FSM e Precedenza degli Errori
[NORMATIVE REQUIREMENT]
Al rilevamento di un errore esteso e in {60 .. 74}, la macchina a stati commuta istantaneamente in base a Fallback_mode_raw:

    IF Fallback_mode == SAFE_DEGRADED:
      1. Esegui ContextStateReset();
      2. Reset della FSM allo stato STATE_INIT;
      3. Emissione del messaggio statico di sicurezza (PCS 4.5 Sez. 7.2);
      4. RETURN Success(SafeDegradedOutcome).

    ELSE IF Fallback_mode == LOSSLESS:
      1. Esegui RemoveIfExists(STAGING_PATH);
      2. IF ClassifyPath(H, STAGING_PATH) != ABSENT:
           RETURN ExecutionAbort(80)                [ERR_EXTENSION_FALLBACK_FAILURE]
      3. Z_fallback = IF (Z_ext e' definita e valida) THEN Z_ext ELSE EMPTY_SET
      4. C_base = ProjectBaseConfig(C_ext_raw, Z_fallback)
      5. res_base = F_sem(D_raw, C_base)
      6. RETURN FallbackTriggered(res_base)

---

## 6. SUITE DI CONFORMITA' ESTESA (EXT-F01 .. EXT-F36)

[CONFORMANCE TEST]
Un'implementazione conforme all'estensione DEVE superare tutti i seguenti 36 scenari deterministici:

* EXT-F01 (Dynamic Token Budget Adaptation & Policy B): Calcolo di S_optimal tramite Pi_budget su testo a densita' variabile con riserva esplicita di delta_join.
* EXT-F02 (Tokenizer Axioms Property Test): Esecuzione di test su mu_tok per verificare non-negativita', monotonicita' e sub-additivita' a giunzione limitata delta_join in [0 .. 4].
* EXT-F03 (AST Selector Conflict Resolution & Leftmost-Wins): Invocazione di F_select con intervalli in sovrapposizione parziale e verifica di scansione deterministica.
* EXT-F04 (Privacy & Hard-Secret Isolation): Blocco assoluto di riduzioni lossy su nodi classificati HARD_SECRET o SPECIAL_CATEGORY_DATA ed emissione di SemanticError(62).
* EXT-F05 (Multi-File Lossy Reduction & Byte-Exact Reversibility): Esecuzione di Phi_red e Psi_rec su dataset multi-file con verifica di ripristino esatto (RIC-L1 .. RIC-L5).
* EXT-F06 (Mutation Churn Metric & MaxDistPct Threshold): Calcolo di Delta_mutation_impact_pct su file vuoto (0%) e su file con mutazioni eccedenti MaxDistPct con SemanticError(71).
* EXT-F07 (Compact Short-ID Bijective Translation): Verifica di biiezione esatta FromCompact(ToCompact(T)) == T e ToCompact(FromCompact(C)) == C su 10.000 token e gestione corretta di K_total = 0.
* EXT-F08 (PCS_FRAME_V1 Length-Prefixed Frame Parsing): Validazione di payload con campi header strutturati, verifica magic header line, controllo P_canon, PosUInt53 e context-binding.
* EXT-F09 (Generative Literal Backslash Preservation): Generazione contenente percorsi con backslash ("C:\dir\file.txt") senza duplicazione o de-escaping spurio.
* EXT-F10 (Dual Fallback Lossless Degradation): Iniezione di errore semantico con Fallback_mode = LOSSLESS, verifica di bonifica staging (ABSENT) e pubblicazione del dataset lossless.
* EXT-F11 (Zero-Width DELETE Isolation Trap): Iniezione di un record DELETE con offset coincidente con un intervallo REPLACE. Rilevamento in ValidateDeltaStructure ed emissione di SemanticError(69).
* EXT-F12 (CJDC Closed-World Schema Enforcement): Documento delta.json contenente chiavi estranee o chiavi duplicate. Rilevamento in ValidateDeltaSchema ed emissione di SemanticError(69).
* EXT-F13 (Tokenizer State Streaming Interface Conformance): Verifica del rispetto del contratto a stati <Init, Append, Cost> e complessita' ammortizzata O(1) per scalare.
* EXT-F14 (Prompt Framing Security con Payload Arbitrario): Payload contenente deliberatamente la sottostringa "\n<<<END_PAYLOAD>>>\n". Verifica che il parser utilizzi PAYLOAD_BYTE_COUNT senza troncamento prematuro.
* EXT-F15 (Reserved Namespace Trap): Ingestione di file utente con percorso ".pcs/file.txt". Rilevamento in F_filter ed emissione di SemanticError(11).
* EXT-F16 (Precedenza Errori Fallback su Storage Failure): Simulazione di fallimento di rimozione staging durante il fallback lossless. Emissione prioritaria di ExecutionAbort(80).
* EXT-F17 (Infeasible Short Chunk Budgeting): Testo corto (L=32), budget con S=32 infeasible e S=16 feasible. Verifica di selezione esatta S_optimal = 16.
* EXT-F18 (Delta Semantic Hash Mismatch): Documento delta conforme a schema e struttura, ma con lossy_sha256 non corrispondente ai byte reali di T_lossy. Emissione di SemanticError(70).
* EXT-F19 (Bounds Arithmetic Anti-Overflow Trap): Operazione delta con offset = MAX_UINT53 - 5 e length = 10. Rilevamento pre-aritmetico ed emissione di SemanticError(69).
* EXT-F20 (Arbitrary Payload Frame Roundtrip): Payload contenente code point Unicode complessi (astral plane, emoji) con verifica di corrispondenza esatta tra PAYLOAD_SCALAR_COUNT e PAYLOAD_BYTE_COUNT.
* EXT-F21 (Cleanup Staging Failure on Fallback): Simulazione directory di staging non rimovibile. Verifica di mancata invocazione del kernel base e transizione ad Abort 80.
* EXT-F22 (AST Identical Candidates Highest-Rank Merge Verification): Due nodi con identiche coordinate e tag divergenti. Verifica di applicazione esatta di MergeTagsHighestRank.
* EXT-F23 (mu_tok_seg Conservative-Bound Soundness): Verifica che ActualCost(T[k : k + S]) <= mu_tok_seg(T, k, S) per tutte le finestre del set di prova.
* EXT-F24 (Subsegment Monotonicity Verification): Verifica della proprieta' inclusiva mu_tok_seg(B) <= mu_tok_seg(A) per B sottoinsieme di A.
* EXT-F25 (Frame Unknown-Field Rejection Trap): Header frame contenente riga spura "EVIL_FIELD:x". Rilevamento in ParseFrameHeaderFields ed emissione di SemanticError(74).
* EXT-F26 (Frame Header Line Count Enforcement): Header contenente un numero di righe diverso da 7 prima di "<<<BEGIN_PAYLOAD>>>\n". Emissione di SemanticError(74).
* EXT-F27 (Delta Byte-Length Mismatch Trap): Documento delta con original_byte_length non corrispondente ai byte reali di T_orig_restored. Emissione di SemanticError(70).
* EXT-F28 (ContextStateReset Observable Isolation): Verifica che nessuna informazione della sessione precedente sia accessibile a livello di protocollo post-reset.
* EXT-F29 (Empty Text Budgeting Behavior): Invocazione di Pi_budget con L_esc = 0. Verifica di restituzione deterministica di Success(0).
* EXT-F30 (Delta Canonicality on Identical Inputs): Due esecuzioni indipendenti di Phi_red con medesimo (T_orig, RedProfile) producono file delta.json identici byte-a-byte.
* EXT-F31 (End-to-End Binary Conformance Chain): Verifica della catena deduttiva a 6 passi con identita' binaria esatta dei chunk file emessi.
* EXT-F32 (Canonical Candidate Precedence Ordering): Verifica dell'ordinamento deterministico prec_select su candidati con span sovrapposti e priorita' divergenti.
* EXT-F33 (RuleSpec Sestupla and Non-Empty Literal Trap): Tentativo di configurazione di EXACT_LITERAL con pattern vuoto. Rifiuto in ValidateRedProfile con INVALID.
* EXT-F34 (Delimited Comment Non-Greedy Scan): Commenti con delimitatori multipli contigui ("/*/*/*/"). Verifica di matching non-greedy e avanzamento canonico.
* EXT-F35 (Contiguous Mutation Fusion Verification): Tre mutazioni contigue (DELETE + INSERT + DELETE) normalizzate in un'unica REPLACE canonica con offset strettamente decrescenti.
* EXT-F36 (Zero-Width Insert Uniqueness Enforcement): Due candidati INSERT coincidenti sullo stesso punto scalare z. Selezione greedy della sola inserzione a priorita' massima.

---

## 7. TRACEABILITY & VERIFICATION MATRIX

```text
+---------------------+-------------------------------+-------------------------------+-----------------------+-------------------------+
| REQUIREMENT ID      | INVARIANTE STRUTTURALE        | ALGORITMO / CONTRATTO         | TEST ID / SUITE       | NORMATIVE STATUS        |
+---------------------+-------------------------------+-------------------------------+-----------------------+-------------------------+
| REQ-EXT-BUDGET-01   | Estimator Soundness           | Pi_budget / mu_tok_seg        | EXT-F01, EXT-F23      | CONDITIONAL_PROVEN      |
| REQ-EXT-BUDGET-02   | Subsegment Monotonicity U_T   | Lemma 2.3 (Proven)            | EXT-F02, EXT-F24      | PROVEN_ANALYTIC         |
| REQ-EXT-BUDGET-03   | Realizability of mu_tok_seg   | Adapter Class A/B/C           | EXT-F13, EXT-F23      | CONDITIONAL_PROVEN      |
| REQ-EXT-SELECT-01   | Absolute Disjointness Z_ext   | Resolve (Sweep/Stack)         | EXT-F03, EXT-F22      | PROVEN_ANALYTIC         |
| REQ-EXT-PRIVACY-01  | Conditional Policy Isolation  | F_select / MergeTags          | EXT-F04               | CONDITIONAL_PROVEN      |
| REQ-EXT-RED-01      | Canonical Candidates Generat. | GenerateCandidates (RuleSpec) | EXT-F32, EXT-F33      | SPECIFIED_DETERMINISTIC |
| REQ-EXT-RED-02      | Greedy Maximal Precedence     | SelectGreedy (prec_select)    | EXT-F30, EXT-F36      | SPECIFIED_DETERMINISTIC |
| REQ-EXT-DELTA-01    | Byte-Exact Reversibility      | Psi_rec / Phi_red             | EXT-F05, EXT-F18      | PROVEN_ANALYTIC         |
| REQ-EXT-DELTA-02    | Delta Canonicality (Identical)| BuildCanonicalDelta           | EXT-F30, EXT-F35      | SPECIFIED_DETERMINISTIC |
| REQ-EXT-DELTA-03    | Byte Length Exact Match       | ValidateDeltaSemantics        | EXT-F27               | REQUIRED_CONFORMANCE    |
| REQ-EXT-DELTA-04    | Delta Closed-World Structure  | ValidateDeltaStructure        | EXT-F11, EXT-F19      | REQUIRED_CONFORMANCE    |
| REQ-EXT-FRAME-01    | Length-Prefixed Zero-Truncate | StripPromptEnvelope           | EXT-F08, EXT-F14      | PROVEN_ANALYTIC         |
| REQ-EXT-FRAME-02    | Frame Closed-World Header     | ParseFrameHeaderFields (Exact)| EXT-F25, EXT-F26      | REQUIRED_CONFORMANCE    |
| REQ-EXT-PURGE-01    | Observable Zero Retention     | ContextStateReset (Protocol)  | EXT-F28               | REQUIRED_CONFORMANCE    |
| REQ-EXT-FALLBACK-01 | Atomicity of Staging Purge    | Dual Fallback FSM             | EXT-F10, EXT-F21      | REQUIRED_CONFORMANCE    |
| REQ-EXT-CONFORM-01  | 6-Step Binary Determinism     | Binary Conformance Chain      | EXT-F05, EXT-F31      | CONDITIONAL_PROVEN      |
+---------------------+-------------------------------+-------------------------------+-----------------------+-------------------------+
```

```text
================================================================================
FINE SPECIFICA TECNICA NORMATIVA ULRP-EXT-SPEC-1.1.0 (FROZEN STANDARD)
================================================================================
```

