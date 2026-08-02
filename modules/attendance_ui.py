import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

def render_attendance_tab(conn):
    st.header("🗓️ Gym Attendance")
    
    # --- LEGEND ---
    st.markdown("""
    **Legend:** 
    🟢 **Weights** (Heavy training days) | 🔵 **Cardio** (Active recovery/treadmill)
    """)
    st.divider()

    # 1. MOCK DATA: Now including 'Session_Type'
    mock_data = {
        "Date": [
            "2026-07-01", "2026-07-02", "2026-07-04", "2026-07-06", 
            "2026-07-08", "2026-07-09", "2026-07-11", "2026-07-13",
            "2026-07-15", "2026-07-16", "2026-07-18" 
        ],
        "Exercise": [
            "Squat", "Treadmill", "Bench Press", "Deadlift", 
            "Overhead Press", "Treadmill", "Squat", "Bench Press",
            "Barbell Row", "Cycling", "Deadlift"
        ],
        "Session_Type": [
            "Weights", "Cardio", "Weights", "Weights", 
            "Weights", "Cardio", "Weights", "Weights",
            "Weights", "Cardio", "Weights"
        ]
    }
    
    df = pd.DataFrame(mock_data)

    # --- TO USE YOUR REAL DATA LATER ---
    # df = conn.read(worksheet="Workouts", ttl=0).dropna(how="all")
    # -----------------------------------

    if df.empty or "Date" not in df.columns or "Session_Type" not in df.columns:
        st.info("No workout data found yet. Ensure your sheet has 'Date' and 'Session_Type'.")
        return

    # 2. Group by Date to determine the day's primary activity
    df["Date"] = pd.to_datetime(df["Date"])
    
    # This creates a DataFrame where each date has a list of the unique Session_Types logged that day
    # e.g., 2026-07-01: ['Weights'] | 2026-07-02: ['Cardio']
    daily_summary = df.groupby(df["Date"].dt.strftime("%Y-%m-%d"))["Session_Type"].apply(set).reset_index()

    # 3. Calendar Visualization
    calendar_events = []

    # Iterate through each unique date to assign colors
    for _, row in daily_summary.iterrows():
        date_str = row["Date"]
        sessions = row["Session_Type"]
        
        # Color Logic: Weights override Cardio if you do both in one day
        if "Weights" in sessions:
            bg_color = "#28a745" # Solid Green
        elif "Cardio" in sessions:
            bg_color = "#007bff" # Blue for Cardio/Rest days
        else:
            bg_color = "#6c757d" # Gray fallback
            
        calendar_events.append({
            "start": date_str,
            "end": date_str,
            "display": "background",
            "backgroundColor": bg_color,
            "borderColor": bg_color,
            "color": "white"
        })

    # 4. Render Calendar
    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "initialView": "dayGridMonth",
        "initialDate": "2026-07-01" # Starts on July for this mockup
    }

    calendar(events=calendar_events, options=calendar_options)
