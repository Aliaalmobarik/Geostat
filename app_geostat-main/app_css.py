import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>
            /* Warm light palette (not too bright) */
            :root {
                --primary: #D95F18;      /* Warm orange */
                --primary-2: #FF9F1C;    /* Softer orange */
                --text: #2C1B12;         /* Dark brown */
                --muted: #5C4A3F;        /* Muted brown */
                --bg: #F7F2EA;           /* Soft cream */
                --bg-2: #F2E9DE;         /* Sidebar light beige */
                --card: #FFFDF8;         /* Light card */
                --accent: #E6C7A1;       /* Pale accent */
            }

            html, body, .stApp, [class^="css"], * {
                font-family: "Inter", "Segoe UI", "Courier New", monospace !important;
                color: var(--text) !important;
            }

            .stApp {
                background: radial-gradient(circle at 20% 20%, rgba(217,95,24,0.10), transparent 35%),
                            radial-gradient(circle at 80% 10%, rgba(255,159,28,0.12), transparent 40%),
                            linear-gradient(180deg, #FBF6EF 0%, #F7F2EA 60%, #F2E9DE 100%) !important;
            }

            /* Headings */
            h1, h2, h3, h4, h5, h6 {
                color: var(--primary) !important;
                font-weight: 700 !important;
            }

            /* Buttons */
            .stButton>button, .stDownloadButton>button {
                background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%) !important;
                color: #fff !important;
                border-radius: 12px !important;
                border: 1px solid #E6C7A1 !important;
                font-weight: 800 !important;
                box-shadow: 0 6px 16px rgba(0,0,0,0.12) !important;
            }
            .stButton>button:hover, .stDownloadButton>button:hover {
                background: linear-gradient(135deg, var(--primary-2) 0%, var(--primary) 100%) !important;
                border-color: #D95F18 !important;
            }

            /* Metrics */
            [data-testid="stMetricValue"] {
                color: var(--primary) !important;
                font-size: 1.9rem !important;
                font-weight: 800 !important;
            }
            [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
                font-weight: 700 !important;
                color: var(--muted) !important;
            }

            /* Sidebar modern card style */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, var(--bg-2) 0%, #F9F3E9 70%) !important;
                color: var(--text) !important;
                border-right: 1px solid rgba(0,0,0,0.04);
            }
            /* Hide default Streamlit multipage nav list to keep only custom navigation */
            [data-testid="stSidebarNav"] ul {
                display: none !important;
            }

            button[data-testid="stBaseButton-headerNoPadding"] {
                width: 32px !important;
                height: 32px !important;
                padding: 0 !important;
                margin: 0 !important;

                display: flex !important;
                align-items: center !important;
                justify-content: center !important;

                overflow: hidden !important;
                border-radius: 8px !important;

                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }

            /* Hide only the problematic label text */
            button[data-testid="stBaseButton-headerNoPadding"] span:not([data-testid="stIconMaterial"]) {
                display: none !important;
            }

            /* Ensure the Material icon stays clean and black */
            button[data-testid="stBaseButton-headerNoPadding"] [data-testid="stIconMaterial"] svg {
                width: 18px !important;
                height: 18px !important;
                display: block !important;
                color: #000000 !important;
            }

            [data-testid="stSidebar"][aria-expanded="false"] .sidebar-brand .title { display: none !important; }
            [data-testid="stSidebar"][aria-expanded="false"] .sidebar-card { display: none !important; }
            .sidebar-card {
                background: #FFFFFF;
                border: 1px solid rgba(0,0,0,0.06);
                border-radius: 12px;
                padding: 12px 14px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.06);
                margin-bottom: 12px;
            }
            .sidebar-title {
                color: var(--primary);
                font-weight: 800;
                letter-spacing: .5px;
                text-transform: uppercase;
                font-size: .9rem;
                margin-bottom: 6px;
            }
                /* Modern sidebar brand and card */
                .sidebar-brand {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 14px 10px;
                    border-bottom: 1px solid rgba(0,0,0,0.06);
                    margin-bottom: 12px;
                }
                .sidebar-brand .logo {
                    font-size: 2rem;
                }
                .sidebar-brand .title {
                    font-weight: 800;
                    color: var(--primary);
                    font-size: 1.2rem;
                }

                .nav-link {
                    display: block;
                    padding: 8px 10px;
                    border-radius: 8px;
                    color: var(--text) !important;
                    text-decoration: none !important;
                    border: 1px solid transparent;
                }
                .nav-link:hover {
                    background: rgba(217,95,24,0.12);
                    border-color: rgba(217,95,24,0.35);
                }
                .nav-link.active {
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%);
                    color: #fff !important;
                    border-color: #D95F18;
                }

            /* Dataframes */
            .dataframe { border: 1px solid rgba(0,0,0,0.06) !important; }
            .dataframe th, .dataframe td { font-weight: 600 !important; color: #3C2B22 !important; }

            /* Info/Success/Warning */
            .stInfo { background-color: #FFF8EF !important; border-left: 5px solid var(--primary) !important; font-weight: 700 !important; color: #3C2B22 !important; }
            .stSuccess { background-color: #F2F8F2 !important; border-left: 5px solid #4CAF50 !important; font-weight: 700 !important; color: #2E4A2F !important; }
            .stWarning { background-color: #FFF4E5 !important; border-left: 5px solid #D95F18 !important; font-weight: 700 !important; color: #4A2A16 !important; }

            /* Hero and metric cards */
            .hero-card {
                background: radial-gradient(circle at 15% 20%, rgba(217,95,24,0.10), transparent 45%),
                            radial-gradient(circle at 80% 0%, rgba(255,159,28,0.12), transparent 40%),
                            #FFFDF8;
                border: 1px solid rgba(217,95,24,0.28);
                border-radius: 18px;
                padding: 24px 28px;
                box-shadow: 0 10px 24px rgba(0,0,0,0.12);
                margin: 8px 0 18px;
            }
            .hero-title { font-size: 2.1rem; font-weight: 800; color: #C64F12; }
            .hero-subtitle { font-size: 1.05rem; color: #4B362A; }

            .metric-card {
                background: linear-gradient(145deg, #FFFFFF 0%, #F9F3E9 100%);
                border: 1px solid rgba(0,0,0,0.06);
                border-radius: 16px;
                padding: 24px 20px;
                text-align: center;
                box-shadow: 0 8px 18px rgba(0,0,0,0.10);
            }
            .metric-card .value { font-size: 2rem; font-weight: 800; color: var(--primary); }
            .metric-card .label { color: var(--muted); }
            /* Hide all Material Icons text while keeping the SVG icon */
span[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"] * {
    font-size: 0 !important;
    line-height: 0 !important;
}

/* Also hide any stray text nodes created by Material Icons */
span[class*="st-emotion-cache"] {
    font-size: inherit;
}

span[class*="st-emotion-cache"]:has(svg) {
    font-size: 0 !important;
}

        </style>
        """,
        unsafe_allow_html=True,
    )
