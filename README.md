# Food Freshness Categorizer

Binäres Bildklassifikationsprojekt für `edible` vs. `non_edible` mit MobileNetV2 Transfer Learning.

Das Projekt untersucht, ob ein leichtgewichtiges Modell Lebensmittelbilder zuverlässig als essbar oder nicht mehr essbar einordnen kann. Der Fokus liegt auf einem verständlichen, lokal ausführbaren ML-Workflow, nicht auf maximaler Modellkomplexität.

## Kurzüberblick

- Input: Smartphonebild eines einzelnen Lebensmittels
- Output: `edible` oder `non_edible`
- Modell: MobileNetV2 Transfer Learning mit Sigmoid-Output
- Aufgabe: binäre Bildklassifikation
- Demo-Modell: `models/updated_raw_standard.keras`
- Empfohlener Demo-Threshold: `0.35`

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

Dadurch ist das Modell Teil eines Human-in-the-loop-Prozesses. Ein niedrigerer Threshold von `0.35` ist in diesem Kontext sinnvoll, weil verdächtige Lebensmittel eher markiert werden. Die endgültige Entscheidung bleibt beim Menschen.

## Ergebnisstand

### Validation Split

Der reguläre Validation Split `data/val/` enthält beide Klassen (`edible` und `non_edible`). Deshalb können hier vollständige Metriken wie Accuracy, Precision, Recall und Confusion Matrix berichtet werden.

Auf diesem Validation Split war die klassische Baseline ohne Online-Augmentation am stärksten:

| Modell | Augmentation | Accuracy | Precision `non_edible` | Recall `non_edible` | FN | FP |
|---|---|---:|---:|---:|---:|---:|
| `rerun_baseline` | keine | `0.8387` | `0.8750` | `0.7500` | `7` | `3` |
| `rerun_standard` | Standard | `0.8065` | `0.8333` | `0.7143` | `8` | `4` |
| `rerun_background` | Background | `0.8226` | `0.8696` | `0.7143` | `8` | `3` |

Interpretation: Die Baseline ist auf dem festen Validation Split am stärksten. Die Augmentationen sind trotzdem relevant, weil sie die Robustheit gegenüber echten Smartphonebildern verbessern können.

### Real-World-Holdout

Zusätzlich wurden 14 neue `non_edible` Smartphonebilder in `data/new_raw/` als separates Holdout-Testset ausgewertet. Diese Bilder wurden nicht ins Training gemischt.

| Modell | Threshold | Erkannte `non_edible` Bilder | Recall `non_edible` | False Negatives |
|---|---:|---:|---:|---:|
| `rerun_baseline` | `0.50` | `6/14` | `0.4286` | `8` |
| `rerun_baseline` | `0.35` | `8/14` | `0.5714` | `6` |
| `rerun_standard` | `0.35` | `6/14` | `0.4286` | `8` |
| `rerun_background` | `0.35` | `7/14` | `0.5000` | `7` |
| `updated_raw_standard` | `0.50` | `7/14` | `0.5000` | `7` |
| `updated_raw_standard` | `0.35` | `12/14` | `0.8571` | `2` |

Für die Demo wird deshalb `models/updated_raw_standard.keras` mit Threshold `0.35` empfohlen.

Wichtig: Das reguläre `data/val/` testet beide Klassen und liefert vollständige Validation-Metriken. Das zusätzliche Real-World-Holdout `data/new_raw/` enthält aktuell nur neue `non_edible` Smartphonebilder. Deshalb ist `12/14 = 85.7%` hier kein vollständiger Real-World-Accuracy-Wert, sondern der Recall bzw. die Detection Rate für die kritische Klasse auf neuen Smartphonebildern.

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
  data/val/non_edible/orange_non_edible_21b002f6319f.png \
  --model-path models/updated_raw_standard.keras \
  --threshold 0.35
```

Die Ausgabe enthält:

- vorhergesagtes Label
- Confidence
- Wahrscheinlichkeit für `non_edible`

### 3. Real-World-Holdout auswerten

```bash
PYTHONPATH=src ./venv/bin/python src/evaluate.py \
  --model-path models/updated_raw_standard.keras \
  --image-dir data/new_raw \
  --true-label non_edible \
  --threshold 0.35 \
  --report-dir reports/real_world_new_raw/updated_raw_standard_t035
```

Erwartetes Ergebnis:

- `12/14` neue `non_edible` Smartphonebilder werden korrekt erkannt
- `recall_non_edible`: `0.8571`
- verpasste Bilder: `IMG_9824.jpeg`, `IMG_9830.jpeg`

Die Evaluation schreibt:

- `evaluation.json`
- `predictions.csv`

### 4. Validation Split auswerten

```bash
PYTHONPATH=src ./venv/bin/python src/evaluate.py \
  --model-path models/rerun_baseline.keras \
  --threshold 0.5 \
  --report-dir reports/rerun_baseline
```

Dieser Lauf reproduziert die dokumentierte Baseline-Evaluation auf `data/val`.

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

Rohdaten:

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

`data/new_raw/` enthält neue Smartphonebilder, die als Real-World-Holdout genutzt werden. Diese Bilder bleiben bewusst außerhalb des Trainings.

## Training Und Experimente

### Datensatz neu aufbauen

```bash
PYTHONPATH=src ./venv/bin/python src/data.py --remove-loose-root-files
```

### Baseline trainieren

```bash
PYTHONPATH=src ./venv/bin/python src/train.py \
  --epochs 10 \
  --augmentation none \
  --experiment-name rerun_baseline \
  --model-path models/rerun_baseline.keras
```

### Standard-Augmentation trainieren

```bash
PYTHONPATH=src ./venv/bin/python src/train.py \
  --epochs 10 \
  --augmentation standard \
  --experiment-name rerun_standard \
  --model-path models/rerun_standard.keras
```

### Background-Augmentation trainieren

```bash
PYTHONPATH=src ./venv/bin/python src/train.py \
  --epochs 10 \
  --augmentation background \
  --experiment-name rerun_background \
  --model-path models/rerun_background.keras
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

Standard-Augmentation umfasst leichte Bildvariationen wie Flip, Rotation, Zoom und Kontrast. Background-Augmentation ersetzt bei geeigneten Bildern einfache Hintergründe durch synthetisch erzeugte Hintergründe.

Die Ergebnisse zeigen: Background-Augmentation ist ein sinnvolles Experiment zur Untersuchung von Background Bias, war in diesem Projekt aber nicht das stärkste finale Setup. Für die Präsentation ist diese Erkenntnis wichtig: echte Smartphonebilder sind für die Robustheit wertvoller als unbalancierte synthetische Hintergründe.

## Modell- Und Report-Artefakte

Behaltene Modellkandidaten:

- `models/rerun_baseline.keras`
- `models/rerun_standard.keras`
- `models/rerun_background.keras`
- `models/updated_raw_standard.keras`

Behaltene Reports:

- `reports/rerun_baseline/`
- `reports/rerun_standard/`
- `reports/rerun_background/`
- `reports/updated_raw_standard/`
- `reports/real_world_new_raw/`
- `reports/dataset_manifest.csv`

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
- Das zusätzliche Real-World-Holdout enthält aktuell nur neue `non_edible` Smartphonebilder.
- Deshalb kann für dieses separate Holdout aktuell nur der Real-World-Recall für `non_edible` berichtet werden, nicht die vollständige Real-World Accuracy.
- Background-Augmentation ist unausgewogen und sollte nicht als finale Hauptstrategie interpretiert werden.
- Object Detection ist im aktuellen Stand noch perspektivisch und nicht Teil des stabilen ML-CLI-Workflows.

## Präsentations-Kernaussage

Wir haben ein verständliches binäres Klassifikationsmodell für Lebensmittel-Frische gebaut. Auf dem klassischen Validation Split erreicht die Baseline eine Accuracy von `83.87%`. Für echte Smartphonebilder ist ein Standard-Augmentation-Modell mit konservativerem Threshold robuster: Es erkennt `12/14` neue `non_edible` Bilder korrekt, also `85.7%` Recall für die kritische Klasse.

Das Modell ist als Assistenzsystem gedacht: Es markiert Verdachtsfälle, die anschließend von Menschen überprüft werden. Damit passt der recall-orientierte Threshold zum Business Use Case, ohne die menschliche Finalprüfung zu ersetzen.
