import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import altair as alt
import plotly.express as px

# -----------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------
st.set_page_config(page_title="EcoStats: Clima en Movimiento", layout="wide")

# -----------------------------
# FUNCIÓN PARA CARGAR DATOS
# -----------------------------
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = [col.lower().strip() for col in df.columns] 
        
        df = df.rename(columns={
            "nombre_estacion": "estacion",
            "lluvia_mm": "precipitacion",
            "temp_ext_media_c": "temperatura" 
        })

        if 'temperatura' not in df.columns:
             if 'temp_ext_media_c ' in df.columns: 
                 df = df.rename(columns={'temp_ext_media_c ': 'temperatura'})
             elif 'temp_ext_media_C' in df.columns: 
                 df = df.rename(columns={'temp_ext_media_C': 'temperatura'})

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['month'] = df['timestamp'].dt.month
        
        cols_to_numeric = ['pm_2p5_media_ugm3', 'temperatura', 'precipitacion', 'hum_ext_ult']
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except FileNotFoundError:
        st.error(f"Error: No se pudo encontrar el archivo de datos en: {file_path}")
        return None
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

# --- ¡IMPORTANTE! ---
# Asegúrate de que esta ruta sea la CORRECTA
FILE_PATH = 'c:/Users/ASUS/Desktop/HACKATON/datos_limpios.csv'
df = load_data(FILE_PATH)

# Diccionario para mapear número de mes a nombre (en español)
month_map = {9: "Septiembre", 10: "Octubre", 11: "Noviembre"}

# -----------------------------
# MENÚ PRINCIPAL
# -----------------------------
with st.sidebar:
    menu = option_menu(
        menu_title="Menú Principal",
        options=["Datos teóricos", "Mapa de estaciones", "Visualización de variables", "Chatbot", "Equipo"],
        icons=["book", "map", "bar-chart-line", "chat", "people"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )

# -----------------------------
# SECCIÓN: DATOS TEÓRICOS
# -----------------------------
if menu == "Datos teóricos":
    # (Pega aquí todo tu código HTML de la sección "Datos teóricos")
    st.markdown("<h1>🌎 <span style='color:#FFF176;'>EcoStats</span></h1>", unsafe_allow_html=True)
    st.markdown("*(El contenido de esta sección se mantiene igual)*")
    # ... (Tu HTML de la sección "Datos teóricos" va aquí) ...
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
    st.info("Agradecimientos a la Red Ambiental Ciudadana de Monitoreo (RACiMo). [Visita su página aquí](https://class.redclara.net/halley/moncora/intro.html).")

# -----------------------------------------------
# SECCIÓN: Visualización de variables
# -----------------------------------------------
elif menu == "Visualización de variables":
    st.title("Visualización de variables")

    if df is not None:
        
        # --- Tres columnas para los filtros ---
        col1, col2, col3 = st.columns([2, 2, 1]) 

        with col1:
            variable_choice = st.selectbox(
                label="Selecciona la Variable:",
                options=[
                    "Concentración de PM2.5 (µg/m³)", 
                    "Temperatura Media (°C)", 
                    "Precipitación (mm)",
                    "Humedad (Mapa de Calor)"
                ],
                index=0
            )

        with col2:
            station_list = df['estacion'].dropna().unique().tolist()
            selected_station = st.selectbox(
                label="Selecciona la Estación:",
                options=sorted(station_list),
                index=0
            )
        
        with col3:
            month_list = sorted([m for m in df['month'].unique() if m in month_map])
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
        # GRÁFICO 1: PM2.5
        # ==========================================================
        if variable_choice == "Concentración de PM2.5 (µg/m³)" and 'pm_2p5_media_ugm3' in df.columns:
            
            data_col = 'pm_2p5_media_ugm3'
            if not df_filtered[data_col].dropna().empty:
                
                # --- Métricas con iconos ---
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Máximo (µg/m³)", f"{df_filtered[data_col].max():.2f}")
                stat_col2.metric("📉 Mínimo (µg/m³)", f"{df_filtered[data_col].min():.2f}")
                stat_col3.metric("📊 Medio (µg/m³)", f"{df_filtered[data_col].mean():.2f}")
                st.markdown("---")

                line_chart = alt.Chart(df_filtered).mark_line(point=True, opacity=0.8).encode(
                    x=alt.X('timestamp:T', title='Fecha y Hora', axis=alt.Axis(tickCount=10)),
                    y=alt.Y(f'{data_col}:Q', title='PM2.5 (µg/m³)', scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip('timestamp:T', title='Fecha y Hora', format='%Y-%m-%d %H:%M'),
                        alt.Tooltip(f'{data_col}:Q', title='PM2.5'),
                        alt.Tooltip('estacion', title='Estación')
                    ]
                )
                
                rule_df = pd.DataFrame({'limite_perjudicial': [56]})
                rule = alt.Chart(rule_df).mark_rule(color='red', strokeWidth=2, strokeDash=[5, 5]).encode(y='limite_perjudicial:Q')
                text = alt.Chart(rule_df).mark_text(align='left', baseline='bottom', dx=5, dy=-5, color='red', fontSize=12).encode(y='limite_perjudicial:Q', text=alt.value('Límite Perjudicial (56 µg/m³)') )

                final_chart_pm25 = alt.layer(line_chart, rule, text).properties(
                    title=f'PM2.5 para: {selected_station} ({month_map.get(selected_month_num, "")})'
                ).interactive()

                st.altair_chart(final_chart_pm25, use_container_width=True)
            else:
                st.warning(f"No hay datos de PM2.5 para '{selected_station}' en {month_map.get(selected_month_num, '')}.")
        
        # ==========================================================
        # GRÁFICO 2: TEMPERATURA
        # ==========================================================
        elif variable_choice == "Temperatura Media (°C)" and 'temperatura' in df.columns:
            
            data_col = 'temperatura'
            dff_temp = df_filtered.dropna(subset=[data_col])
            
            if not dff_temp.empty:
                
                # --- Métricas con iconos ---
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Máxima (°C)", f"{dff_temp[data_col].max():.2f}")
                stat_col2.metric("📉 Mínima (°C)", f"{dff_temp[data_col].min():.2f}")
                stat_col3.metric("📊 Media (°C)", f"{dff_temp[data_col].mean():.2f}")
                st.markdown("---")
                
                colorscale = [[0.0, "rgb(0, 68, 204)"], [0.33, "rgb(102, 204, 255)"], [0.66, "rgb(255, 255, 102)"], [1.0, "rgb(255, 51, 51)"]]

                fig_temp = px.scatter(
                    dff_temp, x="timestamp", y=data_col, color=data_col,
                    color_continuous_scale=colorscale,
                    labels={data_col: "Temperatura (°C)", "timestamp": "Tiempo"},
                )
                fig_temp.add_scatter(
                    x=dff_temp["timestamp"], y=dff_temp[data_col],
                    mode="lines", line=dict(color="rgba(100,100,100,0.3)", width=2), name="Tendencia",
                )
                fig_temp.update_layout(
                    title=dict(text=f"Temperatura - {selected_station} ({month_map.get(selected_month_num, "")})", x=0.5),
                    xaxis_title="Tiempo", yaxis_title="Temperatura (°C)",
                    coloraxis_colorbar=dict(title="°C"),
                    plot_bgcolor="rgba(245,245,245,1)", paper_bgcolor="rgba(245,245,245,1)",
                )
                fig_temp.update_traces(hovertemplate="Fecha: %{x}<br>Temperatura: %{y:.2f} °C<extra></extra>")
                st.plotly_chart(fig_temp, use_container_width=True)
            else:
                st.warning(f"No hay datos de Temperatura para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

        # ==========================================================
        # GRÁFICO 3: PRECIPITACIÓN
        # ==========================================================
        elif variable_choice == "Precipitación (mm)" and 'precipitacion' in df.columns:
            
            data_col = 'precipitacion'
            dff_precip = df_filtered.dropna(subset=[data_col])

            if not dff_precip.empty:
                
                # --- Métricas con iconos (modificadas para lluvia) ---
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("🌧️ Máxima (en 15min)", f"{dff_precip[data_col].max():.2f} mm")
                stat_col2.metric("💧 Total Acumulada", f"{dff_precip[data_col].sum():.2f} mm")
                stat_col3.metric("📊 Media (por registro)", f"{dff_precip[data_col].mean():.2f} mm")
                st.markdown("---")

                fig_precip = px.area(
                    dff_precip, x="timestamp", y=data_col,
                    title=f"Precipitación - {selected_station} ({month_map.get(selected_month_num, "")})",
                    color_discrete_sequence=["#0077cc"],
                )
                fig_precip.update_traces(line_color="#0055aa", fillcolor="rgba(0,119,204,0.3)")
                fig_precip.update_layout(
                    template="plotly_white", xaxis_title="Fecha", yaxis_title="Precipitación (mm)",
                    title_x=0.5, hovermode="x unified",
                )
                fig_precip.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgrey")
                fig_precip.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgrey")
                
                st.plotly_chart(fig_precip, use_container_width=True)
            else:
                st.warning(f"No hay datos de Precipitación para '{selected_station}' en {month_map.get(selected_month_num, '')}.")

        # ==========================================================
        # GRÁFICO 4: HEATMAP DE HUMEDAD
        # ==========================================================
        elif variable_choice == "Humedad (Mapa de Calor)" and 'hum_ext_ult' in df.columns:
            
            data_col = 'hum_ext_ult'
            df_filtered_hum = df_filtered.dropna(subset=[data_col])

            if not df_filtered_hum.empty:

                # --- Métricas con iconos ---
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("📈 Humedad Máxima (%)", f"{df_filtered_hum[data_col].max():.2f}")
                stat_col2.metric("📉 Humedad Mínima (%)", f"{df_filtered_hum[data_col].min():.2f}")
                stat_col3.metric("📊 Humedad Media (%)", f"{df_filtered_hum[data_col].mean():.2f}")
                st.markdown("---")

                heatmap = alt.Chart(df_filtered_hum).mark_rect().encode(
                    x=alt.X('date(timestamp):O', title=f"Día de {month_map.get(selected_month_num, '')}"),
                    y=alt.Y('hours(timestamp):O', title='Hora del Día'),
                    color=alt.Color(f'mean({data_col}):Q', 
                                  title='Humedad Promedio (%)',
                                  scale=alt.Scale(scheme='tealblues')),
                    tooltip=[
                        alt.Tooltip('timestamp:T', title='Fecha y Hora', format='%Y-%m-%d %H:%M'),
                        alt.Tooltip(f'mean({data_col}):Q', title='Humedad Promedio'),
                        alt.Tooltip('estacion', title='Estación')
                    ]
                ).properties(
                    title=f'Mapa de Calor de Humedad - {selected_station} ({month_map.get(selected_month_num, "")})'
                ).interactive()
                
                st.altair_chart(heatmap, use_container_width=True)
            else:
                st.warning(f"No hay datos de Humedad para '{selected_station}' en {month_map.get(selected_month_num, '')}.")
        
        # --- Caso por si falta la columna de la variable ---
        else:
            st.warning(f"La variable '{variable_choice}' no se encuentra en los datos cargados o no está configurada.")

    else:
        st.warning("No se pudieron cargar los datos. Verifica la ruta del archivo CSV.")


# -----------------------------
# OTRAS SECCIONES
# -----------------------------
elif menu == "Mapa de estaciones":
    st.title("Mapa de estaciones")
    st.write("Aquí se podrán mostrar mapas de ubicación de las estaciones. Contenido por definir.")

elif menu == "Chatbot":
    st.title("Chatbot")
    st.write("Asistente virtual para guiar al usuario en la exploración de los datos.")

# --- ¡SECCIÓN DE EQUIPO ACTUALIZADA! ---
elif menu == "Equipo":
    st.title("Nuestro Equipo")
    st.markdown("---")
    
    st.markdown("<h2 style='text-align: center;'>🌎 EcoStats</h2>", unsafe_allow_html=True)
    
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