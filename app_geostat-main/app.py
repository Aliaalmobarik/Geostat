import streamlit as st
from app_css import inject_css

st.set_page_config(
    page_title="Analyse Incendies PACA",
    page_icon="🔥",
    layout="wide"
)

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

st.markdown(
    '<div class="hero-card">'
    '<div class="hero-title">🔥 Forest Fire Insights</div>'
    '<div class="hero-subtitle">Observatoire des Incendies de Forêt — Provence-Alpes-Côte d\'Azur</div>'
    '<div class="hero-subtitle">Analyse spatio-temporelle • Accueil & Analyse</div>'
    '</div>',
    unsafe_allow_html=True
)
