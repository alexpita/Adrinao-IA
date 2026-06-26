# Roadmap

## Fase 0 - Fondazione

Stato: in corso.

- Creare struttura repository.
- Definire strategia QLoRA.
- Preparare ambiente Windows.
- Verificare GPU e dipendenze.
- Eseguire smoke test training.

## Fase 1 - Voce Adriano

Obiettivo: 300-800 esempi manuali di altissima qualità.

Dataset:

- identità del modello;
- scrittura professionale in italiano;
- spiegazioni tecniche;
- revisioni testuali;
- ragionamento critico;
- risposte bilingui;
- gestione dell'incertezza.

Criterio di successo:

- Adriano risponde in italiano senza sembrare tradotto;
- il tono è riconoscibile ma non teatrale;
- le risposte sono utili al primo passaggio.

## Fase 2 - Distillazione

Obiettivo: 5k-20k conversazioni filtrate.

Procedura:

- generare prompt controllati;
- usare teacher più grande;
- filtrare output mediocri;
- bilanciare italiano e inglese;
- mantenere set di valutazione separato.

## Fase 3 - Training

Obiettivo: primo adapter Adriano consistente.

Parametri iniziali:

- LoRA rank 16;
- LoRA alpha 16;
- sequenza 2048 token;
- batch 1;
- gradient accumulation 8;
- learning rate 2e-4.

## Fase 4 - Valutazione

Obiettivo: misurare Adriano con prompt fissi.

Metriche qualitative:

- italiano;
- concretezza;
- fedeltà;
- ragionamento;
- capacità di correggere premesse false;
- comportamento bilingue.

## Fase 5 - Release Locale

Obiettivo: versione usabile.

Output:

- adapter LoRA;
- modello merged;
- eventuale GGUF;
- scheda modello;
- esempi di utilizzo;
- changelog.

