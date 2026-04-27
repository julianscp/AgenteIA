import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. CONFIGURACIÓN Y ESTILO (UI/UX MEJORADA) ---
st.set_page_config(page_title="Airbnb Strategic Analyst 2023", layout="wide")

# CSS que funciona en Modo Claro y Oscuro
st.markdown("""
    <style>
    /* Forzamos colores para las métricas y contenedores para que no se pierdan en el fondo */
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF5A5F;
        color: #1E1E1E !important; /* Texto oscuro para legibilidad */
    }
    [data-testid="stMetricValue"] {
        color: #FF5A5F !important;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #484848 !important;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FF5A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #484848;
        margin-bottom: 2rem;
    }
    /* Estilo para los mensajes del chat */
    .stChatMessage {
        border: 1px solid #e0e0e0;
        border-radius: 15px;
    }
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

# --- 4. LÓGICA DEL AGENTE (KEY INTEGRADA) ---
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
st.markdown('<p class="main-header">🚀 Airbnb Strategic Insight Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analizador de tendencias inmobiliarias basado en el mercado 2023.</p>', unsafe_allow_html=True)

if df is not None:
    avg_p, top_n, n_count, top_c, exp_c, exp_v = get_advanced_insights(df)
    
    # Dashboard de Métricas con diseño corregido
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("💰 Precio Promedio", f"${avg_p:.2f}")
    with col2: st.metric("📍 Barrio Saturado", top_n)
    with col3: st.metric("💎 Ciudad Exclusiva", exp_c)
    with col4: st.metric("📈 Mayor Oferta", top_c)

    # Mapa Interactivo
    st.markdown("### 🗺️ Distribución Geográfica")
    st.map(df[['latitude', 'longitude']].sample(n=1000), color='#FF5A5F')

    st.markdown("---")
    
    # --- SECCIÓN DE CONSULTA CON HISTORIAL ---
    st.subheader("💬 Consola de Análisis Estratégico")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Contenedor para que el historial se vea ordenado
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input del usuario
    user_input = st.chat_input("Pregunta sobre rentabilidad, zonas o competencia...")

    if user_input:
        # Guardar y mostrar pregunta del usuario inmediatamente
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Contexto para el Agente
        prompt_context = f"""
        Eres un Consultor Senior de Real Estate experto en el mercado de USA. 
        Contexto 2023: Precio medio ${avg_p:.2f}. El barrio más saturado es {top_n}.
        La ciudad más exclusiva es {exp_c}.
        
        INSTRUCCIONES: No seas repetitivo. Si preguntan por 'Unincorporated Areas', explica que son zonas con leyes de zonificación flexibles. Proporciona insights sobre inversión y saturación.
        """

        try:
            with st.spinner("Analizando base de datos..."):
                response_text = call_groq_agent(prompt_context, user_input)
                
                # Guardar y mostrar respuesta
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                with st.chat_message("assistant"):
                    st.markdown(response_text)
                    # Forzamos un rerun para asegurar que el historial se mantenga visible arriba
                    st.rerun()
        except Exception as e:
            st.error("Error al procesar la respuesta.")

    # --- 6. VISUALIZACIONES INFERIORES ---
    st.markdown("---")
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("**Top 10 Barrios por Volumen**")
        st.bar_chart(df['neighbourhood'].value_counts().head(10), color="#FF5A5F")
    
    with col_r:
        st.write("**Ciudades con Precios Prime (Promedio)**")
        c_data = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
        st.bar_chart(c_data, color="#484848")

# --- SIDEBAR: DESCRIPCIÓN DETALLADA DEL AGENTE (CORREGIDO) ---
with st.sidebar:
    # Logo estable de Airbnb
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Airbnb_Logo_B%C3%A9lo.svg/512px-Airbnb_Logo_B%C3%A9lo.svg.png", width=150)
    
    st.markdown("""
    # 🤖 Sobre el Agente Estratégico
    
    Este agente es una **IA Analítica** entrenada para procesar el dataset de **Airbnb US 2023**. Utiliza una arquitectura de **Llama-3 sobre LPUs (Groq)** para ofrecer respuestas con baja latencia.
    
    ### 🎯 ¿Qué puede hacer?
    * **Análisis de Saturación:** Identifica exceso de oferta en barrios.
    * **Benchmarking:** Compara precios locales vs promedio nacional.
    * **Explicación de Anomalías:** Analiza zonas como *Unincorporated Areas*.
    * **Estrategia:** Sugiere ciudades según exclusividad y volumen.
    
    ### ❓ ¿Qué puedes preguntarle?
    1. *"¿Por qué Unincorporated Areas domina el volumen frente a ciudades grandes?"*
    2. *"¿Me conviene más Clark County o New York para lujo?"*
    3. *"¿Qué impacto tiene el precio promedio de $259 en la competitividad?"*
    
    ---
    **Tecnología:** Python + Streamlit + Llama-3.
    """)
    
    st.info("📌 **Nota del Equipo:** El agente utiliza razonamiento deductivo basado en los datos cargados en tiempo real.")
