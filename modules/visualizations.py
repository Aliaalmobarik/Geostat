"""
Module de visualisations améliorées
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Tuple
from .data_processing import lambert93_to_wgs84
from scipy import signal, stats
from sklearn.metrics import mutual_info_score
from statsmodels.tsa.stattools import grangercausalitytests
import os

# Import optionnel de geopandas
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

# Mapping des noms de paramètres vers des noms compréhensibles
PARAM_NAMES = {
    'mean_NDVI': 'NDVI moyen (Végétation)',
    'T': 'Température (°C)',
    'PRELIQ': 'Précipitations (mm)',
    'HU': 'Humidité (%)',
    'FF': 'Vitesse du vent (m/s)'
}


def create_map(df: pd.DataFrame, big_fires: pd.DataFrame = None, 
               analysis_results: List[Dict] = None, buffer_radius_km: float = 10) -> go.Figure:
    """Crée une carte interactive sans légende"""
    fig = go.Figure()
    
    # Variables pour le zoom automatique
    map_center_lat, map_center_lon = 43.7, 5.8
    map_zoom = 8
    
    # Charger et afficher le contour Prométhée
    if HAS_GEOPANDAS:
        try:
            parquet_path = 'data/promothee/contour_promothe.parquet'
            if os.path.exists(parquet_path):
                gdf = gpd.read_parquet(parquet_path)
                
                # Convertir en WGS84 si nécessaire
                if gdf.crs is not None and gdf.crs.to_string() != 'EPSG:4326':
                    gdf = gdf.to_crs('EPSG:4326')
                
                # Calculer les bounds pour le zoom automatique
                bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
                map_center_lon = (bounds[0] + bounds[2]) / 2
                map_center_lat = (bounds[1] + bounds[3]) / 2
                
                # Calculer le zoom en fonction de l'étendue
                lat_diff = bounds[3] - bounds[1]
                lon_diff = bounds[2] - bounds[0]
                max_diff = max(lat_diff, lon_diff)
                
                # Estimer le zoom (formule approximative)
                if max_diff > 5:
                    map_zoom = 6
                elif max_diff > 3:
                    map_zoom = 7
                elif max_diff > 1.5:
                    map_zoom = 8
                else:
                    map_zoom = 9
                
                # Parcourir toutes les géométries
                for geom in gdf.geometry:
                    if geom.geom_type == 'Polygon':
                        x, y = geom.exterior.xy
                        fig.add_trace(go.Scattermapbox(
                            lat=list(y),
                            lon=list(x),
                            mode='lines',
                            line=dict(width=2, color='black'),
                            fill='toself',
                            fillcolor='rgba(0, 0, 0, 0)',
                            name='Zone Prométhée',
                            hovertemplate='<b>Zone Prométhée</b><extra></extra>',
                            showlegend=False
                        ))
                    elif geom.geom_type == 'MultiPolygon':
                        for poly in geom.geoms:
                            x, y = poly.exterior.xy
                            fig.add_trace(go.Scattermapbox(
                                lat=list(y),
                                lon=list(x),
                                mode='lines',
                                line=dict(width=2, color='black'),
                                fill='toself',
                                fillcolor='rgba(0, 0, 0, 0)',
                                name='Zone Prométhée',
                                hovertemplate='<b>Zone Prométhée</b><extra></extra>',
                                showlegend=False
                            ))
        except Exception as e:
            print(f"Erreur lors du chargement du contour Prométhée: {e}")
    

    
    # Buffers pour chaque grand feu validé
    if analysis_results is not None and big_fires is not None and len(big_fires) > 0:
        for idx, result in enumerate(analysis_results):
            if result['condition_met']:
                bf = big_fires.iloc[idx]
                lat_bf, lon_bf = lambert93_to_wgs84(bf['x'], bf['y'])
                
                # Cercle pour le buffer
                radius_deg = buffer_radius_km * 0.009
                num_points = 50
                circle_lats = []
                circle_lons = []
                for i in range(num_points + 1):
                    angle = 2 * np.pi * i / num_points
                    circle_lat = lat_bf + radius_deg * np.cos(angle)
                    circle_lon = lon_bf + radius_deg * np.sin(angle) / 0.72
                    circle_lats.append(circle_lat)
                    circle_lons.append(circle_lon)
                
                fig.add_trace(go.Scattermapbox(
                    lat=circle_lats,
                    lon=circle_lons,
                    mode='lines',
                    line=dict(width=3, color='rgba(255, 100, 0, 0.8)'),
                    fill='toself',
                    fillcolor='rgba(255, 100, 0, 0.15)',
                    hoverinfo='skip',
                    showlegend=False
                ))
    
    # Grands feux validés
    if analysis_results is not None and big_fires is not None and len(big_fires) > 0:
        lats_bf, lons_bf = [], []
        bf_communes = []
        bf_surfaces = []
        bf_dates = []
        for idx, result in enumerate(analysis_results):
            if result['condition_met']:
                bf = big_fires.iloc[idx]
                lat, lon = lambert93_to_wgs84(bf['x'], bf['y'])
                lats_bf.append(lat)
                lons_bf.append(lon)
                bf_communes.append(bf['commune'])
                bf_surfaces.append(bf['surface_ha'])
                bf_dates.append(bf['date_alerte'].strftime('%d/%m/%Y'))
        
        if len(lats_bf) > 0:
            fig.add_trace(go.Scattermapbox(
                lat=lats_bf,
                lon=lons_bf,
                mode='markers',
                marker=dict(
                    size=20, 
                    color='#1E5A96', 
                    symbol='star'
                ),
                text=bf_communes,
                hovertemplate='<b>GRAND FEU</b><br>%{text}<br>Date: %{customdata[0]}<br>Surface: %{customdata[1]:.2f} ha<extra></extra>',
                customdata=list(zip(bf_dates, bf_surfaces)),
                showlegend=False
            ))
    
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=map_center_lat, lon=map_center_lon),
            zoom=map_zoom
        ),
        height=700,
        margin={"r": 0, "t": 10, "l": 0, "b": 0},
        showlegend=False
    )
    
    return fig


def create_pie_chart(df: pd.DataFrame, title: str = "Répartition par catégorie") -> go.Figure:
    """Crée un graphique circulaire amélioré"""
    cat_counts = df['categorie'].value_counts()
    colors = {'Petit feu': '#F1E6C9', 'Feu moyen': '#ABDADC', 'Grand feu': '#1E5A96'}
    
    fig = px.pie(
        values=cat_counts.values, 
        names=cat_counts.index,
        title=title,
        height=400,
        color=cat_counts.index,
        color_discrete_map=colors
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def create_line_chart(df: pd.DataFrame, title: str = "Évolution annuelle") -> go.Figure:
    """Crée un graphique linéaire amélioré"""
    yearly = df.groupby(['annee', 'categorie']).size().reset_index(name='count')
    colors = {'Petit feu': '#F1E6C9', 'Feu moyen': '#ABDADC', 'Grand feu': '#1E5A96'}
    
    fig = px.line(
        yearly, 
        x='annee', 
        y='count', 
        color='categorie',
        title=title,
        height=350,
        color_discrete_map=colors,
        markers=True
    )
    fig.update_layout(
        xaxis_title="Année",
        yaxis_title="Nombre d'incendies",
        hovermode='x unified'
    )
    return fig


def create_trend_bar(df_filtered: pd.DataFrame, temporal_window: int) -> go.Figure:
    """Crée un graphique de tendance globale des petits et moyens feux"""
    import numpy as np
    
    # Filtrer petits et moyens feux
    petits_feux = df_filtered[df_filtered['categorie'] == 'Petit feu'].copy()
    moyens_feux = df_filtered[df_filtered['categorie'] == 'Feu moyen'].copy()
    
    # Grouper par année
    petits_par_annee = petits_feux.groupby('annee').size().reset_index(name='Nombre')
    moyens_par_annee = moyens_feux.groupby('annee').size().reset_index(name='Nombre')
    
    fig = go.Figure()
    
    # Ligne pour les petits feux
    fig.add_trace(go.Scatter(
        x=petits_par_annee['annee'],
        y=petits_par_annee['Nombre'],
        name='Petits feux',
        mode='lines+markers',
        line=dict(color='#2E8B9E', width=3),
        marker=dict(size=10, color='#2E8B9E', line=dict(color='white', width=2))
    ))
    
    # Ligne pour les moyens feux
    fig.add_trace(go.Scatter(
        x=moyens_par_annee['annee'],
        y=moyens_par_annee['Nombre'],
        name='Moyens feux',
        mode='lines+markers',
        line=dict(color='#1E5A96', width=3),
        marker=dict(size=10, color='#1E5A96', line=dict(color='white', width=2))
    ))
    
    # Calculer la tendance globale (petits + moyens)
    all_years = sorted(set(petits_par_annee['annee'].tolist() + moyens_par_annee['annee'].tolist()))
    petits_dict = dict(zip(petits_par_annee['annee'], petits_par_annee['Nombre']))
    moyens_dict = dict(zip(moyens_par_annee['annee'], moyens_par_annee['Nombre']))
    
    total_par_annee = [petits_dict.get(y, 0) + moyens_dict.get(y, 0) for y in all_years]
    
    if len(all_years) > 1:
        x = np.array(all_years)
        y = np.array(total_par_annee)
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        # Ligne de tendance globale
        fig.add_trace(go.Scatter(
            x=all_years,
            y=p(x),
            name='Tendance globale',
            mode='lines',
            line=dict(color='#1E5A96', width=4, dash='dash'),
            showlegend=True
        ))
        
        # Déterminer si croissance ou décroissance
        tendance_text = "CROISSANCE" if z[0] > 0 else "DÉCROISSANCE"
        tendance_color = '#2E8B9E' if z[0] > 0 else '#1E5A96'
    else:
        tendance_text = "Données insuffisantes"
        tendance_color = '#95A5A6'
    
    fig.update_layout(
        title={
            'text': f"Tendance Globale - Fenêtre: {temporal_window} jours | {tendance_text}",
            'font': {'size': 16, 'color': tendance_color, 'family': 'Arial Black'}
        },
        xaxis_title="Année",
        yaxis_title="Nombre de feux (toutes communes)",
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(size=12)
        ),
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11),
        xaxis=dict(dtick=1),
        hovermode='x unified'
    )
    
    return fig


def create_scatter_plot(df_filtered: pd.DataFrame, commune: str, temporal_window: int) -> go.Figure:
    """Crée un graphique montrant le nombre de petits feux dans le temps avec les grands feux et tendance"""
    import numpy as np
    from datetime import timedelta
    
    # Filtrer les données de la commune sélectionnée
    df_commune = df_filtered[df_filtered['commune'] == commune].copy()
    
    # Filtrer les grands feux
    grands_feux = df_commune[
        (df_commune['categorie'] == 'Grand feu') &
        (df_commune['date_alerte'].notna())
    ].copy()
    
    # Récupérer tous les petits/moyens feux dans les fenêtres temporelles avant les grands feux
    feux_avant_list = []
    for _, grand_feu in grands_feux.iterrows():
        date_gf = grand_feu['date_alerte']
        start_date = date_gf - timedelta(days=temporal_window)
        
        # Filtrer les petits/moyens feux dans la fenêtre temporelle avant ce grand feu
        mask_temporal = (df_commune['date_alerte'] >= start_date) & (df_commune['date_alerte'] < date_gf)
        mask_categorie = df_commune['categorie'].isin(['Petit feu', 'Feu moyen'])
        feux_fenetre = df_commune[mask_temporal & mask_categorie].copy()
        
        feux_avant_list.append(feux_fenetre)
    
    # Combiner tous les feux des différentes fenêtres (en évitant les doublons)
    if len(feux_avant_list) > 0:
        feux_avant = pd.concat(feux_avant_list, ignore_index=True).drop_duplicates()
    else:
        feux_avant = pd.DataFrame()
    
    if len(feux_avant) == 0:
        # Afficher au moins les grands feux avec message
        fig = go.Figure()
        
        if len(grands_feux) > 0:
            # Marquer les grands feux même sans petits feux
            colors = ['#1E5A96', '#1E5A96', '#1E5A96']
            for idx, (_, grand_feu) in enumerate(grands_feux.iterrows()):
                date_gf = grand_feu['date_alerte']
                color_gf = colors[idx % len(colors)]
                
                fig.add_trace(go.Scatter(
                    x=[date_gf],
                    y=[1],
                    name=f'Grand Feu #{idx+1} ({grand_feu["surface_ha"]:.1f} ha)',
                    mode='markers+text',
                    marker=dict(
                        size=30,
                        color=color_gf,
                        symbol='star',
                        line=dict(color='#2C3E50', width=3)
                    ),
                    text=f'GF{idx+1}',
                    textposition='top center',
                    textfont=dict(size=12, color='#2C3E50', family='Arial Black'),
                    hovertemplate=f'<b>GRAND FEU #{idx+1}</b><br>Date: {date_gf.strftime("%d/%m/%Y")}<br>Surface: {grand_feu["surface_ha"]:.1f} ha<extra></extra>'
                ))
            
            fig.add_annotation(
                text=f"Aucun petit/moyen feu dans les fenêtres temporelles ({temporal_window} jours) avant les grands feux de {commune}<br>Seuls les grands feux sont affichés",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color='#1E5A96')
            )
        else:
            fig.add_annotation(
                text=f"Aucun feu trouvé pour {commune}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='#95A5A6')
            )
        
        fig.update_layout(
            title=f"Évolution des Petits/Moyens Feux - {commune}<br><sub>(Fenêtre: {temporal_window} jours avant les grands feux)</sub>",
            height=550,
            yaxis=dict(visible=False)
        )
        return fig
    
    # Grouper les feux par mois pour avoir une série temporelle
    feux_avant['annee_mois'] = feux_avant['date_alerte'].dt.to_period('M')
    feux_par_mois = feux_avant.groupby('annee_mois').size().reset_index(name='Nombre')
    feux_par_mois['date'] = feux_par_mois['annee_mois'].dt.to_timestamp()
    
    fig = go.Figure()
    
    # Ligne pour les petits/moyens feux par mois
    fig.add_trace(go.Scatter(
        x=feux_par_mois['date'],
        y=feux_par_mois['Nombre'],
        name='Nombre de petits/moyens feux par mois',
        mode='lines+markers',
        line=dict(color='#2E8B9E', width=3),
        marker=dict(size=8, color='#2E8B9E', line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(250, 137, 26, 0.2)',
        hovertemplate='<b>Petits/Moyens feux</b><br>Mois: %{x|%m/%Y}<br>Nombre: %{y}<extra></extra>'
    ))
    
    # Calculer la ligne de tendance globale
    if len(feux_par_mois) > 1:
        # Convertir les dates en timestamps pour la régression
        x_numeric = [(d - feux_par_mois['date'].min()).total_seconds() / 86400 for d in feux_par_mois['date']]
        x_array = np.array(x_numeric)
        y_array = feux_par_mois['Nombre'].values
        
        # Régression linéaire
        z = np.polyfit(x_array, y_array, 1)
        p = np.poly1d(z)
        
        # Déterminer la tendance
        if z[0] > 0:
            tendance_text = "TENDANCE CROISSANTE"
            tendance_color = '#2E8B9E'
        elif z[0] < 0:
            tendance_text = "TENDANCE DÉCROISSANTE"
            tendance_color = '#1E5A96'
        else:
            tendance_text = "TENDANCE STABLE"
            tendance_color = '#ABDADC'
        
        # Ligne de tendance globale
        fig.add_trace(go.Scatter(
            x=feux_par_mois['date'],
            y=p(x_array),
            name='Tendance globale',
            mode='lines',
            line=dict(color=tendance_color, width=4, dash='dash'),
            showlegend=True,
            hovertemplate='<b>Tendance</b><extra></extra>'
        ))
    else:
        tendance_text = "Données insuffisantes"
        tendance_color = '#95A5A6'
    
    # Marquer les grands feux
    if len(grands_feux) > 0:
        # Palette de couleurs pour les grands feux
        colors = ['#1E5A96', '#1E5A96', '#1E5A96', '#1E5A96', '#1E5A96', 
                  '#1E5A96', '#1E5A96', '#1E5A96', '#1E5A96', '#1E5A96']
        
        for idx, (_, grand_feu) in enumerate(grands_feux.iterrows()):
            date_gf = grand_feu['date_alerte']
            color_gf = colors[idx % len(colors)]
            
            # Trouver le nombre de feux au mois du grand feu pour positionner le marqueur
            mois_gf = date_gf.to_period('M')
            y_pos = feux_par_mois[feux_par_mois['annee_mois'] == mois_gf]['Nombre'].values
            y_pos = y_pos[0] if len(y_pos) > 0 else feux_par_mois['Nombre'].max()
            
            # Marquer le grand feu
            fig.add_trace(go.Scatter(
                x=[date_gf],
                y=[y_pos],
                name=f'Grand Feu #{idx+1} ({grand_feu["surface_ha"]:.1f} ha)',
                mode='markers+text',
                marker=dict(
                    size=25,
                    color=color_gf,
                    symbol='star',
                    line=dict(color='#2C3E50', width=3)
                ),
                text=f'GF{idx+1}',
                textposition='top center',
                textfont=dict(size=10, color='#2C3E50', family='Arial Black'),
                hovertemplate=f'<b>GRAND FEU #{idx+1}</b><br>Date: {date_gf.strftime("%d/%m/%Y")}<br>Surface: {grand_feu["surface_ha"]:.1f} ha<extra></extra>'
            ))
            
            # Ligne verticale à la date du grand feu
            fig.add_vline(
                x=date_gf.timestamp() * 1000,
                line_dash="dot",
                line_color=color_gf,
                line_width=2,
                opacity=0.6,
                annotation_text=f"GF#{idx+1}",
                annotation_position="top"
            )
    
    fig.update_layout(
        title={
            'text': f"Évolution des Petits/Moyens Feux (dans fenêtres de {temporal_window}j avant GF) - {commune}<br><sub>({len(grands_feux)} grands feux | {len(feux_avant)} petits/moyens feux | {tendance_text})</sub>",
            'font': {'size': 16, 'color': tendance_color, 'family': 'Arial Black'}
        },
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)'
        ),
        yaxis=dict(
            title="Nombre de petits/moyens feux par mois", 
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)'
        ),
        height=550,
        showlegend=True,
        legend=dict(
            orientation="v", 
            yanchor="top", 
            y=1, 
            xanchor="left", 
            x=1.02,
            font=dict(size=10)
        ),
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11),
        hovermode='x unified'
    )
    
    return fig


def create_temporal_series(daily_counts: pd.DataFrame, fire_date: pd.Timestamp, 
                          commune: str, tendance: str = None, departement: str = None) -> go.Figure:
    """Crée une série temporelle claire avec cumul"""
    # Calcul du cumul
    daily_counts['Cumul'] = daily_counts['Nombre'].cumsum()
    
    # Calculer les dates de la fenêtre
    date_debut = daily_counts['date_only'].min()
    date_fin = fire_date
    nb_jours = (date_fin - date_debut).days
    total_feux = daily_counts['Nombre'].sum()
    
    fig = go.Figure()
    
    # Zone de remplissage pour le cumul (en arrière-plan)
    fig.add_trace(go.Scatter(
        x=daily_counts['date_only'],
        y=daily_counts['Cumul'],
        name='Accumulation des feux',
        mode='lines',
        line=dict(color='rgba(220, 20, 60, 0.3)', width=0),
        fill='tozeroy',
        fillcolor='rgba(220, 20, 60, 0.15)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Barres pour les feux quotidiens
    fig.add_trace(go.Bar(
        x=daily_counts['date_only'],
        y=daily_counts['Nombre'],
        name='Petits feux par jour',
        marker=dict(
            color='#F1E6C9',
            line=dict(color='#2E8B9E', width=1)
        ),
        opacity=0.8,
        hovertemplate='<b>Date: %{x|%d/%m/%Y}</b><br>Feux ce jour: %{y}<extra></extra>'
    ))
    
    # Ligne pour le cumul (épaisse et bien visible)
    fig.add_trace(go.Scatter(
        x=daily_counts['date_only'],
        y=daily_counts['Cumul'],
        name='Cumul total de feux',
        mode='lines+markers',
        line=dict(color='#1E5A96', width=4),
        marker=dict(size=10, color='#1E5A96', line=dict(color='white', width=2)),
        hovertemplate='<b>Date: %{x|%d/%m/%Y}</b><br>Cumul: %{y} feux<extra></extra>'
    ))
    
    # Ligne verticale pour la date du grand feu
    fig.add_vline(
        x=fire_date.timestamp() * 1000,
        line_dash="dash",
        line_color="#1E5A96",
        line_width=3,
        annotation_text="GRAND FEU",
        annotation_position="top",
        annotation=dict(
            font=dict(size=12, color='#1E5A96', family='Arial Black'),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#1E5A96',
            borderwidth=2
        )
    )
    
    # Annotation pour le total final
    fig.add_annotation(
        x=daily_counts['date_only'].iloc[-1],
        y=daily_counts['Cumul'].iloc[-1],
        text=f"Total: {total_feux} feux",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='#1E5A96',
        ax=-50,
        ay=-40,
        font=dict(size=12, color='#1E5A96', family='Arial Black'),
        bgcolor='rgba(255, 255, 255, 0.9)',
        bordercolor='#1E5A96',
        borderwidth=2
    )
    
    # Construire le titre avec tendance et département
    titre_parts = [f"Tendance: {tendance}" if tendance else None,
                   commune,
                   f"Département {departement}" if departement else None]
    titre_parts = [p for p in titre_parts if p]  # Filtrer les None
    titre_principal = " - ".join(titre_parts)
    
    fig.update_layout(
        title={
            'text': f"{titre_principal}<br><sub>Fenêtre d'analyse: {date_debut.strftime('%d/%m/%Y')} → {date_fin.strftime('%d/%m/%Y')} ({nb_jours} jours) | {total_feux} petits feux</sub>",
            'font': {'size': 16, 'color': "#1E5A96", 'family': 'Arial'}
        },
        xaxis=dict(
            title="<b>Date</b>",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            tickformat='%d/%m/%Y'
        ),
        yaxis=dict(
            title="<b>Nombre de feux par jour</b>",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            rangemode='tozero'
        ),
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(size=11),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#CCCCCC',
            borderwidth=1
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(248, 248, 248, 0.8)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11)
    )
    
    return fig


def create_parameter_trends_chart(df_trends: pd.DataFrame, trends_summary: Dict, 
                                   commune: str) -> go.Figure:
    """
    Crée un graphique multi-axes pour visualiser les tendances des paramètres
    environnementaux avant un grand feu
    
    Args:
        df_trends: DataFrame avec les moyennes par période
        trends_summary: Dict avec les statistiques de tendance
        commune: Nom de la commune
    
    Returns:
        Figure plotly avec subplots
    """
    from plotly.subplots import make_subplots
    
    params = [p for p in df_trends.columns if p != 'periode']
    n_params = len(params)
    
    if n_params == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Créer subplots (1 ligne, n_params colonnes)
    subplot_titles = [
        PARAM_NAMES.get(param, param).replace(" (", "<br>(")
        for param in params
    ]

    fig = make_subplots(
        rows=1, 
        cols=n_params,
        subplot_titles=subplot_titles,
        horizontal_spacing=0.08
    )
    
    colors = ['#1E5A96', '#2E8B9E', '#4A7BA7', '#6B8FC4', '#5B7A99', '#3A6F89', '#2F7A8F', '#4A9B8E']
    
    for idx, param in enumerate(params):
        row = 1
        col = idx + 1
        
        friendly_name = PARAM_NAMES.get(param, param)
        values = df_trends[param].values
        periods = df_trends['periode'].values
        
        # Ligne avec marqueurs
        fig.add_trace(
            go.Scatter(
                x=periods,
                y=values,
                mode='lines+markers',
                name=friendly_name,
                line=dict(color=colors[idx % len(colors)], width=3),
                marker=dict(size=10, line=dict(color='white', width=2)),
                showlegend=False,
                hovertemplate=f'<b>{friendly_name}</b><br>Période: %{{x}}<br>Valeur: %{{y:.2f}}<extra></extra>'
            ),
            row=row, col=col
        )
        
        # Ajouter ligne de tendance
        if param in trends_summary:
            x_num = np.arange(len(values))
            trend_line = trends_summary[param]['slope'] * x_num + (values[0] - trends_summary[param]['slope'] * 0)
            
            fig.add_trace(
                go.Scatter(
                    x=periods,
                    y=trend_line,
                    mode='lines',
                    line=dict(color=colors[idx % len(colors)], width=2, dash='dash'),
                    showlegend=False,
                    hoverinfo='skip',
                    opacity=0.5
                ),
                row=row, col=col
            )
            
            # Annotation de tendance
            direction = trends_summary[param]['direction']
            variation = trends_summary[param]['variation_pct']
            
            if direction == "Croissance":
                arrow_symbol = "↗"
                color = "#27AE60"
            elif direction == "Décroissance":
                arrow_symbol = "↘"
                color = "#E74C3C"
            else:
                arrow_symbol = "→"
                color = "#95A5A6"
            
            fig.add_annotation(
                text=f"{arrow_symbol} {variation:+.1f}%",
                xref=f"x{idx+1}", yref=f"y{idx+1}",
                x=periods[-1], y=values[-1],
                showarrow=False,
                font=dict(size=10, color=color, family='Arial Black'),
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor=color,
                borderwidth=1,
                xanchor='left',
                xshift=5
            )
    
    # Mise à jour du layout
    fig.update_xaxes(showgrid=True, gridcolor='rgba(200, 200, 200, 0.3)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(200, 200, 200, 0.3)')
    
    fig.update_layout(
        title={
            'text': f"Tendances des Paramètres Environnementaux - {commune}<br><sub>Évolution avant le grand feu (par période)</sub>",
            'font': {'size': 16, 'color': '#2C3E50', 'family': 'Arial'}
        },
        height=460,
        margin=dict(l=20, r=20, t=135, b=40),
        plot_bgcolor='rgba(248, 248, 248, 0.8)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11),
        hovermode='closest'
    )
    
    return fig


def create_parameter_correlation_chart(correlations: Dict, commune: str) -> go.Figure:
    """
    Crée un graphique des corrélations entre paramètres des petits feux et le grand feu
    
    Args:
        correlations: Dict avec les corrélations pour chaque paramètre
        commune: Nom de la commune
    
    Returns:
        Figure plotly avec barres groupées
    """
    if not correlations:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Préparer les données
    params = []
    pearson_vals = []
    spearman_vals = []
    mi_vals = []
    
    for param, corr_data in correlations.items():
        if corr_data['status'] == 'OK':
            friendly_name = PARAM_NAMES.get(param, param)
            params.append(friendly_name)
            pearson_vals.append(corr_data['pearson'])
            spearman_vals.append(corr_data['spearman'])
            mi_vals.append(corr_data['mutual_info'])
    
    if not params:
        fig = go.Figure()
        fig.add_annotation(
            text="Données insuffisantes",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Créer le graphique avec barres groupées
    fig = go.Figure()
    
    # Pearson (corrélation linéaire)
    fig.add_trace(go.Bar(
        name='Pearson (Linéaire)',
        x=params,
        y=pearson_vals,
        marker=dict(color='#1E5A96'),
        hovertemplate='<b>%{x}</b><br>Pearson: %{y:.3f}<extra></extra>'
    ))
    
    # Spearman (corrélation monotone)
    fig.add_trace(go.Bar(
        name='Spearman (Monotone)',
        x=params,
        y=spearman_vals,
        marker=dict(color='#2E8B9E'),
        hovertemplate='<b>%{x}</b><br>Spearman: %{y:.3f}<extra></extra>'
    ))
    
    # Mutual Information
    fig.add_trace(go.Bar(
        name='Information Mutuelle',
        x=params,
        y=mi_vals,
        marker=dict(color='#4A7BA7'),
        hovertemplate='<b>%{x}</b><br>MI: %{y:.3f}<extra></extra>'
    ))
    
    # Lignes de référence
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    fig.add_hline(y=0.5, line_dash="dot", line_color="green", line_width=1, 
                  annotation_text="Corrélation modérée", annotation_position="right")
    fig.add_hline(y=-0.5, line_dash="dot", line_color="red", line_width=1)
    
    fig.update_layout(
        title={
            'text': f"Corrélations Paramètres → Grand Feu - {commune}<br><sub>Analyse de la relation temporelle entre les conditions des petits feux et le grand feu</sub>",
            'font': {'size': 16, 'color': '#2C3E50', 'family': 'Arial'}
        },
        xaxis=dict(
            title="<b>Paramètres Environnementaux</b>",
            tickangle=-45
        ),
        yaxis=dict(
            title="<b>Coefficient de Corrélation</b>",
            range=[-1, 1],
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)'
        ),
        barmode='group',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#CCCCCC',
            borderwidth=1
        ),
        plot_bgcolor='rgba(248, 248, 248, 0.8)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11),
        hovermode='x unified'
    )
    
    return fig


def create_global_parameter_correlation_chart(correlations: Dict, departement: str = None) -> go.Figure:
    """
    Crée un graphique des corrélations globales entre paramètres des petits feux 
    et les surfaces des grands feux
    
    Args:
        correlations: Dict avec les corrélations pour chaque paramètre
        departement: Code du département filtré (optionnel)
    
    Returns:
        Figure plotly avec barres groupées
    """
    if not correlations:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Préparer les données
    params = []
    pearson_vals = []
    spearman_vals = []
    mi_vals = []
    n_samples_list = []
    
    for param, corr_data in correlations.items():
        if corr_data['status'] == 'OK':
            friendly_name = PARAM_NAMES.get(param, param)
            params.append(friendly_name)
            pearson_vals.append(corr_data['pearson'])
            spearman_vals.append(corr_data['spearman'])
            mi_vals.append(corr_data['mutual_info'])
            n_samples_list.append(corr_data['n_samples'])
    
    if not params:
        fig = go.Figure()
        fig.add_annotation(
            text="Données insuffisantes",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Créer le graphique avec barres groupées
    fig = go.Figure()
    
    # Pearson (corrélation linéaire)
    fig.add_trace(go.Bar(
        name='Pearson (Linéaire)',
        x=params,
        y=pearson_vals,
        marker=dict(color='#1E5A96'),
        hovertemplate='<b>%{x}</b><br>Pearson: %{y:.3f}<extra></extra>'
    ))
    
    # Spearman (corrélation monotone)
    fig.add_trace(go.Bar(
        name='Spearman (Monotone)',
        x=params,
        y=spearman_vals,
        marker=dict(color='#2E8B9E'),
        hovertemplate='<b>%{x}</b><br>Spearman: %{y:.3f}<extra></extra>'
    ))
    
    # Mutual Information
    fig.add_trace(go.Bar(
        name='Information Mutuelle',
        x=params,
        y=mi_vals,
        marker=dict(color='#4A7BA7'),
        hovertemplate='<b>%{x}</b><br>MI: %{y:.3f}<extra></extra>'
    ))
    
    # Lignes de référence
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    fig.add_hline(y=0.5, line_dash="dot", line_color="green", line_width=1, 
                  annotation_text="Corrélation modérée", annotation_position="right")
    fig.add_hline(y=-0.5, line_dash="dot", line_color="red", line_width=1)
    
    # Titre avec nombre d'échantillons et département
    n_total = n_samples_list[0] if n_samples_list else 0
    
    # Construire le titre avec le département si spécifié
    if departement and departement != "Tous":
        dept_text = f"Département {departement}"
    else:
        dept_text = "Tous départements"
    
    fig.update_layout(
        title={
            'text': f"Corrélations Globales: Paramètres des Petits Feux → Surface des Grands Feux<br><sub>{dept_text} | Analyse sur {n_total} grands feux | Corrélation entre variations des paramètres et surfaces des GF</sub>",
            'font': {'size': 16, 'color': '#2C3E50', 'family': 'Arial'}
        },
        xaxis=dict(
            title="<b>Paramètres Environnementaux</b>",
            tickangle=-45
        ),
        yaxis=dict(
            title="<b>Coefficient de Corrélation</b>",
            range=[-1, 1],
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)'
        ),
        barmode='group',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#CCCCCC',
            borderwidth=1
        ),
        plot_bgcolor='rgba(248, 248, 248, 0.8)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11),
        hovermode='x unified'
    )
    
    return fig


def create_commune_chart(commune_pivot_top: pd.DataFrame) -> go.Figure:
    """Crée un graphique empilé par commune"""
    colors = {'Petit feu': '#F1E6C9', 'Feu moyen': '#ABDADC', 'Grand feu': '#1E5A96'}
    
    fig = px.bar(
        commune_pivot_top.reset_index(), 
        x='commune', 
        y=['Petit feu', 'Feu moyen', 'Grand feu'],
        title="Top 10 communes",
        labels={'commune': 'Commune', 'value': 'Nombre'},
        barmode='stack',
        height=400,
        color_discrete_map=colors
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def create_commune_before_chart(df_commune_analysis: pd.DataFrame) -> go.Figure:
    """Crée un graphique des feux avant grands feux par commune"""
    fig = px.bar(
        df_commune_analysis, 
        x='Commune', 
        y=['Petits', 'Moyens'],
        title="Feux avant grands feux par commune",
        labels={'value': 'Nombre', 'variable': 'Type'},
        barmode='group',
        height=350,
        color_discrete_map={'Petits': '#F1E6C9', 'Moyens': '#ABDADC'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def create_commune_evolution(df: pd.DataFrame, commune: str) -> go.Figure:
    """Crée un graphique d'évolution annuelle pour une commune"""
    df_commune = df[df['commune'] == commune]
    
    if len(df_commune) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée pour cette commune",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Comptage par année et catégorie
    yearly = df_commune.groupby(['annee', 'categorie']).size().reset_index(name='count')
    
    colors = {'Petit feu': '#F1E6C9', 'Feu moyen': '#ABDADC', 'Grand feu': '#1E5A96'}
    
    fig = go.Figure()
    
    for cat in ['Petit feu', 'Feu moyen', 'Grand feu']:
        data = yearly[yearly['categorie'] == cat]
        if len(data) > 0:
            fig.add_trace(go.Scatter(
                x=data['annee'],
                y=data['count'],
                name=cat,
                mode='lines+markers',
                line=dict(width=3, color=colors.get(cat, '#999')),
                marker=dict(size=10)
            ))
    
    fig.update_layout(
        title=f"Évolution annuelle des incendies - {commune}",
        xaxis_title="Année",
        yaxis_title="Nombre d'incendies",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    return fig


def create_heatmap_calendar(daily_counts: pd.DataFrame, fire_date: pd.Timestamp, commune: str) -> go.Figure:
    """Option 1: Carte de chaleur calendrier"""
    import numpy as np
    
    # Créer une grille de dates complète
    date_min = daily_counts['date_only'].min()
    date_max = fire_date
    date_range = pd.date_range(start=date_min, end=date_max, freq='D')
    
    # Fusionner avec les données pour avoir tous les jours
    full_data = pd.DataFrame({'date': date_range})
    full_data['date_only'] = full_data['date'].dt.date
    daily_counts_copy = daily_counts.copy()
    daily_counts_copy['date_only'] = pd.to_datetime(daily_counts_copy['date_only']).dt.date
    full_data = full_data.merge(daily_counts_copy[['date_only', 'Nombre']], on='date_only', how='left')
    full_data['Nombre'] = full_data['Nombre'].fillna(0)
    
    # Créer semaine et jour de la semaine
    full_data['semaine'] = full_data['date'].dt.isocalendar().week
    full_data['jour_semaine'] = full_data['date'].dt.dayofweek
    full_data['jour_nom'] = full_data['date'].dt.day_name()
    
    # Pivoter pour créer la heatmap
    pivot = full_data.pivot_table(values='Nombre', index='jour_semaine', columns='semaine', fill_value=0)
    
    # Labels des jours
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f'S{w}' for w in pivot.columns],
        y=jours,
        colorscale=[
            [0, '#FFFFFF'],      # Blanc pour 0
            [0.2, '#F1E6C9'],    # Beige très pâle
            [0.4, '#ABDADC'],    # Bleu clair
            [0.6, '#2E8B9E'],    # Orange
            [0.8, '#1E5A96'],    # Rouge clair
            [1.0, '#1E5A96']     # Rouge foncé
        ],
        hoverongaps=False,
        hovertemplate='<b>%{y}</b> (Semaine %{x})<br>Feux: %{z}<extra></extra>',
        colorbar=dict(title="Nombre<br>de feux")
    ))
    
    fig.update_layout(
        title=f"Carte de Chaleur Calendrier - {commune}<br><sub>Intensité des petits feux par jour avant le grand feu</sub>",
        xaxis_title="Semaines",
        yaxis_title="Jours de la semaine",
        height=350,
        font=dict(family='Arial', size=11)
    )
    
    return fig


def create_risk_gauges(daily_counts: pd.DataFrame, fire_date: pd.Timestamp, commune: str, temporal_window: int) -> go.Figure:
    """Option 2: Jauges de risque par période"""
    from plotly.subplots import make_subplots
    
    # Diviser en 4 périodes (semaines)
    date_min = daily_counts['date_only'].min()
    nb_jours_total = (fire_date - pd.to_datetime(date_min)).days
    jours_par_periode = max(7, nb_jours_total // 4)
    
    periodes = []
    for i in range(4):
        debut = fire_date - pd.Timedelta(days=(4-i) * jours_par_periode)
        fin = fire_date - pd.Timedelta(days=(3-i) * jours_par_periode)
        
        mask = (pd.to_datetime(daily_counts['date_only']) >= debut) & (pd.to_datetime(daily_counts['date_only']) < fin)
        nb_feux = daily_counts[mask]['Nombre'].sum()
        periodes.append({
            'nom': f'P{i+1}',
            'label': f'Période {i+1}<br>({debut.strftime("%d/%m")} - {fin.strftime("%d/%m")})',
            'feux': nb_feux
        })
    
    # Dernière période jusqu'au grand feu
    debut = fire_date - pd.Timedelta(days=jours_par_periode)
    mask = (pd.to_datetime(daily_counts['date_only']) >= debut) & (pd.to_datetime(daily_counts['date_only']) < fire_date)
    nb_feux = daily_counts[mask]['Nombre'].sum()
    periodes[-1] = {
        'nom': 'P4',
        'label': f'Période 4<br>({debut.strftime("%d/%m")} - {fire_date.strftime("%d/%m")})',
        'feux': nb_feux
    }
    
    # Créer les jauges
    fig = make_subplots(
        rows=1, cols=4,
        specs=[[{'type': 'indicator'}] * 4],
        subplot_titles=[p['label'] for p in periodes]
    )
    
    max_feux = max([p['feux'] for p in periodes]) if periodes else 10
    
    for i, periode in enumerate(periodes):
        # Couleur selon niveau
        if periode['feux'] < max_feux * 0.3:
            color = '#2E8B9E'  # Orange
        elif periode['feux'] < max_feux * 0.6:
            color = '#ABDADC'  # Bleu clair
        else:
            color = '#1E5A96'  # Rouge
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=periode['feux'],
            title={'text': f"{periode['feux']} feux"},
            gauge={
                'axis': {'range': [0, max_feux * 1.2]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, max_feux * 0.3], 'color': 'rgba(46, 204, 113, 0.2)'},
                    {'range': [max_feux * 0.3, max_feux * 0.6], 'color': 'rgba(243, 156, 18, 0.2)'},
                    {'range': [max_feux * 0.6, max_feux * 1.2], 'color': 'rgba(231, 76, 60, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_feux * 0.8
                }
            }
        ), row=1, col=i+1)
    
    fig.update_layout(
        title=f"Évolution du Niveau de Risque - {commune}<br><sub>Nombre de feux par période avant le grand feu</sub>",
        height=350,
        showlegend=False,
        font=dict(family='Arial', size=10)
    )
    
    return fig


def create_hourly_distribution(small_fires_df: pd.DataFrame, commune: str) -> go.Figure:
    """Option 3: Distribution horaire polaire"""
    # Extraire l'heure
    small_fires_df['heure'] = small_fires_df['date_alerte'].dt.hour
    hourly_counts = small_fires_df.groupby('heure').size().reset_index(name='count')
    
    # Créer un DataFrame complet avec toutes les heures
    all_hours = pd.DataFrame({'heure': range(24)})
    hourly_counts = all_hours.merge(hourly_counts, on='heure', how='left').fillna(0)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=hourly_counts['count'],
        theta=hourly_counts['heure'] * 15,  # Convertir en degrés (24h = 360°)
        fill='toself',
        fillcolor='rgba(255, 99, 71, 0.3)',
        line=dict(color='#1E5A96', width=4),
        marker=dict(size=10, color='#1E5A96', line=dict(color='white', width=2)),
        name='Nombre de feux',
        hovertemplate='<b>%{theta}°</b> (Heure: %{text})<br>Feux: %{r}<extra></extra>',
        text=[f'{h}h' for h in hourly_counts['heure']]
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=True,
                gridcolor='rgba(200, 200, 200, 0.5)'
            ),
            angularaxis=dict(
                tickmode='array',
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                ticktext=['0h', '3h', '6h', '9h', '12h', '15h', '18h', '21h'],
                direction='clockwise',
                rotation=90
            ),
            bgcolor='rgba(248, 248, 248, 0.5)'
        ),
        title=f"Distribution Horaire des Petits Feux - {commune}<br><sub>À quelles heures les feux se déclenchent-ils le plus ?</sub>",
        height=400,
        showlegend=False,
        font=dict(family='Arial', size=11)
    )
    
    return fig


def create_acceleration_chart(daily_counts: pd.DataFrame, fire_date: pd.Timestamp, commune: str) -> go.Figure:
    """Option 4: Vitesse d'accumulation (dérivée)"""
    import numpy as np
    
    # Calculer le cumul
    daily_counts_sorted = daily_counts.sort_values('date_only')
    daily_counts_sorted['Cumul'] = daily_counts_sorted['Nombre'].cumsum()
    
    # Calculer la dérivée (vitesse d'accumulation) sur fenêtre glissante de 3 jours
    window = 3
    vitesse = []
    dates_vitesse = []
    
    for i in range(window, len(daily_counts_sorted)):
        feux_avant = daily_counts_sorted.iloc[i-window:i]['Nombre'].sum()
        feux_apres = daily_counts_sorted.iloc[i:i+window]['Nombre'].sum() if i+window <= len(daily_counts_sorted) else daily_counts_sorted.iloc[i:]['Nombre'].sum()
        vitesse.append(feux_apres - feux_avant)
        dates_vitesse.append(daily_counts_sorted.iloc[i]['date_only'])
    
    vitesse_df = pd.DataFrame({'date': dates_vitesse, 'vitesse': vitesse})
    
    fig = go.Figure()
    
    # Colorier selon accélération/décélération
    colors = ['#2E8B9E' if v <= 0 else '#1E5A96' for v in vitesse_df['vitesse']]
    
    fig.add_trace(go.Bar(
        x=vitesse_df['date'],
        y=vitesse_df['vitesse'],
        marker=dict(color=colors, line=dict(color='#2C3E50', width=1)),
        name='Accélération',
        hovertemplate='<b>Date: %{x|%d/%m/%Y}</b><br>Variation: %{y:+.0f} feux<extra></extra>'
    ))
    
    # Ligne zéro
    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=1, opacity=0.5)
    
    # Ligne du grand feu
    fig.add_vline(
        x=fire_date.timestamp() * 1000,
        line_dash="dash",
        line_color="#1E5A96",
        line_width=3,
        annotation_text="GRAND FEU"
    )
    
    fig.update_layout(
        title=f"Vitesse d'Accumulation des Feux - {commune}<br><sub>Accélération (rouge) ou ralentissement (vert) du nombre de feux</sub>",
        xaxis_title="Date",
        yaxis_title="Variation du nombre de feux (sur 3 jours)",
        height=350,
        showlegend=False,
        plot_bgcolor='rgba(248, 248, 248, 0.8)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11),
        hovermode='x unified'
    )
    
    return fig


def create_multi_fire_comparison(analysis_results: list, big_fires: pd.DataFrame, 
                                temporal_window: int, nb_feux: int = 10, 
                                show_moyenne: bool = True, show_variance: bool = True) -> go.Figure:
    """Comparaison multi-feux améliorée avec moyenne, variance et paramètres environnementaux"""
    import numpy as np
    from plotly.subplots import make_subplots
    
    # Créer figure avec axe secondaire pour les paramètres
    fig = make_subplots(
        specs=[[{"secondary_y": True}]]
    )
    
    # Palette diversifiée avec contraste : Couleurs vives et saturées
    colors = [
        '#0052CC',  # Bleu vif
        '#00A4EF',  # Cyan lumineux
        '#20B2AA',  # Teal clair
        '#FF6B35',  # Orange vif
        '#F72585',  # Rose magenta
        '#00D4FF',  # Cyan électrique
        '#7209B7',  # Pourpre vibrant
        '#FF4136',  # Rouge criard
        '#2ECC40',  # Vert émeraude
        '#FFDC00',  # Jaune doré
        '#0074D9',  # Bleu cobalt
        '#FF851B',  # Orange saturé
        '#39CCCC',  # Teal éclatant
        '#B10DC9',  # Violet intense
        '#01FF70',  # Vert lime
        '#FF1493',  # Rose deep
        '#1E90FF',  # Dodger blue
        '#FFD700',  # Or pur
        '#00CED1',  # Turquoise vif
        '#FF6347'   # Tomate vive
    ]
    
    # Filtrer les feux valides
    feux_valides = [(i, r) for i, r in enumerate(analysis_results) if r.get('condition_met', False)][:nb_feux]
    
    # Stocker les données pour calculer moyenne, variance et paramètres
    all_curves = []
    max_days = temporal_window
    
    # Pour les paramètres environnementaux
    params_to_track = ['mean_NDVI', 'T', 'PRELIQ', 'HU', 'FF']
    params_data = {param: [] for param in params_to_track}
    
    # Tracer chaque feu
    for idx, (fire_idx, result) in enumerate(feux_valides):
        if 'small_fires' in result and len(result['small_fires']) > 0:
            small_fires = result['small_fires'].copy()
            fire_date = big_fires.iloc[fire_idx]['date_alerte']
            commune = big_fires.iloc[fire_idx]['commune']
            surface = big_fires.iloc[fire_idx]['surface_ha']
            
            # Calculer les jours relatifs (J-X avant le grand feu)
            small_fires['jours_avant'] = (fire_date - small_fires['date_alerte']).dt.days
            small_fires = small_fires[small_fires['jours_avant'] >= 0].sort_values('jours_avant', ascending=False)
            
            # Créer une série complète de J-max_days à J-0
            all_days = list(range(-max_days, 1))
            cumul_par_jour = []
            
            # Dictionnaires pour stocker les paramètres par jour
            params_par_jour = {param: [] for param in params_to_track}
            
            for jour in all_days:
                nb_feux_cumul = len(small_fires[small_fires['jours_avant'] >= abs(jour)])
                cumul_par_jour.append(nb_feux_cumul)
                
                # Calculer les moyennes des paramètres pour ce jour
                fires_ce_jour = small_fires[
                    (small_fires['jours_avant'] >= abs(jour)) & 
                    (small_fires['jours_avant'] < abs(jour) + 1 if jour < 0 else True)
                ]
                
                for param in params_to_track:
                    if param in small_fires.columns and len(fires_ce_jour) > 0:
                        param_mean = fires_ce_jour[param].mean()
                        params_par_jour[param].append(param_mean)
                    else:
                        params_par_jour[param].append(np.nan)
            
            # Stocker pour calcul de moyenne globale
            all_curves.append(cumul_par_jour)
            for param in params_to_track:
                params_data[param].append(params_par_jour[param])
            
            # Tracer la courbe d'accumulation
            fig.add_trace(go.Scatter(
                x=all_days,
                y=cumul_par_jour,
                mode='lines',
                name=f"{commune[:20]} ({result['small_fires_count']})",
                line=dict(width=2.5, color=colors[idx % len(colors)]),
                opacity=0.8,
                hovertemplate=f'<b>{commune}</b><br>GF: {surface:.1f} ha<br>J%{{x}}<br>Cumul: %{{y}}<extra></extra>',
                legendgroup=f'fire_{idx}',
                showlegend=True
            ), secondary_y=False)
    
    # Ajouter les courbes moyennes des paramètres environnementaux
    param_colors = {
        'mean_NDVI': '#2E8B9E',      # Teal pour végétation
        'T': '#1E5A96',              # Bleu primaire pour température
        'PRELIQ': '#4A7BA7',         # Bleu secondaire pour précipitations
        'HU': '#6B8FC4',             # Bleu clair pour humidité
        'FF': '#5B7A99'              # Bleu grisé pour vent
    }
    
    all_days = list(range(-max_days, 1))
    
    for param in params_to_track:
        if params_data[param] and any(params_data[param]):
            # Calculer la moyenne sur tous les feux pour ce paramètre
            param_mean_curve = []
            for day_idx in range(len(all_days)):
                day_values = [curve[day_idx] for curve in params_data[param] if day_idx < len(curve)]
                day_values = [v for v in day_values if not np.isnan(v)]
                if day_values:
                    param_mean_curve.append(np.mean(day_values))
                else:
                    param_mean_curve.append(np.nan)
            
            # Ne tracer que si on a des données
            if not all(np.isnan(v) for v in param_mean_curve):
                friendly_name = PARAM_NAMES.get(param, param)
                fig.add_trace(go.Scatter(
                    x=all_days,
                    y=param_mean_curve,
                    mode='lines',
                    name=friendly_name,
                    line=dict(width=2, color=param_colors.get(param, '#111111'), dash='dot'),
                    opacity=0.7,
                    hovertemplate=f'<b>{friendly_name}</b><br>J%{{x}}<br>Moyenne: %{{y:.2f}}<extra></extra>',
                    legendgroup='params',
                    showlegend=True
                ), secondary_y=True)
    
    # Calculer interprétation
    interpretation = "?"
    if len(all_curves) > 0:
        # Comparer la pente des 7 derniers jours vs le reste
        pentes_finales = []
        for curve in all_curves:
            if len(curve) >= 7:
                pente_finale = curve[-1] - curve[-7]  # Augmentation dans les 7 derniers jours
                pente_totale = curve[-1] - curve[0] if curve[0] != curve[-1] else 1
                ratio = pente_finale / pente_totale if pente_totale > 0 else 0
                pentes_finales.append(ratio)
        
        if pentes_finales:
            ratio_moyen = np.mean(pentes_finales)
            if ratio_moyen > 0.6:
                interpretation = "ESCALADE"
            elif ratio_moyen < 0.3:
                interpretation = "LINÉAIRE"
            else:
                interpretation = "MIXTE"
    
    # Ligne verticale pour J-0
    fig.add_vline(
        x=0, 
        line_dash="solid", 
        line_color="#1E5A96", 
        line_width=4,
        annotation_text="J-0",
        annotation_position="top",
        annotation=dict(
            font=dict(size=12, color='#1E5A96', family='Arial Black'),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#1E5A96',
            borderwidth=2
        )
    )
    
    # Statistiques dans le titre
    if len(all_curves) > 0:
        moyenne_finale = np.mean([c[-1] for c in all_curves])
        titre = f"Comparaison de {len(feux_valides)} Grands Feux | Pattern: <b>{interpretation}</b><br>"
        titre += f"<sub>Cumul moyen: {moyenne_finale:.1f} feux | Fenêtre: {temporal_window}j | Courbes pointillées = Paramètres environnementaux (axe droit)</sub>"
    else:
        titre = f"Comparaison des Patterns"
    
    # Mise à jour du layout avec axes secondaires
    fig.update_xaxes(
        title_text="Jours avant le grand feu",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.3)',
        zeroline=True,
        range=[-max_days-2, 2]
    )
    
    fig.update_yaxes(
        title_text="<b>Cumul de petits feux</b>",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.3)',
        rangemode='tozero',
        secondary_y=False
    )
    
    fig.update_yaxes(
        title_text="<b>Paramètres environnementaux (moyennes)</b>",
        showgrid=False,
        secondary_y=True
    )
    
    fig.update_layout(
        title={
            'text': titre,
            'font': {'size': 15, 'color': '#2C3E50'}
        },
        height=550,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            font=dict(size=9),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#CCCCCC',
            borderwidth=1
        ),
        plot_bgcolor='rgba(248, 248, 248, 0.9)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11),
        hovermode='closest'
    )
    
    return fig


def create_detail_fire_map(big_fire: pd.Series, small_medium_fires: pd.DataFrame, buffer_radius_km: float) -> go.Figure:
    """Crée une carte centrée sur un grand feu avec son buffer et les petits/moyens feux"""
    fig = go.Figure()
    
    # Coordonnées du grand feu
    lat_gf, lon_gf = lambert93_to_wgs84(big_fire['x'], big_fire['y'])
    
    # Cercle du buffer
    radius_deg = buffer_radius_km * 0.009
    num_points = 50
    circle_lats = []
    circle_lons = []
    for i in range(num_points + 1):
        angle = 2 * np.pi * i / num_points
        circle_lat = lat_gf + radius_deg * np.cos(angle)
        circle_lon = lon_gf + radius_deg * np.sin(angle) / 0.72
        circle_lats.append(circle_lat)
        circle_lons.append(circle_lon)
    
    # Tracer le buffer
    fig.add_trace(go.Scattermapbox(
        lat=circle_lats,
        lon=circle_lons,
        mode='lines',
        line=dict(width=4, color='rgba(255, 100, 0, 0.9)'),
        fill='toself',
        fillcolor='rgba(255, 100, 0, 0.2)',
        name=f'Buffer ({buffer_radius_km} km)',
        hovertemplate=f'<b>Zone de buffer</b><br>Rayon: {buffer_radius_km} km<extra></extra>'
    ))
    
    # Petits et moyens feux - séparer en deux traces pour avoir des symboles différents
    if len(small_medium_fires) > 0:
        # Séparer petits feux et feux moyens
        petits_feux = small_medium_fires[small_medium_fires['categorie'] == 'Petit feu']
        moyens_feux = small_medium_fires[small_medium_fires['categorie'] == 'Feu moyen']
        
        # Petits feux (triangles verts)
        if len(petits_feux) > 0:
            lats_p, lons_p, dates_p, surfaces_p = [], [], [], []
            for _, fire in petits_feux.iterrows():
                lat, lon = lambert93_to_wgs84(fire['x'], fire['y'])
                lats_p.append(lat)
                lons_p.append(lon)
                dates_p.append(fire['date_alerte'].strftime('%d/%m/%Y'))
                surfaces_p.append(fire['surface_ha'])
            
            fig.add_trace(go.Scattermapbox(
                lat=lats_p,
                lon=lons_p,
                mode='markers',
                marker=dict(
                    size=14, 
                    color='#00CC00', 
                    symbol='marker', 
                    opacity=1
                ),
                name='Petits feux',
                hovertemplate='<b>Petit feu</b><br>Date: %{customdata[0]}<br>Surface: %{customdata[1]:.2f} ha<extra></extra>',
                customdata=list(zip(dates_p, surfaces_p))
            ))
        
        # Feux moyens (cercles bleus)
        if len(moyens_feux) > 0:
            lats_m, lons_m, dates_m, surfaces_m = [], [], [], []
            for _, fire in moyens_feux.iterrows():
                lat, lon = lambert93_to_wgs84(fire['x'], fire['y'])
                lats_m.append(lat)
                lons_m.append(lon)
                dates_m.append(fire['date_alerte'].strftime('%d/%m/%Y'))
                surfaces_m.append(fire['surface_ha'])
            
            fig.add_trace(go.Scattermapbox(
                lat=lats_m,
                lon=lons_m,
                mode='markers',
                marker=dict(
                    size=10, 
                    color='#0099FF', 
                    symbol='circle', 
                    opacity=1
                ),
                name='Feux moyens',
                hovertemplate='<b>Feu moyen</b><br>Date: %{customdata[0]}<br>Surface: %{customdata[1]:.2f} ha<extra></extra>',
                customdata=list(zip(dates_m, surfaces_m))
            ))
    
    # Grand feu (étoile rouge)
    fig.add_trace(go.Scattermapbox(
        lat=[lat_gf],
        lon=[lon_gf],
        mode='markers',
        marker=dict(
            size=28, 
            color='#1E5A96', 
            symbol='star'
        ),
        name='Grand feu',
        hovertemplate=f'<b>GRAND FEU</b><br>{big_fire["commune"]}<br>Date: {big_fire["date_alerte"].strftime("%d/%m/%Y %H:%M")}<br>Surface: {big_fire["surface_ha"]:.2f} ha<extra></extra>'
    ))
    
    # Calculer le zoom automatique en fonction du buffer
    # Formule approximative : plus le buffer est grand, plus on dézoome
    if buffer_radius_km <= 10:
        auto_zoom = 10.5
    elif buffer_radius_km <= 20:
        auto_zoom = 9.5
    elif buffer_radius_km <= 30:
        auto_zoom = 9
    elif buffer_radius_km <= 50:
        auto_zoom = 8.5
    else:
        auto_zoom = 8
    
    fig.update_layout(
        title=dict(
            text=f"{big_fire['commune']} - {big_fire['date_alerte'].strftime('%d/%m/%Y')}",
            x=0.5,
            xanchor='center',
            font=dict(size=14, color='#333333')
        ),
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=lat_gf, lon=lon_gf),
            zoom=auto_zoom
        ),
        height=750,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#666666',
            borderwidth=1,
            font=dict(size=9, color='#333333')
        )
    )
    
    return fig


def prepare_time_series_for_correlation(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Prépare les séries temporelles pour l'analyse de corrélation entre petits et grands feux"""
    # Filtrer les dates valides
    df_valid = df[df['date_alerte'].notna()].copy()
    
    # Créer une série temporelle journalière
    df_valid['date_only'] = df_valid['date_alerte'].dt.date
    
    # Compter petits feux et grands feux par jour
    petits_feux = df_valid[df_valid['categorie'] == 'Petit feu'].groupby('date_only').size()
    grands_feux = df_valid[df_valid['categorie'] == 'Grand feu'].groupby('date_only').size()
    
    # Créer une plage de dates complète
    date_min = df_valid['date_only'].min()
    date_max = df_valid['date_only'].max()
    date_range = pd.date_range(start=date_min, end=date_max, freq='D')
    
    # Réindexer pour avoir toutes les dates (remplir avec 0)
    petits_series = petits_feux.reindex(date_range.date, fill_value=0)
    grands_series = grands_feux.reindex(date_range.date, fill_value=0)
    
    return petits_series, grands_series


def calculate_cross_correlation(df: pd.DataFrame, max_lag: int = 30) -> Tuple[np.ndarray, np.ndarray, int, float]:
    """
    Calcule la corrélation croisée entre petits et grands feux
    Retourne: (lags, correlations, best_lag, best_corr)
    """
    petits_series, grands_series = prepare_time_series_for_correlation(df)
    
    # Normaliser les séries
    petits_norm = (petits_series - petits_series.mean()) / (petits_series.std() + 1e-10)
    grands_norm = (grands_series - grands_series.mean()) / (grands_series.std() + 1e-10)
    
    # Calculer la corrélation croisée
    correlation = signal.correlate(petits_norm, grands_norm, mode='full', method='auto')
    lags = signal.correlation_lags(len(petits_norm), len(grands_norm), mode='full')
    
    # Normaliser la corrélation
    correlation = correlation / len(petits_norm)
    
    # Filtrer les lags pertinents
    mask = (lags >= -max_lag) & (lags <= max_lag)
    lags_filtered = lags[mask]
    correlation_filtered = correlation[mask]
    
    # Trouver le meilleur lag
    best_idx = np.argmax(np.abs(correlation_filtered))
    best_lag = lags_filtered[best_idx]
    best_corr = correlation_filtered[best_idx]
    
    return lags_filtered, correlation_filtered, best_lag, best_corr


def calculate_granger_causality(df: pd.DataFrame, max_lag: int = 15) -> Tuple[Dict, float, int]:
    """
    Teste la causalité de Granger entre petits et grands feux
    Retourne: (résultats, p-value minimale, meilleur lag)
    """
    petits_series, grands_series = prepare_time_series_for_correlation(df)
    
    # Créer un DataFrame pour le test
    data = pd.DataFrame({
        'grands_feux': grands_series.values,
        'petits_feux': petits_series.values
    })
    
    try:
        # Test de causalité: est-ce que petits_feux cause grands_feux?
        gc_results = grangercausalitytests(data[['grands_feux', 'petits_feux']], maxlag=max_lag, verbose=False)
        
        # Extraire les p-values pour chaque lag
        p_values = {}
        for lag in range(1, max_lag + 1):
            # Utiliser le test F
            p_value = gc_results[lag][0]['ssr_ftest'][1]
            p_values[lag] = p_value
        
        # Trouver le meilleur lag (p-value la plus faible)
        best_lag = min(p_values, key=p_values.get)
        min_p_value = p_values[best_lag]
        
        return p_values, min_p_value, best_lag
    except Exception as e:
        # En cas d'erreur, retourner des valeurs par défaut
        return {}, 1.0, 0


def calculate_mutual_information(df: pd.DataFrame) -> Tuple[float, List[float], List[int]]:
    """
    Calcule l'information mutuelle entre petits et grands feux avec différents décalages
    Retourne: (meilleure MI, liste des MI, liste des lags)
    """
    petits_series, grands_series = prepare_time_series_for_correlation(df)
    
    lags_to_test = list(range(0, 31, 1))
    mi_scores = []
    
    for lag in lags_to_test:
        if lag == 0:
            # Pas de décalage
            mi = mutual_info_score(petits_series, grands_series)
        elif lag > 0:
            # Décaler les petits feux vers l'avant (petits feux arrivent avant grands feux)
            petits_shifted = petits_series[:-lag]
            grands_shifted = grands_series[lag:]
            mi = mutual_info_score(petits_shifted, grands_shifted)
        
        mi_scores.append(mi)
    
    best_idx = np.argmax(mi_scores)
    best_mi = mi_scores[best_idx]
    best_lag = lags_to_test[best_idx]
    
    return best_mi, mi_scores, lags_to_test


def create_correlation_analysis_figure(df: pd.DataFrame) -> go.Figure:
    """
    Crée une figure avec 3 graphiques de corrélation en colonnes:
    1. Cross-Correlation
    2. Granger Causality
    3. Mutual Information
    """
    from plotly.subplots import make_subplots
    
    # Calculer les corrélations
    lags_cc, corr_cc, best_lag_cc, best_corr_cc = calculate_cross_correlation(df)
    p_values_gc, min_p_gc, best_lag_gc = calculate_granger_causality(df)
    best_mi, mi_scores, lags_mi = calculate_mutual_information(df)
    
    # Créer la figure avec 3 sous-graphiques
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            'Cross-Correlation',
            'Granger Causality',
            'Mutual Information'
        ),
        specs=[[{'type': 'xy'}, {'type': 'indicator'}, {'type': 'xy'}]],
        horizontal_spacing=0.1
    )
    
    # 1. Cross-Correlation
    fig.add_trace(
        go.Scatter(
            x=lags_cc,
            y=corr_cc,
            mode='lines',
            line=dict(color='#3498DB', width=2),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.3)',
            name='Cross-Correlation',
            hovertemplate='Lag: %{x} jours<br>Corrélation: %{y:.3f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Marquer le meilleur lag
    fig.add_trace(
        go.Scatter(
            x=[best_lag_cc],
            y=[best_corr_cc],
            mode='markers',
            marker=dict(size=12, color='#E74C3C', symbol='star'),
            name=f'Max (lag={best_lag_cc})',
            hovertemplate=f'Meilleur lag: {best_lag_cc} jours<br>Corrélation: {best_corr_cc:.3f}<extra></extra>',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # 2. Granger Causality
    if p_values_gc:
        pvals_gc = list(p_values_gc.values())
        
        # Afficher seulement la p-value minimale (meilleure) sous forme d'indicateur
        color_gc = '#2E8B9E' if min_p_gc < 0.05 else '#1E5A96'
        
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=min_p_gc,
                title={'text': f"<span style='font-size:11px'>Lag: {best_lag_gc}j</span>", 'font': {'size': 11}},
                domain={'x': [0, 1], 'y': [0.15, 0.85]},
                gauge={
                    'axis': {'range': [0, 0.2], 'tickfont': {'size': 9}},
                    'bar': {'color': color_gc, 'thickness': 0.75},
                    'steps': [
                        {'range': [0, 0.05], 'color': 'rgba(39, 174, 96, 0.2)'},
                        {'range': [0.05, 0.2], 'color': 'rgba(230, 126, 34, 0.2)'}
                    ],
                    'threshold': {
                        'line': {'color': '#E74C3C', 'width': 2},
                        'thickness': 0.75,
                        'value': 0.05
                    }
                },
                number={'suffix': '', 'valueformat': '.4f', 'font': {'size': 28}}
            ),
            row=1, col=2
        )
    
    # 3. Mutual Information
    fig.add_trace(
        go.Scatter(
            x=lags_mi,
            y=mi_scores,
            mode='lines+markers',
            line=dict(color='#9B59B6', width=2),
            marker=dict(size=6, color='#9B59B6'),
            name='Mutual Information',
            hovertemplate='Lag: %{x} jours<br>MI: %{y:.4f}<extra></extra>',
            showlegend=False
        ),
        row=1, col=3
    )
    
    # Marquer le meilleur lag pour MI
    best_lag_mi = lags_mi[np.argmax(mi_scores)]
    fig.add_trace(
        go.Scatter(
            x=[best_lag_mi],
            y=[best_mi],
            mode='markers',
            marker=dict(size=12, color='#E74C3C', symbol='star'),
            name=f'Max (lag={best_lag_mi})',
            hovertemplate=f'Meilleur lag: {best_lag_mi} jours<br>MI: {best_mi:.4f}<extra></extra>',
            showlegend=False
        ),
        row=1, col=3
    )
    
    # Mise en forme
    fig.update_xaxes(title_text='Décalage (jours)', row=1, col=1)
    fig.update_xaxes(title_text='Décalage (jours)', row=1, col=3)
    
    fig.update_yaxes(title_text='Corrélation', row=1, col=1)
    fig.update_yaxes(title_text='Information Mutuelle', row=1, col=3)
    
    fig.update_layout(
        height=500,
        showlegend=False,
        title_text='<b>Analyse de Corrélation: Petits Feux → Grands Feux</b>',
        title_x=0.5,
        title_y=0.98,
        title_font=dict(size=16, color='#2C3E50'),
        plot_bgcolor='rgba(248, 248, 248, 0.9)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11),
        margin=dict(t=100, b=60, l=60, r=60)
    )
    
    # Ajuster les annotations des sous-titres pour éviter les chevauchements
    for i, annotation in enumerate(fig['layout']['annotations']):
        if i == 1:  # Granger Causality (milieu)
            annotation['y'] = 1.08  # Remonter le titre
            annotation['font'] = dict(size=12)
        else:
            annotation['font'] = dict(size=12)
    
    return fig


def create_correlation_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée un tableau récapitulatif des résultats de corrélation avec émojis
    """
    # Calculer les métriques
    lags_cc, corr_cc, best_lag_cc, best_corr_cc = calculate_cross_correlation(df)
    p_values_gc, min_p_gc, best_lag_gc = calculate_granger_causality(df)
    best_mi, mi_scores, lags_mi = calculate_mutual_information(df)
    
    # Déterminer la significativité avec émojis
    def interpret_cross_corr(corr):
        abs_corr = abs(corr)
        if abs_corr >= 0.7:
            return '🟢 Très forte'
        elif abs_corr >= 0.5:
            return '🟡 Forte'
        elif abs_corr >= 0.3:
            return '🔵 Modérée'
        else:
            return '⚪ Faible'
    
    def interpret_granger(p_value):
        if p_value < 0.01:
            return '🟢 Très significative'
        elif p_value < 0.05:
            return '🟡 Significative'
        elif p_value < 0.1:
            return '🔵 Marginale'
        else:
            return '⚪ Non significative'
    
    def interpret_mi(mi):
        if mi >= 0.15:
            return '🟢 Forte'
        elif mi >= 0.10:
            return '🟡 Modérée'
        elif mi >= 0.05:
            return '🔵 Faible'
        else:
            return '⚪ Très faible'
    
    def get_conclusion_cross_corr(corr):
        abs_corr = abs(corr)
        direction = 'positive' if corr > 0 else 'négative'
        if abs_corr >= 0.5:
            return f'Corrélation {direction} forte : les séries temporelles sont similaires'
        elif abs_corr >= 0.3:
            return f'Corrélation {direction} modérée : relation détectée'
        else:
            return f'Corrélation {direction} faible : peu de similarité'
    
    def get_conclusion_granger(p_value):
        if p_value < 0.05:
            return 'Les petits feux permettent de prédire les grands feux (relation causale)'
        elif p_value < 0.1:
            return 'Relation causale marginale : prédictibilité faible'
        else:
            return 'Pas de causalité détectée : les petits feux ne prédisent pas les grands feux'
    
    def get_conclusion_mi(mi):
        if mi >= 0.10:
            return 'Forte dépendance : information partagée importante entre les deux types'
        elif mi >= 0.05:
            return 'Dépendance modérée : information partagée détectée'
        else:
            return 'Indépendance : peu d\'information partagée'
    
    # Créer le tableau
    summary_data = {
        'Méthode': [
            'Cross-Correlation',
            'Granger Causality',
            'Mutual Information'
        ],
        'Valeur': [
            f'{best_corr_cc:.4f}',
            f'p = {min_p_gc:.4f}',
            f'{best_mi:.4f}'
        ],
        'Meilleur Lag (jours)': [
            best_lag_cc,
            best_lag_gc,
            lags_mi[np.argmax(mi_scores)]
        ],
        'Interprétation': [
            interpret_cross_corr(best_corr_cc),
            interpret_granger(min_p_gc),
            interpret_mi(best_mi)
        ],
        'Conclusion': [
            get_conclusion_cross_corr(best_corr_cc),
            get_conclusion_granger(min_p_gc),
            get_conclusion_mi(best_mi)
        ]
    }
    
    return pd.DataFrame(summary_data)


def create_communes_croissance_map(big_fires: pd.DataFrame, analysis_results: List[Dict]) -> go.Figure:
    """
    Crée une carte montrant les communes avec tendance croissante
    
    Args:
        big_fires: DataFrame des grands feux
        analysis_results: Résultats d'analyse avec tendances
        
    Returns:
        Figure Plotly avec carte interactive
    """
    fig = go.Figure()
    
    # Collecter les données des feux à tendance croissante
    lats = []
    lons = []
    communes = []
    dates = []
    surfaces = []
    petits_feux = []
    moyens_feux = []
    totaux = []
    
    for idx, result in enumerate(analysis_results):
        if result['condition_met'] and result['trend'] == 'Croissance':
            bf = big_fires.iloc[idx]
            lat, lon = lambert93_to_wgs84(bf['x'], bf['y'])
            
            lats.append(lat)
            lons.append(lon)
            communes.append(bf['commune'])
            dates.append(bf['date_alerte'].strftime('%d/%m/%Y'))
            surfaces.append(bf['surface_ha'])
            petits_feux.append(result['small_fires_count'])
            moyens_feux.append(result['medium_fires_count'])
            totaux.append(result['small_fires_count'] + result['medium_fires_count'])
    
    if lats:
        # Calculer le centre et le zoom
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        max_range = max(lat_range, lon_range)
        
        if max_range > 3:
            zoom = 7
        elif max_range > 1.5:
            zoom = 8
        elif max_range > 0.5:
            zoom = 9
        else:
            zoom = 10
        
        # Créer des marqueurs colorés par nombre total de feux
        max_total = max(totaux) if totaux else 1
        
        # Tailles proportionnelles à la surface
        max_surface = max(surfaces) if surfaces else 1
        sizes = [15 + (s / max_surface) * 25 for s in surfaces]
        
        # Texte hover personnalisé
        hover_texts = []
        for i in range(len(communes)):
            hover_text = (
                f"<b>{communes[i]}</b><br>"
                f"{dates[i]}<br>"
                f"Surface: {surfaces[i]:.1f} ha<br>"
                f"Petits feux: {petits_feux[i]}<br>"
                f"Moyens feux: {moyens_feux[i]}<br>"
                f"Total: {totaux[i]}"
            )
            hover_texts.append(hover_text)
        
        # Ajouter les marqueurs
        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers',
            marker=dict(
                size=sizes,
                color=totaux,
                colorscale=[[0, '#FF6B35'], [0.25, '#FFA500'], [0.5, '#FFD700'], [0.75, '#20B2AA'], [1, '#1E5A96']],
                cmin=min(totaux),
                cmax=max(totaux),
                colorbar=dict(
                    title="Total<br>feux",
                    thickness=15,
                    len=0.7,
                    x=1.02,
                    bgcolor='rgba(255, 255, 255, 0.9)',
                    bordercolor='#666666',
                    borderwidth=2,
                    titlefont=dict(color='#333333'),
                    tickfont=dict(color='#333333')
                ),
                opacity=0.9
            ),
            text=communes,
            hovertext=hover_texts,
            hoverinfo='text',
            showlegend=False
        ))
        
        # Configuration de la carte
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=center_lat, lon=center_lon),
                zoom=zoom
            ),
            margin=dict(l=0, r=0, t=40, b=0),
            height=600,
            title=dict(
                text="Localisation des Communes<br>à Tendance Croissante",
                x=0.5,
                xanchor='center',
                font=dict(size=14, color='#333333')
            )
        )
    else:
        # Carte vide si aucune donnée
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=43.7, lon=5.8),
                zoom=8
            ),
            margin=dict(l=0, r=0, t=40, b=0),
            height=600,
            title=dict(
                text="Aucune commune à tendance croissante",
                x=0.5,
                xanchor='center',
                font=dict(size=14, color='#333333')
            )
        )
    
    return fig


def create_comprehensive_fire_analysis(small_fires_df: pd.DataFrame, commune: str, fire_date: pd.Timestamp) -> go.Figure:
    """
    Crée un diagramme complet et unique montrant tous les paramètres ensemble:
    - X: Date des petits feux
    - Y primaire (gauche): Nombre de petits feux par jour (barres)
    - Y secondaire (droite): Tous les paramètres environnementaux (lignes colorées)
      * NDVI (vert)
      * Température (rouge)
      * Humidité (bleu)
      * Vent (violet)
      * Précipitations (orange)
    
    Args:
        small_fires_df: DataFrame des petits feux avant le grand feu
        commune: Nom de la commune
        fire_date: Date du grand feu
    
    Returns:
        Figure Plotly avec tous les paramètres ensemble
    """
    if len(small_fires_df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filtrer et préparer les données
    df_clean = small_fires_df[['date_alerte', 'surface_ha', 'mean_NDVI', 'T', 'PRELIQ', 'HU', 'FF']].copy()
    df_clean['date_only'] = pd.to_datetime(df_clean['date_alerte']).dt.date
    
    # Grouper par date pour obtenir le nombre de feux par jour et les moyennes des paramètres
    daily_stats = df_clean.groupby('date_only').agg({
        'surface_ha': ['count', 'sum', 'mean'],
        'mean_NDVI': 'mean',
        'T': 'mean',
        'PRELIQ': 'mean',
        'HU': 'mean',
        'FF': 'mean'
    }).reset_index()
    
    # Aplatir les colonnes multi-index
    daily_stats.columns = ['date_only', 'nb_feux', 'total_surface', 'mean_surface', 'ndvi', 'temp', 'precip', 'humidite', 'vent']
    daily_stats['date_only'] = pd.to_datetime(daily_stats['date_only'])
    daily_stats = daily_stats.sort_values('date_only')
    
    # Créer la figure avec axes secondaires
    fig = go.Figure()
    
    # Couleurs pour les paramètres
    param_colors = {
        'temp': '#FF4136',      # Rouge
        'humidite': '#0074D9',  # Bleu
        'vent': '#B10DC9',      # Violet
        'nb_feux': '#FA891A'    # Orange
    }
    
    param_names = {
        'temp': 'Température (°C)',
        'humidite': 'Humidité (%)',
        'vent': 'Vent (m/s)',
        'nb_feux': 'Nombre de Petits Feux'
    }
    
    # Styles de ligne
    dash_styles = {
        'temp': 'solid',
        'humidite': 'dash',
        'vent': 'dashdot',
        'nb_feux': 'longdash'
    }
    
    # Ajouter tous les paramètres comme lignes
    for param in ['temp', 'humidite', 'vent', 'nb_feux']:
        fig.add_trace(go.Scatter(
            x=daily_stats['date_only'],
            y=daily_stats[param] if param != 'nb_feux' else daily_stats['nb_feux'],
            name=param_names[param],
            mode='lines+markers',
            line=dict(
                color=param_colors[param],
                width=4 if param == 'nb_feux' else 3.5,
                dash=dash_styles[param]
            ),
            marker=dict(
                size=10 if param == 'nb_feux' else 8,
                line=dict(color='white', width=2.5),
                opacity=0.9,
                symbol='diamond' if param == 'nb_feux' else 'circle'
            ),
            yaxis='y1',
            hovertemplate=f'<b>{param_names[param]}</b><br>Date: %{{x|%d/%m/%Y}}<br>Valeur: %{{y:.2f}}<extra></extra>',
            showlegend=True
        ))
    
    # Ligne verticale pour le grand feu
    fig.add_vline(
        x=fire_date.timestamp() * 1000,
        line_dash="solid",
        line_color="#8B0000",
        line_width=5,
        annotation_text="GRAND FEU",
        annotation_position="top",
        annotation=dict(
            font=dict(size=13, color='white', family='Arial Black'),
            bgcolor='#8B0000',
            bordercolor='#FF0000',
            borderwidth=2,
            showarrow=True,
            arrowsize=2,
            arrowwidth=3,
            arrowcolor='#8B0000'
        )
    )
    
    # Annotations pour les noms des paramètres
    last_x = daily_stats['date_only'].iloc[-1]
    
    for param in ['temp', 'humidite', 'vent', 'nb_feux']:
        last_y = daily_stats[param].iloc[-1]
        fig.add_annotation(
            x=last_x,
            y=last_y,
            text=f"<b>{param_names[param].split('(')[0].strip()}</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor=param_colors[param],
            ax=40,
            ay=-20,
            font=dict(size=11, color=param_colors[param], family='Arial Black'),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor=param_colors[param],
            borderwidth=1.5,
            borderpad=4,
            xanchor='left',
            yanchor='bottom'
        )
    
    # Configuration du layout
    fig.update_layout(
        title={
            'text': f"<b>ANALYSE MÉTÉOROLOGIQUE - Petits Feux & Paramètres Clés</b><br><sub>{commune} | Température • Humidité • Vent</sub>",
            'font': {'size': 18, 'color': '#1a1a1a', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=10, family='Arial'),
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='#CCCCCC',
            borderwidth=1
        ),
        plot_bgcolor='rgba(250, 250, 252, 0.9)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=11, color='#333333'),
        hovermode='x unified',
        margin=dict(l=100, r=200, t=160, b=150),
        xaxis=dict(
            title="<b>Date</b>",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            gridwidth=1,
            tickformat='%d/%m/%Y',
            showline=True,
            linewidth=2,
            linecolor='#CCCCCC',
            mirror=True
        ),
        yaxis=dict(
            title="<b>Tous les Paramètres</b><br><sub>(Feux • Temp • Humidité • Vent)</sub>",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            gridwidth=1.5,
            showline=True,
            linewidth=2,
            linecolor='#333333',
            titlefont=dict(color='#333333', size=12, family='Arial Black'),
            dtick=5
        )
    )
    
    return fig
