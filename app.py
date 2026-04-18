import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
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
        # Limpieza básica de coordenadas
        df = df.dropna(subset=['latitude', 'longitude'])
        return df
    except Exception as e:
        st.error(f"Error al cargar el CSV: {e}")
        return None

df = load_data()

# 3. LÓGICA DE ESTADÍSTICAS
def get_stats():
    if df is not None:
        avg_price = df['price'].mean()
        top_n = df['neighbourhood'].value_counts().idxmax()
        df_365 = df[df['availability_365'] == 365]
        host_top = df_365['host_name'].value_counts().idxmax() if not df_365.empty else "N/A"
        return avg_price, host_top, top_n
    return 0, "N/A", "N/A"

# 4. INTERFAZ Y MÉTRICAS
st.title("🤖 Airbnb Strategic Agent & Map Viewer")
st.markdown("---")

if df is not None:
    avg_p, top_h, top_n = get_stats()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Barrio más Popular", top_n)
    col2.metric("Precio Promedio", f"${avg_p:.2f}")
    col3.metric("Anfitrión Dominante", top_h)

    # --- SECCIÓN DEL MAPA (Visualización Geográfica) ---
    st.markdown("### 🗺️ Ubicación Geográfica de los Alojamientos")
    
    # Tomamos una muestra para que el mapa sea fluido en el video
    map_data = df[['latitude', 'longitude', 'price']].sample(n=2000)
    
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=map_data['latitude'].mean(),
            longitude=map_data['longitude'].mean(),
            zoom=3,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[longitude, latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=20000,
            ),
        ],
    ))

    # --- CHAT AGENTE CON GROQ ---
    st.sidebar.header("🔑 Configuración")
    api_key = st.sidebar.text_input("Groq API Key:", type="password")
    
    user_input = st.chat_input("Pregunta sobre la ubicación o estrategia...")

    if user_input:
        if not api_key:
            st.warning("⚠️ Ingresa la API Key en la barra lateral.")
        else:
            prompt_entrenamiento = f"Eres un experto inmobiliario. El barrio más popular es {top_n} y el precio medio es ${avg_p:.2f}. Responde: {user_input}"
            
            headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": prompt_entrenamiento}, {"role": "user", "content": user_input}]
            }
            
            try:
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                st.chat_message("assistant").write(response.json()['choices'][0]['message']['content'])
            except:
                st.error("Error al conectar con el cerebro del agente.")

    # --- GRÁFICOS DE APOYO ---
    st.markdown("---")
    c_graph1, c_graph2 = st.columns(2)
    with c_graph1:
        st.markdown("#### Top Barrios")
        st.bar_chart(df['neighbourhood'].value_counts().head(10))
    with c_graph2:
        st.markdown("#### Distribución de Precios")
        fig, ax = plt.subplots()
        sns.histplot(df[df['price'] < 1000]['price'], bins=30, kde=True, ax=ax, color='salmon')
        st.pyplot(fig)
