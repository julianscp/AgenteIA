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
    # --- 4. CONSULTOR INTELIGENTE (Versión Híbrida Blindada) ---
    st.sidebar.header("🤖 Consultor de Datos")
    api_key = st.sidebar.text_input("Ingresa tu API Key (Opcional):", type="password")

    pregunta = st.sidebar.text_area("Hazle una pregunta estratégica:")

    if pregunta:
        # 1. INTENTO CON GOOGLE (Si hay API Key)
        if api_key:
            try:
                genai.configure(api_key=api_key.strip(), transport='rest')
                model = genai.GenerativeModel('gemini-1.5-flash')
                contexto = f"Dataset Airbnb 2023. Host Top: {host_top}. Precio promedio: {precio_promedio:.2f}. Pregunta: {pregunta}"
                response = model.generate_content(contexto)
                st.info(f"✨ **Análisis de Gemini:**\n\n{response.text}")
            except Exception:
                st.sidebar.warning("⚠️ Google API no responde. Usando motor de análisis local...")
                # Si falla Google, cae automáticamente al motor local de abajo
                
        # 2. MOTOR DE ANÁLISIS LOCAL (Siempre funciona, no requiere internet/API)
        with st.expander("🔍 Análisis Basado en Datos Reales", expanded=True):
            pregunta_l = pregunta.lower()
            
            if "host" in pregunta_l or "anfitrión" in pregunta_l:
                st.write(f"📊 **Dato Clave:** El anfitrión con mayor inventario operativo (365 días) es **{host_top}**. Esto sugiere una gestión profesional con **{host_count}** unidades activas.")
            
            elif "precio" in pregunta_l or "caro" in pregunta_l or "barato" in pregunta_l:
                st.write(f"💰 **Análisis de Precios:** El costo promedio es de **${precio_promedio:.2f}**. Las ciudades con precios más altos están lideradas por el top de tu gráfica de barras.")
            
            elif "ciudad" in pregunta_l or "donde" in pregunta_l:
                ciudad_top = df['city'].value_counts().idxmax()
                st.write(f"📍 **Geografía:** La ciudad con más listados en este dataset es **{ciudad_top}**. Es el mercado con mayor competencia actualmente.")
            
            else:
                st.write("🤖 **Nota del Sistema:** No puedo conectar con el servidor de Google ahora mismo, pero basándome en los datos: tienes un mercado de más de 232 mil propiedades donde el precio medio es alto, lo que indica un mercado de alta demanda.")
            
            st.caption("Esta respuesta fue generada localmente porque la API de Google está experimentando bloqueos de conexión.")
