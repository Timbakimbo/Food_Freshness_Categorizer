# Food Freshness Categorizer

Binäres Bildklassifikationsprojekt für `edible` vs. `non_edible` mit MobileNetV2 Transfer Learning.

Das Projekt untersucht, ob ein leichtgewichtiges Modell Lebensmittelbilder zuverlässig als essbar oder nicht mehr essbar einordnen kann. Der Fokus liegt auf einem verständlichen, lokal ausführbaren ML-Workflow, nicht auf maximaler Modellkomplexität.

## Kurzüberblick

- Input: Smartphonebild eines einzelnen Lebensmittels
- Output: `edible` oder `non_edible`
- Modell: MobileNetV2 Transfer Learning mit Sigmoid-Output
- Aufgabe: binäre Bildklassifikation
- Demo-Modell: `models/freshify_final.keras`
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

Für den finalen Vergleich behalten wir drei Modellartefakte. Das finale Demo-Modell ist nicht automatisch das Modell mit der höchsten Validation Accuracy, sondern das Modell, das im aktuellen Streamlit-/Demo-Setup und auf den neuen Smartphonebildern am besten zum Use Case passt.

| Modell | Variante | Validation Accuracy | Precision `non_edible` | Recall `non_edible` | Real-World-Check `data/new_raw` |
|---|---|---:|---:|---:|---:|
| `freshify_final.keras` | finales Demo-Modell | `0.7581` | `0.6757` | `0.8929` | `12/14` |
| `freshify_standard_augmentation.keras` | Standard-Augmentation | `0.8065` | `0.7500` | `0.8571` | `6/14` |
| `freshify_background_augmentation.keras` | Background-Augmentation | `0.8548` | `0.8065` | `0.8929` | `7/14` |

Die Tabelle nutzt den aktuellen Business-Threshold `0.35`, weil dieser auch für die Demo verwendet wird.

Interpretation: Background-Augmentation liefert in diesem Lauf das beste Validation-Ergebnis. Für die neuen Smartphonebilder ist aber das finale Demo-Modell deutlich stärker. Das zeigt den Domain-Gap zwischen Validation Split und realistischeren Smartphonebildern: Ein Modell kann auf `data/val/` besser aussehen, aber auf neuen Bildern schlechter generalisieren.

### Real-World-Holdout

Zusätzlich wurden 14 neue `non_edible` Smartphonebilder in `data/new_raw/` als separates Holdout-Testset ausgewertet. Diese Bilder wurden nicht ins Training gemischt.

| Modell | Threshold | Erkannte `non_edible` Bilder | Recall `non_edible` | False Negatives |
|---|---:|---:|---:|---:|
| `freshify_final.keras` | `0.35` | `12/14` | `0.8571` | `2` |
| `freshify_standard_augmentation.keras` | `0.35` | `6/14` | `0.4286` | `8` |
| `freshify_background_augmentation.keras` | `0.35` | `7/14` | `0.5000` | `7` |

Für die Demo wird deshalb `models/freshify_final.keras` mit Threshold `0.35` empfohlen.

Wichtig: Das reguläre `data/val/` testet beide Klassen und liefert vollständige Validation-Metriken. Das zusätzliche Real-World-Holdout `data/new_raw/` enthält aktuell nur neue `non_edible` Smartphonebilder. Deshalb ist `12/14 = 85.7%` hier kein vollständiger Real-World-Accuracy-Wert, sondern der Recall bzw. die Detection Rate für die kritische Klasse auf neuen Smartphonebildern.

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
  data/val/non_edible/orange_non_edible_21b002f6319f.png \
  --model-path models/freshify_final.keras \
  --threshold 0.35
```

Die Ausgabe enthält:

- vorhergesagtes Label
- Confidence
- Wahrscheinlichkeit für `non_edible`

### 3. Real-World-Holdout auswerten

```bash
PYTHONPATH=src ./venv/bin/python src/evaluate.py \
  --model-path models/freshify_final.keras \
  --image-dir data/new_raw \
  --true-label non_edible \
  --threshold 0.35 \
  --report-dir reports/real_world_new_raw/freshify_final_t035
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
  --model-path models/freshify_final.keras \
  --threshold 0.35 \
  --report-dir reports/freshify_final
```

Dieser Lauf reproduziert die dokumentierte Evaluation des finalen Demo-Modells auf `data/val`.

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
- `data/new_raw/` enthält aktuell 14 neue `non_edible` Smartphonebilder als separaten Real-World-Check

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

`data/new_raw/` enthält neue Smartphonebilder, die als Real-World-Holdout genutzt werden. Diese Bilder bleiben bewusst außerhalb des Trainings.

### Datenaufteilung

Aktueller Stand des strukturierten Datensatzes:

| Split | `edible` | `non_edible` | Gesamt |
|---|---:|---:|---:|
| `data/train` | 137 | 117 | 254 |
| `data/val` | 34 | 28 | 62 |
| `data/new_raw` | 0 | 14 | 14 |

`data/train` und `data/val` bilden den regulären Datensatz mit beiden Klassen. `data/new_raw` ist kein vollständiger Testdatensatz, sondern ein zusätzlicher Real-World-Check für die kritische Klasse `non_edible`.

### Kategorienverteilung

Die aktuelle Verteilung nach Lebensmittelkategorie ist nicht vollständig balanciert:

| Kategorie | `edible` | `non_edible` | Gesamt |
|---|---:|---:|---:|
| Banane | 45 | 39 | 84 |
| Paprika | 26 | 45 | 71 |
| Orange | 31 | 23 | 54 |
| Gurke | 30 | 12 | 42 |
| Erdbeere | 27 | 13 | 40 |
| Zitrone | 12 | 13 | 25 |

Banane und Paprika sind am stärksten vertreten. Zitrone ist die kleinste Kategorie. Besonders bei `non_edible` sind Gurke, Erdbeere und Zitrone relativ schwach vertreten. Deshalb sollten die Ergebnisse nicht als gleich starke Aussage für jede einzelne Lebensmittelart interpretiert werden, sondern als Gesamtbewertung des binären Klassifikators.

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
  --experiment-name freshify_final \
  --model-path models/freshify_final.keras
```

### Standard-Augmentation trainieren

```bash
PYTHONPATH=src ./venv/bin/python src/train.py \
  --epochs 10 \
  --augmentation standard \
  --experiment-name freshify_standard_augmentation \
  --model-path models/freshify_standard_augmentation.keras
```

### Background-Augmentation trainieren

```bash
PYTHONPATH=src ./venv/bin/python src/train.py \
  --epochs 10 \
  --augmentation background \
  --experiment-name freshify_background_augmentation \
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

Standard-Augmentation umfasst leichte Bildvariationen wie Flip, Rotation, Zoom und Kontrast. Background-Augmentation ersetzt bei geeigneten Bildern einfache Hintergründe durch synthetisch erzeugte Hintergründe.

Die Ergebnisse zeigen: Background-Augmentation ist ein sinnvolles Experiment zur Untersuchung von Background Bias, war in diesem Projekt aber nicht das stärkste finale Setup. Für die Präsentation ist diese Erkenntnis wichtig: echte Smartphonebilder sind für die Robustheit wertvoller als unbalancierte synthetische Hintergründe.

## Modell- und Report-Artefakte

Behaltene Modellkandidaten:

- `models/freshify_final.keras`
- `models/freshify_standard_augmentation.keras`
- `models/freshify_background_augmentation.keras`

Reports:

- `reports/dataset_manifest.csv` dokumentiert den aktuellen Train/Validation-Datensatz.
- `reports/real_world_new_raw/` enthält Real-World-Auswertungen auf den neuen Smartphonebildern.
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
- Das zusätzliche Real-World-Holdout enthält aktuell nur neue `non_edible` Smartphonebilder.
- Deshalb kann für dieses separate Holdout aktuell nur der Real-World-Recall für `non_edible` berichtet werden, nicht die vollständige Real-World Accuracy.
- Background-Augmentation ist unausgewogen und sollte nicht als finale Hauptstrategie interpretiert werden.
- Object Detection ist im aktuellen Stand noch perspektivisch und nicht Teil des stabilen ML-CLI-Workflows.

## Präsentations-Kernaussage

Wir haben ein verständliches binäres Klassifikationsmodell für Lebensmittel-Frische gebaut. Im Modellvergleich erreicht Background-Augmentation auf dem Validation Split die stärkste Accuracy von `85.48%`. Für echte Smartphonebilder ist jedoch das finale Demo-Modell robuster: Es erkennt `12/14` neue `non_edible` Bilder korrekt, also `85.7%` Recall für die kritische Klasse.

Das Modell ist als Assistenzsystem gedacht: Es markiert Verdachtsfälle, die anschließend von Menschen überprüft werden. Damit passt der recall-orientierte Threshold zum Business Use Case, ohne die menschliche Finalprüfung zu ersetzen.
