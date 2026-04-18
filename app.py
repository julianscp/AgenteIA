import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Airbnb Data Expert", layout="wide")

# Estilo personalizado
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff5a5f; color: white; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("📊 Airbnb Data Explorer 2023")
st.markdown("---")

# 1. Carga de Datos (Sin cambios, esto ya te funcionaba)
@st.cache_data
def load_data():
    return pd.read_csv("AB_US_2023.csv")

try:
    df = load_data()
    st.sidebar.success(f"✅ {len(df):,} registros cargados")
except Exception as e:
    st.error(f"No se pudo cargar el archivo: {e}")
    st.stop()

# 2. PANEL DE CONTROL (Sidebar)
st.sidebar.header("🔍 Filtros de Búsqueda")
ciudad = st.sidebar.multiselect("Selecciona Ciudad:", options=df['city'].unique(), default=df['city'].unique()[:5])
precio_max = st.sidebar.slider("Precio máximo por noche:", 0, int(df['price'].max()), 500)

df_filtrado = df[(df['city'].isin(ciudad)) & (df['price'] <= precio_max)]

# 3. RESPUESTAS AUTOMÁTICAS (Lo que antes hacía la IA, ahora es instantáneo)
st.header("💡 Análisis Rápido")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏆 Host con más propiedades (365 días)"):
        # Filtramos disponibilidad total
        full_year = df[df['availability_365'] == 365]
        if not full_year.empty:
            ganador = full_year['host_name'].value_counts().idxmax()
            total = full_year['host_name'].value_counts().max()
            st.info(f"El anfitrión es **{ganador}** con **{total}** propiedades disponibles todo el año.")
        else:
            st.warning("No hay datos para esta consulta.")

with col2:
    if st.button("💰 Ciudad más cara (Promedio)"):
        cara = df.groupby('city')['price'].mean().idxmax()
        precio = df.groupby('city')['price'].mean().max()
        st.info(f"La ciudad más cara es **{cara}** con un promedio de **${precio:.2f}**")

with col3:
    if st.button("🏠 Tipo de habitación más común"):
        tipo = df['room_type'].value_counts().idxmax()
        st.info(f"El tipo preferido es: **{tipo}**")

# 4. VISUALIZACIÓN DE DATOS
st.markdown("---")
st.header("📈 Gráficos de Tendencias")

tab1, tab2 = st.tabs(["Distribución de Precios", "Mapa de Ubicaciones"])

with tab1:
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(df_filtrado['price'], bins=50, kde=True, color='#ff5a5f', ax=ax)
    plt.title("Distribución de Precios en ciudades seleccionadas")
    st.pyplot(fig)

with tab2:
    st.subheader("Geolocalización de Propiedades")
    # Limpiamos datos para el mapa
    map_df = df_filtrado[['latitude', 'longitude']].dropna().head(2000)
    st.map(map_df)

# 5. TABLA DE DATOS CRUDA
with st.expander("Explorar datos crudos"):
    st.write(df_filtrado.head(100))
