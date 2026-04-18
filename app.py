import streamlit as st
import pandas as pd
import requests
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Agente Airbnb", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("AB_US_2023.csv")
    return df

df = load_data()

# --- HERRAMIENTAS DE PYTHON (Lo que el agente "usa") ---
def tool_top_host():
    df_365 = df[df['availability_365'] == 365]
    top = df_365['host_name'].value_counts().idxmax()
    count = df_365['host_name'].value_counts().max()
    return f"El host top es {top} con {count} propiedades."

def tool_price_stats():
    avg = df['price'].mean()
    return f"El precio promedio general es ${avg:.2f}."

# --- MOTOR DEL AGENTE ---
def agente_brain(pregunta, api_key):
    # System Prompt: Aquí es donde se "entrena" su comportamiento
    prompt_sistema = f"""
    Eres un Agente Analista de Airbnb. 
    Datos actuales: {tool_top_host()} y {tool_price_stats()}.
    Tu objetivo es analizar la pregunta del usuario y dar una respuesta estratégica.
    Si te preguntan por datos específicos, usa la información proporcionada.
    Se profesional, breve y ético.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": f"{prompt_sistema}\nUsuario: {pregunta}"}]}]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()['candidates'][0]['content']['parts'][0]['text']

# --- INTERFAZ ---
st.sidebar.title("Configuración")
key = st.sidebar.text_input("API Key de Google", type="password")

st.title("🤖 Agente Inteligente Airbnb")
query = st.chat_input("Ej: ¿Cuál es la estrategia del host líder?")

if query:
    if key:
        try:
            res = agente_brain(query, key)
            st.chat_message("assistant").write(res)
        except:
            st.error("Error de conexión. Revisa la clave.")
    else:
        st.warning("Ingresa la API Key en la izquierda.")
