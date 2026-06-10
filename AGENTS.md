# Food Freshness Categorizer — AGENTS.md

## Projektziel

Entwicklung eines verständlichen und präsentierbaren ML4B-Projekts zur binären Klassifikation von Lebensmitteln.

Klassen:
- edible
- non_edible

Das Projekt soll:
- erklärbarl
- modular
- leichtgewichtig
- akademisch präsentierbar

bleiben.

Unnötige Komplexität vermeiden.

---

# Hauptziel

Input:
- Smartphonebild eines Lebensmittels

Output:
- edible
- non_edible

Aktueller Fokus:
- Klassifikation einzelner Objekte

Optionales Bonusfeature:
- Multi-Object Detection mit Bounding Boxes

---

# Technologie-Stack

Bevorzugter Stack:
- Python
- TensorFlow / Keras
- NumPy
- Streamlit
- MobileNetV2 Transfer Learning

Erlaubt:
- OpenCV
- Pillow
- rembg
- YOLO (nur als optionales Bonusfeature)

Vermeiden:
- unnötige Frameworks
- Cloud-Infrastruktur
- Microservices
- verteilte Systeme
- komplexe Frontend-Frameworks

---

# Repository-Struktur

Bevorzugte Struktur:

src/
- config.py
- data.py
- model.py
- train.py
- predict.py
- evaluate.py

app/
- streamlit_app.py

models/
data/

Module klein und verständlich halten.

---

# ML-Rahmenbedingungen

Dies ist ein binäres Bildklassifikationsproblem.

Verwenden:
- MobileNetV2 Transfer Learning
- sigmoid Output
- binary_crossentropy

Bevorzugter Ansatz:
- zunächst eingefrorener Backbone
- leichter Klassifikationskopf
- einfache Preprocessing-Pipeline

Vermeiden:
- Transformer
- GANs
- unnötig komplexe Forschungsarchitekturen
- exzessives Hyperparameter-Tuning

---

# Datensatz-Regeln

Datensatz-Struktur:

data/
train/
edible/
non_edible/

val/
edible/
non_edible/

Labels müssen bei allen Teammitgliedern konsistent sein.

Erlaubte Lebensmittelkategorien:
- Erdbeere
- Banane
- Paprika
- Orange
- Gurke
- Zitrone

---

# Labeling-Regeln

edible:
- sicher essbar
- darf unperfekt aussehen
- darf leicht älter sein
- darf braune Stellen haben

non_edible:
- Schimmel
- Schleim
- deutliche Fäule
- starke Verderbnis
- nicht mehr sicher essbar

Leicht unansehnliche Lebensmittel nicht als non_edible labeln.

---

# Augmentations-Strategie

Das Projekt soll experimentell vergleichen:

1. Keine Augmentation
2. Standard-Augmentation
3. Background-Augmentation

Ziel:
Untersuchung der Auswirkungen auf:
- Validation Accuracy
- Robustheit
- Generalisierung auf Smartphonebilder

---

# Standard-Augmentation

Erlaubt:
- Horizontal Flip
- kleine Rotationen
- Zoom
- Helligkeitsänderungen
- Kontraständerungen

Augmentation leichtgewichtig halten.

---

# Background-Augmentation

Als optionaler Preprocessing-Schritt erlaubt.

Workflow:
1. weißen/einfachen Hintergrund entfernen
2. Objekt auf realistischen Hintergrund setzen
3. Modell erneut trainieren und vergleichen

Bevorzugte Tools:
- rembg
- Pillow
- OpenCV

Ziel:
Reduktion von Background Bias und teilweise Verringerung des Domain Gaps.

Wichtig:
Background-Augmentation ersetzt niemals echte Smartphonebilder.

Echte Smartphonebilder bleiben die wichtigste Datenquelle.

Vermeiden:
- Diffusion Models
- synthetische Szenengenerierung
- photorealistische Simulationspipelines

---

# Evaluation

Bevorzugte Metriken:
- Validation Accuracy
- Precision
- Recall
- Confusion Matrix

Wichtig:
Recall für non_edible ist besonders relevant.

Alle Augmentationsstrategien sollen experimentell verglichen werden.

---

# Streamlit

Streamlit einfach halten.

Bevorzugte Features:
- Bild-Upload
- Prediction
- Confidence Score

Optionales Bonusfeature:
- Bounding Boxes bei Multi-Object Detection

Frontend nicht overengineeren.

---

# Object Detection (Optionales Bonusfeature)

Mögliche spätere Erweiterung:

Bild mit mehreren Lebensmitteln
→ Object Detection
→ Crop jedes Objekts
→ edible/non_edible Klassifikation
→ grüne/rote Bounding Boxes

Bevorzugter Ansatz:
- pretrained YOLO
- bestehendes Klassifikationsmodell für Crops wiederverwenden

Kein großes eigenes Detection-Modell trainieren, außer falls wirklich notwendig.

---

# Git-Workflow

Niemals direkt auf main committen.

Immer Feature-Branches verwenden.

Beispiele:
- feature/augmentation
- feature/streamlit
- feature/evaluation

Commits klein und verständlich halten.

---

# Coding Style

Bevorzugen:
- Lesbarkeit
- kleine Funktionen
- klare Variablennamen
- Kommentare für wichtige ML-Logik

Vermeiden:
- unnötige Abstraktionen
- tief verschachtelte Architekturen
- Overengineering

Wenn unsicher:
immer die einfachere Lösung bevorzugen.

Der Code soll jederzeit für Studierende nachvollziehbar bleiben.