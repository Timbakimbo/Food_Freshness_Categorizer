from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import streamlit as st
import tensorflow as tf


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DEFAULT_TRAIN_CONFIG  # noqa: E402
from predict import predict_image  # noqa: E402


@st.cache_resource
def load_model(model_path: Path) -> tf.keras.Model:
    return tf.keras.models.load_model(model_path)


def main() -> None:
    st.set_page_config(page_title="Food Freshness Classifier", page_icon="🥬")
    st.title("Food Freshness Classifier")
    st.write("Lade ein einzelnes Lebensmittelbild hoch und erhalte eine Binary-Vorhersage.")

    model_path = DEFAULT_TRAIN_CONFIG.model_path
    if not model_path.exists():
        st.error(f"Kein Modell gefunden unter {model_path}")
        return

    uploaded_file = st.file_uploader("Bild hochladen", type=["jpg", "jpeg", "png", "heic"])
    if uploaded_file is None:
        return

    st.image(uploaded_file, caption="Eingabebild", use_container_width=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix or ".jpg") as handle:
        handle.write(uploaded_file.getbuffer())
        temp_path = Path(handle.name)

    try:
        model = load_model(model_path)
        result = predict_image(model, temp_path, DEFAULT_TRAIN_CONFIG.image_size)
    finally:
        temp_path.unlink(missing_ok=True)

    st.subheader("Vorhersage")
    st.write(f"**Label:** `{result['label']}`")
    st.write(f"**Confidence:** `{result['confidence']:.2%}`")
    st.caption("Das Modell ist konservativ auf non_edible-Risiken auszulegen und ersetzt keine menschliche Prüfung.")


if __name__ == "__main__":
    main()
