import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta

# --- Auth with Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)

client = gspread.authorize(creds)

# --- Open spreadsheets ---
weights_sheet = client.open("Database").sheet1
runs_sheet = client.open("Running Log").sheet1

# --- Initialize session state ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = timedelta(0)

# --- Navigation ---
if st.session_state.page == "home":
    st.title("🏋️🏃 Mi Entrenamiento")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏋️ Pesas", use_container_width=True):
            st.session_state.page = "weights"
            st.rerun()

    with col2:
        if st.button("🏃 Carrera", use_container_width=True):
            st.session_state.page = "runs"
            st.rerun()

# --- Pesas page ---
elif st.session_state.page == "weights":
    st.title("🏋️ Registro de Pesas")

    with st.form("weights_form"):
        date = st.date_input("Fecha", datetime.today())
        exercise = st.text_input("Ejercicio")
        weight = st.number_input("Peso (kg)", min_value=0.0, step=1.0)
        reps = st.number_input("Reps", min_value=0, step=1)
        submitted = st.form_submit_button("Guardar Pesas")

        if submitted:
            weights_sheet.append_row([str(date), exercise, weight, reps])
            st.success("✅ Guardado en Google Sheets!")

    data = pd.DataFrame(weights_sheet.get_all_records())
    if not data.empty:
        st.subheader("📊 Historial de Pesas")
        st.dataframe(data)
        st.line_chart(data.set_index("date")["weight"])

    if st.button("⬅ Volver al inicio"):
        st.session_state.page = "home"
        st.rerun()

# --- Carrera page ---
elif st.session_state.page == "runs":
    st.title("🏃 Cronómetro de Carrera")

    # Start button
    if st.session_state.start_time is None:
        if st.button("▶️ Start"):
            st.session_state.start_time = datetime.now()
            st.session_state.elapsed = timedelta(0)
            st.rerun()
    else:
        # Show elapsed time
        st.write(f"⏱ Tiempo: {datetime.now() - st.session_state.start_time + st.session_state.elapsed}")

        # Stop button
        if st.button("⏹ Stop"):
            st.session_state.elapsed = datetime.now() - st.session_state.start_time
            st.session_state.start_time = None

            # Ask for distance
            distance = st.number_input("Distancia (km)", min_value=0.0, step=0.1)
            if st.button("Guardar Carrera"):
                runs_sheet.append_row([str(datetime.today().date()), distance, str(st.session_state.elapsed)])
                st.success("✅ Carrera guardada en Google Sheets!")

    data = pd.DataFrame(runs_sheet.get_all_records())
    if not data.empty:
        st.subheader("📊 Historial de Carreras")
        st.dataframe(data)
        st.line_chart(data.set_index("date")["distance"])

    if st.button("⬅ Volver al inicio"):
        st.session_state.page = "home"
        st.rerun()
