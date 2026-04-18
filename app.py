import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Airbnb Strategy Agent (Neighborhood Focus)", layout="wide")

# 2. CARGA DE DATOS
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

# 3. LÓGICA DE ESTADÍSTICAS (Incluyendo el Barrio más popular)
def get_stats():
    if df is not None:
        avg_price = df['price'].mean()
        # Tu lógica: Barrio más popular por frecuencia
        top_neighbourhood = df['neighbourhood'].value_counts().idxmax()
        # Host más profesional (365 días)
        df_365 = df[df['availability_365'] == 365]
        host_top = df_365['host_name'].value_counts().idxmax() if not df_365.empty else "N/A"
        return avg_price, host_top, top_neighbourhood
    return 0, "N/A", "N/A"

# 4. INTERFAZ DE USUARIO
st.title("🤖 Airbnb Strategic Agent")
st.caption("Análisis por Ciudades y Barrios | Llama-3 & Groq")
st.markdown("---")

if df is not None:
    avg_p, top_h, top_n = get_stats()
    
    # Métricas principales
    c1, c2, c3 = st.columns(3)
    c1.metric("Anfitrión Líder", top_h)
    c2.metric("Barrio más Popular", top_n) # Aquí se muestra tu nueva lógica
    c3.metric("Precio Promedio", f"${avg_p:.2f}")

    # Sidebar: Configuración de la API
    st.sidebar.header("🔑 Configuración")
    api_key = st.sidebar.text_input("Groq API Key:", type="password")
    
    # Chat Input
    user_input = st.chat_input("Pregunta al agente sobre los barrios o estrategias...")

    if user_input:
        if not api_key:
            st.warning("⚠️ Introduce tu Groq API Key en la barra lateral.")
        else:
            prompt_entrenamiento = f"""
            Eres un Agente experto en Estrategia Inmobiliaria.
            DATOS CLAVE 2023:
            - El barrio con más listings (más popular) es: {top_n}.
            - El precio promedio nacional es ${avg_p:.2f}.
            - El host más exitoso es {top_h}.
            
            Analiza la pregunta del usuario basándote en que {top_n} es la zona de mayor demanda/oferta.
            """
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": prompt_entrenamiento}, {"role": "user", "content": user_input}]
            }
            
            try:
                with st.spinner("Analizando tendencias..."):
                    response = requests.post(url, headers=headers, json=payload)
                    texto_agente = response.json()['choices'][0]['message']['content']
                    st.chat_message("assistant").write(texto_agente)
            except:
                st.error("Error de conexión con Groq.")

    # 5. VISUALIZACIONES (Doble gráfico para el video)
    col_graph1, col_graph2 = st.columns(2)

    with col_graph1:
        st.markdown("### 🌆 Top 10 Ciudades (Precio)")
        fig1, ax1 = plt.subplots()
        top_cities = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
        sns.barplot(x=top_cities.values, y=top_cities.index, hue=top_cities.index, palette="Reds_r", ax=ax1, legend=False)
        st.pyplot(fig1)

    with col_graph2:
        st.markdown("### 🏘️ Top 10 Barrios (Densidad)")
        fig2, ax2 = plt.subplots()
        top_neighs = df['neighbourhood'].value_counts().head(10)
        sns.barplot(x=top_neighs.values, y=top_neighs.index, hue=top_neighs.index, palette="Blues_r", ax=ax2, legend=False)
        st.pyplot(fig2)
