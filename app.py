# -*- coding: utf-8 -*-
"""
WILDFIRE INSIGHTS PACA
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
    create_comprehensive_fire_analysis, PARAM_NAMES
)
from modules.export import export_results, export_csv

# ========== CONFIGURATION PAGE ==========
st.set_page_config(
    page_title="WILDFIRE INSIGHTS PACA",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CSS SIMPLE & PROFESSIONNEL - PALETTE BLEU/GRIS ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #1E5A96;
    --secondary: #4A7BA7;
    --accent: #2E8B9E;
    --bg-main: #F5F7FA;
    --bg-soft: #FFFFFF;
    --text-main: #1F2937;
    --text-muted: #6B7280;
    --border: #E5E7EB;
}

html, body, [class*="stApp"] {
    background: linear-gradient(180deg, #F5F7FA 0%, #FFFFFF 100%) !important;
    background-attachment: fixed !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-main) !important;
}

h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    color: #1E5A96 !important;
    padding: 1rem 0 !important;
    letter-spacing: -0.5px !important;
    text-align: center !important;
}

h2 {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #1E5A96 !important;
    border-left: 4px solid #2E8B9E !important;
    padding-left: 1rem !important;
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
}

h3 {
    color: #4A7BA7 !important;
    font-weight: 600 !important;
}

h4, h5, h6 {
    color: #2E8B9E !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.8rem !important;
}

[data-testid="stMetric"] {
    background: #FFFFFF !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
    transition: all 0.3s ease !important;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(30, 90, 150, 0.12) !important;
    border-color: #2E8B9E !important;
}

[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #1E5A96 !important;
}

[data-testid="stMetricLabel"] {
    color: #6B7280 !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
}

.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #1E5A96, #2E8B9E) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.8rem 1.5rem !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(30, 90, 150, 0.15) !important;
    text-transform: none !important;
}

.stButton>button:hover, .stDownloadButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(30, 90, 150, 0.25) !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E5A96 0%, #2E8B9E 100%) !important;
    border-right: 1px solid #E5E7EB !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] .stSubheader {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

.dataframe {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
}

.dataframe thead tr {
    background: linear-gradient(90deg, #1E5A96 0%, #2E8B9E 100%) !important;
    border-bottom: 3px solid #0E3A5F !important;
}

.dataframe thead th {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    padding: 1.2rem !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    font-size: 0.9rem !important;
}

.dataframe tbody tr {
    border-bottom: 1px solid #E5E7EB !important;
    color: #1F2937 !important;
    transition: background-color 0.2s ease !important;
}

.dataframe tbody tr:hover {
    background: #E8F2FF !important;
}

.dataframe td {
    color: #4B5563 !important;
    font-weight: 500 !important;
    padding: 0.85rem 1rem !important;
}

.stSuccess {
    background: rgba(34, 197, 94, 0.1) !important;
    border: 1px solid #22C55E !important;
    border-radius: 8px !important;
    color: #166534 !important;
    font-weight: 600 !important;
}

.stInfo {
    background: rgba(30, 90, 150, 0.1) !important;
    border: 1px solid #1E5A96 !important;
    border-radius: 8px !important;
    color: #1F2937 !important;
    font-weight: 600 !important;
}

.stWarning {
    background: rgba(245, 158, 11, 0.1) !important;
    border: 1px solid #F59E0B !important;
    border-radius: 8px !important;
    color: #92400E !important;
    font-weight: 600 !important;
}

.stError {
    background: rgba(239, 68, 68, 0.1) !important;
    border: 1px solid #EF4444 !important;
    border-radius: 8px !important;
    color: #7F1D1D !important;
    font-weight: 600 !important;
}

.stSelectbox [data-testid="baseButton-secondary"] {
    background: linear-gradient(135deg, #1E5A96, #2E8B9E) !important;
    border: 2px solid #1E5A96 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
    font-weight: 600 !important;
}

.stSelectbox [data-testid="baseButton-secondary"]:hover {
    border-color: #2E8B9E !important;
    background: linear-gradient(135deg, #2E8B9E, #1E5A96) !important;
    box-shadow: 0 2px 8px rgba(30, 90, 150, 0.3) !important;
}

input[type="number"], input[type="text"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    color: #1F2937 !important;
    border-radius: 8px !important;
}

input[type="number"]:focus, input[type="text"]:focus {
    border-color: #2E8B9E !important;
    box-shadow: 0 0 0 3px rgba(46, 139, 158, 0.1) !important;
}

hr {
    border: 1px solid #E5E7EB !important;
}

.stMarkdown p, .stMarkdown li, .stMarkdown div, .stCaption, label, span {
    color: var(--text-main) !important;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="element-container"] {
    animation: slideIn 0.5s ease-out !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebar"] .stNumberInput button,
[data-testid="stSidebar"] div[data-baseweb="input"] button {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    color: #1E5A96 !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] .stNumberInput button:hover,
[data-testid="stSidebar"] div[data-baseweb="input"] button:hover {
    background-color: #FFFFFF !important;
    border-color: #FFFFFF !important;
}

[data-testid="stSidebar"] .stNumberInput button:disabled {
    background-color: rgba(255, 255, 255, 0.5) !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
    color: rgba(255, 255, 255, 0.6) !important;
    opacity: 0.6 !important;
}

[data-testid="stSidebar"] input[type="number"],
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input {
    background-color: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    color: #1F2937 !important;
}
</style>
""", unsafe_allow_html=True)
# ========== FONCTION APPLY THEME ==========
def apply_premium_theme(fig):
    """Applique le thème simple et professionnel aux graphes"""
    primary_color = "#1E5A96"
    secondary_color = "#4A7BA7"
    accent_color = "#2E8B9E"
    
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(245, 247, 250, 0.98)",
        plot_bgcolor="rgba(255, 255, 255, 0.95)",
        font=dict(family="Inter, sans-serif", color="#1F2937", size=12),
        title_font=dict(size=16, color=primary_color),
        xaxis=dict(
            gridcolor="rgba(30, 90, 150, 0.08)", 
            linecolor="rgba(30, 90, 150, 0.25)", 
            showgrid=True, 
            zeroline=False,
            title_font=dict(color="#1F2937", size=14),
            tickfont=dict(color="#1F2937", size=11)
        ),
        yaxis=dict(
            gridcolor="rgba(30, 90, 150, 0.08)", 
            linecolor="rgba(30, 90, 150, 0.25)", 
            showgrid=True, 
            zeroline=False,
            title_font=dict(color="#1F2937", size=14),
            tickfont=dict(color="#1F2937", size=11)
        ),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0.92)",
            bordercolor="rgba(30, 90, 150, 0.2)",
            borderwidth=1,
            font=dict(color="#1F2937"),
            title=dict(font=dict(color="#1F2937"))
        ),
        hovermode='closest',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Appliquer les couleurs du thème aux traces
    color_palette = [primary_color, accent_color, secondary_color, "#6B8FC4", "#4A9B8E", "#5B7A99"]
    for idx, trace in enumerate(fig.data):
        # Vérifier le type de trace
        if hasattr(trace, 'type') and trace.type == 'pie':
            # Pour les pie charts, utiliser une palette de couleurs pour chaque segment
            if hasattr(trace, 'labels') and len(trace.labels) > 0:
                colors = [color_palette[i % len(color_palette)] for i in range(len(trace.labels))]
                trace.marker.colors = colors
        else:
            # Pour les autres types de graphes (bar, line, scatter, etc.)
            color = color_palette[idx % len(color_palette)]
            if hasattr(trace, 'marker') and trace.marker is not None:
                trace.marker.color = color
            elif hasattr(trace, 'line') and trace.line is not None:
                trace.line.color = color
    
    fig.update_xaxes(title_font=dict(color="#1F2937", size=14), tickfont=dict(color="#1F2937", size=11))
    fig.update_yaxes(title_font=dict(color="#1F2937", size=14), tickfont=dict(color="#1F2937", size=11))
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
    # Titre professionnel
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1>WILDFIRE INSIGHTS PACA</h1>
        <p style='color: #6B7280; font-size: 1.1rem;'>
            Analyse Complète Spatiale & Temporelle
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
        <div style='text-align: center; padding: 0.5rem 0; margin-bottom: 1.5rem; margin-top: -1rem; background: linear-gradient(135deg, rgba(255, 255, 255, 0.50), rgba(255, 255, 255, 0.15)); border-radius: 8px; backdrop-filter: blur(10px);'>
            <h2 style='color: #E5E7EB; margin: 0; font-size: 1.5rem; font-weight: 700; letter-spacing: 0.5px;'>Paramètres</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='color: #FFFFFF;'>📅 Période</h3>", unsafe_allow_html=True)
        annee_min = int(df['annee'].min())
        annee_max = int(df['annee'].max())
        annee_debut = st.number_input("Début", min_value=annee_min, max_value=annee_max, value=annee_min)
        annee_fin = st.number_input("Fin", min_value=annee_min, max_value=annee_max, value=annee_max)
        
        st.markdown("<h3 style='color: #FFFFFF; margin-top: 1.5rem;'>📊 Classification</h3>", unsafe_allow_html=True)
        seuil_petit = st.number_input("Petit feu < (ha)", min_value=0.1, value=1.0, step=0.1)
        seuil_grand = st.number_input("Grand feu ≥ (ha)", min_value=0.1, value=10.0, step=0.5)
        
        st.markdown("<h3 style='color: #FFFFFF; margin-top: 1.5rem;'>⚙️ Analyse</h3>", unsafe_allow_html=True)
        buffer_radius = st.slider("Rayon buffer (km)", 1, 100, 10)
        temporal_window = st.slider("Fenêtre (jours)", 7, 180, 30)
        min_fires_before = st.slider("Min. petits feux", 0, 20, 3)
    
    # Filtrer données
    df_filtered = df[(df['annee'] >= annee_debut) & (df['annee'] <= annee_fin)].copy()
    df_filtered = classify_fires(df_filtered, seuil_petit, seuil_grand)
    
    # ========== KPI DASHBOARD ==========
    st.markdown("""<div style='height: 2rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>Tableau de Bord - Indicateurs Clés</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    kpi_cols = st.columns(5, gap="medium")
    total_fires = len(df_filtered)
    petits = len(df_filtered[df_filtered['categorie'] == 'Petit feu'])
    moyens = len(df_filtered[df_filtered['categorie'] == 'Feu moyen'])
    grands = len(df_filtered[df_filtered['categorie'] == 'Grand feu'])
    total_surface = df_filtered['surface_ha'].sum() if 'surface_ha' in df_filtered else 0
    
    with kpi_cols[0]:
        st.metric("Total Incendies", total_fires)
    with kpi_cols[1]:
        pct_petit = (petits/total_fires*100) if total_fires > 0 else 0
        st.metric("Petits Feux", petits, delta=f"{pct_petit:.0f}%")
    with kpi_cols[2]:
        pct_moyen = (moyens/total_fires*100) if total_fires > 0 else 0
        st.metric("Feux Moyens", moyens, delta=f"{pct_moyen:.0f}%")
    with kpi_cols[3]:
        pct_grand = (grands/total_fires*100) if total_fires > 0 else 0
        st.metric("Grands Feux", grands, delta=f"{pct_grand:.0f}%")
    with kpi_cols[4]:
        st.metric("Surface Totale", f"{total_surface:.0f} ha")
    
    # Insights Section
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    insight_col1, insight_col2, insight_col3 = st.columns(3, gap="medium")
    
    with insight_col1:
        avg_surface = df_filtered['surface_ha'].mean() if len(df_filtered) > 0 else 0
        st.markdown(f"""
        <div style='background: rgba(30, 90, 150, 0.05); border-radius: 10px; padding: 1rem; border-left: 4px solid #1E5A96;'>
            <p style='color: #6B7280; margin: 0 0 0.5rem 0; font-size: 0.9rem;'>Superficie Moyenne</p>
            <p style='color: #1E5A96; margin: 0; font-size: 1.8rem; font-weight: 700;'>{avg_surface:.2f}</p>
            <p style='color: #6B7280; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>hectares</p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        communes = df_filtered['commune'].nunique() if 'commune' in df_filtered else 0
        st.markdown(f"""
        <div style='background: rgba(46, 139, 158, 0.05); border-radius: 10px; padding: 1rem; border-left: 4px solid #2E8B9E;'>
            <p style='color: #6B7280; margin: 0 0 0.5rem 0; font-size: 0.9rem;'>Communes Affectées</p>
            <p style='color: #1E5A96; margin: 0; font-size: 1.8rem; font-weight: 700;'>{communes}</p>
            <p style='color: #6B7280; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>localités</p>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col3:
        annees = df_filtered['annee'].nunique() if 'annee' in df_filtered else 0
        st.markdown(f"""
        <div style='background: rgba(74, 123, 167, 0.05); border-radius: 10px; padding: 1rem; border-left: 4px solid #4A7BA7;'>
            <p style='color: #6B7280; margin: 0 0 0.5rem 0; font-size: 0.9rem;'>Années Couvertes</p>
            <p style='color: #1E5A96; margin: 0; font-size: 1.8rem; font-weight: 700;'>{annees}</p>
            <p style='color: #6B7280; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>périodes</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 2rem 0;'>""", unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    # Statistics Row
    stat_col2, stat_col3, stat_col4 = st.columns(3, gap="medium")
    
    
    
    with stat_col2:
        if grands > 0 and 'surface_ha' in df_filtered.columns:
            max_surface = df_filtered[df_filtered['categorie'] == 'Grand feu']['surface_ha'].max() if len(df_filtered[df_filtered['categorie'] == 'Grand feu']) > 0 else 0
            st.markdown(f"""
            <div style='background: rgba(245, 158, 11, 0.1); border-radius: 10px; padding: 1rem;'>
                <p style='color: #6B7280; margin: 0 0 0.5rem 0; font-size: 0.85rem;'>Plus Grand Feu</p>
                <p style='color: #1E5A96; margin: 0; font-size: 1.6rem; font-weight: 700;'>{max_surface:.0f} ha</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: rgba(245, 158, 11, 0.1); border-radius: 10px; padding: 1rem;'>
                <p style='color: #6B7280; margin: 0 0 0.5rem 0; font-size: 0.85rem;'>Plus Grand Feu</p>
                <p style='color: #999; margin: 0; font-size: 1.3rem;'>-</p>
            </div>
            """, unsafe_allow_html=True)
    
    with stat_col3:
        if len(df_filtered) > 0:
            feu_par_an = total_fires / annees if annees > 0 else 0
            st.markdown(f"""
            <div style='background: rgba(16, 185, 129, 0.1); border-radius: 10px; padding: 1rem;'>
                <p style='color: #6B7280; margin: 0 0 0.5rem 0; font-size: 0.85rem;'>Moyenne/Année</p>
                <p style='color: #1E5A96; margin: 0; font-size: 1.6rem; font-weight: 700;'>{feu_par_an:.0f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with stat_col4:
        if total_fires > 0 and total_surface > 0:
            ratio = total_surface / total_fires
            st.markdown(f"""
            <div style='background: rgba(139, 92, 246, 0.1); border-radius: 10px; padding: 1rem;'>
                <p style='color: #6B7280; margin: 0 0 0.5rem 0; font-size: 0.85rem;'>Surface/Feu</p>
                <p style='color: #1E5A96; margin: 0; font-size: 1.6rem; font-weight: 700;'>{ratio:.2f} ha</p>
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
    
    # ========== DISTRIBUTION & CARTE ==========
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>Analyse Spatiale & Distribution</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    # Trois graphes côte à côte
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.markdown("""
        <div style='background: rgba(30, 90, 150, 0.05);
                border-radius: 10px;
                padding: 0.7rem 1rem;
                border-left: 3px solid #1E5A96;
                text-align: center;
                margin-bottom: 1rem;'>
        <h3 style='margin: 0; font-size: 0.95rem; color: #1E5A96; font-weight: 700;'>Distribution Catégories</h3>
        </div>
        """, unsafe_allow_html=True)
        fig_pie = create_pie_chart(df_filtered)
        fig_pie = apply_premium_theme(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart", height=350)

    with col2:
        st.markdown("""
        <div style='background: rgba(46, 139, 158, 0.05);
                border-radius: 10px;
                padding: 0.7rem 1rem;
                border-left: 3px solid #2E8B9E;
                text-align: center;
                margin-bottom: 1rem;'>
        <h3 style='margin: 0; font-size: 0.95rem; color: #1E5A96; font-weight: 700;'>Trend Annuelle</h3>
        </div>
        """, unsafe_allow_html=True)
        fig_line = create_line_chart(df_filtered)
        fig_line = apply_premium_theme(fig_line)
        st.plotly_chart(fig_line, use_container_width=True, key="line_chart", height=350)
    
    
    # Carte sur ligne seule
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: rgba(30, 90, 150, 0.05);
                backdrop-filter: blur(14px);
                border-radius: 12px;
                padding: 0.8rem 1rem;
                border: 1px solid rgba(30, 90, 150, 0.15);
                display: flex;
                align-items: center;
                height: 72px;
                '>
        <h3 style='margin: 0; font-size: 1.5rem; color: #1E5A96; font-weight: 700;'>Localisation Géographique Interactive</h3>
    </div>
    """, unsafe_allow_html=True)
    
    fig_map = create_map(df_filtered, big_fires, analysis_results, buffer_radius)
    fig_map.update_layout(title_text="Carte des Incendies PACA", title_font_size=17, title_font_color="#1E5A96")
    fig_map = apply_premium_theme(fig_map)
    st.plotly_chart(fig_map, use_container_width=True, key="map_chart", height=600)
    
    # ========== ÉVOLUTION TEMPORELLE ==========
    st.markdown("""
    <h2>Évolution Temporelle</h2>
    """, unsafe_allow_html=True)
    
    valid_indices = [i for i, r in enumerate(analysis_results) if r.get('condition_met')]
    if len(valid_indices) > 0:
        options = [
            f"{big_fires.iloc[i]['commune']} — {big_fires.iloc[i]['date_alerte'].strftime('%d/%m/%Y')} ({analysis_results[i]['small_fires_count']} petits feux)"
            for i in valid_indices
        ]
        st.markdown(""" 
        <div style='background: rgba(30, 90, 150, 0.60); border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 1.5rem; border: 1px solid #1E5A96; box-shadow: 0 2px 8px rgba(30, 90, 150, 0.15);'>
            <h3 style='color: #FFFFFF; margin: 0; font-size: 1.1rem; font-weight: 700; letter-spacing: 0.5px;'>Sélection du Grand Feu</h3>
        </div>
        """, unsafe_allow_html=True)
        sel = st.selectbox("Choisir un grand feu à analyser", options=options, key='select_fire_temporal', label_visibility="collapsed")
        
        actual_idx = valid_indices[options.index(sel)]
        selected_result = analysis_results[actual_idx]
        selected_fire = big_fires.iloc[actual_idx]
        
        if 'small_fires' in selected_result and len(selected_result['small_fires']) > 0:
            small_fires_temp = selected_result['small_fires'].copy()
            small_fires_temp['date_only'] = small_fires_temp['date_alerte'].dt.date
            daily_counts = small_fires_temp.groupby('date_only').size().reset_index(name='Nombre')
            daily_counts['date_only'] = pd.to_datetime(daily_counts['date_only'])
            
            # ===== SECTION 1 : TENDANCES DES PARAMÈTRES ENVIRONNEMENTAUX =====
            st.markdown("""
            <div style='padding: 0.5rem 0; margin: 1.5rem 0 1rem 0;'>
                <h4 style='margin: 0; color: #2E8B9E; font-size: 1.2rem; font-weight: 700;'>📊 Tendances des Paramètres Environnementaux</h4>
            </div>
            """, unsafe_allow_html=True)
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
                
                # Palette de couleurs distinctes dans le thème bleu/gris
                color_palette = {
                    0: "#1E5A96",  # Bleu primaire
                    1: "#2E8B9E",  # Bleu accent
                    2: "#4A7BA7",  # Bleu secondaire
                    3: "#6B8FC4",  # Bleu clair
                    4: "#4A9B8E",  # Teal
                    5: "#5B7A99",  # Bleu gris
                    6: "#3D6B94",  # Bleu foncé
                    7: "#2F7A8A",  # Teal foncé
                }
                
                # Appliquer les couleurs distinctes à chaque trace
                for idx, trace in enumerate(fig_params.data):
                    color = color_palette.get(idx, color_palette[idx % len(color_palette)])
                    if hasattr(trace, 'marker'):
                        trace.marker.color = color
                    if hasattr(trace, 'line'):
                        trace.line.color = color
                
                fig_params.update_layout(margin=dict(l=30, r=30, t=155, b=45), height=510)
                st.plotly_chart(fig_params, use_container_width=True)
                
                # Tableau récapitulatif des tendances
                st.markdown("""
                <div style='padding: 0.5rem 0; margin: 1.5rem 0 1rem 0;'>
                    <h4 style='margin: 0; color: #2E8B9E; font-size: 1.1rem; font-weight: 700;'>📋 Tableau Récapitulatif des Tendances</h4>
                </div>
                """, unsafe_allow_html=True)
                
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
            st.markdown("""
            <div style=';'>
                <h4 style='margin: 0; color: #2E8B9E; font-size: 1.2rem; font-weight: 700;'>📈 Accumulation Temporelle des Incendies</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Métriques clés avec delta pour la tendance - AU-DESSUS DU GRAPHE
            st.markdown("""
            <div style='padding: 0rem 0;'>
                <h4 style='margin: 0; color: #2E8B9E; font-size: 1.1rem; font-weight: 700;'>🔥 Statistiques du Grand Feu</h4>
            </div>
            """, unsafe_allow_html=True)
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
            fig_time.update_layout(margin=dict(l=30, r=30, t=155, b=45), height=510)
            st.plotly_chart(fig_time, use_container_width=True)
            
            # ===== GRAPHIQUE COMPLET MÉTÉOROLOGIQUE =====
            st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
            
            st.markdown("""
            <div style='padding: 0.5rem 0; margin: 1rem 0 1rem 0;'>
                <h4 style='margin: 0; color: #2E8B9E; font-size: 1.2rem; font-weight: 700;'>Analyse Météorologique Complète</h4>
            </div>
            """, unsafe_allow_html=True)
            st.caption("Tous les paramètres environnementaux et feux sur une même visualisation")
            
            # Créer le graphique complet
            try:
                fig_comprehensive = create_comprehensive_fire_analysis(
                    small_fires_temp,
                    selected_fire['commune'],
                    selected_fire['date_alerte']
                )
                st.plotly_chart(fig_comprehensive, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Impossible de générer le graphique météorologique: {str(e)}")
        else:
            st.info("Aucun petit feu dans la fenêtre temporelle")
    
    # ========== COMMUNES À TENDANCE CROISSANTE ==========
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>Communes à Tendance Croissante</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    if st.button("Analyser les Communes à Risque", use_container_width=True):
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
            st.success(f"{len(communes_croissance)} commune(s) avec tendance croissante")
            df_c = pd.DataFrame(communes_croissance).sort_values('Total', ascending=True)
            
            # Deux graphes côte à côte
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown("""
                <div style='background: rgba(30, 90, 150, 0.05);
                backdrop-filter: blur(14px);
                border-radius: 12px;
                padding: 0.8rem 1rem;
                border: 1px solid rgba(30, 90, 150, 0.15);
                display: flex;
                align-items: center;
                justify-content: center;
                height: 72px;
                text-align: center;'>
        <h3 style='margin: 0; font-size: 1.05rem; color: #1E5A96; font-weight: 700;'>Répartition par Commune</h3>
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
                <div style='background: rgba(30, 90, 150, 0.05);
                backdrop-filter: blur(14px);
                border-radius: 12px;
                padding: 0.8rem 1rem;
                border: 1px solid rgba(30, 90, 150, 0.15);
                display: flex;
                align-items: center;
                justify-content: center;
                height: 72px;
                text-align: center;'>
        <h3 style='margin: 0; font-size: 1.05rem; color: #1E5A96; font-weight: 700;'>Proportion Petits vs Moyens</h3>
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
            <div style='background: rgba(30, 90, 150, 0.05);
                backdrop-filter: blur(14px);
                border-radius: 12px;
                padding: 0.8rem 1rem;
                border: 1px solid rgba(30, 90, 150, 0.15);
                display: flex;
                align-items: center;
                height: 72px;
                '>
        <h3 style='margin: 0; font-size: 1.5rem; color: #1E5A96; font-weight: 700;'>Localisation des Communes à Risque</h3>
            </div>
            """, unsafe_allow_html=True)
            fig_map = create_communes_croissance_map(big_fires, analysis_results)
            fig_map.update_layout(title_text="Communes à Tendance Croissante", title_font_size=14, margin=dict(l=50, r=50, t=80, b=50))
            st.plotly_chart(fig_map, use_container_width=True, height=600)
            
            # Métriques récapitulatives en bas (ligne complète)
            st.markdown("---")
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            with metric_col1:
                st.metric("Nb grands feux", len(communes_croissance))
            with metric_col2:
                st.metric("Total petits feux", total_petits)
            with metric_col3:
                st.metric("Total moyens feux", total_moyens)
            with metric_col4:
                total_all = total_petits + total_moyens
                st.metric("Total feux précurseurs", total_all)
        else:
            st.info("Aucun grand feu avec tendance croissante détecté")
    
    # ========== ANALYSE COMPARATIVE ==========
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>Analyse Comparative</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    fig_comp = create_multi_fire_comparison(analysis_results, big_fires, temporal_window, nb_feux=10, show_moyenne=False, show_variance=False)
    fig_comp = apply_premium_theme(fig_comp)
    st.plotly_chart(fig_comp, use_container_width=True)
    
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    # ===== DÉPARTEMENT FILTER FOR CORRELATIONS =====
    st.markdown("""
    <h2>Analyses de Corrélation</h2>
    """, unsafe_allow_html=True)
    st.markdown(""" 
        <div style='background: rgba(30, 90, 150, 0.60); border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 1.5rem; border: 1px solid #1E5A96; box-shadow: 0 2px 8px rgba(30, 90, 150, 0.15);'>
            <h3 style='color: #FFFFFF; margin: 0; font-size: 1.1rem; font-weight: 700; letter-spacing: 0.5px;'>Filtrez les analyses de corrélation par département pour des résultats plus précis Feu</h3>
        </div>
        """, unsafe_allow_html=True)
    
    
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
    st.markdown("""<h3 style='border-bottom: 3px solid rgba(255, 140, 66, 0.4); padding-bottom: 1rem; margin-bottom: 1.5rem;'>Tableau Récapitulatif des Corrélations</h3>""", unsafe_allow_html=True)
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
    
    st.markdown("""<h3 style='border-bottom: 3px solid rgba(255, 140, 66, 0.4); padding-bottom: 1rem; margin-bottom: 1.5rem;'> Corrélations Paramètres → Grands Feux</h3>""", unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    global_param_corr = analyze_global_parameter_correlations(analysis_results, big_fires)
    if global_param_corr and any(c['status'] == 'OK' for c in global_param_corr.values()):
        fig_global = create_global_parameter_correlation_chart(global_param_corr)
        fig_global = apply_premium_theme(fig_global)
        fig_global.update_layout(margin=dict(l=20, r=20, t=150, b=20))
        st.plotly_chart(fig_global, use_container_width=True)
        
        # Tableau détaillé
        st.markdown("""
        <div style='padding: 0.5rem 0; margin: 1.5rem 0 1rem 0;'>
            <h4 style='margin: 0; color: #2E8B9E; font-size: 1.1rem; font-weight: 700;'> Tableau Détaillé des Corrélations Paramétriques</h4>
        </div>
        """, unsafe_allow_html=True)
        
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
    
    exp_col1, exp_col2, exp_col3 = st.columns(3, gap="medium")
    
    with exp_col1:
        
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
    
    with exp_col2:
        csv = export_csv(df_filtered)
        st.download_button(
            "📑 CSV Données",
            csv,
            f"incendies_{annee_debut}_{annee_fin}.csv",
            "text/csv",
            use_container_width=True,
            key="dl_csv_filtered"
        )
    
    with exp_col3:
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
                    "📈 CSV Résultats",
                    results_csv,
                    f"resultats_{annee_debut}_{annee_fin}.csv",
                    "text/csv",
                    use_container_width=True,
                    key="dl_csv_results"
                )

if __name__ == "__main__":
    main()
