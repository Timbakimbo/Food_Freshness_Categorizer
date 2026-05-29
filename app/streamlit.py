import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.predict import predict_image as predict #TODO: Unify function names


st.set_page_config(
    page_title="FreshCheck Donation",
    page_icon="FC",
    layout="wide",
)


st.markdown(
    """
    <style>
        :root {
            --surface: #ffffff;
            --ink: #17211b;
            --muted: #66736a;
            --line: #dfe7e1;
            --fresh: #1f8a5b;
            --fresh-bg: #e8f6ef;
            --risk: #b42318;
            --risk-bg: #fff1f0;
            --review: #93620d;
            --review-bg: #fff7df;
        }

        .block-container {
            max-width: 1160px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--ink);
        }

        .app-header {
            border-bottom: 1px solid var(--line);
            padding-bottom: 1.25rem;
            margin-bottom: 1.5rem;
        }

        .eyebrow {
            color: var(--fresh);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .lead {
            color: var(--muted);
            max-width: 760px;
            font-size: 1.02rem;
            line-height: 1.65;
            margin-top: 0.35rem;
        }

        .panel {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1.15rem;
            height: 100%;
        }

        .metric-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            background: #fbfdfb;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.8rem;
            margin-bottom: 0.25rem;
        }

        .metric-value {
            color: var(--ink);
            font-size: 1.35rem;
            font-weight: 750;
        }

        .result {
            border-radius: 8px;
            padding: 1.1rem 1.2rem;
            border: 1px solid var(--line);
            margin-top: 1rem;
        }

        .result.fresh {
            background: var(--fresh-bg);
            border-color: #afdcc6;
        }

        .result.spoiled {
            background: var(--risk-bg);
            border-color: #ffc9c4;
        }

        .result-title {
            font-size: 1.2rem;
            font-weight: 800;
            color: var(--ink);
            margin-bottom: 0.3rem;
        }

        .result-copy {
            color: var(--muted);
            line-height: 1.6;
        }

        .notice {
            border-left: 4px solid var(--review);
            background: var(--review-bg);
            padding: 0.95rem 1rem;
            border-radius: 6px;
            color: #4f3b07;
            line-height: 1.55;
            margin-top: 1rem;
        }

        [data-testid="stRadio"] label,
        [data-testid="stSelectbox"] label,
        [data-testid="stTextInput"] label,
        [data-testid="stNumberInput"] label,
        [data-testid="stTextArea"] label,
        [data-testid="stFileUploader"] label {
            color: var(--ink);
            font-weight: 650;
        }

        div[data-testid="stFileUploader"] section {
            border-radius: 8px;
            border-color: var(--line);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


PRIVATE_MODE = "Ich moechte eine Spende anmelden"
ORG_MODE = "Ich arbeite fuer eine Organisation"


def get_context(mode: str) -> dict[str, str | int]:
    st.subheader("Kontext")

    if mode == PRIVATE_MODE:
        food_type = st.text_input("Lebensmittel", placeholder="z. B. Aepfel, Bananen, Tomaten")
        amount = st.text_input("Menge", placeholder="z. B. 2 kg oder 1 Kiste")
        pickup_area = st.text_input("Abholort / PLZ", placeholder="z. B. 50667 Koeln")
        note = st.text_area("Hinweis", placeholder="z. B. heute gekauft, kleine Druckstellen")

        return {
            "food_type": food_type,
            "amount": amount,
            "location": pickup_area,
            "note": note,
        }

    food_type = st.text_input("Warengruppe", placeholder="z. B. Obst, Gemuese, Mischkiste")
    batch_id = st.text_input("Chargen- oder Liefer-ID", placeholder="z. B. SP-2026-001")
    quantity = st.number_input("Anzahl Gebinde", min_value=1, value=1, step=1)
    location = st.selectbox(
        "Prozessschritt",
        ["Wareneingang", "Vorsortierung", "Ausgabeplanung", "Dokumentation"],
    )

    return {
        "food_type": food_type,
        "batch_id": batch_id,
        "quantity": quantity,
        "location": location,
    }


def get_message(mode: str, label: str, confidence: float) -> tuple[str, str, str]:
    certainty = f"{confidence:.0%}"

    if mode == PRIVATE_MODE:
        if label == "edible":
            return (
                "Spende voraussichtlich geeignet",
                f"Das Bild wirkt visuell unauffaellig. Die automatische Ersteinschaetzung liegt bei {certainty}.",
                "Naechster Schritt: Spendenanfrage absenden und Lebensmittel bis zur Uebergabe kuehl, sauber und getrennt lagern.",
            )

        return (
            "Spende bitte vorab pruefen",
            f"Das Bild zeigt moegliche Verderbnismerkmale. Die automatische Ersteinschaetzung liegt bei {certainty}.",
            "Naechster Schritt: Nur anbieten, wenn Geruch, Verpackung, Hygiene und Zustand zusaetzlich menschlich geprueft wurden.",
        )

    if label == "edible":
        return (
            "Prioritaet: normale Weiterverarbeitung",
            f"Die Ware wirkt visuell verwendbar. Die automatische Ersteinschaetzung liegt bei {certainty}.",
            "Operative Empfehlung: In die regulaere Vorsortierung aufnehmen und wie gewohnt dokumentieren.",
        )

    return (
        "Prioritaet: manuelle Kontrolle",
        f"Die Ware zeigt visuelle Risikosignale. Die automatische Ersteinschaetzung liegt bei {certainty}.",
        "Operative Empfehlung: Separat markieren, zweite Sichtpruefung durchfuehren und Entscheidung dokumentieren.",
    )


def render_summary(context: dict[str, str | int], mode: str) -> None:
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    first_label = "Rolle"
    first_value = "Privatspende" if mode == PRIVATE_MODE else "Organisation"

    cols = st.columns(3)
    with cols[0]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{first_label}</div>
                <div class="metric-value">{first_value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Lebensmittel</div>
                <div class="metric-value">{context.get("food_type") or "Nicht angegeben"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Zeitpunkt</div>
                <div class="metric-value">{now}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


st.markdown(
    """
    <div class="app-header">
        <div class="eyebrow">FreshCheck Donation</div>
        <h1>Visuelle Frischeeinschaetzung fuer Lebensmittelspenden</h1>
        <div class="lead">
            Ein kamerabasierter ML-Prototyp fuer Privatpersonen und Organisationen.
            Die Bewertung unterstuetzt Vorsortierung, Spendenkommunikation und Dokumentation,
            ersetzt aber keine menschliche Kontrolle.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

mode = st.radio(
    "Nutzung auswaehlen",
    [PRIVATE_MODE, ORG_MODE],
    horizontal=True,
)

left_col, right_col = st.columns([0.92, 1.08], gap="large")

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    context = get_context(mode)
    uploaded_file = st.file_uploader(
        "Bild hochladen",
        type=["jpg", "jpeg", "png"],
    )
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Analyse")

    if uploaded_file is None:
        st.write("Noch kein Bild hochgeladen.")
        st.markdown(
            """
            <div class="notice">
                Die spaetere Ausgabe unterscheidet zwischen Spendenanmeldung und
                Organisationsprozess. So bleibt die Aussage fachlich vorsichtig
                und trotzdem praktisch nutzbar.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Hochgeladenes Bild", use_container_width=True)

        try:
            label, confidence, _ = predict(image.convert("RGB"))
        except FileNotFoundError as error:
            st.error(str(error))
            st.stop()

        render_summary(context, mode)

        title, body, action = get_message(mode, label, confidence)
        result_class = "fresh" if label == "edible" else "spoiled"

        st.markdown(
            f"""
            <div class="result {result_class}">
                <div class="result-title">{title}</div>
                <div class="result-copy">{body}</div>
                <div class="result-copy" style="margin-top: 0.65rem;">{action}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Dokumentationsnotiz"):
            if mode == PRIVATE_MODE:
                st.write(
                    {
                        "modus": "privatspende",
                        "lebensmittel": context.get("food_type"),
                        "menge": context.get("amount"),
                        "abholort": context.get("location"),
                        "modellklasse": label,
                        "sicherheit": round(confidence, 4),
                    }
                )
            else:
                st.write(
                    {
                        "modus": "organisation",
                        "warengruppe": context.get("food_type"),
                        "liefer_id": context.get("batch_id"),
                        "gebinde": context.get("quantity"),
                        "prozessschritt": context.get("location"),
                        "modellklasse": label,
                        "sicherheit": round(confidence, 4),
                    }
                )

        st.markdown(
            """
            <div class="notice">
                Diese Einschaetzung basiert nur auf sichtbaren Bildmerkmalen.
                Geruch, Temperaturverlauf, Keimbelastung und innere Faeulnis
                muessen separat geprueft werden.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)