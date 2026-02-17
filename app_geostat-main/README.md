# 🔥 Application d'Analyse des Incendies en PACA

Application web interactive développée avec Streamlit pour analyser les données d'incendies en région Provence-Alpes-Côte d'Azur.

## 📋 Fonctionnalités

### 1. 📂 Chargement et filtrage des données
- Import automatique des données CSV des incendies
- Filtrage par période temporelle (année de début/fin)
- Prétraitement et nettoyage optimisés des données

### 2. 🔥 Classification des incendies
- **Petit feu** : Surface < X hectares (paramétrable)
- **Feu moyen** : Surface entre X et Y hectares
- **Grand feu** : Surface > Y hectares (paramétrable)

### 3. 🌍 Analyse spatiale
- Création de buffers circulaires autour des grands feux
- Rayon paramétrable (1 à 100 km)
- Identification des incendies dans le buffer
- Calcul des distances optimisé avec vectorisation NumPy

### 4. ⏳ Analyse temporelle
- Fenêtre temporelle avant chaque grand feu (7 à 180 jours)
- Comptage des petits incendies précédents
- Analyse de tendance (croissance/décroissance/stable)
- Régression linéaire pour déterminer la pente

### ⚠️ IMPORTANT : Critères de sélection des feux

**Les petits et moyens feux sont comptés UNIQUEMENT s'ils répondent aux DEUX conditions simultanées :**

1. **✅ Condition temporelle** : Le feu doit survenir dans la fenêtre temporelle définie (X jours AVANT le grand feu)
2. **✅ Condition spatiale** : Le feu doit être situé dans le buffer spatial (rayon de Y km AUTOUR du grand feu)

**Exemple concret :**
- Grand feu : 15 août 2021 à Arles (coordonnées X, Y)
- Paramètres : Buffer = 10 km, Fenêtre = 30 jours
- Petit feu A : 20 juillet 2021 (26 jours avant) à 5 km → **✅ COMPTÉ** (répond aux 2 conditions)
- Petit feu B : 20 juillet 2021 (26 jours avant) à 25 km → **❌ NON COMPTÉ** (hors buffer)
- Petit feu C : 10 juin 2021 (66 jours avant) à 5 km → **❌ NON COMPTÉ** (hors fenêtre temporelle)

Cette double condition garantit que seuls les feux **vraiment proches** (en temps ET en espace) du grand feu sont analysés.

### 5. 📊 Visualisations interactives
- Vue d'ensemble avec statistiques
- Graphiques de distribution (camembert, histogrammes)
- Évolution annuelle des incendies
- Analyse des tendances
- Cartographie interactive avec Plotly

### 6. 📥 Export des résultats
- Export Excel avec feuilles multiples :
  - Liste des grands feux
  - Analyse détaillée
- Export CSV des données filtrées
- Téléchargement direct depuis l'interface

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**
```bash
cd "d:\GMS\Atelier - Bridier\app_web"
```

2. **Créer un environnement virtuel (recommandé)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Installer les dépendances**
```powershell
pip install -r requirements.txt
```

## 📁 Structure du projet

```
app_web/
├── app.py                    # Application principale
├── requirements.txt          # Dépendances
├── README.md                # Documentation
└── data/
    └── Incendies_PACA.csv   # Données des incendies
```

## ▶️ Lancement de l'application

```powershell
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut à l'adresse :
```
http://localhost:8501
```

## 🎯 Guide d'utilisation

### Paramètres dans la barre latérale

#### 📅 Période d'analyse
- **Année de début** : Sélectionner l'année de début de l'analyse
- **Année de fin** : Sélectionner l'année de fin de l'analyse

#### 🔥 Classification des incendies
- **Seuil petit feu** : Surface maximale pour les petits feux (défaut: 1 ha)
- **Seuil grand feu** : Surface minimale pour les grands feux (défaut: 10 ha)

#### 📊 Paramètres d'analyse
- **Nombre min. d'incendies avant grand feu** : Critère de filtrage (défaut: 3)

#### 🌍 Analyse spatiale
- **Rayon du buffer** : Distance en km autour des grands feux (1-100 km, défaut: 10 km)

#### ⏳ Fenêtre temporelle
- **Jours avant le grand feu** : Période d'analyse précédant chaque grand feu (7-180 jours, défaut: 30)

### Onglets de l'application

#### 📊 Vue d'ensemble
- Statistiques générales (total, petits/moyens/grands feux)
- Distribution par catégorie (graphique camembert)
- Évolution annuelle (graphique linéaire)
- Distribution des surfaces brûlées (histogramme)

#### 🔍 Analyse détaillée
- Liste des grands feux répondant aux critères
- Tableau récapitulatif avec :
  - Date et localisation
  - Nombre de petits feux avant
  - Tendance (croissance/décroissance/stable)
  - Pente de régression
- Sélection d'un grand feu pour analyse approfondie
- Liste détaillée des incendies dans le buffer

#### 🗺️ Cartographie
- Carte interactive de tous les incendies
- Grands feux marqués par des étoiles rouges
- Zoom et navigation interactifs

#### 📥 Export
- Génération de fichier Excel avec résultats complets
- Export CSV des données filtrées
- Téléchargement direct

## ⚡ Optimisations implémentées

### Performance
- **Cache des données** : `@st.cache_data` pour éviter les rechargements
- **Vectorisation NumPy** : Calculs de distance et filtrage optimisés
- **Opérations vectorisées pandas** : Classification rapide avec `np.select`
- **Filtres combinés** : Réduction du nombre d'itérations

### Code
- **Fonctions modulaires** : Chaque tâche dans une fonction dédiée
- **Type hints** : Meilleure lisibilité et maintenabilité
- **Gestion d'erreurs** : Try/except pour le chargement des données
- **Nettoyage des données** : Suppression des valeurs manquantes essentielles

### Interface utilisateur
- **Barre de progression** : Feedback visuel pendant les analyses longues
- **Mise en page responsive** : Layout adaptatif avec colonnes
- **Messages clairs** : Success/warning/info pour guider l'utilisateur

## 📊 Format des données

Le fichier CSV doit contenir les colonnes suivantes :
- `annee` : Année de l'incendie
- `x_coord`, `y_coord` : Coordonnées Lambert 93 (mètres)
- `join_surf_ha` : Surface brûlée en hectares
- `join_Alert` : Date et heure d'alerte (format: DD/MM/YYYY HH:MM)
- `join_Commu` : Commune
- Autres colonnes optionnelles

## 🔧 Dépendances

- **streamlit** : Framework web interactif
- **pandas** : Manipulation de données
- **numpy** : Calculs numériques optimisés
- **plotly** : Visualisations interactives
- **openpyxl** : Lecture/écriture Excel
- **xlsxwriter** : Export Excel avancé

## 📝 Notes techniques

### Système de coordonnées
Les coordonnées sont en projection Lambert 93 (EPSG:2154), système officiel français.
- Unité : mètres
- Conversion approximative pour affichage carte : division par 111320

### Calcul de distance
Distance euclidienne en 2D (suffisante pour des analyses locales) :
```python
distance = sqrt((x2-x1)² + (y2-y1)²) / 1000  # en km
```

### Analyse de tendance
Régression linéaire simple sur le nombre d'incendies par jour :
- Pente > 0.1 → Croissance
- Pente < -0.1 → Décroissance
- |Pente| ≤ 0.1 → Stable

## 🐛 Résolution de problèmes

### L'application ne démarre pas
- Vérifier que l'environnement virtuel est activé
- Réinstaller les dépendances : `pip install -r requirements.txt`

### Erreur de chargement des données
- Vérifier que le fichier `data/Incendies_PACA.csv` existe
- Vérifier le format du CSV (séparateur point-virgule)
- Vérifier l'encodage (UTF-8)

### Performances lentes
- Réduire la période d'analyse
- Augmenter les seuils de classification
- Réduire le rayon du buffer

## 📄 Licence

Ce projet est développé dans un cadre éducatif.

## 👨‍💻 Auteur

Développé pour l'analyse des incendies en région PACA.

---

**Date de création** : Février 2026
