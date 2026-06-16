# Notebook-Spezifikation

Diese Datei ist die Arbeits-Spec für die geplanten Analyse-Notebooks. Ziel ist, dass die Notebooks technische Details aus dem README auslagern und die wichtigsten Entscheidungen nachvollziehbar machen.

Orientierung: klassisches Bildklassifikations-Notebook mit Datenüberblick, Preprocessing, Trainingskurven, Confusion Matrix, Per-Class Metrics, Confidence-Auswertung und ROC Curve.

## Gemeinsame Regeln

- Sprache: Deutsch.
- Stil: technisch, knapp, keine langen Fließtexte.
- Keine Daten in `data/val/` verändern.
- Keine neuen Modelle aus Notebooks heraus ins Repo schreiben, außer das Team entscheidet das explizit.
- Plots mit klaren Titeln, Achsenbeschriftungen und kurzen Markdown-Interpretationen.
- Wenn ein benötigtes `predictions.csv` fehlt, Predictions im Notebook neu aus `data/val/` und `models/freshify_baseline_with_new_raw.keras` erzeugen.

## Datenquellen

Diese Quellen sollen im ersten Notebook dokumentiert werden:

| Quelle | Verwendung |
|---|---|
| https://www.kaggle.com/datasets/ulnnproject/food-freshness-dataset | Basisdatensatz für essbare und nicht essbare Lebensmittel |
| https://www.kaggle.com/datasets/yusufemir/lemon-quality-dataset | Ergänzung für Zitrone |
| https://www.kaggle.com/datasets/abdulbasit31/strawberry-dataset | Ergänzung für Erdbeere |
| https://www.kaggle.com/datasets/abdulrafeyyashir/fresh-vs-rotten-fruit-images | Ergänzende frische/verdorbene Obstbilder |
| https://www.kaggle.com/datasets/muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten | Ergänzung für Gurke/Paprika und weitere Fresh-vs-Rotten-Beispiele |
| Pexels | Einzelne ergänzende Bilder für `edible/zitrone` |
| Eigene Smartphonebilder | Zusätzliche realistischere `non_edible` Beispiele, inzwischen in `data/train/` übernommen |

## `01_data_exploration_and_preprocessing.ipynb`

Ziel: Das Notebook untersucht die finale Datensatzstruktur, Klassenverteilung und Kategorieverteilung. Zusätzlich dokumentiert es Preprocessing, Labelregeln und Data-Quality-Checks.

Inputs:

- `data/train/`
- `data/val/`
- `reports/dataset_manifest.csv`
- `reports/training_findings.md`

Zu erzeugende Tabellen:

- Gesamtverteilung pro Split:
  - `train edible`
  - `train non_edible`
  - `val edible`
  - `val non_edible`
- Kategorieverteilung pro Split, Label und Kategorie:
  - Banane
  - Erdbeere
  - Gurke
  - Orange
  - Paprika
  - Zitrone
- Tabelle schwacher Kategorien:
  - kleine Datenmenge
  - kleine Val-Menge
  - relevante Hinweise aus `reports/training_findings.md`
- Data-Quality-Tabelle:
  - nicht-lesbare Bilder
  - Nicht-Bild-Dateien
  - exakte Duplikate
  - Train-Val-Duplikate

Erwartete Plots:

- Balkendiagramm Train/Val-Verteilung nach `edible` und `non_edible`
- Balkendiagramm Kategorieverteilung pro Label
- Grid mit Beispielbildern pro Kategorie und Label
- Beispielbild vor/nach Resize auf `224 x 224`

Markdown-Interpretation:

- Warum `data/val/` klein ist und Metriken dadurch empfindlich sind.
- Warum `new_raw` nicht mehr als unabhängiger Holdout gilt.
- Welche Kategorien für spätere Datenerweiterung besonders relevant sind.
- Welche Labelregeln gelten:
  - `edible`: sicher essbar, darf optisch unperfekt sein
  - `non_edible`: Schimmel, Schleim, deutliche Fäule, starke Verderbnis

## `02_training.ipynb`

Ziel: Das Notebook erklärt das Training mit MobileNetV2 Transfer Learning und dokumentiert den Trainingsverlauf. Es soll zeigen, warum das finale Modell ausgewählt wurde.

Inputs:

- `data/train/`
- `data/val/`
- `models/freshify_baseline_with_new_raw.keras`
- `reports/freshify_baseline_with_new_raw/history.json`
- `reports/freshify_baseline_after_data_cleanup/history.json`
- Optionaler Kontext: `reports/training_findings.md`

Zu erklären:

- MobileNetV2 als vortrainierter Backbone.
- Eingabegröße `224 x 224`.
- Sigmoid-Output für binäre Klassifikation.
- Loss: `binary_crossentropy`.
- Modellentscheidung: aktuelle Baseline mit `new_raw` im Training.

Erwartete Plots:

- Training Loss Kurve
- Validation Loss Kurve
- Training Accuracy Kurve
- Validation Accuracy Kurve
- Vergleich:
  - Baseline nach Data Cleanup
  - Baseline mit `new_raw`

Erwartete Outputs:

- Tabelle der finalen Trainingsläufe:
  - Modellname
  - Datenstand
  - wichtigste Val-Metrik
  - kurze Entscheidung
- Modell-Pipeline-Abbildung:
  - Bild
  - Resize `224 x 224`
  - MobileNetV2
  - Klassifikationskopf
  - Sigmoid-Output
  - `edible` oder `non_edible`

Markdown-Interpretation:

- Warum Transfer Learning für das Projekt sinnvoll ist.
- Warum ein leichtgewichtiges Modell besser zum ML4B-Prototyp passt als eine komplexe Architektur.
- Warum zusätzliche echte Smartphonebilder für Robustheit wichtiger sind als unkontrollierte synthetische Daten.

## `03_evaluation.ipynb`

Ziel: Das Notebook bewertet das finale Modell auf `data/val/` und interpretiert die Metriken im Business-Kontext. Fokus liegt auf `non_edible` Recall, False Negatives und False Positives.

Inputs:

- `models/freshify_baseline_with_new_raw.keras`
- `data/val/`
- `reports/freshify_baseline_with_new_raw_threshold_035/evaluation.json`
- `reports/freshify_baseline_with_new_raw_threshold_045/evaluation.json`
- `reports/freshify_baseline_with_new_raw_threshold_050/evaluation.json`
- `reports/freshify_baseline_after_data_cleanup_threshold_035/evaluation.json`
- `reports/freshify_baseline_after_data_cleanup_threshold_040/evaluation.json`
- `reports/freshify_baseline_after_data_cleanup_threshold_045/evaluation.json`
- `reports/freshify_baseline_after_data_cleanup_threshold_050/evaluation.json`
- Optional: `reports/training_findings.md`

Wichtig:

- Für Confidence-Verteilungen und ROC Curve werden Bild-Level-Predictions benötigt.
- Falls in den Report-Ordnern kein `predictions.csv` vorhanden ist, im Notebook neue Predictions auf `data/val/` erzeugen.
- Der finale README-Stand verwendet Threshold `0.50`.

Zu erzeugende Tabellen:

- Threshold-Vergleich für `0.35`, `0.45`, `0.50`:
  - Accuracy
  - Precision `non_edible`
  - Recall `non_edible`
  - False Negatives
  - False Positives
- Per-Class Metrics:
  - Precision
  - Recall
  - F1
  - Support
- Fehlerbeispiele:
  - False Positives
  - False Negatives
  - wenn möglich mit Bildpfad und Modellscore

Erwartete Plots:

- Confusion Matrix für Threshold `0.50`
- Balkendiagramm Precision/Recall/F1 pro Klasse
- Threshold-Vergleich als Linien- oder Balkendiagramm
- Confidence-Verteilung getrennt nach echtem Label
- ROC Curve mit AUC
- Optional: Grid mit falsch klassifizierten Bildern

Markdown-Interpretation:

- Was `False Negative` im Projekt bedeutet:
  - verdorbenes Lebensmittel wird als `edible` durchgelassen
- Was `False Positive` bedeutet:
  - essbares Lebensmittel wird als auffällig markiert
- Warum `Recall non_edible` im Business Case besonders wichtig ist.
- Warum Precision trotzdem relevant bleibt, damit Human Review nicht zu viele unnötige Fälle bekommt.
- Warum ein neuer Real-World-Holdout mit `edible` und `non_edible` nötig ist.
