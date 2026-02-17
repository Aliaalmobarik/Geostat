# -*- coding: utf-8 -*-
"""
Application Streamlit - Analyse des Incendies en PACA
Analyse spatiale et temporelle avec visualisations améliorées
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from modules.data_processing import (
    load_data, classify_fires, analyze_fires_before_big_fire,
    analyze_parameter_trends, analyze_parameter_correlations_with_big_fire,
    analyze_global_parameter_correlations
)
from modules.visualizations import (
    create_map, create_pie_chart, create_line_chart,
    create_trend_bar, create_scatter_plot, create_temporal_series,
    create_multi_fire_comparison, create_detail_fire_map,
    create_correlation_summary_table,
    create_communes_croissance_map, create_parameter_trends_chart,
    create_parameter_correlation_chart, create_global_parameter_correlation_chart,
    PARAM_NAMES
)
from modules.export import export_results, export_csv

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Incendies PACA",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    st.title("Analyse des Incendies en PACA")
    
    # CSS personnalisé pour améliorer l'apparence
    st.markdown("""
    <style>
    /* Police monospace pour tout le texte */
    * {
        font-family: 'Courier New', 'Consolas', 'Monaco', monospace !important;
    }
    
    /* Amélioration des titres */
    h1, h2, h3 {
        color: #6E026F !important;
        font-weight: bold !important;
    }
    
    /* Style des métriques - valeurs en gras et plus grandes */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #6E026F !important;
        font-weight: bold !important;
    }
    
    /* Labels des métriques */
    [data-testid="stMetricLabel"] {
        font-weight: bold !important;
    }
    
    /* Delta des métriques */
    [data-testid="stMetricDelta"] {
        font-weight: bold !important;
    }
    
    /* Boutons */
    .stButton>button {
        border: 2px solid #6E026F !important;
        background-color: #6E026F !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    .stButton>button:hover {
        background-color: #FA891A !important;
        border-color: #FA891A !important;
    }
    
    /* Download buttons */
    .stDownloadButton>button {
        border: 2px solid #FA891A !important;
        background-color: #FA891A !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #EAEFEF !important;
    }
    
    /* Amélioration des dataframes */
    .dataframe {
        border: 2px solid #ABDADC !important;
    }
    
    /* Chiffres dans les dataframes en gras */
    .dataframe td {
        font-weight: bold !important;
    }
    
    .dataframe th {
        font-weight: bold !important;
    }
    
    /* Success/Info/Warning boxes */
    .stSuccess {
        background-color: #ABDADC !important;
        border-left: 5px solid #FA891A !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    .stInfo {
        background-color: #EAEFEF !important;
        border-left: 5px solid #ABDADC !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    .stWarning {
        background-color: #FFF5E1 !important;
        border-left: 5px solid #8B0000 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    /* Selectbox options avec police plus grande */
    .stSelectbox {
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }
    
    /* Input number fields avec chiffres en gras */
    input[type="number"] {
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    /* Slider values en gras */
    [data-testid="stTickBar"] {
        font-weight: bold !important;
    }
    
    /* Captions avec police légèrement plus grande */
    .stCaption {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Chargement des données
    try:
        # Chemin absolu basé sur l'emplacement de app.py
        csv_path = Path(__file__).parent / 'data' / 'promothee' / 'incendies_paca_2015_2022.csv'
        df = load_data(str(csv_path))
        
        if len(df) == 0:
            st.error("Aucune donnée valide trouvée dans le fichier CSV")
            return
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        st.info("Vérifiez que le fichier data/incendies_paca_2015_2022.csv existe")
        return
    
    st.markdown("---")
    
    # ========== PARAMÈTRES ==========
    st.header("Paramètres d'analyse")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Période")
        annee_min = int(df['annee'].min())
        annee_max = int(df['annee'].max())
        annee_debut = st.number_input("Année de début", min_value=annee_min, 
                                       max_value=annee_max, value=annee_min)
        annee_fin = st.number_input("Année de fin", min_value=annee_min, 
                                     max_value=annee_max, value=annee_max)
    
    with col2:
        st.subheader("Classification")
        seuil_petit = st.number_input("Petit feu < (ha)", min_value=0.1, value=1.0, step=0.1)
        seuil_grand = st.number_input("Grand feu ≥ (ha)", min_value=0.1, value=10.0, step=0.5)
    
    with col3:
        st.subheader("Analyse spatiale")
        buffer_radius = st.slider("Rayon buffer (km)", min_value=1, max_value=100, value=10)
        temporal_window = st.slider("Fenêtre temporelle (jours)", min_value=7, max_value=180, value=30)
    
    min_fires_before = st.slider("Nombre min. de petits feux", min_value=0, max_value=20, value=3)
    
    # Filtrage et classification
    df_filtered = df[(df['annee'] >= annee_debut) & (df['annee'] <= annee_fin)].copy()
    df_filtered = classify_fires(df_filtered, seuil_petit, seuil_grand)
    
    st.markdown("---")
    
    # ========== STATISTIQUES ==========
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total incendies", len(df_filtered))
    with col2:
        petits = len(df_filtered[df_filtered['categorie'] == 'Petit feu'])
        st.metric("Petits feux", petits)
    with col3:
        moyens = len(df_filtered[df_filtered['categorie'] == 'Feu moyen'])
        st.metric("Feux moyens", moyens)
    with col4:
        grands = len(df_filtered[df_filtered['categorie'] == 'Grand feu'])
        st.metric("Grands feux", grands)
    
    st.markdown("---")
    
    # Message méthodologie
    st.info(f"""
    **Méthodologie** : Les petits et moyens feux sont comptés **uniquement** s'ils répondent aux **TROIS conditions** :
    **Temporelle** : **{temporal_window}** jours AVANT le grand feu | **Spatiale** : **{buffer_radius}** km AUTOUR | **Quantité** : Min. **{min_fires_before}** petits feux
    """)
    
    st.markdown("---")
    
    # ========== PRÉPARATION DES DONNÉES ==========
    big_fires = df_filtered[
        (df_filtered['categorie'] == 'Grand feu') & 
        (df_filtered['date_alerte'].notna())
    ].copy()
    
    # Dédupliquer les grands feux (même commune, date, coordonnées, surface)
    big_fires = big_fires.drop_duplicates(
        subset=['commune', 'date_alerte', 'x', 'y', 'surface_ha'],
        keep='first'
    ).reset_index(drop=True)
    
    analysis_results = []
    if len(big_fires) > 0:
        with st.spinner('Analyse en cours...'):
            for _, big_fire in big_fires.iterrows():
                result = analyze_fires_before_big_fire(
                    df_filtered, big_fire, temporal_window, 
                    buffer_radius, min_fires_before
                )
                analysis_results.append(result)
    
    valid_count = sum(1 for r in analysis_results if r['condition_met'])
    
    if len(big_fires) == 0:
        st.warning("Aucun grand feu trouvé dans la période sélectionnée")
        return
    
    if valid_count == 0:
        st.warning("Aucun grand feu ne répond aux critères. Ajustez les paramètres.")
        return
    
    # ========== STATISTIQUES CARTOGRAPHIQUES ==========
    st.subheader("Statistiques Cartographiques")
    
    total_small = sum(r['small_fires_count'] for r in analysis_results if r['condition_met'])
    total_medium = sum(r['medium_fires_count'] for r in analysis_results if r['condition_met'])
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("Grands feux validés", valid_count)
    with col_stat2:
        st.metric("Buffers affichés", valid_count)
    with col_stat3:
        st.metric("Total petits feux", total_small)
    with col_stat4:
        st.metric("Total moyens feux", total_medium)
    
    st.markdown("---")
    
    # Préparer les données de résultats
    results_data = []
    for idx, result in enumerate(analysis_results):
        if result['condition_met']:
            bf = big_fires.iloc[idx]
            results_data.append({
                'Date': bf['date_alerte'].strftime('%d/%m/%Y'),
                'DateTime': bf['date_alerte'].strftime('%d/%m/%Y %H:%M'),
                'Commune': bf['commune'],
                'Surface (ha)': bf['surface_ha'],
                'Petits feux': result['small_fires_count'],
                'Moyens feux': result['medium_fires_count'],
                'Total buffer': len(result['fires_in_buffer']),
                'Tendance': result['trend']
            })
    
    results_df = pd.DataFrame(results_data)
    valid_indices = [i for i, r in enumerate(analysis_results) if r['condition_met']]
    
    # ========== LIGNE 1 : DISTRIBUTION + CARTE ==========
    st.header("Distribution des Incendies et Carte")
    col1_1, col1_2 = st.columns([1, 1])
    
    with col1_1:
        st.subheader("Distribution des incendies")
        
        fig_pie = create_pie_chart(df_filtered)
        st.plotly_chart(fig_pie, width='stretch')
        
        fig_line = create_line_chart(df_filtered)
        st.plotly_chart(fig_line, width='stretch')
    
    with col1_2:
        st.subheader("Carte Interactive")
        st.caption(f"**Rouge** : Grands feux | **Zone** : Buffer **{buffer_radius}** km")
        
        map_fig = create_map(df_filtered, big_fires, analysis_results, buffer_radius)
        st.plotly_chart(map_fig, width='stretch')
    
    st.markdown("---")
    
    # ========== LIGNE 2 : ÉVOLUTION TEMPORELLE ==========
    st.header("Évolution et Détails")
    
    st.subheader("Évolution Temporelle des Petits Feux")
    st.caption("Visualisez l'accumulation progressive des petits feux avant la survenue d'un grand feu")
    
    selected_fire_idx = st.selectbox(
        "Choisir un grand feu à analyser",
        range(len(results_data)),
        format_func=lambda x: f"{results_data[x]['Commune']} - {results_data[x]['DateTime']} - {results_data[x]['Surface (ha)']:.1f} ha ({results_data[x]['Petits feux']} petits feux avant)",
        key='select_fire_temporal'
    )
    
    actual_idx = valid_indices[selected_fire_idx]
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
        st.plotly_chart(fig_time, width='stretch')
    else:
        st.info("Aucun petit feu dans la fenêtre temporelle")
    
    # ========== ANALYSE TENDANCES CROISSANTES ==========
    st.markdown("---")
    st.subheader("Analyse des Tendances Croissantes")
    
    if st.button("Afficher les communes à tendance croissante", width='stretch', type="primary"):
        # Filtrer les feux avec tendance croissante
        communes_croissance = []
        for idx, result in enumerate(analysis_results):
            if result['condition_met'] and result['trend'] == 'Croissance':
                bf = big_fires.iloc[idx]
                communes_croissance.append({
                    'Commune': bf['commune'],
                    'Date': bf['date_alerte'].strftime('%d/%m/%Y'),
                    'DateTime': bf['date_alerte'].strftime('%d/%m/%Y %H:%M'),
                    'Surface (ha)': bf['surface_ha'],
                    'Petits feux': result['small_fires_count'],
                    'Moyens feux': result['medium_fires_count'],
                    'Total': result['small_fires_count'] + result['medium_fires_count']
                })
        
        if communes_croissance:
            st.success(f"{len(communes_croissance)} grand(s) feu(x) avec tendance croissante détecté(s)")
            
            # Créer un DataFrame et trier
            df_croissance = pd.DataFrame(communes_croissance)
            df_croissance = df_croissance.sort_values('Total', ascending=True)  # True pour avoir les plus grands en haut
            
            # Layout en 3 colonnes
            col1, col2, col3 = st.columns([1.2, 1, 1])
            
            # ========== COLONNE 1: Graphique à barres empilées ==========
            with col1:
                # Créer le graphique à barres empilées
                fig_croissance = go.Figure()
                
                # Labels pour l'axe Y (Commune - Date)
                labels = [f"{row['Commune']}<br>{row['Date']}" for _, row in df_croissance.iterrows()]
                
                # Barres pour les petits feux
                fig_croissance.add_trace(go.Bar(
                    y=labels,
                    x=df_croissance['Petits feux'],
                    name='Petits feux',
                    orientation='h',
                    marker=dict(color='#F1E6C9'),
                    text=df_croissance['Petits feux'],
                    textposition='inside',
                    hovertemplate='<b>Petits feux</b>: %{x}<extra></extra>'
                ))
                
                # Barres pour les moyens feux
                fig_croissance.add_trace(go.Bar(
                    y=labels,
                    x=df_croissance['Moyens feux'],
                    name='Moyens feux',
                    orientation='h',
                    marker=dict(color='#ABDADC'),
                    text=df_croissance['Moyens feux'],
                    textposition='inside',
                    hovertemplate='<b>Moyens feux</b>: %{x}<extra></extra>'
                ))
                
                fig_croissance.update_layout(
                    title=dict(
                        text="Feux Précédant les<br>Grands Incendies",
                        x=0.5,
                        xanchor='center',
                        font=dict(size=14)
                    ),
                    barmode='stack',
                    xaxis=dict(title='Nombre de feux'),
                    yaxis=dict(title=''),
                    height=max(400, len(communes_croissance) * 50),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='closest',
                    margin=dict(l=10, r=10, t=80, b=40)
                )
                
                st.plotly_chart(fig_croissance, use_container_width=True)
            
            # ========== COLONNE 2: Graphique circulaire ==========
            with col2:
                # Calculer les totaux
                total_petits = sum(c['Petits feux'] for c in communes_croissance)
                total_moyens = sum(c['Moyens feux'] for c in communes_croissance)
                
                # Créer le pie chart
                fig_pie = go.Figure()
                
                fig_pie.add_trace(go.Pie(
                    labels=['Petits feux', 'Moyens feux'],
                    values=[total_petits, total_moyens],
                    marker=dict(colors=['#F1E6C9', '#ABDADC']),
                    textposition='inside',
                    textinfo='label+percent+value',
                    hovertemplate='<b>%{label}</b><br>Nombre: %{value}<br>Proportion: %{percent}<extra></extra>'
                ))
                
                fig_pie.update_layout(
                    title=dict(
                        text="Répartition des Feux<br>Précurseurs",
                        x=0.5,
                        xanchor='center',
                        font=dict(size=14)
                    ),
                    height=500,
                    margin=dict(l=10, r=10, t=80, b=40),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=0.05
                    )
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # ========== COLONNE 3: Carte des communes ==========
            with col3:
                fig_map = create_communes_croissance_map(big_fires, analysis_results)
                st.plotly_chart(fig_map, use_container_width=True)
            
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
    
    # ========== ANALYSE COMPARATIVE MULTI-FEUX ==========
    st.markdown("---")
    st.header("Analyse Comparative")
    st.subheader("Patterns d'Accumulation")
    
    fig_comparison = create_multi_fire_comparison(
        analysis_results, big_fires, temporal_window, 
        nb_feux=10, show_moyenne=False, show_variance=False
    )
    st.plotly_chart(fig_comparison, width='stretch')
    
    st.markdown("---")
    
    # ===== SÉLECTEUR DE DÉPARTEMENT (COMMUN AUX ANALYSES DE CORRÉLATION) =====
    st.header("Analyses de Corrélation")
    st.caption("Filtrer les analyses de corrélation par département")
    
    # Sélecteur de département pour filtrer TOUTES les analyses de corrélation
    departements_disponibles = sorted(df['depart'].dropna().astype(str).unique())
    departements_options = ["Tous"] + departements_disponibles
    
    selected_dept = st.selectbox(
        "Filtrer par département",
        options=departements_options,
        index=0,
        help="Sélectionnez un département spécifique ou 'Tous' pour l'analyse globale. Ce filtre s'applique à toutes les analyses de corrélation ci-dessous.",
        key='dept_correlation_filter'
    )
    
    # Filtrer les données par département si nécessaire
    if selected_dept != "Tous":
        df_filtered_dept = df_filtered[df_filtered['depart'].astype(str) == str(selected_dept)].copy()
        big_fires_dept = big_fires[big_fires['depart'].astype(str) == str(selected_dept)].copy()
        
        # Filtrer aussi analysis_results pour correspondre aux grands feux filtrés
        filtered_indices = big_fires_dept.index.tolist()
        analysis_results_dept = [analysis_results[i] for i in filtered_indices if i < len(analysis_results)]
        
        # Message informatif
        nb_feux_dept = len(df_filtered_dept)
        nb_grands_feux_dept = len(big_fires_dept)
        st.info(f"🔍 **Filtre actif : Département {selected_dept}** | {nb_feux_dept} incendies totaux | {nb_grands_feux_dept} grands feux")
    else:
        df_filtered_dept = df_filtered
        big_fires_dept = big_fires
        analysis_results_dept = analysis_results
        

    st.markdown("---")
    
    # ========== ANALYSE DE CORRÉLATION ==========
    st.subheader("Analyse de Corrélation: Petits Feux → Grands Feux")
    
    
    
    # Créer le tableau récapitulatif
    with st.spinner('Calcul des corrélations en cours...'):
        try:
            # Tableau récapitulatif
            st.subheader("Résumé des Corrélations")
            summary_df = create_correlation_summary_table(df_filtered_dept)
            
            # Appliquer un style au tableau pour les interprétations
            def color_interpretation(val):
                if '🟢' in str(val):  # Vert fort
                    return 'background-color: #d4edda; color: #155724; font-weight: bold'
                elif '🟡' in str(val):  # Jaune modéré
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold'
                elif '🔵' in str(val):  # Bleu faible
                    return 'background-color: #d1ecf1; color: #0c5460; font-weight: bold'
                elif '⚪' in str(val):  # Blanc très faible
                    return 'background-color: #e2e3e5; color: #383d41; font-weight: bold'
                return ''
            
            styled_df = summary_df.style.applymap(
                color_interpretation,
                subset=['Interprétation']
            )
            
            st.dataframe(
                styled_df,
                width='stretch',
                hide_index=True,
                height=200
            )
            
        except Exception as e:
            st.error(f"Erreur lors du calcul des corrélations: {str(e)}")
            st.warning("Vérifiez que vous avez suffisamment de données pour l'analyse de corrélation.")
    
    st.markdown("---")
    
    # ===== CORRÉLATIONS PARAMÈTRES ENVIRONNEMENTAUX → GRANDS FEUX =====
    st.subheader("Corrélations Paramètres Environnementaux → Grands Feux")
    st.caption("Analyse globale de la relation entre les conditions environnementales des petits feux et les surfaces des grands feux")
    
    with st.spinner('Calcul des corrélations paramétriques...'):
        # Calculer les corrélations globales (avec filtre département)
        global_param_corr = analyze_global_parameter_correlations(analysis_results, big_fires, departement=selected_dept)
        
        if global_param_corr and any(c['status'] == 'OK' for c in global_param_corr.values()):
            # Graphique des corrélations
            fig_global_corr = create_global_parameter_correlation_chart(global_param_corr, departement=selected_dept)
            st.plotly_chart(fig_global_corr, use_container_width=True)
            
            # Tableau des corrélations
            st.markdown("##### Tableau Détaillé des Corrélations Paramétriques")
            
            corr_table_data = []
            for param, corr_data in global_param_corr.items():
                if corr_data['status'] == 'OK':
                    friendly_name = PARAM_NAMES.get(param, param)
                    
                    # Calculer la corrélation maximale pour l'interprétation
                    max_corr = max(
                        abs(corr_data['pearson']),
                        abs(corr_data['spearman']),
                        abs(corr_data['mutual_info'])
                    )
                    
                    # Déterminer l'interprétation
                    if max_corr >= 0.7:
                        interpretation = "🟢 Forte"
                    elif max_corr >= 0.4:
                        interpretation = "🟡 Modérée"
                    elif max_corr >= 0.2:
                        interpretation = "🔵 Faible"
                    else:
                        interpretation = "⚪ Très faible"
                    
                    # Significativité
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
            
            # Style du tableau
            def color_correlation(val):
                try:
                    # Extraire le nombre avant la parenthèse
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
            
            def color_interpretation(val):
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
                color_interpretation,
                subset=['Interprétation']
            )
            
            st.dataframe(styled_global_corr, use_container_width=True, hide_index=True)
            
            # Légende
            st.caption(
                "**Légende** : "
                "**Pearson/Spearman** : ✓ = significatif (p < 0.05), ✗ = non significatif | "
                "**Info. Mutuelle** : quantification de l'information partagée | "
                "**N échantillons** : nombre de grands feux analysés"
            )
        else:
            st.warning("⚠️ Données insuffisantes pour calculer les corrélations paramétriques globales.")
    
    st.markdown("---")
    
    # ========== EXPORT ==========
    st.header("Export des Données")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        st.subheader("Excel Complet")
        st.caption("5 feuilles : Grands feux, Analyses, Buffers, Corrélation, Explications")
        if st.button("Générer Excel", width='stretch', key="btn_excel"):
            # Générer le tableau de corrélation
            try:
                correlation_summary = create_correlation_summary_table(df_filtered)
            except:
                correlation_summary = None
            
            excel_data = export_results(big_fires, analysis_results, correlation_summary)
            st.download_button(
                label="Télécharger Excel",
                data=excel_data,
                file_name=f"analyse_incendies_{annee_debut}_{annee_fin}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='stretch',
                key="dl_excel"
            )
    
    with export_col2:
        st.subheader("CSV Filtré")
        st.caption("Données par période sélectionnée")
        csv = export_csv(df_filtered)
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name=f"incendies_filtres_{annee_debut}_{annee_fin}.csv",
            mime="text/csv",
            width='stretch',
            key="dl_csv"
        )
    
    with export_col3:
        st.subheader("Résultats Analyse")
        st.caption("Tableau récapitulatif des analyses")
        csv_results = results_df.to_csv(index=False, sep=';')
        st.download_button(
            label="Télécharger Résultats",
            data=csv_results,
            file_name=f"resultats_analyse_{annee_debut}_{annee_fin}.csv",
            mime="text/csv",
            width='stretch',
            key="dl_results"
        )


if __name__ == "__main__":
    main()
