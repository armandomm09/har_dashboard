import streamlit as st
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# ---------------------------
# Variables Principales
# ---------------------------
main_event = "2025ilch"  # Usamos el mismo evento para todo

# Configuración de la página
st.set_page_config(page_title="Detalles de Equipo - Midwest Regional", layout="wide")
st.title("Detalles de Equipos - Midwest Regional")

# Obtener la API key de TBA desde variables de entorno
TBA_API_KEY = os.getenv("TBA_API_KEY", "TU_API_KEY_AQUI")
headers = {"X-TBA-Auth-Key": TBA_API_KEY}

# ---------------------------
# Funciones en Cache para Consultas
# ---------------------------
@st.cache_data
def get_team_keys():
    url = f"https://www.thebluealliance.com/api/v3/event/{main_event}/teams/keys"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

@st.cache_data
def get_team_details(team_number):
    url = f"https://api.statbotics.io/v3/team_event/{team_number}/{main_event}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

@st.cache_data
def get_team_matches(team_number):
    # Matches jugados (resultados reales)
    url = f"https://www.thebluealliance.com/api/v3/team/frc{team_number}/event/{main_event}/matches/simple"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

@st.cache_data
def get_match_keys_for_predictions(team_number):
    # Keys de matches programados (para predicción)
    url = f"https://www.thebluealliance.com/api/v3/team/frc{team_number}/event/{main_event}/matches/keys"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

@st.cache_data
def get_match_prediction(match_key):
    # Consulta la predicción usando la key (con main_event)
    url = f"https://api.statbotics.io/v3/match/{match_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

def smooth_line(x, y):
    # Suaviza la curva usando solo valores únicos para evitar duplicados.
    unique_x, index = np.unique(x, return_index=True)
    unique_y = y[index]
    if len(unique_x) < 4:
        return x, y
    x_new = np.linspace(unique_x.min(), unique_x.max(), 300)
    spline = make_interp_spline(unique_x, unique_y, k=3)
    return x_new, spline(x_new)

# ---------------------------
# Selección y Datos del Equipo
# ---------------------------
team_keys = get_team_keys()
if team_keys:
    # Extraer número de equipo (ej. de "frc9280" a "9280")
    team_numbers = [key.replace("frc", "") for key in team_keys]
    selected_team = st.selectbox("Selecciona un equipo", team_numbers, index=0)
    team_details = get_team_details(selected_team)
    
    if team_details:
        st.header(f"Equipo: {team_details.get('team_name', 'N/D')} (frc{selected_team})")
        
        # --- Estadísticas Clave (EPA breakdown) ---
        breakdown = team_details.get("epa", {}).get("breakdown", {})
        total_points = breakdown.get("total_points", "N/D")
        coral_l3 = breakdown.get("coral_l3", "N/D")
        coral_l4 = breakdown.get("coral_l4", "N/D")
        algae_points = breakdown.get("total_algae_points", "N/D")
        barge_points = breakdown.get("barge_points", "N/D")
        
        st.subheader("Estadísticas Clave")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Points", total_points)
        with col2:
            st.metric("Coral L3", coral_l3)
        with col3:
            st.metric("Coral L4", coral_l4)
        col4, col5 = st.columns(2)
        with col4:
            st.metric("Algae Points", algae_points)
        with col5:
            st.metric("Barge Points", barge_points)
        
        # --- Récord del Equipo ---
        record_data = team_details.get("record", {})
        if record_data:
            st.subheader("Récord del Equipo")
            qual = record_data.get("qual", {})
            elim = record_data.get("elim", {})
            total = record_data.get("total", {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### Qual")
                st.markdown(f"- **Wins:** {qual.get('wins', 'N/D')}")
                st.markdown(f"- **Losses:** {qual.get('losses', 'N/D')}")
                st.markdown(f"- **Ties:** {qual.get('ties', 'N/D')}")
                st.markdown(f"- **Count:** {qual.get('count', 'N/D')}")
                st.markdown(f"- **Winrate:** {qual.get('winrate', 'N/D')}")
            with col2:
                st.markdown("#### Elim")
                st.markdown(f"- **Wins:** {elim.get('wins', 'N/D')}")
                st.markdown(f"- **Losses:** {elim.get('losses', 'N/D')}")
                st.markdown(f"- **Ties:** {elim.get('ties', 'N/D')}")
                st.markdown(f"- **Count:** {elim.get('count', 'N/D')}")
                st.markdown(f"- **Winrate:** {elim.get('winrate', 'N/D')}")
            with col3:
                st.markdown("#### Total")
                st.markdown(f"- **Wins:** {total.get('wins', 'N/D')}")
                st.markdown(f"- **Losses:** {total.get('losses', 'N/D')}")
                st.markdown(f"- **Ties:** {total.get('ties', 'N/D')}")
                st.markdown(f"- **Count:** {total.get('count', 'N/D')}")
                st.markdown(f"- **Winrate:** {total.get('winrate', 'N/D')}")
        
        with st.expander("Ver Info completa"):
            team_json = team_details.copy()
            team_json.pop("record", None)
            st.json(team_json)
        
        # ---------------------------
        # Sección: Historial de Matches (Resultados Reales y Predicciones)
        # ---------------------------
        st.header("Historial de Matches (Resultados Reales y Predicciones)")
        
        # Obtener matches reales
        matches = get_team_matches(selected_team)
        actual_data = []
        for match in matches:
            if "alliances" not in match:
                continue
            alliances = match["alliances"]
            team_key = f"frc{selected_team}"
            if team_key in alliances.get("blue", {}).get("team_keys", []):
                alliance = "Blue"
                team_score = alliances["blue"].get("score", 0)
                opp_score = alliances["red"].get("score", 0)
            elif team_key in alliances.get("red", {}).get("team_keys", []):
                alliance = "Red"
                team_score = alliances["red"].get("score", 0)
                opp_score = alliances["blue"].get("score", 0)
            else:
                continue
            outcome = "Win" if match.get("winning_alliance", "").lower() == alliance.lower() else "Loss"
            actual_data.append({
                "Match": match.get("match_number", "N/D"),
                "Alianza": alliance,
                "Team Score": team_score,
                "Opp. Score": opp_score,
                "Resultado": outcome
            })
        df_actual = pd.DataFrame(actual_data)
        
        # Obtener predicciones
        pred_keys = get_match_keys_for_predictions(selected_team)
        pred_data = []
        for key in pred_keys:
            pred = get_match_prediction(key)
            # Asegurarse de que el campo "pred" exista y tenga datos
            if "pred" not in pred or not pred["pred"]:
                continue
            team_key = f"{selected_team}"
            alliances = pred.get("alliances", {})
            if team_key in str(alliances.get("red", {}).get("team_keys", [])):
                alliance = "Red"
                team_pred_score = pred.get("pred", {}).get("red_score", None)
                opp_pred_score = pred.get("pred", {}).get("blue_score", None)
            elif team_key in str(alliances.get("blue", {}).get("team_keys", [])):
                alliance = "Blue"
                team_pred_score = pred.get("pred", {}).get("blue_score", None)
                opp_pred_score = pred.get("pred", {}).get("red_score", None)
            else:
                continue
            predicted_winner = pred.get("pred", {}).get("winner", "").capitalize()
            pred_outcome = "Win" if predicted_winner == alliance else "Loss"
            pred_data.append({
                "Match": pred.get("match_number", "N/D"),
                "Predicted Score": team_pred_score,
                "Predicted Opp Score": opp_pred_score,
                "Predicted Outcome": pred_outcome
            })
        df_pred = pd.DataFrame(pred_data)
        # Si no hay predicciones, crear un DataFrame vacío con las columnas necesarias
        if df_pred.empty:
            df_pred = pd.DataFrame(columns=["Match", "Predicted Score", "Predicted Opp Score", "Predicted Outcome"])
        
        # Combinar en una misma tabla (merge por "Match")
        if not df_actual.empty:
            df_combined = pd.merge(df_actual, df_pred, on="Match", how="left")
        else:
            df_combined = df_pred.copy()
        
        # Reordenar columnas para visualización
        cols_orden = ["Match", "Alianza", "Team Score", "Opp. Score", "Resultado", "Predicted Score", "Predicted Opp Score", "Predicted Outcome"]
        df_combined = df_combined.reindex(columns=cols_orden)
        
        # Función de estilo para colorear filas según resultados reales y predicciones
        def highlight_rows(row):
            style = []
            # Para las primeras 5 columnas (resultados reales)
            if pd.notnull(row.get("Resultado")):
                if row["Resultado"] == "Win":
                    style += ["background-color: rgba(144,238,144, 0.5)"] * 5
                else:
                    style += ["background-color: rgba(255,99,71, 0.5)"] * 5
            else:
                style += [""] * 5
            # Para las 3 columnas de predicción
            if pd.notnull(row.get("Predicted Outcome")):
                if row["Predicted Outcome"] == "Win":
                    style += ["background-color: rgba(144,238,144, 0.3)"] * 3
                else:
                    style += ["background-color: rgba(255,99,71, 0.3)"] * 3
            else:
                style += [""] * 3
            return style
        
        st.dataframe(df_combined.style.apply(highlight_rows, axis=1), use_container_width=True)
        
        # ---------------------------
        # Gráfico Combinado: Resultados Reales y Predicciones
        # ---------------------------
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Datos reales
        if not df_actual.empty:
            df_actual.sort_values("Match", inplace=True)
            x_actual = df_actual["Match"].astype(float).values
            y_actual = df_actual["Team Score"].astype(float).values
            x_a_smooth, y_a_smooth = smooth_line(x_actual, y_actual)
            ax.plot(x_a_smooth, y_a_smooth, label="Resultados Reales", color="blue", alpha=0.8)
            colors_actual = ["green" if res == "Win" else "red" for res in df_actual["Resultado"]]
            ax.scatter(x_actual, y_actual, c=colors_actual, s=100, edgecolors="k", zorder=5)
        
        # Datos de predicción
        if not df_pred.empty:
            df_pred.sort_values("Match", inplace=True)
            x_pred = df_pred["Match"].astype(float).values
            y_pred = df_pred["Predicted Score"].astype(float).values
            x_p_smooth, y_p_smooth = smooth_line(x_pred, y_pred)
            ax.plot(x_p_smooth, y_p_smooth, label="Predicción", color="orange", alpha=0.6, linestyle="--")
            colors_pred = ["green" if res == "Win" else "red" for res in df_pred["Predicted Outcome"]]
            ax.scatter(x_pred, y_pred, c=colors_pred, s=100, edgecolors="k", alpha=0.6, zorder=5)
        
        ax.set_title("Puntajes por Match (Reales y Predicción)")
        ax.set_xlabel("Match")
        ax.set_ylabel("Puntaje")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend()
        st.pyplot(fig)
        
    else:
        st.error("No se pudo obtener la información del equipo.")
else:
    st.error("No se pudo obtener la lista de equipos desde TBA.")
