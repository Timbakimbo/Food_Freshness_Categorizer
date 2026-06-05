# Freshify

# Quickstart

1. Setup the repository:
```bash
git clone https://github.com/Timbakimbo/Food_Freshness_Categorizer
cd Food_Freshness_Categorizer
```

2. Install dependencies:
```bash
uv sync
```
If UV is not installed yet, have a look at it [here!](https://docs.astral.sh/uv/)


3. Run a local prediction:
```bash
uv run main.py predict path/to/image.jpg
```

4. Run it with Streamlit:
```bash
uv run streamlit run app/streamlit.py
```

5. Evaluate the classifier:
```bash
uv run main.py evaluate --model models/...
```
## Tests
```
# EASY: 
uv run main.py predict data/raw/edible/paprika/paprika12.jpeg
uv run main.py predict data/raw/non_edible/banane/banane1.png

# HARD: 
uv run main.py predict data/raw/edible/banane/banane17.jpg
uv run main.py predict data/raw/non_edible/paprika/paprika19.jpeg
```