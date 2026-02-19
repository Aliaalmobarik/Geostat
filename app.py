# -*- coding: utf-8 -*-
"""
🔥 WILDFIRE INSIGHTS PACA - PREMIUM WOW 🔥
Analyse Complète Spatiale & Temporelle
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from modules.data_processing import (
    load_data, classify_fires, analyze_fires_before_big_fire,
    analyze_parameter_trends, analyze_global_parameter_correlations
)
from modules.visualizations import (
    create_map, create_pie_chart, create_line_chart,
    create_temporal_series, create_multi_fire_comparison,
    create_communes_croissance_map, create_parameter_trends_chart,
    create_global_parameter_correlation_chart, create_correlation_summary_table,
    PARAM_NAMES
)
from modules.export import export_results, export_csv

# ========== CONFIGURATION PAGE ==========
st.set_page_config(
    page_title="🔥 WILDFIRE INSIGHTS PACA",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CSS LIGHT ACADEMIC - PALETTE ORANGE + MARRON ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@300;400;600;700;800&display=swap');

:root {
    --primary: #D87A2D;
    --secondary: #8B6B4F;
    --danger: #C4661A;
    --success: #7A8F58;
    --bg-main: #F9F5EE;
    --bg-soft: #FFFDF9;
    --text-main: #3F2F23;
    --text-muted: #6E5A49;
    --card-bg: rgba(255, 252, 246, 0.92);
}

/* Fond clair et professionnel */
html, body, [class*="stApp"] {
    background: linear-gradient(145deg, #F9F5EE 0%, #FFF9F1 45%, #F5EEE4 100%) !important;
    background-attachment: fixed !important;
    font-family: 'Poppins', sans-serif !important;
    color: var(--text-main) !important;
}

/* Titres */
h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 3.2rem !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #8B6B4F 0%, #D87A2D 55%, #C4661A 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    text-shadow: 0 1px 1px rgba(139, 107, 79, 0.18) !important;
    padding: 1.4rem 0 !important;
    letter-spacing: 1px !important;
    text-align: center !important;
}

h2 {
    font-family: 'Playfair Display', serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #8B6B4F, #D87A2D) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    border-left: 4px solid #D87A2D !important;
    padding-left: 1rem !important;
    margin-top: 2rem !important;
}

h3 {
    color: #C4661A !important;
    font-weight: 700 !important;
    text-shadow: none !important;
}

/* KPI Cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(255, 253, 249, 0.98), rgba(249, 242, 231, 0.96)) !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid rgba(216, 122, 45, 0.28) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    box-shadow: 0 4px 14px rgba(139, 107, 79, 0.1) !important;
    transition: all 0.25s ease !important;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 18px rgba(139, 107, 79, 0.16) !important;
    border-color: rgba(216, 122, 45, 0.45) !important;
}

[data-testid="stMetricValue"] {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #8B6B4F, #D87A2D) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

[data-testid="stMetricLabel"] {
    color: #6E5A49 !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
}

/* Boutons */
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #A97F5A, #D87A2D) !important;
    color: #FFFFFF !important;
    border: 2px solid transparent !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.6rem !important;
    font-size: 1rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 6px 16px rgba(196, 102, 26, 0.2) !important;
    text-transform: none !important;
    letter-spacing: 0.3px !important;
}

.stButton>button:hover, .stDownloadButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(196, 102, 26, 0.28) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255, 250, 243, 0.95) 0%, rgba(248, 241, 231, 0.98) 100%) !important;
    backdrop-filter: blur(8px) !important;
    border-right: 1px solid rgba(216, 122, 45, 0.22) !important;
}

[data-testid="stSidebar"] label {
    color: #C4661A !important;
    font-weight: 700 !important;
    text-shadow: none !important;
}

/* Dataframes */
.dataframe {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(216, 122, 45, 0.2) !important;
    border-radius: 12px !important;
}

.dataframe thead tr {
    background: linear-gradient(90deg, rgba(216, 122, 45, 0.18), rgba(169, 127, 90, 0.12)) !important;
    border-bottom: 2px solid rgba(216, 122, 45, 0.35) !important;
}

.dataframe thead th {
    color: #A97F5A !important;
    font-weight: 800 !important;
    padding: 1rem !important;
}

.dataframe tbody tr {
    border-bottom: 1px solid rgba(216, 122, 45, 0.12) !important;
    color: #8B6B4F !important;
}

.dataframe tbody tr:hover {
    background: rgba(216, 122, 45, 0.08) !important;
}

.dataframe td {
    color: #8B6B4F !important;
    font-weight: 600 !important;
    padding: 0.85rem !important;
}

/* Messages d'alerte */
.stSuccess {
    background: rgba(122, 143, 88, 0.14) !important;
    border: 1px solid #7A8F58 !important;
    border-radius: 12px !important;
    color: #3F2F23 !important;
    font-weight: 700 !important;
}

.stInfo {
    background: rgba(216, 122, 45, 0.12) !important;
    border: 1px solid #D87A2D !important;
    border-radius: 12px !important;
    color: #3F2F23 !important;
    font-weight: 700 !important;
}

.stWarning {
    background: rgba(196, 102, 26, 0.13) !important;
    border: 1px solid #C4661A !important;
    border-radius: 12px !important;
    color: #3F2F23 !important;
    font-weight: 700 !important;
}

.stError {
    background: rgba(196, 102, 26, 0.17) !important;
    border: 1px solid #C4661A !important;
    border-radius: 12px !important;
    color: #4E2A12 !important;
    font-weight: 700 !important;
}

/* Sélecteurs & Inputs */
.stSelectbox [data-testid="baseButton-secondary"] {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(216, 122, 45, 0.3) !important;
    color: #6E5A49 !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}

.stSelectbox [data-testid="baseButton-secondary"]:hover {
    border-color: rgba(196, 102, 26, 0.6) !important;
    background: rgba(216, 122, 45, 0.08) !important;
}

input[type="number"], input[type="text"] {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(216, 122, 45, 0.3) !important;
    color: #6E5A49 !important;
    border-radius: 10px !important;
}

input[type="number"]:focus, input[type="text"]:focus {
    border-color: rgba(196, 102, 26, 0.6) !important;
    box-shadow: 0 0 0 2px rgba(216, 122, 45, 0.18) !important;
}

hr {
    border: 1px solid rgba(216, 122, 45, 0.22) !important;
}

.stMarkdown p,
.stMarkdown li,
.stMarkdown div,
.stCaption,
label,
span {
    color: var(--text-main) !important;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: var(--text-main) !important;
}

[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
    background: rgba(255, 248, 238, 0.95) !important;
    border: 1px solid rgba(160, 130, 109, 0.55) !important;
    color: #A0826D !important;
}

[data-testid="stSidebar"] .stNumberInput button,
[data-testid="stSidebar"] div[data-baseweb="input"] button,
[data-testid="stSidebar"] button[aria-label*="Increment"],
[data-testid="stSidebar"] button[aria-label*="Decrement"] {
    background-color: rgba(255, 248, 238, 0.95) !important;
    border: 1px solid rgba(160, 130, 109, 0.55) !important;
    color: #A0826D !important;
    opacity: 1 !important;
    min-width: 34px !important;
    min-height: 34px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative !important;
    z-index: 2 !important;
}

[data-testid="stSidebar"] .stNumberInput button:not(:disabled),
[data-testid="stSidebar"] div[data-baseweb="input"] button:not(:disabled),
[data-testid="stSidebar"] button[aria-label*="Increment"]:not(:disabled),
[data-testid="stSidebar"] button[aria-label*="Decrement"]:not(:disabled) {
    pointer-events: auto !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] [data-testid="stNumberInput"] button:hover {
    background: rgba(255, 242, 224, 0.95) !important;
    border-color: rgba(160, 130, 109, 0.8) !important;
    color: #A0826D !important;
}

[data-testid="stSidebar"] .stNumberInput button:hover,
[data-testid="stSidebar"] div[data-baseweb="input"] button:hover,
[data-testid="stSidebar"] button[aria-label*="Increment"]:hover,
[data-testid="stSidebar"] button[aria-label*="Decrement"]:hover {
    background-color: rgba(255, 242, 224, 0.95) !important;
    border-color: rgba(160, 130, 109, 0.8) !important;
    color: #A0826D !important;
}

[data-testid="stSidebar"] button[aria-label*="Increment"] svg,
[data-testid="stSidebar"] button[aria-label*="Decrement"] svg {
    fill: currentColor !important;
    color: currentColor !important;
}

[data-testid="stSidebar"] button[aria-label*="Increment"] svg *,
[data-testid="stSidebar"] button[aria-label*="Decrement"] svg * {
    fill: currentColor !important;
    stroke: currentColor !important;
}

[data-testid="stSidebar"] .stNumberInput button:disabled,
[data-testid="stSidebar"] div[data-baseweb="input"] button:disabled,
[data-testid="stSidebar"] button[aria-label*="Increment"]:disabled,
[data-testid="stSidebar"] button[aria-label*="Decrement"]:disabled {
    background-color: rgba(247, 239, 228, 1) !important;
    border-color: rgba(160, 130, 109, 0.7) !important;
    color: #A0826D !important;
    -webkit-text-fill-color: #A0826D !important;
    opacity: 1 !important;
    pointer-events: none !important;
    cursor: not-allowed !important;
}

[data-testid="stSidebar"] .stNumberInput button:disabled svg,
[data-testid="stSidebar"] .stNumberInput button:disabled svg *,
[data-testid="stSidebar"] div[data-baseweb="input"] button:disabled svg,
[data-testid="stSidebar"] div[data-baseweb="input"] button:disabled svg *,
[data-testid="stSidebar"] button[aria-label*="Increment"]:disabled svg,
[data-testid="stSidebar"] button[aria-label*="Increment"]:disabled svg *,
[data-testid="stSidebar"] button[aria-label*="Decrement"]:disabled svg,
[data-testid="stSidebar"] button[aria-label*="Decrement"]:disabled svg * {
    fill: #A0826D !important;
    stroke: #A0826D !important;
    color: #A0826D !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] .stNumberInput button span,
[data-testid="stSidebar"] .stNumberInput button:disabled span,
[data-testid="stSidebar"] div[data-baseweb="input"] button span,
[data-testid="stSidebar"] div[data-baseweb="input"] button:disabled span {
    color: #A0826D !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] input[type="number"] {
    color: #8B6B4F !important;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="element-container"] {
    animation: slideIn 0.6s ease-out !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* --- Fix pour rendre les boutons +/- cliquables dans la sidebar --- */

/* Assure que le conteneur n'auto-masque pas les boutons */
[data-testid="stSidebar"] .stNumberInput,
[data-testid="stSidebar"] div[data-baseweb="input"] {
    overflow: visible !important;
}

/* Force les boutons +/- à être visibles, à avoir une taille raisonnable,
   et à accepter les clics (pointer-events) ; z-index élevé pour être au-dessus */
[data-testid="stSidebar"] .stNumberInput button,
[data-testid="stSidebar"] div[data-baseweb="input"] button,
[data-testid="stSidebar"] button[aria-label*="Increment"],
[data-testid="stSidebar"] button[aria-label*="Decrement"] {
    position: relative !important;
    z-index: 9999 !important;
    pointer-events: auto !important;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Si un pseudo-élément recouvre (rare), ignore ses événements */
[data-testid="stSidebar"] .stNumberInput *::before,
[data-testid="stSidebar"] .stNumberInput *::after {
    pointer-events: none !important;
}
</style>
""", unsafe_allow_html=True)
# ========== FONCTION APPLY THEME ==========
def apply_premium_theme(fig):
    """Applique le thème PREMIUM WOW aux graphes"""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255, 253, 249, 0.98)",
        plot_bgcolor="rgba(255, 251, 245, 0.95)",
        font=dict(family="Poppins, sans-serif", color="#3F2F23", size=12),
        title_font=dict(size=16, color="#C4661A"),
        xaxis=dict(
            gridcolor="rgba(139, 107, 79, 0.12)", 
            linecolor="rgba(139, 107, 79, 0.35)", 
            showgrid=True, 
            zeroline=False,
            title_font=dict(color="#3F2F23", size=14),  # Titre axe X
            tickfont=dict(color="#3F2F23", size=11)     # Valeurs axe X
        ),
        yaxis=dict(
            gridcolor="rgba(139, 107, 79, 0.12)", 
            linecolor="rgba(139, 107, 79, 0.35)", 
            showgrid=True, 
            zeroline=False,
            title_font=dict(color="#3F2F23", size=14),  # Titre axe Y
            tickfont=dict(color="#3F2F23", size=11)     # Valeurs axe Y
        ),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255, 247, 235, 0.85)",
            bordercolor="rgba(216, 122, 45, 0.25)",
            borderwidth=1,
            font=dict(color="#3F2F23"),
            title=dict(font=dict(color="#3F2F23"))
        ),
        hovermode='closest',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    fig.update_xaxes(title_font=dict(color="#3F2F23", size=14), tickfont=dict(color="#3F2F23", size=11))
    fig.update_yaxes(title_font=dict(color="#3F2F23", size=14), tickfont=dict(color="#3F2F23", size=11))
    return fig

# ========== CACHE DATA LOADING ==========
@st.cache_data
def load_csv_data():
    """Load CSV data with caching"""
    try:
        csv_path = Path(__file__).parent / 'data' / 'promothee' / 'incendies_paca_2015_2022.csv'
        df = load_data(str(csv_path))
        return df
    except Exception as e:
        st.error(f"❌ Erreur de chargement: {e}")
        return pd.DataFrame()

# ========== MAIN APPLICATION ==========
def main():
    # Titre spectaculaire
    st.markdown("""
    <div style='text-align: center; margin-bottom: 1rem;'>
        <h1>🔥 WILDFIRE INSIGHTS PACA 🔥</h1>
        <p style='color: #FF8C42; font-size: 1.3rem; text-shadow: 0 0 15px rgba(255, 140, 66, 0.4);'>
            ⚡ Analyse Complète Spatiale & Temporelle ⚡
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Charger données
    df = load_csv_data()
    
    if df.empty or len(df) == 0:
        st.error("❌ Aucune donnée trouvée. Vérifiez que le fichier CSV existe.")
        return
    
    # ========== SIDEBAR PARAMÈTRES ==========
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(180deg, rgba(255, 140, 66, 0.1), rgba(160, 130, 109, 0.1)); 
                    backdrop-filter: blur(15px); border-radius: 20px; padding: 1.5rem; 
                    border: 2px solid rgba(255, 140, 66, 0.3);'>
            <h3>⚙️ PARAMÈTRES</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📅 Période")
        annee_min = int(df['annee'].min())
        annee_max = int(df['annee'].max())
        annee_debut = st.number_input("Début", min_value=annee_min, max_value=annee_max, value=annee_min)
        annee_fin = st.number_input("Fin", min_value=annee_min, max_value=annee_max, value=annee_max)
        
        st.subheader("🔥 Classification")
        seuil_petit = st.number_input("Petit feu < (ha)", min_value=0.1, value=1.0, step=0.1)
        seuil_grand = st.number_input("Grand feu ≥ (ha)", min_value=0.1, value=10.0, step=0.5)
        
        st.subheader("📍 Analyse")
        buffer_radius = st.slider("Rayon buffer (km)", 1, 100, 10)
        temporal_window = st.slider("Fenêtre (jours)", 7, 180, 30)
        min_fires_before = st.slider("Min. petits feux", 0, 20, 3)
    
    # Filtrer données
    df_filtered = df[(df['annee'] >= annee_debut) & (df['annee'] <= annee_fin)].copy()
    df_filtered = classify_fires(df_filtered, seuil_petit, seuil_grand)
    
    # ========== KPI DASHBOARD ==========
    st.markdown("""<div style='height: 2rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>📊 TABLEAU DE BORD - Indicateurs Clés</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    kpi_cols = st.columns(4, gap="medium")
    total_fires = len(df_filtered)
    petits = len(df_filtered[df_filtered['categorie'] == 'Petit feu'])
    moyens = len(df_filtered[df_filtered['categorie'] == 'Feu moyen'])
    grands = len(df_filtered[df_filtered['categorie'] == 'Grand feu'])
    
    with kpi_cols[0]:
        st.metric("🔥 TOTAL INCENDIES", total_fires)
    with kpi_cols[1]:
        st.metric("🌱 PETITS FEUX", petits)
    with kpi_cols[2]:
        st.metric("📈 FEUX MOYENS", moyens)
    with kpi_cols[3]:
        st.metric("⚠️ GRANDS FEUX", grands)
    
    st.markdown("""<hr style='border: 2px solid rgba(255, 140, 66, 0.2); margin: 2rem 0;' />""", unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(255, 140, 66, 0.2), rgba(160, 130, 109, 0.15)); 
                backdrop-filter: blur(20px); border-radius: 20px; padding: 1.8rem; 
                border: 2px solid rgba(255, 140, 66, 0.4);
                box-shadow: 0 8px 32px rgba(255, 140, 66, 0.15);'>
        <h3 style='margin-top: 0; margin-bottom: 1rem; color: #FF8C42;'>📊 MÉTHODOLOGIE ANALYTIQUE</h3>
        <p style='margin: 0.8rem 0; color: #F5E6D3; font-size: 1rem;'><b>⏰ Critère Temporel</b> : Fenêtre avant l'événement</p>
        <p style='margin: 0.8rem 0; color: #F5E6D3; font-size: 1rem;'><b>📍 Critère Spatial</b> : Buffer de rayon spécifié autour de la zone</p>
        <p style='margin: 0.8rem 0; color: #F5E6D3; font-size: 1rem;'><b>📊 Critère Quantitatif</b> : Nombre minimum de précurseurs détectés</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    # ========== PRÉPARATION DONNÉES ==========
    big_fires = df_filtered[(df_filtered['categorie'] == 'Grand feu') & (df_filtered['date_alerte'].notna())].copy()
    big_fires = big_fires.drop_duplicates(subset=['commune', 'date_alerte', 'x', 'y', 'surface_ha'], keep='first').reset_index(drop=True)
    
    analysis_results = []
    if len(big_fires) > 0:
        with st.spinner('Analyse en cours...'):
            for _, big_fire in big_fires.iterrows():
                result = analyze_fires_before_big_fire(df_filtered, big_fire, temporal_window, buffer_radius, min_fires_before)
                analysis_results.append(result)
    
    valid_count = sum(1 for r in analysis_results if r['condition_met'])
    
    if len(big_fires) == 0:
        st.warning("⚠️ Aucun grand feu trouvé dans la période")
        return
    
    if valid_count == 0:
        st.warning("⚠️ Aucun grand feu ne répond aux critères")
        return
    
    # ========== DISTRIBUTION & CARTE PREMIUM ==========
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>🗺️ ANALYSE SPATIALE & DISTRIBUTION</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    # Deux graphes côte à côte
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(255, 140, 66, 0.08), rgba(160, 130, 109, 0.06));
                backdrop-filter: blur(14px);
                border-radius: 16px;
                padding: 0.8rem 1rem;
                border: 2px solid rgba(255, 140, 66, 0.22);
                display: flex;
                align-items: center;
                justify-content: center;
                height: 72px;
                text-align: center;'>
        <h3 style='margin: 0; font-size: 1.05rem; color: #FF8C42; font-weight: 800;'>📊 Distribution des Sinistres</h3>
        </div>
        """, unsafe_allow_html=True)
        fig_pie = create_pie_chart(df_filtered)
        fig_pie = apply_premium_theme(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")

    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(255, 140, 66, 0.08), rgba(160, 130, 109, 0.06));
                backdrop-filter: blur(14px);
                border-radius: 16px;
                padding: 0.8rem 1rem;
                border: 2px solid rgba(255, 140, 66, 0.22);
                display: flex;
                align-items: center;
                justify-content: center;
                height: 72px;
                text-align: center;'>
        <h3 style='margin: 0; font-size: 1.05rem; color: #FF8C42; font-weight: 800;'>📈 Évolution Annuelle</h3>
        </div>
    """, unsafe_allow_html=True)
        fig_line = create_line_chart(df_filtered)
        fig_line = apply_premium_theme(fig_line)
        st.plotly_chart(fig_line, use_container_width=True, key="line_chart")
    # Carte sur ligne seule
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(255, 140, 66, 0.08), rgba(160, 130, 109, 0.06));
                backdrop-filter: blur(14px);
                border-radius: 16px;
                padding: 0.8rem 1rem;
                border: 2px solid rgba(255, 140, 66, 0.22);
                display: flex;
                align-items: center;
                height: 72px;
                '>
        <h3 style='margin: 0; font-size: 1.5rem; color: #FF8C42; font-weight: 800;'>🗺️ Localisation Géographique Interactive</h3>
    </div>
    """, unsafe_allow_html=True)
    
    fig_map = create_map(df_filtered, big_fires, analysis_results, buffer_radius)
    fig_map.update_layout(title_text="Carte des Incendies PACA", title_font_size=17, title_font_color="#FFD699")
    fig_map = apply_premium_theme(fig_map)
    st.plotly_chart(fig_map, use_container_width=True, key="map_chart", height=600)
    
    # ========== ÉVOLUTION TEMPORELLE ==========
    st.markdown("""
    <h2>⏳ ÉVOLUTION TEMPORELLE</h2>
    """, unsafe_allow_html=True)
    
    valid_indices = [i for i, r in enumerate(analysis_results) if r.get('condition_met')]
    if len(valid_indices) > 0:
        options = [
            f"{big_fires.iloc[i]['commune']} — {big_fires.iloc[i]['date_alerte'].strftime('%d/%m/%Y')} ({analysis_results[i]['small_fires_count']} petits feux)"
            for i in valid_indices
        ]
        sel = st.selectbox("🔥 Choisir un grand feu à analyser", options=options, key='select_fire_temporal')
        actual_idx = valid_indices[options.index(sel)]
        selected_result = analysis_results[actual_idx]
        selected_fire = big_fires.iloc[actual_idx]
        
        if 'small_fires' in selected_result and len(selected_result['small_fires']) > 0:
            small_fires_temp = selected_result['small_fires'].copy()
            small_fires_temp['date_only'] = small_fires_temp['date_alerte'].dt.date
            daily_counts = small_fires_temp.groupby('date_only').size().reset_index(name='Nombre')
            daily_counts['date_only'] = pd.to_datetime(daily_counts['date_only'])
            
            # ===== SECTION 1 : TENDANCES DES PARAMÈTRES ENVIRONNEMENTAUX =====
            st.markdown("##### Tendances des Paramètres Environnementaux")
            st.caption("Analyse de l'évolution des conditions environnementales durant les petits incendies")
            
            # Analyser les tendances
            df_trends, trends_summary = analyze_parameter_trends(small_fires_temp)
            
            if len(df_trends) > 0 and len(trends_summary) > 0:
                # Graphique des tendances
                fig_params = create_parameter_trends_chart(
                    df_trends, 
                    trends_summary, 
                    selected_fire['commune']
                )
                fig_params = apply_premium_theme(fig_params)
                fig_params.update_layout(margin=dict(l=30, r=30, t=155, b=45), height=510)
                st.plotly_chart(fig_params, use_container_width=True)
                
                # Tableau récapitulatif des tendances
                st.markdown("##### Tableau Récapitulatif des Tendances")
                
                # Préparer les données du tableau
                tableau_data = []
                for param, stats in trends_summary.items():
                    friendly_name = PARAM_NAMES.get(param, param)
                    tableau_data.append({
                        'Paramètre': friendly_name,
                        'Direction': stats['direction'],
                        'Variation (%)': f"{stats['variation_pct']:+.2f}%"
                    })
                
                df_tableau = pd.DataFrame(tableau_data)
                
                # Appliquer un style au tableau
                def color_direction(val):
                    if val == 'Croissance':
                        return 'background-color: #d4edda; color: #155724; font-weight: bold'
                    elif val == 'Décroissance':
                        return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                    elif val == 'Stable':
                        return 'background-color: #d1ecf1; color: #0c5460; font-weight: bold'
                    else:
                        return 'background-color: #e2e3e5; color: #383d41'
                
                styled_df = df_tableau.style.applymap(
                    color_direction, 
                    subset=['Direction']
                )
                
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                # Informations complémentaires
                st.caption(
                    "**Interprétation** : "
                    "Variation (%) = changement entre la première et dernière période"
                )
            else:
                st.warning("⚠️ Données insuffisantes pour analyser les tendances des paramètres")
            
            # ===== SECTION 2 : GRAPHE TEMPOREL =====
            st.markdown("---")
            st.markdown("##### Accumulation Temporelle des Incendies")
            
            # Métriques clés avec delta pour la tendance - AU-DESSUS DU GRAPHE
            st.markdown("##### Statistiques du Grand Feu")
            metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
            with metric_col1:
                st.metric("Petits feux", selected_result['small_fires_count'])
            with metric_col2:
                st.metric("Moyens feux", selected_result['medium_fires_count'])
            with metric_col3:
                total = selected_result['small_fires_count'] + selected_result['medium_fires_count']
                st.metric("Total feux avant", total)
            with metric_col4:
                st.metric("Surface grand feu", f"{selected_fire['surface_ha']:.1f} ha")
            with metric_col5:
                tendance = selected_result['trend']
                st.metric("Tendance", tendance)
            
            # Graphe temporel avec tendance et département dans le titre
            departement = str(selected_fire.get('depart', 'Inconnu'))
            fig_time = create_temporal_series(
                daily_counts, 
                selected_fire['date_alerte'], 
                selected_fire['commune'],
                tendance=tendance,
                departement=departement
            )
            fig_time = apply_premium_theme(fig_time)
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("Aucun petit feu dans la fenêtre temporelle")
    
    # ========== COMMUNES À TENDANCE CROISSANTE ==========
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>📈 COMMUNES À TENDANCE CROISSANTE</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    if st.button("🌲 ANALYSER LES COMMUNES À RISQUE", use_container_width=True):
        communes_croissance = []
        for idx, res in enumerate(analysis_results):
            if res.get('condition_met') and res.get('trend') == 'Croissance':
                bf = big_fires.iloc[idx]
                communes_croissance.append({
                    'Commune': bf['commune'],
                    'Date': bf['date_alerte'].strftime('%d/%m/%Y'),
                    'Petits feux': res['small_fires_count'],
                    'Moyens feux': res['medium_fires_count'],
                    'Total': res['small_fires_count'] + res['medium_fires_count'],
                })
        
        if communes_croissance:
            st.success(f"✅ {len(communes_croissance)} commune(s) avec tendance croissante")
            df_c = pd.DataFrame(communes_croissance).sort_values('Total', ascending=True)
            
            # Deux graphes côte à côte
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(255, 140, 66, 0.08), rgba(160, 130, 109, 0.06));
                backdrop-filter: blur(14px);
                border-radius: 16px;
                padding: 0.8rem 1rem;
                border: 2px solid rgba(255, 140, 66, 0.22);
                display: flex;
                align-items: center;
                justify-content: center;
                height: 72px;
                text-align: center;'>
        <h3 style='margin: 0; font-size: 1.05rem; color: #FF8C42; font-weight: 800;'>📊 Répartition par Commune</h3>
                </div>
                """, unsafe_allow_html=True)
                fig = go.Figure()
                labels = [f"{r['Commune']}<br>{r['Date']}" for _, r in df_c.iterrows()]
                fig.add_trace(go.Bar(y=labels, x=df_c['Petits feux'], name='Petits feux', marker_color='#A0826D', orientation='h'))
                fig.add_trace(go.Bar(y=labels, x=df_c['Moyens feux'], name='Moyens feux', marker_color='#FF8C42', orientation='h'))
                fig.update_layout(barmode='stack', xaxis_title='Nombre de feux', height=max(400, len(df_c) * 45), margin=dict(l=200, r=50, t=50, b=50))
                fig = apply_premium_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(255, 140, 66, 0.08), rgba(160, 130, 109, 0.06));
                backdrop-filter: blur(14px);
                border-radius: 16px;
                padding: 0.8rem 1rem;
                border: 2px solid rgba(255, 140, 66, 0.22);
                display: flex;
                align-items: center;
                justify-content: center;
                height: 72px;
                text-align: center;'>
        <h3 style='margin: 0; font-size: 1.05rem; color: #FF8C42; font-weight: 800;'>🔥 Proportion Petits vs Moyens</h3>
                </div>
                """, unsafe_allow_html=True)
                total_petits = int(df_c['Petits feux'].sum())
                total_moyens = int(df_c['Moyens feux'].sum())
                pie = go.Figure()
                pie.add_trace(go.Pie(labels=['🌱 Petits feux', '🔥 Moyens feux'], values=[total_petits, total_moyens], 
                                     marker_colors=['#A0826D', '#FF8C42'], textinfo='label+percent+value',
                                     textposition='inside', hovertemplate='<b>%{label}</b><br>Nombre: %{value}<br>Pourcentage: %{percent}'))
                pie.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50))
                pie = apply_premium_theme(pie)
                st.plotly_chart(pie, use_container_width=True)
            
            # Carte sur ligne complète
            st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(255, 140, 66, 0.08), rgba(160, 130, 109, 0.06));
                backdrop-filter: blur(14px);
                border-radius: 16px;
                padding: 0.8rem 1rem;
                border: 2px solid rgba(255, 140, 66, 0.22);
                display: flex;
                align-items: center;
                height: 72px;
                '>
        <h3 style='margin: 0; font-size: 1.5rem; color: #FF8C42; font-weight: 800;'>🗺️ Localisation des Communes à Risque</h3>
            </div>
            """, unsafe_allow_html=True)
            fig_map = create_communes_croissance_map(big_fires, analysis_results)
            fig_map.update_layout(title_text="Communes à Tendance Croissante", title_font_size=14, margin=dict(l=50, r=50, t=80, b=50))
            fig_map = apply_premium_theme(fig_map)
            st.plotly_chart(fig_map, use_container_width=True, height=600)
            
            st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("📍 Communes", len(df_c))
            with m2:
                st.metric("🌱 Petits feux", total_petits)
            with m3:
                st.metric("🔥 Moyens feux", total_moyens)
            with m4:
                st.metric("⚠️ Total", total_petits + total_moyens)
        else:
            st.info("ℹ️ Aucune commune avec tendance croissante")
    
    # ========== ANALYSE COMPARATIVE ==========
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>📊 ANALYSE COMPARATIVE</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    fig_comp = create_multi_fire_comparison(analysis_results, big_fires, temporal_window, nb_feux=10, show_moyenne=False, show_variance=False)
    fig_comp = apply_premium_theme(fig_comp)
    st.plotly_chart(fig_comp, use_container_width=True)
    
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    # ===== DÉPARTEMENT FILTER FOR CORRELATIONS =====
    st.markdown("""
    <h2>🔗 ANALYSES DE CORRÉLATION</h2>
    """, unsafe_allow_html=True)
    
    st.caption("Filtrez les analyses de corrélation par département pour des résultats plus précis")
    
    departements_disponibles = sorted(df['depart'].dropna().astype(str).unique())
    departements_options = ["Tous"] + list(departements_disponibles)
    
    selected_dept = st.selectbox(
        "Sélectionnez un département",
        options=departements_options,
        index=0,
        key='dept_correlation_filter'
    )
    
    # Filtrer les données par département
    if selected_dept != "Tous":
        df_filtered_dept = df_filtered[df_filtered['depart'].astype(str) == str(selected_dept)].copy()
        big_fires_dept = big_fires[big_fires['depart'].astype(str) == str(selected_dept)].copy()
        st.info(f"🔍 Filtre actif: Département {selected_dept}")
    else:
        df_filtered_dept = df_filtered
        big_fires_dept = big_fires
    
    st.markdown("---")
    
    # ========== CORRÉLATIONS ==========
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>🔗 ANALYSES DE CORRÉLATION</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    # ========== CORRÉLATIONS ==========
    st.markdown("""<h3 style='border-bottom: 3px solid rgba(255, 140, 66, 0.4); padding-bottom: 1rem; margin-bottom: 1.5rem;'>📋 Tableau Récapitulatif des Corrélations</h3>""", unsafe_allow_html=True)
    try:
        summary_df = create_correlation_summary_table(df_filtered_dept)
        
        # Appliquer un style au tableau
        def color_interpretation(val):
            if '🟢' in str(val):
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif '🟡' in str(val):
                return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            elif '🔵' in str(val):
                return 'background-color: #d1ecf1; color: #0c5460; font-weight: bold'
            elif '⚪' in str(val):
                return 'background-color: #e2e3e5; color: #383d41; font-weight: bold'
            return ''
        
        styled_df = summary_df.style.applymap(color_interpretation, subset=['Interprétation'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(f"⚠️ Corrélations indisponibles: {e}")
    
    st.markdown("---")
    
    st.markdown("""<h3 style='border-bottom: 3px solid rgba(255, 140, 66, 0.4); padding-bottom: 1rem; margin-bottom: 1.5rem;'>📈 Corrélations Paramètres → Grands Feux</h3>""", unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    global_param_corr = analyze_global_parameter_correlations(analysis_results, big_fires)
    if global_param_corr and any(c['status'] == 'OK' for c in global_param_corr.values()):
        fig_global = create_global_parameter_correlation_chart(global_param_corr)
        fig_global = apply_premium_theme(fig_global)
        fig_global.update_layout(margin=dict(l=20, r=20, t=150, b=20))
        st.plotly_chart(fig_global, use_container_width=True)
        
        # Tableau détaillé
        st.markdown("##### Tableau Détaillé des Corrélations Paramétriques")
        
        corr_table_data = []
        for param, corr_data in global_param_corr.items():
            if corr_data['status'] == 'OK':
                friendly_name = PARAM_NAMES.get(param, param)
                
                max_corr = max(
                    abs(corr_data['pearson']),
                    abs(corr_data['spearman']),
                    abs(corr_data['mutual_info'])
                )
                
                if max_corr >= 0.7:
                    interpretation = "🟢 Forte"
                elif max_corr >= 0.4:
                    interpretation = "🟡 Modérée"
                elif max_corr >= 0.2:
                    interpretation = "🔵 Faible"
                else:
                    interpretation = "⚪ Très faible"
                
                pearson_sig = "✓" if corr_data['pearson_pval'] < 0.05 else "✗"
                spearman_sig = "✓" if corr_data['spearman_pval'] < 0.05 else "✗"
                
                corr_table_data.append({
                    'Paramètre': friendly_name,
                    'Pearson': f"{corr_data['pearson']:.3f} ({pearson_sig})",
                    'Spearman': f"{corr_data['spearman']:.3f} ({spearman_sig})",
                    'Info. Mutuelle': f"{corr_data['mutual_info']:.3f}",
                    'Moyenne': f"{corr_data['mean_value']:.2f}",
                    'N échantillons': corr_data['n_samples'],
                    'Interprétation': interpretation
                })
        
        df_global_corr_table = pd.DataFrame(corr_table_data)
        
        def color_correlation(val):
            try:
                num_str = val.split('(')[0].strip() if '(' in val else val
                num_val = float(num_str)
                if abs(num_val) >= 0.7:
                    return 'background-color: #d4edda; color: #155724; font-weight: bold'
                elif abs(num_val) >= 0.4:
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold'
                elif abs(num_val) >= 0.2:
                    return 'background-color: #d1ecf1; color: #0c5460'
                else:
                    return ''
            except:
                return ''
        
        def color_interpretation_table(val):
            if "🟢 Forte" in val:
                return 'background-color: #d4edda; color: #155724; font-weight: bold; font-size: 1.1em'
            elif "🟡 Modérée" in val:
                return 'background-color: #fff3cd; color: #856404; font-weight: bold; font-size: 1.1em'
            elif "🔵 Faible" in val:
                return 'background-color: #d1ecf1; color: #0c5460; font-weight: bold; font-size: 1.1em'
            else:
                return 'background-color: #e2e3e5; color: #383d41; font-size: 1.1em'
        
        styled_global_corr = df_global_corr_table.style.applymap(
            color_correlation,
            subset=['Pearson', 'Spearman', 'Info. Mutuelle']
        ).applymap(
            color_interpretation_table,
            subset=['Interprétation']
        )
        
        st.dataframe(styled_global_corr, use_container_width=True, hide_index=True)
        
        st.caption(
            "**Légende** : "
            "**Pearson/Spearman** : ✓ = significatif (p < 0.05), ✗ = non significatif | "
            "**Info. Mutuelle** : quantification de l'information partagée | "
            "**N échantillons** : nombre de grands feux analysés"
        )
    else:
        st.info("ℹ️ Données insuffisantes pour corrélations")
    
    # ========== EXPORT ==========
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>💾 EXPORT DES DONNÉES</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(255, 140, 66, 0.15), rgba(160, 130, 109, 0.12)); 
                    backdrop-filter: blur(15px); border-radius: 15px; padding: 1.5rem; 
                    border: 2px solid rgba(255, 140, 66, 0.3);'>
            <h3 style='margin-top: 0;'>📊 Excel Complet</h3>
            <p style='color: #F5E6D3; margin: 0.8rem 0;'><b>5 feuilles complètes :</b></p>
            <ul style='color: #F5E6D3; margin: 1rem 0;'>
                <li>🔥 <b>Grands Feux</b> - Liste détaillée</li>
                <li>📊 <b>Analyses</b> - Résultats complets</li>
                <li>📍 <b>Buffers</b> - Zones d'influence</li>
                <li>🔗 <b>Corrélations</b> - Données paramétriques</li>
                <li>📖 <b>Explications</b> - Guide de lecture</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("� GÉNÉRER & TÉLÉCHARGER EXCEL", use_container_width=True, key="btn_excel_gen"):
            try:
                summary = create_correlation_summary_table(df_filtered)
            except:
                summary = None
            excel_data = export_results(big_fires, analysis_results, summary)
            st.download_button(
                "⬇️ Télécharger Excel (5 feuilles)",
                excel_data,
                f"wildfire_paca_complet_{annee_debut}_{annee_fin}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_excel"
            )
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(210, 107, 30, 0.15), rgba(160, 130, 109, 0.12)); 
                    backdrop-filter: blur(15px); border-radius: 15px; padding: 1.5rem; 
                    border: 2px solid rgba(210, 107, 30, 0.3);'>
            <h3 style='margin-top: 0;'>📑 Fichiers CSV Simples</h3>
            <p style='color: #F5E6D3; margin: 0.8rem 0;'><b>2 extractions rapides :</b></p>
            <ul style='color: #F5E6D3; margin: 1rem 0;'>
                <li>🌍 <b>Données Filtrées</b> - Par période sélectionnée</li>
                <li>✓ <b>Résultats Analyse</b> - Tableau récapitulatif</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        csv = export_csv(df_filtered)
        st.download_button(
            "⬇️ CSV - Données Filtrées",
            csv,
            f"incendies_filtres_{annee_debut}_{annee_fin}.csv",
            "text/csv",
            use_container_width=True,
            key="dl_csv_filtered"
        )
        
        st.markdown("""<div style='height: 0.5rem;'></div>""", unsafe_allow_html=True)
        
        # Créer un CSV de résultats analyse
        if len(analysis_results) > 0:
            results_data = []
            for idx, res in enumerate(analysis_results):
                if res.get('condition_met'):
                    bf = big_fires.iloc[idx]
                    results_data.append({
                        'Commune': bf['commune'],
                        'Date_Alerte': bf['date_alerte'],
                        'Petits_Feux_Avant': res['small_fires_count'],
                        'Moyens_Feux_Avant': res['medium_fires_count'],
                        'Total_Precurseurs': res['small_fires_count'] + res['medium_fires_count'],
                        'Tendance': res['trend'],
                        'Surface_ha': bf['surface_ha']
                    })
            if results_data:
                results_df = pd.DataFrame(results_data)
                results_csv = results_df.to_csv(index=False)
                st.download_button(
                    "⬇️ CSV - Résultats Analyse",
                    results_csv,
                    f"resultats_analyse_{annee_debut}_{annee_fin}.csv",
                    "text/csv",
                    use_container_width=True,
                    key="dl_csv_results"
                )

if __name__ == "__main__":
    main()
