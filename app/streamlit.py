"""
Freshify - Visuelle Frischeanalyse fuer den Wareneingang
Version: 0.2.0 | Prototyp
"""

from __future__ import annotations

import io
import json
import sys
import time
import uuid
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image, ImageDraw, ImageFont


APP_VERSION = "0.2.0"
ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

SUPPORTED_ITEMS = [
    ("🍌", "Bananen"),
    ("🍊", "Orangen"),
    ("🥒", "Gurken"),
    ("🍓", "Erdbeeren"),
    ("🫑", "Paprika"),
    ("🍋", "Zitronen"),
]
ORG_STEPS = ["Wareneingang", "Vorsortierung", "Ausgabeplanung", "Dokumentation"]
FOOD_CATEGORIES = [
    "Obst",
    "Gemüse",
    "Mischkiste",
    "Backwaren",
    "Milchprodukte",
    "Tiefkühlware",
    "Konserven",
    "Sonstiges",
]


st.set_page_config(
    page_title=f"Freshify · v{APP_VERSION}",
    page_icon="🥦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #0b1710;
    --muted: #53645a;
    --subtle: #829188;
    --canvas: #f5f8f6;
    --surface: #ffffff;
    --surface-soft: #f0f5f2;
    --border: #dce7e0;
    --green: #00a962;
    --green-dark: #007744;
    --green-soft: #e6f7ef;
    --red: #c9362b;
    --red-soft: #fcecea;
    --amber: #9b5a13;
    --amber-soft: #fff6e8;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --shadow-sm: 0 1px 2px rgba(8, 24, 15, .04), 0 5px 18px rgba(8, 24, 15, .05);
    --shadow-lg: 0 20px 55px rgba(8, 24, 15, .10);
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: "Inter", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
}
body { background: var(--canvas); }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stAppViewContainer"] { background: var(--canvas); }
.block-container {
    max-width: 1320px !important;
    padding: 0 2.4rem 5rem !important;
}

.f-topline {
    height: 4px;
    margin: 0 -2.4rem;
    background: linear-gradient(90deg, #00a962, #57d994 55%, #c6f2dc);
}
.f-nav {
    min-height: 72px;
    margin: 0 -2.4rem;
    padding: 0 2.4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    background: rgba(11, 23, 16, .97);
    border-bottom: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 8px 24px rgba(0,0,0,.08);
}
.f-brand {
    display: flex;
    align-items: center;
    gap: .7rem;
    color: white;
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -.045em;
}
.f-brand-mark {
    width: 39px;
    height: 39px;
    display: grid;
    place-items: center;
    border-radius: 11px;
    background: linear-gradient(145deg, #19c879, #008c51);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.3), 0 8px 18px rgba(0,169,98,.25);
    font-size: 1.25rem;
}
.f-brand-accent { color: #43d990; }
.f-version {
    color: #7de1ad;
    background: rgba(0,169,98,.12);
    border: 1px solid rgba(67,217,144,.25);
    border-radius: 999px;
    padding: .2rem .48rem;
    font-size: .63rem;
    letter-spacing: .04em;
}
.f-nav-meta {
    color: #91a79a;
    font-size: .73rem;
    font-weight: 600;
    letter-spacing: .04em;
    text-transform: uppercase;
}

.f-proto {
    margin: 1rem 0 0;
    display: flex;
    align-items: center;
    gap: .5rem;
    flex-wrap: wrap;
}
.f-proto-label {
    color: var(--muted);
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .05em;
    text-transform: uppercase;
}
.f-chip {
    display: inline-flex;
    align-items: center;
    gap: .25rem;
    padding: .25rem .58rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: rgba(255,255,255,.7);
    color: var(--muted);
    font-size: .7rem;
    font-weight: 600;
}

.f-hero {
    padding: 2.7rem 0 2rem;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 2rem;
    align-items: end;
}
.f-eyebrow {
    margin-bottom: .55rem;
    color: var(--green-dark);
    font-size: .7rem;
    font-weight: 800;
    letter-spacing: .11em;
    text-transform: uppercase;
}
.f-title {
    margin: 0;
    max-width: 730px;
    color: var(--ink);
    font-size: clamp(2rem, 4vw, 3.25rem);
    line-height: 1.02;
    letter-spacing: -.055em;
}
.f-subtitle {
    max-width: 690px;
    margin: .9rem 0 0;
    color: var(--muted);
    font-size: .96rem;
    line-height: 1.72;
}
.f-status {
    min-width: 210px;
    padding: .8rem .95rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    background: rgba(255,255,255,.78);
    box-shadow: var(--shadow-sm);
}
.f-status-label {
    color: var(--subtle);
    font-size: .63rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.f-status-value {
    margin-top: .25rem;
    color: var(--ink);
    font-size: .82rem;
    font-weight: 700;
}
.f-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    margin-right: .4rem;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 0 4px rgba(0,169,98,.11);
}

.f-panel {
    height: 100%;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface);
    box-shadow: var(--shadow-sm);
}
.f-panel-head {
    min-height: 62px;
    margin: -1rem -1rem .15rem;
    padding: 1rem 1.25rem;
    display: flex;
    align-items: center;
    gap: .72rem;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(180deg, #fbfdfc, #f3f7f5);
}
.f-panel-step {
    width: 28px;
    height: 28px;
    flex: 0 0 28px;
    display: grid;
    place-items: center;
    border-radius: 9px;
    background: var(--ink);
    color: white;
    font-size: .7rem;
    font-weight: 800;
    box-shadow: 0 4px 10px rgba(11,23,16,.13);
}
.f-panel-title {
    color: var(--ink);
    font-size: .75rem;
    font-weight: 800;
    letter-spacing: .075em;
    line-height: 1.2;
    text-transform: uppercase;
}
.f-panel-body { padding: 1.25rem; }

[data-testid="stVerticalBlockBorderWrapper"] {
    height: 100%;
    overflow: hidden;
    border-color: var(--border) !important;
    border-radius: var(--radius-lg) !important;
    background: var(--surface);
    box-shadow: var(--shadow-sm);
}

.f-empty {
    min-height: 345px;
    display: grid;
    place-items: center;
    padding: 2rem;
    border: 1px dashed #c9d8cf;
    border-radius: var(--radius-md);
    background:
        radial-gradient(circle at 50% 20%, rgba(0,169,98,.07), transparent 36%),
        var(--surface-soft);
    text-align: center;
}
.f-empty-icon {
    width: 58px;
    height: 58px;
    margin: 0 auto .9rem;
    display: grid;
    place-items: center;
    border-radius: 16px;
    background: white;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    font-size: 1.55rem;
}
.f-empty-title { color: var(--ink); font-size: .96rem; font-weight: 750; }
.f-empty-copy { margin-top: .4rem; color: var(--muted); font-size: .8rem; line-height: 1.65; }

.f-result {
    padding: 1rem;
    display: flex;
    gap: .8rem;
    border-radius: var(--radius-md);
}
.f-result.fresh { background: var(--green-soft); border: 1px solid #acd9c3; }
.f-result.risk { background: var(--red-soft); border: 1px solid #edb6b0; }
.f-result-icon {
    width: 32px;
    height: 32px;
    flex: 0 0 32px;
    display: grid;
    place-items: center;
    border-radius: 9px;
    background: rgba(255,255,255,.74);
}
.f-result-eye {
    color: var(--subtle);
    font-size: .64rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.f-result-title { margin-top: .18rem; color: var(--ink); font-size: .96rem; font-weight: 750; }
.f-result-copy { margin-top: .25rem; color: var(--muted); font-size: .8rem; line-height: 1.55; }

.f-metrics {
    margin-top: .75rem;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .6rem;
}
.f-metric {
    min-width: 0;
    padding: .72rem .8rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: var(--surface-soft);
}
.f-metric-label {
    color: var(--subtle);
    font-size: .61rem;
    font-weight: 700;
    letter-spacing: .07em;
    text-transform: uppercase;
}
.f-metric-value {
    margin-top: .22rem;
    overflow: hidden;
    color: var(--ink);
    font-size: .92rem;
    font-weight: 750;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.f-section-label {
    margin: 1.25rem 0 .75rem;
    padding-bottom: .5rem;
    border-bottom: 1px solid var(--border);
    color: var(--subtle);
    font-size: .65rem;
    font-weight: 800;
    letter-spacing: .09em;
    text-transform: uppercase;
}
.f-notice {
    padding: .85rem .95rem;
    border: 1px solid #ecd1a6;
    border-radius: var(--radius-sm);
    background: var(--amber-soft);
    color: #704214;
    font-size: .78rem;
    line-height: 1.55;
}
.f-demo {
    margin: 0 0 .8rem;
    padding: .7rem .85rem;
    border-radius: var(--radius-sm);
    background: #eef2ff;
    border: 1px solid #d7defc;
    color: #40518c;
    font-size: .76rem;
    line-height: 1.5;
}

.f-about { max-width: 820px; margin: 0 auto; }
.f-card {
    margin-bottom: 1rem;
    padding: 1.45rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--surface);
    box-shadow: var(--shadow-sm);
}
.f-card h3 { margin: 0 0 .7rem; color: var(--ink); font-size: 1rem; }
.f-card p { margin: 0; color: var(--muted); font-size: .86rem; line-height: 1.72; }
.f-flow-row {
    padding: .85rem 0;
    display: grid;
    grid-template-columns: 30px 1fr;
    gap: .8rem;
    border-bottom: 1px solid var(--border);
}
.f-flow-row:last-child { border-bottom: 0; }
.f-flow-num {
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border-radius: 9px;
    background: var(--ink);
    color: white;
    font-size: .7rem;
    font-weight: 800;
}
.f-flow-title { color: var(--ink); font-size: .86rem; font-weight: 700; }
.f-flow-copy { margin-top: .18rem; color: var(--muted); font-size: .8rem; line-height: 1.55; }

[data-testid="stHorizontalBlock"] { align-items: stretch; }
[data-testid="column"] { min-width: 0; }
[data-baseweb="tab-list"] {
    gap: .2rem !important;
    margin-bottom: .9rem;
    padding: .22rem !important;
    border-radius: 10px;
    background: var(--surface-soft) !important;
}
[data-baseweb="tab"] {
    min-height: 36px !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-size: .8rem !important;
    font-weight: 650 !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: var(--ink) !important;
    background: white !important;
    box-shadow: 0 1px 4px rgba(8,24,15,.08) !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

[data-testid="stFileUploader"] section {
    border-color: var(--border) !important;
    border-radius: var(--radius-md) !important;
    background: var(--surface-soft) !important;
}
[data-testid="stFileUploader"] section:hover { border-color: var(--green) !important; }
[data-testid="stImage"] img { border-radius: var(--radius-md); }
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label {
    color: var(--ink) !important;
    font-size: .75rem !important;
    font-weight: 650 !important;
}
input, textarea, [data-baseweb="select"] > div {
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-size: .84rem !important;
}
input:focus, textarea:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px rgba(0,169,98,.11) !important;
}
.stButton > button, [data-testid="stDownloadButton"] > button {
    width: 100%;
    min-height: 40px;
    border-radius: var(--radius-sm) !important;
    font-family: "Inter", sans-serif !important;
    font-size: .8rem !important;
    font-weight: 700 !important;
    transition: transform .15s ease, box-shadow .15s ease, background .15s ease !important;
}
.stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 7px 18px rgba(8,24,15,.10);
}
.stButton > button[kind="primary"] {
    border-color: var(--ink) !important;
    background: var(--ink) !important;
    color: white !important;
}
[data-testid="stDownloadButton"] > button {
    border-color: var(--green) !important;
    background: var(--green) !important;
    color: white !important;
}
[data-testid="stExpander"] {
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
}

@media (max-width: 800px) {
    .block-container { padding: 0 1rem 3rem !important; }
    .f-topline, .f-nav { margin-left: -1rem; margin-right: -1rem; }
    .f-nav { padding: 0 1rem; }
    .f-nav-meta { display: none; }
    .f-hero { grid-template-columns: 1fr; padding-top: 2rem; }
    .f-status { min-width: 0; }
    .f-metrics { grid-template-columns: 1fr; }
}
</style>
""",
    unsafe_allow_html=True,
)


def init_state() -> None:
    defaults = {
        "page": "analyse",
        "analysis_key": None,
        "last_label": None,
        "last_confidence": None,
        "last_original": None,
        "last_annotated": None,
        "last_detections": [],
        "last_engine": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


init_state()


def image_bytes(image: Image.Image, image_format: str = "PNG") -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def source_bytes(source: Any) -> bytes:
    if hasattr(source, "getvalue"):
        return source.getvalue()
    return source.read()


def normalize_prediction(result: Any) -> tuple[str, float]:
    if isinstance(result, dict):
        label = result.get("label") or result.get("class") or "edible"
        confidence = result.get("confidence") or result.get("score") or 0.0
    elif isinstance(result, (tuple, list)) and len(result) >= 2:
        label, confidence = result[0], result[1]
    else:
        raise ValueError("Nicht unterstütztes Ergebnisformat der ML-Schnittstelle.")

    normalized = str(label).strip().lower()
    edible_aliases = {"edible", "fresh", "frisch", "good", "ok", "verwertbar"}
    final_label = "edible" if normalized in edible_aliases else "spoiled"
    return final_label, max(0.0, min(1.0, float(confidence)))


def predict_freshness(image: Image.Image) -> tuple[str, float, str]:
    """Use the project model when installed; otherwise return an explicit demo result."""
    try:
        from src.predict import predict_image

        label, confidence = normalize_prediction(predict_image(image))
        return label, confidence, "src.predict.predict_image"
    except Exception:
        # Deterministic visual heuristic for UI demonstrations only.
        sample = image.copy()
        sample.thumbnail((160, 160))
        pixels = list(sample.convert("RGB").getdata())
        if not pixels:
            return "edible", 0.5, "Demo-Heuristik"
        green = sum(g for _, g, _ in pixels) / len(pixels)
        red = sum(r for r, _, _ in pixels) / len(pixels)
        score = max(0.58, min(0.91, 0.71 + (green - red) / 700))
        return "edible", score, "Demo-Heuristik"


def normalize_detection(det: Any) -> dict[str, Any] | None:
    if not isinstance(det, dict):
        return None
    box = det.get("box") or det.get("bbox")
    if not isinstance(box, (list, tuple)) or len(box) != 4:
        return None
    try:
        coords = [int(float(value)) for value in box]
        return {
            "box": coords,
            "label": str(det.get("label") or det.get("class_name") or "Produkt"),
            "score": max(0.0, min(1.0, float(det.get("score") or det.get("confidence") or 0.0))),
        }
    except (TypeError, ValueError):
        return None


def detect_objects(image: Image.Image) -> tuple[list[dict[str, Any]], str]:
    """Use src.yolo.main.detect_objects when available."""
    try:
        from src.yolo.main import detect_objects as project_detector

        raw = project_detector(image)
        detections = [normalized for item in raw if (normalized := normalize_detection(item))]
        return detections, "src.yolo.main.detect_objects"
    except Exception:
        return [], "Simulierte Position"


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_boxes(
    image: Image.Image,
    detections: list[dict[str, Any]],
    freshness_label: str,
    confidence: float,
) -> Image.Image:
    canvas = image.copy()
    draw = ImageDraw.Draw(canvas)
    width, height = canvas.size
    line_width = max(3, int(min(width, height) * 0.006))
    color = "#00A962" if freshness_label == "edible" else "#C9362B"
    verdict = "Verwertbar" if freshness_label == "edible" else "Prüfen"
    font = load_font(max(13, int(min(width, height) * 0.028)))

    boxes = detections or [{
        "box": [
            int(width * 0.13),
            int(height * 0.14),
            int(width * 0.87),
            int(height * 0.86),
        ],
        "label": "Produkt",
        "score": confidence,
    }]

    for detection in boxes:
        x1, y1, x2, y2 = detection["box"]
        x1, x2 = sorted((max(0, x1), min(width - 1, x2)))
        y1, y2 = sorted((max(0, y1), min(height - 1, y2)))
        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=max(5, line_width * 2),
            outline=color,
            width=line_width,
        )

        label_text = f"{detection['label']}  {detection['score']:.0%} · {verdict}"
        text_box = draw.textbbox((0, 0), label_text, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
        pad_x, pad_y = line_width * 3, line_width * 2
        pill_top = max(0, y1 - text_height - pad_y * 2 - line_width)
        pill_right = min(width, x1 + text_width + pad_x * 2)
        draw.rounded_rectangle(
            [x1, pill_top, pill_right, y1],
            radius=max(4, line_width * 2),
            fill=color,
        )
        draw.text((x1 + pad_x, pill_top + pad_y), label_text, fill="white", font=font)

    return canvas


def result_copy(label: str, confidence: float) -> tuple[str, str, str, str]:
    percentage = f"{confidence:.0%}"
    if label == "edible":
        return (
            "fresh",
            "Ware visuell unauffällig",
            f"Keine eindeutigen Verderbnismerkmale erkannt. ML-Konfidenz: {percentage}.",
            "Empfehlung: regulär vorsortieren und sensorisch gegenprüfen.",
        )
    return (
        "risk",
        "Manuelle Kontrolle empfohlen",
        f"Mögliche Verderbnismerkmale erkannt. ML-Konfidenz: {percentage}.",
        "Empfehlung: Charge separieren und Sicht- sowie Geruchskontrolle durchführen.",
    )


def generate_pdf(
    report_id: str,
    timestamp: str,
    context: dict[str, Any],
    label: str,
    confidence: float,
    annotated_image: Image.Image,
) -> bytes | None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            Image as ReportImage,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError:
        return None

    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
    )
    ink = colors.HexColor("#0B1710")
    green = colors.HexColor("#00A962")
    red = colors.HexColor("#C9362B")
    muted = colors.HexColor("#53645A")
    soft = colors.HexColor("#F0F5F2")
    border = colors.HexColor("#DCE7E0")
    verdict_color = green if label == "edible" else red

    styles = {
        "brand": ParagraphStyle("brand", fontName="Helvetica-Bold", fontSize=16, textColor=green),
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Bold", fontSize=18, textColor=ink, spaceAfter=4
        ),
        "meta": ParagraphStyle("meta", fontName="Helvetica", fontSize=8, textColor=muted),
        "label": ParagraphStyle(
            "label",
            fontName="Helvetica-Bold",
            fontSize=7,
            textColor=muted,
            spaceBefore=12,
            spaceAfter=5,
        ),
        "verdict": ParagraphStyle(
            "verdict", fontName="Helvetica-Bold", fontSize=13, textColor=verdict_color
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=8.5, leading=13, textColor=muted
        ),
    }

    story = [
        Paragraph("freshify", styles["brand"]),
        Paragraph("Qualitätsprotokoll Wareneingang", styles["title"]),
        Paragraph(
            f"Protokoll-ID: <b>{escape(report_id)}</b> · {escape(timestamp)} · v{APP_VERSION}",
            styles["meta"],
        ),
        Spacer(1, 8),
        Paragraph("BEFUND", styles["label"]),
        Paragraph(
            "Visuell verwertbar" if label == "edible" else "Manuelle Kontrolle erforderlich",
            styles["verdict"],
        ),
        Paragraph(f"ML-Konfidenz: <b>{confidence:.0%}</b>", styles["body"]),
        Paragraph("ANALYSE-OVERLAY", styles["label"]),
    ]

    image_buffer = io.BytesIO(image_bytes(annotated_image))
    story.extend(
        [
            ReportImage(image_buffer, width=130 * mm, height=97.5 * mm, kind="proportional"),
            Paragraph("CHARGENDATEN", styles["label"]),
        ]
    )

    rows = [
        ["Feld", "Wert"],
        ["Warengruppe", context.get("food_type", "–")],
        ["Chargen-ID", context.get("batch_id") or "–"],
        ["Gebinde", str(context.get("quantity", 1))],
        ["Prozessschritt", context.get("process_step", "–")],
        ["Notiz", context.get("note") or "–"],
        ["ML-Klasse", label],
        ["ML-Konfidenz", f"{confidence:.4f}"],
        ["Zeitpunkt", timestamp],
        ["App-Version", APP_VERSION],
    ]
    table = Table(rows, colWidths=[52 * mm, 114 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), soft),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (-1, -1), muted),
                ("TEXTCOLOR", (0, 1), (0, -1), ink),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.4, border),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, soft]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend(
        [
            table,
            Spacer(1, 14),
            Paragraph(
                "Automatisierte visuelle ML-Analyse. Geruch, Kerntemperatur und "
                "mikrobiologische Belastung sind separat zu prüfen. Freshify unterstützt "
                "die Qualitätskontrolle, ersetzt sie aber nicht.",
                styles["body"],
            ),
        ]
    )
    document.build(story)
    return buffer.getvalue()


chips = "".join(
    f'<span class="f-chip">{emoji} {escape(name)}</span>' for emoji, name in SUPPORTED_ITEMS
)
st.markdown('<div class="f-topline"></div>', unsafe_allow_html=True)
st.markdown(
    f"""
<div class="f-nav">
    <div class="f-brand">
        <span class="f-brand-mark">🥦</span>
        <span>fresh<span class="f-brand-accent">ify</span></span>
        <span class="f-version">v{APP_VERSION}</span>
    </div>
    <div class="f-nav-meta">Visual Quality Intelligence</div>
</div>
<div class="f-proto">
    <span class="f-proto-label">Prototyp · optimiert für</span>
    {chips}
</div>
""",
    unsafe_allow_html=True,
)

nav_a, nav_b, nav_space = st.columns([1, 1.65, 7.35])
with nav_a:
    if st.button(
        "Analyse",
        type="primary" if st.session_state.page == "analyse" else "secondary",
        use_container_width=True,
    ):
        st.session_state.page = "analyse"
        st.rerun()
with nav_b:
    if st.button(
        "So funktioniert es",
        type="primary" if st.session_state.page == "about" else "secondary",
        use_container_width=True,
    ):
        st.session_state.page = "about"
        st.rerun()


if st.session_state.page == "analyse":
    st.markdown(
        """
<div class="f-hero">
    <div>
        <div class="f-eyebrow">B2B · Wareneingang und Qualitätssicherung</div>
        <h1 class="f-title">Frische sichtbar machen.</h1>
        <p class="f-subtitle">
            Ware fotografieren, sichtbare Auffälligkeiten per ML einordnen und den
            Vorgang direkt dokumentieren. Schnell im Ablauf, nachvollziehbar im Ergebnis.
        </p>
    </div>
    <div class="f-status">
        <div class="f-status-label">Systemstatus</div>
        <div class="f-status-value"><span class="f-dot"></span>Bereit für Analyse</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    left_column, right_column = st.columns([1.04, 0.96], gap="large")

    with left_column.container(border=True):
        st.markdown(
            """
<div class="f-panel-head">
    <span class="f-panel-step">1</span>
    <span class="f-panel-title">Bilderfassung</span>
</div>
""",
            unsafe_allow_html=True,
        )

        upload_tab, camera_tab = st.tabs(["Datei oder Galerie", "Kamera"])
        uploaded_file = None
        camera_image = None
        with upload_tab:
            uploaded_file = st.file_uploader(
                "Foto auswählen",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
                help="Auf Mobilgeräten kann hier direkt die Fotogalerie geöffnet werden.",
            )
        with camera_tab:
            camera_image = st.camera_input("Foto aufnehmen", label_visibility="collapsed")

        image_source = camera_image if camera_image is not None else uploaded_file
        if image_source is None:
            st.markdown(
                """
<div class="f-empty">
    <div>
        <div class="f-empty-icon">＋</div>
        <div class="f-empty-title">Foto hinzufügen</div>
        <div class="f-empty-copy">
            Bild aus der Galerie oder vom Rechner auswählen.<br>
            Eine helle Draufsicht liefert die stabilsten Ergebnisse.
        </div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            raw_bytes = source_bytes(image_source)
            analysis_key = f"{getattr(image_source, 'name', 'camera')}:{len(raw_bytes)}:{hash(raw_bytes)}"
            if st.session_state.analysis_key != analysis_key:
                with st.spinner("ML-Analyse läuft …"):
                    image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                    label, confidence, freshness_engine = predict_freshness(image)
                    detections, detection_engine = detect_objects(image)
                    annotated = draw_boxes(image, detections, label, confidence)
                    time.sleep(0.25)
                    st.session_state.update(
                        {
                            "analysis_key": analysis_key,
                            "last_label": label,
                            "last_confidence": confidence,
                            "last_original": image,
                            "last_annotated": annotated,
                            "last_detections": detections,
                            "last_engine": {
                                "freshness": freshness_engine,
                                "detection": detection_engine,
                            },
                        }
                    )

            st.image(
                st.session_state.last_annotated,
                use_container_width=True,
                caption="ML-Overlay · Grün: visuell unauffällig · Rot: manuell prüfen",
            )
            download_image_a, download_image_b = st.columns(2)
            with download_image_a:
                st.download_button(
                    "Originalfoto herunterladen",
                    data=image_bytes(st.session_state.last_original),
                    file_name="freshify_original.png",
                    mime="image/png",
                    use_container_width=True,
                )
            with download_image_b:
                st.download_button(
                    "Overlay herunterladen",
                    data=image_bytes(st.session_state.last_annotated),
                    file_name="freshify_ml_overlay.png",
                    mime="image/png",
                    use_container_width=True,
                )

    with right_column.container(border=True):
        st.markdown(
            """
<div class="f-panel-head">
    <span class="f-panel-step">2</span>
    <span class="f-panel-title">Befund und Protokoll</span>
</div>
""",
            unsafe_allow_html=True,
        )

        if image_source is None or st.session_state.last_label is None:
            st.markdown(
                """
<div class="f-notice">
    Nach dem Foto erscheinen hier Befund, Chargendaten und Exporte.
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            label = st.session_state.last_label
            confidence = st.session_state.last_confidence
            annotated = st.session_state.last_annotated
            detections = st.session_state.last_detections
            engines = st.session_state.last_engine

            if engines["freshness"] == "Demo-Heuristik":
                st.markdown(
                    """
<div class="f-demo">
    <strong>Demo-Modus:</strong> Kein trainiertes Frischemodell gefunden.
    Der gezeigte Befund demonstriert den Ablauf und ist keine Qualitätsfreigabe.
</div>
""",
                    unsafe_allow_html=True,
                )

            css_class, title, body, action = result_copy(label, confidence)
            icon = "✓" if css_class == "fresh" else "!"
            eye = "Befund · visuell unauffällig" if css_class == "fresh" else "Befund · prüfen"
            st.markdown(
                f"""
<div class="f-result {css_class}">
    <div class="f-result-icon">{icon}</div>
    <div>
        <div class="f-result-eye">{eye}</div>
        <div class="f-result-title">{escape(title)}</div>
        <div class="f-result-copy">{escape(body)}<br>{escape(action)}</div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            timestamp = datetime.now().strftime("%d.%m.%Y, %H:%M")
            object_count = len(detections)
            object_display = str(object_count) if object_count else "1 · Demo"
            st.markdown(
                f"""
<div class="f-metrics">
    <div class="f-metric">
        <div class="f-metric-label">ML-Konfidenz</div>
        <div class="f-metric-value">{confidence:.0%}</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Objekte</div>
        <div class="f-metric-value">{object_display}</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Zeitpunkt</div>
        <div class="f-metric-value">{timestamp}</div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            st.markdown('<div class="f-section-label">Chargendaten</div>', unsafe_allow_html=True)
            autofill_column, autofill_space = st.columns([1.35, 1.65])
            with autofill_column:
                if st.button("Daten vorschlagen", use_container_width=True):
                    st.session_state.update(
                        {
                            "af_food": "Obst",
                            "af_batch": (
                                f"FC-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
                            ),
                            "af_qty": 1,
                            "af_step": "Wareneingang",
                            "af_note": (
                                f"Freshify v{APP_VERSION} · ML-Befund: "
                                f"{'visuell unauffällig' if label == 'edible' else 'manuell prüfen'}."
                            ),
                        }
                    )
                    st.rerun()

            default_food = st.session_state.get("af_food", "Obst")
            food_type = st.selectbox(
                "Warengruppe",
                FOOD_CATEGORIES,
                index=FOOD_CATEGORIES.index(default_food),
            )
            batch_column, quantity_column = st.columns(2)
            with batch_column:
                batch_id = st.text_input(
                    "Chargen-ID",
                    value=st.session_state.get("af_batch", ""),
                    placeholder="FC-20260610-A4B2F1",
                )
            with quantity_column:
                quantity = st.number_input(
                    "Gebinde",
                    min_value=1,
                    value=int(st.session_state.get("af_qty", 1)),
                    step=1,
                )
            default_step = st.session_state.get("af_step", "Wareneingang")
            process_step = st.selectbox(
                "Prozessschritt",
                ORG_STEPS,
                index=ORG_STEPS.index(default_step),
            )
            note = st.text_area(
                "Interne Notiz",
                value=st.session_state.get("af_note", ""),
                placeholder="Optionaler Kontext für das Protokoll",
                height=76,
            )

            context = {
                "food_type": food_type,
                "batch_id": batch_id,
                "quantity": quantity,
                "process_step": process_step,
                "note": note,
            }
            report_id = batch_id or f"FC-{datetime.now():%Y%m%d%H%M%S}"
            report_data = {
                "protokoll_id": report_id,
                "zeitpunkt": timestamp,
                "warengruppe": food_type,
                "chargen_id": batch_id or None,
                "gebinde": quantity,
                "prozessschritt": process_step,
                "ml_klasse": label,
                "ml_konfidenz": round(confidence, 4),
                "objekte": detections,
                "notiz": note or None,
                "schnittstellen": engines,
                "app_version": APP_VERSION,
                "prototyp": True,
            }

            st.markdown('<div class="f-section-label">Export</div>', unsafe_allow_html=True)
            export_pdf, export_json = st.columns(2)
            pdf_bytes = generate_pdf(
                report_id,
                timestamp,
                context,
                label,
                confidence,
                annotated,
            )
            with export_pdf:
                if pdf_bytes:
                    st.download_button(
                        "PDF herunterladen",
                        data=pdf_bytes,
                        file_name=f"freshify_{report_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.button("PDF nicht verfügbar", disabled=True, use_container_width=True)
            with export_json:
                st.download_button(
                    "JSON herunterladen",
                    data=json.dumps(report_data, ensure_ascii=False, indent=2).encode("utf-8"),
                    file_name=f"freshify_{report_id}.json",
                    mime="application/json",
                    use_container_width=True,
                )

            with st.expander("Technische Rohdaten"):
                st.json(report_data)

            st.markdown(
                """
<div class="f-notice">
    <strong>Ein Werkzeug, kein Orakel.</strong> Freshify bewertet sichtbare Merkmale.
    Geruch, Kerntemperatur und mikrobiologische Risiken bleiben Teil der Fachprüfung.
</div>
""",
                unsafe_allow_html=True,
            )

else:
    st.markdown(
        """
<div class="f-hero">
    <div>
        <div class="f-eyebrow">Produkt und Methodik</div>
        <h1 class="f-title">Klare Unterstützung. Klare Grenzen.</h1>
        <p class="f-subtitle">
            Freshify strukturiert die visuelle Erstsichtung im Wareneingang.
            Das System liefert einen Hinweis, die Freigabe bleibt eine Fachentscheidung.
        </p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="f-about">
    <div class="f-card">
        <h3>Warum Freshify?</h3>
        <p>
            Große Warenmengen, wenig Zeit und wechselnde Teams machen konsistente
            Erstsichtungen schwer. Freshify verbindet Foto, visuellen ML-Befund,
            Chargendaten und Export in einem kompakten Ablauf.
        </p>
    </div>
    <div class="f-card">
        <h3>Der Ablauf</h3>
        <div class="f-flow-row">
            <div class="f-flow-num">1</div>
            <div><div class="f-flow-title">Foto erfassen</div>
            <div class="f-flow-copy">Aus Galerie, Dateisystem oder Kamera.</div></div>
        </div>
        <div class="f-flow-row">
            <div class="f-flow-num">2</div>
            <div><div class="f-flow-title">ML-Modelle ausführen</div>
            <div class="f-flow-copy">Ein Klassifikator bewertet sichtbare Frischemerkmale; eine optionale Objekterkennung lokalisiert Produkte.</div></div>
        </div>
        <div class="f-flow-row">
            <div class="f-flow-num">3</div>
            <div><div class="f-flow-title">Befund einordnen</div>
            <div class="f-flow-copy">Konfidenz und Overlay machen das Ergebnis nachvollziehbar, nicht unfehlbar.</div></div>
        </div>
        <div class="f-flow-row">
            <div class="f-flow-num">4</div>
            <div><div class="f-flow-title">Dokumentieren</div>
            <div class="f-flow-copy">Originalfoto, Overlay, PDF und JSON stehen direkt zum Download bereit.</div></div>
        </div>
    </div>
    <div class="f-card">
        <h3>Schnittstellenstatus in v{APP_VERSION}</h3>
        <p>
            Freshify bindet ein Frischemodell über <strong>src.predict.predict_image</strong>
            und eine Objekterkennung über <strong>src.yolo.main.detect_objects</strong> an.
            Fehlen diese Module, wechselt die Oberfläche sichtbar in den Demo-Modus.
            Sie behauptet dann ausdrücklich keine echte Qualitätsanalyse.
        </p>
    </div>
    <div class="f-card">
        <h3>Was das System nicht sieht</h3>
        <p>
            Geruch, Kerntemperatur, innere Fäulnis, Kühlkettenverlauf und
            mikrobiologische Belastung liegen außerhalb einer visuellen Bildanalyse.
            Freshify v{APP_VERSION} unterstützt die Entscheidung; es trifft sie nicht allein.
        </p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
