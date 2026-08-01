# modules/workouts.py
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.database import append_entry, load_data
from modules.schedule import init_schedule

def render_workouts_tab():
    """Renders the workout logging & progression tab."""
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        selected_date = st.date_input("Workout Date", datetime.now(), key="log_date")
    
    init_schedule()
    day_name = selected_date.strftime("%A")
    today_plan = st.session_state.workout_schedule.get(day_name, {"routine": "Custom", "exercises": []})
    
    st.markdown(f"""
        <div style="background-color: #F8FAFC; border-left: 4px solid #2563EB; padding: 12px 16px; border-radius: 8px; margin-bottom: 12px;">
            <span style="font-weight: 700; color: #1E293B;">{day_name}'s Plan:</span> 
            <span style="color: #2563EB; font-weight: 600;">{today_plan['routine']}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # 1. Quick Log Scheduled Exercises
    if today_plan["exercises"]:
        st.subheader("⚡ Quick Log Planned Exercises")
        
        with st.form("quick_log_form", clear_on_submit=True):
            chosen_ex = st.selectbox("Select Scheduled Exercise", today_plan["exercises"])
            
            c1, c2 = st.columns(2)
            with c1:
                weight_val = st.number_input("Weight (kg)", min_value=0.0, step=0.5, key="q_w")
            with c2:
                reps_sets_val = st.text_input("Sets & Reps", placeholder="e.g. 3x10", key="q_s")
                
            q_notes = st.text_area("Notes (RPE, rest, form)", height=65, key="q_n")
            
            submit_quick = st.form_submit_button("Log Planned Exercise", type="primary", use_container_width=True)
            
            if submit_quick:
                if weight_val > 0:
                    note_str = f"[{reps_sets_val}] {q_notes}".strip() if reps_sets_val else q_notes
                    append_entry(selected_date.strftime("%Y-%m-%d"), "Workout", chosen_ex, weight_val, note_str)
                    st.success(f"Logged {chosen_ex}: {weight_val} kg")
                else:
                    st.error("Please enter a weight greater than 0.")

    st.markdown("---")
    
    # 2. Add Custom Exercise
    with st.expander("➕ Add Custom / Unscheduled Exercise"):
        with st.form("custom_ex_form", clear_on_submit=True):
            c_ex = st.text_input("Exercise Name", placeholder="e.g. Dumbbell Flyes")
            c3, c4 = st.columns(2)
            with c3:
                c_weight = st.number_input("Weight (kg)", min_value=0.0, step=0.5)
            with c4:
                c_sets = st.text_input("Sets & Reps", placeholder="e.g. 4x8")
            c_notes = st.text_input("Notes")
            
            submit_custom = st.form_submit_button("Log Custom Exercise", use_container_width=True)
            if submit_custom:
                if c_ex and c_weight > 0:
                    c_note_str = f"[{c_sets}] {c_notes}".strip() if c_sets else c_notes
                    append_entry(selected_date.strftime("%Y-%m-%d"), "Workout", c_ex.strip().title(), c_weight, c_note_str)
                    st.success(f"Logged {c_ex}: {c_weight} kg")
                else:
                    st.error("Enter exercise name and weight.")

    st.markdown("---")
    st.subheader("📈 Exercise Progression")
    
    df_all = load_data()
    df_workouts = df_all[df_all["Category"] == "Workout"] if not df_all.empty else pd.DataFrame()
    
    if not df_workouts.empty and "Item" in df_workouts.columns:
        exercises = df_workouts["Item"].dropna().unique()
        selected_ex = st.selectbox("Select Exercise to View History", exercises)
        
        chart_df = df_workouts[df_workouts["Item"] == selected_ex].copy()
        chart_df["Value"] = pd.to_numeric(chart_df["Value"], errors="coerce")
        chart_df = chart_df.sort_values("Date")
        
        if not chart_df.empty:
            st.line_chart(chart_df.set_index("Date")["Value"])
            st.dataframe(
                chart_df[["Date", "Value", "Notes"]].rename(columns={"Value": "Weight (kg)"}),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No workout entries logged yet.")
