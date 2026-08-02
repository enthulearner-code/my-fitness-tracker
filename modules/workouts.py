# modules/workouts.py
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.database import append_entry, load_data
from modules.schedule import get_current_schedule, DAYS_OF_WEEK

def render_workouts_tab():
    """Renders set-by-set workout logging linked to flexible Day 1-7 schedule."""
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        selected_date = st.date_input("Workout Date", datetime.now(), key="log_date")
    
    current_schedule = get_current_schedule()
    
    with col_d2:
        selected_program_day = st.selectbox("Select Program Day", DAYS_OF_WEEK, key="program_day_select")
    
    today_plan = current_schedule.get(selected_program_day, {"routine": "Custom", "exercises": []})
    
    st.markdown(f"""
        <div style="background-color: #F8FAFC; border-left: 4px solid #2563EB; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;">
            <span style="font-weight: 700; color: #1E293B;">Selected Routine ({selected_program_day}):</span> 
            <span style="color: #2563EB; font-weight: 600;">{today_plan['routine']}</span>
        </div>
    """, unsafe_allow_html=True)
    
    scheduled_names = [e["name"] for e in today_plan["exercises"]] if today_plan["exercises"] else []
    
    st.subheader("🏋️ Log Exercise Sets")
    
    log_type = st.radio("Choose Exercise Source", ["From Schedule", "Custom Exercise"], horizontal=True)
    
    exercise_name = ""
    num_sets = 3
    target_reps = 10
    
    if log_type == "From Schedule" and scheduled_names:
        selected_ex_obj = st.selectbox(
            "Select Scheduled Exercise", 
            today_plan["exercises"], 
            format_func=lambda x: f"{x['name']} (Target: {x['default_sets']}x{x['default_reps']})"
        )
        exercise_name = selected_ex_obj["name"]
        num_sets = selected_ex_obj.get("default_sets", 3)
        target_reps = selected_ex_obj.get("default_reps", 10)
    else:
        exercise_name = st.text_input("Exercise Name", placeholder="e.g. Incline Dumbbell Press")
        num_sets = st.number_input("Number of Sets", min_value=1, max_value=10, value=3)

    if exercise_name.strip():
        st.markdown(f"#### Log Details for **{exercise_name}**")
        
        set_data = []
        for s in range(1, num_sets + 1):
            st.caption(f"**Set {s}**")
            col_w, col_r = st.columns(2)
            with col_w:
                w = st.number_input(f"Weight (kg)", min_value=0.0, step=0.5, key=f"set_w_{exercise_name}_{s}")
            with col_r:
                r = st.number_input(f"Reps", min_value=1, max_value=100, value=target_reps, key=f"set_r_{exercise_name}_{s}")
            set_data.append({"set": s, "weight": w, "reps": r})
            
        workout_notes = st.text_area("Notes (Optional)", placeholder="Rest time, RPE, machine settings...", height=65)
        
        if st.button(f"Save All Sets for {exercise_name}", type="primary", use_container_width=True):
            max_weight = max([s["weight"] for s in set_data]) if set_data else 0.0
            sets_summary = " | ".join([f"S{s['set']}: {s['reps']}r @ {s['weight']}kg" for s in set_data])
            full_notes = f"[{selected_program_day}] [{sets_summary}] {workout_notes}".strip()
            
            if max_weight > 0:
                append_entry(
                    date_str=selected_date.strftime("%Y-%m-%d"),
                    category="Workout",
                    item=exercise_name.strip().title(),
                    value=max_weight,
                    notes=full_notes
                )
                st.success(f"Logged {exercise_name} successfully for {selected_program_day}!")
                st.rerun()
            else:
                st.error("Please enter a weight greater than 0 for at least one set.")

    st.markdown("---")
    st.subheader("📈 Exercise Progression")
    
    df_all = load_data()
    df_workouts = df_all[df_all["Category"] == "Workout"] if not df_all.empty else pd.DataFrame()
    
    if not df_workouts.empty and "Item" in df_workouts.columns:
        exercises = df_workouts["Item"].dropna().unique()
        selected_ex = st.selectbox("Select Exercise to View Progression", exercises)
        
        chart_df = df_workouts[df_workouts["Item"] == selected_ex].copy()
        chart_df["Value"] = pd.to_numeric(chart_df["Value"], errors="coerce")
        chart_df = chart_df.sort_values("Date")
        
        if not chart_df.empty:
            st.line_chart(chart_df.set_index("Date")["Value"])
            st.caption("Max Weight (kg) per session & Set Breakdown:")
            st.dataframe(
                chart_df[["Date", "Value", "Notes"]].rename(columns={"Value": "Top Weight (kg)", "Notes": "Set Log & Notes"}),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No workout entries logged yet.")
