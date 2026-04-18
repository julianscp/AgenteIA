import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent

# Configuración de la interfaz
st.set_page_config(page_title="Airbnb Smart Agent", layout="wide")
st.title("🏠 Airbnb Concierge Inteligente")

# 1. Cargar la Base de Datos
@st.cache_data 
def cargar_datos():
    # Asegúrate de que el archivo se llame exactamente así en tu GitHub
    df = pd.read_csv("AB_US_2023.csv") 
    return df

try:
    df = cargar_datos()
    st.success("✅ Datos cargados")
except Exception as e:
    st.error(f"❌ Error al cargar CSV: {e}")
    st.stop()

# 2. Configuración de API Key (Secrets de Streamlit)
# En Streamlit Cloud, usaremos st.secrets para mayor seguridad
with st.sidebar:
    st.header("Configuración")
    
    # Intenta obtener la clave desde los Secrets de Streamlit
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("🔑 API Key cargada desde Secrets")
    else:
        api_key = st.text_input("Ingresa tu Google API Key:", type="password")

# 3. Lógica del Agente
if api_key:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=api_key,
            temperature=0.2
        )

        agent = create_pandas_dataframe_agent(
            llm, 
            df, 
            verbose=True, 
            allow_dangerous_code=True,
            handle_parsing_errors=True
        )

        user_query = st.chat_input("Ejemplo: ¿Cuál es el anfitrión con más propiedades?")

        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                with st.spinner("Analizando..."):
                    # Usamos .invoke() que es el estándar actual
                    respuesta = agent.invoke({"input": user_query})
                    st.write(respuesta["output"])
                    
                    if plt.get_fignums():
                        st.pyplot(plt.gcf())
                        plt.clf() 

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
else:
    st.info("💡 Ingresa tu API Key para comenzar.")
