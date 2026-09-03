```text
================================================================================
SPECIFICA TECNICA NORMATIVA: ULRP-SPEC-1.6.27
UNIVERSAL LLM-SAFE REVERSIBLE PARTITIONING AND PREPROCESSING PROTOCOL
Standard di Ingegneria Difensiva per Pipeline di Preprocessing Reversibile
================================================================================
Status    : APPROVED NORMATIVE SPECIFICATION (v1.6.27 - FROZEN STANDARD)
Reference : Protocollo Colomba Serpente (PCS 4.5)
Scope     : Strictly Language-Agnostic, Runtime-Agnostic, OS-Agnostic, LLM-Agnostic
================================================================================
```

## 0. CONVENZIONI, MODELLO DI CONFORMITA', MODELLO DI MINACCIA E AMBITO OSSERVABILE

### 0.1 Convenzioni Normative
Le parole chiave MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY e OPTIONAL nel presente documento devono essere interpretate conformemente a BCP 14 (RFC 2119 / RFC 8174).

### 0.2 Postulato della Funzione Pura e Separazione Semantica / Esecuzione (REQ-SEM-001)
[NORMATIVE REQUIREMENT]
La trasformazione logica deterministica del protocollo e' definita dalla funzione matematica pura:

    F_sem : D_raw x C_raw -> SemanticResult

dove:
* D_raw: Insieme finito di tuple grezze D_raw := { < P_raw, B_raw > }, con percorso grezzo P_raw in SIGMA* e sequenza di byte grezzi B_raw in {0x00..0xFF}*.
* C_raw: Tupla dei parametri grezzi C_raw := < S_target_raw, R_min_raw, Z_raw >.
* SemanticResult: Unione disgiunta dei risultati semantici:
    SemanticResult := Success(O_semantic) UNION SemanticError(e)
  con O_semantic := < K, M, R > e codice di errore semantico e in {10, 11, 12, 20, 21, 22, 30, 40}.

L'esecuzione fisica su un ambiente host reale e' modellata dalla funzione:

    F_exec : Implementation x D_raw x C_raw x HostState -> ExecutionOutcome

dove:

    ExecutionOutcome := Completed(SemanticResult) UNION ExecutionAbort(50)

Criterio di Conformita' dell'Implementazione (Conforming Implementation):
Un'implementazione I e' conforme se e solo se, per ogni input (D, C) in D_raw x C_raw e per ogni stato host H:

    (F_exec(I, D, C, H) == Completed(R)) => (R == F_sem(D, C))

L'esito ExecutionAbort(50) (ERR_STORAGE_IO_FAILURE) attesta un'interruzione operativa derivante dal fallimento non recuperabile delle risorse host o delle primitive di storage. L'abort operativo non costituisce un esito semantico alternativo per (D, C). Qualsiasi esecuzione che raggiunga il punto di completamento Completed MUST produrre un risultato identico a F_sem(D, C).

### 0.3 Struttura dell'Output Osservabile di Successo (O_semantic)
[NORMATIVE REQUIREMENT]
Quando F_sem(D, C) restituisce Success(O_semantic), la tripla O_semantic := < K, M, R > e' composta da:
1. K (Sequenza Ordinata dei Chunk File): Sequenza ordinata di tuple < P_c, B_c >, dove P_c in P_canon e' il percorso relativo canonico del chunk file e B_c in {0x00..0xFF}* e' la sequenza esatta di byte UTF-8 del contenuto del chunk compresso con placeholder sintetici.
2. M (Manifest Document): Sequenza esatta di byte del file manifest.json, serializzata conformemente al Canonical JSON Output Contract (CJOC, Section 3.1).
3. R (Reverse Map Document): Sequenza esatta di byte del file reverse_map.json, serializzata conformemente al Canonical JSON Output Contract (CJOC, Section 3.1), contenente la serializzazione canonica della TokenMap globale.

### 0.4 Confini di Non-Osservabilita' (Esclusioni Esplicite)
[NORMATIVE REQUIREMENT]
I seguenti elementi sono formalmente esterni a O_semantic e MUST NOT essere utilizzati per determinare la conformita':
* Metadati del filesystem host (inode, permessi POSIX, UID/GID, attributi DOS/Windows);
* Timestamp di creazione, accesso o modifica (atime, mtime, ctime);
* Layout dei blocchi su storage, frammentazione o chiamate di sistema;
* Stream diagnostici stdout e stderr, inclusi testi descrittivi di errore;
* Ordine fisico di allocazione o scansione dei file nelle directory host.

### 0.5 Definizione di "LLM-Safe", Confini di Validazione e Modello di Minaccia
[NORMATIVE REQUIREMENT]
1. LLM-Safe: Attesta esclusivamente l'invarianza strutturale del dataset per elaborazione automatica:
   a. Assenza di troncamenti arbitrari di sequenze multi-byte UTF-8 o code point surrogati;
   b. Atomicita' assoluta dei token protetti (nessun blocco o placeholder sintetico e' diviso tra chunk adiacenti);
   c. Verificabilita' deterministica della reversibilita' mediante Roundtrip Integrity Check (Section 4.6).
   In conformita' all'Assioma 5 PCS (ValidSchema(x) != SafeSemantic(x)), la conformita' al protocollo garantisce la ricostruzione strutturale del testo, ma NON garantisce l'equivalenza semantica del codice qualora elaborato da modelli esterni.

2. Distinzione tra Integrita' Interna e Identita' Autoritativa:
   La condizione ValidateDataset(OUTPUT_PATH) == VALID attesta esclusivamente che la directory OUTPUT_PATH soddisfa i vincoli di schema chiuso, coerenza di digest SHA-256, conteggio scalari/byte e chiusura fisica del namespace.
   ValidateDataset(OUTPUT_PATH) == VALID NON implica ne' attesta che OUTPUT_PATH corrisponda a uno specifico dataset autoritativo atteso da un client o da una configurazione esterna.
   Il protocollo locale di recovery non verifica autonomamente l'identita' autoritativa di OUTPUT_PATH rispetto a configurazioni esterne; qualsiasi associazione tra OUTPUT_PATH e una specifica generazione attesa e' demandata all'ancoraggio host-level out-of-band (HostConfiguredTargetMeta, Section 5.3).

3. Threat Model e Fault Model:
   a. Crash Fault Model (F_crash - In-Scope per Teorema 2A):
      * Terminazione improvvisa del processo (crash-stop);
      * Interruzione improvvisa di erogazione energetica (power loss);
      * Operazioni di storage incomplete o interrotte i cui esiti parziali risultano strettamente conformi ai contratti delle primitive definiti in Section 5.1 (es. un file di journal lasciato in stato CORRUPT o STAGED, o una directory in stato CORRUPT con RemainingCount monotonicamente non crescente).
      Ogni corruzione parziale in F_crash e' qualificata unicamente come lo stato incompleto prodotto su un percorso bersaglio da una primitiva interrotta secondo il rispettivo contratto di Section 5.1.
   b. Permanent Hardware / External Fault Model (F_hardware_decay - Out-of-Scope per Teorema 2A):
      * Corruzione arbitraria di dati precedentemente persistiti e confermati da PersistBarrier;
      * Degrado fisico permanente o guasto distruttivo dei blocchi del supporto (bit rot, bad sectors);
      * Perdita fisica permanente di file o directory non mutati dalle primitive correnti;
      * Modifica distruttiva o malevola esterna da parte di processi con accesso in scrittura concorrente;
      * Attaccante con privilegi di scrittura sul filesystem host capace di alterare coordinatamente chunk, manifest e journal, producendo un dataset internamente valido appartenente a una generazione differente;
      * Compromissione o falsificazione dei metadati esterni HostConfiguredTargetMeta.
   c. Disciplina dell'Hash SHA-256:
      L'algoritmo SHA-256 e' impiegato esclusivamente come funzione di hash crittografica non autenticata per la verifica di integrita' strutturale interna e deduplicazione deterministica dei token. L'uso di SHA-256 NON costituisce autenticazione di origine, Message Authentication Code (MAC) o firma digitale.

---

# PARTE I -- DATA MODEL, CODEC & STORAGE NAMESPACE

---

## 1. DOMINI OPERATIVI, UNICODE E SPAZIO DEI PERCORSI P_canon

### 1.1 Ingestione e Validazione UTF-8 Strict
[NORMATIVE REQUIREMENT]
1. Dominio Scalare Unicode:
   SIGMA := [U+0000..U+D7FF] UNION [U+E000..U+10FFFF]   (surrogati esclusi)
   I code point nell'intervallo surrogati [U+D800..U+DFFF] sono VIETATI.
   Ogni testo T e' una sequenza finita: T in SIGMA*, lunghezza L = len(T).
2. Dominio Binario:
   Sequenze di byte B in {0x00..0xFF}*.
3. Ingestione Strict:
   Ogni file di input B MUST essere decodificato secondo RFC 3629 in modalita' strict.
   La presenza di byte illegali, sequenze overlong o code point surrogati MUST determinare SemanticError(10) (ERR_INVALID_UTF8).
4. Divieto di Normalizzazione:
   Nel percorso lossless, qualsiasi normalizzazione Unicode (NFC, NFD, NFKC, NFKD) e' STRICTLY PROHIBITED. T = DecodeStrictUTF8(B) MUST preservare esattamente la sequenza originaria di Unicode Scalar Values.

### 1.2 Disciplina del Leading U+FEFF (Data-Centric Model)
[NORMATIVE REQUIREMENT]
Il protocollo adotta il modello data-centric, in cui B ed il testo T in SIGMA* sono legati biunivocamente da RFC 3629:
    B == EncodeStrictUTF8(T)
    T == DecodeStrictUTF8(B)

1. Sequenza Iniziale 0xEF 0xBB 0xBF: Se e solo se B inizia con i byte 0xEF 0xBB 0xBF, il testo T ha come primo elemento lo Scalar Value U+FEFF (T[0] == U+FEFF).
2. Preservazione Lossless: U+FEFF e' trattato come ordinario dato logico all'indice 0 di T. Viene incluso nel chunk c_1 e ri-serializzato nei byte iniziali 0xEF 0xBB 0xBF di c_1.
3. Assenza della Sequenza Iniziale: Se B non inizia con 0xEF 0xBB 0xBF, allora T[0] != U+FEFF (salvo presenza esplicita nel sorgente) e l'implementazione MUST NOT inserire alcun U+FEFF in testa ai chunk emessi.

### 1.3 Definizione Formale di P_canon Portabile
[NORMATIVE REQUIREMENT]
Ogni percorso canonico P in P_canon SUBSET SIGMA* ammette una e una sola rappresentazione come sequenza finita di segmenti non vuoti:
    P = s_1 + "/" + s_2 + ... + "/" + s_n    (n >= 1, con s_i in SIGMA+)
soddisfacente tutte le seguenti condizioni:
1. P non inizia con "/" (U+002F) e non termina con "/".
2. P non contiene alcuno dei seguenti caratteri vietati:
   * Quotation mark: '"' (U+0022)
   * Asterisco: '*' (U+002A)
   * Due punti: ':' (U+003A)
   * Minore di: '<' (U+003C)
   * Maggiore di: '>' (U+003E)
   * Punto interrogativo: '?' (U+003F)
   * Barra rovesciata: '\' (U+005C)
   * Pipe: '|' (U+007C)
3. P non contiene prefissi di volume o drive (es. "C:").
4. Nessun segmento s_i e' uguale a "." o ".." (riferimenti relativi vietati).
5. Nessun segmento s_i e' vuoto (sequenze "//" vietate).
6. Nessun segmento s_i termina con uno spazio (U+0020) o con un punto (U+002E).
7. Per ciascun segmento s_i, sia BaseName(s_i) il prefisso di s_i che precede il primo carattere "." (oppure s_i stesso se non contiene punti). BaseName(s_i) MUST NOT corrispondere (in modo case-insensitive) ad alcun nome di periferica DOS/Windows riservata (CON, PRN, AUX, NUL, COM1..COM9, LPT1..LPT9).
8. Nessun carattere in P appartiene all'intervallo di controllo [U+0000..U+001F] o a U+007F.

### 1.4 Decomposizione in Segmenti e DirectoryParents
[NORMATIVE REQUIREMENT]
Dato un percorso canonico decomposto in segmenti p = s_1 + "/" + ... + "/" + s_n:
* Se n == 1 (file di primo livello, es. "manifest.json"):
    DirectoryParents(p) := EMPTY_SET
* Se n >= 2:
    DirectoryParents(p) := { s_1 + "/" + ... + "/" + s_k | 1 <= k <= n - 1 }

Dato un insieme di percorsi di file dichiarati DeclaredFiles:
    DeclaredParentDirs(DeclaredFiles) := UNION { DirectoryParents(f) | f in DeclaredFiles }

Garanzia di Chiusura Fisica:
La funzione ListaTutteLeDirectoryRelative(H, path) restituisce l'insieme di tutte le directory (antenati intermedi e directory foglia) fisicamente presenti sotto path, escludendo path stesso. Se tale insieme differisce esattamente da DeclaredParentDirs(DeclaredFiles), ValidateDataset(H, path) restituisce INVALID.

### 1.5 Storage Namespace e Confinamento
[NORMATIVE REQUIREMENT]
Dato il percorso radice assoluto STORAGE_ROOT sul filesystem host:
    JOURNAL_PATH := STORAGE_ROOT + "/tx.json"
    STAGING_PATH := STORAGE_ROOT + "/__staging__"
    BACKUP_PATH  := STORAGE_ROOT + "/__backup__"
    OUTPUT_PATH  := STORAGE_ROOT + "/OUTPUT_DIR"

1. Atomic Rename Domain: STAGING_PATH, BACKUP_PATH e OUTPUT_PATH MUST risiedere sul medesimo volume storage e medesimo filesystem logico host.
2. Definizione di ContieneLinkOIndirezioni(H, path):
   Sia AllPhysicalEntries(H, path) l'insieme di tutte le entita' fisiche presenti al di sotto di path nello stato host H.
   ContieneLinkOIndirezioni(H, path) -> Boolean:
     RETURN TRUE se path stesso o qualsiasi entry in AllPhysicalEntries(H, path) e':
       un link simbolico, una directory junction, un mount point,
       un Windows reparse point, oppure un file con indicazione filesystem
       di hard link count > 1.
     Altrimenti RETURN FALSE.
   La presenza di qualsiasi indirezione determina l'esito INVALID.

---

## 2. CODEC CANONICO DI ESCAPING E IDENTITA' DEI TOKEN

### 2.1 Linguaggio dei Placeholder Sintetici (L_ph)
[NORMATIVE REQUIREMENT]
* Carattere di Fuga: CHAR_ESC := U+005C (Reverse Solidus)
* Carattere Delimitatore: CHAR_DELIM := U+00A7 (Section Sign)
* Notazione di Sequenza Delimitatore: DELIM_SEQ := [U+00A7, U+00A7] (sequenza di due code point U+00A7 consecutivi)
* Linguaggio dei Placeholder:
    L_ph := { DELIM_SEQ + TokenType + ":" + TokenID + DELIM_SEQ |
              TokenType in {'s', 'b', 'h', 'c'} AND TokenID in [0-9a-f]{64} }
  La lunghezza di ogni elemento in L_ph e' esattamente pari a 70 Unicode Scalar Values.

### 2.2 Funzioni Scalari Pure E(T) e D(T_prime)
[NORMATIVE REQUIREMENT]
Sia T in SIGMA* con L = len(T). La funzione pura E : SIGMA* -> SIGMA* e' definita da:

    E(T):
      T_out = ""
      k = 0
      Mentre k < L:
        IF T[k] == U+005C:
          T_out = T_out + [U+005C, U+005C]
          k = k + 1
        ELSE IF T[k] == U+00A7:
          T_out = T_out + [U+005C, U+00A7]
          k = k + 1
        ELSE:
          T_out = T_out + T[k]
          k = k + 1
      Ritorna T_out

Sia T_prime in SIGMA* con L_prime = len(T_prime). La funzione pura D : SIGMA* -> SIGMA* e' definita da:

    D(T_prime):
      T_orig = ""
      k = 0
      Mentre k < L_prime:
        IF (k + 1 < L_prime) AND (T_prime[k] == U+005C) AND (T_prime[k+1] == U+005C):
          T_orig = T_orig + U+005C
          k = k + 2
        ELSE IF (k + 1 < L_prime) AND (T_prime[k] == U+005C) AND (T_prime[k+1] == U+00A7):
          T_orig = T_orig + U+00A7
          k = k + 2
        ELSE:
          T_orig = T_orig + T_prime[k]
          k = k + 1
      Ritorna T_orig

### 2.3 Teorema di Left-Inverse, Biiezione su Im(E) e Disgiunzione
[STRUCTURAL INVARIANT]
1. Left-Inverse Globale su SIGMA*:
    FORALL T in SIGMA*: D(E(T)) == T    (ovvero: D o E == id_SIGMA*)
2. Biiezione sull'Immagine Im(E):
   Sia Im(E) := { E(T) | T in SIGMA* } SUBSET SIGMA*.
   La funzione E : SIGMA* -> Im(E) e' biiettiva e la sua inversa formale e' la restrizione di D a Im(E):
    E^(-1) == D|Im(E)
    FORALL T_prime in Im(E): E(D(T_prime)) == T_prime
   E' formalmente vietato affermare che D sia l'inversa di E su tutto SIGMA*, poiche' D non e' iniettiva al di fuori di Im(E).
3. Invariante di Disgiunzione da L_ph:
   Per costruzione di E, ogni occorrenza di U+00A7 in E(T) e' preceduta da U+005C:
    FORALL j in [0..len(E(T))-1]: (E(T)[j] == U+00A7 => (j >= 1 AND E(T)[j-1] == U+005C))
   Di conseguenza, la sottostringa DELIM_SEQ = [U+00A7, U+00A7] non puo' comparire in alcuna posizione di E(T):
    DELIM_SEQ NOT IN Substrings_2(E(T)) => Substrings_70(E(T)) INTERSECT L_ph == EMPTY_SET

### 2.4 Primitiva ExtractBlocks
[NORMATIVE REQUIREMENT]
Dato il testo T in SIGMA* e gli intervalli protetti Z = { < tau_1, [z_s1, z_e1) >, ..., < tau_K, [z_sK, z_eK) > }, dove tau_k in {'s', 'b', 'h', 'c'} e 0 <= z_sk < z_ek <= len(T):
    ExtractBlocks(T, Z) -> Sequence(Block)
    Block_k := < tau_k, K_k, [z_sk, z_ek) >
    K_k := T[z_sk : z_ek] in SIGMA+    (payload non vuoto)
    TokenID(K_k) := HexLowerCase(SHA256(EncodeStrictUTF8(K_k))) in [0-9a-f]{64}

### 2.5 Regola Semantica di Tipo e Conflitti (Errori 21, 22)
[NORMATIVE REQUIREMENT]
Vincolo Semantico di Tipo: Tutti i blocchi con identico contenuto K MUST possedere identico TokenType.
La mappa dei token e' l'accumulatore TokenMap : TokenID -> < TokenType, K >.

    RegisterToken(TokenMap, < tau_curr, K_curr >):
      id_curr = TokenID(K_curr)
      IF id_curr NOT IN keys(TokenMap):
        TokenMap_next = TokenMap UNION { id_curr |-> < tau_curr, K_curr > }
        RETURN < TokenMap_next, SUCCESS >
      ELSE:
        IF TokenMap[id_curr].K != K_curr:
          RETURN < TokenMap, SemanticError(21) >    [ERR_TOKEN_COLLISION]
        ELSE IF TokenMap[id_curr].tau != tau_curr:
          RETURN < TokenMap, SemanticError(22) >    [ERR_MAPPING_CONFLICT]
        ELSE:
          RETURN < TokenMap, SUCCESS >              [Deduplicazione idempotente]

### 2.6 Scansione Deterministica di ParsePlaceholders (Errore 20)
[NORMATIVE REQUIREMENT]
La funzione ParsePlaceholders opera su sequenze c in SIGMA*:

    ParsePlaceholders(c):
      records = ()
      k = 0
      L = len(c)
      Mentre k < L:
        IF (k + 1 < L) AND (c[k] == U+00A7) AND (c[k+1] == U+00A7):
          IF k + 70 > L:
            RETURN SemanticError(20)                [ERR_MALFORMED_PLACEHOLDER]
          w = c[k : k+70]
          IF w NOT IN L_ph:
            RETURN SemanticError(20)                [ERR_MALFORMED_PLACEHOLDER]
          type = w[2]
          id = w[4 : 68]
          records = records + ( < type, id, k > )
          k = k + 70
        ELSE:
          k = k + 1
      RETURN Success(records)

Dato l'esito Success(records) di ParsePlaceholders(c), la funzione ausiliaria PlaceholdersIn(c) restituisce l'insieme dei TokenID identificati:
    PlaceholdersIn(c) := { rec.id | rec in records }

---

# PARTE II -- SERIALIZATION, RECONSTRUCTION & VERIFICATION

---

## 3. CANONICAL JSON OUTPUT CONTRACT (CJOC) E RICOSTRUZIONE FILE

### 3.1 Canonical JSON Output Contract (CJOC)
[NORMATIVE REQUIREMENT]
La funzione Serialize(Doc) -> ByteString produce una sequenza deterministica conforme a:
1. Codifica: UTF-8 standard senza BOM (RFC 3629).
2. Ordinamento Chiavi: Lessicografico crescente basato sul confronto byte-a-byte dei valori UTF-8 delle chiavi.
3. Indentazione: Rigorosamente 2 spazi U+0020 U+0020 per livello di profondita'.
4. Separatori: Chiave-valore espressa da ": " (U+003A U+0020); elementi di array e oggetti separati da "," (U+002C) seguito da "\n" (U+000A).
5. Terminatore di Linea: Singolo "\n" (U+000A), con un "\n" terminale obbligatorio a fine file.
6. Dominio Numerico: Interi a 64-bit non negativi nel range [0, 9007199254740991] (2^53 - 1, Safe Integer Limit IEEE 754). Floating point ("1.0"), notazione esponenziale ("1e0"), zeri iniziali ("01") o segni negativi ("-1") sono VIETATI.
7. String Escaping: Solo ed esclusivamente i caratteri obbligatori per RFC 8259:
   * Quotation mark: '\"' (U+005C U+0022)
   * Reverse solidus: '\\' (U+005C U+005C)
   * Caratteri di controllo [U+0000..U+001F]: sequenza \u00xx con esadecimale minuscolo.
   * Tutti gli altri caratteri >= U+0020 (incluso '/', U+002F) MUST NOT essere escapati e devono essere emessi come byte UTF-8 letterali.

### 3.2 Tipi Numerici Interoperabili ed Aritmetica Esatta
[NORMATIVE REQUIREMENT]
La verifica numerica opera sulla forma lessicale ASCII originale presente nel flusso JSON:
    IsInteger(x)    <==> IsJSONNumber(x) AND (RawJSONLexicalForm(x) matches "^[0-9]+$")
    IsUInt53(x)     <==> IsInteger(x) AND (0 <= x) AND (x <= 9007199254740991)
    IsPosUInt53(x)  <==> IsInteger(x) AND (1 <= x) AND (x <= 9007199254740991)

Tutti i conteggi di scalari e somme di byte sono interi matematici esatti. Se durante la validazione un totale parziale o cumulativo supera 9007199254740991, l'operazione restituisce INVALID.

### 3.3 Regole di Parsing JSON e Closed-World Schema
[NORMATIVE REQUIREMENT]
1. ParseJSON(bytes) MUST rigettare con errore PARSE_ERROR qualsiasi documento contenente nomi di membro duplicati all'interno del medesimo oggetto o non conformita' a RFC 8259.
2. Tutti i documenti JSON normativi (manifest.json, reverse_map.json, tx.json) hanno schema chiuso: la presenza di qualsiasi chiave non definita dalla specifica causa l'emissione di INVALID (per i manifest e reverse_map) o CORRUPT (per il journal).
3. Relazione tra TokenMap e reverse_map.json: reverse_map.json e' la serializzazione CJOC esatta del documento contenente l'oggetto globale "placeholders", in cui keys(reverse_map.placeholders) == keys(TokenMap) e reverse_map.placeholders[id] == { "payload": TokenMap[id].K, "token_type": TokenMap[id].tau }.

### 3.4 Naming Normativo dei Chunk File (ChunkFileName) e Ownership
[NORMATIVE REQUIREMENT]
Dato l'indice progressivo del chunk i in [1..2^53 - 1], la funzione ChunkFileName e' definita da:
    ChunkFileName(i) :=
      IF 1 <= i <= 9999 THEN PadZero4(i) + ".txt"
      ELSE ToString(i) + ".txt"

Ogni record c in manifest.chunks contiene obbligatoriamente ed esclusivamente le seguenti chiavi:
* c.byte_length_utf8 in [0..2^53 - 1].
* c.code_point_count in [0..2^53 - 1].
* c.file_path in P_canon: percorso canonico del file (c.file_path in keys(manifest.files)).
* c.index in [1..2^53 - 1]: indice sequenziale del chunk nel file.
* c.relative_path in P_canon: la stringa esatta c.file_path + "/" + ChunkFileName(c.index).
* c.sha256 in [0-9a-f]{64} (esadecimale minuscolo).

Invariante di Partizione dei Chunk:
Per ogni c in manifest.chunks esiste uno e un solo f in keys(manifest.files) tale che c.file_path == f.
Inoltre:
    FORALL c1, c2 in manifest.chunks: (c1 != c2 => c1.relative_path != c2.relative_path)

### 3.5 Funzione Canonica ManifestHash e BackupIdentity
[NORMATIVE REQUIREMENT]
La funzione pura ManifestHash e' definita sui byte esatti del documento manifest.json:
    ManifestHash(manifest_bytes) := HexLowerCase(SHA256(manifest_bytes)) in [0-9a-f]{64}

L'identita' di una directory di backup e' definita da:
    BackupIdentity(H, path) -> < generation_id, manifest_hash > | ABSENT:
      IF ValidateDataset(H, path) == INVALID:
        RETURN ABSENT
      manifest_bytes = LeggiByte(H, path + "/manifest.json")
      manifest = ParseJSON(manifest_bytes)
      RETURN < manifest.generation_id, ManifestHash(manifest_bytes) >

### 3.6 Primitiva Deterministica ReconstructFile(H, path, f, manifest)
[NORMATIVE REQUIREMENT]
    ReconstructFile(H, path, f, manifest) -> < code_point_count, byte_length_utf8, sha256_full, total_chunks > | INVALID:
      0. IF NOT (f in P_canon):
           RETURN INVALID
      1. Sia K_f la lista dei record c in manifest.chunks con c.file_path == f.
      2. Sia N_f = len(K_f). IF N_f == 0: RETURN INVALID.
      3. Ordina K_f per valore crescente di c.index.
      4. FORALL j in [1..N_f]:
           IF K_f[j].index != j: RETURN INVALID.
           expected_rel_path = f + "/" + ChunkFileName(j)
           IF K_f[j].relative_path != expected_rel_path: RETURN INVALID.
           chunk_file_path = path + "/" + expected_rel_path
           IF NOT (chunk_file_path esiste su H AND Leggibile(H, chunk_file_path)):
             RETURN INVALID
           chunk_bytes = LeggiByte(H, chunk_file_path)
           IF NOT IsValidStrictUTF8(chunk_bytes):
             RETURN INVALID
           IF HexLowerCase(SHA256(chunk_bytes)) != K_f[j].sha256:
             RETURN INVALID
           T_chunk_j = DecodeStrictUTF8(chunk_bytes)
           IF len(T_chunk_j) != K_f[j].code_point_count:
             RETURN INVALID
           IF len(chunk_bytes) != K_f[j].byte_length_utf8:
             RETURN INVALID
      5. T_file = Concat(T_chunk_1, T_chunk_2, ..., T_chunk_N_f)
      6. file_bytes = EncodeStrictUTF8(T_file)
      7. RETURN < len(T_file), len(file_bytes), HexLowerCase(SHA256(file_bytes)), N_f >

### 3.7 Funzione Canonica ValidateDataset(H, path)
[NORMATIVE REQUIREMENT]
    ValidateDataset(H, path) -> < VALID, BackupIdentity > | INVALID:
      manifest_path = path + "/manifest.json"
      IF NOT (manifest_path esiste su H AND Leggibile(H, manifest_path)):
        RETURN INVALID

      manifest_bytes = LeggiByte(H, manifest_path)
      IF NOT (IsValidStrictUTF8(manifest_bytes) AND IsConformingCJOC(manifest_bytes)):
        RETURN INVALID

      manifest = ParseJSON(manifest_bytes)
      IF manifest == PARSE_ERROR OR NOT IsJSONObject(manifest):
        RETURN INVALID

      (* 1. Verifica Closed-World Schema Radice *)
      expected_root_keys = { "byte_length_utf8", "chunks", "files", "generation_id",
                             "generator", "language_profile", "mode",
                             "total_chunks", "total_scalar_values" }
      IF keys(manifest) != expected_root_keys:
        RETURN INVALID

      IF NOT (manifest.generator == "ULRP-SPEC-1.6" AND
              manifest.mode == "lossless" AND
              manifest.language_profile == "default-closed-world" AND
              IsUInt53(manifest.generation_id) AND
              IsPosUInt53(manifest.total_chunks) AND
              IsUInt53(manifest.total_scalar_values) AND
              IsUInt53(manifest.byte_length_utf8) AND
              IsJSONArray(manifest.chunks) AND
              IsJSONObject(manifest.files) AND
              manifest.total_chunks == len(manifest.chunks)):
        RETURN INVALID

      (* 2. Verifica Closed-World Schema e Tipi di manifest.files *)
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

      (* 3. Verifica Closed-World Schema e Tipizzazione Rigorosa dei Chunk *)
      expected_chunk_keys = { "byte_length_utf8", "code_point_count", "file_path", "index", "relative_path", "sha256" }
      declared_paths = EMPTY_SET
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
        IF c.relative_path in declared_paths:
          RETURN INVALID
        declared_paths = declared_paths UNION { c.relative_path }

      (* 4. Ricostruzione, Catena Byte Length e SHA-256 *)
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
        IF total_scalars_calc > 9007199254740991 OR total_bytes_calc > 9007199254740991:
          RETURN INVALID

      IF total_scalars_calc != manifest.total_scalar_values:
        RETURN INVALID
      IF total_bytes_calc != manifest.byte_length_utf8:
        RETURN INVALID

      (* 5. Chiusura del Namespace Fisico *)
      declared_files = { "manifest.json" } UNION declared_paths
      IF ListaTuttiIFilesRelativi(H, path) != declared_files:
        RETURN INVALID
      IF ListaTutteLeDirectoryRelative(H, path) != DeclaredParentDirs(declared_files):
        RETURN INVALID
      IF ContieneLinkOIndirezioni(H, path):
        RETURN INVALID

      identity = < manifest.generation_id, ManifestHash(manifest_bytes) >
      RETURN < VALID, identity >

---

# PARTE III -- PARTITIONING ALGORITHM & PIPELINE

---

## 4. PARTITIONING DETERMINISTICO, PLACEHOLDER SUBSTITUTION E ROUNDTRIP (RIC)

### 4.1 Mappatura degli Indici tra Testo Originale ed Escaped (EscapeMap_T)
[NORMATIVE REQUIREMENT]
Dato il testo originale T_orig in SIGMA* (L_orig = len(T_orig)) e il testo escaped T_esc = E(T_orig) (L_esc = len(T_esc)), la corrispondenza biunivoca degli indici e' definita da:
    EscapeMap_T : [0..L_orig] -> [0..L_esc]
    EscapeMap_T(k) := k + count_{0 <= i < k}( T_orig[i] == U+005C OR T_orig[i] == U+00A7 )

Dato l'insieme di intervalli protetti Z = { < tau_k, [z_sk, z_ek) > } su T_orig, l'insieme trasformato Z_esc su T_esc mantiene esplicitamente il payload originale K_k come metadato semantico associato:
    Z_esc := { < tau_k, [ EscapeMap_T(z_sk), EscapeMap_T(z_ek) ), K_k > |
               < tau_k, [z_sk, z_ek) > in Z AND K_k == T_orig[z_sk : z_ek] }

Invariante di Corrispondenza Escaped:
Per ciascun elemento < tau_k, [z'_sk, z'_ek), K_k > in Z_esc:
    z'_sk == EscapeMap_T(z_sk)
    z'_ek == EscapeMap_T(z_ek)
    T_esc[z'_sk : z'_ek] == E(K_k)

L'inclusione di K_k nella tupla costituisce unicamente metadato semantico di riferimento e non altera la lunghezza ne' le coordinate di T_esc.

### 4.2 Confini di Riga B(T_esc) e CollidingInterval
[NORMATIVE REQUIREMENT]
L'insieme dei confini di riga validi B(T_esc) per T_esc e':
    B(T_esc) := { p in [1..L_esc] | T_esc[p-1] == U+000A 
                 OR (p >= 2 AND T_esc[p-2] == U+000D AND T_esc[p-1] == U+000A) }

La funzione CollidingInterval(p, Z_esc) e' definita da:
    CollidingInterval(p, Z_esc) :=
      [z_s_esc, z_e_esc)   se esiste < tau, [z_s_esc, z_e_esc), K > in Z_esc tale che z_s_esc < p < z_e_esc
      EMPTY_SET            altrimenti (inclusi i casi esatti p == z_s_esc e p == z_e_esc)

### 4.3 Funzioni Partition e SplitPoint
[NORMATIVE REQUIREMENT]
    Partition(T_esc, S_target, R_min_pct, Z_esc) -> Sequence(RawChunk):
      L_esc = len(T_esc)
      IF L_esc == 0:
        RETURN ( "" )

      raw_chunks = ()
      C_start = 0
      Mentre C_start < L_esc:
        C_split = SplitPoint(T_esc, C_start, S_target, R_min_pct, Z_esc)
        IF C_split <= C_start:
          ABORT SemanticError(30)               [ERR_PARTITION_VIOLATION]
        raw_chunks = raw_chunks + ( T_esc[C_start : C_split] )
        C_start = C_split
      RETURN raw_chunks

    SplitPoint(T, C_start, S_target, R_min_pct, Z_esc):
      L = len(T)
      IF (L - C_start) <= S_target:
        RETURN L

      S_min = floor((R_min_pct * S_target) / 100)
      C_ideal = C_start + S_target

      (* Gestione Oversize all'inizio del chunk *)
      IF EXISTS < tau, [z_s, z_e), K > in Z_esc tale che z_s == C_start AND (z_e - z_s) > S_target:
        RETURN z_e

      (* Gestione Oversize nella finestra *)
      IF EXISTS < tau, [z_s, z_e), K > in Z_esc tale che C_start < z_s < C_ideal AND (z_e - z_s) > S_target:
        RETURN z_s

      (* Scansione Confini di Riga Primari: limite inferiore strettamente maggiore di C_start *)
      B_primary = { p in B(T) | (C_start + max(1, S_min)) <= p <= C_ideal }
      IF B_primary != EMPTY_SET:
        p = max(B_primary)
        match = CollidingInterval(p, Z_esc)
        IF match == EMPTY_SET:
          RETURN p
        ELSE IF match.z_s > C_start:
          RETURN match.z_s

      (* Scansione Confini di Riga Secondari *)
      B_secondary = { p in B(T) | C_start < p < (C_start + max(1, S_min)) }
      IF B_secondary != EMPTY_SET:
        p = max(B_secondary)
        match = CollidingInterval(p, Z_esc)
        IF match == EMPTY_SET:
          RETURN p
        ELSE IF match.z_s > C_start:
          RETURN match.z_s

      (* Fallback Infra-Linea *)
      match = CollidingInterval(C_ideal, Z_esc)
      IF match == EMPTY_SET:
        RETURN C_ideal
      ELSE IF match.z_s > C_start:
        RETURN match.z_s
      ELSE:
        RETURN match.z_e

### 4.4 Primitiva Deterministica ApplyPlaceholders
[NORMATIVE REQUIREMENT]
La funzione pura ApplyPlaceholders opera post-partizionamento sul singolo chunk escapato grezzo c_esc == T_esc[C_start : C_split], sostituendo i blocchi protetti con i rispettivi placeholder sintetici in L_ph:

    ApplyPlaceholders(c_esc, C_start, C_split, Z_esc) -> String:
      c_out = ""
      curr = C_start
      Z_chunk = { < tau, [z_s, z_e), K > in Z_esc | C_start <= z_s AND z_e <= C_split }
      Ordina Z_chunk per valore di z_s crescente

      Per ciascun < tau_k, [z_sk, z_ek), K_k > in Z_chunk:
        (* Copia testo non protetto precedente al blocco *)
        c_out = c_out + c_esc[ (curr - C_start) : (z_sk - C_start) ]
        (* Generazione del placeholder deterministico *)
        id_k = TokenID(K_k)
        P_k = [ U+00A7, U+00A7 ] + tau_k + ":" + id_k + [ U+00A7, U+00A7 ]
        c_out = c_out + P_k
        curr = z_ek

      (* Copia testo non protetto finale *)
      c_out = c_out + c_esc[ (curr - C_start) : (C_split - C_start) ]
      RETURN c_out

Regola di Invalidazione delle Coordinate:
Dopo l'invocazione di ApplyPlaceholders, le coordinate di Z_esc non corrispondono piu' alle posizioni dei caratteri nel chunk trasformato c_out a causa della sostituzione di blocchi di lunghezza arbitraria con placeholder di lunghezza fissa 70. Le coordinate di Z_esc MUST NOT essere utilizzate per indicizzare o manipolare c_out.

### 4.5 Invarianti del Partizionamento e Atomicita' dei Placeholder
[STRUCTURAL INVARIANT]
1. Progresso Stretto: Per ogni iterazione di Partition, SplitPoint restituisce C_split tale che C_split - C_start >= 1. Quando S_min == 0, la condizione (C_start + max(1, S_min)) <= p garantisce che C_start non appartenga a B_primary, prevenendo split nulli.
2. Cardinalita' dei Chunk: Il numero totale di chunk emessi N soddisfa 1 <= N <= max(1, L_esc).
3. Atomicita' dei Token e dei Placeholder:
   Per ogni punto di split C_split calcolato da SplitPoint e per ogni intervallo < tau, [z_s, z_e), K > in Z_esc:
       C_split <= z_s  OR  C_split >= z_e
   Di conseguenza, nessun intervallo protetto E(K_k) e' diviso tra due chunk grezzi adiacenti. Ciascun blocco E(K_k) appartiene interamente ad un singolo raw chunk e viene trasformato integralmente in un singolo placeholder P_k all'interno del corrispondente chunk finale c_out.

### 4.6 Primitiva Resolve e Predicati RIC-1 .. RIC-5
[NORMATIVE REQUIREMENT]
La funzione pura Resolve : SIGMA* x TokenMap -> SIGMA* sostituisce ciascun placeholder sintetico con la forma escaped del payload originale E(TokenMap[id].K):

    Resolve(T_comp, TokenMap):
      T_out = ""
      k = 0
      L = len(T_comp)
      Mentre k < L:
        IF (k + 70 <= L) AND (T_comp[k : k+70] IN L_ph):
          token_str = T_comp[k : k+70]
          type = token_str[2]
          id = token_str[4 : 68]
          IF id NOT IN keys(TokenMap):
            ABORT SemanticError(40)
          IF TokenMap[id].tau != type:
            ABORT SemanticError(40)
          T_out = T_out + E(TokenMap[id].K)
          k = k + 70
        ELSE:
          T_out = T_out + T_comp[k]
          k = k + 1
      Ritorna T_out

Dato T_comp := Concat(c_1, ..., c_N), i predicati di Roundtrip Integrity (RIC-1 .. RIC-5) sono definiti da:
* RIC-1: Concat(c_1, ..., c_N) == T_comp
* RIC-2: FORALL i in [1..N]: HexLowerCase(SHA256(EncodeStrictUTF8(c_i))) == chunk_i.sha256
* RIC-3: ParsePlaceholders(T_comp) == SUCCESS
* RIC-4: FORALL i in [1..N]:
    keys(c_i.mapping_subset) == PlaceholdersIn(c_i) AND
    c_i.mapping_subset == Restriction(TokenMap, PlaceholdersIn(c_i))
* RIC-5: EncodeStrictUTF8(D(Resolve(T_comp, TokenMap))) == B_raw

### 4.7 Pipeline Sequenziale Totale di F_sem
[NORMATIVE REQUIREMENT]
Dato SortedFiles(D_raw) ordinato per confronto lessicografico byte-a-byte dei percorsi:

    F_sem(D_raw, C_raw):
      FASE 1 -- VALIDAZIONE INGESTIONE UTF-8 (Priorita' 10):
        Per ciascun < P_j, B_j > in SortedFiles(D_raw):
          IF NOT IsValidStrictUTF8(B_j): RETURN SemanticError(10)

      FASE 2 -- VALIDAZIONE PERCORSI CANONICI (Priorita' 11):
        Per ciascun < P_j, B_j > in SortedFiles(D_raw):
          IF P_j NOT in P_canon: RETURN SemanticError(11)

      FASE 3 -- VALIDAZIONE CONFIGURAZIONE (Priorita' 12):
        IF S_target_raw < 64 OR R_min_raw not in [1..100] OR NOT IsValidZ(Z_raw):
          RETURN SemanticError(12)

      FASE 4 -- TOKENIZZAZIONE E CONTROLLO COLLISIONI (Priorita' 21, 22):
        TokenMap = EMPTY_MAP
        Per ciascun < P_j, B_j > in SortedFiles(D_raw):
          T_orig_j = DecodeStrictUTF8(B_j)
          blocks = ExtractBlocks(T_orig_j, Z_j)
          Per ciascun block in blocks:
            < TokenMap, status > = RegisterToken(TokenMap, < block.tau, block.K >)
            IF status != SUCCESS: RETURN status

      FASE 5 -- PARTIZIONAMENTO E SOSTITUZIONE PLACEHOLDER (Priorita' 30):
        DatasetChunks = ()
        Per ciascun < P_j, B_j > in SortedFiles(D_raw):
          T_orig_j = DecodeStrictUTF8(B_j)
          T_esc_j = E(T_orig_j)
          Z_esc_j = { < tau_k, [ EscapeMap_{T_orig_j}(z_sk), EscapeMap_{T_orig_j}(z_ek) ), T_orig_j[z_sk : z_ek] > |
                      < tau_k, [z_sk, z_ek) > in Z_j }
          raw_chunks = Partition(T_esc_j, S_target, R_min_pct, Z_esc_j)
          
          (* Invariante Raw: Concat(raw_chunks) == T_esc_j *)
          chunks_j = ()
          C_start = 0
          Per ciascun raw_c in raw_chunks:
            C_split = C_start + len(raw_c)
            chunk_ph = ApplyPlaceholders(raw_c, C_start, C_split, Z_esc_j)
            chunks_j = chunks_j + ( chunk_ph )
            C_start = C_split
          
          DatasetChunks = DatasetChunks UNION { P_j |-> chunks_j }

      FASE 6 -- VERIFICA STRUTTURALE E ROUNDTRIP RIC (Priorita' 20, 40):
        Per ciascun < P_j, B_j > in SortedFiles(D_raw):
          chunks_j = DatasetChunks[P_j]
          T_comp_j = Concat(chunks_j)
          IF ParsePlaceholders(T_comp_j) != SUCCESS:
            RETURN SemanticError(20)
          Per ciascun chunk c_i in chunks_j:
            IF ParsePlaceholders(c_i) != SUCCESS:
              RETURN SemanticError(20)
          IF NOT ( RIC_1_to_5_Hold(B_j, chunks_j, T_comp_j, TokenMap) ):
            RETURN SemanticError(40)

      FASE 7 -- EMISSIONE SUCCESSO:
        RETURN Success(O_semantic)

### 4.8 Invariante Centrale di Risoluzione e Reversibilita' Lossless
[STRUCTURAL INVARIANT]
Per ogni file valido B_raw con testo decodificato T_orig in SIGMA*, rappresentato come:
    T_orig = U_0 + K_1 + U_1 + ... + K_m + U_m
dove U_i sono segmenti non protetti e K_k sono i blocchi protetti associati ai placeholder P_k in L_ph, si ha:
    T_esc  = E(U_0) + E(K_1) + E(U_1) + ... + E(K_m) + E(U_m)
    T_comp = E(U_0) + P_1    + E(U_1) + ... + P_m    + E(U_m)

Dalla definizione di Resolve (Section 4.6), poiche' ciascun P_k viene sostituito con E(TokenMap[id_k].K) == E(K_k):
    Resolve(T_comp, TokenMap) == E(T_orig)

Applicando la funzione pura di decodifica escaping D:
    D(Resolve(T_comp, TokenMap)) == D(E(T_orig))

Per il Teorema 2.3 (Invariante 1: D(E(T)) == T per ogni T in SIGMA*):
    D(Resolve(T_comp, TokenMap)) == T_orig

Ne consegue l'invarianza esatta a livello binario:
    EncodeStrictUTF8(D(Resolve(T_comp, TokenMap))) == EncodeStrictUTF8(T_orig) == B_raw

---

# PARTE IV -- PERSISTENCE, COMMIT & CRASH RECOVERY

---

## 5. CONTRATTO DELLE PRIMITIVE DI STORAGE, COMMIT PIPELINE E PROGRESSIONE

### 5.1 Contratti Astratti delle Primitive di Storage
[NORMATIVE REQUIREMENT]
1. WriteAtomic(path, bytes) -> Status (SUCCESS | FAIL):
   * Scrittura crash-atomic di metadati su file singolo (JOURNAL_PATH o staging manifest).
   * SUCCESS: path contiene integralmente bytes, conformemente al contratto di persistenza.
   * FAIL / Crash in F_crash: path rimane nello stato precedente, oppure risulta ABSENT o CORRUPT.
2. RemoveIfExists(path) -> Status (SUCCESS | FAIL):
   * Rimozione idempotente di path.
   * Invariante su Directory (STAGING_PATH, BACKUP_PATH): Se interrotta da un crash in F_crash, lo stato risultante soddisfa ClassifyPath(H_crash, path) in {ABSENT, CORRUPT} e riduce strettamente RemainingCount(H_crash, path) non appena avviene un avanzamento fisico.
   * Invariante su Journal File (JOURNAL_PATH): Se interrotta da un crash in F_crash, ClassifyJournal(H_crash, JOURNAL_PATH).tx_state in {ABSENT, CORRUPT, STAGED, COMMITTED}.
3. RenameIfAbsent(source, target) -> Status (SUCCESS | FAIL):
   * Spostamento atomico di directory all'interno del medesimo Atomic Rename Domain.
   * Invariante Crash-Atomic: Dopo un crash in F_crash, o source e' integro e target e' ABSENT, oppure target e' presente integro e source e' ABSENT.
4. PersistBarrier() -> Status (SUCCESS | FAIL):
   * Operazione non mutante rispetto al namespace logico del filesystem.
   * SUCCESS: Conferma che tutte le mutazioni logiche precedentemente completate con SUCCESS sono durabili rispetto a qualsiasi successivo crash appartenente a F_crash.
   * FAIL / Crash in F_crash: Indica la mancata conferma di durabilita', ma MUST NOT alterare il namespace logico o introdurre corruzioni parziali su stati di dataset precedentemente validi.
   * Clausola di Esclusione: PersistBarrier NON garantisce la sopravvivenza a guasti fisici permanenti del supporto (F_hardware_decay).

### 5.2 Funzioni di Classificazione dello Stato Host
[NORMATIVE REQUIREMENT]
    ClassifyPath(H, path) -> { ABSENT, VALID, CORRUPT }:
      IF path e' fisicamente assente su H:
        RETURN ABSENT
      IF ValidateDataset(H, path) != INVALID:
        RETURN VALID
      RETURN CORRUPT

    ClassifyJournal(H, JOURNAL_PATH) -> < tx_state, tx_meta >:
      IF JOURNAL_PATH e' fisicamente assente su H:
        RETURN < ABSENT, ABSENT >
      IF JOURNAL_PATH esiste su H AND Leggibile(H, JOURNAL_PATH):
        bytes = LeggiByte(H, JOURNAL_PATH)
        IF IsValidStrictUTF8(bytes) AND IsConformingCJOC(bytes):
          doc = ParseJSON(bytes)
          IF doc != PARSE_ERROR AND IsJSONObject(doc):
            expected_journal_keys = { "source_generation", "source_manifest_hash", "state" }
            IF keys(doc) == expected_journal_keys:
              IF IsUInt53(doc.source_generation) AND IsHexLowerCase64(doc.source_manifest_hash):
                meta = < doc.source_generation, doc.source_manifest_hash >
                IF doc.state == "STAGED":
                  RETURN < STAGED, meta >
                ELSE IF doc.state == "COMMITTED":
                  RETURN < COMMITTED, meta >
      RETURN < CORRUPT, ABSENT >

### 5.3 Proiezione Pura StateOf(H) e MatchTransaction(S)
[NORMATIVE REQUIREMENT]
Invariante di Quiescenza del Recovery:
Durante l'intera esecuzione di RecoveryProcedure, nessun processo concorrente modifica i percorsi di STORAGE_ROOT ne' la configurazione HostConfiguredTargetMeta(H).

Lo spazio discreto degli stati di base (finite base status-state space) e' formato dal prodotto cartesiano dei quattro vettori di stato:
4 tx_state values x 3 staging statuses x 3 backup statuses x 3 output statuses = 108 combinazioni di base.

I metadati tx_meta, backup_meta e target_meta non costituiscono ulteriori dimensioni nello spazio finito dei base status states; essi influenzano le decisioni di recovery esclusivamente attraverso la valutazione del predicato booleano deterministico MatchTransaction(S) in {TRUE, FALSE}.

    StateOf(H) := < tx_state, staging_status, backup_status, output_status, tx_meta, backup_meta, target_meta >
dove:
* < tx_state, tx_meta > := ClassifyJournal(H, JOURNAL_PATH).
* staging_status := ClassifyPath(H, STAGING_PATH).
* backup_status := ClassifyPath(H, BACKUP_PATH).
* output_status := ClassifyPath(H, OUTPUT_PATH).
* backup_meta := IF backup_status == VALID THEN ValidateDataset(H, BACKUP_PATH).identity ELSE ABSENT.
* target_meta := HostConfiguredTargetMeta(H).

    MatchTransaction(S) :=
      IF (S.tx_state in {STAGED, COMMITTED}) AND (S.tx_meta != ABSENT) AND (S.backup_status == VALID) AND (S.backup_meta != ABSENT):
        (S.backup_meta.generation_id == S.tx_meta.source_generation AND
         S.backup_meta.manifest_hash == S.tx_meta.source_manifest_hash)
      ELSE IF (S.tx_state == ABSENT) AND (S.backup_status == VALID) AND (S.backup_meta != ABSENT) AND (S.target_meta != ABSENT):
        (S.backup_meta.generation_id == S.target_meta.expected_generation_id AND
         S.backup_meta.manifest_hash == S.target_meta.expected_manifest_hash)
      ELSE:
        FALSE

### 5.4 CommitLinearizationPoint vs CommitDurabilityPoint
[NORMATIVE REQUIREMENT]
La sequenza di pubblicazione transazionale della pipeline e' rigorosamente ordinata come segue:

    FASE PUBBLICAZIONE:
      1. Generazione dataset completo in STAGING_PATH;
      2. PersistBarrier() == SUCCESS;
      3. ValidateDataset(H, STAGING_PATH) == VALID;
      4. WriteAtomic(JOURNAL_PATH, { state: "STAGED", source_generation: G_prev, source_manifest_hash: H_prev });
      5. PersistBarrier() == SUCCESS;
      6. IF OUTPUT_PATH esiste: RenameIfAbsent(OUTPUT_PATH, BACKUP_PATH);
      7. RenameIfAbsent(STAGING_PATH, OUTPUT_PATH);
      8. PersistBarrier() == SUCCESS;
      9. WriteAtomic(JOURNAL_PATH, { state: "COMMITTED", source_generation: G_prev, source_manifest_hash: H_prev });
         ===> [ COMMIT LINEARIZATION POINT ]
     10. PersistBarrier() == SUCCESS;
         ===> [ COMMIT DURABILITY POINT ]
     11. RemoveIfExists(BACKUP_PATH);
     12. RemoveIfExists(JOURNAL_PATH);
     13. PersistBarrier() == SUCCESS;
     14. RETURN Success(O_semantic) al chiamante.

Definizioni Temporali e Semantiche:
1. CommitLinearizationPoint: Coincide con il completamento con esito SUCCESS dell'invocazione WriteAtomic(JOURNAL_PATH, COMMITTED) (Passo 9).
   * Prima del CommitLinearizationPoint, la transazione e' logicamente in stato STAGED (o non iniziata);
   * Al completamento del Passo 9, la transazione e' logicamente linearizzata come COMMITTED nel journal di persistenza;
   * L'esito SUCCESS di WriteAtomic(JOURNAL_PATH, COMMITTED) indica la serializzazione logica della transazione, ma MUST NOT essere interpretato come durability acknowledgment per il chiamante.
2. CommitDurabilityPoint: Coincide con il completamento con esito SUCCESS dell'invocazione PersistBarrier() al Passo 10.
   * Il chiamante riceve la notifica Success(O_semantic) ONLY AFTER il CommitDurabilityPoint;
   * Se si verifica un crash in F_crash tra il Passo 9 e il Passo 10:
     - Se la scrittura del journal ha soddisfatto il contratto di persistenza, al riavvio ClassifyJournal rileva COMMITTED;
     - Se la scrittura non e' stata confermata, al riavvio ClassifyJournal rileva STAGED, CORRUPT o ABSENT conformemente al contratto di WriteAtomic.
   * In ogni caso in cui ClassifyJournal osservi COMMITTED dopo il reboot, il recovery protocol considera la transazione irrevocabilmente committed e procede con il consolidamento (Passi 11-13).
3. Invariante di Sequenza: La scrittura di COMMITTED al Passo 9 avviene esclusivamente DOPO che OUTPUT_PATH e' stato posizionato e validato (Passi 7-8).

### 5.5 Full Storage Progress Assumption
[NORMATIVE REQUIREMENT]
Sotto l'invariante di quiescenza e limitatamente ai guasti coperti da F_crash (escludendo F_hardware_decay permanente):
1. Ogni invocazione ritentata di WriteAtomic, RenameIfAbsent, RemoveIfExists e PersistBarrier, quando le relative precondizioni rimangono soddisfatte, completa con esito SUCCESS entro un numero finito di tentativi.
2. Per RemoveIfExists applicata a una directory di dataset, ogni tentativo interrotto che compie un avanzamento fisico riduce strettamente RemainingCount(H_crash, path), oppure lascia la directory in stato ABSENT o CORRUPT.
3. Le funzioni ClassifyJournal e ValidateDataset terminano deterministicamente in tempo finito.
4. Ogni ciclo di recovery rivaluta integralmente StateOf(H) e RecoveryDecision(StateOf(H)) a partire dallo stato host fisico corrente.
5. Le invocazioni di PersistBarrier(), incluse quelle interrotte da un crash in F_crash, sono non-mutanti rispetto al namespace logico del filesystem e non introducono mutazioni o corruzioni parziali su stati di dataset precedentemente validi.
6. I contratti delle primitive definiti in Section 5.1 sono sufficienti a vincolare tutti gli stati intermedi raggiungibili sotto F_crash a supporto del Teorema 2A.

---

## 6. DECISIONE ED ESECUZIONE DEL RECOVERY

### 6.1 Predicato Irrecoverable(S)
[NORMATIVE REQUIREMENT]
    Irrecoverable(S) <==>
      (S.output_status == CORRUPT)
      OR (S.tx_state == CORRUPT AND S.output_status != VALID)
      OR (S.tx_state == COMMITTED AND S.output_status != VALID)
      OR (S.output_status == ABSENT AND S.backup_status == CORRUPT)
      OR (S.output_status == ABSENT AND S.backup_status == VALID AND MatchTransaction(S) == FALSE)
      OR (S.output_status == ABSENT AND S.backup_status == ABSENT AND S.tx_state == STAGED)

Sia S_recoverable := { S in S | Irrecoverable(S) == FALSE }.

### 6.2 Funzione RecoveryDecision(S)
[NORMATIVE REQUIREMENT]
    RecoveryDecision(S):
      IF Irrecoverable(S) == TRUE:
        RETURN PLAN_ABORT

      ELSE IF (S.tx_state == COMMITTED) AND (S.output_status == VALID):
        RETURN PLAN_CONSOLIDATE_OUTPUT

      ELSE IF (S.tx_state in {ABSENT, STAGED}) AND (S.output_status == ABSENT) AND (S.backup_status == VALID) AND (MatchTransaction(S) == TRUE):
        RETURN PLAN_RESTORE_BACKUP

      ELSE IF (S.tx_state == ABSENT) AND (S.staging_status == ABSENT) AND (S.backup_status in {ABSENT, VALID}):
        RETURN PLAN_NOOP

      ELSE IF (S.staging_status != ABSENT) OR (S.tx_state == STAGED) OR (S.backup_status == CORRUPT) OR (S.tx_state == CORRUPT AND S.output_status == VALID):
        RETURN PLAN_CLEANUP_STAGING

      ELSE:
        RETURN PLAN_ABORT

[STRUCTURAL INVARIANT]
Lemma 2 (Precondizione per PLAN_CLEANUP_STAGING):
Per ogni S in S_recoverable, se RecoveryDecision(S) == PLAN_CLEANUP_STAGING, allora:
    (S.output_status == VALID) OR (S.output_status == ABSENT AND S.backup_status == ABSENT AND S.tx_state == ABSENT)

### 6.3 Funzione ExecuteRecovery
[NORMATIVE REQUIREMENT]
    ExecuteRecovery(Plan, H) -> RecoveryOutcome:
      S = StateOf(H)
      IF Plan != RecoveryDecision(S):
        RETURN FatalExecutionAbort(50)

      CASE Plan OF:

        PLAN_NOOP:
          RETURN Recovered(S)

        PLAN_CLEANUP_STAGING:
          IF RemoveIfExists(STAGING_PATH) == FAIL:
            RETURN FatalExecutionAbort(50)
          IF S.output_status == VALID AND S.backup_status == CORRUPT:
            IF RemoveIfExists(BACKUP_PATH) == FAIL:
              RETURN FatalExecutionAbort(50)
          IF RemoveIfExists(JOURNAL_PATH) == FAIL:
            RETURN FatalExecutionAbort(50)
          IF PersistBarrier() == FAIL:
            RETURN FatalExecutionAbort(50)
          RETURN Recovered(StateOf(H))

        PLAN_RESTORE_BACKUP:
          IF ValidateDataset(H, BACKUP_PATH) == INVALID:
            RETURN FatalExecutionAbort(50)
          IF MatchTransaction(StateOf(H)) == FALSE:
            RETURN FatalExecutionAbort(50)
          IF RemoveIfExists(STAGING_PATH) == FAIL:
            RETURN FatalExecutionAbort(50)
          IF RenameIfAbsent(BACKUP_PATH, OUTPUT_PATH) == FAIL:
            RETURN FatalExecutionAbort(50)
          IF RemoveIfExists(JOURNAL_PATH) == FAIL:
            RETURN FatalExecutionAbort(50)
          IF PersistBarrier() == FAIL:
            RETURN FatalExecutionAbort(50)
          RETURN Recovered(StateOf(H))

        PLAN_CONSOLIDATE_OUTPUT:
          IF ValidateDataset(H, OUTPUT_PATH) == INVALID:
            RETURN FatalExecutionAbort(50)
          IF RemoveIfExists(STAGING_PATH) == FAIL:
            RETURN FatalExecutionAbort(50)
          IF RemoveIfExists(BACKUP_PATH) == FAIL:
            RETURN FatalExecutionAbort(50)
          IF RemoveIfExists(JOURNAL_PATH) == FAIL:
            RETURN FatalExecutionAbort(50)
          IF PersistBarrier() == FAIL:
            RETURN FatalExecutionAbort(50)
          RETURN Recovered(StateOf(H))

        PLAN_ABORT:
          RETURN FatalExecutionAbort(50)

---

## 7. DIMOSTRAZIONI FORMALI

### 7.1 Insieme degli Stati Canonici Stabili
[STRUCTURAL INVARIANT]
Definiamo S_canonical := { S_A, S_B, S_C } dove:
* S_A := < ABSENT, ABSENT, ABSENT, VALID, ABSENT, ABSENT, target_meta > (Output valido, nessun artefatto).
* S_B := < ABSENT, ABSENT, VALID, VALID, ABSENT, backup_meta, target_meta > (Output valido, backup valido storico preservato).
* S_C := < ABSENT, ABSENT, ABSENT, ABSENT, ABSENT, ABSENT, target_meta > (Stato iniziale pulito).

### 7.2 Teorema di Idempotenza
[STRUCTURAL INVARIANT]
Sia RecoveryProcedure(H) := ExecuteRecovery(RecoveryDecision(StateOf(H)), H).

Teorema 1 (Idempotenza del Recovery):
Per ogni stato host H con StateOf(H) in S_recoverable, sotto i contratti delle primitive di Section 5.1 e l'invariante di quiescenza, in assenza di fallimenti operativi:
1. RecoveryProcedure(H) produce H' tale che StateOf(H') in S_canonical;
2. RecoveryDecision(StateOf(H')) == PLAN_NOOP;
3. RecoveryProcedure(H') == Recovered(StateOf(H')) senza compiere mutazioni su H'.

Dimostrazione:
1. Piani applicati:
   * PLAN_CONSOLIDATE_OUTPUT e PLAN_RESTORE_BACKUP rimuovono staging, backup e journal con output validato, producendo StateOf(H') = S_A in S_canonical.
   * PLAN_CLEANUP_STAGING rimuove staging, journal e backup se corrotto, producendo S_A (se backup assente/corrotto), S_B (se backup valido), o S_C (se output assente). In ogni caso StateOf(H') in S_canonical.
   * PLAN_NOOP lascia H inalterato con StateOf(H) in S_canonical.
2. Su S_A, S_B e S_C si ha tx_state == ABSENT, staging_status == ABSENT e backup_status in {ABSENT, VALID}. La clausola 4 di RecoveryDecision restituisce PLAN_NOOP.
3. ExecuteRecovery(PLAN_NOOP, H') restituisce Recovered(StateOf(H')) senza invocare primitive mutanti. Q.E.D.

### 7.3 Teoremi di Crash-Safety e Convergenza Operativa
[STRUCTURAL INVARIANT]
Teorema 2A (Decision-Level Crash-Safety Invariant):
Sia H_0 uno stato host iniziale tale che StateOf(H_0) in S_recoverable.
Sotto il Crash Fault Model F_crash, i contratti delle primitive di Section 5.1, l'invariante di quiescenza e il modello di esecuzione consentito per le primitive, ogni stato H_crash raggiungibile a seguito di un crash consentito durante ExecuteRecovery soddisfa:
    StateOf(H_crash) in S_recoverable AND RecoveryDecision(StateOf(H_crash)) != PLAN_ABORT

Dimostrazione per Analisi dei Piani:
1. Piani PLAN_CLEANUP_STAGING:
   * Per Lemma 2, S_0 soddisfa output_status == VALID oppure (output == ABSENT AND backup == ABSENT AND tx == ABSENT).
   * Un crash durante RemoveIfExists(STAGING_PATH) lascia staging in {ABSENT, CORRUPT} senza alterare output ne' backup => Irrecoverable(H_crash) == FALSE.
   * Un crash durante RemoveIfExists(BACKUP_PATH) (con output == VALID) lascia backup in {ABSENT, CORRUPT} con output == VALID => Irrecoverable(H_crash) == FALSE.
   * Un crash durante RemoveIfExists(JOURNAL_PATH) lascia tx_state in {ABSENT, CORRUPT, STAGED, COMMITTED}. Se output == VALID, per Section 6.1 nessuna clausola di Irrecoverable e' soddisfatta per alcuno dei 4 valori di tx_state. Se output == ABSENT, tx_state era gia' ABSENT prima dell'invocazione. In tutti i casi Irrecoverable(H_crash) == FALSE.
2. Piani PLAN_RESTORE_BACKUP:
   * S_0 soddisfa output == ABSENT, backup == VALID, MatchTransaction == TRUE, tx_state in {ABSENT, STAGED}.
   * Un crash durante RemoveIfExists(STAGING_PATH) non altera backup ne' journal => si riesegue PLAN_RESTORE_BACKUP.
   * Un crash durante RenameIfAbsent(BACKUP_PATH, OUTPUT_PATH) produce atomicamente o (backup == VALID AND output == ABSENT), rieseguendo PLAN_RESTORE_BACKUP, oppure (backup == ABSENT AND output == VALID), per cui output == VALID => Irrecoverable(H_crash) == FALSE.
   * Un crash durante RemoveIfExists(JOURNAL_PATH) avviene con output == VALID => Irrecoverable(H_crash) == FALSE.
3. Piani PLAN_CONSOLIDATE_OUTPUT:
   * S_0 soddisfa output == VALID e tx_state == COMMITTED.
   * Nessuna operazione muta OUTPUT_PATH. Qualsiasi interruzione durante la rimozione di staging, backup o journal lascia output == VALID invariato.
   * Poiche' output == VALID, per Section 6.1 Irrecoverable(H_crash) == FALSE per tutti i possibili stati residui di journal e backup.
4. Esclusione degli Stati Irrecuperabili:
   Sotto F_crash, i contratti delle primitive di Section 5.1, l'invariante di quiescenza e il modello di esecuzione consentito, nessun crash coperto dal modello puo' generare COMMITTED + OUTPUT_ABSENT o COMMITTED + OUTPUT_CORRUPT a partire da uno stato recuperabile.
   Tali stati rimangono classificati come PLAN_ABORT per preservare il commit invariant e proibire il rollback verso un backup obsoleto; essi appartengono strettamente a F_hardware_decay. Q.E.D.

Teorema 2B (Eventual Operational Convergence):
Sotto la Full Storage Progress Assumption (Section 5.5), qualsiasi sequenza di tentativi di ripristino interrotta da un numero finito di crash transitori in F_crash raggiunge un'esecuzione in cui tutte le primitive ritentate completano con SUCCESS, PersistBarrier() ha successo, e lo stato finale appartiene a S_canonical.

Dimostrazione:
Per il Teorema 2A, ogni stato H_crash intermedio soddisfa RecoveryDecision != PLAN_ABORT. Per Section 5.5 (clausola 1), ogni primitiva ritentata ha successo entro tentativi finiti. Poiche' ciascun piano contiene al piu' 4 primitive e ogni iterazione rivaluta StateOf(H), il processo raggiunge PersistBarrier() == SUCCESS e restituisce Recovered(StateOf(H')) con StateOf(H') in S_canonical. Q.E.D.

---

# PARTE V -- ERROR TAXONOMY & TEST SUITE

---

## 8. TASSONOMIA DEI CODICI DI ERRORE ED ESITI

### 8.1 Errori Semantici e Abort Operativi
[NORMATIVE REQUIREMENT]
La quadrupla di uscita e' categorizzata univocamente come segue:

    +-------+-------------------------------+---------------------+------------------------------------------------+
    | Cod.  | Identificatore Simbolico      | Categoria           | Condizione Normativa di Emissione Univoca      |
    +-------+-------------------------------+---------------------+------------------------------------------------+
    | 0     | SUCCESS                       | SemanticResult      | Trasformazione ed emissione completate con OK. |
    | 10    | ERR_INVALID_UTF8              | SemanticError       | Byte stream non conforme a RFC 3629 / BOM.     |
    | 11    | ERR_INVALID_PATH              | SemanticError       | Percorso P_raw non conforme a P_canon (Sec 1.3)|
    | 12    | ERR_INVALID_CONFIG            | SemanticError       | S_target < 64, R_min not in [1..100], Z inval. |
    | 20    | ERR_MALFORMED_PLACEHOLDER     | SemanticError       | Pattern delimitatore non conforme a L_ph.      |
    | 21    | ERR_TOKEN_COLLISION           | SemanticError       | Hash collision: K_1 != K_2 AND SHA256(K1)==(K2)|
    | 22    | ERR_MAPPING_CONFLICT          | SemanticError       | Conflitto TokenType per medesimo K in map.     |
    | 30    | ERR_PARTITION_VIOLATION       | SemanticError       | C_split <= C_start durante il partizionamento. |
    | 40    | ERR_RIC_VERIFICATION_FAILED   | SemanticError       | Fallimento predicati di roundtrip RIC-1..RIC-5.|
    +-------+-------------------------------+---------------------+------------------------------------------------+
    | 50    | ERR_STORAGE_IO_FAILURE        | ExecutionAbort      | Fallimento operativo storage host / recovery.  |
    +-------+-------------------------------+---------------------+------------------------------------------------+

In caso di esito SemanticError(e) o ExecutionAbort(50), l'implementazione MUST NOT pubblicare o alterare i file nella directory OUTPUT_PATH.

---

## 9. SUITE DI FALSIFICAZIONE CANONICA (F01 -- F15)

[CONFORMANCE TEST]
Una suite di test di conformita' valida con successo i seguenti 15 scenari deterministici:
* F01 (Boundary Snapping Inferiore): Boundary p in B(T_esc) coincidente con z_s_esc. Split a z_s_esc; token all'inizio del chunk successivo.
* F02 (Boundary Snapping Superiore): Boundary p in B(T_esc) coincidente con z_e_esc. Split a z_e_esc; token alla fine del chunk corrente.
* F03 (BOM e Caratteri 4-Byte): File con byte iniziali 0xEF 0xBB 0xBF e caratteri astral plane (U+1F600). Preservazione esatta in c_1 e roundtrip identico.
* F04 (Token Oversize all'Origine): Intervallo con (z_e_esc - z_s_esc) > S_target a C_start. Singolo chunk oversize dedicato [C_start, z_e_esc).
* F05 (Token Oversize nella Finestra): Intervallo con (z_e_esc - z_s_esc) > S_target che interseca la finestra target. Chiusura a z_s_esc e gestione oversize al passo successivo.
* F06 (Sequenze Delimitatore Letterali): Testo sorgente contenente sequenze letterali con U+00A7 o pattern conformi a L_ph. Escaping E(T) e ripristino esatto D(T_prime) == T.
* F07 (Atomicita' CRLF): Terminatori \r\n. Snapping del partizionatore rigorosamente dopo \n senza separare la coppia \r\n.
* F08 (File Vuoto): Testo con L = 0. Emissione di 0001.txt vuoto (0 byte), total_chunks = 1, total_scalar_values = 0, e digest SHA-256 coerente.
* F09 (Assenza Terminatore Finale): Testo privo di newline finale all'EOF. Chiusura a L senza aggiunta di newline spuri.
* F10 (Riga Singola Continua): Riga di lunghezza > S_target priva di terminatori. Fallback infra-linea deterministico a C_ideal.
* F11 (Crash Recovery Staging): Simulazione crash in stato STAGED. Recovery esegue rollback e rimozione di staging.
* F12 (Crash Recovery Commit): Simulazione crash dopo il CommitLinearizationPoint con journal COMMITTED. Recovery esegue rollforward e consolidamento.
* F13 (CJOC String Escaping): Verifica assenza di escape per '/' (U+002F) in stringhe JSON e rispetto rigoroso di \u00xx per controlli U+0000..U+001F.
* F14 (Ordinamento Multi-File): Ingestione percorsi non ordinati ("b/file.txt", "a/file.txt"). Ordinamento lessicografico byte-a-byte in manifest.files e manifest.chunks.
* F15 (Isolamento TokenType): Token con medesimo TokenID ma diverso TokenType. Rilevamento mapping conflict conforme a Sezione 2.5 (Errore 22).

```text
================================================================================
FINE SPECIFICA TECNICA NORMATIVA ULRP-SPEC-1.6.27 (FROZEN STANDARD)
================================================================================
```

