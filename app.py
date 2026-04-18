import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Airbnb Data Expert 2023", layout="wide")

# --- ESTILO ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏠 Airbnb Concierge & Data Explorer")
st.markdown("---")

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_csv("AB_US_2023.csv")
    df.columns = df.columns.str.strip()
    return df

# --- INICIO DEL BLOQUE PRINCIPAL ---
try:
    df = load_data()
    
    # --- 2. CÁLCULOS DIRECTOS ---
    df_365 = df[df['availability_365'] == 365]
    if not df_365.empty:
        counts = df_365['host_name'].value_counts()
        host_top = counts.idxmax()
        host_count = counts.max()
    else:
        host_top = "N/A"
        host_count = 0

    precio_promedio = df['price'].mean()

    # --- 3. DASHBOARD DE MÉTRICAS ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Anfitrión Top (365 días)", host_top, f"{host_count} propiedades")
    m2.metric("Precio Promedio", f"${precio_promedio:.2f}")
    m3.metric("Total Registros", f"{len(df):,}")

    # --- 4. CONSULTOR INTELIGENTE (Híbrido) ---
    st.sidebar.header("🤖 Consultor de Datos")
    api_key = st.sidebar.text_input("Ingresa tu API Key (Opcional):", type="password")
    pregunta = st.sidebar.text_area("Hazle una pregunta estratégica:")

    if pregunta:
        # Intento con IA
        ia_respondio = False
try:
            # Forzamos la configuración REST
            genai.configure(api_key=api_key.strip(), transport='rest')
            
            # INTENTO 1: El nombre más estándar hoy
            model = genai.GenerativeModel('gemini-1.5-flash-latest') 
            
            st.sidebar.success("IA Conectada")
            pregunta = st.sidebar.text_area("Hazle una pregunta estratégica:")
            
            if pregunta:
                # Contexto ultra-reducido para evitar errores de tokens
                contexto = f"Dataset Airbnb 2023. Host Top: {host_top}. Precio: {precio_promedio:.2f}. Pregunta: {pregunta}"
                
                with st.spinner("Gemini pensando..."):
                    # Forzamos la versión v1 explícitamente en la llamada
                    response = model.generate_content(contexto)
                    
                    if response:
                        st.info(f"✨ **Análisis de Gemini:**\n\n{response.text}")
                        ia_respondio = True

        except Exception as e:
            # SI FALLA EL ANTERIOR, INTENTAMOS CON EL NOMBRE SIN 'MODELS/'
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                response = model_alt.generate_content(f"Responde corto: Conectado a {host_top}")
                st.info(f"✨ **Respuesta (vía Gemini Pro):**\n\n{response.text}")
                ia_respondio = True
            except:
                st.sidebar.error(f"Error de conexión: {e}")
# --- FIN DEL BLOQUE PRINCIPAL ---
