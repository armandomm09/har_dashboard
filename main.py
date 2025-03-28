import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# ---------------------------
# Variable principal del evento
# ---------------------------
main_event = "2025ilch"

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Scouting FRC - Midwest Regional",
    layout="wide"
)

st.title("Dashboard de Scouting - Midwest Regional")

# ---------------------------
# Sección: Datos del Evento desde The Blue Alliance (TBA)
# ---------------------------
st.header("Datos del Evento (The Blue Alliance)")
TBA_API_KEY = st.secrets["TBA_API_KEY"]
headers = {"X-TBA-Auth-Key": TBA_API_KEY}

tba_event_url = f"https://www.thebluealliance.com/api/v3/event/{main_event}"
tba_response = requests.get(tba_event_url, headers=headers)

if tba_response.status_code == 200:
    tba_event_data = tba_response.json()
    st.markdown(f"**Nombre:** {tba_event_data.get('name', 'N/D')}")
    st.markdown(f"**Ciudad:** {tba_event_data.get('city', 'N/D')}")
    st.markdown(f"**Estado/Provincia:** {tba_event_data.get('state_prov', 'N/D')}")
    st.markdown(f"**Fecha de inicio:** {tba_event_data.get('start_date', 'N/D')}")
    st.markdown(f"**Fecha de finalización:** {tba_event_data.get('end_date', 'N/D')}")
else:
    st.error("Error al obtener datos del evento desde TBA.")

# ---------------------------
# Sección: Datos del Evento desde Statbotics
# ---------------------------
st.header("Datos del Evento (Statbotics)")
statbotics_event_url = f"https://api.statbotics.io/v3/event/{main_event}"
statbotics_response = requests.get(statbotics_event_url)

if statbotics_response.status_code == 200:
    event_data = statbotics_response.json()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Información General")
        st.markdown(f"**Nombre:** {event_data.get('name', 'N/D')}")
        st.markdown(f"**Año:** {event_data.get('year', 'N/D')}")
        st.markdown(f"**Tipo:** {event_data.get('type', 'N/D')}")
        st.markdown(f"**Semana:** {event_data.get('week', 'N/D')}")
        st.markdown(f"**Equipos Participantes:** {event_data.get('num_teams', 'N/D')}")
    
    with col2:
        st.subheader("Fechas y Video")
        st.markdown(f"**Fecha de inicio:** {event_data.get('start_date', 'N/D')}")
        st.markdown(f"**Fecha de finalización:** {event_data.get('end_date', 'N/D')}")
        st.markdown(f"**Video:** [Ver en Twitch]({event_data.get('video', '#')})")
        st.markdown(f"**Estado:** {event_data.get('status_str', 'N/D')}")
    
    st.subheader("EPA del Evento")
    epa = event_data.get("epa", {})
    st.markdown(f"**Promedio EPA:** {epa.get('mean', 'N/D')}")
    st.markdown(f"**Desviación estándar:** {epa.get('sd', 'N/D')}")
    st.markdown(f"**Top 8:** {epa.get('top_8', 'N/D')}")
    st.markdown(f"**Top 24:** {epa.get('top_24', 'N/D')}")
    st.markdown(f"**Máximo EPA:** {epa.get('max', 'N/D')}")
else:
    st.error("Error al obtener datos del evento desde Statbotics.")

# ---------------------------
# Sección: Listado de Equipos del Regional
# ---------------------------
st.header("Listado de Equipos del Regional")

# Obtener listado de claves de equipos desde TBA
teams_keys_url = f"https://www.thebluealliance.com/api/v3/event/{main_event}/teams/keys"
teams_response = requests.get(teams_keys_url, headers=headers)

if teams_response.status_code == 200:
    team_keys = teams_response.json()
    st.markdown(f"Se encontraron **{len(team_keys)}** equipos en el regional.")
else:
    st.error("Error al obtener el listado de equipos desde TBA.")
    team_keys = []

# Lista para almacenar la información de cada equipo desde Statbotics
team_data_list = []

with st.spinner("Obteniendo información de los equipos..."):
    for team_key in team_keys:
        team_number = team_key.replace("frc", "")
        statbotics_team_url = f"https://api.statbotics.io/v3/team_event/{team_number}/{main_event}"
        team_info_response = requests.get(statbotics_team_url)
        if team_info_response.status_code == 200:
            team_info = team_info_response.json()
            team_data_list.append(team_info)
        else:
            st.warning(f"No se pudo obtener información para el equipo {team_key}")

# Mostrar la información de los equipos en una tabla con las estadísticas solicitadas
if team_data_list:
    df = pd.DataFrame(team_data_list)
    
    # Extraer estadísticas desde el diccionario "epa" -> "breakdown"
    if "epa" in df.columns:
        df['total_points'] = df['epa'].apply(lambda x: x.get("breakdown", {}).get("total_points") if isinstance(x, dict) else None)
        df['coral_l3'] = df['epa'].apply(lambda x: x.get("breakdown", {}).get("coral_l3") if isinstance(x, dict) else None)
        df['coral_l4'] = df['epa'].apply(lambda x: x.get("breakdown", {}).get("coral_l4") if isinstance(x, dict) else None)
        df['algae_points'] = df['epa'].apply(lambda x: x.get("breakdown", {}).get("total_algae_points") if isinstance(x, dict) else None)
        df['barge_points'] = df['epa'].apply(lambda x: x.get("breakdown", {}).get("barge_points") if isinstance(x, dict) else None)
        df['epa_total_mean'] = df['epa'].apply(lambda x: x.get("norm") if isinstance(x, dict) else None)
    # Seleccionar columnas de interés: número de equipo, nombre y estadísticas
    columnas = {
        'epa_total_mean': "EPA Promedio",
        'team': "Equipo",
        'team_name': "Nombre",
        'total_points': "Total Points",
        'coral_l3': "Coral L3",
        'coral_l4': "Coral L4",
        'algae_points': "Algae Points",
        'barge_points': "Barge Points",

    }
    cols_disponibles = [col for col in columnas.keys() if col in df.columns]
    if cols_disponibles:
        df_display = df[cols_disponibles].rename(columns=columnas)
    else:
        df_display = df

    # Aplicar estilos: se utiliza un fondo degradado para las columnas numéricas
    styled_df = df_display.style.background_gradient(
        cmap='YlGnBu', 
        subset=["Total Points", "Coral L3", "Coral L4", "Algae Points", "Barge Points", "EPA Promedio"]
    ).set_properties(**{'text-align': 'center'}).set_table_styles(
        [{'selector': 'th', 'props': [('text-align', 'center')]}]
    )
    
    st.dataframe(styled_df, use_container_width=True)
else:
    st.markdown("No se pudo obtener información de los equipos desde Statbotics.")
