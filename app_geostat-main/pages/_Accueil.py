import streamlit as st
from app_css import inject_css

inject_css()

with st.sidebar:
    st.markdown('<div class="sidebar-brand"><span class="logo">🔥</span><span class="title">Forest Fire Insights</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-card"><div class="sidebar-title">Navigation</div>', unsafe_allow_html=True)
    try:
        st.page_link("pages/_Accueil.py", label="Accueil", icon="🏠")
        st.page_link("pages/_Analyse.py", label="Analyse", icon="📊")
        st.page_link("pages/_Meteo.py", label="Meteo", icon="☀️")
    except Exception:
        st.markdown('<div class="nav-link">🏠 Accueil</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-link">📊 Analyse</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-link">☀️ Meteo</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Hero card
st.markdown(
    '<div class="hero-card">'
    '<div class="hero-title">🔥 Forest Fire Insights</div>'
    '<div class="hero-subtitle">Observatoire des Incendies de Forêt en Provence-Alpes-Côte d\'Azur</div>'
    '<div class="hero-subtitle">Analyse spatio-temporelle • Période 1973–2022 • 50 ans de données</div>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("### Chiffres Clés (1973–2022)")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-card"><div class="value">50</div><div class="label">Années d\'étude</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-card"><div class="value">6</div><div class="label">Départements PACA</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-card"><div class="value">118k+</div><div class="label">Incendies recensés</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="metric-card"><div class="value">~400k ha</div><div class="label">Surfaces brûlées</div></div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("Fonctionnalités du Dashboard")

f_col1, f_col2 = st.columns(2)
with f_col1:
        st.markdown("""
        <div class="metric-card" style="text-align:left;">
            <div class="hero-title" style="font-size:1.2rem;">🗺️ Carte Interactive</div>
            <div class="label">Visualisation spatiale par commune et département, buffers dynamiques et zones à risque.</div>
        </div>
        <div class="metric-card" style="text-align:left; margin-top:12px;">
            <div class="hero-title" style="font-size:1.2rem;">📊 Analyses Temporelles</div>
            <div class="label">Saisonnalité, tendances longues, détection des périodes critiques.</div>
        </div>
        """, unsafe_allow_html=True)

with f_col2:
        st.markdown("""
        <div class="metric-card" style="text-align:left;">
            <div class="hero-title" style="font-size:1.2rem;">📌 Comparaison Territoriale</div>
            <div class="label">Comparaison des départements et zones littoral/montagne, identification des zones vulnérables.</div>
        </div>
        <div class="metric-card" style="text-align:left; margin-top:12px;">
            <div class="hero-title" style="font-size:1.2rem;">🎯 Aide à la Décision</div>
            <div class="label">Synthèses et exports pour prioriser la prévention et le pilotage local.</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("Zone d'étude : Région PACA")
z1, z2 = st.columns(2)

with z1:
        st.markdown("""
        <div class="metric-card" style="text-align:left;">
            <div class="hero-title" style="font-size:1.1rem;">📍 6 Départements</div>
            <ul style="color:#3C2B22; padding-left:18px; line-height:1.6;">
                <li>04 - Alpes-de-Haute-Provence</li>
                <li>05 - Hautes-Alpes</li>
                <li>06 - Alpes-Maritimes</li>
                <li>13 - Bouches-du-Rhône</li>
                <li>83 - Var</li>
                <li>84 - Vaucluse</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

with z2:
        st.markdown("""
        <div class="metric-card" style="text-align:left;">
            <div class="hero-title" style="font-size:1.1rem;">⚡ Facteurs de Risque</div>
            <ul style="color:#3C2B22; padding-left:18px; line-height:1.6;">
                <li>Climat méditerranéen sec</li>
                <li>Vents violents (Mistral)</li>
                <li>Végétation inflammable</li>
                <li>Forte pression anthropique</li>
                <li>Axes de transport et interfaces urbaines</li>
                <li>Fréquentation touristique</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
