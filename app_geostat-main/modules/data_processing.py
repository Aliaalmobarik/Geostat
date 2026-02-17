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
    df = pd.read_csv(file_path, sep=';', encoding='utf-8', low_memory=False, decimal=',')
    
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
