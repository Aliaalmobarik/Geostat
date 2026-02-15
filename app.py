# -*- coding: utf-8 -*-
"""
Application Streamlit - Analyse des Incendies en PACA
Analyse spatiale et temporelle avec visualisations améliorées
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_processing import (
    load_data, classify_fires, analyze_fires_before_big_fire
)
from modules.visualizations import (
    create_map, create_pie_chart, create_line_chart,
    create_trend_bar, create_scatter_plot, create_temporal_series,
    create_multi_fire_comparison, create_detail_fire_map,
    create_correlation_analysis_figure, create_correlation_summary_table,
    create_communes_croissance_map
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
        df = load_data('data/incendies_paca_2015_2022.csv')
        
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
        
        fig_time = create_temporal_series(daily_counts, selected_fire['date_alerte'], 
                                          selected_fire['commune'])
        st.plotly_chart(fig_time, width='stretch')
        
        # Métriques clés avec delta pour la tendance
        st.markdown("##### Statistiques du Grand Feu")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Petits feux", selected_result['small_fires_count'])
        with metric_col2:
            st.metric("Moyens feux", selected_result['medium_fires_count'])
        with metric_col3:
            total = selected_result['small_fires_count'] + selected_result['medium_fires_count']
            st.metric("Total feux avant", total)
        with metric_col4:
            st.metric("Surface grand feu", f"{selected_fire['surface_ha']:.1f} ha")
        
        # Tendance
        tendance = selected_result['trend']
        st.info(f"**Tendance avant le grand feu** : {tendance}")
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
    
    # ========== ANALYSE DE CORRÉLATION ==========
    st.header("Analyse de Corrélation: Petits Feux → Grands Feux")
    
    st.info("""
    **Analyse statistique de la relation entre petits et grands incendies**
    
    - **Cross-Correlation** : Mesure la similarité des séries temporelles avec différents décalages
    - **Granger Causality** : Teste si les petits feux permettent de prédire les grands feux
    - **Mutual Information** : Quantifie l'information partagée entre les deux types d'incendies
    """)
    
    # Créer les visualisations de corrélation
    with st.spinner('Calcul des corrélations en cours...'):
        try:
            correlation_fig = create_correlation_analysis_figure(df_filtered)
            st.plotly_chart(correlation_fig, width='stretch')
            
            st.markdown("---")
            
            # Tableau récapitulatif
            st.subheader("Résumé des Corrélations")
            summary_df = create_correlation_summary_table(df_filtered)
            
            # Appliquer un style au tableau
            st.dataframe(
                summary_df,
                width='stretch',
                hide_index=True,
                height=200
            )
            
        except Exception as e:
            st.error(f"Erreur lors du calcul des corrélations: {str(e)}")
            st.warning("Vérifiez que vous avez suffisamment de données pour l'analyse de corrélation.")
    
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
