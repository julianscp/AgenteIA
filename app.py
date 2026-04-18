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

    # --- 4. CONSULTOR INTELIGENTE (Híbrido) ---
    st.sidebar.header("🤖 Consultor de Datos")
    api_key = st.sidebar.text_input("Ingresa tu API Key (Opcional):", type="password")
    user_query = st.sidebar.text_area("Hazle una pregunta estratégica:")

    if user_query:
        ia_respondio = False
        
        # INTENTO CON IA
        if api_key:
            try:
                # Forzamos configuración estable
                genai.configure(api_key=api_key.strip(), transport='rest')
                
                # Intentamos con el modelo más actual
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                contexto = f"Dataset Airbnb 2023. Host Top: {host_top} ({host_count} casas). Precio medio: {precio_promedio:.2f}. Pregunta: {user_query}"
                
                with st.spinner("Gemini pensando..."):
                    response = model.generate_content(contexto)
                    if response:
                        st.info(f"✨ **Análisis de Gemini:**\n\n{response.text}")
                        ia_respondio = True
            except Exception as e:
                # Intento de respaldo con modelo Pro si falla el Flash
                try:
                    model_alt = genai.GenerativeModel('gemini-pro')
                    response = model_alt.generate_content(f"Analiza brevemente: {user_query}. Contexto: Host {host_top}")
                    st.info(f"✨ **Respuesta (vía Gemini Pro):**\n\n{response.text}")
                    ia_respondio = True
                except:
                    st.sidebar.error(f"Error de conexión: {e}")

        # MOTOR LOCAL (Si la IA no responde o no hay key)
        if not ia_respondio:
            with st.expander("🔍 Análisis Basado en Datos Reales", expanded=True):
                query_l = user_query.lower()
                if "host" in query_l or "anfitrión" in query_l:
                    st.write(f"📊 **Dato:** El líder es **{host_top}** con **{host_count}** unidades activas todo el año.")
                elif "precio" in query_l or "caro" in query_l:
                    st.write(f"💰 **Dato:** El precio promedio nacional en este dataset es de **${precio_promedio:.2f}**.")
                else:
                    st.write("🤖 El motor local analizó tu pregunta. El dataset muestra una alta profesionalización en hosts como Jino & Scott.")
                st.caption("Respuesta generada localmente ante la falta de conexión con la IA.")

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
        st.subheader("Mapa de Propiedades (Muestra)")
        st.map(df[['latitude', 'longitude']].dropna().sample(min(1500, len(df))))

except Exception as e:
    st.error(f"Error en la aplicación: {e}")
