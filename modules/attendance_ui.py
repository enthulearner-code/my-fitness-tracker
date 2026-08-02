import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

def render_attendance_tab(conn):
    st.header("🗓️ Gym Attendance")

    # 1. Fetch Existing Data
    try:
        # Read the sheet. ttl=0 ensures we get fresh data on load.
        df = conn.read(worksheet="Attendance", usecols=[0, 1], ttl=0)
        # Drop any completely empty rows that Google Sheets might return
        df = df.dropna(how="all") 
    except Exception as e:
        st.error("Could not read from Google Sheets. Ensure a worksheet named 'Attendance' exists with 'Date' and 'Session_Type' columns.")
        return

    # 2. Log New Session Form
    with st.form("log_attendance_form", clear_on_submit=True):
        st.subheader("Log a Workout")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_date = st.date_input("Date", date.today())
        with col2:
            session_type = st.selectbox("Session Type", ["Lifting", "Cardio", "Active Recovery", "Other"])
        
        submitted = st.form_submit_button("Log Attendance", use_container_width=True)
        
        if submitted:
            # Convert date to string to match how Pandas reads Google Sheets
            date_str = selected_date.strftime("%Y-%m-%d")
            
            # Check for duplicates to prevent multiple entries on the same day
            if not df.empty and date_str in df["Date"].astype(str).values:
                st.warning(f"You already logged a session for {date_str}!")
            else:
                # Create a new DataFrame for the new row
                new_entry = pd.DataFrame([{"Date": date_str, "Session_Type": session_type}])
                
                # Append to the existing data
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                
                # Push the updated DataFrame back to Google Sheets
                conn.update(worksheet="Attendance", data=updated_df)
                
                st.success(f"Successfully logged workout for {date_str}!")
                st.rerun()

    st.divider()

    # 3. Heatmap Visualization
    st.subheader("Consistency Tracker")
    
    if df.empty:
        st.info("No attendance data yet. Log a workout to see your heatmap!")
        return
        
    # Ensure Date column is treated as datetime objects for Altair grouping
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Assign a value of 1 for every attended day to color the heatmap
    df["Attended"] = 1 
    
    # Calculate grid coordinates (Week of Year and Day of Week)
    df["Week"] = df["Date"].dt.isocalendar().week
    df["DayName"] = df["Date"].dt.day_name()
    
    # Filter to current year to keep the chart clean and focused
    current_year = date.today().year
    df_current_year = df[df["Date"].dt.year == current_year]

    if df_current_year.empty:
        st.info(f"No attendance logged yet for {current_year}.")
        return

    # Build the Altair Chart
    heatmap = alt.Chart(df_current_year).mark_rect(rx=4, ry=4).encode(
        x=alt.X('Week:O', axis=alt.Axis(title='Week of Year', labelAngle=0)),
        y=alt.Y('DayName:O', sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], title=None),
        color=alt.Color('Attended:Q', scale=alt.Scale(scheme='greens'), legend=None), # 'greens' mimics GitHub
        tooltip=[alt.Tooltip('Date:T', format='%B %d, %Y'), 'Session_Type']
    ).properties(
        height=250
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(heatmap, use_container_width=True)
