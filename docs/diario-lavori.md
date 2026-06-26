# Diario Dei Lavori

Questo diario documenta le decisioni tecniche, culturali e operative del progetto Adriano IA. Non è un registro ornamentale: serve a rendere leggibile il percorso, a spiegare le scelte e a mantenere alta la qualità del lavoro.

## 2026-06-26 - Fondazione Del Progetto

### Contesto

Il progetto nasce con un obiettivo netto: costruire un modello bilingue italiano/inglese, con priorità alla qualità dell'italiano, partendo da una base Qwen 14B e lavorando in locale su Windows 11 con una RTX 4060 Ti da 16 GB VRAM.

Il riferimento culturale è Adriano Olivetti: industria come progetto civile, tecnologia come responsabilità, prodotto come incontro tra tecnica e umanesimo.

### Decisione Tecnica Principale

È stata scelta una strategia QLoRA 4-bit su Qwen3-14B.

Motivazione:

- un full fine-tune di un 14B non è realistico su 16 GB VRAM;
- QLoRA permette iterazioni locali, controllabili e relativamente economiche;
- Unsloth riduce il costo operativo e semplifica il training;
- gli adapter LoRA consentono versionamento rapido senza duplicare l'intero modello.

Base operativa:

- `Qwen/Qwen3-14B` come riferimento ufficiale;
- `unsloth/Qwen3-14B-unsloth-bnb-4bit` come base pratica di training.

### Chiarimento Su Qwen3.6-14B

La richiesta iniziale indicava Qwen 3.6 14B. La verifica ha mostrato che non risulta una release ufficiale `Qwen3.6-14B`. La scelta più corretta è quindi:

- usare Qwen3-14B come student locale;
- valutare Qwen3.6 in taglie più grandi come teacher per distillazione, se disponibile.

### Materiale Creato

Sono stati creati:

- configurazione QLoRA;
- script di setup ambiente;
- script di verifica GPU;
- script di training;
- script di distillazione da teacher;
- script di chat locale;
- script di merge/export;
- dataset seed minimale;
- documento strategico.

### Profilo Di Adriano

La prima identità del modello è stata definita così:

- italiano naturale, preciso e non burocratico;
- inglese solido;
- tono operativo, non promozionale;
- capacità di dire quando mancano dati;
- attenzione alla qualità del lavoro umano;
- rifiuto delle risposte generiche.

### Prossimo Passo

Costruire un dataset manuale di 300-800 esempi eccellenti. La distillazione va avviata solo dopo avere stabilito con chiarezza la voce del modello.

## 2026-06-26 - Impostazione Bilingue Del Repository

### Contesto

Il progetto non deve essere soltanto un modello capace di parlare italiano e inglese: anche il repository deve comunicare in entrambe le lingue. Questo serve a rendere Adriano IA leggibile sia per chi segue il progetto dall'Italia sia per chi valuta la parte tecnica in un contesto internazionale.

### Decisione

È stata mantenuta la documentazione italiana come fonte primaria e sono stati aggiunti documenti inglesi dedicati:

- worklog;
- manifesto;
- roadmap;
- README bilingue.

### Motivo

L'italiano resta centrale perché è il cuore qualitativo del progetto. L'inglese è necessario per interoperabilità tecnica, collaborazione, review pubblica e futura pubblicazione del modello.

### Rischio Residuo

La documentazione bilingue va mantenuta allineata. Ogni decisione importante dovrà essere registrata almeno nel diario italiano e nel worklog inglese.

## 2026-06-26 - Launcher Windows One-Click

### Contesto

Il setup manuale su Windows ha mostrato un problema concreto: la virtualenv poteva essere creata senza `pip`, facendo fallire le installazioni successive senza bloccare chiaramente lo script.

### Decisione

È stato aggiunto un launcher Windows da doppio click per eseguire:

- setup completo;
- verifica GPU e pacchetti;
- training smoke test;
- chat locale.

Sono state anche rinforzate le verifiche in `scripts/setup_env.ps1`, così gli errori dei comandi nativi fermano davvero lo script.

### Motivo

La prima esperienza deve essere diretta: l'utente deve poter avviare Adriano senza ricordare una sequenza di comandi PowerShell. Quando qualcosa fallisce, il punto di errore deve essere visibile.

## 2026-06-26 - Pipeline Dati E Distillazione

### Contesto

Il training smoke test non basta a costruire Adriano. Un modello con identità linguistica e qualità italiana richiede dati specifici: prompt progettati, risposte generate da un teacher, filtro qualità, dataset SFT e valutazione separata.

### Decisione

Sono stati aggiunti:

- prompt bank per distillazione;
- eval set separato;
- script di validazione JSONL;
- script di preparazione dataset SFT;
- configurazione training su dataset curato;
- preparazione dati e training tramite launcher root.

### Motivo

Il modello non deve essere solo Qwen con un nome diverso. Adriano deve essere ottenuto tramite dati che insegnano italiano, metodo, tono, limiti e ragionamento operativo.

### Rischio Residuo

Il filtro automatico elimina solo errori evidenti. La qualità vera richiede revisione umana e ampliamento progressivo del dataset.

## 2026-06-26 - Piano Contesto 512k

### Contesto

È stato richiesto di portare Adriano a 512k token di contesto. La richiesta è corretta come ambizione di prodotto, ma non è realistica come semplice modifica di `max_seq_length` nel training locale.

### Decisione

Sono stati aggiunti:

- profili long-context 32k, 128k e target 512k;
- documento tecnico dedicato;
- script di stima KV cache;
- script di stima contesto lungo.

### Motivo

Qwen3-14B va trattato con prudenza: 32k è il target stabile, 128k è sperimentale con YaRN, 512k richiede backend/hardware diverso oppure memoria esterna. Il progetto deve dichiarare questa distinzione con chiarezza.

### Rischio Residuo

Il target 512k dovrà essere realizzato con un'architettura di retrieval/memoria o con un modello più adatto al long-context nativo. Non va promesso come capacità locale della 4060 Ti.

## 2026-06-26 - Ricerca Fonti Dataset Italiane

### Contesto

La qualità di Adriano dipende dal dataset. È stata avviata una ricerca su fonti italiane, universitarie e free per capire cosa può alimentare training, distillazione e valutazione.

### Decisione

È stata aggiunta una scheda dedicata alle fonti dataset italiane, con distinzione tra corpus, benchmark e instruction dataset.

### Motivo

Scaricare dataset grandi non basta. Le fonti devono essere classificate per uso, licenza, rischio e coerenza con il profilo Adriano.

### Rischio Residuo

Molti dataset italiani sono `NC`, derivati da traduzioni, oppure pensati per evaluation e non per training. Ogni fonte va verificata prima dell'uso nel modello finale.

## 2026-06-26 - Ripartenza Pulita E Training Riprendibile

### Contesto

La prima esecuzione completa ha prodotto confusione operativa: il dataset distillato non era materializzato in `data/distilled`, la finestra di comando poteva chiudersi lasciando poca traccia, e una nuova esecuzione rischiava di mescolare output vecchi e dati aggiornati.

### Decisione

Il launcher `TRAINA_TUTTO_ADRIANO.bat` ora gestisce una ripartenza pulita quando non esiste una run attiva: rimuove solo artefatti generati, ricrea il dataset distillato locale, prepara il dataset finale e avvia il training. Se una run viene interrotta, il marker locale permette al batch successivo di riprendere dai checkpoint invece di ricominciare da zero.

### Motivo

Il progetto deve essere eseguibile da doppio click anche da chi non vuole usare comandi manuali. I passaggi critici devono essere espliciti, ripetibili e tracciati su log locale.

### Rischio Residuo

Il distillato locale deriva ancora dai dataset instruction disponibili localmente; una distillazione con teacher esterno richiede credenziali e una scelta esplicita del modello teacher.

## Registro Decisioni

| Data | Decisione | Motivo |
| --- | --- | --- |
| 2026-06-26 | QLoRA 4-bit invece di full fine-tune | Limite realistico della VRAM disponibile |
| 2026-06-26 | Qwen3-14B come base 14B | Assenza di un Qwen3.6-14B ufficiale |
| 2026-06-26 | Distillazione separata dal training | Separare generazione dati, filtro qualità e SFT |
| 2026-06-26 | Adapter LoRA come formato iniziale | Iterazione rapida e costi contenuti |
| 2026-06-26 | Repository bilingue italiano/inglese | Coerenza con l'identità bilingue del modello |
| 2026-06-26 | Launcher Windows | Ridurre attrito operativo e rendere il setup ripetibile |
| 2026-06-26 | Pipeline dati distillata | Rendere Adriano addestrabile su dati curati, non solo su seed |
| 2026-06-26 | Target contesto 512k come architettura | Evitare configurazioni locali irrealistiche e pianificare long-context in modo robusto |
| 2026-06-26 | Catalogo fonti dataset italiane | Separare corpus, benchmark e instruction data con attenzione alle licenze |
| 2026-06-26 | Launcher root `TRAINA_TUTTO_ADRIANO.bat` e `CREA_MODELLO_USABILE_ADRIANO.bat` | Tenere solo due batch operativi: training completo e creazione modello |
| 2026-06-26 | Training pulito con resume automatico | Evitare output mescolati e recuperare da interruzioni della finestra |

## Standard Del Diario

Ogni voce futura deve indicare:

- cosa è stato fatto;
- perché è stato fatto;
- quali alternative sono state scartate;
- quali rischi restano;
- come si misura il risultato.
