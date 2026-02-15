# 🔥 Application Streamlit - Analyse des Incendies en PACA

Application web interactive pour l'analyse spatiale et temporelle des incendies en région PACA.

## 📁 Structure Modulaire du Projet

```
app_web/
├── app.py                          # Application principale (350 lignes)
├── modules/
│   ├── __init__.py                 # Initialisation du package
│   ├── data_processing.py          # Traitement et analyse (180 lignes)
│   ├── visualizations.py           # Graphiques améliorés (250 lignes)
│   └── export.py                   # Export données (65 lignes)
├── data/
│   └── Incendies_PACA.csv         # Données source
├── .streamlit/
│   └── config.toml                 # Configuration
├── requirements.txt                # Dépendances
└── README.md                       # Documentation
```

## 🎨 Améliorations Visuelles

### Carte Interactive
- ✅ **Légende supprimée** (interface plus épurée)
- 🟡 **Petits feux** : marqueurs jaunes dorés (#FFD700)
- 🟠 **Moyens feux** : marqueurs orange (#FF8C00)
- ⭐ **Grands feux** : étoiles rouges (#DC143C)
- 🔴 **Buffers** : zones rouges semi-transparentes

### Graphiques
- **Palette de couleurs cohérente** sur tous les graphiques
- **Effets visuels** : bordures blanches, opacité optimisée
- **Interactivité** : hover amélioré avec détails complets
- **Annotations** : dates et événements marqués

## 📊 Section Export

3 options d'export disponibles :

### 1. 📊 Excel Complet
- **Feuille 1** : Grands feux (date, commune, surface, coordonnées)
- **Feuille 2** : Analyses (tendances, comptages, pentes)
- **Feuille 3** : Détails buffers (tous les feux par buffer)

### 2. 📄 CSV Filtré
- Données complètes filtrées par période
- Format CSV standard (séparateur point-virgule)

### 3. 📈 Résultats Analyse
- Tableau récapitulatif uniquement
- Format CSV compact

## 🛠️ Installation

```bash
# Cloner le projet
cd "d:\GMS\Atelier - Bridier\app_web"

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

## 📦 Modules

### `data_processing.py`
Fonctions :
- `load_data()` : Chargement et prétraitement CSV
- `classify_fires()` : Classification par taille
- `analyze_fires_before_big_fire()` : Analyse spatio-temporelle
- `lambert93_to_wgs84()` : Conversion coordonnées

### `visualizations.py`
Fonctions :
- `create_map()` : Carte interactive sans légende
- `create_pie_chart()` : Graphique circulaire coloré
- `create_line_chart()` : Évolution temporelle
- `create_trend_bar()` : Distribution tendances
- `create_scatter_plot()` : Corrélations
- `create_temporal_series()` : Série temporelle
- `create_commune_chart()` : Analyse par commune

### `export.py`
Fonctions :
- `export_results()` : Génération Excel multi-feuilles
- `export_csv()` : Export CSV simple

## ⚙️ Configuration

Le fichier `.streamlit/config.toml` permet de personnaliser :
- Thème de couleur
- Police de caractères
- Paramètres de sécurité

## 📋 Méthodologie

Les petits et moyens feux sont comptés **uniquement** s'ils répondent aux **DEUX conditions** :

✅ **Condition temporelle** : Survenus X jours AVANT le grand feu
✅ **Condition spatiale** : Situés dans un rayon de Y km AUTOUR du grand feu

## 🚀 Avantages de la Structure Modulaire

1. **Code organisé** : Chaque module a une responsabilité claire
2. **Maintenance facile** : Modifications isolées par fonctionnalité
3. **Réutilisabilité** : Fonctions importables dans d'autres projets
4. **Lisibilité** : Fichiers courts et focalisés
5. **Tests simplifiés** : Chaque module testable indépendamment

## 📝 Encodage

Tous les fichiers sont encodés en **UTF-8** pour éviter les problèmes d'accents :
- ✅ Caractères français correctement affichés
- ✅ Émojis supportés
- ✅ Compatibilité multi-plateforme

## 🔄 Mise à Jour depuis l'Ancienne Version

L'ancien fichier `app.py` monolithique (735 lignes) a été restructuré en :
- **app.py** : 350 lignes (logique principale)
- **modules/** : 495 lignes (4 fichiers spécialisés)

**Bénéfices** :
- Code plus court et plus lisible
- Pas de duplication
- Séparation des responsabilités
- Meilleure performance (imports optimisés)
