import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Airbnb Strategy Agent", layout="wide")

# 2. CARGA DE DATOS (Con manejo de errores integrado)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("AB_US_2023.csv")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar el CSV: {e}")
        return None

df = load_data()

# 3. LÓGICA DEL AGENTE (Funciones de apoyo)
def get_stats():
    if df is not None:
        avg_price = df['price'].mean()
        df_365 = df[df['availability_365'] == 365]
        host_top = df_365['host_name'].value_counts().idxmax() if not df_365.empty else "N/A"
        return avg_price, host_top
    return 0, "N/A"

# 4. INTERFAZ DE USUARIO
st.title("🤖 Airbnb Strategic Agent")
st.markdown("---")

if df is not None:
    avg_p, top_h = get_stats()
    
    # Métricas principales
    c1, c2, c3 = st.columns(3)
    c1.metric("Anfitrión Líder", top_h)
    c2.metric("Precio Promedio", f"${avg_p:.2f}")
    c3.metric("Registros Totales", f"{len(df):,}")

    # Sidebar para el Agente
    st.sidebar.header("Configuración del Agente")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    
    # Chat Input
    user_input = st.chat_input("Hazle una pregunta estratégica al agente...")

    if user_input:
        if not api_key:
            st.warning("Por favor, introduce tu API Key en la barra lateral.")
        else:
            # PROMPT DE ENTRENAMIENTO (Aquí explican el 'from scratch')
            prompt_entrenamiento = f"""
            Eres un Agente experto en Estrategia Inmobiliaria.
            Datos del mercado 2023:
            - Precio promedio: ${avg_p:.2f}
            - Host con más dominio: {top_h}
            Analiza la pregunta del usuario con ética y precisión profesional.
            Pregunta: {user_input}
            """
            
            # Conexión Directa (Evita errores de librerías viejas en el servidor)
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt_entrenamiento}]}]}
            
            try:
                with st.spinner("El agente está analizando los datos..."):
                    response = requests.post(url, json=payload)
                    respuesta_json = response.json()
                    texto_agente = respuesta_json['candidates'][0]['content']['parts'][0]['text']
                    st.chat_message("assistant").write(texto_agente)
            except Exception as e:
                st.error("El agente no pudo conectar. Usando respuesta local de respaldo.")
                st.info(f"Análisis local: El mercado liderado por {top_h} muestra precios de ${avg_p:.2f}.")

    # 5. VISUALIZACIONES (Para el video)
    st.markdown("### 📊 Tendencias de Mercado")
    fig, ax = plt.subplots(figsize=(10, 4))
    top_cities = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
    sns.barplot(x=top_cities.values, y=top_cities.index, palette="Reds_r", ax=ax)
    st.pyplot(fig)
