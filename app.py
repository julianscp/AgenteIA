import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# CONFIGURACIÓN CRÍTICA: Forzamos el uso de la API estable v1 antes de cargar genai
os.environ["GOOGLE_API_USE_G2_CLIENT"] = "false"

st.set_page_config(page_title="Airbnb AI Fix", layout="wide")
st.title("🏠 Airbnb Concierge Inteligente (Versión Estable)")

# 1. Cargar Datos
@st.cache_data
def load_data():
    # Cargamos el archivo original
    return pd.read_csv("AB_US_2023.csv") 

try:
    df = load_data()
    st.success(f"✅ Datos cargados: {df.shape[0]} filas.")
except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
    st.stop()

# 2. Configurar Google
api_key = st.sidebar.text_input("Google API Key:", type="password")

if api_key:
    try:
        # Limpiamos la clave y configuramos
        clave_limpia = api_key.strip()
        genai.configure(api_key=clave_limpia)
        
        # Seleccionamos el modelo con la ruta absoluta y sin usar v1beta
        model = genai.GenerativeModel(
            model_name='models/gemini-1.5-flash'
        )
        
        # Pequeño truco: Forzamos una llamada simple para validar la conexión
        # Si esto falla, saltará al except
        _ = model.generate_content("Hola", safety_settings={})

        user_query = st.chat_input("¿Quién es el host con más propiedades?")

        if user_query:
            with st.chat_message("user"):
                st.write(user_query)

            with st.chat_message("assistant"):
                with st.spinner("Analizando datos..."):
                    prompt = f"""
                    Tienes un dataframe llamado 'df' con estas columnas: {list(df.columns)}
                    Escribe ÚNICAMENTE el código de Python necesario para responder a: '{user_query}'
                    El resultado final debe guardarse en una variable llamada 'resultado'.
                    Usa nombres de columnas exactos.
                    No des explicaciones, solo el código.
                    """
                    
                    try:
                        # Llamada directa al modelo estable
                        response = model.generate_content(prompt)
                        codigo_limpio = response.text.replace('```python', '').replace('```', '').strip()
                        
                        # Ejecución del código generado
                        locales = {'df': df}
                        exec(codigo_limpio, {}, locales)
                        resultado = locales.get('resultado', "No se pudo calcular el resultado.")
                        
                        st.write("### Respuesta:")
                        st.write(resultado)
                        
                        with st.expander("Ver lógica interna"):
                            st.code(codigo_limpio)
                    except Exception as e:
                        st.error(f"Error en la generación de respuesta: {e}")
                        
    except Exception as e:
        st.error(f"⚠️ Error de API: {e}")
        st.info("Asegúrate de que tu API Key sea de Google AI Studio y que el modelo gemini-1.5-flash esté disponible.")
else:
    st.info("Ingresa tu API Key para comenzar.")
