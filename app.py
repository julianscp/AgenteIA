import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Airbnb Strategy Agent 2023", layout="wide")

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("AB_US_2023.csv")
        df.columns = df.columns.str.strip()
        # Limpieza de coordenadas para evitar errores en el mapa
        df = df.dropna(subset=['latitude', 'longitude'])
        # Asegurarnos de que lat/lon sean números
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        return df.dropna(subset=['latitude', 'longitude'])
    except Exception as e:
        st.error(f"Error al cargar el CSV: {e}")
        return None

df = load_data()

# 3. LÓGICA DE ESTADÍSTICAS
def get_stats():
    if df is not None:
        avg_price = df['price'].mean()
        # Tu lógica de barrio más popular
        top_n = df['neighbourhood'].value_counts().idxmax()
        # Host con más propiedades (profesional)
        df_365 = df[df['availability_365'] == 365]
        host_top = df_365['host_name'].value_counts().idxmax() if not df_365.empty else "N/A"
        return avg_price, host_top, top_n
    return 0, "N/A", "N/A"

# 4. INTERFAZ DE USUARIO
st.title("🤖 Airbnb Strategic Agent")
st.markdown("---")

if df is not None:
    avg_p, top_h, top_n = get_stats()
    
    # Métricas en la parte superior
    c1, c2, c3 = st.columns(3)
    c1.metric("Barrio más Popular", top_n)
    c2.metric("Precio Promedio", f"${avg_p:.2f}")
    c3.metric("Anfitrión Líder", top_h)

    # --- MAPA INTERACTIVO (Versión compatible que NO se ve negra) ---
    st.markdown("### 📍 Distribución de Propiedades en EE.UU.")
    
    # Filtramos una muestra para que el mapa sea fluido
    # Usamos st.map que es más estable para despliegues rápidos
    map_df = df[['latitude', 'longitude']].sample(n=1500)
    st.map(map_df, color='#FF5A5F') # El color oficial de Airbnb

    # --- SECCIÓN DEL AGENTE (GROQ) ---
    st.sidebar.header("🔑 Configuración")
    api_key = st.sidebar.text_input("Groq API Key:", type="password", help="Consíguela en console.groq.com")
    
    st.sidebar.markdown("""
    **Guía para el video:**
    - El mapa muestra 1,500 puntos aleatorios.
    - El agente usa **Llama 3** para analizar.
    """)

    user_input = st.chat_input("Hazle una pregunta estratégica al agente...")

    if user_input:
        if not api_key:
            st.warning("⚠️ Introduce la API Key en la barra lateral para activar al agente.")
        else:
            # Prompt estratégico
            prompt = f"""Eres un consultor de Airbnb. 
            Contexto: El barrio más popular es {top_n}, el precio medio es ${avg_p:.2f} y el líder es {top_h}.
            Pregunta: {user_input}"""
            
            headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": user_input}]
            }
            
            try:
                with st.spinner("El agente está pensando..."):
                    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                    respuesta = response.json()['choices'][0]['message']['content']
                    st.chat_message("assistant").write(respuesta)
            except:
                st.error("Error al conectar con Groq. Verifica tu API Key.")

    # --- GRÁFICOS INFERIORES ---
    st.markdown("---")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("#### Top 10 Barrios (Oferta)")
        st.bar_chart(df['neighbourhood'].value_counts().head(10))
    with g2:
        st.markdown("#### Precio por Ciudad (Top 10)")
        top_cities = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
        st.bar_chart(top_cities)
