import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import altair as alt
import plotly.express as px
import numpy as np
import pydeck as pdk

# -----------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------
st.set_page_config(page_title="EcoStats: Clima en Movimiento", layout="wide")

# -----------------------------
# FUNCIÓN PARA CARGAR DATOS (¡OPTIMIZADA!)
# -----------------------------

# Diccionario para unificar nombres de columnas
COLUMN_RENAME_MAP = {
    "nombre_estacion": "estacion",
    "lluvia_mm": "precipitacion",
    "temp_ext_media_c": "temperatura",
    "temp_ext_media_C": "temperatura",
    "hum_ext_ult": "humedad",
    "pm_2p5_media_ugm3": "pm2_5",
    "aqi_media_val": "ica",
    "viento_vel_media_kmh": "viento_velocidad",
    "viento_dir_media_grados": "viento_direccion",
    "presion_nivel_mar_hpa": "presion"
}

# Columnas que deben ser numéricas
NUMERIC_COLS = [
    'latitud', 'longitud', 'temperatura', 'humedad', 'precipitacion',
    'pm2_5', 'ica', 'viento_velocidad', 'viento_direccion', 'presion'
]


@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = [col.lower().strip() for col in df.columns]
        df = df.rename(columns=COLUMN_RENAME_MAP)

        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['month'] = df['timestamp'].dt.month
        else:
            st.error("Error: La columna 'timestamp' no se encuentra en los datos.")
            return None

        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'latitud' not in df.columns or 'longitud' not in df.columns:
            st.error("Error: Faltan columnas 'latitud' o 'longitud' en los datos.")
            return None

        return df

    except FileNotFoundError:
        st.error(
            f"Error: No se pudo encontrar el archivo de datos en: {file_path}")
        st.error("Asegúrate de que 'datos_limpios.csv' esté en una carpeta llamada 'data' en el mismo nivel que 'app_streamlit.py'.")
        return None
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None


# --- FUNCIÓN CENTRALIZADA PARA OBTENER DATOS VÁLIDOS ---
def get_valid_data(df_filtered, data_col):
    """Retorna el DataFrame filtrado y sin NaN en la columna de datos."""
    if data_col in df_filtered.columns:
        # Aquí eliminamos los NaN en la columna de interés
        return df_filtered.dropna(subset=[data_col])
    return pd.DataFrame() # Retorna DataFrame vacío si la columna no existe o no hay datos


# --- RUTA RELATIVA PARA TODOS ---
FILE_PATH = 'data/datos_limpios.csv'
df = load_data(FILE_PATH)

# Diccionario para mapear número de mes a nombre (en español)
month_map = {9: "Septiembre", 10: "Octubre", 11: "Noviembre"}

# -----------------------------
# MENÚ PRINCIPAL
# -----------------------------
with st.sidebar:
    st.markdown("## 🌎 EcoStats")
    st.markdown("Clima en Movimiento")
    menu = option_menu(
    menu_title="🌎 EcoStats",
    options=[
        "Inicio",
        "Mapa de Estaciones",
        "Análisis por Estación",
        "Chatbot",
        "Equipo"
    ],
    icons=["house", "map", "play-btn-fill", "bar-chart-line", "chat-dots", "people"],
    menu_icon="cast",
    default_index=0,
    orientation="vertical",
)


# -----------------------------
# SECCIÓN: INICIO (Tus "Datos teóricos")
# -----------------------------
if menu == "Inicio":
    st.markdown("<h1>🌎 <span style='color:#2E8B57 ;'>EcoStats</span></h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        body {
            background-color: #0B1D33;
        }
        .fade-in {
            animation: fadeIn 2s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>

        <h2 style="
            text-align: center;
            color: #2E8B57 ;
            font-size: 32px;
            font-family: 'Trebuchet MS', sans-serif;
            margin-top: 30px;
        ">
            ¿Te gustaría interactuar jugando mediante mapas para entender el clima?
        </h2>
        <p style="
            text-align: center;
            color: #2E8B57  ;
            font-size: 22px;
            font-family: 'Verdana', sans-serif;
            margin-bottom: 10px;
        ">
            Bienvenido a:
        </p>
        <h1 style="
            text-align: center;
            color: #FFFFFF;
            font-size: 90px;
            font-family: 'Trebuchet MS', sans-serif;
            font-weight: 900;
            letter-spacing: 3px;
            margin-top: 0;
        ">
            🌎 <span style="color:#2E8B57 ;">EcoStats</span>
        </h1>
        <h2 style="
            text-align: center;
            color: #2E8B57 ;
            font-size: 50px;
            font-family: 'Trebuchet MS', sans-serif;
            margin-top: -10px;
        ">
            Clima en Movimiento
        </h2>
        <p style="
            text-align: center;
            color: #2E8B57  ;
            font-size: 22px;
            font-family: 'Verdana', sans-serif;
        ">
            Explora, visualiza y comprende los datos ambientales de Santander — una experiencia interactiva con RACiMo.
        </p>
        
        <hr style="border: 1px solid #2E8B57 ; width: 80%; margin:auto; margin-bottom:40px;">
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h2 style='color:#2E8B57; text-align:center; margin-top:40px;'>🌦️ Variables que podrás explorar:</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="variable-card">
            <h3 style="color:#ffffff;">🌡️ Temperatura</h3>
            <p style="color:#C1D1B4  ;">Indica qué tan caliente o frío está el ambiente. Afecta la salud, la agricultura y los ecosistemas.</p>
            <small style="color:#C1D1B4;">Un aumento sostenido puede indicar olas de calor.</small>
        </div>

        <div class="variable-card">
            <h3 style="color:#ffffff;">💧 Humedad Relativa</h3>
            <p style="color:#C1D1B4  ;">Nos dice cuánta agua hay en el aire. Una alta humedad puede hacer que sintamos más calor.</p>
        </div>

        <div class="variable-card">
            <h3 style="color:#ffffff;">🌧️ Precipitación</h3>
            <p style="color:#C1D1B4  ;">Cantidad de lluvia registrada. Es clave para entender sequías, inundaciones y el ciclo del agua.</p>
        </div>

        <style>
        .variable-card {
            background-color:#2E8B57  ;
            padding:30px;
            border-radius:15px;
            margin-bottom:40px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.4);
            transition: transform 0.3s;
            display: inline-block;
            width: 100%;
        }
        .variable-card:hover {
            transform: translateY(-10px);
        }
        </style>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="variable-card">
            <h3 style="color:#ffffff;">🌫️ PM2.5 (Partículas finas)</h3>
            <p style="color:#C1D1B4  ;">Son pequeñas partículas en el aire que pueden afectar la salud respiratoria.</p>
            <small style="color:#C1D1B4;">Se miden en microgramos por metro cúbico (µg/m³).</small>
        </div>

        <div class="variable-card">
            <h3 style="color:#ffffff;">🌈 Índice de Calidad del Aire (ICA)</h3>
            <p style="color:#C1D1B4  ;">Nos muestra qué tan limpio o contaminado está el aire mediante una escala de colores:</p>
            <p style="color:#FFFFFF;">
            🟢 Buena | 🟡 Moderada | 🟠 Regular | 🔴 Mala
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <h3 style="text-align:center; color:#2E8B57 ; font-size:24px;">
        🌍 Entender los datos ambientales nos ayuda a actuar: plantar árboles, reducir la contaminación y adaptarnos al cambio climático.
    </h3>
    <p style="text-align:center; font-size:18px; color:#2E8B57;">
        <b>¡Cada dato cuenta para cuidar nuestro planeta! 🌎</b>
    </p>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.info(
        "Agradecimientos a la Red Ambiental Ciudadana de Monitoreo (RACiMo). [Visita su página aquí](https://class.redclara.net/halley/moncora/intro.html).")


# SECCIÓN: MAPA DE ESTACIONES (usando Kepler.gl publicado en GitHub Pages)
# ----------------------------------------------------------
# SECCIÓN: MAPA DE ESTACIONES

# -----------------------------------------------
# -----------------------------------------------
# SECCIÓN: MAPA DE ESTACIONES (usando Kepler.gl publicado en GitHub Pages)
# -----------------------------------------------
elif menu == "Mapa de Estaciones":
    st.title("Mapa Interactivo de Estaciones")
    st.write("Explora las estaciones activas y observa las 11 estaciones a través del mapa interactivo.")

    # URL pública de tu mapa en GitHub Pages
    kepler_url = "https://orsaki.github.io/Hackaton-CoAfina/"

    # Insertar el mapa en un iframe dentro de Streamlit
    st.components.v1.iframe(kepler_url, height=700, scrolling=True)

    st.info("Este mapa ha sido elaborado con Kepler.gl y publicado en GitHub Pages. "
            "Puedes acercarte, moverte por el mapa y observar cada estación.")

    # ----------------------------------------------------------
    # TABLERO DE ESTACIONES CON ENLACES
    # ----------------------------------------------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #000;'>🌎 ¿Te gustaría conocer los datos en vivo de cada estación?</h2>", unsafe_allow_html=True)

    estaciones = {
        "Barranca - Racimo Orquídea": "https://www.weatherlink.com/bulletin/a802f429-f29b-447f-ba13-a312386571e7",
        "Halley UIS": "https://www.weatherlink.com/bulletin/0ce364bd-acae-4bd0-92d4-f9a998a21a61",
        "RACiMo - Socorro CONS4": "https://www.weatherlink.com/bulletin/1e67f9ec-96da-48be-816c-e56af49b28a0",
        "RACiMo - Barbosa Air2.1": "https://www.weatherlink.com/bulletin/88abfff2-2f29-423a-978d-62514f799ff3",
        "RACiMo - Barbosa CONS2": "https://www.weatherlink.com/bulletin/6d53fbb4-321a-4e4c-91f8-2384ddd5ea2d",
        "RACiMo - Bucaramanga San AIR5": "https://www.weatherlink.com/bulletin/930ccf8f-d05f-4dd4-be28-d50d99078065",
        "RACiMo - Málaga AIR3.1": "https://www.weatherlink.com/bulletin/9e3826b4-1dfc-437b-b37f-bc09e5cf6e9b",
        "RACiMo - Málaga CONS3": "https://www.weatherlink.com/bulletin/cd65618a-540a-4b4b-858d-8df2ab30406c",
        "RACiMo - Socorro Conv AIR4.1": "https://www.weatherlink.com/bulletin/e024efe8-b546-4f05-b3b8-04ffef19e8d8"
    }

    # Crear diseño en dos columnas
    col1, col2 = st.columns(2)
    estaciones_items = list(estaciones.items())

    # Mostrar 2 por fila
    for i in range(0, len(estaciones_items), 2):
        with col1:
            if i < len(estaciones_items):
                nombre, url = estaciones_items[i]
                st.markdown(
                    f"""
                    <div style="background-color:#F5F7F2; color:black; border-radius:12px; padding:15px; 
                                margin-bottom:10px; text-align:center; font-size:18px;">
                        <b>{nombre}</b><br>
                        Consulta sus datos en tiempo real dando clic 
                        <a href="{url}" target="_blank" style="font-weight:bold; color:#007b55;">aquí</a>.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col2:
            if i + 1 < len(estaciones_items):
                nombre, url = estaciones_items[i + 1]
                st.markdown(
                    f"""
                    <div style="background-color:#F5F7F2; color:black; border-radius:12px; padding:15px; 
                                margin-bottom:10px; text-align:center; font-size:18px;">
                        <b>{nombre}</b><br>
                        Consulta sus datos en tiempo real dando clic 
                        <a href="{url}" target="_blank" style="font-weight:bold; color:#007b55;">aquí</a>.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ----------------------------------------------------------
    

    # ----------------------------------------------------------
    st.markdown("""
    <div style='text-align: center; background-color: white; color: black; padding: 25px; border-radius: 12px; width: 100%;'>
        <h3 style='text-align: center; font-weight: bold;'>Sobre los tipos de estaciones y sus mediciones</h3>
        <p style='font-size: 17px; margin: 0 auto; max-width: 900px; line-height: 1.5;'>
        Dentro de la red RACiMo contamos con diferentes tipos de estaciones, cada una diseñada para registrar información específica sobre el ambiente. 
        Las estaciones <b>Airlink (AIR)</b> registran la temperatura, la humedad y los niveles de material particulado (PM2.5). 
        Las estaciones <b>Vantage Vue (VUE)</b> miden temperatura, humedad, presión atmosférica, velocidad y dirección del viento, y además cada una está conectada con una estación Airlink. 
        Por último, la <b>Vantage Pro2</b> ofrece un monitoreo meteorológico más completo, con mediciones de viento y presión de alta precisión. 
        A continuación puedes ver qué variables se encuentran disponibles para cada estación en la siguiente tabla.
        </p>
    </div>
    """, unsafe_allow_html=True)


    # ----------------------------------------------------------
    # TABLA DE VARIABLES POR ESTACIÓN
    # ----------------------------------------------------------
    st.markdown("""
    <style>
        .tabla-estaciones {
            background-color: #F5F7F2;
            width: 100%;
            border-collapse: collapse;
            text-align: center;
            margin-top: 20px;
            border-radius: 12px;
            overflow: hidden;
        }
        .tabla-estaciones th, .tabla-estaciones td {
            padding: 10px;
            border-bottom: 1px solid #ccc;
            color: black;
            font-size: 16px;
        }
        .tabla-estaciones th {
            font-weight: bold;
            background-color: #E7F2E5;
        }
        .tabla-estaciones tr:hover {
            background-color: #e9f0eb;
        }
    </style>

    <table class='tabla-estaciones'>
        <tr>
            <th>Estación</th>
            <th>PM2.5</th>
            <th>Temperatura</th>
            <th>Precipitación</th>
            <th>Humedad</th>
            <th>Velocidad del Viento</th>
            <th>Dirección del Viento</th>
            <th>Presión Barométrica</th>
        </tr>
        <tr><td>Barranca – Racimo Orquídea (AIR)</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
        <tr><td>Halley UIS (VUE)</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
        <tr><td>RACiMo – Socorro CONS4 (VUE)</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
        <tr><td>RACiMo – Barbosa Air2.1 (AIR)</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
        <tr><td>RACiMo – Barbosa CONS2 (VUE)</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
        <tr><td>RACiMo – Bucaramanga San AIR5 (AIR)</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
        <tr><td>RACiMo – Bucaramanga Guatiguará AIR5.1 (AIR)</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
        <tr><td>RACiMo – Málaga AIR3.1 (AIR)</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
        <tr><td>RACiMo – Málaga CONS3 (VUE)</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
        <tr><td>RACiMo – Socorro Conv AIR4.1 (AIR)</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
        <tr><td>RACiMo – Barranca AIR1.1 (AIR)</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    </table>
    """, unsafe_allow_html=True)





# -----------------------------------------------
# SECCIÓN: ANÁLISIS POR ESTACIÓN
# -----------------------------------------------
elif menu == "Análisis por Estación":
    st.title("Análisis Detallado por Estación")
    st.write(
        "Explora gráficos estáticos y detallados para una estación y variable específica.")

    if df is not None:

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            variable_map = {
                "PM2.5 (µg/m³)": "pm2_5",
                "Temperatura (°C)": "temperatura",
                "Precipitación (mm)": "precipitacion",
                "Humedad (%)": "humedad",
                "Velocidad Viento (km/h)": "viento_velocidad",
                "Dirección Viento (Rosa)": "viento_direccion",
                "Presión Barométrica (hPa)": "presion"
            }
            variable_choice_label = st.selectbox(
                label="Selecciona la Variable:",
                options=list(variable_map.keys()),
                index=0
            )
            data_col = variable_map[variable_choice_label]

        with col2:
            station_list = df['estacion'].dropna().unique().tolist()
            selected_station = st.selectbox(
                label="Selecciona la Estación:",
                options=sorted(station_list),
                index=0
            )

        with col3:
            month_list = sorted(
                [m for m in df['month'].unique() if m in month_map])
            selected_month_num = st.radio(
                label="Selecciona el Mes:",
                options=month_list,
                format_func=lambda x: month_map.get(x, "Mes desconocido"),
                horizontal=True,
                index=0
            )

        st.markdown("---")

        df_filtered = df[
            (df['estacion'] == selected_station) &
            (df['month'] == selected_month_num)
        ]
        
        # --- Obtener datos válidos para la métrica ---
        # df_filtered_valid contendrá los datos limpios de NaN para la columna actual.
        df_filtered_valid = get_valid_data(df_filtered, data_col)
        
        # --- Chequeo de datos ---
        if df_filtered_valid.empty:
            st.warning(f"No hay datos de {data_col} para '{selected_station}' en {month_map.get(selected_month_num, '')}.")
        
        else:
            # ==========================================================
            # GRÁFICO 1: PM2.5 (Adaptado a 'pm2_5')
            # ==========================================================
            if data_col == "pm2_5":
                
                # --- Métricas con iconos ---
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Máximo (µg/m³)", f"{df_filtered_valid[data_col].max():.2f}")
                stat_col2.metric("📉 Mínimo (µg/m³)", f"{df_filtered_valid[data_col].min():.2f}")
                stat_col3.metric("📊 Medio (µg/m³)", f"{df_filtered_valid[data_col].mean():.2f}")
                st.markdown("---")

                line_chart = alt.Chart(df_filtered_valid).mark_line(point=True, opacity=0.8).encode(
                    x=alt.X('timestamp:T', title='Fecha y Hora', axis=alt.Axis(tickCount=10)),
                    y=alt.Y(f'{data_col}:Q', title='PM2.5 (µg/m³)', scale=alt.Scale(zero=False)),
                    tooltip=['timestamp:T', f'{data_col}:Q', 'estacion']
                )
                rule_df = pd.DataFrame({'limite_perjudicial': [56]})
                rule = alt.Chart(rule_df).mark_rule(color='red', strokeWidth=2, strokeDash=[5, 5]).encode(y='limite_perjudicial:Q')
                text = alt.Chart(rule_df).mark_text(align='left', baseline='bottom', dx=5, dy=-5, color='red', fontSize=12).encode(y='limite_perjudicial:Q', text=alt.value('Límite Perjudicial (56 µg/m³)'))
                
                final_chart_pm25 = alt.layer(line_chart, rule, text).properties(
                    title=f'PM2.5 para: {selected_station} ({month_map.get(selected_month_num, "")})'
                ).interactive()
                st.altair_chart(final_chart_pm25, use_container_width=True)

            # ==========================================================
            # GRÁFICO 2: TEMPERATURA (Adaptado a 'temperatura')
            # ==========================================================
            elif data_col == "temperatura":
                
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Máxima (°C)", f"{df_filtered_valid[data_col].max():.2f}")
                stat_col2.metric("📉 Mínima (°C)", f"{df_filtered_valid[data_col].min():.2f}")
                stat_col3.metric("📊 Media (°C)", f"{df_filtered_valid[data_col].mean():.2f}")
                st.markdown("---")

                colorscale = [[0.0, "rgb(0, 68, 204)"], [0.33, "rgb(102, 204, 255)"], [0.66, "rgb(255, 255, 102)"], [1.0, "rgb(255, 51, 51)"]]
                fig_temp = px.scatter(
                    df_filtered_valid, x="timestamp", y=data_col, color=data_col,
                    color_continuous_scale=colorscale, labels={data_col: "Temperatura (°C)", "timestamp": "Tiempo"},
                )
                fig_temp.add_scatter(x=df_filtered_valid["timestamp"], y=df_filtered_valid[data_col], mode="lines", line=dict(
                    color="rgba(100,100,100,0.3)", width=2), name="Tendencia")
                fig_temp.update_layout(
                    title=dict(text=f"Temperatura - {selected_station} ({month_map.get(selected_month_num, "")})", x=0.5),
                    xaxis_title="Tiempo", yaxis_title="Temperatura (°C)", coloraxis_colorbar=dict(title="°C"),
                    plot_bgcolor="rgba(245,245,245,1)", paper_bgcolor="rgba(245,245,245,1)",
                )
                fig_temp.update_traces(hovertemplate="Fecha: %{x}<br>Temperatura: %{y:.2f} °C<extra></extra>")
                st.plotly_chart(fig_temp, use_container_width=True)


            # ==========================================================
            # GRÁFICO 3: PRECIPITACIÓN (Adaptado a 'precipitacion')
            # ==========================================================
            elif data_col == "precipitacion":
                
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("🌧️ Máxima (en 15min)", f"{df_filtered_valid[data_col].max():.2f} mm")
                stat_col2.metric("💧 Total Acumulada", f"{df_filtered_valid[data_col].sum():.2f} mm")
                stat_col3.metric("📊 Media (por registro)", f"{df_filtered_valid[data_col].mean():.2f} mm")
                st.markdown("---")

                fig_precip = px.area(
                    df_filtered_valid, x="timestamp", y=data_col,
                    title=f"Precipitación - {selected_station} ({month_map.get(selected_month_num, "")})",
                    color_discrete_sequence=["#0077cc"],
                )
                fig_precip.update_traces(line_color="#0055aa", fillcolor="rgba(0,119,204,0.3)")
                fig_precip.update_layout(
                    template="plotly_white", xaxis_title="Fecha", yaxis_title="Precipitación (mm)",
                    title_x=0.5, hovermode="x unified",
                )
                st.plotly_chart(fig_precip, use_container_width=True)

            # ==========================================================
            # GRÁFICO 4: HEATMAP DE HUMEDAD (Adaptado a 'humedad')
            # ==========================================================
            elif data_col == "humedad":
                
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Humedad Máxima (%)", f"{df_filtered_valid[data_col].max():.2f}")
                stat_col2.metric("📉 Humedad Mínima (%)", f"{df_filtered_valid[data_col].min():.2f}")
                stat_col3.metric("📊 Humedad Media (%)", f"{df_filtered_valid[data_col].mean():.2f}")
                st.markdown("---")

                heatmap = alt.Chart(df_filtered_valid).mark_rect().encode(
                    x=alt.X('date(timestamp):O', title=f"Día de {month_map.get(selected_month_num, '')}"),
                    y=alt.Y('hours(timestamp):O', title='Hora del Día'),
                    color=alt.Color(f'mean({data_col}):Q', title='Humedad Promedio (%)', scale=alt.Scale(
                        scheme='tealblues')),
                    tooltip=['timestamp:T', f'mean({data_col}):Q', 'estacion']
                ).properties(
                    title=f'Mapa de Calor de Humedad - {selected_station} ({month_map.get(selected_month_num, "")})'
                ).interactive()
                st.altair_chart(heatmap, use_container_width=True)

            # ==========================================================
            # GRÁFICO 5: VELOCIDAD VIENTO (Adaptado a 'viento_velocidad')
            # ==========================================================
            elif data_col == "viento_velocidad":
                
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("💨 Máxima (km/h)", f"{df_filtered_valid[data_col].max():.2f}")
                stat_col2.metric("🍃 Mínima (km/h)", f"{df_filtered_valid[data_col].min():.2f}")
                stat_col3.metric("📊 Media (km/h)", f"{df_filtered_valid[data_col].mean():.2f}")
                st.markdown("---")

                fig_wind_speed = px.line(
                    df_filtered_valid, x="timestamp", y=data_col,
                    title=f"Velocidad del Viento - {selected_station} ({month_map.get(selected_month_num, "")})",
                    color_discrete_sequence=["#2ca02c"]
                )
                fig_wind_speed.update_layout(
                    template="plotly_white", xaxis_title="Fecha", yaxis_title="Velocidad Viento (km/h)",
                    title_x=0.5, hovermode="x unified",
                )
                st.plotly_chart(fig_wind_speed, use_container_width=True)

            # ==========================================================
            # GRÁFICO 6: PRESIÓN (Adaptado a 'presion')
            # ==========================================================
            elif data_col == "presion":
                
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Máxima (hPa)", f"{df_filtered_valid[data_col].max():.2f}")
                stat_col2.metric("📉 Mínima (hPa)", f"{df_filtered_valid[data_col].min():.2f}")
                stat_col3.metric("📊 Media (hPa)", f"{df_filtered_valid[data_col].mean():.2f}")
                st.markdown("---")

                fig_pressure = px.line(
                    df_filtered_valid, x="timestamp", y=data_col,
                    title=f"Presión Barométrica - {selected_station} ({month_map.get(selected_month_num, "")})",
                    color_discrete_sequence=["#9467bd"]
                )
                fig_pressure.update_layout(
                    template="plotly_white", xaxis_title="Fecha", yaxis_title="Presión (hPa)",
                    title_x=0.5, hovermode="x unified",
                )
                st.plotly_chart(fig_pressure, use_container_width=True)

            # ==========================================================
            # GRÁFICO 7: ROSA DE VIENTOS (Adaptado)
            # ==========================================================
            elif data_col == "viento_direccion":
                
                # Para la Rosa de Vientos, necesitamos ambas columnas limpias
                dff_wind = df_filtered_valid.dropna(subset=['viento_direccion', 'viento_velocidad'])
                
                if not dff_wind.empty:
                    st.info("La Rosa de Vientos muestra la frecuencia de la dirección (de dónde viene el viento) y su intensidad.")

                    bins = [-0.1, 22.5, 67.5, 112.5, 157.5,
                            202.5, 247.5, 292.5, 337.5, 360]
                    labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
                    dff_wind_binned = dff_wind.copy()

                    dff_wind_binned['Dirección'] = pd.cut(
                        dff_wind_binned['viento_direccion'], bins=bins, labels=labels, right=True, ordered=False)

                    speed_bins = [0, 5, 10, 15, 20, float('inf')]
                    speed_labels = ['0-5 km/h', '5-10 km/h',
                                    '10-15 km/h', '15-20 km/h', '>20 km/h']
                    dff_wind_binned['Velocidad (km/h)'] = pd.cut(
                        dff_wind_binned['viento_velocidad'], bins=speed_bins, labels=speed_labels, right=False)

                    wind_rose_data = dff_wind_binned.groupby(
                        ['Dirección', 'Velocidad (km/h)']).size().reset_index(name='Frecuencia')

                    try:
                        fig_wind_rose = px.bar_polar(
                            wind_rose_data, r="Frecuencia", theta="Dirección", color="Velocidad (km/h)",
                            template="plotly_white",
                            title=f"Rosa de Vientos - {selected_station} ({month_map.get(selected_month_num, "")})",
                            color_discrete_sequence=px.colors.sequential.YlOrRd,
                            category_orders={"Dirección": ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']}
                        )
                        st.plotly_chart(fig_wind_rose, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error al generar la Rosa de Vientos: {e}.")
                else:
                    st.warning(
                        f"No hay datos suficientes de Viento para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

    else:
        st.warning(
            "No se pudieron cargar los datos. Verifica que 'datos_limpios.csv' esté en el mismo directorio.")

# -----------------------------------------------
# SECCIÓN: CHATBOT (¡CON LÓGICA CONTEXTUAL Y CORRECTA!)
# -----------------------------------------------
elif menu == "Chatbot":
    
    # --- DATOS DE ESTADÍSTICAS GLOBALES PARA EL CHATBOT ---
    # (Asegúrate de que este diccionario esté definido en la parte superior de tu script)
    STATION_STATS_DATA = {
        "Barranca-RacimoOrquidea": {
            "latitud": 7.068842, "longitud": -73.85138,
            "stats": {
                "temperatura": {"max": 36.67, "min": 17.44, "mean": 27.87, "unit": "°C"},
                "humedad": {"max": 95.40, "min": 45.30, "mean": 77.54, "unit": "%"},
                "precipitacion": {"max": 30.60, "sum": 655.60, "mean": 0.12, "unit": "mm"},
                "pm2_5": {"max": 54.47, "min": 0.00, "mean": 9.13, "unit": "µg/m³"},
                "ica": {"max": 128.49, "min": 0.00, "mean": 28.25, "unit": ""},
                "viento_velocidad": {"max": 16.35, "min": 0.00, "mean": 3.38, "unit": "km/h"},
                "presion": {"max": 1019.57, "min": 1003.62, "mean": 1010.60, "unit": "hPa"}
            }
        },
        "Halley UIS": {
            "latitud": 7.13908, "longitud": -73.12137,
            "stats": {
                "temperatura": {"max": 31.17, "min": 22.28, "mean": 26.72, "unit": "°C"},
                "humedad": {"max": 96.00, "min": 45.00, "mean": 79.36, "unit": "%"},
                "precipitacion": {"max": 0.80, "sum": 108.60, "mean": 0.02, "unit": "mm"},
                "pm2_5": {"max": 2.43, "min": 1.45, "mean": 1.94, "unit": "µg/m³"},
                "ica": {"max": 7.89, "min": 4.71, "mean": 6.30, "unit": ""},
                "viento_velocidad": {"max": 16.09, "min": 0.00, "mean": 1.96, "unit": "km/h"},
                "presion": {"max": 1016.49, "min": 1003.42, "mean": 1011.17, "unit": "hPa"}
            }
        },
        "RACIMO-SOCORROCONS4": {
            "latitud": 6.461252, "longitud": -73.25759,
            "stats": {
                "temperatura": {"max": 30.78, "min": 15.72, "mean": 21.59, "unit": "°C"},
                "humedad": {"max": 96.70, "min": 36.50, "mean": 81.04, "unit": "%"},
                "precipitacion": {"max": 12.00, "sum": 281.20, "mean": 0.05, "unit": "mm"},
                "pm2_5": {"max": 322.42, "min": 0.00, "mean": 2.56, "unit": "µg/m³"},
                "ica": {"max": 372.27, "min": 0.00, "mean": 8.16, "unit": ""},
                "viento_velocidad": {"max": 11.59, "min": 0.00, "mean": 3.23, "unit": "km/h"},
                "presion": {"max": 1023.03, "min": 1009.52, "mean": 1017.49, "unit": "hPa"}
            }
        },
        "RACiMo BarbosaAir2.1": {
            "latitud": 5.92901, "longitud": -73.61547,
            "stats": {
                "temperatura": {"max": 31.78, "min": 15.89, "mean": 23.94, "unit": "°C"},
                "humedad": {"max": 82.00, "min": 29.20, "mean": 61.88, "unit": "%"},
                "precipitacion": {"max": 0.00, "sum": 0.00, "mean": 0.00, "unit": "mm"},
                "pm2_5": {"max": 305.55, "min": 0.00, "mean": 13.21, "unit": "µg/m³"},
                "ica": {"max": 355.56, "min": 0.00, "mean": 36.33, "unit": ""},
                "viento_velocidad": {"max": 6.47, "min": 0.08, "mean": 3.28, "unit": "km/h"},
                "presion": {"max": 1049.99, "min": 1016.28, "mean": 1035.37, "unit": "hPa"}
            }
        },
        "RACiMo BarbosaCONS2": {
            "latitud": 5.949394, "longitud": -73.60563,
            "stats": {
                "temperatura": {"max": 30.06, "min": 12.72, "mean": 20.07, "unit": "°C"},
                "humedad": {"max": 97.30, "min": 31.60, "mean": 80.28, "unit": "%"},
                "precipitacion": {"max": 9.80, "sum": 385.80, "mean": 0.06, "unit": "mm"},
                "pm2_5": {"max": 349.67, "min": 0.00, "mean": 5.68, "unit": "µg/m³"},
                "ica": {"max": 451.16, "min": 0.00, "mean": 16.43, "unit": ""},
                "viento_velocidad": {"max": 17.14, "min": 0.00, "mean": 2.81, "unit": "km/h"},
                "presion": {"max": 1025.26, "min": 1013.48, "mean": 1020.40, "unit": "hPa"}
            }
        },
        "RACiMo BarrancaAIR1.1": {
            "latitud": 7.077814, "longitud": -73.85829,
            "stats": {
                "temperatura": {"max": 38.28, "min": 23.50, "mean": 30.36, "unit": "°C"},
                "humedad": {"max": 96.50, "min": 42.30, "mean": 67.35, "unit": "%"},
                "precipitacion": {"max": 0.00, "sum": 0.00, "mean": 0.00, "unit": "mm"},
                "pm2_5": {"max": 357.39, "min": 0.00, "mean": 11.30, "unit": "µg/m³"},
                "ica": {"max": 402.05, "min": 0.00, "mean": 33.47, "unit": ""},
                "viento_velocidad": {"max": 8.59, "min": 7.64, "mean": 8.12, "unit": "km/h"},
                "presion": {"max": 1024.30, "min": 1018.46, "mean": 1021.38, "unit": "hPa"}
            }
        },
        "RACiMo BucGuatiAIR5.1": {
            "latitud": 6.994449, "longitud": -73.066086,
            "stats": {
                "temperatura": {"max": 28.11, "min": 19.00, "mean": 23.43, "unit": "°C"},
                "humedad": {"max": 92.80, "min": 52.00, "mean": 76.98, "unit": "%"},
                "precipitacion": {"max": 0.00, "sum": 0.00, "mean": 0.00, "unit": "mm"},
                "pm2_5": {"max": 128.50, "min": 0.00, "mean": 6.33, "unit": "µg/m³"},
                "ica": {"max": 187.36, "min": 0.00, "mean": 20.12, "unit": ""},
                "viento_velocidad": {"max": 7.64, "min": 5.48, "mean": 6.56, "unit": "km/h"},
                "presion": {"max": 1037.62, "min": 1024.30, "mean": 1030.96, "unit": "hPa"}
            }
        },
        "RACiMo BucSanAIR5": {
            "latitud": 7.1386485, "longitud": -73.122185,
            "stats": {
                "temperatura": {"max": 29.22, "min": 21.94, "mean": 25.38, "unit": "°C"},
                "humedad": {"max": 82.30, "min": 44.90, "mean": 68.68, "unit": "%"},
                "precipitacion": {"max": 0.00, "sum": 0.00, "mean": 0.00, "unit": "mm"},
                "pm2_5": {"max": 62.34, "min": 0.00, "mean": 7.29, "unit": "µg/m³"},
                "ica": {"max": 143.97, "min": 0.00, "mean": 22.85, "unit": ""},
                "viento_velocidad": {"max": 5.48, "min": 2.48, "mean": 3.98, "unit": "km/h"},
                "presion": {"max": 1049.99, "min": 1037.63, "mean": 1044.82, "unit": "hPa"}
            }
        },
        "RACiMo MalagaAIR3.1": {
            "latitud": 6.698055, "longitud": -72.73542,
            "stats": {
                "temperatura": {"max": 26.89, "min": 11.83, "mean": 18.89, "unit": "°C"},
                "humedad": {"max": 100.00, "min": 33.20, "mean": 70.16, "unit": "%"},
                "precipitacion": {"max": 0.00, "sum": 0.00, "mean": 0.00, "unit": "mm"},
                "pm2_5": {"max": 24.54, "min": 0.00, "mean": 2.69, "unit": "µg/m³"},
                "ica": {"max": 68.79, "min": 0.00, "mean": 8.74, "unit": ""},
                "viento_velocidad": {"max": 2.48, "min": 0.00, "mean": 1.24, "unit": "km/h"},
                "presion": {"max": 1043.76, "min": 1028.01, "mean": 1035.88, "unit": "hPa"}
            }
        },
        "RACiMo MalagaCONS3": {
            "latitud": 6.700839, "longitud": -72.727615,
            "stats": {
                "temperatura": {"max": 28.44, "min": 12.17, "mean": 18.07, "unit": "°C"},
                "humedad": {"max": 96.60, "min": 31.30, "mean": 75.70, "unit": "%"},
                "precipitacion": {"max": 18.40, "sum": 366.40, "mean": 0.07, "unit": "mm"},
                "pm2_5": {"max": 58.24, "min": 0.00, "mean": 2.83, "unit": "µg/m³"},
                "ica": {"max": 135.91, "min": 0.00, "mean": 9.13, "unit": ""},
                "viento_velocidad": {"max": 13.45, "min": 0.00, "mean": 1.74, "unit": "km/h"},
                "presion": {"max": 1029.67, "min": 1019.24, "mean": 1024.87, "unit": "hPa"}
            }
        },
        "RACiMo SocConvAir4.1": {
            "latitud": 6.4681354, "longitud": -73.25675,
            "stats": {
                "temperatura": {"max": 30.50, "min": 19.39, "mean": 24.50, "unit": "°C"},
                "humedad": {"max": 83.70, "min": 34.70, "mean": 66.62, "unit": "%"},
                "precipitacion": {"max": 0.00, "sum": 0.00, "mean": 0.00, "unit": "mm"},
                "pm2_5": {"max": 82.66, "min": 0.00, "mean": 4.53, "unit": "µg/m³"},
                "ica": {"max": 160.90, "min": 0.00, "mean": 14.34, "unit": ""},
                "viento_velocidad": {"max": 5.66, "min": 5.66, "mean": 5.66, "unit": "km/h"},
                "presion": {"max": 1023.43, "min": 1023.43, "mean": 1023.43, "unit": "hPa"}
            }
        }
    }
    
    # --- LÓGICA DE CHATBOT MEJORADA ---
    
    # 1. Mapas de conocimiento del Bot
    
    # Aseguramos que la lista esté ordenada para que los números coincidan
    unique_stations = sorted(list(STATION_STATS_DATA.keys()))
    station_count = len(unique_stations)
    
    # Mapa de Índice de Estaciones (Número -> Nombre)
    station_index_map = {index + 1: station for index, station in enumerate(unique_stations)}
    numbered_list_str_stations = "\n".join([f"{i}. {station}" for i, station in station_index_map.items()])
    
    # Mapeo de palabras (números) a índice de Estación
    number_word_map_stations = {
        'primera': 1, '1ra': 1, '1': 1,
        'segunda': 2, '2da': 2, '2': 2,
        'tercera': 3, '3ra': 3, '3': 3,
        'cuarta': 4, '4ta': 4, '4': 4,
        'quinta': 5, '5ta': 5, '5': 5,
        'sexta': 6, '6ta': 6, '6': 6,
        'séptima': 7, 'septima': 7, '7ma': 7, '7': 7,
        'octava': 8, '8va': 8, '8': 8,
        'novena': 9, '9na': 9, '9': 9,
        'décima': 10, 'decima': 10, '10ma': 10, '10': 10,
        'onceava': 11, '11va': 11, '11': 11
    }

    # Mapa de Definiciones de Variables
    VARIABLE_DESCRIPTIONS = {
        "pm2_5": "**PM2.5 (µg/m³)**: Son las partículas contaminantes más peligrosas. El gráfico en 'Análisis por Estación' muestra una línea roja en **56 µg/m³**, que es el límite de riesgo.",
        "temperatura": "**Temperatura (°C)**: Es el grado de calor. El gráfico en 'Análisis por Estación' usa puntos de colores (azul a rojo) para identificar fácilmente picos de calor o frío.",
        "precipitacion": "**Precipitación (mm)**: Es la cantidad de lluvia. En 'Análisis por Estación', las métricas clave son la **Máxima** (cuánto llovió en 15 min) y la **Total Acumulada** en el mes.",
        "humedad": "**Humedad (%)**: Afecta la sensación térmica. El gráfico de 'Humedad (Mapa de Calor)' en 'Análisis por Estación' es ideal para ver patrones (ej. '¿A qué hora del día es más húmedo?').",
        "viento_velocidad": "**Velocidad Viento (km/h)**: Un gráfico de línea que muestra las ráfagas. Lo encuentras en 'Análisis por Estación'.",
        "viento_direccion": "**Dirección Viento (Rosa)**: Un gráfico polar que muestra la dirección *predominante* (de dónde viene el viento). Lo encuentras en 'Análisis por Estación'.",
        "presion": "**Presión Barométrica (hPa)**: Una presión baja generalmente indica mal tiempo (tormentas); una presión alta indica buen tiempo estable.",
        "ica": "**ICA (Índice de Calidad del Aire)**: Es un indicador que te dice qué tan limpio está el aire. El gráfico en 'Análisis por Estación' muestra bandas de colores (🟢, 🟡, 🟠, 🔴) para que veas el nivel de riesgo."
    }
    
    # Mapa de Índice de Variables (Número -> Clave)
    VARIABLE_INDEX_MAP = {
        1: "pm2_5",
        2: "temperatura",
        3: "precipitacion",
        4: "humedad",
        5: "viento_velocidad",
        6: "viento_direccion",
        7: "presion",
        8: "ica"
    }

    # Lista enumerada de variables para mostrar al usuario
    numbered_list_str_vars = "\n".join([f"{i}. {VARIABLE_DESCRIPTIONS[key].split(':')[0]}" for i, key in VARIABLE_INDEX_MAP.items()])

    # Mapeo de palabras clave (prompt) a clave de variable
    VAR_MAP_QUERY = {
        'pm2.5': 'pm2_5', 'partículas': 'pm2_5', 'contaminación': 'pm2_5',
        'temperatura': 'temperatura', 'temp': 'temperatura', 'calor': 'temperatura',
        'humedad': 'humedad',
        'precipitación': 'precipitacion', 'lluvia': 'precipitacion',
        'viento': 'viento_velocidad', 'velocidad': 'viento_velocidad',
        'dirección': 'viento_direccion', 'direccion': 'viento_direccion', 'rosa': 'viento_direccion',
        'presión': 'presion', 'presion': 'presion',
        'ica': 'ica', 'calidad del aire': 'ica'
    }
    
    # Mapeo de palabras (números) a índice de Variable
    number_word_map_vars = {
        'primera': 1, '1ra': 1, '1': 1,
        'segunda': 2, '2da': 2, '2': 2,
        'tercera': 3, '3ra': 3, '3': 3,
        'cuarta': 4, '4ta': 4, '4': 4,
        'quinta': 5, '5ta': 5, '5': 5,
        'sexta': 6, '6ta': 6, '6': 6,
        'séptima': 7, 'septima': 7, '7ma': 7, '7': 7,
        'octava': 8, '8va': 8, '8': 8
    }

    # Mapeo de variables amigables para el Chatbot
    variable_friendly_map = {
        "temperatura": "Temperatura", "humedad": "Humedad Relativa", "precipitacion": "Precipitación",
        "pm2_5": "PM2.5", "viento_velocidad": "Velocidad del Viento", "presion": "Presión Barométrica",
        "ica": "Índice de Calidad del Aire (ICA)"
    }
    
    # -----------------------------------------------------

    st.title("Asistente Virtual EcoStats 🤖")
    
    # Inicializar el historial del chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant",
             "content": "👋 ¡Hola! Soy **EcoBot**, tu guía en *EcoStats*. ¿Cómo puedo ayudarte a entender los gráficos?"}
        ]

    # Mostrar historial
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("Escribe tu pregunta aquí... (ej. 'temperatura máxima de Halley UIS')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        prompt_lower = prompt.lower()
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta del asistente
        with st.chat_message("assistant"):
            response = ""

            # --- DICCIONARIOS DE MAPPING PARA CONSULTAS ---
            stat_keywords = {'máxima': 'max', 'maxima': 'max', 'mínima': 'min', 'minima': 'min', 'media': 'mean', 'promedio': 'mean', 'total': 'sum', 'sumatoria': 'sum'}
            
            found_stat_key = None
            found_var_key = None
            found_station = None
            
            # 1. Identificar la estadística, variable y estación
            
            # Intento 1: Identificar Estación por Nombre
            for station_name in unique_stations:
                if station_name.lower() in prompt_lower:
                    found_station = station_name
                    break
            
            # Intento 2: Identificar Estación por Número (SI LA PALABRA "estación" ESTÁ)
            if not found_station and ("estación" in prompt_lower or "estacion" in prompt_lower):
                for word in prompt_lower.split():
                    if word in number_word_map_stations:
                        index = number_word_map_stations[word]
                        if index in station_index_map:
                            found_station = station_index_map[index]
                            break

            # Intento 3: Identificar Variable por Nombre
            for keyword, var_name in VAR_MAP_QUERY.items():
                if keyword in prompt_lower:
                    found_var_key = var_name
                    break
            
            # Intento 4: Identificar Variable por Número (SI LA PALABRA "variable" ESTÁ)
            if not found_var_key and "variable" in prompt_lower:
                for word in prompt_lower.split():
                    if word in number_word_map_vars:
                        index = number_word_map_vars[word]
                        if index in VARIABLE_INDEX_MAP:
                            found_var_key = VARIABLE_INDEX_MAP[index]
                            break

            # Intento 5: Identificar Estadística
            for keyword, stat_name in stat_keywords.items():
                if keyword in prompt_lower:
                    found_stat_key = stat_name.lower()
                    break
            
            # -------------------------------------------------------------------
            # --- LÓGICA DE RESPUESTAS (Prioridad Inversa) ---
            # -------------------------------------------------------------------
            
            # 1. Saludos y Despedidas
            if "adios" in prompt_lower or "chao" in prompt_lower or "hasta luego" in prompt_lower:
                response = "¡Hasta pronto! Que tengas un excelente día. Vuelve cuando quieras explorar más datos. 👋"
            
            elif "hola" in prompt_lower or "saludos" in prompt_lower or "buenos dias" in prompt_lower:
                response = "¡Hola! Soy EcoBot. Es un placer saludarte. ¿Qué te gustaría que te explique sobre el dashboard o los datos de RACiMo?"

            # 2. Lista de Variables
            elif "cuales son las variables" in prompt_lower or "dime las variables" in prompt_lower or "lista de variables" in prompt_lower:
                response = f"Analizamos 8 variables principales. Puedes preguntarme por ellas (ej. '¿qué es la variable 1?' o '¿qué es PM2.5?'):\n\n{numbered_list_str_vars}"

            # 3. Lista de Estaciones
            elif "cuantas estaciones" in prompt_lower or "cuales son las estaciones" in prompt_lower or "lista de estaciones" in prompt_lower or "dime las estaciones" in prompt_lower:
                response = f"Actualmente monitoreamos **{station_count} estaciones**:\n\n{numbered_list_str_stations}\n\nPuedes preguntarme por el nombre o el número (ej. 'dame las estadísticas de la estación 1')."

            # 4. Ubicación General
            elif "ubicacion" in prompt_lower or "donde estan" in prompt_lower or "zona de estudio" in prompt_lower:
                response = "Nuestra zona de estudio principal es el departamento de **Santander, Colombia**. Puedes ver los puntos exactos en la sección **'Mapa de Estaciones'**."
            
            # 5. Navegación
            elif "mapa" in prompt_lower and "animado" not in prompt_lower:
                response = "Puedes ver la ubicación de todas las estaciones en la sección **'Mapa de Estaciones'** en el menú de la izquierda."
            elif "animación" in prompt_lower or "evolución" in prompt_lower:
                response = "La sección **'Animación de Datos'** te permite seleccionar una variable y ver cómo cambian los niveles en todas las estaciones con el tiempo, como un *time-lapse*."
            elif "análisis" in prompt_lower or "gráfico" in prompt_lower or "sección" in prompt_lower:
                response = (
                    "La sección **'Análisis por Estación'** es para ver gráficos detallados. "
                    "Recuerda que tienes **tres filtros** arriba (Variable, Estación y Mes) para refinar tu vista."
                )
            
            # 6. Estadística Específica (La consulta más compleja)
            elif found_stat_key and found_var_key and found_station:
                station_data = STATION_STATS_DATA[found_station]['stats']
                
                if found_var_key == 'precipitacion' and found_stat_key == 'sum':
                    json_key = 'sum'; stat_name_es = 'Total Acumulada'
                elif found_var_key == 'precipitacion' and found_stat_key == 'max':
                    json_key = 'max'; stat_name_es = 'Máxima (15min)'
                else:
                    json_key = found_stat_key; stat_name_es = found_stat_key.capitalize()

                try:
                    value = station_data[found_var_key][json_key]
                    unit = station_data[found_var_key]['unit']
                    response = (
                        f"La estadística **{stat_name_es} de {variable_friendly_map.get(found_var_key, found_var_key.capitalize())}** "
                        f"registrada en la estación **{found_station}** es de: **{value:.2f} {unit}**."
                    )
                except KeyError:
                     response = f"No pude encontrar el valor '{stat_name_es}' para la variable '{found_var_key.capitalize()}' en esa estación."
            
            # 7. Estadística General de Estación (Por nombre o número)
            elif found_station and ("estadísticas" in prompt_lower or "datos de" in prompt_lower or "háblame de" in prompt_lower or "información de" in prompt_lower):
                
                station_data = STATION_STATS_DATA[found_station]
                stats = station_data['stats']
                
                response = f"Aquí están las estadísticas resumidas para la estación **{found_station}**:\n\n"
                response += f"**Ubicación:** Lat: {station_data['latitud']:.6f}, Lon: {station_data['longitud']:.6f}\n\n"
                
                stat_output = []
                for var_key, stats_dict in stats.items():
                    var_name = variable_friendly_map.get(var_key, var_key.capitalize())
                    unit = stats_dict['unit']
                    
                    if var_key == 'precipitacion':
                        stat_output.append(f"**{var_name}:** Total {stats_dict['sum']:.2f} {unit}, Máx (15min) {stats_dict['max']:.2f} {unit}.")
                    else:
                        stat_output.append(f"**{var_name} ({unit}):** Máx {stats_dict['max']:.2f}, Mín {stats_dict['min']:.2f}, Media {stats_dict['mean']:.2f}.")
                
                response += "\n\n".join(stat_output)

            # 8. Definición de Variable (Por nombre o número)
            elif found_var_key and ("qué es" in prompt_lower or "explicame" in prompt_lower or "háblame de" in prompt_lower or "definición" in prompt_lower or "variable" in prompt_lower):
                 response = VARIABLE_DESCRIPTIONS.get(found_var_key, "Lo siento, no tengo una descripción para esa variable específica.")
            
            # --- LÓGICA DE FALLO ---
            elif not response: 
                response = (
                    "No estoy seguro de cómo responder a eso. Intenta preguntar por una **variable** ('PM2.5', 'variable 1'), una **sección** ('mapa', 'animación'), o una **estadística específica** (ej. 'máxima temperatura en Halley UIS')."
                )

            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(f"🌿 **EcoBot:** {response}")



# SECCIÓN: EQUIPO (con colores verdes unificados)
# -----------------------------------------------
elif menu == "Equipo":
    st.markdown("""
    <style>
        .team-banner {
            text-align: center;
            color: #2E8B57;
            font-size: 36px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 5px;
        }
        .team-subtitle {
            text-align: center;
            color: #2E8B57;
            font-size: 16px;
            margin-bottom: 30px;
        }
        .team-container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 40px;
            margin: 0 auto;
            max-width: 1000px;
        }
        .member-card {
            background-color: #DDE6D5;
            color: #2E8B57;
            border-radius: 20px;
            padding: 25px;
            width: 260px;
            text-align: center;
            box-shadow: 4px 6px 14px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .member-card:hover {
            transform: translateY(-8px);
            box-shadow: 6px 8px 18px rgba(0,0,0,0.25);
        }
        .member-name {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2E8B57;
        }
        .member-link {
            margin-top: 10px;
            color: #2E8B57;
        }
        .member-link a {
            text-decoration: none;
            color: #2E8B57;
            font-weight: bold;
            transition: color 0.3s ease;
        }
        .member-link a:hover {
            color: #1F6B44;
        }
    </style>

    <p style="color: #2E8B57; font-size: 28px; text-align: center; line-height: 1.6; max-width: 850px; margin: 0 auto;">
    Somos el equipo que da vida a <b>EcoStats</b>, una iniciativa dedicada a convertir los datos ambientales en conocimiento útil y accesible para todos. 
    Nuestro objetivo es impulsar la comprensión del entorno mediante herramientas tecnológicas que inspiren un cambio sostenible.
    </p>

    <div class="team-container">
        <div class="member-card">
            <div class="member-name">Daniel Ormeño</div>
            <div class="member-link">Visita mi GitHub <a href="https://github.com/Orsaki" target="_blank">aquí</a></div>
        </div>

        <div class="member-card">
            <div class="member-name">Brisa Paredes</div>
            <div class="member-link">Visita mi GitHub <a href="https://github.com/BrisaParedes" target="_blank">aquí</a></div>
        </div>

        <div class="member-card">
            <div class="member-name">Pamela Lázaro</div>
            <div class="member-link">Visita mi GitHub <a href="https://github.com/lazaropamela" target="_blank">aquí</a></div>
        </div>

        <div class="member-card">
            <div class="member-name">Fátima Montes</div>
            <div class="member-link">Visita mi GitHub <a href="https://github.com/FatimaMY" target="_blank">aquí</a></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


