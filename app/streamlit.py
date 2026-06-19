"""
Freshify - Visuelle Frischeanalyse fuer den Wareneingang
Version: 0.2.0 | Prototyp
"""

from __future__ import annotations

import io
import json
import sys
import time
import os
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

import PIL
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps


APP_VERSION = "0.2.0"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SUPPORTED_ITEMS = [
    ("🍌", "Bananen"),
    ("🍊", "Orangen"),
    ("🥒", "Gurken"),
    ("🍓", "Erdbeeren"),
    ("🫑", "Paprika"),
    ("🍋", "Zitronen"),
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
    --canvas: #f1f5f3;
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
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 8% 8%, rgba(0,169,98,.045), transparent 26rem),
        radial-gradient(circle at 92% 24%, rgba(65,113,89,.04), transparent 30rem),
        var(--canvas);
}
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
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: .62rem;
    flex-wrap: wrap;
}
.f-proto-label {
    color: var(--muted);
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: .05em;
    text-transform: uppercase;
}
.f-chip {
    display: inline-flex;
    align-items: center;
    gap: .25rem;
    padding: .34rem .72rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: rgba(255,255,255,.7);
    color: var(--muted);
    font-size: .77rem;
    font-weight: 600;
    box-shadow: 0 2px 7px rgba(8,24,15,.04);
}
.f-nav-controls { height: 1rem; }
.f-nav-center { max-width: 780px; margin: 0 auto; }
.st-key-sticky_navigation {
    position: relative;
    width: calc(100% + 4.8rem) !important;
    max-width: none !important;
    margin: 0 -2.4rem;
    padding: .72rem 2.4rem .78rem;
    border-bottom: 1px solid rgba(116, 171, 141, .22);
    background: rgba(11, 31, 21, .88);
    box-shadow: 0 10px 30px rgba(8, 24, 15, .12);
    backdrop-filter: blur(16px) saturate(140%);
    -webkit-backdrop-filter: blur(16px) saturate(140%);
}
div[data-testid="stLayoutWrapper"]:has(> .st-key-sticky_navigation) {
    position: sticky;
    top: 0;
    z-index: 500;
}
.st-key-sticky_navigation .f-proto-label { color: #a8bcb0; }
.st-key-sticky_navigation .f-chip {
    border-color: rgba(137, 196, 164, .18);
    background: rgba(255,255,255,.055);
    color: #dce8e1;
    box-shadow: none;
}
.st-key-sticky_navigation [data-testid="stHorizontalBlock"] {
    max-width: 780px;
    margin: .6rem auto 0;
}
.st-key-sticky_navigation .stButton > button {
    min-height: 28px !important;
    padding: 0 .8rem !important;
    border: 1px solid transparent !important;
    border-radius: 9px !important;
    background: transparent !important;
    box-shadow: none !important;
    color: #d8e5dd !important;
    font-size: .78rem !important;
    letter-spacing: .01em;
}
.st-key-sticky_navigation .stButton > button:hover {
    transform: none !important;
    color: white !important;
    background: rgba(255,255,255,.06) !important;
    border-color: rgba(255,255,255,.08) !important;
}
.st-key-sticky_navigation .stButton > button[kind="primary"] {
    color: #62e3a4 !important;
    background: rgba(0,0,0,.24) !important;
    border-color: rgba(98,227,164,.12) !important;
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
    font-weight: 800;
    line-height: 1.02;
    letter-spacing: -.055em;
}
.f-title-linkless { display: block; }
.stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a,
[data-testid="stHeaderActionElements"] { display: none !important; }
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
    height: auto;
    min-height: 100%;
    overflow: visible;
    border-color: var(--border) !important;
    border-radius: var(--radius-lg) !important;
    background: var(--surface);
    box-shadow: var(--shadow-sm);
}

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
.f-metric-note {
    margin-top: .16rem;
    color: var(--subtle);
    font-size: .57rem;
    line-height: 1.35;
}
.f-metric-wide { grid-column: span 2; }
.f-crisp-intro {
    margin: 0 0 .8rem;
    color: var(--muted);
    font-size: .86rem !important;
    line-height: 1.72 !important;
}
.st-key-crisp_dm {
    margin: 0 auto;
    padding: 1.15rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: linear-gradient(145deg, #ffffff, #f1f7f3);
    box-shadow: var(--shadow-sm);
}
.st-key-crisp_dm .f-section-label {
    color: var(--ink);
    font-size: 1rem;
    letter-spacing: 0;
    text-transform: none;
}
.st-key-crisp_dm [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .55rem;
    width: 100%;
    max-width: 920px;
    margin-left: auto;
    margin-right: auto;
}
.st-key-crisp_dm [data-testid="stColumn"] {
    width: auto !important;
    min-width: 0 !important;
}
.st-key-crisp_dm .stButton > button {
    min-height: 46px;
    padding: .42rem .58rem !important;
    border: 1px solid var(--border) !important;
    background: white !important;
    color: var(--ink) !important;
    box-shadow: none !important;
    font-size: .74rem !important;
    line-height: 1.35 !important;
    white-space: normal !important;
}
.st-key-crisp_dm .stButton > button[kind="primary"] {
    border-color: var(--green) !important;
    background: var(--ink) !important;
    color: white !important;
}
.f-crisp-detail {
    margin-top: .85rem;
    padding: 1rem 1.05rem;
    border-left: 4px solid var(--green);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    background: #eaf7f0;
}
.f-crisp-detail-kicker {
    color: var(--green-dark);
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .09em;
    text-transform: uppercase;
}
.f-crisp-detail h4 {
    margin: .25rem 0 .4rem;
    color: var(--ink);
    font-size: 1rem;
}
.f-crisp-detail p {
    margin: 0;
    color: var(--muted);
    font-size: .86rem;
    line-height: 1.72;
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
    width: 100%;
    max-width: 100%;
    overflow-wrap: anywhere;
    margin-top: 1rem;
    padding: .85rem .95rem;
    border: 1px solid #ecd1a6;
    border-radius: var(--radius-sm);
    background: var(--amber-soft);
    color: #704214;
    font-size: .78rem;
    line-height: 1.55;
}
.f-safety-notice {
    margin-top: 1.5rem;
    margin-bottom: 1.75rem;
    display: flex;
    align-items: flex-start;
    gap: .2rem;
}
.f-safety-icon {
    width: 22px;
    height: 22px;
    flex: 0 0 22px;
    display: grid;
    place-items: center;
    border-radius: 7px;
    background: #fff3dc;
    font-weight: 800;
}
.f-safety-copy { min-width: 0; }
.f-awaiting {
    min-height: 270px;
    margin-top: .9rem;
    display: grid;
    place-items: center;
    padding: 1.4rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    background:
        radial-gradient(circle at 50% 0, rgba(0,169,98,.08), transparent 52%),
        linear-gradient(145deg, #fbfdfc, #f0f5f2);
    text-align: center;
}
.st-key-capture_panel,
.st-key-finding_panel {
    height: 100%;
    min-height: 480px;
}
[data-testid="stHorizontalBlock"]:has(.st-key-capture_panel):has(.st-key-finding_panel) {
    align-items: stretch;
}
[data-testid="stColumn"]:has(.st-key-capture_panel),
[data-testid="stColumn"]:has(.st-key-finding_panel) {
    display: flex;
    flex-direction: column;
}
[data-testid="stColumn"]:has(.st-key-capture_panel) > [data-testid="stVerticalBlock"],
[data-testid="stColumn"]:has(.st-key-finding_panel) > [data-testid="stVerticalBlock"],
[data-testid="stColumn"]:has(.st-key-capture_panel) [data-testid="stLayoutWrapper"],
[data-testid="stColumn"]:has(.st-key-finding_panel) [data-testid="stLayoutWrapper"] {
    height: 100%;
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
}
.f-awaiting-icon {
    width: 42px;
    height: 42px;
    margin: 0 auto .7rem;
    display: grid;
    place-items: center;
    border: 1px solid #b8d8c7;
    border-radius: 12px;
    background: white;
    color: var(--green-dark);
    font-size: 1rem;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}
.f-awaiting-icon::before {
    content: "";
    width: 16px;
    height: 16px;
    border: 2px solid #92c7aa;
    border-radius: 5px;
    animation: f-await-pulse 1.8s ease-in-out infinite;
}
.f-awaiting-icon::after {
    content: "";
    position: absolute;
    left: 9px;
    right: 9px;
    top: 12px;
    height: 2px;
    background: var(--green);
    box-shadow: 0 0 7px rgba(0,169,98,.6);
    animation: f-await-scan 1.8s ease-in-out infinite;
}
@keyframes f-await-pulse { 0%,100% { transform:scale(.9); opacity:.65; } 50% { transform:scale(1.08); opacity:1; } }
@keyframes f-await-scan { 0%,100% { top:12px; } 50% { top:28px; } }
.f-awaiting-title { color: var(--ink); font-size: .84rem; font-weight: 750; }
.f-awaiting-copy { margin-top: .3rem; color: var(--muted); font-size: .74rem; line-height: 1.55; }
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

.f-about { width: 100%; max-width: 1180px; margin: 0 auto; }
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
.f-footer {
    width: 100%;
    max-width: 1180px;
    margin: 3rem auto 0;
    padding: 1rem 0 .3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    border-top: 1px solid var(--border);
    color: var(--subtle);
    font-size: .66rem;
    line-height: 1.5;
}
.f-footer strong { color: var(--muted); font-weight: 700; }

[data-testid="stHorizontalBlock"] { align-items: stretch; }
[data-testid="column"] { min-width: 0; }
[data-baseweb="tab-list"] {
    width: fit-content;
    max-width: 100%;
    gap: .25rem !important;
    margin: .35rem auto 1rem;
    padding: .28rem !important;
    border-radius: 10px;
    background: var(--surface-soft) !important;
    border: 1px solid var(--border);
}
[data-baseweb="tab"] {
    min-height: 36px !important;
    padding: 0 1.1rem !important;
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
    min-height: 345px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 1rem !important;
    padding: 2rem !important;
    border-color: var(--border) !important;
    border-style: dashed !important;
    border-radius: var(--radius-md) !important;
    background:
        radial-gradient(circle at 50% 32%, rgba(0,169,98,.09), transparent 29%),
        var(--surface-soft) !important;
    transition: border-color .18s ease, background .18s ease, transform .18s ease !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: var(--green) !important;
    background:
        radial-gradient(circle at 50% 32%, rgba(0,169,98,.14), transparent 31%),
        #f3faf6 !important;
}
[data-testid="stFileUploader"] section > div {
    width: 100%;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: .75rem !important;
    text-align: center !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    align-items: center !important;
    text-align: center !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] > div {
    align-items: center !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span {
    color: var(--ink) !important;
    font-size: .92rem !important;
    font-weight: 750 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: var(--muted) !important;
    font-size: .75rem !important;
}
[data-testid="stFileUploader"] section button {
    min-width: 180px !important;
    min-height: 44px !important;
    border: 0 !important;
    border-radius: 10px !important;
    background: var(--ink) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 20px rgba(11,23,16,.15) !important;
}
[data-testid="stCameraInput"] {
    min-height: 345px;
    padding: 2rem;
    display: grid;
    place-items: center;
    border: 1px dashed var(--border);
    border-radius: var(--radius-md);
    background: var(--surface-soft);
}
[data-testid="stImage"] img { border-radius: var(--radius-md); }
.f-uploaded-frame [data-testid="stImage"] {
    min-height: 345px;
    display: grid;
    place-items: center;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    background: var(--surface-soft);
}
.f-uploaded-frame [data-testid="stImage"] img {
    width: 100%;
    height: 345px;
    object-fit: contain;
}
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

/* Animated product stories */
.f-stories { margin-top: 1rem; }
.f-story {
    display: grid;
    grid-template-columns: minmax(0, 1.15fr) minmax(250px, .85fr);
    gap: 1.2rem;
    align-items: center;
    margin-bottom: 1rem;
    padding: 1.3rem;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: linear-gradient(145deg, #fff, #f1f7f3);
    box-shadow: var(--shadow-sm);
}
.f-story-copy h3 { margin: 0 0 .55rem; color: var(--ink); font-size: 1.02rem; }
.f-story-copy p { margin: 0; color: var(--muted); font-size: .84rem; line-height: 1.7; }
.f-story-kicker {
    margin-bottom: .4rem;
    color: var(--green-dark);
    font-size: .64rem;
    font-weight: 800;
    letter-spacing: .09em;
    text-transform: uppercase;
}
.f-scene {
    position: relative;
    min-height: 250px;
    overflow: hidden;
    border: 1px solid #cfe0d6;
    border-radius: 14px;
    background: linear-gradient(180deg, #dff3e8 0 62%, #c7d8ce 62% 65%, #edf2ef 65%);
}
.f-person {
    position: absolute;
    left: 13%;
    bottom: 32px;
    width: 78px;
    height: 128px;
}
.f-head {
    position: absolute;
    top: 0;
    left: 23px;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #d99b72;
    box-shadow: inset -8px 7px 0 #263b31;
}
.f-story:first-child .f-person .f-head {
    box-shadow: inset 8px 7px 0 #263b31;
}
.f-body {
    position: absolute;
    left: 13px;
    bottom: 0;
    width: 55px;
    height: 92px;
    border-radius: 22px 22px 8px 8px;
    background: #173d2a;
}
.f-arm {
    position: absolute;
    top: 52px;
    left: 48px;
    width: 65px;
    height: 13px;
    border-radius: 10px;
    background: #d99b72;
    transform: rotate(-8deg);
    transform-origin: left center;
}
.f-tablet {
    position: absolute;
    top: 78px;
    left: 31%;
    z-index: 8;
    width: 76px;
    height: 104px;
    padding: 7px;
    border: 2px solid #31483d;
    border-radius: 10px;
    background: #102219;
    transform: rotate(3deg);
    box-shadow: 0 8px 18px rgba(11,23,16,.22);
    animation: f-tablet-focus 3s ease-in-out infinite;
}
.f-tablet-screen {
    width: 100%;
    height: 100%;
    overflow: hidden;
    border-radius: 4px;
    border: 1px solid rgba(255,255,255,.48);
    position: relative;
    background:
        radial-gradient(circle at 30% 65%, #f29a27 0 9px, transparent 10px),
        radial-gradient(circle at 68% 42%, #765035 0 9px, transparent 10px),
        radial-gradient(circle at 70% 72%, #7daf49 0 9px, transparent 10px),
        #c9eedb;
}
.f-tablet-screen::before,
.f-tablet-screen::after {
    content: "";
    position: absolute;
    border: 2px solid var(--green);
    border-radius: 3px;
}
.f-tablet-screen::before { left: 7px; top: 48px; width: 23px; height: 23px; }
.f-tablet-screen::after { right: 5px; top: 22px; width: 24px; height: 24px; border-color: var(--red); }
.f-tablet-good-box {
    position: absolute;
    left: 31px;
    bottom: 16px;
    width: 24px;
    height: 24px;
    border: 2px solid var(--green);
    border-radius: 3px;
}
.f-tablet-line {
    position: absolute;
    left: 8px;
    right: 8px;
    top: 10px;
    height: 2px;
    background: #00d47a;
    box-shadow: 0 0 8px #00d47a;
    animation: f-mini-scan 2s ease-in-out infinite;
}
.f-crate {
    position: absolute;
    right: 10%;
    bottom: 35px;
    width: 145px;
    height: 78px;
    border: 7px solid #936331;
    border-top-width: 10px;
    border-radius: 5px;
    background: repeating-linear-gradient(0deg, #bc8247 0 12px, #9d6937 12px 17px);
}
.f-fruit {
    position: absolute;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #f39b24;
    box-shadow: inset -5px -4px 0 rgba(126,55,5,.16);
}
.f-fruit::after {
    content: "";
    position: absolute;
    top: -5px;
    left: 13px;
    width: 4px;
    height: 8px;
    border-radius: 4px;
    background: #2f743d;
    transform: rotate(28deg);
}
.f-f1 { left: 10px; top: -22px; }
.f-f2 { left: 48px; top: -30px; background: #e54e3f; }
.f-f3 { left: 86px; top: -19px; background: #f4b42b; }
.f-f4 { left: 32px; top: 5px; background: #84b84a; }
.f-f5 { left: 75px; top: 3px; background: #eb6845; }
.f-fruit.bad {
    background: #765035 !important;
    box-shadow:
        inset -7px -6px 0 rgba(45,25,13,.23),
        inset 5px 4px 0 rgba(177,128,82,.24);
}
.f-fruit.bad::before {
    content: "";
    position: absolute;
    inset: 5px 7px 8px 4px;
    border-radius: 50%;
    background: radial-gradient(circle, #3f2b20 0 2px, transparent 3px);
}
.f-help-pill {
    position: absolute;
    right: 8%;
    top: 22px;
    padding: .45rem .65rem;
    border: 1px solid #e5aaa5;
    border-radius: 9px;
    background: rgba(255,255,255,.92);
    color: var(--red);
    font-size: .66rem;
    font-weight: 800;
    box-shadow: var(--shadow-sm);
    animation: f-fade-result 3s ease-in-out infinite;
}

.f-belt-scene { background: linear-gradient(180deg, #e7f2ec 0 64%, #d7dfda 64%); }
.f-belt {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 47px;
    height: 44px;
    border-top: 7px solid #263c32;
    border-bottom: 7px solid #263c32;
    background: repeating-linear-gradient(90deg, #809087 0 30px, #a7b3ac 30px 36px);
}
.f-moving-crate {
    right: auto;
    left: 10%;
    bottom: 88px;
    transform: scale(.74);
    transform-origin: bottom left;
    animation: f-belt-move 6s linear infinite;
}
.f-camera-rig {
    position: absolute;
    left: 42%;
    top: 2px;
    width: 8px;
    height: 76px;
    background: #263c32;
}
.f-camera-rig::after {
    content: "";
    position: absolute;
    left: -22px;
    bottom: -19px;
    width: 52px;
    height: 31px;
    border-radius: 7px;
    background: #102219;
    box-shadow: inset 0 -5px 0 rgba(255,255,255,.08);
}
.f-lens {
    position: absolute;
    left: calc(42% - 1px);
    top: 66px;
    z-index: 2;
    width: 11px;
    height: 11px;
    border: 2px solid #62e8a7;
    border-radius: 50%;
    background: #07110c;
}
.f-scan-beam {
    position: absolute;
    left: 33%;
    top: 83px;
    width: 20%;
    height: 105px;
    clip-path: polygon(43% 0, 57% 0, 100% 100%, 0 100%);
    background: linear-gradient(180deg, rgba(0,212,122,.28), rgba(0,212,122,.03));
    animation: f-beam 1.5s ease-in-out infinite;
}
.f-alert-person {
    left: auto;
    right: 4%;
    bottom: 24px;
    transform: scale(.63);
    transform-origin: bottom right;
}
.f-phone {
    position: absolute;
    right: 22%;
    top: 24px;
    width: 118px;
    min-height: 136px;
    padding: .55rem;
    border: 5px solid #102219;
    border-radius: 12px;
    background: white;
    color: var(--ink);
    box-shadow: 0 12px 25px rgba(8,24,15,.2);
    animation: f-notification 6s ease-in-out infinite;
}
.f-phone-title { font-size: .58rem; font-weight: 800; text-transform: uppercase; color: var(--subtle); }
.f-phone-row { margin-top: .35rem; display: flex; justify-content: space-between; font-size: .62rem; font-weight: 750; }
.f-phone-row.good strong { color: var(--green-dark); }
.f-phone-row.bad strong { color: var(--red); }
.f-result-photo {
    position: relative;
    height: 57px;
    margin-top: .45rem;
    overflow: hidden;
    border-radius: 6px;
    background:
        radial-gradient(circle at 20% 36%, #f19b28 0 8px, transparent 9px),
        radial-gradient(circle at 48% 62%, #80b04b 0 8px, transparent 9px),
        radial-gradient(circle at 76% 34%, #765035 0 8px, transparent 9px),
        radial-gradient(circle at 80% 76%, #765035 0 8px, transparent 9px),
        #d7eadf;
}
.f-result-photo span {
    position: absolute;
    width: 22px;
    height: 22px;
    border: 2px solid var(--green);
    border-radius: 3px;
}
.f-rp1 { left: 8px; top: 7px; }
.f-rp2 { left: 38px; top: 27px; }
.f-rp3 { right: 9px; top: 6px; border-color: var(--red) !important; }
.f-rp4 { right: 7px; bottom: 3px; border-color: var(--red) !important; }
.f-bad-box {
    position: absolute;
    z-index: 8;
    width: 32px;
    height: 32px;
    border: 3px solid var(--red);
    border-radius: 5px;
    opacity: 0;
    pointer-events: none;
    animation: f-detect-box 6s ease-in-out infinite;
}
.f-bad-box.good { border-color: var(--green); }
.f-box-1 { left: 8px; top: -24px; }
.f-box-2 { left: 46px; top: -32px; }
.f-box-3 { left: 84px; top: -21px; }
.f-box-4 { left: 30px; top: 3px; }
.f-box-5 { left: 73px; top: 1px; }
@keyframes f-tablet-focus {
    0%, 100% { transform: rotate(3deg) translateY(0); }
    50% { transform: rotate(1deg) translateY(-4px); }
}
@keyframes f-mini-scan { 0%, 100% { top: 10px; } 50% { top: 58px; } }
@keyframes f-fade-result { 0%, 20% { opacity: 0; transform: translateY(5px); } 45%, 85% { opacity: 1; transform: none; } 100% { opacity: 0; } }
@keyframes f-belt-move { 0% { left: -20%; } 100% { left: 55%; } }
@keyframes f-beam { 0%, 100% { opacity: .4; } 50% { opacity: 1; } }
@keyframes f-notification { 0%, 48% { opacity: 0; transform: translateY(8px); } 58%, 92% { opacity: 1; transform: none; } 100% { opacity: 0; } }
@keyframes f-detect-box {
    0%, 57% { opacity: 0; transform: scale(.86); }
    63%, 80% { opacity: 1; transform: scale(1); }
    87%, 100% { opacity: 0; transform: scale(.96); }
}

/* ML pipeline */
.f-ml-viz {
    position: relative;
    margin: 0 0 1rem;
    padding: 1.3rem;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: linear-gradient(145deg, #0d1e15, #153326);
    box-shadow: var(--shadow-lg);
}
.f-ml-viz-head { color: white; font-size: .98rem; font-weight: 750; }
.f-ml-viz-copy { margin-top: .3rem; color: #a4b9ad; font-size: .79rem; line-height: 1.55; }
.f-pipeline {
    position: relative;
    margin-top: 1.2rem;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: .7rem;
}
.f-pipeline::before {
    content: "";
    position: absolute;
    left: 9%;
    right: 9%;
    top: 31px;
    height: 2px;
    background: #315544;
}
.f-pipe-node {
    position: relative;
    z-index: 2;
    min-height: 96px;
    padding: .75rem .55rem;
    border: 1px solid #315544;
    border-radius: 11px;
    background: #13281d;
    color: white;
    text-align: center;
}
.f-pipe-icon {
    width: 38px;
    height: 38px;
    margin: 0 auto .45rem;
    display: grid;
    place-items: center;
    border: 1px solid #397259;
    border-radius: 10px;
    background: #193b2a;
    color: #58e39b;
    font-size: 1rem;
}
.f-pipe-visual {
    position: relative;
    width: 38px;
    height: 38px;
    margin: 0 auto .45rem;
    overflow: hidden;
    border: 1px solid #397259;
    border-radius: 10px;
    background: #193b2a;
}
.f-yolo-visual::before,
.f-yolo-visual::after {
    content: "";
    position: absolute;
    border: 1.5px solid #58e39b;
    animation: f-box-pop 2s ease-in-out infinite;
}
.f-yolo-visual::before { inset: 7px 16px 14px 5px; }
.f-yolo-visual::after { inset: 16px 5px 5px 18px; animation-delay: .35s; }
.f-input-visual::before {
    content: "";
    position: absolute;
    left: 6px;
    right: 6px;
    top: 8px;
    bottom: 7px;
    border: 1.5px solid #58e39b;
    border-radius: 4px;
}
.f-input-visual::after {
    content: "";
    position: absolute;
    left: 10px;
    bottom: 10px;
    width: 18px;
    height: 12px;
    clip-path: polygon(0 100%, 36% 42%, 55% 70%, 72% 48%, 100% 100%);
    background: #58e39b;
}
.f-input-visual span {
    position: absolute;
    right: 9px;
    top: 11px;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #a7e9c8;
}
.f-crop-visual::before {
    content: "";
    position: absolute;
    inset: 9px;
    border: 2px solid #58e39b;
    animation: f-crop-zoom 2s ease-in-out infinite;
}
.f-cnn-visual {
    background:
        radial-gradient(circle at 8px 9px, #58e39b 0 2px, transparent 3px),
        radial-gradient(circle at 19px 8px, #58e39b 0 2px, transparent 3px),
        radial-gradient(circle at 30px 10px, #58e39b 0 2px, transparent 3px),
        radial-gradient(circle at 12px 25px, #8bbda1 0 2px, transparent 3px),
        radial-gradient(circle at 26px 26px, #8bbda1 0 2px, transparent 3px),
        #193b2a;
    animation: f-neural-pulse 1.8s ease-in-out infinite;
}
.f-overlay-visual::before,
.f-overlay-visual::after {
    content: "";
    position: absolute;
    width: 13px;
    height: 13px;
    border: 2px solid #58e39b;
    border-radius: 2px;
}
.f-overlay-visual::before { left: 5px; top: 9px; }
.f-overlay-visual::after { right: 5px; bottom: 7px; border-color: #ef746b; }
@keyframes f-box-pop { 0%,100% { opacity:.35; transform:scale(.85); } 50% { opacity:1; transform:scale(1); } }
@keyframes f-crop-zoom { 0%,100% { inset:12px; } 50% { inset:5px; } }
@keyframes f-neural-pulse { 0%,100% { filter:brightness(.85); } 50% { filter:brightness(1.45); } }
.f-pipe-title { font-size: .7rem; font-weight: 750; }
.f-pipe-sub { margin-top: .18rem; color: #829c8e; font-size: .58rem; line-height: 1.35; }
.f-data-pulse {
    position: absolute;
    z-index: 4;
    top: 27px;
    left: 8%;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #58e39b;
    box-shadow: 0 0 15px #58e39b;
    animation: f-data-travel 4s ease-in-out infinite;
}
@keyframes f-data-travel { 0% { left: 8%; } 100% { left: 91%; } }

/* P-Team */
.f-team-scene {
    position: relative;
    min-height: 350px;
    margin-bottom: 1rem;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background:
        radial-gradient(circle at 78% 20%, rgba(255,255,255,.48), transparent 25%),
        linear-gradient(180deg, #e3f1e9 0 69%, #bdd0c5 69% 71%, #eef3f0 71%);
    box-shadow: var(--shadow-sm);
}
.f-team-label {
    position: absolute;
    left: 24px;
    top: 20px;
    color: var(--green-dark);
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .1em;
    text-transform: uppercase;
}
.f-student {
    position: absolute;
    bottom: 0;
    width: 126px;
    height: 224px;
}
.f-student .f-head {
    z-index: 2;
    top: 18px;
    left: 41px;
    width: 45px;
    height: 49px;
    border-radius: 48% 48% 45% 45%;
    box-shadow: none;
}
.f-student .f-body {
    z-index: 1;
    left: 19px;
    top: 75px;
    bottom: auto;
    width: 88px;
    height: 154px;
    border-radius: 40px 40px 16px 16px;
    box-shadow: inset 0 -10px 0 rgba(0,0,0,.06);
}
.f-student-cap { left: 28%; transform:rotate(-1deg); }
.f-student-bun { left: 45%; transform:rotate(1deg); }
.f-student-wave { left: 62%; transform:rotate(-1deg); }
.f-team-arm {
    position: absolute;
    z-index: 3;
    top: 93px;
    width: 66px;
    height: 16px;
    border-radius: 999px;
    background: #d99b72;
    transform-origin: 8px center;
}
.f-arm-tablet {
    right: -7px;
    top: 96px;
    width: 59px;
    transform: rotate(15deg);
}
.f-cap {
    position: absolute;
    z-index: 3;
    top: 14px;
    left: 34px;
    width: 61px;
    height: 25px;
    border-radius: 25px 25px 7px 7px;
    background: #102219;
}
.f-cap::after {
    content: "";
    position: absolute;
    right: -21px;
    bottom: 1px;
    width: 35px;
    height: 7px;
    border-radius: 6px;
    background: #102219;
}

/* Bun hair – Person Mitte: Dutt-Kugel oberhalb des Kopfes */
.f-bun-hair {
    position: absolute;
    z-index: 4;
    top: 4px;
    left: 47px;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: #9f835f;
    box-shadow: inset -4px 4px 0 #7a6044;
}

/* Wave hair – Person Rechts: kein separates Element nötig */
.f-dark-hair {
    display: none;
}

/* Haar per inset box-shadow direkt auf dem Kopf – wie Business-Use-Case */
.f-student-bun .f-head,
.f-student-wave .f-head {
    left: 41px;
    top: 18px;
    width: 45px;
    height: 49px;
    border-radius: 48% 48% 45% 45%;
}
/* Hellbraunes Haar (Bun-Person): inset von links oben */
.f-student-bun .f-head {
    box-shadow: inset -10px 9px 0 #9f835f;
}
/* Dunkles Haar (Wave-Person): inset von links oben */
.f-student-wave .f-head {
    box-shadow: inset -10px 9px 0 #35251e;
}
.f-team-tablet {
    position: absolute;
    z-index: 4;
    left: 84px;
    top: 99px;
    width: 62px;
    height: 84px;
    padding: 5px;
    border-radius: 8px;
    background: #102219;
    transform: rotate(5deg);
    animation: f-tablet-focus 3s ease-in-out infinite;
}
.f-team-tablet-screen {
    width: 100%;
    height: 100%;
    border-radius: 4px;
    background:
        linear-gradient(180deg, #113625 0 18%, transparent 18%),
        radial-gradient(circle at 35% 58%, #ef9b28 0 8px, transparent 9px),
        radial-gradient(circle at 67% 60%, #765035 0 8px, transparent 9px),
        #d8eee2;
}
.f-dog {
    position: absolute;
    z-index: 5;
    left: 20%;
    bottom: -13px;
    width: 166px;
    height: 151px;
    border-radius: 52% 52% 25% 25%;
    background:
        radial-gradient(ellipse at 50% 12%, #2d2927 0 27%, transparent 28%),
        linear-gradient(90deg, #c68745 0 28%, #3d3430 29% 71%, #c68745 72%);
    box-shadow: inset 0 -13px 0 rgba(58,40,30,.08);
    transform: scale(.53);
    transform-origin: left bottom;
}
.f-dog-head {
    position: absolute;
    z-index: 3;
    left: 31px;
    top: -94px;
    width: 104px;
    height: 112px;
    border-radius: 44% 44% 52% 52% / 38% 38% 62% 62%;
    background: #c98845;
    box-shadow:
        inset 13px 0 0 rgba(226,169,98,.28),
        inset -10px 0 0 rgba(104,57,31,.13);
}
.f-dog-head::before {
    content: "";
    position: absolute;
    z-index: 1;
    left: 20px;
    top: 7px;
    width: 64px;
    height: 72px;
    border-radius: 42% 42% 48% 48%;
    background: #40312c;
    clip-path: polygon(18% 0, 82% 0, 100% 37%, 76% 58%, 70% 100%, 30% 100%, 24% 58%, 0 37%);
}
.f-dog-head::after {
    content: "";
    position: absolute;
    z-index: 2;
    left: 11px;
    right: 11px;
    top: 37px;
    height: 40px;
    border-radius: 50%;
    background:
        radial-gradient(ellipse at 19% 45%, #dfa35d 0 16px, transparent 17px),
        radial-gradient(ellipse at 81% 45%, #dfa35d 0 16px, transparent 17px);
}
.f-dog-ear {
    position: absolute;
    z-index: 2;
    left: 35px;
    top: -132px;
    width: 42px;
    height: 66px;
    clip-path: polygon(50% 0, 94% 100%, 6% 100%);
    border-radius: 58% 58% 28% 28%;
    background: #4b3028;
    transform: rotate(-5deg);
}
.f-dog-ear::after {
    content: "";
    position: absolute;
    left: 9px;
    top: 12px;
    width: 24px;
    height: 43px;
    clip-path: polygon(50% 0, 92% 100%, 8% 100%);
    border-radius: 60% 60% 28% 28%;
    background: #c96e63;
}
.f-dog-ear.two {
    left: 89px;
    transform: rotate(5deg) scaleX(-1);
}
.f-dog-eye {
    position: absolute;
    z-index: 6;
    left: 57px;
    top: -49px;
    width: 9px;
    height: 10px;
    border-radius: 50%;
    background: #171918;
    box-shadow: 42px 0 0 #171918;
}
.f-dog-eye::before {
    content: "";
    position: absolute;
    left: -4px;
    top: -10px;
    width: 17px;
    height: 8px;
    border-radius: 50%;
    background: #e5a45b;
    transform: rotate(-5deg);
    box-shadow: 42px 4px 0 #e5a45b;
}
.f-dog-eye::after {
    content: "";
    position: absolute;
    left: 2px;
    top: 2px;
    width: 2px;
    height: 2px;
    border-radius: 50%;
    background: white;
    box-shadow: 42px 0 0 white;
}
.f-dog-muzzle {
    position: absolute;
    z-index: 7;
    left: 59px;
    top: -29px;
    width: 49px;
    height: 38px;
    border-radius: 48% 48% 56% 56%;
    background: #352b28;
    box-shadow: inset 0 -7px 0 rgba(16,18,17,.12);
}
.f-dog-muzzle::after {
    content: "";
    position: absolute;
    left: 14px;
    top: 3px;
    width: 21px;
    height: 13px;
    border-radius: 52% 52% 46% 46%;
    background: #111716;
    box-shadow: inset 0 3px 0 rgba(255,255,255,.08);
}
.f-dog-mouth {
    position: absolute;
    z-index: 8;
    left: 74px;
    top: -1px;
    width: 19px;
    height: 10px;
    border-bottom: 3px solid #141817;
    border-radius: 0 0 50% 50%;
}
.f-dog-tongue {
    position: absolute;
    z-index: 7;
    left: 76px;
    top: 5px;
    width: 15px;
    height: 19px;
    border-radius: 4px 4px 10px 10px;
    background: #df7c79;
    box-shadow: inset -3px 0 0 rgba(135,49,52,.15);
    animation: f-dog-happy 2.6s ease-in-out infinite;
}
.f-dog-chest {
    position: absolute;
    z-index: 2;
    left: 46px;
    top: 14px;
    width: 74px;
    height: 137px;
    background: #efd19d;
    clip-path: polygon(50% 0, 94% 25%, 78% 47%, 86% 100%, 14% 100%, 22% 47%, 6% 25%);
}
.f-dog-shoulder {
    position: absolute;
    z-index: 1;
    left: 18px;
    top: 27px;
    width: 130px;
    height: 69px;
    border-radius: 50% 50% 28% 28%;
    border-top: 25px solid #242b2c;
    transform: rotate(-1deg);
}

/* FIXED: Dog tail – sauberer Halbkreisbogen */
.f-dog-tail {
    display: none;
}

.f-team-produce-crate {
    position: absolute;
    z-index: 5;
    right: 8%;
    bottom: 1px;
    width: 126px;
    height: 78px;
    border: 5px solid #865d35;
    border-top-width: 8px;
    border-radius: 10px 10px 7px 7px;
    background:
        linear-gradient(180deg, transparent 0 42%, rgba(108,67,34,.24) 43% 48%, transparent 49% 69%, rgba(108,67,34,.22) 70% 75%, transparent 76%),
        #b9854e;
    box-shadow: inset 0 -8px 0 rgba(92,56,30,.12);
}
.f-team-produce-crate::before,
.f-team-produce-crate::after {
    content: "";
    position: absolute;
    top: -31px;
    width: 39px;
    height: 35px;
    border-radius: 52% 48% 50% 46%;
    box-shadow: inset -6px -5px 0 rgba(65,73,31,.12);
}
.f-team-produce-crate::before {
    left: 15px;
    background:
        radial-gradient(ellipse at 55% 4%, #416939 0 5px, transparent 6px),
        #73a64e;
    transform: rotate(-7deg);
}
.f-team-produce-crate::after {
    right: 13px;
    background:
        radial-gradient(ellipse at 48% 4%, #42633a 0 5px, transparent 6px),
        #dc6b4f;
    transform: rotate(7deg);
}
.f-team-produce {
    position: absolute;
    z-index: 6;
    top: -35px;
    left: 47px;
    width: 34px;
    height: 38px;
    border-radius: 48% 52% 50% 50%;
    background:
        radial-gradient(ellipse at 50% 4%, #4b7041 0 5px, transparent 6px),
        #efaa36;
    box-shadow:
        -31px 7px 0 -6px #8fb84f,
        31px 7px 0 -6px #719b45;
}
@keyframes f-tail { 0%,100% { transform:rotate(-30deg); } 50% { transform:rotate(-12deg); } }
@keyframes f-dog-happy {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(2px); }
}
@keyframes f-dog-tail-wag {
    0%, 100% { transform: rotate(-18deg); }
    50% { transform: rotate(10deg); }
}

/* Responsive layout */
@media (max-width: 1180px) {
    .block-container {
        max-width: 100% !important;
        padding-left: 1.75rem !important;
        padding-right: 1.75rem !important;
    }
    .f-topline,
    .f-nav {
        margin-left: -1.75rem;
        margin-right: -1.75rem;
    }
    .f-nav { padding-left: 1.75rem; padding-right: 1.75rem; }
    .st-key-sticky_navigation {
        width: calc(100% + 3.5rem) !important;
        margin-left: -1.75rem;
        margin-right: -1.75rem;
        padding-left: 1.75rem;
        padding-right: 1.75rem;
    }
    .f-hero { gap: 1.35rem; }
    .f-title { font-size: clamp(2rem, 4.8vw, 2.85rem); }
    .f-story {
        grid-template-columns: minmax(0, 1fr) minmax(235px, .78fr);
        gap: 1rem;
    }
    .f-pipeline { gap: .45rem; }
    .f-pipe-node { padding-left: .35rem; padding-right: .35rem; }
}

@media (max-height: 850px) and (min-width: 901px) {
    .f-nav { min-height: 62px; }
    .st-key-sticky_navigation {
        padding-top: .48rem;
        padding-bottom: .52rem;
    }
    .st-key-sticky_navigation [data-testid="stHorizontalBlock"] {
        margin-top: .4rem;
    }
    .f-hero {
        padding-top: 1.55rem;
        padding-bottom: 1.15rem;
    }
    .f-subtitle { margin-top: .6rem; }
    .f-panel-head {
        min-height: 54px;
        padding-top: .8rem;
        padding-bottom: .8rem;
    }
    [data-testid="stFileUploader"] section,
    [data-testid="stCameraInput"] {
        min-height: 265px !important;
        padding: 1.25rem !important;
    }
    .f-awaiting { min-height: 235px; }
    .f-uploaded-frame [data-testid="stImage"] {
        min-height: 280px;
    }
    .f-uploaded-frame [data-testid="stImage"] img {
        height: 280px;
    }
}

@media (max-width: 900px) {
    .f-nav { min-height: 64px; }
    .f-brand { font-size: 1.35rem; }
    .f-brand-mark { width: 35px; height: 35px; }
    .f-nav-meta { display: none; }
    .f-proto {
        justify-content: flex-start;
        flex-wrap: nowrap;
        overflow-x: auto;
        overscroll-behavior-inline: contain;
        padding-bottom: .2rem;
        scrollbar-width: thin;
        scrollbar-color: #426553 transparent;
    }
    .f-proto-label,
    .f-chip { flex: 0 0 auto; white-space: nowrap; }
    .st-key-sticky_navigation [data-testid="stHorizontalBlock"] {
        max-width: 100%;
        gap: .35rem;
    }
    .st-key-sticky_navigation .stButton > button {
        min-height: 34px !important;
        padding: .2rem .4rem !important;
        font-size: .62rem !important;
        line-height: 1.15 !important;
        white-space: normal !important;
    }
    .f-hero {
        grid-template-columns: 1fr;
        gap: 1rem;
        padding: 2.15rem 0 1.5rem;
    }
    .f-status {
        min-width: 0;
        width: min(100%, 310px);
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlockBorderWrapper"]) {
        display: grid !important;
        grid-template-columns: minmax(0, 1fr);
        gap: 1rem;
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stFileUploader"]) {
        display: grid !important;
        grid-template-columns: minmax(0, 1fr);
        gap: 1rem;
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlockBorderWrapper"])
    > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has([data-testid="stFileUploader"])
    > [data-testid="stColumn"] {
        width: auto !important;
        min-width: 0 !important;
        flex: none !important;
    }
    .f-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .f-story {
        grid-template-columns: 1fr;
        padding: 1.1rem;
    }
    .f-scene { min-height: 265px; }
    .f-ml-viz { padding: 1.1rem; }
    .f-pipeline {
        width: 590px;
        grid-template-columns: repeat(5, 110px);
        gap: .55rem;
    }
    .f-ml-viz {
        overflow-x: auto;
        overscroll-behavior-inline: contain;
    }
    .f-pipeline::before {
        left: 45px;
        right: auto;
        width: 540px;
    }
    .f-about { max-width: 100%; }
    .f-team-scene {
        min-height: 0;
        height: 315px;
    }
    .f-team-scene > *:not(.f-team-label) {
        transform-origin: bottom center;
    }
    [data-testid="stFileUploader"] section,
    [data-testid="stCameraInput"],
    .f-uploaded-frame [data-testid="stImage"] {
        min-height: 300px !important;
    }
    .f-uploaded-frame [data-testid="stImage"] img {
        height: 300px;
    }
}

@media (max-width: 700px) {
    .block-container {
        padding: 0 1rem 3rem !important;
        overflow-x: clip;
    }
    .f-topline,
    .f-nav {
        margin-left: -1rem;
        margin-right: -1rem;
    }
    .f-nav {
        padding: 0 1rem;
        min-height: 60px;
    }
    .f-brand { gap: .5rem; font-size: 1.22rem; }
    .f-brand-mark {
        width: 32px;
        height: 32px;
        border-radius: 9px;
        font-size: 1rem;
    }
    .f-version { padding: .15rem .38rem; font-size: .56rem; }
    .st-key-sticky_navigation {
        width: calc(100% + 2rem) !important;
        margin: 0 -1rem;
        padding: .45rem 1rem .55rem;
    }
    .f-proto { gap: .38rem; }
    .f-proto-label { font-size: .61rem; }
    .st-key-sticky_navigation .f-chip {
        padding: .18rem .46rem;
        font-size: .65rem;
    }
    .st-key-sticky_navigation [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: .35rem;
        margin-top: .4rem;
    }
    .st-key-sticky_navigation [data-testid="stColumn"] {
        width: auto !important;
        min-width: 0 !important;
    }
    .st-key-sticky_navigation .stButton > button {
        min-height: 32px !important;
        font-size: .60rem !important;
    }
    .f-hero { padding: 1.65rem 0 1.25rem; }
    .f-eyebrow { font-size: .62rem; letter-spacing: .085em; }
    .f-title {
        max-width: 100%;
        font-size: clamp(1.8rem, 9vw, 2.35rem);
        line-height: 1.06;
        letter-spacing: -.045em;
        overflow-wrap: anywhere;
    }
    .f-subtitle { font-size: .86rem; line-height: 1.62; }
    .f-status { width: 100%; }
    [data-testid="stHorizontalBlock"]:not(.st-key-sticky_navigation [data-testid="stHorizontalBlock"]) {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"]:not(.st-key-sticky_navigation [data-testid="stHorizontalBlock"])
    > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 0 !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 0;
        border-radius: 13px !important;
    }
    .f-panel-head {
        min-height: 56px;
        padding: .85rem 1rem;
    }
    .f-metrics { grid-template-columns: 1fr; }
    .f-metric-wide { grid-column: auto; }
    .st-key-crisp_dm {
        padding: .9rem;
        border-radius: 13px;
    }
    .st-key-crisp_dm [data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    }
    .st-key-crisp_dm [data-testid="stColumn"] {
        width: auto !important;
        flex: none !important;
    }
    .st-key-crisp_dm .stButton > button {
        height: 52px;
        min-height: 52px;
        padding: .34rem .24rem !important;
        font-size: .68rem !important;
    }
    .f-crisp-intro,
    .f-crisp-detail p {
        font-size: .8rem !important;
        line-height: 1.62 !important;
    }
    .st-key-crisp_dm .f-section-label { font-size: .94rem; }
    .f-crisp-detail h4 { font-size: .94rem; }
    .f-card,
    .f-story { padding: 1rem; border-radius: 13px; }
    .f-card h3,
    .f-story-copy h3 { font-size: .94rem; }
    .f-card p,
    .f-story-copy p { font-size: .8rem; line-height: 1.62; }
    .f-scene {
        min-height: 245px;
        transform: translateZ(0);
    }
    .f-phone { right: 5%; }
    .f-help-pill { right: 5%; }
    .f-team-scene {
        height: 270px;
        overflow: hidden;
    }
    .f-team-label { left: 16px; top: 14px; }
    .f-student-cap { left: 19%; transform: scale(.83) rotate(-1deg); transform-origin: bottom center; }
    .f-student-bun { left: 43%; transform: scale(.83) rotate(1deg); transform-origin: bottom center; }
    .f-student-wave { left: 67%; transform: scale(.83) rotate(-1deg); transform-origin: bottom center; }
    .f-dog { left: 7%; transform: scale(.43); }
    .f-team-produce-crate { right: 2%; transform: scale(.82); transform-origin: bottom right; }
    [data-testid="stFileUploader"] section,
    [data-testid="stCameraInput"],
    .f-uploaded-frame [data-testid="stImage"] {
        min-height: 245px !important;
        padding: 1.1rem !important;
    }
    .f-uploaded-frame [data-testid="stImage"] img {
        height: 245px;
    }
    [data-baseweb="tab-list"] {
        width: 100%;
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    [data-baseweb="tab"] {
        min-width: 0;
        padding: 0 .45rem !important;
        justify-content: center;
        font-size: .72rem !important;
    }
    .f-footer {
        margin-top: 2.3rem;
        flex-direction: column;
        align-items: flex-start;
        gap: .25rem;
    }
}

@media (max-width: 440px) {
    .block-container { padding-left: .75rem !important; padding-right: .75rem !important; }
    .f-topline,
    .f-nav { margin-left: -.75rem; margin-right: -.75rem; }
    .f-nav { padding-left: .75rem; padding-right: .75rem; }
    .f-brand { font-size: 1.08rem; }
    .f-brand-mark { width: 29px; height: 29px; }
    .st-key-sticky_navigation {
        width: calc(100% + 1.5rem) !important;
        margin-left: -.75rem;
        margin-right: -.75rem;
        padding-left: .75rem;
        padding-right: .75rem;
    }
    .f-title { font-size: clamp(1.65rem, 10vw, 2rem); }
    .f-status { padding: .7rem .8rem; }
    .f-result { padding: .8rem; gap: .6rem; }
    .f-result-icon { width: 28px; height: 28px; flex-basis: 28px; }
    .f-result-copy { font-size: .74rem; }
    .f-flow-row { grid-template-columns: 27px 1fr; gap: .6rem; }
    .f-flow-num { width: 26px; height: 26px; }
    .st-key-crisp_dm [data-testid="stHorizontalBlock"] {
        grid-template-columns: 1fr !important;
    }
    .st-key-crisp_dm .stButton > button {
        height: 46px;
        min-height: 46px;
        font-size: .72rem !important;
    }
    .f-scene { min-height: 225px; }
    .f-person { left: 5%; transform: scale(.88); transform-origin: bottom left; }
    .f-tablet { left: 27%; transform: scale(.88) rotate(3deg); transform-origin: center; }
    .f-crate { right: 3%; transform: scale(.86); transform-origin: bottom right; }
    .f-story:nth-child(2) .f-phone {
        left: 4%;
        right: auto;
        transform: scale(.88);
        transform-origin: top left;
    }
    .f-story:nth-child(2) .f-alert-person {
        left: auto;
        right: 4%;
        transform: scale(.63);
        transform-origin: bottom right;
    }
    .f-team-scene { height: 225px; }
    .f-student-cap { left: 14%; transform: scale(.68) rotate(-1deg); }
    .f-student-bun { left: 40%; transform: scale(.68) rotate(1deg); }
    .f-student-wave { left: 66%; transform: scale(.68) rotate(-1deg); }
    .f-dog { left: 1%; transform: scale(.34); }
    .f-team-produce-crate { right: -3%; transform: scale(.65); }
    [data-testid="stFileUploader"] section button {
        min-width: min(180px, 100%) !important;
    }
}

/* Consistent content width and original P-Team illustration */
.st-key-crisp_dm {
    width: 100%;
    max-width: 1180px;
    margin-left: auto;
    margin-right: auto;
}
.f-team-stage {
    position: absolute;
    inset: 0;
}
.f-student .f-head {
    top: 10px;
    left: 36px;
    width: 54px;
    height: 56px;
    border-radius: 49% 49% 46% 46%;
}
.f-arm-tablet {
    right: -18px;
    top: 96px;
}
.f-cap {
    top: 9px;
    left: 34px;
    width: 55px;
    height: 23px;
}
.f-cap::after {
    right: -18px;
    width: 31px;
    height: 6px;
}
.f-bun-hair {
    top: -1px;
    left: 35px;
    width: 22px;
    height: 22px;
    box-shadow: none;
}
.f-student-bun .f-head,
.f-student-wave .f-head {
    left: 37px;
    top: 12px;
    width: 54px;
    height: 54px;
    border-radius: 50%;
}
.f-student-bun .f-head {
    box-shadow: inset 13px 10px 0 #9f835f;
}
.f-student-wave .f-head {
    box-shadow: inset 13px 10px 0 #35251e;
}
.f-team-tablet {
    left: 96px;
}
.f-dog-tongue {
    left: 78px;
    top: 6px;
    width: 11px;
    height: 14px;
    border-radius: 3px 3px 8px 8px;
}
.f-dog-tail {
    display: block;
    position: absolute;
    z-index: 4;
    left: calc(20% - 20px);
    bottom: -16px;
    width: 43px;
    height: 58px;
    border: 10px solid #b9763f;
    border-right-color: transparent;
    border-bottom-color: transparent;
    border-radius: 78% 45% 34% 72%;
    transform-origin: 38px 52px;
    animation: f-dog-tail-wag 1.5s ease-in-out infinite;
}

@media (max-width: 900px) {
    .f-team-scene { height: 298px; }
    .f-team-scene > .f-team-stage {
        left: 50%;
        right: auto;
        width: 820px;
        height: 350px;
        transform: translateX(-50%) scale(.85);
        transform-origin: center top;
    }
    .f-student-cap { left: 28%; transform: rotate(-1deg); }
    .f-student-bun { left: 45%; transform: rotate(1deg); }
    .f-student-wave { left: 62%; transform: rotate(-1deg); }
    .f-dog { left: 20%; bottom: -13px; transform: scale(.53); }
    .f-dog-tail { left: calc(20% - 20px); bottom: -16px; }
    .f-team-produce-crate {
        right: 8%;
        bottom: 1px;
        transform: none;
    }
}

@media (max-width: 700px) {
    .f-team-scene { height: 252px; }
    .f-team-scene > .f-team-stage { transform: translateX(-50%) scale(.72); }
}

@media (max-width: 520px) {
    .f-team-scene { height: 196px; }
    .f-team-scene > .f-team-stage { transform: translateX(-50%) scale(.56); }
}

@media (max-width: 400px) {
    .f-team-scene { height: 147px; }
    .f-team-scene > .f-team-stage { transform: translateX(-50%) scale(.42); }
}

@media (min-width: 901px) {
    .f-topline,
    .f-nav {
        width: 100vw;
        margin-left: calc(50% - 50vw);
        margin-right: calc(50% - 50vw);
    }
    .st-key-sticky_navigation {
        width: 100vw !important;
        margin-left: calc(50% - 50vw);
        margin-right: calc(50% - 50vw);
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
    }
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
        "last_detail_mode": False,
        "crisp_phase": "business",
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

def load_evaluation_metrics() -> dict[str, Any] | None:
    metrics_path = ROOT / "models" / "evaluation_metrics.json"
    try:
        return None
    except (OSError, json.JSONDecodeError):
        return None


def normalize_prediction(result: Any) -> tuple[str, float]:
    if isinstance(result, dict):
        label = result.get("label") or result.get("class") or "edible"
        confidence = result.get("confidence") or result.get("score") or 0.0
    elif isinstance(result, (tuple, list)) and len(result) >= 2:
        label, confidence = result[0], result[1]
    else:
        raise ValueError("Nicht unterstütztes Ergebnisformat der ML-Schnittstelle.")

    normalized = str(label).strip().lower()
    if normalized == "error":
        raise RuntimeError("Das Frischemodell konnte das Bild nicht verarbeiten.")

    edible_aliases = {"edible", "fresh", "frisch", "good", "ok", "verwertbar"}
    spoiled_aliases = {"non_edible", "spoiled", "rotten", "bad", "risk", "pruefen", "prüfen"}
    if normalized in edible_aliases:
        final_label = "edible"
    elif normalized in spoiled_aliases:
        final_label = "spoiled"
    else:
        final_label = "spoiled"
    return final_label, max(0.0, min(1.0, float(confidence)))


def predict_freshness(image: Image.Image) -> tuple[str, float, float, str]:
    """Use the project model for one PIL image and normalize the UI label."""
    from src.predict import predict_image

    result = predict_image(image)
    label, confidence = normalize_prediction(result)
    probability_non_edible = float(result[2]) if isinstance(result, (tuple, list)) and len(result) >= 3 else 0.0
    return label, confidence, max(0.0, min(1.0, probability_non_edible)), "src.predict.predict_image"


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
            "label": str("Produkt"),
            "score": max(0.0, min(1.0, float(det.get("score") or det.get("confidence") or 0.0))),
        }
    except Exception:
        return None


def detect_objects(image: Image.Image) -> tuple[list[dict[str, Any]], str]:
    """Use the optional project detector when available."""
    try:
        from src.detector import detect_objects as project_detector

        raw = project_detector(image)
        detections = []
        for item in raw:
            normalized = normalize_detection(item)
            if normalized:
                detections.append(normalized)
        return detections, "src.detector.detect_objects"
    except Exception as e:
        print(f"[WARN] Object detection unavailable: {e}")
        return [], "Detektion nicht verfügbar"


def crop_detection(image: Image.Image, detection: dict[str, Any]) -> Image.Image | None:
    width, height = image.size
    try:
        x1, y1, x2, y2 = [int(value) for value in detection["box"]]
    except (KeyError, TypeError, ValueError):
        return None

    x1, x2 = sorted((max(0, x1), min(width - 1, x2)))
    y1, y2 = sorted((max(0, y1), min(height - 1, y2)))
    if x2 <= x1 or y2 <= y1:
        return None
    return image.crop((x1, y1, x2, y2))


def analyze_image(
    image: Image.Image,
    detail_mode: bool = False,
) -> tuple[str, float, list[dict[str, Any]], dict[str, str]]:
    label, confidence, probability_non_edible, freshness_engine = predict_freshness(image)
    engines = {
        "freshness": freshness_engine,
        "detection": "Gesamtbildanalyse",
    }

    if not detail_mode:
        return label, confidence, [], engines

    detections, detection_engine = detect_objects(image)
    enriched_detections = [
        {
            **detection,
            "freshness_label": label,
            "freshness_confidence": confidence,
            "probability_non_edible": probability_non_edible,
        }
        for detection in detections
    ]
    engines["detection"] = detection_engine
    return label, confidence, enriched_detections, engines


def load_font(size: int) -> ImageFont.ImageFont:
    font_path = os.path.join(os.path.dirname(PIL.__file__), "fonts", "DejaVuSans.ttf")
    return ImageFont.truetype(font_path, size=size)


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
    base_font_size = max(11, int(min(width, height) * 0.026))

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
        item_label = detection.get("freshness_label", freshness_label)
        item_confidence = detection.get("freshness_confidence", confidence)
        color = "#00A962" if item_label == "edible" else "#C9362B"
        verdict = "Verwertbar" if item_label == "edible" else "Prüfen"
        x1, y1, x2, y2 = detection["box"]
        x1, x2 = sorted((max(0, x1), min(width - 1, x2)))
        y1, y2 = sorted((max(0, y1), min(height - 1, y2)))
        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=max(5, line_width * 2),
            outline=color,
            width=line_width,
        )

        is_portrait = height > width * 1.15
        if is_portrait:
            label_text = (
                f"{detection['label']} · Objekt {detection['score']:.0%}\n"
                f"Frische {item_confidence:.0%} · {verdict}"
            )
        else:
            label_text = (
                f"{detection['label']} · Objekt {detection['score']:.0%} · "
                f"Frische {item_confidence:.0%} · {verdict}"
            )
        font_size = base_font_size
        font = load_font(font_size)
        text_box = draw.multiline_textbbox((0, 0), label_text, font=font, spacing=2)
        max_text_width = max(40, width - line_width * 8)
        while text_box[2] - text_box[0] > max_text_width and font_size > 8:
            font_size -= 1
            font = load_font(font_size)
            text_box = draw.multiline_textbbox((0, 0), label_text, font=font, spacing=2)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
        pad_x, pad_y = max(4, line_width * 2), max(3, line_width)
        pill_width = min(width, text_width + pad_x * 2)
        pill_left = min(max(0, x1), max(0, width - pill_width))
        pill_height = text_height + pad_y * 2
        if y1 >= pill_height + line_width:
            pill_top = y1 - pill_height - line_width
            pill_bottom = pill_top + pill_height
        else:
            pill_top = min(max(0, y1 + line_width), max(0, height - pill_height))
            pill_bottom = pill_top + pill_height
        pill_right = pill_left + pill_width
        draw.rounded_rectangle(
            [pill_left, pill_top, pill_right, pill_bottom],
            radius=max(4, line_width * 2),
            fill=color,
        )
        draw.multiline_text(
            (pill_left + pad_x, pill_top + pad_y - text_box[1]),
            label_text,
            fill="white",
            font=font,
            spacing=2,
        )

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
    label: str,
    confidence: float,
    annotated_image: Image.Image,
    detections: list[dict[str, Any]],
    engines: dict[str, str],
) -> bytes | None:
    try:
        None
    except ImportError:
        return None
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
        "brand": ParagraphStyle(
            "brand", fontName="Helvetica-Bold", fontSize=16, leading=20,
            textColor=green, spaceAfter=5
        ),
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Bold", fontSize=18, leading=23,
            textColor=ink, spaceAfter=8
        ),
        "meta": ParagraphStyle(
            "meta", fontName="Helvetica", fontSize=8, leading=12,
            textColor=muted, spaceAfter=5
        ),
        "label": ParagraphStyle(
            "label",
            fontName="Helvetica-Bold",
            fontSize=7,
            textColor=muted,
            spaceBefore=16,
            spaceAfter=8,
        ),
        "verdict": ParagraphStyle(
            "verdict", fontName="Helvetica-Bold", fontSize=13, leading=18,
            textColor=verdict_color, spaceAfter=6
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=8.5, leading=14,
            textColor=muted, spaceAfter=5
        ),
    }

    story = [
        Paragraph("freshify", styles["brand"]),
        Paragraph("Qualitätsprotokoll Wareneingang", styles["title"]),
        Paragraph(
            f"Protokoll-ID: <b>{escape(report_id)}</b> · {escape(timestamp)} · v{APP_VERSION}",
            styles["meta"],
        ),
        Spacer(1, 12),
        Paragraph("BEFUND", styles["label"]),
        Paragraph(
            "Visuell verwertbar" if label == "edible" else "Manuelle Kontrolle erforderlich",
            styles["verdict"],
        ),
        Paragraph(f"ML-Konfidenz: <b>{confidence:.0%}</b>", styles["body"]),
        Spacer(1, 5),
        Paragraph("ANALYSE-OVERLAY", styles["label"]),
    ]

    image_buffer = io.BytesIO(image_bytes(annotated_image))
    story.extend(
        [
            ReportImage(image_buffer, width=130 * mm, height=97.5 * mm, kind="proportional"),
            Spacer(1, 10),
            Paragraph("ANALYSEDATEN", styles["label"]),
        ]
    )

    rows = [
        ["Feld", "Wert"],
        ["Protokoll-ID", report_id],
        ["ML-Klasse", label],
        ["ML-Konfidenz", f"{confidence:.4f}"],
        ["Erkannte Objekte", str(len(detections)) if detections else "1 (Demo)"],
        ["Frischemodell", engines.get("freshness", "–")],
        ["Objekterkennung", engines.get("detection", "–")],
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
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend(
        [
            table,
            Spacer(1, 18),
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
""",
    unsafe_allow_html=True,
)

with st.container(key="sticky_navigation"):
    st.markdown(
        f"""
<div class="f-proto">
    <span class="f-proto-label">Prototyp · optimiert für</span>
    {chips}
</div>
""",
        unsafe_allow_html=True,
    )
    nav_a, nav_b, nav_c, nav_d = st.columns([1.05, 1.5, 1.7, 1.1])
    with nav_a:
        if st.button(
            "◉  Analyse",
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
    with nav_c:
        if st.button(
            "Business Use Cases",
            type="primary" if st.session_state.page == "business" else "secondary",
            use_container_width=True,
        ):
            st.session_state.page = "business"
            st.rerun()
    with nav_d:
        if st.button(
            "Über uns",
            type="primary" if st.session_state.page == "team" else "secondary",
            use_container_width=True,
        ):
            st.session_state.page = "team"
            st.rerun()


if st.session_state.page == "analyse":
    st.markdown(
        """
<div class="f-hero">
    <div>
        <div class="f-eyebrow">B2B · Wareneingang und Qualitätssicherung</div>
        <div class="f-title f-title-linkless">Frische sichtbar machen.</div>
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

    with left_column.container(border=True, key="capture_panel"):
        st.markdown(
            """
<div class="f-panel-head">
    <span class="f-panel-step">1</span>
    <span class="f-panel-title">Bilderfassung</span>
</div>
""",
            unsafe_allow_html=True,
        )

        upload_tab, camera_tab = st.tabs(["Datei oder Galerie", "Foto aufnehmen"])
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

        detail_mode = st.toggle(
            "Detailmodus",
            value=False,
            help="Aktiviert MobileSAM-Objektsegmentierung. Die Standardanalyse klassifiziert nur das Gesamtbild.",
        )

        replacement_file = st.session_state.get("replace_file")
        image_source = (
            replacement_file
            if replacement_file is not None
            else camera_image if camera_image is not None else uploaded_file
        )
        if image_source is not None:
            st.markdown(
                """
<style>
[data-testid="stFileUploader"],
[data-testid="stCameraInput"] { display: none !important; }
.st-key-replace_file,
.st-key-replace_file [data-testid="stFileUploader"] {
    display: block !important;
}
.st-key-replace_file [data-testid="stFileUploader"] section {
    min-height: 50px !important;
    padding: .35rem !important;
    border: 0 !important;
    background: transparent !important;
}
.st-key-replace_file [data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
.st-key-replace_file [data-testid="stFileUploader"] section button {
    min-width: 100% !important;
    min-height: 40px !important;
    background: var(--surface-soft) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}
[data-testid="stImage"] {
    min-height: 345px;
    display: grid;
    place-items: center;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    background: var(--surface-soft);
}
[data-testid="stImage"] img {
    width: 100%;
    height: 345px;
    object-fit: contain;
}
</style>
""",
                unsafe_allow_html=True,
            )
            raw_bytes = source_bytes(image_source)
            analysis_key = (
                f"{getattr(image_source, 'name', 'camera')}:"
                f"{len(raw_bytes)}:{hash(raw_bytes)}:detail={int(detail_mode)}"
            )
            if st.session_state.analysis_key != analysis_key:
                with st.spinner("ML-Analyse läuft …"):
                    started_at = time.perf_counter()
                    try:
                        image = ImageOps.exif_transpose(Image.open(io.BytesIO(raw_bytes))).convert("RGB")
                        label, confidence, detections, engines = analyze_image(
                            image,
                            detail_mode=detail_mode,
                        )
                        annotated = draw_boxes(image, detections, label, confidence)
                    except Exception as e:
                        st.error(f"ML-Analyse konnte nicht ausgeführt werden: {e}")
                        st.stop()

                    inference_ms = (time.perf_counter() - started_at) * 1000
                    time.sleep(0.25)
                    st.session_state.update(
                        {
                            "analysis_key": analysis_key,
                            "last_label": label,
                            "last_confidence": confidence,
                            "last_original": image,
                            "last_annotated": annotated,
                            "last_detections": detections,
                            "last_engine": engines,
                            "last_detail_mode": detail_mode,
                            "last_inference_ms": inference_ms,
                            "last_image_size": image.size,
                        }
                    )

            st.image(
                st.session_state.last_annotated,
                use_container_width=True,
                caption="ML-Overlay · Grün: visuell unauffällig · Rot: manuell prüfen",
            )
            st.markdown(
                '<div class="f-section-label" style="margin-top:.7rem">Anderes Bild analysieren</div>',
                unsafe_allow_html=True,
            )
            st.file_uploader(
                "Bild ersetzen",
                type=["jpg", "jpeg", "png"],
                key="replace_file",
                label_visibility="collapsed",
                help="Eine neue Datei auswählen und die aktuelle Analyse ersetzen.",
            )

    with right_column.container(border=True, key="finding_panel"):
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
<div class="f-awaiting">
    <div>
        <div class="f-awaiting-icon"></div>
        <div class="f-awaiting-title">Bereit für den ersten Befund</div>
        <div class="f-awaiting-copy">
            Nach der Bilderfassung erscheinen hier ML-Ergebnis, Laufzeitmetriken
            sowie PDF- und JSON-Export.
        </div>
    </div>
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
            inference_ms = st.session_state.get("last_inference_ms", 0.0)
            image_width, image_height = st.session_state.get("last_image_size", (0, 0))
            detail_mode = st.session_state.get("last_detail_mode", False)

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
            object_display = str(object_count) if detail_mode else "Gesamtbild"
            object_note = "SAM-Objekte im Detailmodus" if detail_mode else "Keine Segmentierung im Standardmodus"
            image_megapixels = (image_width * image_height) / 1_000_000
            throughput = (
                image_megapixels / (inference_ms / 1000)
                if inference_ms > 0
                else 0.0
            )
            confidence_level = (
                "hoch" if confidence >= 0.8
                else "mittel" if confidence >= 0.65
                else "niedrig"
            )
            engine_display = (
                "Projektmodell"
                if engines["freshness"] != "Demo-Heuristik"
                else "Demo"
            )
            st.markdown(
                f"""
<div class="f-metrics">
    <div class="f-metric">
        <div class="f-metric-label">ML-Konfidenz</div>
        <div class="f-metric-value">{confidence:.0%}</div>
        <div class="f-metric-note">Bewertungsniveau: {confidence_level}</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Objekte</div>
        <div class="f-metric-value">{object_display}</div>
        <div class="f-metric-note">{object_note}</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Inferenzzeit</div>
        <div class="f-metric-value">{inference_ms:.0f} ms</div>
        <div class="f-metric-note">Gesamte Analyse-Pipeline</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Durchsatz</div>
        <div class="f-metric-value">{throughput:.2f} MP/s</div>
        <div class="f-metric-note">Megapixel pro Sekunde</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Bildauflösung</div>
        <div class="f-metric-value">{image_width} × {image_height}</div>
        <div class="f-metric-note">{image_megapixels:.2f} Megapixel</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Engine</div>
        <div class="f-metric-value">{engine_display}</div>
        <div class="f-metric-note">{escape(engines["freshness"])} · {escape(engines["detection"])}</div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            evaluation_metrics = load_evaluation_metrics()
            if evaluation_metrics:
                accuracy = float(evaluation_metrics["accuracy"])
                precision_macro = float(evaluation_metrics["precision_macro"])
                recall_macro = float(evaluation_metrics["recall_macro"])
                f1_macro = float(evaluation_metrics["f1_macro"])
                test_loss = float(evaluation_metrics["loss"])
                test_samples = int(evaluation_metrics["samples"])
                st.markdown(
                    '<div class="f-section-label">CNN-Evaluation · Testset</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
<div class="f-metrics">
    <div class="f-metric">
        <div class="f-metric-label">Accuracy</div>
        <div class="f-metric-value">{accuracy:.1%}</div>
        <div class="f-metric-note">Korrekte Klassifikationen</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Precision · Macro</div>
        <div class="f-metric-value">{precision_macro:.1%}</div>
        <div class="f-metric-note">Trefferqualität je Klasse</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Recall · Macro</div>
        <div class="f-metric-value">{recall_macro:.1%}</div>
        <div class="f-metric-note">Erkennungsrate je Klasse</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">F1-Score · Macro</div>
        <div class="f-metric-value">{f1_macro:.1%}</div>
        <div class="f-metric-note">Balance aus Precision und Recall</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Test Loss</div>
        <div class="f-metric-value">{test_loss:.4f}</div>
        <div class="f-metric-note">Binary Cross-Entropy</div>
    </div>
    <div class="f-metric">
        <div class="f-metric-label">Testumfang</div>
        <div class="f-metric-value">{test_samples} Bilder</div>
        <div class="f-metric-note">8 frisch · 3 verdorben</div>
    </div>
</div>
<div class="f-demo" style="margin-top:.75rem">
    <strong>Globale Modellmetriken:</strong> Diese Werte stammen aus dem separaten
    CNN-Testset und beschreiben nicht die Sicherheit des aktuell hochgeladenen Einzelbildes.
</div>
""",
                    unsafe_allow_html=True,
                )

            report_id = f"FC-{datetime.now():%Y%m%d%H%M%S}"
            report_data = {
                "protokoll_id": report_id,
                "zeitpunkt": timestamp,
                "ml_klasse": label,
                "ml_konfidenz": round(confidence, 4),
                "konfidenzniveau": confidence_level,
                "inferenzzeit_ms": round(inference_ms, 2),
                "durchsatz_megapixel_pro_s": round(throughput, 4),
                "bildaufloesung": [image_width, image_height],
                "bild_megapixel": round(image_megapixels, 4),
                "cnn_evaluation_testset": evaluation_metrics,
                "detailmodus": detail_mode,
                "objekte": detections,
                "schnittstellen": engines,
                "app_version": APP_VERSION,
                "prototyp": True,
            }

            st.markdown('<div class="f-section-label">Export</div>', unsafe_allow_html=True)
            export_pdf, export_json = st.columns(2)
            pdf_bytes = generate_pdf(
                report_id,
                timestamp,
                label,
                confidence,
                annotated,
                detections,
                engines,
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
<div class="f-notice f-safety-notice">
    <span class="f-safety-icon">!</span>
    <span class="f-safety-copy">
        <strong>Ein Werkzeug, kein Orakel.</strong> Freshify bewertet sichtbare Merkmale.
        Geruch, Kerntemperatur und mikrobiologische Risiken bleiben Teil der Fachprüfung.
    </span>
</div>
""",
                unsafe_allow_html=True,
            )

elif st.session_state.page == "about":
    st.markdown(
        """
<div class="f-hero">
    <div>
        <div class="f-eyebrow">Produkt und Methodik</div>
        <div class="f-title f-title-linkless">Klare Unterstützung. Klare Grenzen.</div>
        <p class="f-subtitle">
            Freshify strukturiert die visuelle Erstsichtung im Wareneingang.
            Das System liefert einen Hinweis, die Freigabe bleibt eine Fachentscheidung.
        </p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

if st.session_state.page == "business":
    st.markdown(
        """
<div class="f-hero">
    <div>
        <div class="f-eyebrow">Business Use Cases</div>
        <div class="f-title f-title-linkless">Von der Einzelkiste bis zum Warenstrom.</div>
        <p class="f-subtitle">
            Freshify kann Mitarbeitende bei einer mobilen Sichtprüfung unterstützen
            oder als Baustein einer automatisierten Qualitätslinie eingesetzt werden.
        </p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="f-about">
    <div class="f-stories">
        <div class="f-story">
            <div class="f-story-copy">
                <div class="f-story-kicker">Business Use Case 01 · Mobile Prüfung</div>
                <h3>Mehr Sicherheit direkt an der Obstkiste</h3>
                <p>
                    Eine Person fotografiert die Ware mit der Tablet-Kamera. Das ML
                    markiert unauffällige Produkte grün und auffällige Produkte rot.
                    So lässt sich ein Fund direkt in der Kiste lokalisieren, statt nur
                    eine abstrakte Anzahl zu erhalten.<br><br>
                    <strong>Profiteure:</strong> Spendenstellen und Restaurants, die
                    wechselnde Lieferungen schnell, nachvollziehbar und mit wenig
                    technischem Aufwand vorsortieren möchten.
                </p>
            </div>
            <div class="f-scene" aria-label="Person fotografiert eine Obstkiste mit einem Tablet">
                <div class="f-person">
                    <div class="f-head"></div>
                    <div class="f-body"></div>
                    <div class="f-arm"></div>
                </div>
                <div class="f-tablet">
                    <div class="f-tablet-screen"></div>
                    <div class="f-tablet-good-box"></div>
                    <div class="f-tablet-line"></div>
                </div>
                <div class="f-crate">
                    <span class="f-fruit f-f1"></span>
                    <span class="f-fruit f-f2 bad"></span>
                    <span class="f-fruit f-f3"></span>
                    <span class="f-fruit f-f4"></span>
                    <span class="f-fruit f-f5"></span>
                </div>
                <div class="f-help-pill">Overlay · Rot direkt lokalisieren</div>
            </div>
        </div>
        <div class="f-story">
            <div class="f-story-copy">
                <div class="f-story-kicker">Business Use Case 02 · Automatisierung</div>
                <h3>Kontinuierliche Sichtprüfung am Fließband</h3>
                <p>
                    Eine fest installierte Kamera analysiert vorbeifahrende Kisten.
                    Die Meldung zeigt nicht nur 14 unauffällige und 2 zu prüfende
                    Produkte, sondern auch das Ergebnisfoto: Grün steht für
                    unauffällig, Rot zeigt die exakte Position einer Auffälligkeit.<br><br>
                    <strong>Profiteure:</strong> Kantinen und Supermärkte mit
                    wiederkehrenden Warenströmen, höherem Volumen und Bedarf an
                    schneller, standardisierter Dokumentation.
                </p>
            </div>
            <div class="f-scene f-belt-scene" aria-label="Kamera scannt eine Obstkiste auf einem Fließband">
                <div class="f-belt"></div>
                <div class="f-crate f-moving-crate">
                    <span class="f-fruit f-f1"></span>
                    <span class="f-fruit f-f2 bad"></span>
                    <span class="f-fruit f-f3"></span>
                    <span class="f-fruit f-f4"></span>
                    <span class="f-fruit f-f5 bad"></span>
                    <span class="f-bad-box good f-box-1"></span>
                    <span class="f-bad-box f-box-2"></span>
                    <span class="f-bad-box good f-box-3"></span>
                    <span class="f-bad-box good f-box-4"></span>
                    <span class="f-bad-box f-box-5"></span>
                </div>
                <div class="f-camera-rig"></div>
                <div class="f-lens"></div>
                <div class="f-scan-beam"></div>
                <div class="f-person f-alert-person">
                    <div class="f-head"></div>
                    <div class="f-body"></div>
                </div>
                <div class="f-phone">
                    <div class="f-phone-title">Kiste analysiert</div>
                    <div class="f-result-photo">
                        <span class="f-rp1"></span><span class="f-rp2"></span>
                        <span class="f-rp3"></span><span class="f-rp4"></span>
                    </div>
                    <div class="f-phone-row good"><span>Frisch</span><strong>14</strong></div>
                    <div class="f-phone-row bad"><span>Prüfen</span><strong>2</strong></div>
                </div>
            </div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

if st.session_state.page == "team":
    st.markdown(
        """
<div class="f-hero">
    <div>
        <div class="f-eyebrow">Über uns</div>
        <div class="f-title f-title-linkless">Drei Studierende. Eine praktische ML-Idee.</div>
        <p class="f-subtitle">
            Freshify ist ein studentischer Prototyp, der visuelle Qualitätskontrolle
            verständlicher, schneller und besser dokumentierbar machen soll.
        </p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="f-about">
    <div class="f-team-scene" aria-label="Das P-Team mit drei Studierenden und einem Schäferhund">
      <div class="f-team-stage">
        <div class="f-team-label">Das P-Team</div>
        <div class="f-student f-student-cap">
            <div class="f-head"></div>
            <div class="f-cap"></div>
            <div class="f-body"></div>
        </div>
        <span class="f-dog-tail"></span>
        <div class="f-dog">
            <span class="f-dog-ear"></span>
            <span class="f-dog-ear two"></span>
            <span class="f-dog-head"></span>
            <span class="f-dog-shoulder"></span>
            <span class="f-dog-chest"></span>
            <span class="f-dog-eye"></span>
            <span class="f-dog-muzzle"></span>
            <span class="f-dog-mouth"></span>
            <span class="f-dog-tongue"></span>
        </div>
        <div class="f-student f-student-bun">
            <div class="f-head"></div>
            <div class="f-bun-hair"></div>
            <div class="f-body"></div>
            <div class="f-team-arm f-arm-tablet"></div>
            <div class="f-team-tablet"><div class="f-team-tablet-screen"></div></div>
        </div>
        <div class="f-student f-student-wave">
            <div class="f-head"></div>
            <div class="f-dark-hair"></div>
            <div class="f-body"></div>
        </div>
        <div class="f-team-produce-crate">
            <span class="f-team-produce"></span>
        </div>
      </div>
    </div>
    <div class="f-card">
        <h3>Das Projekt</h3>
        <p>
            Freshify wurde vom <strong>P-Team</strong>, drei Studierenden, im Rahmen der
            Lehrveranstaltung <strong>Machine Learning for Business</strong> entwickelt.
            Im Mittelpunkt steht nicht nur ein ML-Modell, sondern die Frage, wie aus
            technischer Erkennung ein sinnvoller und verständlicher Arbeitsablauf entsteht.
        </p>
    </div>
    <div class="f-card">
        <h3>Unser Ansatz</h3>
        <p>
            Der Prototyp kombiniert Objekterkennung, bildbasierte Frischebewertung,
            visuelle Overlays und strukturierte Exporte. Ziel ist eine Lösung, die
            Mitarbeitende unterstützt, ohne menschliche Qualitätskontrolle oder
            sensorische Prüfungen zu ersetzen.
        </p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

if st.session_state.page == "about":
    st.markdown(
        f"""
<div class="f-about">
    <div class="f-card">
        <h3>Warum Freshify?</h3>
        <p>
            Große Warenmengen, wenig Zeit und wechselnde Teams machen konsistente
            Erstsichtungen schwer. Freshify verbindet Foto, visuellen ML-Befund
            und einen klaren Export in einem kompakten Ablauf.
        </p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    crisp_phases = {
        "business": {
            "number": "01",
            "button": "Business Understanding",
            "title": "Geschäftsproblem verstehen",
            "copy": (
                "Ausgangspunkt ist die Frage, wie Wareneingang und Vorsortierung "
                "beschleunigt werden können, ohne die fachliche Qualitätskontrolle "
                "zu ersetzen. Zielgrößen sind nachvollziehbare Befunde, kurze "
                "Bearbeitungszeiten und eine einfache Dokumentation."
            ),
        },
        "data": {
            "number": "02",
            "button": "Data Understanding",
            "title": "Bilddaten verstehen",
            "copy": (
                "Die Bildbasis kombiniert Bilder aus öffentlichen Datenbanken mit "
                "selbst aufgenommenen Produktbildern. Beide Quellen werden hinsichtlich "
                "Bildqualität, Beleuchtung, Perspektive, sichtbaren Verderbnismerkmalen "
                "und möglicher Verzerrungen untersucht."
            ),
        },
        "preparation": {
            "number": "03",
            "button": "Data Preparation",
            "title": "Trainingsdaten vorbereiten",
            "copy": (
                "Datenbankbilder und eigene Aufnahmen werden manuell in die zwei Klassen "
                "frisch und verdorben gelabelt. Danach werden sie vereinheitlicht, skaliert "
                "und in Trainings-, Validierungs- und Testdaten getrennt. Mit diesen "
                "gelabelten Bildern wird das CNN trainiert; Augmentationen ergänzen "
                "realistische Varianten."
            ),
        },
        "modeling": {
            "number": "04",
            "button": "Modeling",
            "title": "CNN und YOLO modellieren",
            "copy": (
                "Das CNN lernt visuelle Frischemerkmale, während YOLO Produkte und deren "
                "Positionen erkennt. Hyperparameter, Schwellenwerte und Modellvarianten "
                "werden iterativ verglichen, ohne den Business-Kontext aus den Augen zu verlieren."
            ),
        },
        "evaluation": {
            "number": "05",
            "button": "Evaluation",
            "title": "Leistung und Grenzen bewerten",
            "copy": (
                "Neben Accuracy sind Precision, Recall, F1-Score, Confusion Matrix und "
                "Fehlerbilder relevant. Zusätzlich wird geprüft, ob Laufzeit, Erklärbarkeit "
                "und Fehlerrisiko zum vorgesehenen Einsatz im Wareneingang passen."
            ),
        },
        "deployment": {
            "number": "06",
            "button": "Deployment",
            "title": "Prototyp einsetzen und überwachen",
            "copy": (
                "Streamlit verbindet Bilderfassung, Modellaufruf, Overlay und Export. "
                "Für einen produktiven Betrieb wären Modellversionierung, Monitoring, "
                "Drift-Erkennung, Feedbackschleifen und regelmäßige Neubewertungen notwendig."
            ),
        },
    }

    with st.container(key="crisp_dm"):
        st.markdown(
            """
<div class="f-section-label" style="margin-top:0">CRISP-DM · Projektvorgehen</div>
<p class="f-crisp-intro">
    Das Projekt folgt dem iterativen CRISP-DM-Modell. Eine Phase auswählen,
    um ihre konkrete Bedeutung für Freshify anzuzeigen.
</p>
""",
            unsafe_allow_html=True,
        )
        crisp_items = list(crisp_phases.items())
        for row_start in range(0, len(crisp_items), 3):
            row = crisp_items[row_start:row_start + 3]
            columns = st.columns(len(row))
            for column, (phase_key, phase) in zip(columns, row):
                with column:
                    if st.button(
                        f"{phase['number']} · {phase['button']}",
                        key=f"crisp_{phase_key}",
                        type=(
                            "primary"
                            if st.session_state.crisp_phase == phase_key
                            else "secondary"
                        ),
                        use_container_width=True,
                    ):
                        st.session_state.crisp_phase = phase_key
                        st.rerun()

        selected_phase = crisp_phases[st.session_state.crisp_phase]
        st.markdown(
            f"""
<div class="f-crisp-detail">
    <div class="f-crisp-detail-kicker">
        Phase {selected_phase['number']} · {escape(selected_phase['button'])}
    </div>
    <h4>{escape(selected_phase['title'])}</h4>
    <p>{escape(selected_phase['copy'])}</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
<div class="f-about">
    <div class="f-ml-viz">
        <div class="f-ml-viz-head">Vom Prototyp zur produktgenauen Frischeanalyse</div>
        <div class="f-ml-viz-copy">
            Im Prototyp wurden CNN und YOLO trainiert beziehungsweise angebunden:
            Das CNN bewertet aktuell das Gesamtbild, YOLO liefert Produktpositionen.
            Die produktweise Crop-Verknüpfung ist als nächster Endprodukt-Schritt vorgesehen.
        </div>
        <div class="f-pipeline">
            <div class="f-data-pulse"></div>
            <div class="f-pipe-node"><div class="f-pipe-visual f-input-visual"><span></span></div><div class="f-pipe-title">Eingangsbild</div><div class="f-pipe-sub">Kamera oder Galerie</div></div>
            <div class="f-pipe-node"><div class="f-pipe-visual f-yolo-visual"></div><div class="f-pipe-title">YOLO · Prototyp</div><div class="f-pipe-sub">Findet Produkte und Bounding Boxes</div></div>
            <div class="f-pipe-node"><div class="f-pipe-visual f-crop-visual"></div><div class="f-pipe-title">Crop · geplant</div><div class="f-pipe-sub">Schneidet jede Box für eine Einzelbewertung aus</div></div>
            <div class="f-pipe-node"><div class="f-pipe-visual f-cnn-visual"></div><div class="f-pipe-title">CNN · Prototyp</div><div class="f-pipe-sub">Bewertet derzeit das Gesamtbild</div></div>
            <div class="f-pipe-node"><div class="f-pipe-visual f-overlay-visual"></div><div class="f-pipe-title">Overlay · Zielbild</div><div class="f-pipe-sub">Position plus Einzelbewertung ergibt Grün oder Rot</div></div>
        </div>
    </div>
    <div class="f-card">
        <h3>Idee im Ablauf und aktueller Prototyp</h3>
        <p>
            <strong>Bereits umgesetzt:</strong> Das CNN wurde für die visuelle
            Frischebewertung trainiert und bewertet im Prototyp ein Gesamtbild.
            YOLO ist für die Erkennung und Positionierung von Produkten angebunden.
            Beide Ergebnisse werden in der Oberfläche demonstriert.<br><br>
            <strong>Für das Endprodukt vorgesehen:</strong> Jede YOLO-Box wird als
            eigener Crop an das CNN übergeben. Dadurch erhält jedes Produkt eine
            individuelle Bewertung und kann innerhalb derselben Kiste korrekt grün
            oder rot markiert werden. Dieser Verknüpfungsschritt ist noch nicht
            Bestandteil des aktuellen Prototyps.
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
            <div class="f-flow-copy">PDF und JSON stehen direkt zum Download bereit.</div></div>
        </div>
    </div>
    <div class="f-card">
        <h3>Schnittstellenstatus in v{APP_VERSION}</h3>
        <p>
            Freshify bindet ein Frischemodell über <strong>src.predict.predict_image</strong>
            und eine Objekterkennung über <strong>src.yolo.main.detect_objects</strong> an.
            Training und Prototypenlogik für CNN und YOLO sind vorgesehen beziehungsweise
            projektseitig angebunden. Die produktweise Crop-Klassifikation ist noch Teil
            der geplanten Endproduktarchitektur. Fehlen Modellmodule, wechselt die
            Oberfläche sichtbar in den Demo-Modus.
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


st.markdown(
    """
<div class="f-footer">
    <span><strong>Freshify</strong> · Prototyp zur visuellen Frischeanalyse</span>
    <span>P-Team · Machine Learning for Business</span>
</div>
""",
    unsafe_allow_html=True,
)
