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

    # 1. Fetch Actual Data from Google Sheets
    try:
        # Read the 'Workouts' sheet. ttl=0 bypasses cache to get live data.
        df = conn.read(worksheet="Workouts", ttl=0)
        df = df.dropna(how="all") # Clean any entirely blank rows
    except Exception as e:
        st.error(f"Could not read from Google Sheets. Error: {e}")
        return

    # Check that data exists and the required columns are present
    if df.empty or "Date" not in df.columns or "Session_Type" not in df.columns:
        st.info("No workout data found yet. Ensure your sheet has 'Date' and 'Session_Type' columns.")
        return

    # 2. Group by Date to determine the day's primary activity
    # Convert string dates to datetime objects for accurate grouping
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Group by the date string and collect all unique Session_Types for that day into a set
    daily_summary = df.groupby(df["Date"].dt.strftime("%Y-%m-%d"))["Session_Type"].apply(set).reset_index()

    # 3. Calendar Visualization
    calendar_events = []

    # Iterate through each unique date to assign colors based on the session set
    for _, row in daily_summary.iterrows():
        date_str = row["Date"]
        sessions = row["Session_Type"]
        
        # Color Logic: Weights override Cardio if you happen to do both in one day
        if "Weights" in sessions:
            bg_color = "#28a745" # Solid Green
        elif "Cardio" in sessions:
            bg_color = "#007bff" # Blue for Cardio/Rest days
        else:
            bg_color = "#6c757d" # Gray fallback if Session_Type is unrecognized
            
        calendar_events.append({
            "start": date_str,
            "end": date_str,
            "display": "background",
            "backgroundColor": bg_color,
            "borderColor": bg_color,
            "color": "white" # Keeps the calendar date number legible
        })

    # 4. Render Calendar
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today", 
            "center": "title", 
            "right": "dayGridMonth"
        },
        "initialView": "dayGridMonth"
    }

    calendar(events=calendar_events, options=calendar_options)
