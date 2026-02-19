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

# ========== CSS PREMIUM WOW - PALETTE MARRON + ORANGE ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@300;400;600;700;800&display=swap');

:root {
    --primary: #FF8C42;
    --secondary: #A0826D;
    --danger: #D2691E;
    --success: #8B7355;
    --dark-bg: #1a1410;
    --card-bg: rgba(40, 30, 25, 0.8);
}

/* Fond spectaculaire marron-orange */
html, body, [class*="stApp"] {
    background: linear-gradient(135deg, #1a1410 0%, #2d1f14 30%, #3d2514 70%, #1f1410 100%) !important;
    background-attachment: fixed !important;
    font-family: 'Poppins', sans-serif !important;
    color: #F5E6D3 !important;
}

/* Titres ultra-premium */
h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 3.5rem !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #A0826D 0%, #FF8C42 50%, #D2691E 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    text-shadow: 0 0 30px rgba(255, 140, 66, 0.3) !important;
    padding: 2rem 0 !important;
    letter-spacing: 2px !important;
    text-align: center !important;
}

h2 {
    font-family: 'Playfair Display', serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #A0826D, #FF8C42) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    border-left: 4px solid #FF8C42 !important;
    padding-left: 1rem !important;
    margin-top: 2rem !important;
}

h3 {
    color: #FF8C42 !important;
    font-weight: 700 !important;
    text-shadow: 0 0 20px rgba(255, 140, 66, 0.3) !important;
}

/* KPI Cards LUXE */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(160, 130, 109, 0.12), rgba(255, 140, 66, 0.12)) !important;
    backdrop-filter: blur(20px) !important;
    border: 2px solid rgba(255, 140, 66, 0.4) !important;
    border-radius: 20px !important;
    padding: 1rem !important;
    box-shadow: 0 8px 32px 0 rgba(255, 140, 66, 0.2) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

[data-testid="stMetric"]:hover {
    background: linear-gradient(135deg, rgba(160, 130, 109, 0.2), rgba(255, 140, 66, 0.2)) !important;
    transform: translateY(-8px) scale(1.02) !important;
    box-shadow: 0 16px 40px 0 rgba(255, 140, 66, 0.4) !important;
    border-color: rgba(255, 140, 66, 0.7) !important;
}

[data-testid="stMetricValue"] {
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #A0826D, #FF8C42) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

[data-testid="stMetricLabel"] {
    color: #F5E6D3 !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
}

/* Boutons PREMIUM */
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #A0826D, #FF8C42) !important;
    color: #1a1410 !important;
    border: 2px solid transparent !important;
    font-weight: 800 !important;
    border-radius: 15px !important;
    padding: 1rem 2rem !important;
    font-size: 1.1rem !important;
    transition: all 0.4s ease !important;
    box-shadow: 0 10px 30px rgba(255, 140, 66, 0.3) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

.stButton>button:hover, .stDownloadButton>button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 15px 40px rgba(255, 140, 66, 0.5) !important;
}

/* Sidebar LUXE */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(40, 30, 25, 0.95) 0%, rgba(26, 20, 16, 1) 100%) !important;
    backdrop-filter: blur(10px) !important;
    border-right: 3px solid rgba(255, 140, 66, 0.3) !important;
}

[data-testid="stSidebar"] label {
    color: #FF8C42 !important;
    font-weight: 700 !important;
    text-shadow: 0 0 10px rgba(255, 140, 66, 0.2) !important;
}

/* Dataframes */
.dataframe {
    background: rgba(40, 30, 25, 0.6) !important;
    border: 2px solid rgba(255, 140, 66, 0.3) !important;
    border-radius: 15px !important;
}

.dataframe thead tr {
    background: linear-gradient(90deg, rgba(255, 140, 66, 0.3), rgba(160, 130, 109, 0.2)) !important;
    border-bottom: 3px solid rgba(255, 140, 66, 0.5) !important;
}

.dataframe thead th {
    color: #FF8C42 !important;
    font-weight: 800 !important;
    padding: 1.2rem !important;
}

.dataframe tbody tr {
    border-bottom: 1px solid rgba(255, 140, 66, 0.2) !important;
    color: #F5E6D3 !important;
}

.dataframe tbody tr:hover {
    background: rgba(255, 140, 66, 0.15) !important;
}

.dataframe td {
    color: #F5E6D3 !important;
    font-weight: 600 !important;
    padding: 1rem !important;
}

/* Messages d'alerte */
.stSuccess {
    background: rgba(139, 115, 85, 0.15) !important;
    border: 2px solid #A0826D !important;
    border-radius: 15px !important;
    color: #FFB366 !important;
    font-weight: 700 !important;
}

.stInfo {
    background: rgba(255, 140, 66, 0.15) !important;
    border: 2px solid #FF8C42 !important;
    border-radius: 15px !important;
    color: #FFD699 !important;
    font-weight: 700 !important;
}

.stWarning {
    background: rgba(210, 107, 30, 0.15) !important;
    border: 2px solid #D2691E !important;
    border-radius: 15px !important;
    color: #FFB366 !important;
    font-weight: 700 !important;
}

.stError {
    background: rgba(210, 107, 30, 0.2) !important;
    border: 2px solid #D2691E !important;
    border-radius: 15px !important;
    color: #FF9955 !important;
    font-weight: 700 !important;
}

/* Sélecteurs & Inputs */
.stSelectbox [data-testid="baseButton-secondary"] {
    background: rgba(255, 140, 66, 0.1) !important;
    border: 2px solid rgba(255, 140, 66, 0.3) !important;
    color: #FF8C42 !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}

.stSelectbox [data-testid="baseButton-secondary"]:hover {
    border-color: rgba(210, 107, 30, 0.6) !important;
    background: rgba(255, 140, 66, 0.2) !important;
}

input[type="number"], input[type="text"] {
    background: rgba(255, 140, 66, 0.1) !important;
    border: 2px solid rgba(255, 140, 66, 0.3) !important;
    color: #FF8C42 !important;
    border-radius: 10px !important;
}

input[type="number"]:focus, input[type="text"]:focus {
    border-color: rgba(210, 107, 30, 0.6) !important;
    box-shadow: 0 0 15px rgba(255, 140, 66, 0.3) !important;
}

hr {
    border: 1px solid rgba(255, 140, 66, 0.2) !important;
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

# ========== FONCTION APPLY THEME ==========
def apply_premium_theme(fig):
    """Applique le thème PREMIUM WOW aux graphes"""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(26, 20, 16, 0.1)",
        plot_bgcolor="rgba(40, 30, 25, 0.3)",
        font=dict(family="Poppins, sans-serif", color="#F5E6D3", size=12),
        title_font=dict(size=16, color="#FF8C42"),
        xaxis=dict(gridcolor="rgba(255, 140, 66, 0.1)", showgrid=True, zeroline=False),
        yaxis=dict(gridcolor="rgba(255, 140, 66, 0.1)", showgrid=True, zeroline=False),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255, 140, 66, 0.1)",
            bordercolor="rgba(255, 140, 66, 0.3)",
            borderwidth=2,
            font=dict(color="#FF8C42")
        ),
        hovermode='closest',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig

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
    try:
        csv_path = Path(__file__).parent / 'data' / 'promothee' / 'incendies_paca_2015_2022.csv'
        df = load_data(str(csv_path))
        
        if len(df) == 0:
            st.error("❌ Aucune donnée trouvée")
            return
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
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
            
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.metric("Petits feux", selected_result['small_fires_count'])
            with m2:
                st.metric("Moyens feux", selected_result['medium_fires_count'])
            with m3:
                st.metric("Total avant", selected_result['small_fires_count'] + selected_result['medium_fires_count'])
            with m4:
                st.metric("Surface (ha)", f"{selected_fire['surface_ha']:.1f}")
            with m5:
                st.metric("Tendance", selected_result['trend'])
            
            departement = str(selected_fire.get('depart', 'Inconnu'))
            fig_time = create_temporal_series(daily_counts, selected_fire['date_alerte'], selected_fire['commune'], 
                                            tendance=selected_result['trend'], departement=departement)
            fig_time = apply_premium_theme(fig_time)
            fig_time.update_layout(
            margin=dict(l=20, r=20, t=100, b=20)  # l,r,t,b en pixels
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
            
            df_trends, trends_summary = analyze_parameter_trends(small_fires_temp)
            if len(df_trends) > 0 and len(trends_summary) > 0:
                st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
                st.markdown("""<h3 style='border-bottom: 3px solid rgba(255, 140, 66, 0.4); padding-bottom: 1rem; margin-bottom: 1.5rem;'>📈 Tendances Environnementales</h3>""", unsafe_allow_html=True)
                st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
                fig_params = create_parameter_trends_chart(df_trends, trends_summary, selected_fire['commune'])
                fig_params = apply_premium_theme(fig_params)
                fig_params.update_layout(
            margin=dict(l=20, r=20, t=150, b=20)  # l,r,t,b en pixels
            )
                st.plotly_chart(fig_params, use_container_width=True, height=500)
        else:
            st.info("ℹ️ Aucun petit feu dans la fenêtre temporelle")
    
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
    
    # ========== CORRÉLATIONS ==========
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <h2>🔗 ANALYSES DE CORRÉLATION</h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""<h3 style='border-bottom: 3px solid rgba(255, 140, 66, 0.4); padding-bottom: 1rem; margin-bottom: 1.5rem;'>📋 Tableau Récapitulatif des Corrélations</h3>""", unsafe_allow_html=True)
    try:
        summary_df = create_correlation_summary_table(df_filtered)
        st.dataframe(summary_df, use_container_width=True, height=300)
    except Exception as e:
        st.warning(f"⚠️ Corrélations indisponibles: {e}")
    
    st.markdown("""<div style='height: 1.5rem;'></div>""", unsafe_allow_html=True)
    
    st.markdown("""<h3 style='border-bottom: 3px solid rgba(255, 140, 66, 0.4); padding-bottom: 1rem; margin-bottom: 1.5rem;'>📈 Corrélations Paramètres → Grands Feux</h3>""", unsafe_allow_html=True)
    
    st.markdown("""<div style='height: 1rem;'></div>""", unsafe_allow_html=True)
    global_param_corr = analyze_global_parameter_correlations(analysis_results, big_fires)
    if global_param_corr and any(c['status'] == 'OK' for c in global_param_corr.values()):
        fig_global = create_global_parameter_correlation_chart(global_param_corr)
        fig_global = apply_premium_theme(fig_global)
        fig_global.update_layout(
            margin=dict(l=20, r=20, t=150, b=20)  # l,r,t,b en pixels
            )
        st.plotly_chart(fig_global, use_container_width=True)
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
