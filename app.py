import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Page Configuration
st.set_page_config(page_title="Personal Fitness Tracker", page_icon="🏋️‍♂️", layout="centered")

# Initialize Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to load data safely
def load_data():
    try:
        df = conn.read(ttl="0s") # ttl=0 disables caching so new entries show immediately
        # Remove empty rows if any
        df = df.dropna(how="all")
        return df
    except Exception as e:
        return pd.DataFrame(columns=["Date", "Category", "Item", "Value", "Notes"])

st.title("🏋️‍♂️ Fitness & Body Tracker")

# Sidebar Navigation
option = st.sidebar.radio("Navigation", ["Log Entry", "Progress Charts", "View Raw Data"])

# --- TAB 1: LOG ENTRY ---
if option == "Log Entry":
    st.header("📝 New Entry")
    
    entry_date = st.date_input("Date", datetime.now())
    category = st.selectbox("Category", ["Body Measurement", "Workout"])
    
    if category == "Body Measurement":
        item = st.selectbox("Metric", ["Weight (kg)", "Chest (cm)", "Waist (cm)", "Biceps (cm)", "Body Fat (%)"])
    else:
        item = st.text_input("Exercise Name (e.g., Bench Press, Squat)", placeholder="Bench Press")
        
    value = st.number_input("Value (Weight/Reps/Measurement)", min_value=0.0, step=0.5)
    notes = st.text_area("Notes", placeholder="Optional details (e.g., 3 sets x 10 reps)")
    
    if st.button("Save Entry", type="primary"):
        if item and value > 0:
            existing_df = load_data()
            
            new_row = pd.DataFrame([{
                "Date": entry_date.strftime("%Y-%m-%d"),
                "Category": category,
                "Item": item,
                "Value": float(value),
                "Notes": notes
            }])
            
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            
            # Update Google Sheet
            conn.update(data=updated_df)
            st.success(f"Saved to Google Sheets: {item} = {value}")
            st.cache_data.clear()
        else:
            st.error("Please provide valid details before saving.")

# --- TAB 2: PROGRESS CHARTS ---
elif option == "Progress Charts":
    st.header("📈 Progress Dashboard")
    df = load_data()
    
    if not df.empty and "Category" in df.columns:
        category_filter = st.selectbox("Select Category", df["Category"].dropna().unique())
        filtered_df = df[df["Category"] == category_filter]
        
        if not filtered_df.empty:
            item_filter = st.selectbox("Select Item / Exercise", filtered_df["Item"].dropna().unique())
            chart_df = filtered_df[filtered_df["Item"] == item_filter].copy()
            chart_df["Value"] = pd.to_numeric(chart_df["Value"], errors="coerce")
            chart_df = chart_df.sort_values("Date")
            
            if not chart_df.empty:
                st.subheader(f"Trend for {item_filter}")
                st.line_chart(chart_df.set_index("Date")["Value"])
            else:
                st.info("No numerical data available to chart.")
    else:
        st.info("No entries logged yet in Google Sheets.")

# --- TAB 3: VIEW RAW DATA ---
elif option == "View Raw Data":
    st.header("📋 Google Sheets Live Data")
    df = load_data()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Google Sheet is currently empty.")
