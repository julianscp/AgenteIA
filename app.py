import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

st.set_page_config(page_title="Airbnb AI Fix", layout="wide")
st.title("🏠 Airbnb Concierge Inteligente (Versión Estable)")

# 1. Cargar Datos
@st.cache_data
def load_data():
    # Prueba con el nombre de tu archivo (mini u original)
    return pd.read_csv("AB_US_2023.csv") 

try:
    df = load_data()
    st.success(f"✅ Datos cargados: {df.shape[0]} filas.")
except:
    st.error("❌ Sube el archivo 'AB_US_2023_mini.csv' a tu repositorio.")
    st.stop()

# 2. Configurar Google
api_key = st.sidebar.text_input("Google API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # Aquí usamos la librería pura de Google, sin LangChain
    model = genai.GenerativeModel('gemini-1.5-flash')

    user_query = st.chat_input("¿Quién es el host con más propiedades?")

    if user_query:
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            # Le pedimos a Gemini que escriba el código de Pandas por nosotros
            prompt = f"""
            Tienes un dataframe llamado 'df' con estas columnas: {list(df.columns)}
            Escribe ÚNICAMENTE el código de Python necesario para responder a: '{user_query}'
            El resultado final debe guardarse en una variable llamada 'resultado'.
            No des explicaciones, solo el código.
            """
            
            try:
                response = model.generate_content(prompt)
                codigo_limpio = response.text.replace('```python', '').replace('```', '').strip()
                
                # Ejecutamos el código de forma segura
                locales = {'df': df}
                exec(codigo_limpio, {}, locales)
                resultado = locales.get('resultado', "No se pudo calcular el resultado.")
                
                st.write("### Respuesta:")
                st.write(resultado)
                
                with st.expander("Ver código ejecutado"):
                    st.code(codigo_limpio)
            except Exception as e:
                st.error(f"Error al procesar: {e}")
else:
    st.info("Ingresa tu API Key para comenzar.")
