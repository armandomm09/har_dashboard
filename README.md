# FRC Scouting Dashboard 🏎️🤖

Este proyecto es un **dashboard interactivo hecho con Streamlit** para analizar el desempeño de equipos durante un regional de la competencia **FIRST Robotics Competition (FRC)**.

El dashboard permite ver estadísticas, resultados de partidos y predicciones utilizando datos de **The Blue Alliance** y **Statbotics**.

---

## 🔧 Funcionalidades

### Página principal (`Home`)
- Visualización general del evento (nombre, ubicación, fechas).
- Estadísticas globales del regional (EPA promedio, desviación, top 8/24).
- Listado de equipos participantes con sus estadísticas clave:
  - Total Points
  - Coral L3 / L4
  - Algae Points
  - Barge Points
- Tabla estilizada con colores para facilitar la lectura.

### Página de Detalles de Equipo (`Team`)
- Selecciona un equipo para ver:
  - Estadísticas EPA detalladas.
  - Récord de partidos (qual/elims).
  - Tabla combinada de partidos jugados y predicciones:
    - Puntajes reales
    - Puntajes esperados
    - Resultado vs predicción
    - Estilo de fila verde/rojo (victoria/derrota) con transparencias para predicción
  - Gráfica combinada con curvas suavizadas de puntajes reales y predichos.

---

## 📦 Estructura del proyecto

# har_dashboard
