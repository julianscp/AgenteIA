import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Airbnb Data Expert 2023", layout="wide")

# --- ESTILO ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_stdio=True)

# --- 1. CARGA DE DATOS (EL MOTOR) ---
@st.cache_data
def load_data():
    df = pd.read_csv("AB_US_2023.csv")
    # Limpieza básica de nombres de columnas
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")
    st.stop()

# --- 2. LÓGICA DE ANÁLISIS (SIN IA) ---
# Calculamos las respuestas difíciles con Python puro para que sean 100% exactas
df_365 = df[df['availability_365'] == 365]
host_top = df_365['host_name'].value_counts().idxmax()
host_count = df_365['host_name'].value_counts().max()
precio_promedio = df['price'].mean()

# --- 3. INTERFAZ VISUAL ---
st.title("🏠 Airbnb Concierge & Data Explorer")
st.markdown("---")

# Métricas Principales
m1, m2, m3 = st.columns(3)
m1.metric("Anfitrión Top (365 días)", host_top, f"{host_count} propiedades")
m2.metric("Precio Promedio", f"${precio_promedio:.2f}")
m3.metric("Total Registros", f"{len(df):,}")

# --- 4. CONSULTOR INTELIGENTE (IA OPCIONAL) ---
st.sidebar.header("🤖 Consultor Gemini")
api_key = st.sidebar.text_input("Ingresa tu API Key:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key.strip())
        # Usamos el modelo más reciente con un bloque try/except específico
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.sidebar.success("IA Conectada")
        
        pregunta = st.text_input("Hazle una pregunta estratégica al consultor sobre estos datos:")
        
        if pregunta:
            # En lugar de darle el DF entero (que lo marea), le damos el resumen
            contexto = f"""
            El dataset de Airbnb 2023 tiene {len(df)} filas. 
            El host con más casas disponibles todo el año es {host_top} ({host_count} casas).
            El precio promedio es {precio_promedio}.
            Pregunta del usuario: {pregunta}
            """
            with st.spinner("Consultando al experto..."):
                response = model.generate_content(contexto)
                st.chat_message("assistant").write(response.text)
                
    except Exception as e:
        st.sidebar.warning(f"Modo IA no disponible (Error: {e})")

# --- 5. EXPLORACIÓN VISUAL ---
st.header("📊 Explorador de Tendencias")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top 10 Ciudades por Precio")
    top_cities = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_cities.values, y=top_cities.index, palette="Reds_r", ax=ax)
    st.pyplot(fig)

with col_b:
    st.subheader("Mapa de Propiedades")
    # Muestra una muestra aleatoria para no saturar el navegador
    st.map(df[['latitude', 'longitude']].dropna().sample(1000))

# --- 6. TABLA INTERACTIVA ---
st.markdown("---")
st.subheader("🔎 Buscador de Propiedades")
filtro_ciudad = st.selectbox("Filtrar por ciudad:", ["Todas"] + list(df['city'].unique()))

if filtro_ciudad != "Todas":
    st.dataframe(df[df['city'] == filtro_ciudad].head(50))
else:
    st.dataframe(df.head(50))
