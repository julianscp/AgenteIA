import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Airbnb Strategic Analyst 2023", layout="wide")

# CSS personalizado para que no parezca un chat genérico
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #FF5A5F; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stButton>button { border-radius: 20px; background-color: #FF5A5F; color: white; border: none; }
    h1 { color: #484848; font-weight: 800; }
    .chat-container { border: 1px solid #e0e0e0; padding: 20px; border-radius: 15px; background: white; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("AB_US_2023.csv")
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['latitude', 'longitude', 'neighbourhood', 'city'])
        return df
    except Exception as e:
        st.error(f"Error cargando base de datos: {e}")
        return None

df = load_data()

# --- 3. EXTRACCIÓN DE INSIGHTS ---
def get_advanced_insights(df):
    avg_p = df['price'].mean()
    top_n = df['neighbourhood'].value_counts().idxmax()
    top_n_count = df['neighbourhood'].value_counts().max()
    top_city = df['city'].value_counts().idxmax()
    expensive_city = df.groupby('city')['price'].mean().idxmax()
    expensive_val = df.groupby('city')['price'].mean().max()
    return avg_p, top_n, top_n_count, top_city, expensive_city, expensive_val

# --- 4. LÓGICA DEL AGENTE (HARDCODED KEY) ---
GROQ_API_KEY = "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"

def call_groq_agent(prompt_context, user_query):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": prompt_context},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# --- 5. INTERFAZ PRINCIPAL ---
st.title("🚀 Airbnb Strategic Insight Agent")
st.markdown("Analizador inteligente de tendencias inmobiliarias basado en el mercado 2023.")

if df is not None:
    avg_p, top_n, n_count, top_c, exp_c, exp_v = get_advanced_insights(df)
    
    # Dashboard de Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Precio Promedio", f"${avg_p:.2f}")
    col2.metric("📍 Barrio Saturado", top_n)
    col3.metric("💎 Ciudad Exclusiva", exp_c)
    col4.metric("📈 Mayor Oferta", top_c)

    # Mapa con Estilo
    st.markdown("### 🗺️ Distribución Geográfica de Listings")
    st.map(df[['latitude', 'longitude']].sample(n=1000), color='#FF5A5F')

    st.markdown("---")
    
    # --- SECCIÓN DE CONSULTA (HISTORIAL) ---
    st.subheader("💬 Consulta Estratégica")
    
    # Inicializar historial de chat si no existe
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes previos para que no desaparezcan
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input del usuario
    user_input = st.chat_input("Escribe tu consulta aquí...")

    if user_input:
        # 1. Guardar y mostrar pregunta del usuario
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. Preparar contexto mejorado
        prompt_context = f"""
        Eres un Consultor Senior de Real Estate. 
        Contexto del Mercado: Precio medio nacional ${avg_p:.2f}. Barrio con más volumen: {top_n} ({n_count} listings). 
        La ciudad más costosa es {exp_c} (${exp_v:.2f}).
        Regla de oro: No parezcas un bot. Analiza la saturación de mercado, regulaciones y competitividad. 
        Si el usuario pregunta por 'Unincorporated', explica que son zonas con menos regulaciones y mayor flexibilidad para Airbnb.
        """

        # 3. Llamar a la API
        try:
            with st.spinner("Generando análisis estratégico..."):
                response_text = call_groq_agent(prompt_context, user_input)
                
                # 4. Guardar y mostrar respuesta
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                with st.chat_message("assistant"):
                    st.markdown(response_text)
        except Exception as e:
            st.error("Hubo un problema al procesar la respuesta.")

    # --- 6. VISUALIZACIONES INFERIORES ---
    st.markdown("---")
    st.subheader("📊 Análisis de Datos Visual")
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.write("**Top 10 Barrios por Volumen de Listings**")
        n_data = df['neighbourhood'].value_counts().head(10)
        st.bar_chart(n_data, color="#FF5A5F")
    
    with c_right:
        st.write("**Ciudades con Precios más Elevados (Promedio)**")
        c_data = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
        st.bar_chart(c_data, color="#484848")

# Sidebar informativa (Opcional)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Airbnb_Logo_B%C3%A9lo.svg/2560px-Airbnb_Logo_B%C3%A9lo.svg.png", width=150)
st.sidebar.markdown("### Sobre la Herramienta")
st.sidebar.write("Este agente procesa miles de registros de Airbnb 2023 para identificar oportunidades de mercado y riesgos de inversión.")
