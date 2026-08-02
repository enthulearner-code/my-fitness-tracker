import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

def render_attendance_tab(conn):
    st.header("🗓️ Gym Attendance")
    st.write("Automated from your main workout logs.")

    # 1. Fetch Existing Workout Data (Directly from your main log)
    try:
        # IMPORTANT: Change "Workouts" to the actual name of your Google Sheet tab
        # where you log your daily exercises.
        df = conn.read(worksheet="Workouts", ttl=0)
        df = df.dropna(how="all") 
    except Exception as e:
        st.error("Could not read from Google Sheets. Check your worksheet name.")
        return

    # Ensure there is data and a Date column exists
    if df.empty or "Date" not in df.columns:
        st.info("No workout data found yet. Go log a workout to see it here!")
        return

    # 2. Extract Unique Dates
    # Since you might have 10 rows for a single day (one for each exercise),
    # we only want to highlight the date once on the calendar.
    df["Date"] = pd.to_datetime(df["Date"])
    unique_dates = df["Date"].dt.strftime("%Y-%m-%d").unique()

    # 3. Simple Calendar Visualization
    calendar_events = []
    
    highlight_style = {
        "backgroundColor": "#28a745", # Green highlight
        "borderColor": "#28a745",
        "color": "white",
        "display": "background" 
    }

    # Create an event for every unique date you worked out
    for date_str in unique_dates:
        calendar_events.append({
            "start": date_str,
            "end": date_str,
            **highlight_style
        })

    # Calendar Component Configuration
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth"
        },
        "initialView": "dayGridMonth",
    }

    # Render the Calendar
    calendar(events=calendar_events, options=calendar_options)
