import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Airbnb Data Expert 2023", layout="wide")

# --- ESTILO CORREGIDO ---
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
    """, unsafe_allow_html=True) # <-- Aquí estaba el error, ya está corregido

st.title("🏠 Airbnb Concierge & Data Explorer")
st.markdown("---")

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Asegúrate de que el nombre del archivo coincida con el que subiste a GitHub
    df = pd.read_csv("AB_US_2023.csv")
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    # --- 2. CÁLCULOS DIRECTOS (Súper rápidos) ---
    # Buscamos al host con más disponibilidad total
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

    # --- 4. CONSULTOR INTELIGENTE (IA OPCIONAL) ---
    if api_key:
        try:
            # FORZADO DE VERSIÓN ESTABLE
            # Esto sobreescribe cualquier intento de la librería de usar v1beta
            genai.configure(api_key=api_key.strip(), transport='rest') 
            
            # Usamos el identificador de modelo que Google garantiza como estable
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            st.sidebar.success("IA Conectada")
            pregunta = st.sidebar.text_area("Hazle una pregunta estratégica:")
            
            if pregunta:
                # Simplificamos el contexto para asegurar que la llamada sea ligera
                contexto = f"Dataset Airbnb 2023. Top Host: {host_top}. Precio medio: {precio_promedio:.2f}. Pregunta: {pregunta}"
                
                with st.spinner("Consultando..."):
                    # Forzamos la llamada sin usar streaming para evitar rutas beta
                    response = model.generate_content(contexto)
                    if response.text:
                        st.info(response.text)
                    else:
                        st.warning("La IA no devolvió texto. Revisa tu cuota de API.")
                        
        except Exception as e:
            # Si el error persiste, intentamos una última maniobra: cambiar a 'gemini-1.5-pro'
            if "404" in str(e):
                st.sidebar.warning("Intentando conectar vía ruta alterna...")
                try:
                    model_alt = genai.GenerativeModel('gemini-1.5-pro')
                    response = model_alt.generate_content("Hola, confirma conexión.")
                    st.sidebar.success("Conectado a Gemini Pro")
                except:
                    st.sidebar.error("Error persistente de Google API. Verifica tu clave en AI Studio.")
            else:
                st.sidebar.error(f"Error de IA: {e}")
