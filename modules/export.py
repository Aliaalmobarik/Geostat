"""
Module d'export des données
"""

import pandas as pd
import io
from typing import List, Dict, Optional


def export_results(big_fires: pd.DataFrame, analysis_results: List[Dict], 
                   correlation_summary: Optional[pd.DataFrame] = None) -> bytes:
    """Exporte les résultats dans un fichier Excel"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Feuille 1 : Grands feux
        big_fires_export = big_fires[['annee', 'commune', 'date_alerte', 'surface_ha', 'x', 'y']].copy()
        big_fires_export.to_excel(writer, sheet_name='Grands_feux', index=False)
        
        # Feuille 2 : Analyse détaillée
        if analysis_results:
            analysis_data = []
            for idx, result in enumerate(analysis_results):
                if result['valid'] and result['condition_met']:
                    bf = big_fires.iloc[idx]
                    analysis_data.append({
                        'Grand_feu_date': bf['date_alerte'],
                        'Commune': bf['commune'],
                        'Surface_ha': bf['surface_ha'],
                        'Petits_feux_avant': result['small_fires_count'],
                        'Moyens_feux_avant': result['medium_fires_count'],
                        'Tendance': result['trend'],
                        'Pente': result['slope'],
                        'Feux_dans_buffer': len(result['fires_in_buffer'])
                    })
            
            if analysis_data:
                pd.DataFrame(analysis_data).to_excel(writer, sheet_name='Analyse', index=False)
        
        # Feuille 3 : Détails des feux dans buffers
        if analysis_results:
            all_buffer_fires = []
            for idx, result in enumerate(analysis_results):
                if result['valid'] and result['condition_met']:
                    bf = big_fires.iloc[idx]
                    for _, fire in result['fires_in_buffer'].iterrows():
                        all_buffer_fires.append({
                            'Grand_feu_commune': bf['commune'],
                            'Grand_feu_date': bf['date_alerte'],
                            'Feu_buffer_date': fire['date_alerte'],
                            'Feu_buffer_commune': fire['commune'],
                            'Type': fire['categorie'],
                            'Surface_ha': fire['surface_ha'],
                            'Distance_km': fire['distance_km']
                        })
            
            if all_buffer_fires:
                pd.DataFrame(all_buffer_fires).to_excel(writer, sheet_name='Feux_buffers', index=False)
        
        # Feuille 4 : Analyse de corrélation
        if correlation_summary is not None:
            correlation_summary.to_excel(writer, sheet_name='Correlation', index=False)
            
            # Ajouter une feuille avec des explications
            workbook = writer.book
            worksheet_exp = workbook.add_worksheet('Explications_Correlation')
            
            bold_format = workbook.add_format({'bold': True, 'font_size': 12})
            text_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
            
            row = 0
            worksheet_exp.write(row, 0, 'Interprétation des Résultats de Corrélation', bold_format)
            row += 2
            
            worksheet_exp.write(row, 0, 'Cross-Correlation:', bold_format)
            row += 1
            worksheet_exp.write(row, 0, '• Mesure la similarité entre les séries temporelles de petits et grands feux', text_format)
            row += 1
            worksheet_exp.write(row, 0, '• Valeur proche de 1 : forte corrélation positive', text_format)
            row += 1
            worksheet_exp.write(row, 0, '• Valeur proche de -1 : forte corrélation négative', text_format)
            row += 1
            worksheet_exp.write(row, 0, '• Valeur proche de 0 : pas de corrélation linéaire', text_format)
            row += 2
            
            worksheet_exp.write(row, 0, 'Granger Causality:', bold_format)
            row += 1
            worksheet_exp.write(row, 0, '• Teste si les petits feux permettent de prédire les grands feux', text_format)
            row += 1
            worksheet_exp.write(row, 0, '• p-value < 0.05 : causalité significative (les petits feux prédisent les grands feux)', text_format)
            row += 1
            worksheet_exp.write(row, 0, '• p-value ≥ 0.05 : pas de causalité statistiquement significative', text_format)
            row += 2
            
            worksheet_exp.write(row, 0, 'Mutual Information:', bold_format)
            row += 1
            worksheet_exp.write(row, 0, '• Quantifie l\'information partagée entre petits et grands feux', text_format)
            row += 1
            worksheet_exp.write(row, 0, '• Valeur élevée : forte dépendance entre les deux phénomènes', text_format)
            row += 1
            worksheet_exp.write(row, 0, '• Valeur proche de 0 : phénomènes indépendants', text_format)
            
            worksheet_exp.set_column(0, 0, 80)
    
    output.seek(0)
    return output.getvalue()


def export_csv(df: pd.DataFrame) -> str:
    """Exporte les données filtrées en CSV"""
    return df.to_csv(index=False, sep=';')
