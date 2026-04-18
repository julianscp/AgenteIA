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

    # --- 4. CONSULTOR INTELIGENTE (Sidebar) ---
    st.sidebar.header("🤖 Consultor Gemini")
    api_key = st.sidebar.text_input("Ingresa tu API Key:", type="password")

    if api_key:
        try:
            # Configuración forzada para evitar errores 404 de v1beta
            genai.configure(api_key=api_key.strip(), transport='rest')
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            st.sidebar.success("IA Conectada")
            pregunta = st.sidebar.text_area("Hazle una pregunta estratégica:")
            
            if pregunta:
                contexto = f"Dataset Airbnb 2023. Host Top: {host_top} con {host_count} casas. Precio medio: {precio_promedio:.2f}. Pregunta: {pregunta}"
                with st.spinner("Consultando..."):
                    response = model.generate_content(contexto)
                    st.info(response.text)
                    
        except Exception as e:
            if "404" in str(e):
                st.sidebar.warning("Intentando ruta alterna (Gemini Pro)...")
                try:
                    model_alt = genai.GenerativeModel('models/gemini-1.5-pro')
                    res = model_alt.generate_content("Confirmar conexión.")
                    st.sidebar.success("Conectado a Gemini Pro")
                except:
                    st.sidebar.error("Error crítico de API Google.")
            else:
                st.sidebar.error(f"Error de IA: {e}")

    # --- 5. VISUALIZACIÓN ---
    st.header("📊 Explorador de Tendencias")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top Ciudades por Precio")
        top_cities = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=top_cities.values, y=top_cities.index, color="#ff5a5f", ax=ax)
        st.pyplot(fig)

    with col_b:
        st.subheader("Mapa de Propiedades")
        # Muestra una muestra para evitar lentitud
        sample_size = min(2000, len(df))
        st.map(df[['latitude', 'longitude']].dropna().sample(sample_size))

except Exception as e:
    st.error(f"Error en la aplicación: {e}")
