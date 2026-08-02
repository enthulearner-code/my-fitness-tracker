# modules/progress.py
import streamlit as st
import pandas as pd
import re

def parse_volume_from_notes(notes_str):
    """
    Parses set breakdowns in notes (e.g., '[Day 1] [S1: 10r @ 50kg | S2: 10r @ 50kg]')
    and calculates total volume (weight * reps across all sets).
    Fallback: returns 0 if parsing fails.
    """
    if not isinstance(notes_str, str):
        return 0.0
    
    pattern = r"(\d+)\s*r\s*@\s*([\d\.]+)\s*kg"
    matches = re.findall(pattern, notes_str, re.IGNORECASE)
    
    total_volume = 0.0
    for reps, weight in matches:
        try:
            total_volume += int(reps) * float(weight)
        except ValueError:
            continue
            
    return total_volume

def extract_program_day(notes_str):
    """Extracts '[Day X]' from the notes column if available."""
    if not isinstance(notes_str, str):
        return "Uncategorized"
    match = re.search(r"\[(Day\s*\d+)\]", notes_str, re.IGNORECASE)
    if match:
        return match.group(1).title()
    return "Uncategorized"

def render_progress_tab():
    """Renders the overall volume progress and week-over-week comparisons."""
    st.subheader("📊 Session Volume & Progress Tracker")
    st.caption("Tracks total volume lifted (Weight × Reps) per workout session.")

    from modules.database import load_data
    df_all = load_data()
    
    if df_all.empty or "Category" not in df_all.columns:
        st.info("No workout entries logged yet. Start logging workouts to track your volume progression!")
        return

    # Filter for Workout category
    df_workouts = df_all[df_all["Category"] == "Workout"].copy()
    
    if df_workouts.empty:
        st.info("No workout entries logged yet.")
        return

    # Calculate total volume for each logged set/exercise entry
    df_workouts["Volume"] = df_workouts["Notes"].apply(parse_volume_from_notes)
    df_workouts["ProgramDay"] = df_workouts["Notes"].apply(extract_program_day)
    df_workouts["Date"] = pd.to_datetime(df_workouts["Date"])

    # Aggregate total volume per Day & ProgramDay
    daily_summary = (
        df_workouts.groupby(["Date", "ProgramDay"], as_index=False)["Volume"]
        .sum()
        .sort_values("Date")
    )

    st.markdown("### 📈 Total Volume Over Time")
    
    c_f1, c_f2 = st.columns([2, 1])
    with c_f1:
        available_days = sorted(list(daily_summary["ProgramDay"].unique()))
        day_filter = st.selectbox(
            "Filter by Program Day", 
            ["All Days"] + available_days
        )
    with c_f2:
        chart_style = st.radio("Chart Style", ["Line Chart", "Area Chart"], horizontal=True)
    
    filtered_df = daily_summary.copy()
    if day_filter != "All Days":
        filtered_df = filtered_df[filtered_df["ProgramDay"] == day_filter]

    if not filtered_df.empty:
        # Pivot table cleanly aggregates values and prevents collisions
        chart_df = filtered_df.pivot_table(
            index="Date", 
            columns="ProgramDay", 
            values="Volume", 
            aggfunc="sum"
        ).fillna(0)
        
        if chart_style == "Line Chart":
            st.line_chart(chart_df, use_container_width=True)
        else:
            st.area_chart(chart_df, use_container_width=True)
        
        # Session Comparisons
        st.markdown("---")
        st.subheader("⚔️ Session Comparisons")
        
        if len(filtered_df) >= 2:
            latest_session = filtered_df.iloc[-1]
            previous_session = filtered_df.iloc[-2]
            
            vol_diff = latest_session["Volume"] - previous_session["Volume"]
            pct_change = (vol_diff / previous_session["Volume"] * 100) if previous_session["Volume"] > 0 else 0
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(
                    label=f"Latest Session ({latest_session['Date'].strftime('%Y-%m-%d')})", 
                    value=f"{latest_session['Volume']:,.0f} kg"
                )
            with c2:
                st.metric(
                    label=f"Previous Session ({previous_session['Date'].strftime('%Y-%m-%d')})", 
                    value=f"{previous_session['Volume']:,.0f} kg"
                )
            with c3:
                st.metric(
                    label="Volume Change", 
                    value=f"{vol_diff:+,.0f} kg", 
                    delta=f"{pct_change:+.1f}%"
                )
        
        st.markdown("#### 📋 History Breakdown")
        display_df = filtered_df.copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
        display_df["Volume (kg)"] = display_df["Volume"].apply(lambda x: f"{x:,.1f} kg")
        st.dataframe(
            display_df[["Date", "ProgramDay", "Volume (kg)"]], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.warning(f"No volume data recorded for {day_filter}.")
