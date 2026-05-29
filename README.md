# Food_Freshness_Categorizer

# Quickstart

1. Setup the repository:
```
git clone https://github.com/Timbakimbo/Food_Freshness_Categorizer
cd Food_Freshness_Categorizer
```

2. Setup a environment:
```
python -m venv .venv
source .venv/bin/activate    # Windows: venv\Scripts\activate
```

3. Install all dependencies:
```
pip install -r requirements.txt
```

4. Start Streamlit:
```
streamlit run app/streamlit.py
```

5. For development purposes:
```
# Run a local prediction
python main.py predict path/to/image.jpg

#TODO: Train the classifier
python main.py train --data-dir data
```
## Tests
```
# EASY: 
python main.py predict data/raw/edible/paprika/paprika12.jpeg
python main.py predict data/raw/non_edible/banane/banane1.png

# HARD: 
python main.py predict data/raw/edible/banane/banane17.jpg
python main.py predict data/raw/non_edible/paprika/paprika19.jpeg
```

# Structure
TODO: Describe

## Highlevel Folder
TODO: Describe

```
root/
│
├── data/
│
├── logs/
│
├── doc/
│
├── models/
│   ├── classifier.keras
│
├── src/
│   ├── data_loader.py
│   ├── train.py
│   ├── predict.py
│   ├── ...
│
├── app/
│   ├── streamlit.py
│
├── config/
│   ├── config.yaml
│   ├── ...
│
├── main.py
├── requirements.txt
└── README.md
```

## Data Folder
TODO: Describe

```
root/
│
├── data/
│   ├── generated/
│   │    ├── background_aug/
│   │    │    ├── ediable/
│   │    │    │      ├── <categories>/
│   │    │    │      │       ├── <files>
│   │    │    │      ├── .../
│   │    │    │      │       ├── ...
│   │    │    ├── non_ediable/
│   │    │    │      ├── <categories>/
│   │    │    │      │       ├── <files>
│   │    │    │      ├── .../
│   │    │    │      │       ├── ...
│   │
│   ├── raw/
│   │    ├── unsorted/
│   │    ├── ediable/
│   │    │      ├── <categories>/
│   │    │      │       ├── <files>
│   │    │      ├── .../
│   │    │      │       ├── ...
│   │    ├── non_ediable/
│   │    │      ├── <categories>/
│   │    │      │       ├── <files>
│   │
│   ├── train/
│   │   ├── edible/
│   │   │    ├── <categories>/
│   │   │    │      ├── <files>
│   │   │    ├── .../
│   │   │    │      ├── ...
│   │   ├── non_edible/
│   │   │    ├── <categories>/
│   │   │    │      ├── <files>
│   │   │    ├── .../
│   │   │    │      ├── ...
│   │
│   ├── val/
│   │   ├── edible/
│   │   │    ├── <categories>/
│   │   │    │      ├── <files>
│   │   │    ├── .../
│   │   │    │      ├── ...
│   │   ├── non_edible/
│   │   │    ├── <categories>/
│   │   │    │      ├── <files>
│
├── ...
```

# Usefull stuff
## Scripts
``move_rename_images.py``:
Move files from a ``SRC`` to ``DST`` directory, replacing each file's number with the next available one based on the highest number already present in the destination — preserving the original filename and extension.

``image_resize.py``:
Recursively processes all JPEG, PNG, and HEIC images from a source directory, resizes them to a centered 224×224 square (scale-then-pad, no distortion) with EXIF orientation correction, and saves them as compressed progressive JPEGs to a mirrored destination directory structure.

## CLI
TLDR: ``for f in data/train/edible/*.jpg; do mv -- "$f" "${f%.jpg}.jpeg"; done``