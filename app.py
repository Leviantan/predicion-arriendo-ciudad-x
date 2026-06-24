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
# ESTILO MINIMALISTA LEGIBLE
# ============================================================

st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fb;
        color: #111827;
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    /* HEADER */
    .title-card {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.05);
    }

    .title-card h1 {
        font-size: 1.8rem;
        margin: 0;
        color: #111827;
    }

    .title-card p {
        margin-top: 0.4rem;
        color: #6b7280;
        font-size: 0.95rem;
    }

    /* INFO BOX */
    .info-box {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        color: #111827;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }

    /* METRIC CARDS */
    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }

    .metric-card h4 {
        font-size: 1.4rem;
        margin: 0.2rem 0;
        color: #111827;
    }

    .metric-card p {
        margin: 0;
        color: #6b7280;
        font-size: 0.85rem;
    }

    /* PREDICCIÓN */
    .prediction-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        margin-top: 1rem;
    }

    .prediction-card h1 {
        font-size: 2.2rem;
        margin: 0.5rem 0 0 0;
        color: #16a34a;
    }

    .prediction-card h2 {
        margin: 0;
        font-size: 1.1rem;
        color: #111827;
    }

    /* ERROR */
    .error-card {
        background: #fef2f2;
        border: 1px solid #fecaca;
        padding: 1rem;
        border-radius: 12px;
        color: #991b1b;
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
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES AUXILIARES
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


# ============================================================
# DATAROBOT BATCH
# ============================================================

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

    buffer = io.StringIO()
    df_input.to_csv(buffer, index=False)

    requests.put(
        upload_url,
        headers={
            "Authorization": f"Token {DATAROBOT_API_KEY}",
            "Content-Type": "text/csv"
        },
        data=buffer.getvalue().encode("utf-8")
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
        raise Exception(f"Error en el job: {status}")

    download_url = job_data["links"]["download"]

    result = requests.get(download_url, headers={"Authorization": f"Token {DATAROBOT_API_KEY}"})

    df = pd.read_csv(io.StringIO(result.text))

    progress.progress(100)
    status_text.success("Predicción completada")

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
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("Configuración")

    modo_demo = st.toggle("Modo demo", False)

    st.divider()
    st.write("Variables del modelo")

# ============================================================
# INPUTS
# ============================================================

col1, col2 = st.columns(2)

with col1:
    metros_cuadrados = st.slider("Metros cuadrados", 10, 500, 70)
    habitaciones = st.number_input("Habitaciones", 0, 20, 2)

with col2:
    banos = st.number_input("Baños", 0, 10, 1)
    estrato = st.select_slider("Estrato", [1,2,3,4,5,6], 3)
    calcular = st.button("Predecir")

# ============================================================
# DATAFRAME
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
            with st.spinner("Consultando DataRobot..."):
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
                {str(e)}
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("Streamlit + DataRobot")
