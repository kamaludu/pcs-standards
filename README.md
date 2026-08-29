# PCS Standards & Normative Core Archive

> *«Ecco, io vi mando come pecore in mezzo ai lupi; siate dunque prudenti come i serpenti e semplici come le colombe.»* (Mt 10, 16)  
>
> *«Behold, I am sending you like sheep in the midst of wolves; so be shrewd as serpents and simple as doves.»* (Mt 10, 16)

Archivio normativo ufficiale del **Protocollo Colomba Serpente (PCS 4.5)** e delle relative specifiche tecniche e procedurali collegate.

---

## COS'È IL PROTOCOLLO COLOMBA SERPENTE (PCS)

Il **Protocollo Colomba Serpente (PCS)** è uno standard di **ingegneria difensiva, resilienza operativa e gestione del rischio** progettato per concepire, sviluppare, collaudare e distribuire artefatti software, pipeline dati, sistemi di intelligenza artificiale e strumenti di ricerca aperti.

Il framework risponde a un dilemma centrale dell'era digitale: **come pubblicare software e modelli utili massimizzandone il valore sociale e tecnico, contenendo al contempo il danno massimo potenziale, azzerando le trappole per l'utente e blindando l'opera contro cause legali asimmetriche, derive dei modelli e guasti dell'ambiente operativo.**

---

## I DUE PILASTRI: L'ETICA DELLA COLOMBA E LA DIFESA DEL SERPENTE

Il protocollo traduce la virtù evangelica di Matteo 10, 16 in vincoli architetturali, test di falsificazione e prove crittografiche:

```text
+-----------------------------------+-----------------------------------+
|     LA COLOMBA (Assioma 1)        |      IL SERPENTE (Assioma 2)      |
|    "Integrità dello Scopo"        |    "Prudenza Strutturale"         |
+-----------------------------------+-----------------------------------+
| * Zero profilazione o telemetria  | * Collasso a SAFE-DEGRADED        |
| * Zero trappole o dark patterns   | * Prova di Diligenza Tecnica      |
| * Dati sensibili mai nel cloud    | * Tono Notarile contro querele    |
| * Tutela dei soggetti fragili     | * FSM a mondo chiuso (Allowlist)  |
| * Isolamento strutturale dell'AI  | * Prove crittografiche offline    |
+-----------------------------------+-----------------------------------+
```

### 1. La Colomba: L'Etica trasformata in Vincolo Matematico
La Colomba stabilisce **cosa è onesto fare**, vietando ogni comportamento abusivo attraverso controlli bloccanti nel codice:
* **Zero Sorveglianza ed Estrazione Dati:** Scansioni sintattiche (AST) impediscono la presenza di moduli di telemetria, webhooks o pixel di tracciamento nascosti (100% determinismo offline);
* **Privacy Radicale (GDPR Art. 6, 9, 10):** Divieto architetturale di inoltro di dati particolari (salute, convinzioni, dati biometrici) verso API cloud esterne;
* **Nessun Inganno Cognitivo:** L'AI opera come mero trasformatore privo di facoltà esecutive (*zero tool-calling* dinamico, Assioma 6), senza simulare empatia ingannevole o indurre dipendenza;
* **Protezione dei Soggetti Fragili:** In contesti assistivi (classe R3), a fronte di emergenze o input di pericolo, il sistema esegue il **Session State Purge** immediato (cancellazione atomica della memoria contestuale) e reindirizza ai servizi pubblici ufficiali.

### 2. Il Serpente: La Corazza Ingegneristica contro le Crisi
Il Serpente assume a priori che l'ambiente sia ostile, le reti instabili e gli avversari agguerriti, proteggendo l'opera da 4 scenari di rischio reali:
* **Contro Crash e Allucinazioni (Minaccia T4):** Architettura ad allowlist chiusa (*Closed-World FSM*, Assioma 4), Output Contracts deterministici e Circuit Breaker a isolamento generazionale rigido (DTM-R);
* **Contro Cause Legali Asimmetriche e SLAPP (Minaccia T1):** In sede giudiziaria, i disclaimer generici non tutelano. Il PCS consente di esibire la **Prova di Diligenza Tecnica** tramite 17 Evidence Records firmati crittograficamente in modo immutabile;
* **Contro Attacchi Mediatici e Gogne (Minaccia T5):** Impone il **Protocollo di Comunicazione Notarile**, sostituendo illazioni o polemiche con rilievi puramente metrologici e riproducibili (*"i dati parlano"*);
* **Contro Richieste di Risarcimento Indebite:** Esclude categoricamente i sistemi critici fuori perimetro (R4 Boundary, Assioma 8) e traccia ogni variazione tramite la `ConfigurationIdentity` a 7 parametri.

---

## COSA GARANTISCE IL PCS (E COSA NON PROMETTE)

Per prevenire l'illusione di sicurezza (**Minaccia T0**), il PCS dichiara formalmente i propri limiti:
1. **Non costituisce immunità legale automatica (Assioma 3):** La tutela legale deriva dalla dimostrazione empirica della diligenza tecnica applicata e dal contenimento del danno;
2. **Non garantisce la veridicità semantica dell'AI (Assioma 5):**  
   `ValidSchema(x) != SafeSemantic(x)`  
   Il PCS non promette che un LLM non allucini mai, ma garantisce che ogni deviazione sintattica o logica venga **intercettata prima di raggiungere l'utente, forzando la degradazione sicura (*fail-closed*)**.

---

## STRUTTURA DELL'ARCHIVIO E DOCUMENTI

Tutti i collegamenti interni puntano direttamente ai sorgenti del repository, garantendo la piena leggibilità e verificabilità su qualsiasi piattaforma o clone locale:

* 📄 **[PCS 4.5 Core Normative](core/PCS.md)** — Assiomi, Spazio del Rischio (R, S, IR, K), Matrice dei Controlli (C0–C4) e Modello Universale delle Minacce (UTM T0–T5).
* 📄 **[SOP-PCS-001 Rev. 3.5.1](core/PCS-SOP.md)** — Procedura Operativa Standardizzata, formule metrologiche, schemi JSON e Pipeline di Pre-Flight Gate a 5 fasi.
* 📁 **[Specifiche Figlie Collegate](specifications/)** — Registro delle specifiche tecniche verticali governate dal protocollo.
* 📄 **[Licenza di Distribuzione](LICENSE)** — Licenza GNU General Public License v3.0 (GPL-3.0-or-later).

---

## DICHIARAZIONE DI AMBITO D'USO, LIMITAZIONE E DILIGENZA TECNICA (PCS-L4.5)

1. **NATURA SPERIMENTALE E AMBITO OPERATIVO:**
   Il presente software e la documentazione associata sono rilasciati per scopi di studio, ricerca indipendente, collaudo metrologico e supporto operativo. L'autore ha applicato la diligenza tecnica secondo i principi di ingegneria difensiva del Protocollo PCS 4.5. L'opera viene fornita "NELLO STATO IN CUI SI TROVA" (AS-IS), senza garanzie implicite o esplicite di idoneità a scopi particolari, continuità operativa o assenza assoluta di difetti.

2. **ESCLUSIONE CATEGORICA DA DOMINI CRITICI ED EMERGENZIALI (CLASSE R4):**
   Il software NON costituisce dispositivo medico, NON formula diagnosi, NON eroga prescrizioni terapeutiche, NON costituisce consulenza legale o finanziaria e NON è progettato per la gestione di emergenze, pericolo di vita o sicurezza fisica. In presenza di scenari critici o di urgenza, l'utente deve fare affidamento esclusivo sui servizi pubblici preposti e su professionisti abilitati.

3. **AUTONOMIA DALLE PIATTAFORME TERZE:**
   Il progetto è autonomo e non opera su incarico, approvazione, patrocinio o affiliazione formale di alcuno dei fornitori di API, modelli o servizi terzi.

4. **DELIMITAZIONE DELLA RESPONSABILITÀ E ASSENZA DI VALORE LEGALE AUTONOMO:**
   Nei limiti massimi ammessi dalla legge, l'autore declina ogni responsabilità per danni diretti o indiretti conseguenti all'uso del software, a interruzioni di servizi terzi o a decisioni operative autonome dell'utente. La presente dichiarazione documenta la diligenza tecnica e la delimitazione dell'ambito operativo, ma non costituisce parere legale né certificazione di conformità normativa per alcuna giurisdizione.

---

## LICENZA

Questo archivio è distribuito sotto licenza **GNU General Public License v3.0 (GPL-3.0-or-later)**. Consulta il file [LICENSE](LICENSE) per i termini completi.

