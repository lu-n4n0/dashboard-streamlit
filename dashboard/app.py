"""
=============================================================================
SENTINEL 360 . Dashboard GDELT Benin 2025
=============================================================================
Lancer :  streamlit run app.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_data, get_date_range, filter_data,
    compute_weekly_zscore, compute_actor_interactions,
     compute_zone_stats,
    compute_source_bias, compute_alert_feed,
    analyze_peak_complete, analyze_all_crises,
    compute_positive_vs_negative_duration, compute_media_concentration,
    ZONE_ORDER,
)

st.set_page_config(page_title="Sentinel 360", page_icon="S", layout="wide", initial_sidebar_state="expanded")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PALETTE DE COULEURS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Couleur principale : bleu roi
ROYAL = "#2C5F8A"
ROYAL_LIGHT = "#3A7CB8"
ROYAL_DARK = "#1E3A5F"

# Accents
TURQUOISE = "#4ECDC4"
CORAL = "#FF6B6B"
GOLD = "#F7DC6F"

# Semantique
C_POS = "#2ECC71"
C_NEU = "#F39C12"
C_NEG = "#E74C3C"

# Surfaces
CARD_BG = "#141820"
CARD_BORDER = "#1F2530"
TEXT_PRIMARY = "#EAEAEA"
TEXT_SECONDARY = "#9098A3"

QUADCLASS_COLORS = {"Coopération verbale":"#5DADE2","Coopération matérielle":"#2ECC71","Conflit verbal":"#F39C12","Conflit matériel":"#E74C3C"}
ZONE_COLORS = {"Littoral . Cotonou / Porto-Novo":"#3498DB","Sud . Plateau / Zou":"#27AE60","Centre . Borgou / Collines":"#F39C12","Nord . Zone frontaliere":"#E74C3C"}
SENTIMENT_COLORS = {"positif":"#2ECC71","neutre":"#F39C12","négatif":"#E74C3C","negatif":"#E74C3C"}
PILIER_COLORS = {"economie":"#3498DB","securite":"#E74C3C","social":"#2ECC71","autre":"#7F8C8D"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    .block-container {{ padding-top: 0.5rem; max-width: 1200px; }}
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    /* ── Titre de page ── */
    .page-title {{
        font-size: 1.8rem;
        font-weight: 800;
        color: {ROYAL_LIGHT};
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin-bottom: 6px;
    }}
    .page-subtitle {{
        font-size: 0.88rem;
        font-weight: 400;
        color: {TEXT_SECONDARY};
        line-height: 1.45;
        margin-bottom: 22px;
        padding-bottom: 16px;
        border-bottom: 2px solid {ROYAL_DARK};
    }}

    /* ── Carte metrique ── */
    .kpi-card {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-top: 3px solid {ROYAL};
        border-radius: 6px;
        padding: 18px 20px 14px 20px;
        margin-bottom: 10px;
    }}
    .kpi-label {{
        font-size: 0.7rem;
        font-weight: 600;
        color: {TEXT_SECONDARY};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        line-height: 1.2;
    }}
    .kpi-note {{ font-size: 0.76rem; margin-top: 4px; }}
    .kpi-note.neg {{ color: {C_NEG}; }}
    .kpi-note.pos {{ color: {C_POS}; }}
    .kpi-note.neu {{ color: {C_NEU}; }}

    /* ── Titre de section ── */
    .sec-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {ROYAL_LIGHT};
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }}
    .sec-desc {{
        font-size: 0.8rem;
        font-weight: 400;
        color: {TEXT_SECONDARY};
        line-height: 1.5;
        margin-bottom: 16px;
    }}

    /* ── Encadre Insight ── */
    .insight {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-left: 4px solid {ROYAL};
        border-radius: 0 6px 6px 0;
        padding: 14px 18px;
        margin: 12px 0;
    }}
    .insight-tag {{
        font-size: 0.65rem;
        font-weight: 700;
        color: {ROYAL_LIGHT};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 6px;
    }}
    .insight-body {{
        font-size: 0.86rem;
        color: #C0C4CC;
        line-height: 1.55;
    }}
    .insight-body strong {{
        color: {TEXT_PRIMARY};
        font-weight: 600;
    }}

    /* ── Encadre Alerte ── */
    .alert {{
        background: #1c1215;
        border: 1px solid #2a1a1e;
        border-left: 4px solid {C_NEG};
        border-radius: 0 6px 6px 0;
        padding: 14px 18px;
        margin: 12px 0;
    }}
    .alert.warning {{
        background: #1c1a12;
        border-color: #2a2518;
        border-left-color: {C_NEU};
    }}
    .alert-tag {{
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 6px;
        color: {C_NEG};
    }}
    .alert.warning .alert-tag {{ color: {C_NEU}; }}

    /* ── Zone card ── */
    .zone {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 0 6px 6px 0;
        padding: 14px 18px;
        margin-bottom: 8px;
    }}
    .zone-name {{ font-size: 0.84rem; font-weight: 700; margin-bottom: 5px; }}
    .zone-stats {{ display: flex; gap: 16px; font-size: 0.78rem; color: #B8BCC4; }}
    .zone-stats strong {{ color: {TEXT_PRIMARY}; }}
    .zone-detail {{ font-size: 0.72rem; color: {TEXT_SECONDARY}; margin-top: 5px; }}

    /* ── Utilitaires ── */
    .sep {{ border: none; border-top: 1px solid {CARD_BORDER}; margin: 22px 0; }}

    .fixed-footer {{
        position: fixed; bottom: 0; left: 0; right: 0;
        background: #0C0E12; border-top: 1px solid {CARD_BORDER};
        padding: 8px 0; text-align: center; z-index: 999;
    }}
    .fixed-footer span {{ font-size: 0.68rem; color: #444; font-family: 'Inter', sans-serif; }}
    .bottom-spacer {{ height: 45px; }}

    [data-testid="stSidebar"] {{ border-right: 1px solid {CARD_BORDER}; }}
    [data-testid="stMetric"] {{ background: transparent !important; border: none !important; padding: 0 !important; }}
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def kpi(label, value, note=None, note_type="neu"):
    n = f'<div class="kpi-note {note_type}">{note}</div>' if note else ""
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{n}</div>', unsafe_allow_html=True)

def sec(title, desc=""):
    d = f'<div class="sec-desc">{desc}</div>' if desc else ""
    st.markdown(f'<div class="sec-title">{title}</div>{d}', unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight"><div class="insight-tag">A retenir</div><div class="insight-body">{text}</div></div>', unsafe_allow_html=True)

def alert(text, level="alert"):
    cls = "warning" if level == "warning" else ""
    tag = "Point de vigilance" if level == "warning" else "Signal detecte"
    st.markdown(f'<div class="alert {cls}"><div class="alert-tag">{tag}</div><div class="insight-body">{text}</div></div>', unsafe_allow_html=True)

def apply_style(fig, height=400):
    fig.update_layout(
        height=height, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#B0B4BC", size=12),
        margin=dict(l=40, r=20, t=30, b=40),
        legend=dict(orientation="h", y=-0.15, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#181C24", zerolinecolor="#1F2530"),
        yaxis=dict(gridcolor="#181C24", zerolinecolor="#1F2530"),
        hovermode="x unified",
    )
    return fig

def page_header(title, subtitle):
    st.markdown(
        '<div style="font-size:2rem;font-weight:800;color:#3A7CB8;letter-spacing:-0.03em;margin-top:22px;margin-bottom:6px;">'
        + title
        + '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="font-size:0.88rem;color:#9098A3;margin-bottom:22px;padding-bottom:16px;border-bottom:2px solid #1E3A5F;">'
        + subtitle
        + '</div>',
        unsafe_allow_html=True
    )

def link_to_page(label, target_page):
    """Affiche un lien qui change de page quand on clique."""
    if st.button(label, key=label + "_link_" + target_page, type="tertiary"):
        st.session_state["nav"] = target_page
        st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DONNEES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_data
def get_data():
    return load_data()

try:
    df_raw = get_data()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with st.sidebar:
    st.markdown(f"""
    <div style="padding: 4px 0 16px 0; border-bottom: 2px solid {ROYAL_DARK}; margin-bottom: 16px;">
        <div style="font-size: 1.2rem; font-weight: 800; color: {ROYAL_LIGHT}; letter-spacing: 0.04em;">SENTINEL 360</div>
        <div style="font-size: 0.72rem; color: {TEXT_SECONDARY}; margin-top: 3px; font-weight: 400;">Intelligence mediatique . Benin 2025</div>
    </div>
    """, unsafe_allow_html=True)

    # Initialiser la navigation
    if "nav" not in st.session_state:
        st.session_state["nav"] = "Analyse et recommandations"

    page = st.radio("Navigation",
        ["Analyse et recommandations", "Exploration detaillee"],
        index=["Analyse et recommandations", "Exploration detaillee"].index(st.session_state["nav"]),
        label_visibility="collapsed",
        key="nav_radio")

    # Synchroniser
    st.session_state["nav"] = page


    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-label">Filtres</div>', unsafe_allow_html=True)

    date_min, date_max = get_date_range(df_raw)
    date_range = st.date_input("Periode", value=(date_min, date_max), min_value=date_min, max_value=date_max)
    selected_dates = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (date_min, date_max)

    piliers_sel = st.multiselect("Pilier", sorted(df_raw["pilier"].dropna().unique().tolist()), default=sorted(df_raw["pilier"].dropna().unique().tolist()))
    sentiments_sel = st.multiselect("Sentiment", df_raw["sentiment_proxy"].dropna().unique().tolist(), default=df_raw["sentiment_proxy"].dropna().unique().tolist())

    df = filter_data(df_raw, selected_dates, piliers_sel, sentiments_sel)

    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Evenements selectionnes</div><div class="kpi-value">{len(df):,}</div><div class="kpi-note neu">sur {len(df_raw):,} au total</div></div>'.replace(",", " "), unsafe_allow_html=True)

if page == "Analyse et recommandations":
 
    page_header("Sentinel 360",
                "")
    
    # KPIs
    c3, c4 = st.columns(2)
    avg_tone = df["AvgTone"].mean()
    avg_stab = df["stability_index"].mean()
    pct_neg = (df["sentiment_proxy"].isin(["négatif", "negatif"])).mean() * 100

    with c3: kpi("Ton mediatique moyen", f"{avg_tone:.2f}", "Couverture a dominante negative" if avg_tone < 0 else "Couverture a dominante positive", "neg" if avg_tone < 0 else "pos")
    with c4: kpi("Part de couverture negative", f"{pct_neg:.1f}%", f"Soit {int(pct_neg*len(df)/100)} evenements sur la periode", "neg" if pct_neg > 50 else "neu")

    st.markdown('<hr class="sep">', unsafe_allow_html=True)
 
    # ══════════════════════════════════════════════════════════════════
    # SECTION 1 : CHRONOLOGIE DES CRISES ET LEUR DUREE
    # ══════════════════════════════════════════════════════════════════
 
    sec("Chronologie et duree des crises majeures",
        "Chaque crise est mesuree sur trois dimensions : sa duree dans les medias (en semaines), son intensite (ton minimum atteint) et le temps de retour a la normale.")
 
    crises = analyze_all_crises(df)
 
    if crises:
        for crisis in crises:
            # Couleur selon le type
            if "Securite" in crisis["type"]:
                cr_color = C_NEG
            elif "Politique" in crisis["type"] or "Justice" in crisis["type"]:
                cr_color = C_NEU
            else:
                cr_color = ROYAL_LIGHT
 
            duree = crisis.get("duree_semaines", 0)
            tone_min = crisis.get("tone_minimum", 0)
            tone_avant = crisis.get("tone_avant", 0)
            retour = "Oui" if crisis.get("retour_normal") else "Non a ce jour"
            date_retour = crisis.get("date_retour")
            date_retour_str = date_retour.strftime("%d/%m/%Y") if date_retour else "N/A"
 
            # Gravite visuelle
            if duree >= 4:
                gravite_text = "Crise prolongee"
                gravite_color = C_NEG
            elif duree >= 2:
                gravite_text = "Impact significatif"
                gravite_color = C_NEU
            else:
                gravite_text = "Impact court"
                gravite_color = C_POS
 
            crisis_html = (
                '<div style="background:' + CARD_BG + ';border:1px solid ' + CARD_BORDER
                + ';border-left:4px solid ' + cr_color
                + ';border-radius:0 8px 8px 0;padding:18px 22px;margin-bottom:12px;">'
 
                # Ligne 1 : nom + type
                + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
                + '<div style="font-size:1.05rem;font-weight:700;color:#FFFFFF;">'
                + crisis["nom"] + '</div>'
                + '<div style="background:' + cr_color + '18;border:1px solid ' + cr_color
                + '40;border-radius:4px;padding:3px 10px;font-size:0.65rem;font-weight:600;color:' + cr_color + ';">'
                + crisis["type"] + '</div></div>'
 
                # Ligne 2 : date + description
                + '<div style="font-size:0.8rem;color:' + TEXT_SECONDARY + ';margin-bottom:12px;">'
                + pd.Timestamp(crisis["date"]).strftime("%d %B %Y").replace("January","janvier").replace("February","fevrier").replace("March","mars").replace("April","avril").replace("May","mai").replace("June","juin").replace("July","juillet").replace("August","aout").replace("September","septembre").replace("October","octobre").replace("November","novembre").replace("December","decembre")
                + ' . ' + crisis["description"] + '</div>'
 
                # Ligne 3 : metriques
                + '<div style="display:flex;gap:20px;flex-wrap:wrap;">'
                + '<div style="background:#0E1117;border-radius:6px;padding:10px 14px;min-width:120px;">'
                + '<div style="font-size:0.58rem;color:' + TEXT_SECONDARY + ';text-transform:uppercase;letter-spacing:0.05em;">Duree mediatique</div>'
                + '<div style="font-family:JetBrains Mono,monospace;font-size:1.2rem;font-weight:700;color:' + gravite_color + ';">'
                + str(duree) + ' semaines</div>'
                + '<div style="font-size:0.68rem;color:' + gravite_color + ';">' + gravite_text + '</div></div>'
 
                + '<div style="background:#0E1117;border-radius:6px;padding:10px 14px;min-width:120px;">'
                + '<div style="font-size:0.58rem;color:' + TEXT_SECONDARY + ';text-transform:uppercase;letter-spacing:0.05em;">Ton minimum atteint</div>'
                + '<div style="font-family:JetBrains Mono,monospace;font-size:1.2rem;font-weight:700;color:' + C_NEG + ';">'
                + str(tone_min) + '</div>'
                + '<div style="font-size:0.68rem;color:' + TEXT_SECONDARY + ';">Avant crise : ' + str(tone_avant) + '</div></div>'
 
                + '<div style="background:#0E1117;border-radius:6px;padding:10px 14px;min-width:120px;">'
                + '<div style="font-size:0.58rem;color:' + TEXT_SECONDARY + ';text-transform:uppercase;letter-spacing:0.05em;">Retour a la normale</div>'
                + '<div style="font-size:1rem;font-weight:700;color:' + (C_POS if retour == "Oui" else C_NEG) + ';">'
                + retour + '</div></div>'
 
                + '</div></div>'
            )
            st.markdown(crisis_html, unsafe_allow_html=True)
 
        # Insight duree
        durees = [c["duree_semaines"] for c in crises if c["duree_semaines"] > 0]
        if durees:
            moy_duree = round(sum(durees) / len(durees), 1)
            max_crise = max(crises, key=lambda x: x["duree_semaines"])
            insight(
                "En moyenne, une crise mediatique au Benin dure <strong>" + str(moy_duree)
                + " semaines</strong> dans les medias internationaux. "
                + "La crise la plus longue est « <strong>" + max_crise["nom"] + "</strong> » avec "
                + str(max_crise["duree_semaines"]) + " semaines de couverture negative. "
                + "Ce chiffre est essentiel pour dimensionner les plans de communication de crise."
            )

    # link_to_page("Voir le detail des principaux evenements →", "Exploration detaillee")
 
    st.markdown('<hr class="sep">', unsafe_allow_html=True)
 
    # ══════════════════════════════════════════════════════════════════
    # SECTION 2 : ASYMETRIE POSITIF / NEGATIF
    # ══════════════════════════════════════════════════════════════════
 
    sec("Le desequilibre entre couverture positive et negative",
        "Les evenements negatifs durent-ils plus longtemps dans les medias que les evenements positifs ? Cette asymetrie revele la capacite du pays a se remettre d'une crise mediatique.")
 
    duration_stats = compute_positive_vs_negative_duration(df)
 
    cd1, cd2, cd3 = st.columns(3)
    with cd1:
        kpi("Duree moyenne d'une periode negative",
            str(duration_stats["duree_moy_negative"]) + " sem.",
            str(duration_stats["nb_periodes_negatives"]) + " periodes identifiees",
            "neg")
    with cd2:
        kpi("Duree moyenne d'une periode positive",
            str(duration_stats["duree_moy_positive"]) + " sem.",
            str(duration_stats["nb_periodes_positives"]) + " periodes identifiees",
            "pos")
    with cd3:
        ratio = duration_stats["ratio"]
        kpi("Ratio negatif / positif",
            str(ratio) + "x",
            "Les crises durent " + str(ratio) + " fois plus longtemps" if ratio > 1 else "Equilibre",
            "neg" if ratio > 1.5 else "neu")
 
    if ratio > 1:
        alert(
            "Les periodes de couverture negative durent en moyenne <strong>" + str(ratio)
            + " fois plus longtemps</strong> que les periodes positives. Cela signifie que chaque crise "
            + "laisse une empreinte mediatique durable, tandis que les evenements positifs (comme la "
            + "reconnaissance d'Angelique Kidjo) s'effacent rapidement. Ce desequilibre structurel "
            + "necessite une strategie de communication proactive et soutenue, pas seulement reactive.",
            level="warning"
        )
 
    st.markdown('<hr class="sep">', unsafe_allow_html=True)
 
    # ══════════════════════════════════════════════════════════════════
    # SECTION 3 : CONCENTRATION MEDIATIQUE
    # ══════════════════════════════════════════════════════════════════
 
    sec("Qui controle le recit sur le Benin ?",
        "Analyse de la concentration mediatique : combien de sources produisent l'essentiel de la couverture, et lesquelles sont systematiquement negatives ou positives.")
 
    media_conc = compute_media_concentration(df)
 
    if media_conc:
        cm1, cm2, cm3, cm4 = st.columns(4)
        with cm1:
            kpi("Sources totales", str(media_conc["nb_sources"]))
        with cm2:
            kpi("Top 5 sources", str(media_conc["top5_pct"]) + "% de la couverture", "", "neu")
        with cm3:
            kpi("Sources toujours negatives", str(media_conc["nb_always_negative"]),
                "Ton < -3 en moyenne", "neg")
        with cm4:
            kpi("Sources toujours positives", str(media_conc["nb_always_positive"]),
                "Ton > +1 en moyenne", "pos")
 
        col_neg, col_pos = st.columns(2)
 
        with col_neg:
            sec("Sources systematiquement negatives")
            if media_conc["sources_negatives"]:
                for src, tone, nb in media_conc["sources_negatives"]:
                    st.markdown(
                        '<div style="display:flex;justify-content:space-between;padding:6px 0;'
                        + 'border-bottom:1px solid ' + CARD_BORDER + ';font-size:0.82rem;">'
                        + '<span style="color:#C8C8C8;">' + str(src) + ' <span style="color:' + TEXT_SECONDARY
                        + ';">(' + str(nb) + ' articles)</span></span>'
                        + '<span style="color:' + C_NEG + ';font-family:JetBrains Mono,monospace;font-weight:600;">'
                        + str(tone) + '</span></div>',
                        unsafe_allow_html=True)
 
        with col_pos:
            sec("Sources systematiquement positives")
            if media_conc["sources_positives"]:
                for src, tone, nb in media_conc["sources_positives"]:
                    st.markdown(
                        '<div style="display:flex;justify-content:space-between;padding:6px 0;'
                        + 'border-bottom:1px solid ' + CARD_BORDER + ';font-size:0.82rem;">'
                        + '<span style="color:#C8C8C8;">' + str(src) + ' <span style="color:' + TEXT_SECONDARY
                        + ';">(' + str(nb) + ' articles)</span></span>'
                        + '<span style="color:' + C_POS + ';font-family:JetBrains Mono,monospace;font-weight:600;">'
                        + str(tone) + '</span></div>',
                        unsafe_allow_html=True)
 
        insight(
            "<strong>" + str(media_conc["top5_pct"]) + "% de la couverture</strong> est produite par seulement 5 sources. "
            + "Cela signifie que le recit mondial sur le Benin est controle par une poignee de medias. "
            + "Parmi eux, <strong>" + str(media_conc["nb_always_negative"]) + " sources</strong> sont systematiquement negatives. "
            + "Engager un dialogue editorial avec ces redactions specifiques pourrait avoir un impact "
            + "disproportionne sur la perception globale."
        )
 
    st.markdown('<hr class="sep">', unsafe_allow_html=True)
 
    # ══════════════════════════════════════════════════════════════════
    # SECTION 4 : LE PARADOXE PERCEPTION / REALITE
    # ══════════════════════════════════════════════════════════════════
 
    sec("Le paradoxe perception-realite",
        "Le Benin affiche une croissance economique solide mais subit une perception mediatique negative. Ce decalage constitue un risque pour l'attractivite du pays.")
 
    col_eco, col_media = st.columns(2)
 
    with col_eco:
        st.markdown(
            '<div style="background:#122a1a;border:1px solid #1a3d25;border-radius:8px;padding:20px;margin-bottom:12px;">'
            + '<div style="font-size:0.65rem;color:' + C_POS + ';text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Realite economique (sources : Banque Mondiale, Coface)</div>'
            + '<div style="font-size:2rem;font-weight:800;color:' + C_POS + ';margin-bottom:6px;">+6.4%</div>'
            + '<div style="font-size:0.85rem;color:#B8D4C8;margin-bottom:8px;">Croissance du PIB prevue en 2025</div>'
            + '<div style="font-size:0.78rem;color:#8aaa98;line-height:1.5;">'
            + 'Zone industrielle GDIZ en expansion . Modernisation du port de Cotonou . '
            + 'Eurobond de 500M USD emis en janvier 2025 . Inflation maitrisee a 1.3%'
            + '</div></div>',
            unsafe_allow_html=True
        )
 
    with col_media:
        avg_tone = round(df["AvgTone"].mean(), 2)
        pct_neg = round((df["sentiment_proxy"].isin(["négatif", "negatif"])).mean() * 100)
        pct_secu = round(len(df[df["pilier"] == "securite"]) / len(df) * 100) if len(df) > 0 else 0
 
        st.markdown(
            '<div style="background:#2a1215;border:1px solid #3d1a1e;border-radius:8px;padding:20px;margin-bottom:12px;">'
            + '<div style="font-size:0.65rem;color:' + C_NEG + ';text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Perception mediatique (source : GDELT)</div>'
            + '<div style="font-size:2rem;font-weight:800;color:' + C_NEG + ';margin-bottom:6px;">' + str(avg_tone) + '</div>'
            + '<div style="font-size:0.85rem;color:#d4b8b8;margin-bottom:8px;">Ton mediatique moyen sur 2025</div>'
            + '<div style="font-size:0.78rem;color:#aa8a8a;line-height:1.5;">'
            + str(pct_neg) + '% de couverture negative . '
            + str(pct_secu) + '% des articles sur la securite . '
            + 'Medias internationaux plus negatifs que la presse locale'
            + '</div></div>',
            unsafe_allow_html=True
        )
 
    insight(
        "Le Benin presente un <strong>paradoxe perception-realite</strong> : une economie en croissance "
        + "de 6.4% avec des investissements structurants, mais un ton mediatique moyen de <strong>"
        + str(avg_tone) + "</strong> et " + str(pct_neg) + "% de couverture negative. Ce decalage "
        + "s'explique par la predominance des crises securitaires dans la couverture internationale, "
        + "qui eclipsent les avancees economiques. Pour un investisseur qui ne connait le Benin "
        + "qu'a travers les medias, l'image est trompeuse."
    )
 
    st.markdown('<hr class="sep">', unsafe_allow_html=True)
 
    # ══════════════════════════════════════════════════════════════════
    # SECTION 5 : INSIGHTS ACTIONNABLES
    # ══════════════════════════════════════════════════════════════════
 
    sec("5 insights actionnables pour les decideurs",
        "Ces conclusions sont directement exploitables par un decideur public, un responsable de communication ou un diplomate.")
 
    # Calculs pour les insights
    if "source_type" in df.columns:
        nat = df[df["source_type"].str.contains("national", case=False, na=False)]
        intl = df[~df["source_type"].str.contains("national", case=False, na=False)]
        tone_nat = round(nat["AvgTone"].mean(), 2) if len(nat) > 0 else 0
        tone_intl = round(intl["AvgTone"].mean(), 2) if len(intl) > 0 else 0
        nb_nat_sources = nat["source_domain"].nunique() if "source_domain" in nat.columns else 0
        nb_total_sources = df["source_domain"].nunique() if "source_domain" in df.columns else 1
    else:
        tone_nat, tone_intl, nb_nat_sources, nb_total_sources = 0, 0, 0, 1
 
    insights_data = [
        {
            "numero": "01",
            "titre": "Les crises securitaires captent l'essentiel de l'attention et durent plus longtemps",
            "constat": (
                "Les attaques du JNIM (janvier et avril) et la tentative de coup d'Etat (decembre) "
                "representent les 3 plus gros pics de couverture de l'annee. Chaque crise "
                "dure en moyenne " + str(round(sum(durees)/len(durees), 1)) + " semaines dans les medias, "
                "contre " + str(duration_stats["duree_moy_positive"]) + " semaines pour les evenements positifs."
            ) if durees else "Les crises securitaires dominent la couverture mediatique du Benin.",
            "action": "Mettre en place une cellule de communication de crise pre-positionnee, capable de reagir dans les 24h avec des elements factuels et des porte-paroles identifies.",
            "color": C_NEG,
        },
        {
            "numero": "02",
            "titre": "La voix nationale est marginale dans le recit mondial",
            "constat": (
                "Seulement " + str(nb_nat_sources) + " sources nationales identifiees sur "
                + str(nb_total_sources) + " au total (" + str(round(nb_nat_sources/nb_total_sources*100)) + "%). "
                "L'image du Benin est construite a " + str(100 - round(nb_nat_sources/nb_total_sources*100))
                + "% par des medias etrangers, avec les biais que cela implique."
            ),
            "action": "Accompagner les medias beninois dans leur transition numerique : publication en ligne, referencement international, production multilingue. Objectif : doubler la part des sources nationales en 2 ans.",
            "color": C_NEU,
        },
        {
            "numero": "03",
            "titre": "Les medias internationaux sont significativement plus negatifs",
            "constat": (
                "Le ton moyen des sources internationales (" + str(tone_intl) + ") est "
                + str(round(abs(tone_intl - tone_nat), 2)) + " points en dessous des sources nationales ("
                + str(tone_nat) + "). Ce biais porte principalement sur les sujets de securite."
            ),
            "action": "Identifier les 5 redactions internationales les plus negatives et engager un dialogue editorial : communiques proactifs, invitations de correspondants, donnees economiques positives.",
            "color": C_NEG,
        },
        {
            "numero": "04",
            "titre": "Le paradoxe croissance-perception menace l'attractivite",
            "constat": (
                "Le Benin affiche 6.4% de croissance, une zone industrielle en expansion et un Eurobond "
                "de 500M USD reussi. Pourtant, " + str(pct_neg) + "% de la couverture est negative. "
                "Un investisseur qui decouvre le Benin via les medias internationaux a une image deformee."
            ),
            "action": "Lancer une campagne d'image « Benin : the untold story » ciblee sur les medias economiques internationaux (FT, Bloomberg, Jeune Afrique), mettant en avant les indicateurs de croissance et les projets structurants.",
            "color": C_NEU,
        },
        {
            "numero": "05",
            "titre": "Un systeme d'alerte precoce est possible et necessaire",
            "constat": (
                "Notre analyse montre que les crises sont detectables des les premieres heures "
                "par le volume et le ton des articles. Le systeme Sentinel 360 identifie les anomalies "
                "automatiquement. Deploye en temps reel, il permettrait de reagir avant le pic mediatique."
            ),
            "action": "Deployer Sentinel 360 comme outil de veille permanente au sein de la cellule de communication gouvernementale. Cout : quasi nul (donnees GDELT gratuites, infrastructure cloud legere).",
            "color": ROYAL_LIGHT,
        },
    ]
 
    for ins in insights_data:
        st.markdown(
            '<div style="background:' + CARD_BG + ';border:1px solid ' + CARD_BORDER
            + ';border-radius:8px;padding:20px 24px;margin-bottom:14px;">'
 
            # Numero + titre
            + '<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">'
            + '<div style="background:' + ins["color"] + '18;border:1px solid ' + ins["color"]
            + '40;border-radius:6px;width:38px;height:38px;display:flex;align-items:center;justify-content:center;'
            + 'font-family:JetBrains Mono,monospace;font-size:0.85rem;font-weight:700;color:' + ins["color"] + ';">'
            + ins["numero"] + '</div>'
            + '<div style="font-size:1rem;font-weight:700;color:#FFFFFF;flex:1;">' + ins["titre"] + '</div>'
            + '</div>'
 
            # Constat
            + '<div style="font-size:0.84rem;color:#B0B4BC;line-height:1.6;margin-bottom:12px;">'
            + ins["constat"] + '</div>'
 
            # Action recommandee
            + '<div style="background:#0E1117;border-radius:6px;padding:12px 16px;">'
            + '<div style="font-size:0.6rem;color:' + ROYAL_LIGHT + ';text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Action recommandee</div>'
            + '<div style="font-size:0.82rem;color:#C8CCD4;line-height:1.5;">' + ins["action"] + '</div>'
            + '</div>'
 
            + '</div>',
            unsafe_allow_html=True
        )

elif page == "Exploration detaillee":

    page_header("Exploration detaillee",
                "Explorez les donnees GDELT sur le Benin en profondeur : signaux temporels, acteurs, medias et geographie.")

    tab1, tab2, tab3, tab4 = st.tabs(["Securite territoriale", "Dynamique d'influence", "Focus medias", "Principaux evenements"])

    with tab2:

        # =========================
        # FILTRAGE DES ACTEURS
        # =========================

        BAD_ACTORS = {
        # Pays
        "BENIN", "GHANA", "NIGERIA", "FRANCE",
        "TOGO", "BURKINA FASO", "MALI",
        "UNITED STATES", "CHINA", "RUSSIA",
        }

        # On nettoie les données
        filtered_df = df.copy()

        filtered_df = filtered_df[
            (filtered_df["Actor1Name"].notna()) &
            (~filtered_df["Actor1Name"].str.upper().isin(BAD_ACTORS))
        ]

        # =========================
        # PRINCIPAUX ACTEURS
        # =========================
        # ── Ligne 1 : Top acteurs + Paires bilaterales cote a cote ──
        cl, cr = st.columns(2)

        with cl:
            sec(
                "Principales organisations identifiées",
                "Les 5 organisations ou groupes apparaissant le plus souvent comme initiateurs d'événements."
            )

            ta = (
                filtered_df["Actor1Name"]
                .value_counts()
                .head(5)
                .reset_index()
            )

            ta.columns = ["Acteur", "N"]

            fig_a = px.bar(
                ta,
                x="N",
                y="Acteur",
                orientation="h",
                color_discrete_sequence=[ROYAL_LIGHT]
            )

            apply_style(fig_a, 350)

            fig_a.update_layout(
                yaxis=dict(
                    autorange="reversed",
                    title=""
                ),
                xaxis_title="Nombre d'événements"
            )

            st.plotly_chart(fig_a, width='stretch')


        # =========================
        # RELATIONS BILATÉRALES
        # =========================

        with cr:
            sec(
                "Relations bilatérales les plus fréquentes",
                "Les 5 interactions les plus fréquentes entre organisations ou groupes. La couleur indique la nature de la relation."
            )

            # On filtre aussi les relations contenant des pays/génériques
            filtered_pairs_df = filtered_df[
                (filtered_df["Actor2Name"].notna()) &
                (~filtered_df["Actor2Name"].str.upper().isin(BAD_ACTORS))
            ]

            pairs = compute_actor_interactions(
                filtered_pairs_df,
                min_count=3
            )

            if len(pairs) > 0:

                pt = pairs.head(5).copy()

                pt["paire"] = (
                    pt["Actor1Name"]
                    + "  >  "
                    + pt["Actor2Name"]
                )

                pt["nature"] = pt["tone_moyen"].apply(
                    lambda x:
                        "Relation tendue" if x < -2
                        else (
                            "Coopération" if x > 2
                            else "Relation neutre"
                        )
                )

                fig_pr = px.bar(
                    pt,
                    x="interactions",
                    y="paire",
                    orientation="h",
                    color="nature",
                    color_discrete_map={
                        "Relation tendue": C_NEG,
                        "Relation neutre": C_NEU,
                        "Coopération": C_POS
                    },
                    hover_data={
                        "tone_moyen": ":.2f",
                        "pct_conflit": ":.1f"
                    },
                    labels={
                        "interactions": "Interactions",
                        "paire": ""
                    }
                )

                apply_style(fig_pr, 350)

                fig_pr.update_layout(
                    yaxis=dict(autorange="reversed"),
                    legend=dict(title="")
                )

                st.plotly_chart(fig_pr, width='stretch')

        st.markdown('<hr class="sep">', unsafe_allow_html=True)

        # ── Ligne 3 : Pays etrangers ──
        sec("Géopolitique Béninoise", "Pays etrangers apparaissant comme acteurs dans les evenements lies au Benin.")
        ac = pd.concat([df["Actor1CountryCode"].dropna(), df["Actor2CountryCode"].dropna()])
        fg = ac[~ac.isin(["BEN", ""])].value_counts().head(10).reset_index()
        fg.columns = ["Pays", "Mentions"]
        fig_f = px.bar(fg, x="Pays", y="Mentions", color_discrete_sequence=[GOLD])
        apply_style(fig_f, 300)
        fig_f.update_layout(xaxis_title="Code pays", yaxis_title="Nombre de mentions")
        st.plotly_chart(fig_f, width='stretch')
        if len(fg) > 0:
            top_pays = fg.iloc[0]
            insight(
                "Le pays tiers le plus present dans la couverture du Benin est <strong>"
                + str(top_pays["Pays"]) + "</strong> avec <strong>"
                + str(top_pays["Mentions"]) + " mentions</strong>. "
                + "Cela traduit un interet geopolitique marque de ce pays pour le Benin, "
                + "que ce soit en termes de cooperation economique, de securite ou de relations diplomatiques."
            )

    with tab1 :

        sec("Repartition geographique de l'attention", "Le Benin est decoupe en quatre macro-zones (Littoral, Sud, Centre, Nord). La carte localise chaque evenement ; le tableau a droite synthetise le niveau de tension par zone.")
        cm, cz = st.columns([3,2])

        with cm:
            df_geo = df[df["ActionGeo_Lat"].notna() & df["ActionGeo_Long"].notna()].copy()
            if len(df_geo) > 0:
                dm = df_geo.head(5000)
                fig_mp = px.scatter_map(dm, lat="ActionGeo_Lat", lon="ActionGeo_Long", color="macro_zone", color_discrete_map=ZONE_COLORS,
                    hover_name="ActionGeo_FullName", hover_data={"pilier":True,"AvgTone":":.2f","event_date":True,"Actor1Name":True,"ActionGeo_Lat":False,"ActionGeo_Long":False,"macro_zone":False},
                    zoom=5.5, center={"lat":9.3,"lon":2.3}, map_style="carto-darkmatter", labels={"macro_zone":"Zone"}, category_orders={"macro_zone":ZONE_ORDER})
                fig_mp.update_traces(marker=dict(size=6,opacity=0.7))
                fig_mp.update_layout(height=480, margin=dict(l=0,r=0,t=0,b=0), legend=dict(orientation="h",y=-0.02,font=dict(size=10),bgcolor="rgba(0,0,0,0.5)"))
                st.plotly_chart(fig_mp, width='stretch')
            else:
                st.warning("Aucun evenement geolocalise disponible avec les filtres actuels.")

        with cz:
            sec("Indicateurs par zone")
            zs = compute_zone_stats(df)
            if len(zs) > 0:
                zs["order"] = zs["macro_zone"].map({z:i for i,z in enumerate(ZONE_ORDER)})
                zs = zs.sort_values("order")
                for _, row in zs.iterrows():
                    zone = row["macro_zone"]
                    color = ZONE_COLORS.get(zone, "#888")
                    if row["pct_conflit"]>40: tension,tc = "Eleve","#E74C3C"
                    elif row["pct_conflit"]>25: tension,tc = "Modere","#F39C12"
                    else: tension,tc = "Faible","#2ECC71"
                    st.markdown(f'''<div class="zone" style="border-left:4px solid {color};"><div class="zone-name" style="color:{color};">{zone}</div><div class="zone-stats"><span><strong>{int(row["nb_events"])}</strong> evt</span><span>Ton : <strong>{row["tone_moyen"]:.1f}</strong></span><span style="color:{tc};">Tension : <strong>{tension}</strong></span></div><div class="zone-detail">{row["pct_conflit"]:.0f}% conflictuel . {row["pct_negatif"]:.0f}% negatif . Stabilite : {row["stability_moyen"]:.0f}/100</div></div>''', unsafe_allow_html=True)

        mt_row = zs.loc[zs["pct_conflit"].idxmax()]
        ms_row = zs.loc[zs["pct_conflit"].idxmin()]
        insight(f"La zone <strong>{mt_row['macro_zone']}</strong> concentre le plus de tensions avec <strong>{mt_row['pct_conflit']:.0f}%</strong> d'evenements conflictuels et un ton moyen de {mt_row['tone_moyen']:.1f}. A l'inverse, <strong>{ms_row['macro_zone']}</strong> presente le profil le plus stable ({ms_row['pct_conflit']:.0f}% conflictuel ; indice de stabilite a {ms_row['stability_moyen']:.0f}/100).")

        st.markdown('<hr class="sep">', unsafe_allow_html=True)

        sec("Evolution du ton mediatique par zone geographique", "Cette courbe permet de suivre la trajectoire de chaque zone au fil des mois. Un passage sous la barre du zero indique une couverture a dominante negative pour la zone concernee.")
        zm = df[df["macro_zone"]!="Non localisé"].groupby(["mois","macro_zone"]).agg(tone_moyen=("AvgTone","mean")).reset_index()
        fig_ze = px.line(zm, x="mois", y="tone_moyen", color="macro_zone", color_discrete_map=ZONE_COLORS,
            labels={"tone_moyen":"Ton moyen","mois":"","macro_zone":"Zone"}, category_orders={"macro_zone":ZONE_ORDER}, markers=True)
        fig_ze.add_hline(y=0, line_dash="dot", line_color="#444")
        apply_style(fig_ze, 340)
        fig_ze.update_layout(legend=dict(orientation="h",y=-0.2,title=""))
        st.plotly_chart(fig_ze, width='stretch')
    
    with tab3:

        sec("Repartition thematique", "Part relative de chaque pilier dans la couverture mediatique du Benin.")
        pc = df["pilier"].value_counts().reset_index(); pc.columns=["pilier","count"]
        fig_p = px.pie(pc, values="count", names="pilier", color="pilier", color_discrete_map=PILIER_COLORS, hole=0.45)
        apply_style(fig_p, 350)
        fig_p.update_layout(legend=dict(orientation="h",y=-0.1), margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig_p, width='stretch')

        sb = compute_source_bias(df)
        if len(sb) > 0:
            st.markdown('<hr class="sep">', unsafe_allow_html=True)
            sec("Repartition thematique selon le type de source", "La presse internationale et la presse nationale couvrent-elles les memes sujets ? Un desequilibre revele un biais editorial : si les sources etrangeres se concentrent sur la securite, elles donnent une image deformee du pays.")
            fig_sb = px.bar(sb, x="source_type", y="nb_events", color="pilier", barmode="group",
                color_discrete_map=PILIER_COLORS,
                labels={"nb_events":"Evenements","source_type":"","pilier":"Pilier"})
            apply_style(fig_sb, 300)
            st.plotly_chart(fig_sb, width='stretch')

        st.markdown('<hr class="sep">', unsafe_allow_html=True)

        
        sec("Ecart de perception : presse nationale contre internationale", "Le ton moyen des articles est compare selon l'origine du media. Un ecart significatif revele un biais de couverture.")
        if "source_type" in df.columns:
            bias = df.groupby("source_type").agg(tone_moyen=("AvgTone","mean"), nb=("GLOBALEVENTID","count")).reset_index()
            fig_bi = go.Figure()
            for _, row in bias.iterrows():
                c = C_POS if row["tone_moyen"]>0 else C_NEG
                fig_bi.add_trace(go.Bar(x=[row["source_type"]], y=[row["tone_moyen"]], marker_color=c, text=f"{row['tone_moyen']:.2f}", textposition="outside", showlegend=False))
            fig_bi.add_hline(y=0, line_color="#333", line_dash="dot")
            apply_style(fig_bi, 340)
            fig_bi.update_layout(xaxis_title="", yaxis_title="Ton moyen")
            st.plotly_chart(fig_bi, width='stretch')
            if len(bias) >= 2:
                nat = bias[bias["source_type"].str.contains("national",case=False,na=False)]
                intl = bias[~bias["source_type"].str.contains("national",case=False,na=False)]
                if len(nat)>0 and len(intl)>0:
                    diff = abs(intl.iloc[0]["tone_moyen"]-nat.iloc[0]["tone_moyen"])
                    if diff > 0.5:
                        d = "plus negative" if intl.iloc[0]["tone_moyen"]<nat.iloc[0]["tone_moyen"] else "plus positive"
                        insight(f"Un ecart de <strong>{diff:.2f} points</strong> separe les sources internationales des sources nationales : la couverture etrangere est {d}. Ce biais peut affecter la perception du Benin aupres des investisseurs et des partenaires internationaux.")
        else:
            st.info("La classification des sources n'est pas disponible dans les donnees.")

    with tab4 :

        alert_feed = compute_alert_feed(df, top_n=10)

        # section sentiment
        sec("Evolution du sentiment dans le temps", "Proportion mensuelle des ressentis sur les événéments couverts. Une hausse durable de la part negative (zone rouge du graphique) constitue un signal de degradation de l'image.")
        ms = df.groupby(["mois","sentiment_proxy"]).size().reset_index(name="count")
        mt = ms.groupby("mois")["count"].transform("sum")
        ms["pct"] = (ms["count"]/mt*100).round(1)
        fig_s = px.bar(ms, x="mois", y="pct", color="sentiment_proxy", color_discrete_map=SENTIMENT_COLORS, labels={"pct":"Part (%)","mois":"","sentiment_proxy":"Sentiment"}, barmode="stack")
        
        # Calculer le % negatif par mois pour la ligne de tendance
        neg_trend = ms[ms["sentiment_proxy"].isin(["négatif", "negatif"])].copy()
        if len(neg_trend) > 0:
            neg_trend = neg_trend.sort_values("mois")
            fig_s.add_trace(go.Scatter(
                x=neg_trend["mois"],
                y=neg_trend["pct"],
                name="Tendance couverture negative",
                line=dict(color="#FFFFFF", width=3),
                mode="lines+markers",
                marker=dict(size=7, symbol="diamond"),
            ))

        apply_style(fig_s, 320)
        fig_s.update_layout(legend=dict(orientation="h",y=-0.18,title=""))
        st.plotly_chart(fig_s, width='stretch')

        if len(neg_trend) >= 2:
            first_neg = neg_trend.iloc[0]["pct"]
            last_neg = neg_trend.iloc[-1]["pct"]
            diff = last_neg - first_neg
            if diff > 3:
                alert(
                    "La part de couverture negative est passee de <strong>" + f"{first_neg:.0f}%" + "</strong> a <strong>"
                    + f"{last_neg:.0f}%" + "</strong> entre " + neg_trend.iloc[0]["mois"] + " et " + neg_trend.iloc[-1]["mois"]
                    + ". Cette tendance haussiere signale une degradation de l'image mediatique du Benin.",
                    level="warning"
                )
            elif diff < -3:
                insight(
                    "La part de couverture negative a recule de <strong>" + f"{first_neg:.0f}%" + "</strong> a <strong>"
                    + f"{last_neg:.0f}%" + "</strong> entre " + neg_trend.iloc[0]["mois"] + " et " + neg_trend.iloc[-1]["mois"]
                    + ". Cette amelioration progressive est un signal positif pour l'image du Benin."
                )
            else:
                insight(
                    "La part de couverture negative est restee stable autour de <strong>" + f"{last_neg:.0f}%" + "</strong> sur la periode. "
                    + "Pas de degradation notable, mais pas d'amelioration non plus."
                )

        st.markdown('<hr class="sep">', unsafe_allow_html=True)

        # ── Anomalies ──
        sec("Detection des periodes inhabituelles",
            "Le graphique ci-dessous represente le volume d'evenements par semaine. Les barres orange et rouges signalent les semaines dont l'activite depasse significativement la normale (Z-Score superieur a 2). La courbe blanche materialise la tendance de fond sur 4 semaines.")

        
        weekly = compute_weekly_zscore(df)
        fig1 = go.Figure()
        for _, row in weekly[weekly["alerte"] != "Normal"].iterrows():
            c = "rgba(231,76,60,0.12)" if row["alerte"] == "Alerte" else "rgba(243,156,18,0.10)"
            fig1.add_vrect(x0=row["semaine"]-pd.Timedelta(days=3), x1=row["semaine"]+pd.Timedelta(days=3), fillcolor=c, line_width=0, layer="below")

        bar_colors = []
        for _, row in weekly.iterrows():
            if row["alerte"] == "Alerte": bar_colors.append(C_NEG)
            elif row["alerte"] == "Vigilance": bar_colors.append(C_NEU)
            elif row["alerte"] == "Creux inhabituel": bar_colors.append("#4A5060")
            else: bar_colors.append(ROYAL_LIGHT)

        fig1.add_trace(go.Bar(x=weekly["semaine"], y=weekly["volume"], name="Volume hebdomadaire", marker_color=bar_colors, opacity=0.85))
        fig1.add_trace(go.Scatter(x=weekly["semaine"], y=weekly["volume_ma4"], name="Tendance (moy. mobile 4 sem.)", line=dict(color="#FFF", width=2, dash="dot"), mode="lines"))
        apply_style(fig1, 400)
        fig1.update_layout(yaxis_title="Nombre d'evenements")
        st.plotly_chart(fig1, width='stretch')
        st.markdown('<hr class="sep">', unsafe_allow_html=True)


        if len(alert_feed) > 0:

            # KPIs du Principaux evenements
            ca1, ca2, ca3 = st.columns(3)
            nb_alertes = len(alert_feed[alert_feed["alerte"] == "Alerte"])
            nb_vigilances = len(alert_feed[alert_feed["alerte"] == "Vigilance"])

            with ca1: kpi("Periodes detectees", str(len(alert_feed)))
            with ca2: kpi("Alertes fortes", str(nb_alertes), "Z-Score superieur a 3" if nb_alertes > 0 else "Aucune", "neg" if nb_alertes > 0 else "pos")
            with ca3: kpi("Points de vigilance", str(nb_vigilances), "Z-Score entre 2 et 3" if nb_vigilances > 0 else "Aucun", "neu" if nb_vigilances > 0 else "pos")

            st.markdown('<hr class="sep">', unsafe_allow_html=True)

            sec("Chronologie des periodes inhabituelles", "Chaque fiche correspond a une semaine dont le volume d'evenements depasse significativement la moyenne. Les informations contextuelles sont extraites automatiquement des donnees GDELT.")

            # Afficher chaque alerte comme une fiche
        
            for i, row in alert_feed.iterrows():

                if row["alerte"] == "Alerte":
                    border_color = C_NEG
                    badge_bg = "#2a1215"
                    badge_color = C_NEG
                    badge_text = "ALERTE"
                elif row["alerte"] == "Vigilance":
                    border_color = C_NEU
                    badge_bg = "#2a2212"
                    badge_color = C_NEU
                    badge_text = "VIGILANCE"
                else:
                    border_color = ROYAL_LIGHT
                    badge_bg = "#12202a"
                    badge_color = ROYAL_LIGHT
                    badge_text = "SIGNAL"

                analysis = analyze_peak_complete(df, row["semaine"])
                if analysis is None:
                    continue

                theme = analysis["theme"].get("theme", "Activite mediatique")
                secondary = analysis["theme"].get("secondary", [])
                theme_display = theme + " / " + secondary[0] if secondary else theme
                peak_day = analysis.get("peak_day")
                summary = analysis.get("summary", "")
                articles = analysis.get("articles", [])
                ctx = analysis.get("context", {})
                topics = analysis.get("topics", [])
                cause_title = analysis.get("cause_title", "")
                cause = analysis.get("cause", "")

                sem_date = row["semaine"].strftime("%d/%m/%Y")
                tone_val = ctx.get("tone_moyen", 0)
                tone_color = C_NEG if tone_val < -2 else (C_POS if tone_val > 2 else C_NEU)
                pct_c = ctx.get("pct_conflit", 0)

                

                # ══════════════════════════════════════════════════
                # BLOC 1 : EN-TETE AVEC PIC MIS EN AVANT
                # ══════════════════════════════════════════════════

                # Si on a le jour du pic, il devient le titre principal
                if peak_day:
                    peak_str = peak_day["date"].strftime("%d/%m/%Y")
                    peak_vol = str(peak_day["volume"])
                    peak_pct = str(peak_day["pct_du_total"])

                    header_html = (
                        '<div style="background:' + CARD_BG + ';border:1px solid ' + CARD_BORDER
                        + ';border-left:4px solid ' + border_color
                        + ';border-radius:0 8px 8px 0;padding:20px 24px;margin-bottom:4px;">'

                        # Ligne 1 : badge alerte a droite
                        + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
                        + '<span style="font-size:0.75rem;color:' + TEXT_SECONDARY + ';">Semaine du ' + sem_date + '</span>'
                        + '<div style="background:' + badge_bg + ';border:1px solid ' + border_color
                        + ';border-radius:4px;padding:3px 10px;font-size:0.62rem;font-weight:700;color:' + badge_color
                        + ';letter-spacing:0.08em;">' + badge_text + '</div>'
                        + '</div>'

                        # Ligne 2 : date du pic en GRAND
                        + '<div style="font-size:1.6rem;font-weight:800;color:#FFFFFF;margin-bottom:4px;">'
                        + peak_str + '</div>'
                        + '<div style="font-size:0.82rem;color:' + TEXT_SECONDARY + ';margin-bottom:14px;">'
                        + peak_vol + ' evenements ce jour-la (' + peak_pct + '% de la semaine)'
                        + '</div>'
                    )
                else:
                    header_html = (
                        '<div style="background:' + CARD_BG + ';border:1px solid ' + CARD_BORDER
                        + ';border-left:4px solid ' + border_color
                        + ';border-radius:0 8px 8px 0;padding:20px 24px;margin-bottom:4px;">'
                        + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">'
                        + '<span style="font-size:1.2rem;font-weight:700;color:#FFFFFF;">Semaine du ' + sem_date + '</span>'
                        + '<div style="background:' + badge_bg + ';border:1px solid ' + border_color
                        + ';border-radius:4px;padding:3px 10px;font-size:0.62rem;font-weight:700;color:' + badge_color
                        + ';letter-spacing:0.08em;">' + badge_text + '</div></div>'
                    )

                # Theme badge
                header_html += (
                    '<div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">'
                    + '<div style="background:' + border_color + '18;border:1px solid ' + border_color
                    + '40;border-radius:4px;padding:4px 12px;">'
                    + '<span style="font-size:0.78rem;font-weight:600;color:' + border_color + ';">' + theme_display + '</span>'
                    + '</div></div>'
                )

                # Metriques
                header_html += (
                    '<div style="display:flex;gap:28px;flex-wrap:wrap;">'
                    + '<div><div style="font-size:0.58rem;color:' + TEXT_SECONDARY + ';text-transform:uppercase;letter-spacing:0.05em;">Volume total</div>'
                    + '<div style="font-family:JetBrains Mono,monospace;font-size:1.1rem;font-weight:700;color:#FFFFFF;">'
                    + str(ctx.get("nb_events", 0)) + '</div></div>'
                    + '<div><div style="font-size:0.58rem;color:' + TEXT_SECONDARY + ';text-transform:uppercase;letter-spacing:0.05em;">Ton moyen</div>'
                    + '<div style="font-family:JetBrains Mono,monospace;font-size:1.1rem;font-weight:700;color:' + tone_color + ';">'
                    + str(tone_val) + '</div></div>'
                    + '<div><div style="font-size:0.58rem;color:' + TEXT_SECONDARY + ';text-transform:uppercase;letter-spacing:0.05em;">Conflit</div>'
                    + '<div style="font-family:JetBrains Mono,monospace;font-size:1.1rem;font-weight:700;color:'
                    + (C_NEG if pct_c > 40 else C_NEU) + ';">' + str(pct_c) + '%</div></div>'
                    + '</div></div>'
                )
                st.markdown(header_html, unsafe_allow_html=True)

                # ══════════════════════════════════════════════════
                # BLOC 2 : CAUSE AVEC TITRE + TOPICS
                # ══════════════════════════════════════════════════

                if cause_title or cause:
                    cause_html = (
                        '<div style="background:#0f1520;border:1px solid #1a2540;border-left:4px solid '
                        + C_NEU + ';border-radius:0 6px 6px 0;padding:16px 20px;margin-bottom:4px;">'
                    )

                    # Titre synthetique
                    if cause_title:
                        cause_html += (
                            '<div style="font-size:1rem;font-weight:700;color:#FFFFFF;margin-bottom:8px;">'
                            + cause_title + '</div>'
                        )

                    # Texte explicatif
                    if cause:
                        cause_html += (
                            '<div style="font-size:0.84rem;color:#B8BCC4;line-height:1.6;margin-bottom:10px;">'
                            + cause + '</div>'
                        )

                    # Topics en liste
                    if topics:
                        cause_html += (
                            '<div style="font-size:0.72rem;color:' + TEXT_SECONDARY
                            + ';margin-bottom:6px;">Les discussions portent principalement sur :</div>'
                            + '<div style="display:flex;flex-wrap:wrap;gap:6px;">'
                        )
                        for topic in topics:
                            cause_html += (
                                '<span style="background:#1a2540;border:1px solid #2a3560;border-radius:4px;'
                                + 'padding:3px 10px;font-size:0.76rem;color:#a0b4d0;">' + topic + '</span>'
                            )
                        cause_html += '</div>'

                    cause_html += '</div>'
                    st.markdown(cause_html, unsafe_allow_html=True)

                # ══════════════════════════════════════════════════
                # BLOC 3 : RESUME ANALYTIQUE (facteurs)
                # ══════════════════════════════════════════════════

                factors = []
                if "top_types" in ctx and len(ctx["top_types"]) > 0:
                    type_items = [t[0] + " (" + str(t[2]) + "%)" for t in ctx["top_types"][:3]]
                    factors.append(("Types d'evenements", " . ".join(type_items)))
                if "top_actors" in ctx and len(ctx["top_actors"]) > 0:
                    actor_items = [a[0] for a in ctx["top_actors"][:3]]
                    factors.append(("Acteurs principaux", " . ".join(actor_items)))
                if "top_lieux" in ctx and len(ctx["top_lieux"]) > 0:
                    lieu_items = [l[0] + " (" + str(l[1]) + ")" for l in ctx["top_lieux"][:3]]
                    factors.append(("Lieux", " . ".join(lieu_items)))
                if "top_sources" in ctx and len(ctx["top_sources"]) > 0:
                    src_items = [s[0] for s in ctx["top_sources"][:3]]
                    factors.append(("Medias principaux", " . ".join(src_items)))

                if factors:
                    factors_html = (
                        '<div style="background:#0a1628;border:1px solid #1a3050;border-radius:6px;'
                        + 'padding:14px 18px;margin-bottom:4px;">'
                        + '<div style="font-size:0.62rem;font-weight:700;color:' + ROYAL_LIGHT
                        + ';text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Facteurs dominants</div>'
                    )
                    for label, value in factors:
                        factors_html += (
                            '<div style="display:flex;gap:8px;margin-bottom:5px;font-size:0.78rem;">'
                            + '<span style="color:' + TEXT_SECONDARY + ';min-width:150px;">' + label + ' :</span>'
                            + '<span style="color:#B8BCC4;">' + value + '</span></div>'
                        )
                    factors_html += '</div>'
                    st.markdown(factors_html, unsafe_allow_html=True)

                # ══════════════════════════════════════════════════
                # BLOC 4 : ARTICLES MAJEURS (sans le ton)
                # ══════════════════════════════════════════════════

                if articles:
                    articles_html = (
                        '<div style="background:#080e1a;border:1px solid #1a2540;border-radius:0 0 8px 8px;'
                        + 'padding:14px 18px;margin-bottom:24px;">'
                        + '<div style="font-size:0.62rem;font-weight:700;color:' + ROYAL_LIGHT
                        + ';text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Articles identifies</div>'
                    )

                    for evt in articles[:4]:
                        titre = evt.get("titre", "")
                        nb = evt.get("nb_articles", 1)

                        articles_html += (
                            '<div style="margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid #1a2540;">'
                            + '<div style="font-size:0.86rem;font-weight:600;color:#E0E0E0;margin-bottom:5px;">'
                            + titre + '</div>'
                            + '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
                            + '<span style="font-size:0.7rem;color:' + TEXT_SECONDARY + ';">'
                            + str(nb) + ' source(s)</span>'
                        )

                        for src in evt.get("sources", [])[:4]:
                            source_name = src.get("source", "")
                            url = src.get("url", "")
                            lang = src.get("langue", "")
                            lang_badge = "FR" if lang == "francais" else ("EN" if lang == "anglais" else "")
                            lang_color = "#4a90d9" if lang_badge == "FR" else "#d9a04a"

                            if url:
                                articles_html += (
                                    '<a href="' + url + '" target="_blank" style="text-decoration:none;">'
                                    + '<span style="background:#111827;border:1px solid #2a3550;border-radius:4px;'
                                    + 'padding:2px 7px;font-size:0.68rem;color:#8ab4f0;">'
                                    + source_name
                                )
                                if lang_badge:
                                    articles_html += ' <span style="color:' + lang_color + ';font-weight:600;">' + lang_badge + '</span>'
                                articles_html += '</span></a>'

                        articles_html += '</div></div>'

                    articles_html += '</div>'
                    st.markdown(articles_html, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

        else:
            insight("Aucune periode anormale n'a ete detectee avec les filtres actuels. La couverture mediatique du Benin est restee dans les limites habituelles sur toute la plage selectionnee.")

    
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FOOTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown('<div class="bottom-spacer"></div>', unsafe_allow_html=True)
st.markdown('<div class="fixed-footer"><span>SENTINEL 360 . Hackathon GDELT x Benin 2025 . Donnees : GDELT Project</span></div>', unsafe_allow_html=True)