# Dataset Italiani E Fonti Universitarie

Questa nota raccoglie fonti italiane/free utili per Adriano IA. Non tutti i dataset sono adatti allo stesso scopo: alcuni servono per pretraining/continual learning, altri per evaluation, altri ancora per generare istruzioni tramite distillazione.

## Regola Operativa

Per Adriano non basta scaricare corpus grandi. La priorità è:

1. dataset manuale Adriano, piccolo ma eccellente;
2. distillazione controllata da teacher;
3. fonti italiane free usate per generare prompt, evaluation e compiti;
4. corpus grandi solo se licenza e qualità sono chiare.

## Candidati Prioritari

| Fonte | Tipo | Ente/Origine | Uso consigliato | Rischio |
| --- | --- | --- | --- | --- |
| PAISÀ | Corpus web italiano | progetto PAISÀ, CNR/Università | lingua italiana generale, estrazione prompt, stile, continual learning leggero | licenze CC miste, verificare clausole NC |
| KIParla | parlato italiano trascritto | Università di Bologna + Torino | italiano parlato, variazione regionale, dialoghi/eval | audio con restrizioni; usare con attenzione |
| EVALITA / EVALITA4ELG | benchmark NLP italiani | comunità accademica italiana, Univ. Torino e altri | evaluation set, task specifici | licenze diverse per task |
| ITA-Bench | benchmark LLM italiano | SapienzaNLP | valutazione LLM italiana | usare per eval, non training |
| Universal Dependencies Italian | treebank annotati | comunità UD, Univ./CNR | grammatica, sintassi, evaluation linguistica | spesso CC BY-NC-SA |
| PaCCSS-IT | coppie complesso-semplice | CNR | semplificazione testi, instruction tuning mirato | verificare licenza e derivazione ItWaC |
| Camoscio dataset | instruction tuning italiano | Sapienza/CLiC-it | baseline instruction in italiano | traduzione ChatGPT di Alpaca; cautela commerciale |
| Fauno dataset | conversational/instruction italiano | Sapienza/RSTLess | baseline conversazionale | sintetico/tradotto; cautela licenza/qualità |
| Minerva | modello/dati italiani aperti | SapienzaNLP + FAIR + CINECA | teacher, confronto, ispirazione dataset mix | verificare esatta disponibilità dei dati |
| ParlaMint-IT | parlamento italiano annotato | CLARIN | linguaggio istituzionale, argomentazione, eval long-context | corpus politico; bilanciare bias |

## Fonti Da Valutare

### PAISÀ

Corpus web italiano contemporaneo, circa 380.000 documenti e circa 250 milioni di token. È una delle fonti più interessanti perché nasce con licenze Creative Commons e ha un taglio linguistico autentico.

Uso Adriano:

- estrarre frasi e paragrafi per prompt di riscrittura;
- costruire task di sintesi, classificazione, spiegazione;
- generare esempi di italiano naturale, poi filtrati.

Non usarlo grezzamente per SFT chat: va trasformato in istruzioni/risposte.

### KIParla

Corpus di italiano parlato nato dalla collaborazione fra Università di Bologna e Università di Torino. Utile per evitare un italiano solo scritto, rigido o burocratico.

Uso Adriano:

- esempi di dialogo naturale;
- valutazione su italiano parlato;
- costruzione di prompt su registri linguistici.

### EVALITA E ITA-Bench

Sono più importanti per valutare Adriano che per addestrarlo. Un modello serio va misurato su benchmark italiani, ma non bisogna contaminare il training con gli stessi item di valutazione.

Uso Adriano:

- creare eval suite;
- misurare NER, sentiment, QA, stance, safety, ragionamento;
- confrontare versioni del modello.

### Camoscio/Fauno

Sono utili come riferimento storico per instruction tuning italiano. Non vanno copiati alla cieca:

- possono essere traduzioni o dati sintetici;
- possono avere vincoli legati ai generatori originali;
- possono insegnare un italiano tradotto, non naturale.

Uso Adriano:

- ispirazione per schema dati;
- baseline comparativa;
- non fonte principale del tono Adriano.

### Minerva

Minerva è rilevante perché è un progetto italiano forte, nato in ambito SapienzaNLP con FAIR/CINECA. Per Adriano può servire come:

- teacher italiano;
- riferimento metodologico;
- confronto di qualità linguistica.

## Piano Pratico Per Adriano

### Fase A - Evaluation Italiana

Integrare subito:

- prompt nostri;
- subset EVALITA/ITA-Bench se licenza compatibile;
- prompt da PAISÀ trasformati in task;
- prompt long-context da ParlaMint-IT.

### Fase B - Dataset SFT

Costruire:

- 300-800 esempi manuali Adriano;
- 5k-20k esempi distillati;
- esempi di riscrittura, sintesi, critica, spiegazione tecnica;
- esempi bilingui italiano/inglese.

### Fase C - Corpus Grandi

Solo dopo:

- PAISÀ;
- ItWaC o derivati;
- ParlaMint-IT;
- eventuali dataset CLARIN.

Devono passare da:

```text
deduplica -> filtro licenza -> filtro qualità -> trasformazione in istruzioni -> review campionaria
```

## Link

- PAISÀ: https://www.corpusitaliano.it/
- PAISÀ CLARIN/Eurac: https://clarin.eurac.edu/repository/xmlui/handle/20.500.12124/3
- PAISÀ paper: https://aclanthology.org/W14-0406/
- ItWaC / WaCky: https://wacky.sslmit.unibo.it/doku.php?id=download
- Corpora DIT Forlì, Università di Bologna: https://corpora.dipintra.it/
- KIParla: https://kiparla.it/en/il-corpus/
- KIParla access/license: https://www.leadhoc.org/index.php/data-access/corpus-of-spoken-italian/
- EVALITA: https://www.evalita.it/
- EVALITA4ELG paper: https://aclanthology.org/2022.lrec-1.19/
- ITA-Bench: https://github.com/SapienzaNLP/ita-bench
- UD Italian ISDT: https://universaldependencies.org/treebanks/it_isdt/index.html
- PaCCSS-IT: https://www.cnr.it/en/institutes-databases/database/1027/paccss-it-parallel-corpus-of-complex-simple-sentences-for-italian
- Camoscio dataset: https://huggingface.co/datasets/teelinsan/camoscio
- Camoscio project: https://gladia.di.uniroma1.it/project/camoscio-gpt/
- Fauno paper: https://arxiv.org/html/2306.14457v1
- Minerva technical docs: https://minerva-ai.org/en/docs/tech-page
- Minerva model card: https://huggingface.co/sapienzanlp/Minerva-7B-base-v1.0
- CLARIN-IT: https://www.clarin-it.it/
- CLARIN-IT repository: https://dspace-clarin-it.ilc.cnr.it/
- ParlaMint-IT paper: https://aclanthology.org/2022.parlaclarin-1.17/

