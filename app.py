st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1200px;
    }

    h1, h2, h3, h4 {
        color: #0f172a;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .title-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }

    .title-card h1 {
        font-size: 2.2rem;
        margin-bottom: 0.3rem;
        color: #111827;
    }

    .title-card p {
        color: #64748b;
        font-size: 1rem;
    }

    .info-box {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        text-align: center;
        min-height: 120px;
    }

    .metric-card h3 {
        font-size: 1.5rem;
        margin-bottom: 0.2rem;
    }

    .metric-card h4 {
        font-size: 1.3rem;
        color: #2563eb;
        margin-bottom: 0.2rem;
    }

    .metric-card p {
        color: #6b7280;
        font-size: 0.95rem;
    }

    .prediction-card {
        background: white;
        border: 2px solid #22c55e;
        padding: 2rem;
        border-radius: 18px;
        text-align: center;
        margin-top: 1rem;
    }

    .prediction-card h1 {
        color: #16a34a;
        font-size: 2.7rem;
        margin-top: 0.5rem;
    }

    .error-card {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
        padding: 1rem;
        border-radius: 14px;
        margin-top: 1rem;
    }

    div.stButton > button {
        width: 100%;
        height: 3rem;
        background: #2563eb;
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        font-size: 1rem;
    }

    div.stButton > button:hover {
        background: #1d4ed8;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)
