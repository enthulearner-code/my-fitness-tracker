import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Page Configuration
st.set_page_config(page_title="Personal Fitness Tracker", page_icon="🏋️‍♂️", layout="centered")

DATA_FILE = "fitness_data.csv"

# Function to load existing data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Category", "Item", "Value", "Notes"])

# Function to save new entry
def save_entry(date, category, item, value, notes):
    df = load_data()
    new_data = pd.DataFrame([{
        "Date": date,
        "Category": category,
        "Item": item,
        "Value": float(value),
        "Notes": notes
    }])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

st.title("🏋️‍♂️ Fitness & Body Tracker")

# Sidebar navigation
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
            save_entry(entry_date.strftime("%Y-%m-%d"), category, item, value, notes)
            st.success(f"Saved {item}: {value}")
        else:
            st.error("Please provide valid details before saving.")

# --- TAB 2: PROGRESS CHARTS ---
elif option == "Progress Charts":
    st.header("📈 Progress Dashboard")
    df = load_data()
    
    if not df.empty:
        category_filter = st.selectbox("Select Category", df["Category"].unique())
        filtered_df = df[df["Category"] == category_filter]
        
        if not filtered_df.empty:
            item_filter = st.selectbox("Select Item / Exercise", filtered_df["Item"].unique())
            chart_df = filtered_df[filtered_df["Item"] == item_filter].sort_values("Date")
            
            if not chart_df.empty:
                st.subheader(f"Trend for {item_filter}")
                st.line_chart(chart_df.set_index("Date")["Value"])
            else:
                st.info("No data available for this item.")
    else:
        st.info("No entries logged yet. Start by logging some entries!")

# --- TAB 3: VIEW RAW DATA ---
elif option == "View Raw Data":
    st.header("📋 All Logs")
    df = load_data()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Download option for CSV backup
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name="my_fitness_data_backup.csv",
            mime="text/csv",
        )
    else:
        st.info("No data found.")
