"""
Module de traitement des données
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Tuple, Dict
import streamlit as st


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """Charge et prétraite les données d'incendies"""
    df = pd.read_csv(file_path, sep=',', encoding='utf-8', decimal=',', 
                     on_bad_lines='skip', engine='python')
    
    # Nettoyage et conversion des colonnes
    # Compatibilité avec les deux formats de fichier
    if 'join_surf_ha' in df.columns:
        df['surface_ha'] = pd.to_numeric(df['join_surf_ha'], errors='coerce')
    elif 'surf_ha' in df.columns:
        df['surface_ha'] = pd.to_numeric(df['surf_ha'], errors='coerce')
    
    df['annee'] = pd.to_numeric(df['annee'], errors='coerce')
    
    # Parse date d'alerte
    if 'join_Alert' in df.columns:
        df['date_alerte'] = pd.to_datetime(df['join_Alert'], format='%d/%m/%Y %H:%M', errors='coerce')
    elif 'Alerte' in df.columns:
        df['date_alerte'] = pd.to_datetime(df['Alerte'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    # Nettoyage des coordonnées
    if df['x_coord'].dtype == 'object':
        df['x'] = pd.to_numeric(df['x_coord'].str.replace(',', '.'), errors='coerce')
        df['y'] = pd.to_numeric(df['y_coord'].str.replace(',', '.'), errors='coerce')
    else:
        df['x'] = pd.to_numeric(df['x_coord'], errors='coerce')
        df['y'] = pd.to_numeric(df['y_coord'], errors='coerce')
    
    # Supprimer les lignes sans données essentielles
    df = df.dropna(subset=['surface_ha', 'annee', 'x', 'y'])
    
    # Convertir l'année en entier
    df['annee'] = df['annee'].astype(int)
    
    # Commune
    if 'join_Commu' in df.columns:
        df['commune'] = df['join_Commu'].fillna('Inconnue')
    elif 'Commune' in df.columns:
        df['commune'] = df['Commune'].fillna('Inconnue')
    
    # Conversion des paramètres environnementaux
    env_params = ['mean_NDVI', 'T', 'PRELIQ', 'HU', 'FF']
    for param in env_params:
        if param in df.columns:
            df[param] = pd.to_numeric(df[param], errors='coerce')
    
    return df


def calculate_distance_km(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calcule la distance euclidienne entre deux points en km (Lambert 93)"""
    distance_m = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance_m / 1000


@st.cache_data
def classify_fires(df: pd.DataFrame, seuil_petit: float, seuil_grand: float) -> pd.DataFrame:
    """Classifie les incendies par taille"""
    df = df.copy()
    
    conditions = [
        df['surface_ha'] < seuil_petit,
        df['surface_ha'] >= seuil_grand,
        (df['surface_ha'] >= seuil_petit) & (df['surface_ha'] < seuil_grand)
    ]
    choices = ['Petit feu', 'Grand feu', 'Feu moyen']
    df['categorie'] = np.select(conditions, choices, default='Non classé')
    
    return df


def get_fires_in_buffer(df: pd.DataFrame, center_x: float, center_y: float, 
                        radius_km: float) -> pd.DataFrame:
    """Trouve tous les incendies dans un buffer circulaire"""
    distances = np.sqrt((df['x'] - center_x)**2 + (df['y'] - center_y)**2) / 1000
    mask = distances <= radius_km
    result = df[mask].copy()
    result['distance_km'] = distances[mask]
    return result


def analyze_temporal_trend(fires_count: pd.Series) -> Tuple[str, float]:
    """Analyse la tendance temporelle du nombre d'incendies"""
    if len(fires_count) < 2:
        return "Insuffisant", 0.0
    
    x = np.arange(len(fires_count))
    y = fires_count.values
    
    if len(x) > 1:
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        
        if abs(slope) < 0.1:
            return "Stable", slope
        elif slope > 0:
            return "Croissance", slope
        else:
            return "Décroissance", slope
    
    return "Stable", 0.0


def analyze_fires_before_big_fire(df: pd.DataFrame, big_fire_row: pd.Series,
                                   temporal_window_days: int, buffer_radius_km: float,
                                   min_fires_before: int) -> Dict:
    """
    Analyse les incendies dans une fenêtre spatio-temporelle avant un grand feu
    Double condition : temporelle ET spatiale
    """
    big_fire_date = big_fire_row['date_alerte']
    
    if pd.isna(big_fire_date):
        return {
            'valid': False,
            'fires_in_buffer': pd.DataFrame(),
            'small_fires_count': 0,
            'trend': 'N/A',
            'slope': 0.0,
            'condition_met': False
        }
    
    # Condition 1 : Fenêtre temporelle
    start_date = big_fire_date - timedelta(days=temporal_window_days)
    temporal_mask = (df['date_alerte'] >= start_date) & (df['date_alerte'] < big_fire_date)
    fires_temporal = df[temporal_mask].copy()
    
    # Condition 2 : Buffer spatial
    fires_in_buffer = get_fires_in_buffer(
        fires_temporal,
        big_fire_row['x'],
        big_fire_row['y'],
        buffer_radius_km
    )
    
    # Extraction des petits et moyens feux
    small_fires = fires_in_buffer[fires_in_buffer['categorie'] == 'Petit feu'].copy()
    medium_fires = fires_in_buffer[fires_in_buffer['categorie'] == 'Feu moyen'].copy()
    
    # Analyse temporelle
    if len(small_fires) > 0:
        small_fires['date_only'] = small_fires['date_alerte'].dt.date
        daily_counts = small_fires.groupby('date_only').size()
        trend, slope = analyze_temporal_trend(daily_counts)
    else:
        trend, slope = "Aucun", 0.0
    
    condition_met = len(small_fires) >= min_fires_before
    
    return {
        'valid': True,
        'fires_in_buffer': fires_in_buffer,
        'small_fires': small_fires,
        'medium_fires': medium_fires,
        'small_fires_count': len(small_fires),
        'medium_fires_count': len(medium_fires),
        'trend': trend,
        'slope': slope,
        'condition_met': condition_met
    }


def lambert93_to_wgs84(x: float, y: float) -> Tuple[float, float]:
    """Convertit les coordonnées Lambert 93 en WGS84 (lat/lon)"""
    lat = 46.5 + (y - 6600000) / 111320
    lon = 3.0 + (x - 700000) / (111320 * 0.72)
    return lat, lon


def analyze_parameter_trends(small_fires: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Analyse les tendances temporelles des paramètres environnementaux
    avant un grand feu
    
    Args:
        small_fires: DataFrame des petits feux avec date_alerte triée
        
    Returns:
        df_trends: DataFrame avec les valeurs moyennes par période
        trends_summary: Dict avec les tendances calculées pour chaque paramètre
    """
    params = ['FF', 'HU', 'T', 'PRELIQ', 'mean_NDVI']
    
    # Filtrer les paramètres disponibles
    available_params = [p for p in params if p in small_fires.columns]
    
    if len(small_fires) == 0 or len(available_params) == 0:
        return pd.DataFrame(), {}
    
    # Trier par date
    small_fires_sorted = small_fires.sort_values('date_alerte').copy()
    
    # Créer des périodes (diviser en 5 intervalles)
    n_periods = min(5, len(small_fires_sorted))
    small_fires_sorted['periode'] = pd.qcut(
        range(len(small_fires_sorted)), 
        q=n_periods, 
        labels=[f"P{i+1}" for i in range(n_periods)],
        duplicates='drop'
    )
    
    # Calculer les moyennes par période
    df_trends = small_fires_sorted.groupby('periode')[available_params].mean().reset_index()
    
    # Calculer les tendances (régression linéaire)
    trends_summary = {}
    for param in available_params:
        values = df_trends[param].dropna().values
        if len(values) >= 2:
            x = np.arange(len(values))
            # Régression linéaire
            slope, intercept = np.polyfit(x, values, 1)
            
            # Coefficient de corrélation
            correlation = np.corrcoef(x, values)[0, 1] if len(values) > 2 else 0
            
            # Variation en pourcentage
            if values[0] != 0:
                variation_pct = ((values[-1] - values[0]) / abs(values[0])) * 100
            else:
                variation_pct = 0
            
            # Direction de la tendance
            if abs(slope) < 0.01 * np.std(values):
                direction = "Stable"
            elif slope > 0:
                direction = "Croissance"
            else:
                direction = "Décroissance"
            
            trends_summary[param] = {
                'slope': slope,
                'correlation': correlation,
                'variation_pct': variation_pct,
                'direction': direction,
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
        else:
            trends_summary[param] = {
                'slope': 0,
                'correlation': 0,
                'variation_pct': 0,
                'direction': 'Insuffisant',
                'mean': values[0] if len(values) > 0 else 0,
                'std': 0,
                'min': values[0] if len(values) > 0 else 0,
                'max': values[0] if len(values) > 0 else 0
            }
    
    return df_trends, trends_summary


def analyze_parameter_correlations_with_big_fire(small_fires: pd.DataFrame, 
                                                   big_fire_surface: float) -> Dict:
    """
    Analyse les corrélations entre les paramètres des petits feux et la surface du grand feu
    
    Args:
        small_fires: DataFrame des petits feux dans la fenêtre temporelle
        big_fire_surface: Surface du grand feu (ha)
        
    Returns:
        Dict avec les corrélations pour chaque paramètre
    """
    from scipy.stats import pearsonr, spearmanr
    from sklearn.metrics import mutual_info_score
    
    params = ['FF', 'HU', 'T', 'PRELIQ', 'mean_NDVI']
    available_params = [p for p in params if p in small_fires.columns]
    
    if len(small_fires) == 0 or len(available_params) == 0:
        return {}
    
    correlations = {}
    
    for param in available_params:
        values = small_fires[param].dropna()
        
        if len(values) < 2:
            correlations[param] = {
                'pearson': 0,
                'spearman': 0,
                'mutual_info': 0,
                'mean_value': 0,
                'status': 'Insuffisant'
            }
            continue
        
        # Pearson correlation (linéaire)
        # Corrélation entre la moyenne du paramètre et la surface du grand feu
        param_mean = values.mean()
        
        # Pour une vraie corrélation, on aurait besoin de plusieurs grands feux
        # Ici on calcule la corrélation entre les valeurs du paramètre au fil du temps
        # et on regarde si elles tendent vers une valeur critique
        
        # Calcul de la variabilité
        param_std = values.std()
        param_trend = np.polyfit(range(len(values)), values, 1)[0]
        
        # Spearman correlation (monotone)
        time_index = np.arange(len(values))
        try:
            spearman_corr, _ = spearmanr(time_index, values)
        except:
            spearman_corr = 0
        
        # Mutual Information (discrétiser pour MI)
        try:
            # Discrétiser les valeurs en 5 bins
            values_binned = pd.qcut(values, q=5, labels=False, duplicates='drop')
            time_binned = pd.qcut(time_index, q=min(5, len(time_index)), labels=False, duplicates='drop')
            mi_score = mutual_info_score(time_binned, values_binned)
        except:
            mi_score = 0
        
        # Pearson avec le temps
        try:
            pearson_corr, _ = pearsonr(time_index, values)
        except:
            pearson_corr = 0
        
        correlations[param] = {
            'pearson': pearson_corr,
            'spearman': spearman_corr,
            'mutual_info': mi_score,
            'mean_value': param_mean,
            'std_value': param_std,
            'trend': param_trend,
            'status': 'OK'
        }
    
    return correlations


def analyze_global_parameter_correlations(analysis_results: list, big_fires: pd.DataFrame, departement: str = None) -> Dict:
    """
    Analyse les corrélations entre les paramètres des petits feux et les grands feux
    sur l'ensemble des données (tous les grands feux analysés)
    
    Args:
        analysis_results: Liste des résultats d'analyse pour chaque grand feu
        big_fires: DataFrame des grands feux
        departement: Code du département à filtrer (optionnel, ex: '84', '5', '6')
        
    Returns:
        Dict avec les corrélations pour chaque paramètre
    """
    from scipy.stats import pearsonr, spearmanr
    from sklearn.metrics import mutual_info_score
    
    params = ['FF', 'HU', 'T', 'PRELIQ', 'mean_NDVI']
    
    # Filtrer par département si spécifié
    if departement is not None and departement != "Tous":
        # Filtrer big_fires par département
        mask = big_fires['depart'].astype(str) == str(departement)
        filtered_indices = big_fires[mask].index.tolist()
        
        # Ne garder que les analysis_results correspondants
        filtered_analysis_results = [analysis_results[i] for i in filtered_indices if i < len(analysis_results)]
        filtered_big_fires = big_fires[mask].reset_index(drop=True)
    else:
        filtered_analysis_results = analysis_results
        filtered_big_fires = big_fires
    
    # Collecter toutes les données des petits feux et les surfaces des grands feux
    all_param_values = {param: [] for param in params}
    all_big_fire_surfaces = []
    
    for idx, result in enumerate(filtered_analysis_results):
        if result.get('condition_met', False) and 'small_fires' in result:
            small_fires = result['small_fires']
            big_fire_surface = filtered_big_fires.iloc[idx]['surface_ha']
            
            if len(small_fires) > 0:
                # Trier par date pour avoir l'ordre temporel
                small_fires_sorted = small_fires.sort_values('date_alerte')
                
                # Pour chaque paramètre, calculer la VARIATION (pente) au lieu de la moyenne
                for param in params:
                    if param in small_fires_sorted.columns:
                        param_values = small_fires_sorted[param].dropna()
                        
                        if len(param_values) >= 2:
                            # Calculer la pente (tendance) de la variation temporelle
                            # Régression linéaire : param = a*temps + b
                            # On veut 'a' qui représente la variation par unité de temps
                            time_index = np.arange(len(param_values))
                            try:
                                slope, _ = np.polyfit(time_index, param_values, 1)
                                # Normaliser la pente par la durée pour avoir une variation comparable
                                param_variation = slope * len(param_values)  # Variation totale sur la période
                            except:
                                # Si régression échoue, utiliser la différence simple
                                param_variation = param_values.iloc[-1] - param_values.iloc[0]
                            
                            if not np.isnan(param_variation):
                                all_param_values[param].append(param_variation)
                                # Stocker la surface correspondante
                                if param == params[0]:  # Faire seulement une fois
                                    all_big_fire_surfaces.append(big_fire_surface)
                        elif len(param_values) == 1:
                            # Si une seule valeur, variation = 0
                            all_param_values[param].append(0.0)
                            if param == params[0]:
                                all_big_fire_surfaces.append(big_fire_surface)
    
    # Calculer les corrélations
    correlations = {}
    
    for param in params:
        if len(all_param_values[param]) < 3:
            correlations[param] = {
                'pearson': 0,
                'pearson_pval': 1,
                'spearman': 0,
                'spearman_pval': 1,
                'mutual_info': 0,
                'mean_value': 0,
                'std_value': 0,
                'n_samples': 0,
                'status': 'Insuffisant'
            }
            continue
        
        param_values = np.array(all_param_values[param])
        surfaces = np.array(all_big_fire_surfaces[:len(param_values)])
        
        # Pearson correlation
        try:
            pearson_corr, pearson_pval = pearsonr(param_values, surfaces)
        except:
            pearson_corr, pearson_pval = 0, 1
        
        # Spearman correlation
        try:
            spearman_corr, spearman_pval = spearmanr(param_values, surfaces)
        except:
            spearman_corr, spearman_pval = 0, 1
        
        # Mutual Information
        try:
            # Discrétiser en bins
            n_bins = min(5, len(param_values) // 3)
            if n_bins >= 2:
                param_binned = pd.qcut(param_values, q=n_bins, labels=False, duplicates='drop')
                surface_binned = pd.qcut(surfaces, q=n_bins, labels=False, duplicates='drop')
                mi_score = mutual_info_score(param_binned, surface_binned)
            else:
                mi_score = 0
        except:
            mi_score = 0
        
        correlations[param] = {
            'pearson': pearson_corr,
            'pearson_pval': pearson_pval,
            'spearman': spearman_corr,
            'spearman_pval': spearman_pval,
            'mutual_info': mi_score,
            'mean_value': np.mean(param_values),
            'std_value': np.std(param_values),
            'n_samples': len(param_values),
            'status': 'OK'
        }
    
    return correlations
