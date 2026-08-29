# PROTOCOLLO COLOMBA SERPENTE (PCS 4.5)
### Standard di Ingegneria Difensiva, Resilienza Operativa e Gestione del Rischio per Progetti Software e Ricerca Aperta

---

```text
+------------------------------------------------------------------------------+
|                   INDICE DELLE SPECIFICHE FORMALI (PCS 4.5)                  |
+------------------------------------------------------------------------------+
|  0. Preambolo Assiomatico e Gerarchia Documentale                            |
|  1. Modello Universale delle Minacce (Universal Threat Model: T0 - T5)       |
|  2. Spazio del Rischio: Dominio (R), Severità (S), Irreversibilità (IR), K   |
|  3. Matrice dei Requisiti Minimi di Controllo (C_min) e Criterio di Gate     |
|  4. Dependency Threat Model (DTM-L e DTM-R)                                  |
|  5. Riduzione della Correlabilità e Trattamento dei Dati                    |
|  6. Clausola Modello di Delimitazione dell'Ambito (PCS-L4.5)                 |
|  7. Architettura Deterministica ad Allowlist, Output Contracts e Drift       |
|  8. Protocollo di Comunicazione Notarile e Invarianti di Condotta           |
|  9. Pre-Flight Gate, Materialità delle Modifiche e Ciclo di Validità (PASS)  |
| 10. Strategia di Arresto Locale Autenticato e Risposta agli Incidenti       |
| 11. Criteri di Falsificazione, Multiple-Failure Test e Verifica Continua     |
| 12. Architettura della Documentazione di Attuazione (PCS, SOP, Blueprint)   |
+------------------------------------------------------------------------------+
```

---

## 0. PREAMBOLO ASSIOMATICO E GERARCHIA DOCUMENTALE

> *«Ecco, io vi mando come pecore in mezzo ai lupi; siate dunque prudenti come i serpenti e semplici come le colombe.»* (Mt 10, 16)

Il presente protocollo costituisce il **nucleo normativo (Normative Core)** per concepire, sviluppare, collaudare e distribuire artefatti software, rilevazioni metrologiche e strumenti ad accesso pubblico.

L'obiettivo primario è **massimizzare l'utilità tecnica e sociale dell'opera minimizzando la superficie di attacco, contenendo il danno massimo potenziale e garantendo la degradazione sicura del sistema**, a tutela dell'autore, degli utenti, dei terzi e dell'integrità del progetto.

```text
+------------------------------------------------------------------------------+
|                    ASSIOMATICA DEL PROTOCOLLO PCS 4.5                        |
+------------------------------------------------------------------------------+
| 1. Assioma dell'Integrità dello Scopo (Colomba)                              |
|    "L'opera non persegue secondi fini: assenza di estrazione occulta di      |
|     dati, trappole commerciali o comportamenti ingannevoli."                 |
|                                                                              |
| 2. Assioma della Prudenza Strutturale (Serpente)                             |
|    "Il sistema deve essere concepito assumendo a priori che l'ambiente       |
|     operativo e le dipendenze esterne siano instabili, ostili o compromesse."|
|                                                                              |
| 3. Assioma della Non-Immunità e Assenza di Valore Legale Certificatorio      |
|    "Nessun disclaimer o protocollo ingegneristico esclude la responsabilità  |
|     per colpa grave o violazione di legge. Il PCS non costituisce parere     |
|     legale né certificazione di conformità normativa per alcuna giurisdizione|
|     La tutela si fonda sulla diligenza tecnica e sul contenimento del danno."|
|                                                                              |
| 4. Assioma dell'Autorizzazione Esplicita (Closed-World Assumption)           |
|    "Un modulo software non deve pretendere di dimostrare la sicurezza        |
|     generale di un input: tutto ciò che non appartiene a una classe          |
|     esplicitamente autorizzata deve degradare a uno stato sicuro."           |
|                                                                              |
| 5. Assioma della Non-Equivalenza Contrattuale                                |
|    "ValidSchema(x) != SafeSemantic(x). La validazione dell'Output Contract   |
|     attesta unicamente la conformità alle proprietà formali (schema, tipi,   |
|     limiti), non la veridicità o la sicurezza semantica del contenuto."     |
|                                                                              |
| 6. Assioma dell'Isolamento Strutturale dei Modelli Generativi                |
|    "La qualifica di un modello LLM come mero trasformatore espressivo        |
|     deve essere garantita dall'architettura del codice (assenza di binding   |
|     e tool-calling) e non può derivare dalle istruzioni impartite nel prompt"|
|                                                                              |
| 7. Assioma della Prevalenza della Severità sull'Irreversibilità              |
|    "L'irreversibilità qualifica l'onere di ripristino, non la magnitudo del  |
|     danno. Una severità elevata impone il livello di controllo corrispondente|
|     alla magnitudo del danno potenziale, indipendentemente dalla teorica     |
|     reversibilità dell'evento avverso."                                      |
|                                                                              |
| 8. Assioma di Esclusione dei Sistemi Critici (R4 Boundary)                   |
|    "Il PCS non costituisce framework applicabile o sufficiente per sistemi ad|
|     impatto critico diretto (R4), i quali richiedono standard di sicurezza   |
|     funzionale dedicati, certificazioni di settore e supervisione legale."   |
|                                                                              |
| 9. Assioma della Decadenza della Validità del Gate (Stateful & Temporal Gate)|
|    "L'esito di verifica PASS non è un attributo permanente: decade a fronte  |
|     di mutamenti materiali del software o allo scadere del TTL temporale."   |
+------------------------------------------------------------------------------+
```

---

## 1. MODELLO UNIVERSALE DELLE MINACCE (UTM)

Ogni progetto governato da PCS 4.5 deve mappare formalmente il proprio profilo operativo rispetto a sei categorie universali di minaccia:

```text
                            SPAZIO DELLE MINACCE (UTM)
              +------------------------------------------------------------+
              | T0: Fallimento del Protocollo e Falsa Sicurezza (Overconf) |
              | T1: Minaccia Legale Asimmetrica (SLAPP, Copyright, ToS)    |
              | T2: Minaccia Regolatoria (GDPR, Normative AI, Privacy)     |
              | T3: Minaccia da Correlazione e Sicurezza Personale         |
              | T4: Minaccia da Malfunzionamento Diretto su Fragilità      |
              | T5: Minaccia Dialettico-Sociale ed Esposizione Mediatica   |
              +------------------------------------------------------------+
```

* **`T0` — Fallimento del Protocollo, Overconfidence e Falsa Sicurezza (*Compliance Illusion*):**
  L'autore o il team sviluppano una percezione fallace di invulnerabilità generata dalla mera esecuzione burocratica delle checklist, omettendo verifiche empiriche avversariali, confondendo la validazione sintattica con la sicurezza semantica o introducendo difetti logici nelle FSM.
* **`T1` — Rischio Legale Asimmetrico (SLAPP & Proprietà Intellettuale):**
  Azioni giudiziarie, diffide o contestazioni contrattuali promosse da soggetti dotati di asimmetria di risorse per inibire attività di analisi, benchmarking, interoperabilità o presunte violazioni dei Termini di Servizio (ToS).
* **`T2` — Rischio Regolatorio e Normativo:**
  Sanzioni o blocchi derivanti dalla violazione di normative cogenti in materia di protezione dei dati personali, trasparenza algoritmica, responsabilità per danno da prodotto o regolamentazione sull'intelligenza artificiale.
* **`T3` — Rischio di Correlazione e Sicurezza Personale:**
  De-anonimizzazione o ricostruzione dell'identità fisica, patrimoniale, geografica o relazionale dei manutentori tramite correlazione incrociata di metadati Git, intestazioni di rete, log, stilometria o transazioni.
* **`T4` — Rischio da Malfunzionamento Diretto ed Errori Operativi:**
  Danno emergente o ritardo critico subito dall'utente finale a causa di interruzioni di servizio, allucinazioni non intercettate, anomalie di parsing o risposte improprie in contesti di vulnerabilità o supporto decisionale.
* **`T5` — Rischio Dialettico, Sociale e Reputazionale:**
  Gogne mediatiche, distorsioni comunicative o campagne diffamatorie generate da affermazioni pubbliche non dimostrabili, toni polemici o pubblicazione di rilievi tecnici privi di riscontri notarili e riproducibili.

---

## 2. SPAZIO DEL RISCHIO: DOMINIO ($R$), SEVERITÀ ($S$), IRREVERSIBILITÀ ($IR$), INDICE AUSILIARIO ($K$) E CONTROLLI ($C$)

### 2.1 Classe di Rischio del Dominio ($R$)

La classificazione $R$ è determinata dalla **destinazione d'uso effettiva, dal contesto operativo reale e dal massimo impatto ragionevolmente prevedibile**, e non dalla sola architettura software dichiarata.

```text
+------+---------------+-------------------------------------------------------+
| Cl.  | Denominazione | Definizione Operativa                                 |
+------+---------------+-------------------------------------------------------+
|  R0  | Negligible    | Script locali, tool CLI offline a esclusivo uso       |
|      |               | personale, collaudo o sviluppo interno.               |
|  R1  | Informational | Dataset metrologici, benchmark di rete, reportistica, |
|      |               | documentazione e analisi tecniche riproducibili.      |
|  R2  | Functional    | Servizi web pubblici, bot interattivi, pipeline dati  |
|      |               | con dati comuni (no dati particolari/Art. 9).         |
|  R3  | Assistive     | Software a supporto di contesti di fragilità, utenti  |
|      |               | vulnerabili, caregiver o ausilio cognitivo indiretto. |
|  R4  | Critical      | Dispositivi medici, infrastrutture critiche, automaz. |
|      | (Out-of-Scope)| industriale, sicurezza fisica, decisioni legali cog.  |
+------+---------------+-------------------------------------------------------+
```

> **Regola della Classe più Restrittiva:** In caso di sovrapposizione funzionale o ambiguità nella destinazione d'uso, si assegna obbligatoriamente la classe $R$ di rango superiore.
>
> **Regola di Esclusione $R4$:** La classe $R4$ delimita i sistemi critici **fuori perimetro**. Il PCS non autorizza rilasci in classe $R4$.
>
> **Procedura di Verifica e Riclassificazione:** La classe $R$ dichiarata deve essere verificata empiricamente rispetto alla destinazione d'uso effettiva e al massimo danno prevedibile. Qualora l'analisi evidenzi uno scenario di guasto con indice ausiliario $K=3$ su progetti censiti originariamente come $R0, R1, R2$, il gate entra nello stato **BLOCKED per contraddizione**: il rilascio è inibito fino a riconfigurazione dell'ambito operativo o riclassificazione a $R3$ (se assistivo/mitigabile) o $R4$ (con conseguente arresto per uscita dal perimetro PCS).

---

### 2.2 Indice di Severità del Danno Potenziale ($S$)

L'indice $S$ quantifica la **magnitudo del danno massimo plausibile** subito da utenti, terzi o autori in caso di guasto, compromissione o uso improprio prevedibile:

* **`S0` — Trascurabile:** Nessun impatto materiale, economico, fisico o psicologico.
* **`S1` — Basso:** Disagio temporaneo, lieve inefficienza operativa, fastidio o ritardo trascurabile.
* **`S2` — Medio:** Perdita economica circoscritta, stress acuto, indisponibilità prolungata di funzioni non vitali, esposizione di dati personali comuni.
* **`S3` — Grave / Critico:** Lesioni fisiche, compromissione psicologica di soggetti fragili, esposizione di categorie particolari di dati (GDPR Art. 9), violazioni legali gravi o danni irreversibili.

---

### 2.3 Indice di Irreversibilità ($IR$) e Indice Ausiliario di Gating ($K$)

L'indice $IR$ misura l'**onere tecnico, economico o temporale richiesto per ripristinare lo stato integro precedente all'evento avverso**:

```text
+------+-------------------------+---------------------------------------------+
| Liv. | Grado di Ripristino     | Tipologia di Impatto Tipico                 |
+------+-------------------------+---------------------------------------------+
| IR0  | Immediato / Pieno       | Errore UI gestito, retry trasparente        |
| IR1  | Agevole con Intervento  | Riavvio servizio, correzione configurazione |
| IR2  | Oneroso / Complesso     | Ripristino da backup, transazione contestata|
| IR3  | Sostanzialmente         | Compromissione permanente dati personali,   |
|      | Irreversibile           | lesione psicofisica, violazione legale grave|
+------+-------------------------+---------------------------------------------+
```

#### Definizione dell'Indice Ausiliario di Gating ($K$)
Ai soli fini del calcolo formale dei requisiti minimi di controllo nel Pre-Flight Gate, si definisce l'indice ausiliario:

$$K(S, IR) = \max(S, IR) \quad \text{con } K \in \{0, 1, 2, 3\}$$

> **Nota Epistemica sull'Indice $K$:** 
> L'indice $K$ costituisce una funzione di gating conservativa e **non un indice ontologico di rischio**. $K$ non sostituisce né altera il significato semantico distinto di $S$ (severità del danno) e $IR$ (onere di ripristino). L'adozione di $\max(S, IR)$ assicura che una severità elevata ($S \ge 2$) imponga il corrispondente livello di controllo anche qualora l'evento fosse teoricamente reversibile ($IR \le 1$, Assioma 7), impedendo al contempo che danni a bassa severità ma a persistenza permanente ($S1 \land IR3$) siano rilasciati senza i controlli previsti.

---

### 2.4 Livelli di Controllo Architetturale ($C$)

```text
+------+----------------------+------------------------------------------------+
| Liv. | Denominazione        | Requisiti Minimi Obbligatori                   |
+------+----------------------+------------------------------------------------+
|  C0  | Baseline Hygiene     | Licenza open source esplicita, zero credenziali|
|      |                      | tracciate, blocco script post-install, gestione|
|      |                      | pulita dei segnali di processo (SIGINT/SIGTERM)|
+------+----------------------+------------------------------------------------+
|  C1  | Legal & Tone Defense | C0 + Clausola PCS-L4.5 + Documentazione        |
|      |                      | metrologica riproducibile + Tono neutrale.     |
+------+----------------------+------------------------------------------------+
|  C2  | Metadata Hygiene &   | C1 + Stripping metadati Git/FS + Relay email   |
|      | DTM Analysis         | mascherato + Schede DTM-L e DTM-R + Tecniche di|
|      |                      | minimizzazione/pseudonimizzazione dati comuni. |
+------+----------------------+------------------------------------------------+
|  C3  | Deterministic Cage & | C2 + Gabbia FSM deterministica ad allowlist +  |
|      | Dual Fallback        | Output Contracts + Circuit Breaker anti-flap + |
|      |                      | Kill-switch offline persistente + Session State|
|      |                      | Purge su escalation + Dati Art. 9 locali.      |
+------+----------------------+------------------------------------------------+
|  C4  | Audited Control &    | C3 + Supervisione Human-in-the-Loop vincolante |
|      | Independent Review   | + Kill-switch con verifica d'audit terzo       |
|      |                      | + Audit formale indipendente privo di conflitti|
+------+----------------------+------------------------------------------------+
```

#### Requisiti Operativi per l'Audit Indipendente ($C4$)
Il soddisfacimento del livello $C4$ richiede l'intervento di un revisore indipendente conforme ai seguenti vincoli:
1. **Terzietà Strutturale:** L'auditor deve essere un soggetto o team tecnico disgiunto dagli sviluppatori primari del modulo decisionale/FSM.
2. **Assenza di Conflitto di Interessi Materiale:** L'auditor non deve detenere interessi commerciali o patrimoniali diretti nel rilascio, né ricoprire il ruolo di responsabile gerarchico dell'approvazione finale del progetto.
3. **Perimetro di Verifica:** Ispezione del codice sorgente, collaudo empirico dell'isolamento FSM, test di iniezione di guasti multipli e validazione del funzionamento offline del meccanismo di kill-switch locale.
4. **Epistemologia del Verbale Notarile:** Il revisore rilascia un'attestazione limitata *all'esecuzione delle verifiche previste e agli esiti metrologici osservati*, astenendosi da asserzioni assolute di invulnerabilità o conformità legale autonoma (prevenzione attiva di $T0$).

---

## 3. MATRICE DEI REQUISITI MINIMI DI CONTROLLO ($C_{min}$) E CRITERIO DI GATE

Il livello di controllo implementato $C$ deve soddisfare la condizione:

$$C \ge C_{min}(R, K)$$

### 3.1 Funzione Piecewise $C_{min}(R, K)$

La funzione normativa $C_{min}(R, K)$ è definita univocamente su tutto il dominio $\{R0, R1, R2, R3, R4\} \times \{0, 1, 2, 3\}$:

$$C_{min}(R, K) = \begin{cases}
C0 & \text{se } R = R0 \ \land \ K \le 1 \\
C1 & \text{se } R = R0 \ \land \ K = 2 \\
\mathbf{CONTRADDIZIONE / BLOCKED} & \text{se } R = R0 \ \land \ K = 3 \\
C1 & \text{se } R = R1 \ \land \ K \le 1 \\
C2 & \text{se } R = R1 \ \land \ K = 2 \\
\mathbf{BLOCKED} & \text{se } R = R1 \ \land \ K = 3 \\
C2 & \text{se } R = R2 \ \land \ K \le 1 \\
C3 & \text{se } R = R2 \ \land \ K = 2 \\
\mathbf{BLOCKED} & \text{se } R = R2 \ \land \ K = 3 \\
C3 & \text{se } R = R3 \ \land \ K \le 2 \\
C4 + \text{Audit Indipendente} & \text{se } R = R3 \ \land \ K = 3 \\
\mathbf{OUT\ OF\ SCOPE\ (BLOCKED)} & \text{se } R = R4
\end{cases}$$

### 3.2 Matrice Tabellare dei Controlli

```text
       +───────────+───────────────+───────────────────+───────────────────────────+
       |           |     K ≤ 1     |       K = 2       |           K = 3           |
       |           | (S≤1 ∧ IR≤1)  |  (max(S, IR) = 2) |     (S=3 oppure IR=3)     |
       +───────────+───────────────+───────────────────+───────────────────────────+
       | R0 (Negl) |      C0       |        C1         |  CONTRADDIZIONE / BLOCKED |
       | R1 (Info) |      C1       |        C2         |  BLOCKED                  |
       | R2 (Func) |      C2       |        C3         |  BLOCKED                  |
       | R3 (Asst) |      C3       |        C3         |  C4 + AUDIT INDIPENDENTE  |
       | R4 (Crit) |    FUORI      |      FUORI        |  FUORI PERIMETRO (BLOCKED)|
       |           |  PERIMETRO    |    PERIMETRO      |                           |
       +───────────+───────────────+───────────────────+───────────────────────────+
```

---

### 3.3 Condizione Logico-Formale del Release Gate

$$\text{PCS Release Gate} = \text{PASS} \iff \begin{cases} 
R \in \{R0, R1, R2, R3\} \\
C \ge C_{min}(R, K) \\
C_{min}(R, K) \neq \mathbf{BLOCKED} \\
\bigwedge_{i} \text{Eval}(P_i, R, C) = \text{TRUE} \quad (\text{Validazione formale checklist Pre-Flight})
\end{cases}$$

> **Semantica di `PASS`:** L'esito `PASS` certifica esclusivamente il superamento delle verifiche ingegneristiche interne formalizzate nel presente standard allo specifico commit e ambiente verificato. Non costituisce perizia legale, garanzia commerciale di idoneità o esenzione di responsabilità verso terzi.

---

## 4. DEPENDENCY THREAT MODEL (DTM)

La gestione dell'albero delle dipendenze e degli artefatti esterni si articola in due modelli complementari:

```text
                     DEPENDENCY THREAT MODEL (DTM)
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
  DTM-L (Local Software & Artifacts)            DTM-R (Remote External Services)
  - Typosquatting / Supply-chain injection      - Outage infrastrutturale / 5xx
  - Compromissione account maintainer           - Rate Limit / HTTP 429
  - Transitive dependencies non verificate      - Drift semantico del modello (pesi)
  - Lockfile tampering / Build hijacking        - Logging e data-retention remoto
  - Model deserialization attack (Pickle RCE)   - Circuit Breaker flapping / loop
```

### 4.1 Matrice DTM-L (Dipendenze Software Locali e Artefatti AI)

```text
+-------------------------------+-----------------------------------------------+
| Vettore di Rischio Locale     | Contromisura Obbligatoria                     |
+-------------------------------+-----------------------------------------------+
| 1. Modifica pacchetto upstream| Pinning esatto delle versioni (no range `^/~`)|
| 2. Man-in-the-middle / Poison | Verifica crittografica checksum / Lockfile    |
| 3. Dipendenze transitive      | Audit automatico supply-chain (SBOM)          |
| 4. Esecuzione script di build | Disattivazione script post-install non sicuri |
| 5. Deserializzazione Modelli  | Divieto formati non sicuri (es. Pickle puro); |
|    (AI Artifact Poisoning)    | uso esclusivo di formati sicuri (SafeTensors, |
|                               | GGUF) con pinning hash crittografico SHA-256. |
+-------------------------------+-----------------------------------------------+
```

### 4.2 Matrice DTM-R (Servizi Remoti e API Cloud)

```text
+-------------------------------+-----------------------------------------------+
| Vettore di Rischio Remoto     | Contromisura Obbligatoria                     |
+-------------------------------+-----------------------------------------------+
| 1. Outage / Indisponibilità   | Circuit Breaker deterministico -> Safe State  |
| 2. Rate Limit / HTTP 429      | Backoff esponenziale con hard cap immediato   |
| 3. Circuit Flapping           | FSM Breaker (CLOSED->OPEN->HALF-OPEN) con     |
|    (Oscillazione a loop)      | tempo di quarantena minimo nello stato OPEN.  |
| 4. Model Drift (cambio pesi)  | Validazione sintattica forte (Output Contract)|
| 5. Data Logging da terzi      | Minimizzazione preventiva / Pseudonimizzazione|
| 6. Aumento Improvviso Costi   | Hard-cap di spesa gestito a livello software  |
| 7. Modifica ToS del Provider  | Astrazione client per sostituzione rapida     |
+-------------------------------+-----------------------------------------------+
```

---

## 5. RIDUZIONE DELLA CORRELABILITÀ E TRATTAMENTO DEI DATI

1. **Igiene dei Repository e dei Sorgenti:**
   * Configurazione Git priva di dati anagrafici personali diretti (`user.name` di progetto, indirizzo relay email mascherato).
   * Bonifica integrale della cronologia Git: divieto assoluto di commit contenenti credenziali, token, chiavi crittografiche, percorsi assoluti dell'ambiente host (`/home/username/...`) o riferimenti a infrastrutture private.
   * Uso esclusivo di percorsi relativi o variabili d'ambiente standardizzate (`$WORKSPACE_DIR`).
2. **Governance dei Dati Personali Comuni e Particolari (GDPR Art. 6 e Art. 9):**
   * **Dati Comuni (Progetti $R2$):** Obbligo di applicare principi di *Data Minimization* prima di qualunque chiamata a servizi remoti (DTM-R). Gli identificativi utente, gli indirizzi IP o i campi anagrafici devono essere rimossi, mascherati o sottoposti ad hashing unidirezionale locale (pseudonimizzazione) prima della trasmissione del payload.
   * **Dati Particolari (GDPR Art. 9):** Divieto assoluto di inoltro verso servizi cloud o API esterne di categorie particolari di dati (salute, convinzioni filosofico-religiose, opinioni politiche, dati biometrici o genetici).
   * **Isolamento Locale ($R3$):** Nei sistemi $R3$, l'eventuale trattamento di parametri legati a condizioni di fragilità o assistenza deve avvenire **esclusivamente su runtime locale offline**, privo di canali di telemetria verso l'esterno.

---

## 6. CLAUSOLA MODELLO DI DELIMITAZIONE DELL'AMBITO (PCS-L4.5)

```text
================================================================================
DICHIARAZIONE DI AMBITO D'USO, LIMITAZIONE E DILIGENZA TECNICA (PCS-L4.5)
================================================================================
1. NATURA SPERIMENTALE E AMBITO OPERATIVO:
   Il presente software e la documentazione associata sono rilasciati per scopi
   di studio, ricerca indipendente, collaudo metrologico e supporto operativo.
   L'autore ha applicato la diligenza tecnica secondo i principi di ingegneria
   difensiva del Protocollo PCS 4.5. L'opera viene fornita "NELLO STATO IN CUI
   SI TROVA" (AS-IS), senza garanzie implicite o esplicite di idoneità a scopi
   particolari, continuità operativa o assenza assoluta di difetti.

2. ESCLUSIONE CATEGORICA DA DOMINI CRITICI ED EMERGENZIALI (CLASSE R4):
   Il software NON costituisce dispositivo medico, NON formula diagnosi, NON
   eroga prescrizioni terapeutiche, NON costituisce consulenza legale o finanziaria
   e NON è progettato per la gestione di emergenze, pericolo di vita o sicurezza
   fisica. In presenza di scenari critici o di urgenza, l'utente deve fare
   affidamento esclusivo sui servizi pubblici preposti e su professionisti abilitati.

3. AUTONOMIA DALLE PIATTAFORME TERZE:
   Il progetto è autonomo e non opera su incarico, approvazione, patrocinio o
   affiliazione formale di alcuno dei fornitori di API, modelli o servizi terzi.

4. DELIMITAZIONE DELLA RESPONSABILITÀ E ASSENZA DI VALORE LEGALE AUTONOMO:
   Nei limiti massimi ammessi dalla legge, l'autore declina ogni responsabilità
   per danni diretti o indiretti conseguenti all'uso del software, a interruzioni
   di servizi terzi o a decisioni operative autonome dell'utente.
   La presente dichiarazione documenta la diligenza tecnica e la delimitazione
   dell'ambito operativo, ma non costituisce parere legale né certificazione di
   conformità normativa per alcuna giurisdizione.
================================================================================
```

---

## 7. ARCHITETTURA DETERMINISTICA AD ALLOWLIST, OUTPUT CONTRACTS E CONTENIMENTO DEL DRIFT

Nei progetti di classe $R3$, i modelli probabilistici o generativi operano privi di facoltà decisionali o di mutazione di stato autonoma.

```text
[ Input Utente ]
       │
       v
+─────────────────────────────────────────────────────────────+
|  LIVELLO 0: GABBIA AD ALLOWLIST (Closed-World FSM)          |
|  - L'input appartiene a una classe esplicitamente AMMESSA?  |
|  - Se NON PROVABILE o AMBIGUO -> Transizione a Fallback     |
|  - Se Trigger di Pericolo     -> CRITICAL-ESCALATION        |
|                                  (+ SESSION STATE PURGE)    |
+──────────────────────────────┬──────────────────────────────+
                               │ Classe esplicitamente autorizzata
                               v
+─────────────────────────────────────────────────────────────+
|  LIVELLO 1: TRASFORMATORE ESPRESSIVO (LLM Confinato)        |
|  - Isolamento architetturale: zero tool-calling, zero stato |
|  - Riformulazione o sintesi puramente linguistica           |
+──────────────────────────────┬──────────────────────────────+
                               │ Payload generato
                               v
+─────────────────────────────────────────────────────────────+
|  LIVELLO 2: VERIFICA GERARCHICA DELL'OUTPUT                 |
|  [BARRIERA DETERMINISTICA FORTE - Bloccante]                |
|  - Validità schema (JSON Schema / Enum / Tipi corretti)     |
|  - Rispetto limiti dimensionali (Lunghezza / Delimitatori)  |
|  - Coerenza transizionale FSM                               |
|  [DIFESA LINGUISTICA SECONDARIA - Filtro di mitigazione]    |
|  - Blacklist termini clinici, prescrizioni, comandi imperat.|
|  - Se qualsiasi check fallisce -> SAFE-DEGRADED             |
+──────────────────────────────┬──────────────────────────────+
                               │ Proprietà verificate
                               v
[ Output Conforme per l'Utente ]
```

### 7.1 Invariante di Isolamento e Assioma di Non-Equivalenza ($T0$)
1. **Isolamento Strutturale:** L'incapacità dell'LLM di intraprendere azioni non autorizzate deve essere **garantita dall'architettura del codice** tramite disabilitazione a runtime di binding, chiamate di sistema o tool-calling, e non delegata a direttive testuali nel prompt (*system prompt instructions*).
2. **Mitigazione del Drift Semantico vs Sicurezza Semantica:**
   $$\text{ValidSchema}(x) \neq \text{SafeSemantic}(x)$$
   L'applicazione di gabbie FSM, template e Output Contracts costituisce una misura di **contenimento e limitazione del danno potenziale derivante dal drift semantico**, non una prova di correttezza o veridicità del contenuto. Qualora il dominio esiga garanzia di veridicità semantica, devono intervenire verifiche deterministiche esterne e supervisione umana (*Human-in-the-Loop*).

### 7.2 Gestione Differenziata degli Stati di Fallback e Session State Purge

* **Stato `SAFE-DEGRADED` (Guasto Tecnico, Timeout, Output Invalido, Drift Sintattico):**
  Transizione deterministica verso un messaggio statico sicuro, con attivazione del cooldown di quarantena per prevenire oscillazioni del Circuit Breaker:
  > *"Il servizio di elaborazione è momentaneamente non disponibile. Riprova più tardi o contatta il supporto tecnico."*
* **Stato `CRITICAL-ESCALATION` (Input Fuori Perimetro, Trigger di Rischio, Emergenza):**
  1. Interruzione immediata di ogni elaborazione generativa.
  2. **Session State Purge Obbligatorio:** Cancellazione atomica del buffer di conversazione, della memoria di sessione e ripristino forzato della FSM allo stato iniziale pulito, per impedire la contaminazione contestuale di successive richieste.
  3. Reindirizzamento dell'utente:
     > *"Questo strumento non è progettato per gestire situazioni urgenti o critiche. In caso di necessità o pericolo immediato, contatta i servizi di emergenza ufficiali."*

---

## 8. PROTOCOLLO DI COMUNICAZIONE NOTARILE E INVARIANTI DI CONDOTTA

Per neutralizzare le minacce $T1$ (SLAPP) e $T5$ (attacchi mediatici o reputazionali):

1. **Invariante Notarile e Metrologico:**
   Tutte le comunicazioni pubbliche, issue, benchmark e relazioni tecniche devono basarsi rigorosamente su registrazioni empiriche, riproducibili e deterministiche.
   * *Formulazione Vietata:* giudizi morali o illazioni sull'operato di terzi (*"Il provider X altera arbitrariamente le metriche"*).
   * *Formulazione Obbligatoria:* registrazione fattuale (*"Con il payload P e seed S, l'endpoint X restituisce lo stato HTTP 403 con il body B"*).
2. **Invariante di Assenza di Bersagli Personali:**
   La documentazione analizza esclusivamente il comportamento di protocolli, interfacce ed endpoint pubblici, astenendosi da attacchi personali, illazioni motivazionali o speculazioni su sviluppatori e manutentori terzi.
3. **Condotta nei Canali Pubblici:**
   Divieto assoluto di alimentare polemiche su reti sociali. Alle richieste o contestazioni tecniche si risponde esclusivamente rimandando al manifest dei test:
   > *"I dati pubblicati sono verificabili rieseguendo la suite di test con i parametri archiviati nel manifest metrologico."*

---

## 9. PRE-FLIGHT GATE, MATERIALITÀ DELLE MODIFICHE E CICLO DI VALIDITÀ DEL VERDETTO

### 9.1 Checklist Pre-Flight e Semantica dei Predicati

```text
================================================================================
                    PRE-FLIGHT GATE (CHECKLIST BINARIA)
================================================================================
[ ] P_SCOPE_OK   : Il progetto ricade nelle classi R0-R3? (Se R4 -> BLOCCATO)
[ ] P_K_CALC     : L'indice ausiliario K = max(S, IR) è formalmente calcolato?
[ ] P_CTRL_MATCH : Il livello implementato soddisfa C >= C_min(R, K)?
[ ] P_NO_BLOCK   : Il verdetto della matrice non risulta BLOCKED o CONTRADDIZIONE?
[ ] P_THREAT_MOD : Il threat model a 6 fattori (T0-T5) è formalmente compilato?
[ ] P_T0_TEST    : Eseguiti test avversariali per verificare che la conformità
                   formale non nasconda difetti logici o falsa sicurezza?
[ ] P_DTM_LOCAL  : DTM-L completato: version pinning, lockfile e verifica formati
                   sicuri per artefatti/modelli (SafeTensors/GGUF)?
[ ] P_DTM_REMOTE : [Condizionale DTM-R] Circuit breaker anti-flapping, hard-cap
                   e minimizzazione/pseudonimizzazione dati comuni implementati?
[ ] P_DATA_GOV   : Garantito che nessun dato particolare/Art. 9 sia inviato a terzi?
[ ] P_METADATA   : Percorsi host, credenziali e metadati personali rimossi dal repo?
[ ] P_LEGAL_DOC  : Clausola PCS-L4.5 e licenza visibili nei repository di release?
[ ] P_ALLOWLIST  : [Condizionale R3] La FSM opera su allowlist chiusa (default-deny)?
[ ] P_LLM_ISOL   : [Condizionale R3] L'LLM è privo di binding runtime o tool-calling?
[ ] P_CONTRACT   : [Condizionale R3] Gli Output Contracts sono verificati a runtime?
[ ] P_DUAL_FAIL  : [Condizionale R3] Validati SAFE-DEGRADED, CRITICAL-ESCALATION
                   e Session State Purge mediante iniezione di guasti?
[ ] P_C4_AUDIT   : [Condizionale C4] L'audit indipendente è completato da terzi
                   privi di conflitto con verbale notarile allegato?
[ ] P_ABORT_OFF  : Meccanismo di arresto/kill-switch locale verificato e proporzionato
                   al livello C (SIGINT/SIGTERM per C0-C2; offline per C3-C4)?
================================================================================
```

#### Semantica Formale di Valutazione dei Predicati:
La funzione di valutazione $\text{Eval}(P_i, R, C)$ per ciascun predicato $P_i$ è definita come segue:

$$\text{Eval}(P_i, R, C) = \begin{cases}
\text{TRUE} & \text{se } P_i \text{ è applicabile a } (R, C) \ \land \ P_i \text{ è verificato positivamente} \\
\text{TRUE} & \text{se } P_i \text{ non è applicabile alle condizioni } (R, C) \text{ del progetto (N/A per vacuità)} \\
\text{FALSE} & \text{se } P_i \text{ è applicabile a } (R, C) \ \land \ P_i \text{ non è verificato (FALLIMENTO)}
\end{cases}$$

$$\text{Esito Pre-Flight Gate} = \begin{cases}
\mathbf{PASS} & \iff \forall i, \ \text{Eval}(P_i, R, C) = \text{TRUE} \\
\mathbf{FAIL} & \iff \exists i \mid \text{Eval}(P_i, R, C) = \text{FALSE}
\end{cases}$$

---

### 9.2 Invariante di Decadimento del PASS, Materialità e Invariante Temporale (TTL)

Il verdetto `PCS Release Gate: PASS` è **stateful e temporalmente limitato**: attesta unicamente la conformità dello specifico stato del software, delle dipendenze e dell'ambiente al momento del collaudo.

```text
                  STATO: PASS
                       │
                       ├────────────────────────────────────┐
                       │ Evento di Modifica Materiale               │
                       │ OPPURE Scadenza TTL Temporale              │
                       ▼                                           │
      ┌───────────────────────────┐                           │
      │ Cause di Invalidazione:         │                           │
      │ - Modifica Codice / FSM         │                           │
      │ - Aggiornamento Dipendenze      │                           │
      │ - Variazione Modello / API      │                           │
      │ - Decorso TTL (180/365 gg)      │                           │
      └─────────────┬─────────────┘                           │
                       │                                            │
                       ▼                                           ▼
             INVALIDAZIONE AUTOMATICA                       Modifica Non-Materiale
                       │                                    (README, Commenti)
                       ▼                                    entro la finestra TTL
             STATO: RE-ASSESSMENT REQUIRED                          │
                       │                                           ▼
                       ▼                                    STATO INVARIATO
             Esecuzione Pre-Flight Gate
                       │
             ┌───────┴─────────┐
             ▼                    ▼
            PASS                 FAIL
             │                    │
             ▼                   ▼
        DEPLOY PERMESSO     DEPLOY BLOCCATO
```

#### Criterio di Materialità delle Modifiche
**La classificazione SemVer non determina da sola la non-materialità di una modifica.**

* **Modifiche Non-Materiali (Stato `PASS` mantenibile fino a scadenza TTL):**
  * Revisioni della documentazione non normativa o del file README.
  * Modifiche a commenti interni del codice sorgente.
  * Aggiornamento di asset grafici statici privi di logica attiva.
* **Modifiche Materiali (Decadenza Immediata del `PASS` $\rightarrow$ `RE-ASSESSMENT REQUIRED`):**
  * **Qualsiasi aggiornamento di dipendenze software o artefatti**, incluse le patch dependencies (`x.y.Z`), modifiche ai lockfile, aggiornamenti a librerie transitive o sostituzione di pesi del modello locale (DTM-L).
  * Modifiche alla logica della FSM, alle allowlist, ai parser o agli Output Contracts.
  * Variazione di provider, endpoint, iperparametri o pesi del modello linguistico (DTM-R).
  * Mutamenti nel perimetro operativo, nella destinazione d'uso o nelle tipologie di dati trattati.
  * Emersione di nuove vulnerabilità o vettori di rischio nel registro $T0-T5$.

#### Invariante Temporale (Time-To-Live del PASS):
Indipendentemente dalla presenza di modifiche al codice sorgente, l'esito `PASS` decade automaticamente al decorrere di un intervallo massimo prefissato:
* **Per Classi $R0, R1, R2$:** $T_{\text{TTL}} = 365 \text{ giorni}$.
* **Per Classe $R3$:** $T_{\text{TTL}} = 180 \text{ giorni}$.

Allo scadere del TTL, il sistema entra nello stato `RE-ASSESSMENT REQUIRED` per imporre un ciclo di audit periodico su vulnerabilità emergenti (CVE), mutamenti della supply-chain e tenuta dei vincoli di sicurezza.

---

## 10. STRATEGIA DI ARRESTO LOCALE AUTENTICATO E RISPOSTA AGLI INCIDENTI

1. **Graduazione dei Requisiti di Arresto Locale:**
   * **Livelli $C0 - C2$:** Gestione deterministica e pulita dei segnali di terminazione del sistema operativo (`SIGINT`, `SIGTERM`), garantendo l'arresto dei processi senza corruzione di file o stati parziali.
   * **Livelli $C3 - C4$:** Meccanismo di disattivazione d'emergenza locale dedicato e persistente (es. file di lock autenticato, variabile di runtime protetta o comando di abort locale), capace di forzare istantaneamente lo stato `SAFE-DEGRADED` in modo autonomo, garantendo l'arresto operativo anche in caso di isolamento totale della rete. Nei livelli $C4$, l'efficacia offline del kill-switch deve essere esplicitamente validata dal revisore indipendente.
2. **Procedura di Dismissione Controllata (Archiving & Revocation):**
   In presenza di contenzioso formale non componibile o di vulnerabilità strutturale non mitigabile:
   * Revoca immediata di token applicativi e chiavi d'accesso API.
   * Archiviazione del repository pubblico in modalità di sola lettura (*read-only*).
   * Pubblicazione di una memoria notarile neutra che attesti la dismissione tecnica.
3. **Analisi Post-Mortem $T0$:**
   Ogni malfunzionamento rilevato in produzione deve essere analizzato per verificare se causato da un'assunzione fallace del protocollo (*Fallimento $T0$*), integrando la suite di falsificazione prima di qualunque nuovo ciclo di rilascio.

---

## 11. CRITERI DI FALSIFICAZIONE E MULTIPLE-FAILURE TEST

Il modello normativo PCS 4.5 deve poter essere sottoposto a verifica empirica avversariale:

### Test di Falsificazione Obbligatori:
1. *È possibile iniettare un input semanticamente o sintatticamente non compreso nell'allowlist che non provochi l'immediata degradazione allo stato sicuro?*
2. *La violazione di una proprietà dell'Output Contract può essere mascherata o propagata a valle senza intercettazione?*
3. *Il kill-switch locale è in grado di forzare l'arresto operativo in assenza totale di connettività di rete verso l'esterno?*
4. **Multiple-Failure Invariant Test:**
   *A fronte del guasto simultaneo del classificatore, dell'indisponibilità della rete esterna e della ricezione di un payload malformato dal motore generativo, il sistema collassa in modo deterministico e non autorizzativo sullo stato di fallback previsto?*

---

## 12. ARCHITETTURA DELLA DOCUMENTAZIONE DI ATTUAZIONE

Il PCS 4.5 costituisce il vertice normativo di una struttura gerarchica standardizzata:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PCS 4.5 (QUESTO DOCUMENTO)                                       │
│                        NUCLEO NORMATIVO & INVARIANTI                                         │
│            Definisce COSA è obbligatorio, le classi e i vincoli.                             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 SOP-PCS-001                                                  │
│                      PROCEDURA OPERATIVA STANDARDIZZATA                                      │
│           Definisce COME applicare, verificare e auditare il PCS.                            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PCS PROJECT BLUEPRINT (PCS-PB / PCS-PSB)                                │
│                        ISTANZA DI PROGETTO VERSIONATA                                        │
│    Definisce COME il PCS è istanziato per uno specifico programma software.                  │
│                                                                                              │
│    ├── PCS-PB-Lite  (per R0 / R1)  -> Record classificazione e DTM-L base.                  │
│    └── PCS-PSB-Full (per R2 / R3)  -> Blueprint completo con FSM,                           │
│                                       Non-Purposes, DTM-L/R, Contract e Test                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---
*Fine delle Specifiche Formali — PROTOCOLLO COLOMBA SERPENTE (PCS 4.5)*
