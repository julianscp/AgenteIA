import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Airbnb Strategy Agent (Groq Edition)", layout="wide")

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    try:
        # Cargamos el dataset (asegúrate de que el CSV esté en el mismo repo)
        df = pd.read_csv("AB_US_2023.csv")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar el CSV: {e}")
        return None

df = load_data()

# 3. LÓGICA DE ESTADÍSTICAS
def get_stats():
    if df is not None:
        avg_price = df['price'].mean()
        # Filtrar disponibilidad 365 para ver anfitriones profesionales
        df_365 = df[df['availability_365'] == 365]
        host_top = df_365['host_name'].value_counts().idxmax() if not df_365.empty else "N/A"
        return avg_price, host_top
    return 0, "N/A"

# 4. INTERFAZ DE USUARIO
st.title("🤖 Airbnb Strategic Agent")
st.caption("Powered by Llama-3 & Groq | University Project")
st.markdown("---")

if df is not None:
    avg_p, top_h = get_stats()
    
    # Métricas principales (Visualización rápida)
    c1, c2, c3 = st.columns(3)
    c1.metric("Anfitrión Líder (Profesional)", top_h)
    c2.metric("Precio Promedio General", f"${avg_p:.2f}")
    c3.metric("Registros en Dataset", f"{len(df):,}")

    # Sidebar: Configuración de la API
    st.sidebar.header("🔑 Configuración")
    api_key = st.sidebar.text_input("Groq API Key:", type="password", help="Obtenla en console.groq.com")
    
    st.sidebar.info("""
    **Instrucciones para el video:**
    1. Ingresa la API Key.
    2. Haz una pregunta sobre el mercado.
    3. El agente analizará los datos de 2023.
    """)
    
    # Chat Input
    user_input = st.chat_input("Ej: ¿Cuál es la ventaja competitiva de los hosts top?")

    if user_input:
        if not api_key:
            st.warning("⚠️ Introduce tu Groq API Key en la barra lateral.")
        else:
            # PROMPT DE ENTRENAMIENTO (Lógica del Agente)
            prompt_entrenamiento = f"""
            Eres un Agente experto en Estrategia Inmobiliaria y Análisis de Datos.
            CONTEXTO DEL DATASET AIRBNB 2023:
            - Tenemos {len(df)} registros en total.
            - El precio promedio nacional es ${avg_p:.2f}.
            - El anfitrión con mayor presencia profesional (disponibilidad 365 días) es: {top_h}.
            
            TAREA:
            Responde a la pregunta del usuario usando este contexto. Sé profesional, estratégico y breve. 
            Si te preguntan algo fuera de estos datos, usa tu conocimiento general pero prioriza los datos mencionados.
            """
            
            # CONEXIÓN CON GROQ (API REST)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key.strip()}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": prompt_entrenamiento},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7
            }
            
            try:
                with st.spinner("🧠 El agente está razonando..."):
                    response = requests.post(url, headers=headers, json=payload)
                    respuesta_json = response.json()
                    
                    if "choices" in respuesta_json:
                        texto_agente = respuesta_json['choices'][0]['message']['content']
                        with st.chat_message("assistant"):
                            st.write(texto_agente)
                    else:
                        st.error(f"Error de API: {respuesta_json.get('error', {}).get('message', 'Desconocido')}")
            
            except Exception as e:
                st.error(f"Fallo en la conexión: {e}")

    # 5. VISUALIZACIONES (Impacto visual para el video)
    st.markdown("### 📊 Top 10 Ciudades por Precio Promedio")
    fig, ax = plt.subplots(figsize=(10, 4))
    top_cities = df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)
    
    # Usamos un color acorde a Airbnb (rojo/coral)
    sns.barplot(x=top_cities.values, y=top_cities.index, hue=top_cities.index, palette="Reds_r", ax=ax, legend=False)
    ax.set_xlabel("Precio Promedio ($)")
    ax.set_ylabel("Ciudad")
    st.pyplot(fig)
