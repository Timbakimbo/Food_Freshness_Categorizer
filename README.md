# Food Freshness Categorizer

Binäres Bildklassifikationsprojekt für `edible` vs. `non_edible` mit MobileNetV2 Transfer Learning.

Das Projekt untersucht, ob ein leichtgewichtiges Modell Lebensmittelbilder zuverlässig als essbar oder nicht mehr essbar einordnen kann. Der Fokus liegt auf einem verständlichen, lokal ausführbaren ML-Workflow, nicht auf maximaler Modellkomplexität.

## Kurzüberblick

- Input: Smartphonebild eines einzelnen Lebensmittels
- Output: `edible` oder `non_edible`
- Modell: MobileNetV2 Transfer Learning mit Sigmoid-Output
- Aufgabe: binäre Bildklassifikation
- Aktuell stärkste neue Baseline: `models/freshify_baseline_with_new_raw.keras`
- Empfohlener Threshold für diese Baseline: `0.50`

Unterstützte Lebensmittelkategorien im Datensatz:

- Banane
- Erdbeere
- Gurke
- Orange
- Paprika
- Zitrone

## Business-Kontext

Perspektivisch ist das Modell als Assistenzsystem für die Vorsortierung von Lebensmitteln gedacht, nicht als finale Wegwerfentscheidung.

Geplanter Workflow:

1. Ein Bild oder Videoframe enthält mehrere Lebensmittel.
2. Eine Object Detection erkennt einzelne Lebensmittel und erzeugt Crops.
3. Der Classifier bewertet jeden Crop als `edible` oder `non_edible`.
4. Verdächtige Fälle werden markiert.
5. Menschen prüfen die markierten Lebensmittel final.

Dadurch ist das Modell Teil eines Human-in-the-loop-Prozesses. In diesem Kontext sind False Negatives kritischer als False Positives: Ein verdorbenes Lebensmittel sollte möglichst nicht als essbar durchgehen. False Positives sind fachlich eher akzeptabel, weil auffällige Fälle noch einmal menschlich geprüft werden. Sie dürfen aber nicht zu hoch werden, sonst wird der Review-Prozess ineffizient.

## Ergebnisstand

### Validation Split

Der reguläre Validation Split `data/val/` enthält beide Klassen (`edible` und `non_edible`). Deshalb können hier vollständige Metriken wie Accuracy, Precision, Recall und Confusion Matrix berichtet werden.

Die neue stärkste Baseline wurde nach Datenbereinigung und Aufnahme der eigenen `new_raw`-Smartphonebilder in das Training erstellt.

Wichtig: `data/new_raw` ist dadurch kein unabhängiger Testdatensatz mehr. Für die nächste echte Real-World-Aussage muss ein neuer Holdout-Datensatz mit `edible` und `non_edible` Bildern aufgebaut werden.

| Modell | Threshold | Validation Accuracy | Precision `non_edible` | Recall `non_edible` | False Negatives | False Positives |
|---|---:|---:|---:|---:|---:|---:|
| `freshify_old_final_demo.keras` | `0.35` | `0.7581` | `0.6757` | `0.8929` | `3` | `12` |
| `freshify_old_background_augmentation.keras` | `0.35` | `0.8548` | `0.8065` | `0.8929` | `3` | `6` |
| `freshify_baseline_after_data_cleanup.keras` | `0.50` | `0.8065` | `0.7353` | `0.8929` | `3` | `9` |
| `freshify_baseline_with_new_raw.keras` | `0.50` | `0.9032` | `0.8929` | `0.8929` | `3` | `3` |

Interpretation: Die neue Baseline mit `new_raw` im Training ist auf dem regulären Validation Split aktuell der stärkste Stand. Sie hält denselben `non_edible` Recall wie die besten alten Modelle, reduziert aber die False Positives deutlich.

### Historischer Alt-vs-Neu-Vergleich

Vor der Aufnahme von `data/new_raw` in das Training wurden die neu trainierten Modelle zusätzlich gegen die alten Modellartefakte bei gleichem Threshold `0.35` verglichen.

| Stand | Modell | Val Accuracy | Recall `non_edible` | False Negatives `non_edible` | Real-World-Check `data/new_raw` |
|---|---|---:|---:|---:|---:|
| alt | altes finales Modell | `0.7581` | `0.8929` | `3` | `12/14` |
| alt | alte Standard-Augmentation | `0.8065` | `0.8571` | `4` | `6/14` |
| alt | alte Background-Augmentation | `0.8548` | `0.8929` | `3` | `7/14` |
| neu | neue No-Augmentation | `0.7097` | `0.9643` | `1` | `10/14` |
| neu | neue Standard-Augmentation | `0.7903` | `0.8571` | `4` | `7/14` |
| neu | neue Background-Augmentation | `0.7903` | `0.8929` | `3` | `7/14` |

Fazit: Vor der Aufnahme von `new_raw` war das alte Background-Augmentation-Modell der beste Allrounder. Nach der Aufnahme von `new_raw` ist die neue Baseline auf `data/val` stärker. Der nächste notwendige Schritt ist ein neuer unabhängiger Real-World-Holdout.

### Real-World-Holdout

Die 14 neuen `non_edible` Smartphonebilder aus `data/new_raw/` wurden inzwischen bewusst in das Training aufgenommen, um die kritische Klasse mit eigenen Bildern zu stärken.

Deshalb gilt ab diesem Stand:

- `data/new_raw` ist Trainingsmaterial.
- Ergebnisse auf `data/new_raw` sind nicht mehr als unabhängige Testmetriken gültig.
- Ein neuer Real-World-Holdout sollte unter `data/holdout_real_world/` aufgebaut werden.
- Dieser Holdout sollte beide Klassen enthalten: `edible` und `non_edible`.

Ausführlichere Trainingsnotizen stehen in `reports/training_findings.md`.

## Abbildungen

Für README und Präsentation sind zwei Abbildungen sinnvoll:

1. Business-Workflow: Kamera oder Bildaufnahme -> optional Object Detection/Crop -> Freshify Classifier -> Markierung auffälliger Fälle -> Human Review
2. Modell-Pipeline: Bild -> Resize auf `224 x 224` -> MobileNetV2 Backbone -> Klassifikationskopf -> `edible` oder `non_edible`

Die Bilddateien sollten erst eingebunden werden, wenn sie im Repository liegen, zum Beispiel unter `docs/images/`. Dadurch zeigt GitHub keine kaputten Bildlinks an.

## Get Started

Diese Schritte testen den stabilen ML-Teil des Projekts über die Kommandozeile. Die Streamlit-UI wird parallel weiterentwickelt und sollte nach dem Merge der UI-Arbeit als zusätzlicher Demo-Einstieg verwendet werden.

### 1. Umgebung einrichten

Python-Version:

```text
Python 3.10
```

Setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Einzelbild klassifizieren

```bash
PYTHONPATH=src ./venv/bin/python src/predict.py \
  data/val/non_edible/orange/orange_non_edible_21b002f6319f.png \
  --model-path models/freshify_baseline_with_new_raw.keras \
  --threshold 0.50
```

Die Ausgabe enthält:

- vorhergesagtes Label
- Confidence
- Wahrscheinlichkeit für `non_edible`

### 3. Validation Split auswerten

```bash
PYTHONPATH=src ./venv/bin/python src/evaluate.py \
  --model-path models/freshify_baseline_with_new_raw.keras \
  --threshold 0.50 \
  --report-dir reports/freshify_baseline_with_new_raw_threshold_050
```

Erwartetes Ergebnis:

- Validation Accuracy: ca. `0.9032`
- `recall_non_edible`: ca. `0.8929`
- False Positives `non_edible`: `3`

Die Evaluation schreibt:

- `evaluation.json`
- `predictions.csv`

### 4. Neuer Real-World-Holdout

Der alte Ordner `data/new_raw/` wurde in das Training aufgenommen. Für eine neue unabhängige Real-World-Auswertung sollte ein frischer Testordner aufgebaut werden:

```text
data/holdout_real_world/
  edible/<kategorie>/
  non_edible/<kategorie>/
```

Erst dieser neue Holdout kann wieder als unabhängiger Real-World-Test verwendet werden.

### 5. Streamlit UI

Die Streamlit-App liegt unter:

```text
app/streamlit_app.py
```

Sie ist als UI-Demo vorgesehen, der finale UI-Stand wird aber im Team parallel entwickelt. Für eine robuste Prüfung durch Dozenten ist aktuell der CLI-Weg oben der stabilere Einstieg.

Nach dem UI-Merge kann die App typischerweise so gestartet werden:

```bash
streamlit run app/streamlit_app.py
```

## Projektstruktur

```text
food_freshness/
├── app/
│   └── streamlit_app.py
├── data/
│   ├── train/
│   ├── val/
│   └── new_raw/
├── dataset_cat1/
├── dataset_cat2/
├── generated/
│   ├── background_aug/
│   └── background_library/
├── models/
├── reports/
├── src/
│   ├── background_augment.py
│   ├── config.py
│   ├── data.py
│   ├── evaluate.py
│   ├── model.py
│   ├── predict.py
│   └── train.py
├── AGENTS.md
├── README.md
└── requirements.txt
```

## Datensatz

Die Daten stammen aus einer Kombination aus öffentlichem Kaggle-Datensatz und eigenen Smartphonebildern.

Kaggle-Datensatz:

```text
https://www.kaggle.com/datasets/ulnnproject/food-freshness-dataset
```

Eigene Bilder:

- zusätzliche Smartphonebilder, um das Modell näher an realistischere Testbedingungen zu bringen
- die 14 Bilder aus `data/new_raw/` wurden inzwischen als `non_edible` in das Training übernommen

Rohdaten im Projekt:

- `dataset_cat1/` enthält `edible` Bilder
- `dataset_cat2/` enthält `non_edible` Bilder

Trainierbarer Datensatz:

```text
data/
├── train/
│   ├── edible/
│   └── non_edible/
├── val/
│   ├── edible/
│   └── non_edible/
└── new_raw/
```

`data/new_raw/` ist ab dem aktuellen Stand kein unabhängiger Holdout mehr, sondern Quelle für zusätzliche Trainingsbilder. Ein neuer unabhängiger Real-World-Holdout sollte unter `data/holdout_real_world/` aufgebaut werden.

### Datenaufteilung

Aktueller Stand des strukturierten Datensatzes:

| Split | `edible` | `non_edible` | Gesamt |
|---|---:|---:|---:|
| `data/train` | 265 | 215 | 480 |
| `data/val` | 34 | 28 | 62 |

`data/train` und `data/val` bilden den regulären Datensatz mit beiden Klassen. `data/val` bleibt der aktuelle Vergleichssplit.

### Kategorienverteilung

Die aktuelle Verteilung nach Lebensmittelkategorie ist nicht vollständig balanciert:

| Kategorie | `edible` | `non_edible` | Gesamt |
|---|---:|---:|---:|
| Banane | 87 | 55 | 142 |
| Orange | 60 | 47 | 107 |
| Gurke | 49 | 38 | 87 |
| Paprika | 42 | 51 | 93 |
| Erdbeere | 32 | 26 | 58 |
| Zitrone | 29 | 26 | 55 |

Banane und Orange sind weiterhin stark vertreten, aber Zitrone, Erdbeere, Paprika und Gurke wurden gezielt ergänzt. Die Kategorien sind trotzdem nicht perfekt balanciert, deshalb sollten die Ergebnisse als Gesamtbewertung des binären Klassifikators interpretiert werden.

## Training und Experimente

### Datensatz neu aufbauen

```bash
PYTHONPATH=src ./venv/bin/python src/data.py --remove-loose-root-files
```

### Modell ohne Augmentation trainieren

```bash
PYTHONPATH=src ./venv/bin/python src/train.py \
  --epochs 10 \
  --augmentation none \
  --experiment-name freshify_baseline_with_new_raw \
  --model-path models/freshify_baseline_with_new_raw.keras
```

Das aktuell stärkste neue Baseline-Modell liegt unter `models/freshify_baseline_with_new_raw.keras`.

### Standard-Augmentation trainieren

```bash
PYTHONPATH=src ./venv/bin/python src/train.py \
  --epochs 10 \
  --augmentation standard \
  --experiment-name freshify_standard_augmentation_retrained \
  --model-path models/freshify_standard_augmentation.keras
```

### Background-Augmentation trainieren

```bash
PYTHONPATH=src ./venv/bin/python src/train.py \
  --epochs 10 \
  --augmentation background \
  --experiment-name freshify_background_augmentation_retrained \
  --model-path models/freshify_background_augmentation.keras
```

### Background-Augmentation neu erzeugen

```bash
PYTHONPATH=src ./venv/bin/python src/background_augment.py --variants-per-image 2
```

## Augmentation-Einordnung

Es wurden drei Strategien verglichen:

1. Keine Online-Augmentation
2. Standard-Augmentation
3. Background-Augmentation

Standard-Augmentation umfasst leichte Bildvariationen wie Flip, Rotation, Zoom und Kontrast. Die aktuelle Background-Variante im Training nutzt zusätzlich Helligkeits- und stärkere Kontrastvariation. Separat existieren generierte Background-Bilder unter `generated/background_aug/`; diese wurden im aktuellen Re-Training nicht zusätzlich in `data/train` eingemischt.

Die Ergebnisse zeigen: Augmentation kann die Validation Accuracy verbessern, war in diesem Projekt aber nicht das stärkste finale Setup für neue Smartphonebilder. Für die Präsentation ist diese Erkenntnis wichtig: echte Smartphonebilder sind für die Robustheit wertvoller als unbalancierte synthetische Hintergründe.

Nach der Aufnahme der eigenen `new_raw`-Bilder ist die neue Baseline ohne Augmentation aktuell stärker als die alten Augmentation-Stände auf `data/val`. Gezielte Augmentation bleibt der nächste sinnvolle Versuch, sollte aber gegen diese neue Baseline verglichen werden.

## Modell- und Report-Artefakte

Behaltene Modellkandidaten:

- `models/freshify_baseline_with_new_raw.keras`
- `models/freshify_baseline_after_data_cleanup.keras`
- `models/freshify_old_final_demo.keras`
- `models/freshify_old_background_augmentation.keras`
- `models/freshify_standard_augmentation.keras`
- `models/freshify_background_augmentation.keras`

Reports:

- `reports/dataset_manifest.csv` dokumentiert den aktuellen Train/Validation-Datensatz.
- `reports/training_findings.md` fasst die wichtigsten Trainings- und Evaluationsfindings zusammen.
- `reports/freshify_baseline_with_new_raw_threshold_050/` enthält die aktuelle beste Validation-Auswertung.
- Weitere Report-Ordner sind historische Experimentausgaben. Neue Reports können über die Commands im Abschnitt `Get Started` mit den aktuellen Modellnamen erzeugt werden.

## Wichtige Code-Dateien

- `src/data.py`: baut den Datensatz und erzeugt Train/Val-Splits
- `src/model.py`: definiert MobileNetV2 und die Augmentationen
- `src/train.py`: trainiert das Modell
- `src/evaluate.py`: evaluiert Validation Split oder externe Bildordner
- `src/predict.py`: klassifiziert ein einzelnes Bild
- `src/background_augment.py`: erzeugt optionale Background-Augmentationsbilder
- `app/streamlit_app.py`: einfache UI-Demo, finaler UI-Stand nach Team-Merge

## Limitationen

- Der Datensatz ist klein.
- Nicht alle Kategorien sind gleich stark vertreten.
- Der reguläre Validation Split enthält beide Klassen und erlaubt vollständige Validation-Metriken.
- `data/new_raw` wurde in das Training aufgenommen und ist deshalb kein unabhängiger Test mehr.
- Für echte Real-World Accuracy fehlt noch ein neuer Holdout mit `edible` und `non_edible`.
- Background-Augmentation ist unausgewogen und sollte nicht als finale Hauptstrategie interpretiert werden.
- Object Detection ist im aktuellen Stand noch perspektivisch und nicht Teil des stabilen ML-CLI-Workflows.

## Präsentations-Kernaussage

Wir haben ein verständliches binäres Klassifikationsmodell für Lebensmittel-Frische gebaut. Nach Datenbereinigung und Aufnahme eigener `non_edible` Smartphonebilder erreicht die neue Baseline auf dem Validation Split `90.32%` Accuracy, `89.29%` Recall für `non_edible` und nur 3 False Positives.

Das Modell ist als Assistenzsystem gedacht: Es markiert Verdachtsfälle, die anschließend von Menschen überprüft werden. Dadurch ist hoher `non_edible` Recall wichtiger als reine Accuracy. Der nächste notwendige Schritt ist ein neuer Real-World-Holdout mit beiden Klassen.
