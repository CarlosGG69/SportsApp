import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- Auth with Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)

client = gspread.authorize(creds)

# --- Open sheet ---
SHEET_NAME = "Database"
spreadsheet = client.open(SHEET_NAME).sheet1

st.title("🏋️ My Sports Log (Google Sheets)")

# --- Form for logging ---
with st.form("log_form"):
    date = st.date_input("Date", datetime.today())
    exercise = st.text_input("Exercise")
    weight = st.number_input("Weight (kg)", min_value=0.0, step=1.0)
    reps = st.number_input("Reps", min_value=0, step=1)
    time = st.text_input("Time (e.g. 00:25:30)")
    submitted = st.form_submit_button("Save Entry")

    if submitted:
        spreadsheet.append_row([str(date), exercise, weight, reps, time])
        st.success("✅ Entry saved to Google Sheets!")

# --- Load data for analysis ---
data = spreadsheet.get_all_records()
df = pd.DataFrame(data)

st.subheader("📊 Training History")
st.dataframe(df)

if not df.empty:
    st.line_chart(df.groupby("date")["weight"].mean())
