import streamlit as st
import pandas as pd
import requests
import time
import io

# ============================================================
# CONFIGURACIÓN DATAROBOT
# ============================================================

DATAROBOT_API_KEY = st.secrets["DATAROBOT_API_KEY"]
DATAROBOT_DEPLOYMENT_ID = st.secrets["DATAROBOT_DEPLOYMENT_ID"]
DATAROBOT_HOST = st.secrets["DATAROBOT_HOST"]

# ============================================================
# CONFIG STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Predicción de Arriendos",
    page_icon="🏠",
    layout="wide"
)

# ============================================================
# ESTILO MINIMALISTA
# ============================================================

st.markdown("""
<style>
    .stApp {
        background-color: #0b1220;
        color: #e5e7eb;
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* HEADER */
    .title-card {
        background: #111827;
        border: 1px solid #1f2937;
        padding: 1.8rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .title-card h1 {
        font-size: 2rem;
        margin: 0;
        color: #f9fafb;
    }

    .title-card p {
        margin-top: 0.4rem;
        color: #9ca3af;
        font-size: 0.95rem;
    }

    /* INFO BOX */
    .info-box {
        background: #111827;
        border: 1px solid #1f2937;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        color: #e5e7eb;
    }

    /* METRIC CARDS */
    .metric-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }

    .metric-card h4 {
        font-size: 1.4rem;
        margin: 0.2rem 0;
        color: #f9fafb;
    }

    .metric-card p {
        margin: 0;
        color: #9ca3af;
        font-size: 0.85rem;
    }

    /* PREDICCIÓN */
    .prediction-card {
        background: #0f172a;
        border: 1px solid #334155;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        margin-top: 1rem;
    }

    .prediction-card h1 {
        font-size: 2.2rem;
        margin: 0.5rem 0 0 0;
        color: #22c55e;
    }

    .prediction-card h2 {
        margin: 0;
        font-size: 1.1rem;
        color: #e5e7eb;
    }

    /* ERROR */
    .error-card {
        background: #1f1b1b;
        border: 1px solid #7f1d1d;
        padding: 1rem;
        border-radius: 12px;
        color: #fca5a5;
    }

    /* BOTÓN */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-weight: 600;
        background: #2563eb;
        color: white;
        border: none;
    }

    div.stButton > button:hover {
        background: #1d4ed8;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES
# ============================================================

def formato_cop(valor):
    try:
        valor = float(valor)
        return f"${valor:,.0f}".replace(",", ".") + " COP"
    except:
        return str(valor)


def detectar_columna_prediccion(resultado, columnas_entrada):
    columnas = list(resultado.columns)

    posibles = [
        col for col in columnas
        if "prediction" in col.lower()
        and "status" not in col.lower()
        and col not in columnas_entrada
    ]

    if posibles:
        return posibles[0]

    posibles = [
        col for col in columnas
        if "predicted" in col.lower()
        and col not in columnas_entrada
    ]

    if posibles:
        return posibles[0]

    return None


def hacer_prediccion_batch(df_input):
    batch_url = f"{DATAROBOT_HOST}/api/v2/batchPredictions/"

    headers_json = {
        "Authorization": f"Token {DATAROBOT_API_KEY}",
        "Content-Type": "application/json; encoding=utf-8"
    }

    payload = {
        "deploymentId": DATAROBOT_DEPLOYMENT_ID,
        "passthroughColumnsSet": "all",
        "includePredictionStatus": True
    }

    response = requests.post(batch_url, headers=headers_json, json=payload)

    if response.status_code >= 400:
        raise Exception(response.text)

    job = response.json()

    upload_url = job["links"]["csvUpload"]
    job_url = job["links"]["self"]

    csv_buffer = io.StringIO()
    df_input.to_csv(csv_buffer, index=False)

    requests.put(
        upload_url,
        headers={
            "Authorization": f"Token {DATAROBOT_API_KEY}",
            "Content-Type": "text/csv"
        },
        data=csv_buffer.getvalue().encode("utf-8")
    )

    progress = st.progress(0)
    status_text = st.empty()

    status = ""

    while status not in ["COMPLETED", "FAILED", "ABORTED"]:
        job_response = requests.get(job_url, headers={"Authorization": f"Token {DATAROBOT_API_KEY}"})
        job_data = job_response.json()

        status = job_data.get("status", "")
        pct = int(float(job_data.get("percentageCompleted", 0)))

        progress.progress(min(pct, 100))
        status_text.write(f"Estado: {status} ({pct}%)")

        time.sleep(2)

    if status != "COMPLETED":
        raise Exception(f"Job terminó en estado {status}")

    download_url = job_data["links"]["download"]

    result = requests.get(download_url, headers={"Authorization": f"Token {DATAROBOT_API_KEY}"})
    df = pd.read_csv(io.StringIO(result.text))

    progress.progress(100)
    status_text.success("Completado")

    return df

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="title-card">
    <h1>Predicción de Arriendos</h1>
    <p>Modelo de Machine Learning conectado a DataRobot</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# INPUTS
# ============================================================

with st.sidebar:
    st.header("Configuración")

    modo_demo = st.toggle("Modo demo", False)

    st.divider()
    st.write("Variables: metros, habitaciones, baños, estrato")

col1, col2 = st.columns(2)

with col1:
    metros_cuadrados = st.slider("Metros", 10, 500, 70)
    habitaciones = st.number_input("Habitaciones", 0, 20, 2)

with col2:
    banos = st.number_input("Baños", 0, 10, 1)
    estrato = st.select_slider("Estrato", [1,2,3,4,5,6], 3)
    calcular = st.button("Predecir")

# ============================================================
# DATA
# ============================================================

input_data = pd.DataFrame([{
    "metros_cuadrados": metros_cuadrados,
    "habitaciones": habitaciones,
    "banos": banos,
    "estrato": estrato
}])

st.dataframe(input_data, use_container_width=True)

# ============================================================
# EJECUCIÓN
# ============================================================

if calcular:

    if modo_demo:
        pred = metros_cuadrados * 18000 + habitaciones * 120000 + banos * 100000 + estrato * 180000

        st.markdown(f"""
        <div class="prediction-card">
            <h2>Resultado demo</h2>
            <h1>{formato_cop(pred)}</h1>
        </div>
        """, unsafe_allow_html=True)

    else:
        try:
            with st.spinner("Consultando modelo..."):
                resultado = hacer_prediccion_batch(input_data)

            col = detectar_columna_prediccion(resultado, list(input_data.columns))

            if col:
                valor = formato_cop(resultado[col].iloc[0])

                st.markdown(f"""
                <div class="prediction-card">
                    <h2>Precio estimado</h2>
                    <h1>{valor}</h1>
                </div>
                """, unsafe_allow_html=True)

            st.dataframe(resultado, use_container_width=True)

        except Exception as e:
            st.markdown(f"""
            <div class="error-card">
                Error: {str(e)}
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Streamlit + DataRobot")
