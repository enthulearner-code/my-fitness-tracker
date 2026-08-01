# modules/workouts.py
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.database import append_entry, load_data
from modules.schedule import get_current_schedule

def calculate_1rm(weight: float, reps: int) -> float:
    """Calculates Estimated 1-Rep Max using Epley's Formula."""
    if reps <= 1:
        return weight
    return round(weight * (1 + (reps / 30.0)), 2)

def render_workouts_tab():
    """Renders workout logging & progressive overload analytics."""
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        selected_date = st.date_input("Workout Date", datetime.now(), key="log_date")
    
    day_name = selected_date.strftime("%A")
    today_plan = st.session_state.workout_schedule.get(day_name, {"routine": "Custom", "exercises": []})
    
    st.markdown(f"""
        <div style="background-color: #F8FAFC; border-left: 4px solid #2563EB; padding: 12px 16px; border-radius: 8px; margin-bottom: 12px;">
            <span style="font-weight: 700; color: #1E293B;">{day_name}'s Plan:</span> 
            <span style="color: #2563EB; font-weight: 600;">{today_plan['routine']}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # --- LOG PLANNED EXERCISE ---
    if today_plan["exercises"]:
        st.subheader("⚡ Quick Log Planned Exercise")
        
        with st.form("quick_log_form", clear_on_submit=True):
            chosen_ex = st.selectbox("Select Scheduled Exercise", today_plan["exercises"])
            
            c1, c2, c3 = st.columns(3)
            with c1:
                weight_val = st.number_input("Weight (kg)", min_value=0.0, step=0.5, key="q_w")
            with c2:
                reps_val = st.number_input("Reps", min_value=1, max_value=100, step=1, value=10, key="q_r")
            with c3:
                sets_val = st.number_input("Sets", min_value=1, max_value=20, step=1, value=3, key="q_s")
                
            q_notes = st.text_area("Notes (RPE, rest time, form)", height=65, key="q_n")
            
            # Real-time scientific metrics preview
            if weight_val > 0:
                est_1rm = calculate_1rm(weight_val, reps_val)
                total_vol = weight_val * reps_val * sets_val
                st.caption(f"📊 **Calculated 1RM:** `{est_1rm} kg` | **Volume Load:** `{total_vol} kg`")
            
            submit_quick = st.form_submit_button("Log Exercise Set", type="primary", use_container_width=True)
            
            if submit_quick:
                if weight_val > 0:
                    est_1rm = calculate_1rm(weight_val, reps_val)
                    total_vol = weight_val * reps_val * sets_val
                    formatted_notes = f"[{sets_val}x{reps_val} @ {weight_val}kg] 1RM: {est_1rm}kg | Vol: {total_vol}kg. {q_notes}".strip()
                    
                    # Store 1RM as the main numerical value for accurate linear progression tracking
                    append_entry(selected_date.strftime("%Y-%m-%d"), "Workout", chosen_ex, est_1rm, formatted_notes)
                    st.success(f"Logged {chosen_ex}! Est. 1RM: {est_1rm} kg")
                else:
                    st.error("Please enter a weight greater than 0.")

    st.markdown("---")
    
    # --- LOG CUSTOM EXERCISE ---
    with st.expander("➕ Add Custom / Unscheduled Exercise"):
        with st.form("custom_ex_form", clear_on_submit=True):
            c_ex = st.text_input("Exercise Name", placeholder="e.g. Dumbbell Flyes")
            c1, c2, c3 = st.columns(3)
            with c1:
                c_weight = st.number_input("Weight (kg)", min_value=0.0, step=0.5)
            with c2:
                c_reps = st.number_input("Reps", min_value=1, max_value=100, step=1, value=10)
            with c3:
                c_sets = st.number_input("Sets", min_value=1, max_value=20, step=1, value=3)
                
            c_notes = st.text_input("Notes")
            submit_custom = st.form_submit_button("Log Custom Exercise", use_container_width=True)
            
            if submit_custom:
                if c_ex and c_weight > 0:
                    c_1rm = calculate_1rm(c_weight, c_reps)
                    c_vol = c_weight * c_reps * c_sets
                    c_formatted = f"[{c_sets}x{c_reps} @ {c_weight}kg] 1RM: {c_1rm}kg | Vol: {c_vol}kg. {c_notes}".strip()
                    
                    append_entry(selected_date.strftime("%Y-%m-%d"), "Workout", c_ex.strip().title(), c_1rm, c_formatted)
                    st.success(f"Logged {c_ex}! Est. 1RM: {c_1rm} kg")
                else:
                    st.error("Enter exercise name and weight.")

    # --- PROGRESSIVE OVERLOAD ANALYTICS ---
    st.markdown("---")
    st.subheader("📊 Progressive Overload Trends")
    
    df_all = load_data()
    df_workouts = df_all[df_all["Category"] == "Workout"] if not df_all.empty else pd.DataFrame()
    
    if not df_workouts.empty and "Item" in df_workouts.columns:
        exercises = df_workouts["Item"].dropna().unique()
        selected_ex = st.selectbox("Select Exercise to Analyze Progress", exercises)
        
        chart_df = df_workouts[df_workouts["Item"] == selected_ex].copy()
        chart_df["Value"] = pd.to_numeric(chart_df["Value"], errors="coerce")
        chart_df = chart_df.sort_values("Date")
        
        if not chart_df.empty:
            # Highlight Peak 1RM vs Recent
            max_1rm = chart_df["Value"].max()
            latest_1rm = chart_df.iloc[-1]["Value"]
            
            metric_col1, metric_col2 = st.columns(2)
            metric_col1.metric("Latest Est. 1RM", f"{latest_1rm} kg")
            metric_col2.metric("All-Time Peak 1RM", f"{max_1rm} kg")
            
            st.caption("Estimated 1-Rep Max (Epley Formula) over time:")
            st.line_chart(chart_df.set_index("Date")["Value"])
            
            st.dataframe(
                chart_df[["Date", "Value", "Notes"]].rename(columns={"Value": "Est 1RM (kg)"}),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No workout entries logged yet.")
