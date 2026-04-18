import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Airbnb Strategic Analyst 2023", layout="wide")

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("AB_US_2023.csv")
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['latitude', 'longitude', 'neighbourhood', 'city'])
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = load_data()

# 3. EXTRACCIÓN DE INSIGHTS (Para alimentar el cerebro de la IA)
def get_advanced_insights(df):
    avg_p = df['price'].mean()
    top_n = df['neighbourhood'].value_counts().idxmax()
    top_n_count = df['neighbourhood'].value_counts().max()
    top_city = df['city'].value_counts().idxmax()
    # Encontrar la ciudad más cara
    expensive_city = df.groupby('city')['price'].mean().idxmax()
    expensive_val = df.groupby('city')['price'].mean().max()
    
    return avg_p, top_n, top_n_count, top_city, expensive_city, expensive_val

# 4. INTERFAZ
st.title("🚀 Airbnb Strategic Insight Agent")
st.markdown("---")

if df is not None:
    avg_p, top_n, n_count, top_c, exp_c, exp_v = get_advanced_insights(df)
    
    # Dashboard Visual
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio Promedio", f"${avg_p:.2f}")
    col2.metric("Barrio Hot 🔥", top_n)
    col3.metric("Ciudad más Cara", exp_c)
    col4.metric("Ciudad con más Listings", top_c)

    # Mapa interactivo
    st.map(df[['latitude', 'longitude']].sample(n=1000), color='#FF5A5F')

    # CONFIGURACIÓN DEL AGENTE EN SIDEBAR
    st.sidebar.header("🧠 Cerebro del Agente")
    api_key = st.sidebar.text_input("Groq API Key:", type="password")
    
    user_input = st.chat_input("Pregúntame algo complejo, ej: ¿Por qué hay tantos listings en el área de Unincorporated?")

    if user_input:
        if not api_key:
            st.warning("Introduce la API Key para hablar con el analista.")
        else:
            # PROMPT EVOLUCIONADO (Aquí está el truco para que no sea un robot)
            prompt_analista = f"""
            Eres un consultor senior de Real Estate y Airbnb. No eres un robot, eres un analista con visión crítica.
            
            CONTEXTO REAL DEL DATASET 2023:
            1. El mercado está promediando los ${avg_p:.2f} por noche.
            2. El barrio '{top_n}' es el más saturado con {n_count} propiedades.
            3. La ciudad de '{exp_c}' es la más exclusiva, con precios promedio de ${exp_v:.2f}.
            4. '{top_c}' es el mercado con mayor volumen de oferta.
            
            REGLAS DE RESPUESTA:
            - Usa un tono profesional pero cercano, como un consultor de negocios.
            - No repitas siempre los mismos números si no vienen al caso.
            - Si te preguntan por 'Unincorporated Areas', explica que esto suele deberse a zonas rurales o zonas turísticas fuera de límites municipales donde las regulaciones suelen ser más laxas.
            - Analiza tendencias: menciona competencia, saturación de mercado y oportunidades de inversión.
            """
            
            headers = {"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": prompt_analista},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.8 # Subimos la temperatura para más creatividad
            }
            
            try:
                with st.spinner("Analizando mercado..."):
                    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                    respuesta = response.json()['choices'][0]['message']['content']
                    st.chat_message("assistant").write(respuesta)
            except:
                st.error("Error al conectar con el analista.")

    # Gráficos extra para el video
    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("Top 10 Barrios por Oferta")
        st.bar_chart(df['neighbourhood'].value_counts().head(10))
    with c_right:
        st.subheader("Precio Medio por Ciudad (Top 10)")
        st.bar_chart(df.groupby('city')['price'].mean().sort_values(ascending=False).head(10))
