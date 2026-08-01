# modules/database.py
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """Reads all rows from Google Sheets cleanly."""
    try:
        df = conn.read(ttl="0s")
        df = df.dropna(how="all")
        if df.empty:
            return pd.DataFrame(columns=["Date", "Category", "Item", "Value", "Notes"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Date", "Category", "Item", "Value", "Notes"])

def append_entry(date_str, category, item, value, notes):
    """Appends a single entry row to Google Sheets."""
    existing_df = load_data()
    new_row = pd.DataFrame([{
        "Date": date_str,
        "Category": category,
        "Item": item,
        "Value": float(value),
        "Notes": notes
    }])
    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    conn.update(data=updated_df)
    st.cache_data.clear()
