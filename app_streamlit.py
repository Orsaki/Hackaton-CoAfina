import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import altair as alt
import plotly.express as px
import numpy as np
import pydeck as pdk  # <-- AÑADIDO: Necesario para el mapa de estaciones

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
    "temp_ext_media_C": "temperatura",  # Maneja ambas mayúsculas
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

        # 1. Limpiar nombres de columnas
        df.columns = [col.lower().strip() for col in df.columns]

        # 2. Renombrar usando el mapa
        df = df.rename(columns=COLUMN_RENAME_MAP)

        # 3. Convertir timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['month'] = df['timestamp'].dt.month
        else:
            st.error("Error: La columna 'timestamp' no se encuentra en los datos.")
            return None

        # 4. Convertir columnas a numérico
        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                # Informar si falta una columna esperada (opcional)
                print(
                    f"Advertencia: La columna '{col}' no se encontró y no será cargada.")

        # 5. Asegurar latitud y longitud
        if 'latitud' not in df.columns or 'longitud' not in df.columns:
            st.error("Error: Faltan columnas 'latitud' o 'longitud' en los datos.")
            return None

        return df

    except FileNotFoundError:
        st.error(
            f"Error: No se pudo encontrar el archivo de datos en: {file_path}")
        return None
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None


# --- ¡CORRECCIÓN CRÍTICA DE RUTA! ---
# Esto asume que 'datos_limpios.csv' está en el MISMO directorio que 'app_streamlit.py'
FILE_PATH = 'datos_limpios.csv'
df = load_data(FILE_PATH)

# Diccionario para mapear número de mes a nombre (en español)
month_map = {9: "Septiembre", 10: "Octubre", 11: "Noviembre"}

# -----------------------------
# MENÚ PRINCIPAL (¡REESTRUCTURADO!)
# -----------------------------
with st.sidebar:
    st.markdown("## 🌎 EcoStats")
    st.markdown("Clima en Movimiento")
    menu = option_menu(
        menu_title="Menú Principal",
        options=[
            "Inicio",
            "Mapa de Estaciones",      # Objetivo 1
            "Animación de Datos",      # Objetivo 3 (¡El principal!)
            "Análisis por Estación",   # Objetivo 2 (Tu sección)
            "Chatbot",                 # Objetivo 4
            "Equipo"
        ],
        icons=[
            "house",
            "map",                     # Icono para Mapa
            "play-btn-fill",           # Icono para Animación
            "bar-chart-line",          # Icono para Análisis
            "chat-dots",               # Icono para Chatbot
            "people"
        ],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )

# -----------------------------
# SECCIÓN: INICIO (Tus "Datos teóricos")
# -----------------------------
if menu == "Inicio":
    # (Tu código HTML para la portada se mantiene)
    st.markdown("<h1>🌎 <span style='color:#FFF176;'>EcoStats</span></h1>",
                unsafe_allow_html=True)
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
            color: #FFF9C4;
            font-size: 32px;
            font-family: 'Trebuchet MS', sans-serif;
            margin-top: 30px;
        ">
            ¿Te gustaría interactuar jugando mediante mapas para entender el clima?
        </h2>
        <p style="
            text-align: center;
            color: #E0E0E0;
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
            🌎 <span style="color:#FFF176;">EcoStats</span>
        </h1>
        <h2 style="
            text-align: center;
            color: #FFF176;
            font-size: 50px;
            font-family: 'Trebuchet MS', sans-serif;
            margin-top: -10px;
        ">
            Clima en Movimiento
        </h2>
        <p style="
            text-align: center;
            color: #E0E0E0;
            font-size: 22px;
            font-family: 'Verdana', sans-serif;
        ">
            Explora, visualiza y comprende los datos ambientales de Santander — una experiencia interactiva con RACiMo.
        </p>
        <div style="text-align:center; margin-top:30px; margin-bottom:40px;" class="fade-in">
            <img src="https://pouch.jumpshare.com/preview/9wCPCONGBeJ9GOnB3uF4BEwEYIFdKu8ss-ssPDHI89ASlfXDRIz6eexvDq3G29-lFEICOzJf0GzmGjQEgiU4L42IMI9s50zJa-nQi_6gRUk" 
                 alt="Animación del clima"
                 style="width:70%; max-width:700px; border:none; border-radius:20px; box-shadow:none;">
        </div>
        <hr style="border: 1px solid #FFF176; width: 80%; margin:auto; margin-bottom:40px;">
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h2 style='color:#FFFFFF; text-align:center; margin-top:40px;'>🌦️ Variables que podrás explorar:</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("""
        <div style="background-color:#123456; padding:30px; border-radius:15px; margin-bottom:40px;">
            <h3 style="color:#FFD700;">🌡️ Temperatura</h3>
            <p style="color:#E0E0E0;">Indica qué tan caliente o frío está el ambiente. Afecta la salud, la agricultura y los ecosistemas.</p>
            <small style="color:#B0BEC5;">Un aumento sostenido puede indicar olas de calor.</small>
        </div>
        <div style="background-color:#123456; padding:30px; border-radius:15px; margin-bottom:40px;">
            <h3 style="color:#FFD700;">💧 Humedad Relativa</h3>
            <p style="color:#E0E0E0;">Nos dice cuánta agua hay en el aire. Una alta humedad puede hacer que sintamos más calor.</p>
        </div>
        <div style="background-color:#123456; padding:30px; border-radius:15px; margin-bottom:40px;">
            <h3 style="color:#FFD700;">🌧️ Precipitación</h3>
            <p style="color:#E0E0E0;">Cantidad de lluvia registrada. Es clave para entender sequías, inundaciones y el ciclo del agua.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background-color:#123456; padding:30px; border-radius:15px; margin-bottom:40px;">
            <h3 style="color:#FFD700;">🌫️ PM2.5 (Partículas finas)</h3>
            <p style="color:#E0E0E0;">Son pequeñas partículas en el aire que pueden afectar la salud respiratoria.</p>
            <small style="color:#B0BEC5;">Se miden en microgramos por metro cúbico (µg/m³).</small>
        </div>
        <div style="background-color:#123456; padding:30px; border-radius:15px; margin-bottom:40px;">
            <h3 style="color:#FFD700;">🌈 Índice de Calidad del Aire (ICA)</h3>
            <p style="color:#E0E0E0;">Nos muestra qué tan limpio o contaminado está el aire mediante una escala de colores:</p>
            <p style="color:#FFFFFF;">
            🟢 Buena | 🟡 Moderada | 🟠 Regular | 🔴 Mala
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <h3 style="text-align:center; color:#FFF9C4; font-size:24px;">
        🌍 Entender los datos ambientales nos ayuda a actuar: plantar árboles, reducir la contaminación y adaptarnos al cambio climático.
    </h3>
    <p style="text-align:center; font-size:18px; color:#EAEAEA;">
        <b>¡Cada dato cuenta para cuidar nuestro planeta! 🌎</b>
    </p>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.info(
        "Agradecimientos a la Red Ambiental Ciudadana de Monitoreo (RACiMo). [Visita su página aquí](https://class.redclara.net/halley/moncora/intro.html).")

# -----------------------------------------------
# SECCIÓN: MAPA DE ESTACIONES (¡NUEVO!)
# -----------------------------------------------
elif menu == "Mapa de Estaciones":
    st.title("Mapa de Ubicación de Estaciones RACiMo")
    st.write("Explora la ubicación geográfica de cada estación de monitoreo.")

    if df is not None:
        # Obtenemos las ubicaciones únicas de las estaciones
        locations = df.drop_duplicates(subset=['estacion'])[
            ['estacion', 'latitud', 'longitud']]
        # Pydeck prefiere 'lat' y 'lon'
        locations = locations.rename(
            columns={"latitud": "lat", "longitud": "lon"})

        # Centramos el mapa
        mid_lat = locations['lat'].mean()
        mid_lon = locations['lon'].mean()

        view_state = pdk.ViewState(
            latitude=mid_lat,
            longitude=mid_lon,
            zoom=8,
            pitch=50,
        )

        # Capa para los puntos
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=locations,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',  # Color RGB
            get_radius=500,  # Radio en metros
            pickable=True,
            auto_highlight=True
        )

        # Tooltip
        tooltip = {
            "html": "<b>Estación:</b> {estacion}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }

        # Renderizar el mapa
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip
        ))
    else:
        st.warning("No se pudieron cargar los datos para el mapa.")

# -----------------------------------------------
# SECCIÓN: ANIMACIÓN DE DATOS (¡NUEVO - CLAVE DEL RETO!)
# -----------------------------------------------
elif menu == "Animación de Datos":
    st.title("Animación de Datos Ambientales")
    st.write("Selecciona una variable y presiona 'Play' para ver su evolución en el tiempo sobre el mapa.")

    if df is not None:
        df_anim = df.copy()

        # Asegurarnos que el timestamp está ordenado
        df_anim = df_anim.sort_values(by="timestamp")

        # --- Optimización para la animación ---
        # Creamos una columna 'fecha_hora' como string para el 'animation_frame'
        # Agrupar por hora mejora el rendimiento y la visualización
        df_anim['fecha_hora_anim'] = df_anim['timestamp'].dt.strftime(
            '%Y-%m-%d %H:00')

        # Agrupamos los datos por estación y hora
        df_anim_grouped = df_anim.groupby(['estacion', 'latitud', 'longitud', 'fecha_hora_anim']).agg({
            'temperatura': 'mean',
            'precipitacion': 'sum',
            'humedad': 'mean',
            'pm2_5': 'mean',
            'ica': 'mean',
            'presion': 'mean'
        }).reset_index()

        # --- Selectores ---
        variables_anim_list = [
            'temperatura', 'precipitacion', 'humedad', 'pm2_5', 'ica', 'presion']
        variable_anim_choice = st.selectbox(
            "Selecciona la variable a animar:",
            variables_anim_list,
            index=0  # 'temperatura' por defecto
        )

        st.info("💡 Consejo: Usa el control deslizante de tiempo y el botón de 'Play' en la parte inferior del mapa.")

        # --- El Gráfico Animado ---
        fig_anim = px.scatter_mapbox(
            df_anim_grouped.dropna(
                # Evitar errores
                subset=[variable_anim_choice, 'latitud', 'longitud']),
            lat="latitud",
            lon="longitud",
            size=variable_anim_choice,  # El tamaño del círculo representa la variable
            color=variable_anim_choice,  # El color también representa la variable
            hover_name="estacion",
            hover_data={
                "latitud": False,
                "longitud": False,
                "fecha_hora_anim": True,
                variable_anim_choice: ":.2f"
            },
            animation_frame="fecha_hora_anim",  # ¡La magia de la animación!
            color_continuous_scale=px.colors.sequential.YlOrRd,
            size_max=30,
            zoom=8,
            mapbox_style="carto-positron",
            center={"lat": df_anim_grouped['latitud'].mean(
            ), "lon": df_anim_grouped['longitud'].mean()},
            title=f"Animación de '{variable_anim_choice}' a lo largo del tiempo"
        )

        fig_anim.update_layout(height=600)
        st.plotly_chart(fig_anim, use_container_width=True)

    else:
        st.warning("No se pudieron cargar los datos para la animación.")


# -----------------------------------------------
# SECCIÓN: ANÁLISIS POR ESTACIÓN (Tu "Visualización de variables" adaptada)
# -----------------------------------------------
elif menu == "Análisis por Estación":
    st.title("Análisis Detallado por Estación")
    st.write(
        "Explora gráficos estáticos y detallados para una estación y variable específica.")

    if df is not None:

        # --- Tres columnas para los filtros ---
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            # --- MODIFICADO ---
            # Opciones adaptadas a los nuevos nombres de columnas
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
            # Obtenemos el nombre de la columna real
            data_col = variable_map[variable_choice_label]
            # --------------------

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

        # --- Filtro de datos general ---
        df_filtered = df[
            (df['estacion'] == selected_station) &
            (df['month'] == selected_month_num)
        ]

        # --- Lógica para mostrar el gráfico seleccionado ---

        # ==========================================================
        # GRÁFICO 1: PM2.5 (Adaptado a 'pm2_5')
        # ==========================================================
        if data_col == "pm2_5":
            if not df_filtered[data_col].dropna().empty:
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Máximo (µg/m³)",
                                 f"{df_filtered[data_col].max():.2f}")
                stat_col2.metric("📉 Mínimo (µg/m³)",
                                 f"{df_filtered[data_col].min():.2f}")
                stat_col3.metric("📊 Medio (µg/m³)",
                                 f"{df_filtered[data_col].mean():.2f}")
                st.markdown("---")

                line_chart = alt.Chart(df_filtered).mark_line(point=True, opacity=0.8).encode(
                    x=alt.X('timestamp:T', title='Fecha y Hora',
                            axis=alt.Axis(tickCount=10)),
                    y=alt.Y(f'{data_col}:Q', title='PM2.5 (µg/m³)',
                            scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('timestamp:T', title='Fecha y Hora',
                                    format='%Y-%m-%d %H:%M'),
                        alt.Tooltip(f'{data_col}:Q', title='PM2.5'),
                        alt.Tooltip('estacion', title='Estación')]
                )
                rule_df = pd.DataFrame({'limite_perjudicial': [56]})
                rule = alt.Chart(rule_df).mark_rule(color='red', strokeWidth=2, strokeDash=[
                    5, 5]).encode(y='limite_perjudicial:Q')
                text = alt.Chart(rule_df).mark_text(align='left', baseline='bottom', dx=5, dy=-5, color='red',
                                                    fontSize=12).encode(y='limite_perjudicial:Q', text=alt.value('Límite Perjudicial (56 µg/m³)'))
                final_chart_pm25 = alt.layer(line_chart, rule, text).properties(
                    title=f'PM2.5 para: {selected_station} ({month_map.get(selected_month_num, "")})'
                ).interactive()
                st.altair_chart(final_chart_pm25, use_container_width=True)
            else:
                st.warning(
                    f"No hay datos de PM2.5 para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

        # ==========================================================
        # GRÁFICO 2: TEMPERATURA (Adaptado a 'temperatura')
        # ==========================================================
        elif data_col == "temperatura":
            dff_temp = df_filtered.dropna(subset=[data_col])
            if not dff_temp.empty:
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric(
                    "📈 Máxima (°C)", f"{dff_temp[data_col].max():.2f}")
                stat_col2.metric(
                    "📉 Mínima (°C)", f"{dff_temp[data_col].min():.2f}")
                stat_col3.metric(
                    "📊 Media (°C)", f"{dff_temp[data_col].mean():.2f}")
                st.markdown("---")

                colorscale = [[0.0, "rgb(0, 68, 204)"], [0.33, "rgb(102, 204, 255)"], [
                    0.66, "rgb(255, 255, 102)"], [1.0, "rgb(255, 51, 51)"]]
                fig_temp = px.scatter(
                    dff_temp, x="timestamp", y=data_col, color=data_col,
                    color_continuous_scale=colorscale, labels={
                        data_col: "Temperatura (°C)", "timestamp": "Tiempo"},
                )
                fig_temp.add_scatter(x=dff_temp["timestamp"], y=dff_temp[data_col], mode="lines", line=dict(
                    color="rgba(100,100,100,0.3)", width=2), name="Tendencia")
                fig_temp.update_layout(
                    title=dict(
                        text=f"Temperatura - {selected_station} ({month_map.get(selected_month_num, "")})", x=0.5),
                    xaxis_title="Tiempo", yaxis_title="Temperatura (°C)", coloraxis_colorbar=dict(title="°C"),
                    plot_bgcolor="rgba(245,245,245,1)", paper_bgcolor="rgba(245,245,245,1)",
                )
                fig_temp.update_traces(
                    hovertemplate="Fecha: %{x}<br>Temperatura: %{y:.2f} °C<extra></extra>")
                st.plotly_chart(fig_temp, use_container_width=True)
            else:
                st.warning(
                    f"No hay datos de Temperatura para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

        # ==========================================================
        # GRÁFICO 3: PRECIPITACIÓN (Adaptado a 'precipitacion')
        # ==========================================================
        elif data_col == "precipitacion":
            dff_precip = df_filtered.dropna(subset=[data_col])
            if not dff_precip.empty:
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("🌧️ Máxima (en 15min)",
                                 f"{dff_precip[data_col].max():.2f} mm")
                stat_col2.metric("💧 Total Acumulada",
                                 f"{dff_precip[data_col].sum():.2f} mm")
                stat_col3.metric("📊 Media (por registro)",
                                 f"{dff_precip[data_col].mean():.2f} mm")
                st.markdown("---")

                fig_precip = px.area(
                    dff_precip, x="timestamp", y=data_col,
                    title=f"Precipitación - {selected_station} ({month_map.get(selected_month_num, "")})",
                    color_discrete_sequence=["#0077cc"],
                )
                fig_precip.update_traces(
                    line_color="#0055aa", fillcolor="rgba(0,119,204,0.3)")
                fig_precip.update_layout(
                    template="plotly_white", xaxis_title="Fecha", yaxis_title="Precipitación (mm)",
                    title_x=0.5, hovermode="x unified",
                )
                st.plotly_chart(fig_precip, use_container_width=True)
            else:
                st.warning(
                    f"No hay datos de Precipitación para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

        # ==========================================================
        # GRÁFICO 4: HEATMAP DE HUMEDAD (Adaptado a 'humedad')
        # ==========================================================
        elif data_col == "humedad":
            df_filtered_hum = df_filtered.dropna(subset=[data_col])
            if not df_filtered_hum.empty:
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Humedad Máxima (%)",
                                 f"{df_filtered_hum[data_col].max():.2f}")
                stat_col2.metric("📉 Humedad Mínima (%)",
                                 f"{df_filtered_hum[data_col].min():.2f}")
                stat_col3.metric("📊 Humedad Media (%)",
                                 f"{df_filtered_hum[data_col].mean():.2f}")
                st.markdown("---")

                heatmap = alt.Chart(df_filtered_hum).mark_rect().encode(
                    x=alt.X(
                        'date(timestamp):O', title=f"Día de {month_map.get(selected_month_num, '')}"),
                    y=alt.Y('hours(timestamp):O', title='Hora del Día'),
                    color=alt.Color(f'mean({data_col}):Q', title='Humedad Promedio (%)', scale=alt.Scale(
                        scheme='tealblues')),
                    tooltip=[
                        alt.Tooltip('timestamp:T', title='Fecha y Hora',
                                    format='%Y-%m-%d %H:%M'),
                        alt.Tooltip(f'mean({data_col}):Q',
                                    title='Humedad Promedio'),
                        alt.Tooltip('estacion', title='Estación')]
                ).properties(
                    title=f'Mapa de Calor de Humedad - {selected_station} ({month_map.get(selected_month_num, "")})'
                ).interactive()
                st.altair_chart(heatmap, use_container_width=True)
            else:
                st.warning(
                    f"No hay datos de Humedad para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

        # ==========================================================
        # GRÁFICO 5: VELOCIDAD VIENTO (Adaptado a 'viento_velocidad')
        # ==========================================================
        elif data_col == "viento_velocidad":
            dff_wind_speed = df_filtered.dropna(subset=[data_col])
            if not dff_wind_speed.empty:
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("💨 Máxima (km/h)",
                                 f"{dff_wind_speed[data_col].max():.2f}")
                stat_col2.metric("🍃 Mínima (km/h)",
                                 f"{dff_wind_speed[data_col].min():.2f}")
                stat_col3.metric("📊 Media (km/h)",
                                 f"{dff_wind_speed[data_col].mean():.2f}")
                st.markdown("---")

                fig_wind_speed = px.line(
                    dff_wind_speed, x="timestamp", y=data_col,
                    title=f"Velocidad del Viento - {selected_station} ({month_map.get(selected_month_num, "")})",
                    color_discrete_sequence=["#2ca02c"]
                )
                fig_wind_speed.update_layout(
                    template="plotly_white", xaxis_title="Fecha", yaxis_title="Velocidad Viento (km/h)",
                    title_x=0.5, hovermode="x unified",
                )
                st.plotly_chart(fig_wind_speed, use_container_width=True)
            else:
                st.warning(
                    f"No hay datos de Velocidad del Viento para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

        # ==========================================================
        # GRÁFICO 6: PRESIÓN (Adaptado a 'presion')
        # ==========================================================
        elif data_col == "presion":
            dff_pressure = df_filtered.dropna(subset=[data_col])
            if not dff_pressure.empty:
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Máxima (hPa)",
                                 f"{dff_pressure[data_col].max():.2f}")
                stat_col2.metric("📉 Mínima (hPa)",
                                 f"{dff_pressure[data_col].min():.2f}")
                stat_col3.metric(
                    "📊 Media (hPa)", f"{dff_pressure[data_col].mean():.2f}")
                st.markdown("---")

                fig_pressure = px.line(
                    dff_pressure, x="timestamp", y=data_col,
                    title=f"Presión Barométrica - {selected_station} ({month_map.get(selected_month_num, "")})",
                    color_discrete_sequence=["#9467bd"]
                )
                fig_pressure.update_layout(
                    template="plotly_white", xaxis_title="Fecha", yaxis_title="Presión (hPa)",
                    title_x=0.5, hovermode="x unified",
                )
                st.plotly_chart(fig_pressure, use_container_width=True)
            else:
                st.warning(
                    f"No hay datos de Presión para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

        # ==========================================================
        # GRÁFICO 7: ROSA DE VIENTOS (Adaptado)
        # ==========================================================
        elif data_col == "viento_direccion":
            dff_wind = df_filtered.dropna(
                subset=['viento_direccion', 'viento_velocidad'])
            if not dff_wind.empty:
                st.info(
                    "La Rosa de Vientos muestra la frecuencia de la dirección (de dónde viene el viento) y su intensidad.")

                bins = [-0.1, 22.5, 67.5, 112.5, 157.5,
                        202.5, 247.5, 292.5, 337.5, 360]
                labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
                dff_wind_binned = dff_wind.copy()
                dff_wind_binned['Dirección'] = pd.cut(
                    dff_wind_binned['viento_direccion'], bins=bins, labels=labels, right=True)

                speed_bins = [0, 5, 10, 15, 20, float('inf')]
                speed_labels = ['0-5 km/h', '5-10 km/h',
                                '10-15 km/h', '15-20 km/h', '>20 km/h']
                dff_wind_binned['Velocidad (km/h)'] = pd.cut(
                    dff_wind_binned['viento_velocidad'], bins=speed_bins, labels=speed_labels, right=False)

                wind_rose_data = dff_wind_binned.groupby(
                    ['Dirección', 'Velocidad (km/h)']).size().reset_index(name='Frecuencia')
                wind_rose_data_final = wind_rose_data.groupby(
                    ['Dirección', 'Velocidad (km/h)']).sum().reset_index()

                try:
                    fig_wind_rose = px.bar_polar(
                        wind_rose_data_final, r="Frecuencia", theta="Dirección", color="Velocidad (km/h)",
                        template="plotly_white",
                        title=f"Rosa de Vientos - {selected_station} ({month_map.get(selected_month_num, "")})",
                        color_discrete_sequence=px.colors.sequential.YlOrRd,
                        category_orders={"Dirección": [
                            'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']}
                    )
                    st.plotly_chart(fig_wind_rose, use_container_width=True)
                except Exception as e:
                    st.error(f"Error al generar la Rosa de Vientos: {e}.")
            else:
                st.warning(
                    f"No hay datos suficientes de Viento para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

        # --- Caso por si falta la columna ---
        else:
            st.warning(
                f"No hay datos para la variable '{data_col}' en '{selected_station}' en {month_map.get(selected_month_num, '')}.")

    else:
        st.warning(
            "No se pudieron cargar los datos. Verifica que 'datos_limpios.csv' esté en el mismo directorio.")

# -----------------------------------------------
# SECCIÓN: CHATBOT (¡NUEVO Y FUNCIONAL!)
# -----------------------------------------------
elif menu == "Chatbot":
    st.title("Asistente Virtual EcoStats 🤖")
    st.write("¡Hola! Soy tu asistente para el Reto 5. ¿En qué te puedo ayudar?")

    # Inicializar el historial del chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant",
                "content": "¿Cómo puedo ayudarte a explorar los datos de RACiMo?"}
        ]

    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input del usuario
    if prompt := st.chat_input("Escribe tu pregunta... (ej. 'mapa', 'animación', 'variables')"):
        # Añadir mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta del asistente
        with st.chat_message("assistant"):
            response = ""
            prompt_lower = prompt.lower()

            if "hola" in prompt_lower or "saludos" in prompt_lower:
                response = "¡Hola! ¿Qué te gustaría saber sobre la app?"
            elif "mapa" in prompt_lower and "animado" not in prompt_lower:
                response = "Puedes ver la ubicación de todas las estaciones en la sección **'Mapa de Estaciones'** en el menú de la izquierda."
            elif "animación" in prompt_lower or ("mapa" in prompt_lower and "interactivo" in prompt_lower):
                response = "¡Claro! La sección **'Animación de Datos'** te permite ver las variables animadas en el tiempo sobre un mapa. ¡Es la función estrella del reto!"
            elif "análisis" in prompt_lower or "gráfico" in prompt_lower or "estación" in prompt_lower:
                response = "Usa la sección **'Análisis por Estación'** para ver gráficos detallados (series de tiempo, mapas de calor, etc.) de una estación y variable específica."
            elif "variables" in prompt_lower:
                response = (
                    "Analizamos variables meteorológicas y de calidad del aire. Las principales son:\n"
                    "- **Temperatura**\n"
                    "- **Humedad**\n"
                    "- **Precipitación**\n"
                    "- **PM2.5**\n"
                    "- **ICA** (Índice de Calidad del Aire)\n"
                    "- **Viento** (velocidad y dirección)\n"
                    "- **Presión**"
                )
            elif "viento" in prompt_lower:
                response = "Puedes ver un análisis de la dirección y velocidad del viento en la sección **'Análisis por Estación'** y seleccionando la variable de viento."
            elif "gracias" in prompt_lower:
                response = "¡De nada! Estoy aquí para ayudarte a ganar este reto. 😉"
            else:
                response = (
                    "No estoy seguro de cómo responder a eso. Intenta preguntarme sobre:\n"
                    "- 'mapa'\n"
                    "- 'animación'\n"
                    "- 'análisis por estación'\n"
                    "- 'variables'"
                )

            st.markdown(response)
            st.session_state.messages.append(
                {"role": "assistant", "content": response})

# -----------------------------------------------
# SECCIÓN: EQUIPO (Tu código)
# -----------------------------------------------
elif menu == "Equipo":
    st.title("Nuestro Equipo")
    st.markdown("---")

    st.markdown("<h2 style='text-align: center;'>🌎 EcoStats</h2>",
                unsafe_allow_html=True)

    st.write(
        """
        Somos el equipo detrás de este proyecto, dedicados a hacer los datos ambientales 
        accesibles y comprensibles para todos.
        """
    )
    st.markdown("---")
    st.subheader("Integrantes:")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Daniel Kenyi Ormeño Sakihama")
        st.markdown("#### Brisa Paredes")
    with col2:
        st.markdown("#### Pamela Lazaro")
        st.markdown("#### Fatima Montes")
