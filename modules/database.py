# modules/database.py
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """Reads fitness logs from the default Sheet1."""
    try:
        df = conn.read(worksheet="Sheet1", ttl="0s")
        df = df.dropna(how="all")
        if df.empty:
            return pd.DataFrame(columns=["Date", "Category", "Item", "Value", "Notes"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Date", "Category", "Item", "Value", "Notes"])

def append_entry(date_str, category, item, value, notes):
    """Appends a new log entry to Sheet1."""
    existing_df = load_data()
    new_row = pd.DataFrame([{
        "Date": date_str,
        "Category": category,
        "Item": item,
        "Value": float(value),
        "Notes": notes
    }])
    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    conn.update(worksheet="Sheet1", data=updated_df)
    st.cache_data.clear()

def load_schedule_from_sheets():
    """Loads weekly schedule from the 'Schedule' worksheet in Google Sheets."""
    try:
        df_sched = conn.read(worksheet="Schedule", ttl="0s")
        df_sched = df_sched.dropna(how="all")
        if df_sched.empty:
            return None
        return df_sched
    except Exception:
        return None

def save_schedule_to_sheets(schedule_df):
    """Overwrites the 'Schedule' worksheet with the updated schedule DataFrame."""
    conn.update(worksheet="Schedule", data=schedule_df)
    st.cache_data.clear()
