# modules/schedule.py
import streamlit as st
import pandas as pd
from modules.database import load_schedule_from_sheets, save_schedule_to_sheets

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

DEFAULT_SCHEDULE = {
    "Monday": {"routine": "Chest & Triceps", "exercises": [
        {"name": "Bench Press", "default_sets": 3, "default_reps": 10},
        {"name": "Incline Dumbbell Press", "default_sets": 3, "default_reps": 12},
        {"name": "Tricep Pushdown", "default_sets": 3, "default_reps": 12}
    ]},
    "Tuesday": {"routine": "Back & Biceps", "exercises": [
        {"name": "Lat Pulldown", "default_sets": 3, "default_reps": 10},
        {"name": "Seated Cable Row", "default_sets": 3, "default_reps": 12},
        {"name": "Barbell Curl", "default_sets": 3, "default_reps": 10}
    ]},
    "Wednesday": {"routine": "Rest Day / Cardio", "exercises": []},
    "Thursday": {"routine": "Legs & Core", "exercises": [
        {"name": "Squat", "default_sets": 4, "default_reps": 8},
        {"name": "Leg Press", "default_sets": 3, "default_reps": 12}
    ]},
    "Friday": {"routine": "Shoulders & Arms", "exercises": [
        {"name": "Overhead Press", "default_sets": 3, "default_reps": 10},
        {"name": "Lateral Raise", "default_sets": 4, "default_reps": 15}
    ]},
    "Saturday": {"routine": "Active Recovery", "exercises": []},
    "Sunday": {"routine": "Rest Day", "exercises": []},
}

def get_current_schedule():
    """Loads schedule from Google Sheets, or falls back to defaults."""
    df_sched = load_schedule_from_sheets()
    schedule_dict = {}
    
    if df_sched is not None and not df_sched.empty and "Day" in df_sched.columns:
        for day in DAYS_OF_WEEK:
            day_rows = df_sched[df_sched["Day"] == day]
            if not day_rows.empty:
                routine = day_rows.iloc[0]["Routine"]
                ex_list = []
                for _, row in day_rows.iterrows():
                    if pd.notna(row["Exercise"]) and str(row["Exercise"]).strip():
                        ex_list.append({
                            "name": str(row["Exercise"]).strip(),
                            "default_sets": int(row["TargetSets"]) if pd.notna(row["TargetSets"]) else 3,
                            "default_reps": int(row["TargetReps"]) if pd.notna(row["TargetReps"]) else 10
                        })
                schedule_dict[day] = {"routine": str(routine), "exercises": ex_list}
            else:
                schedule_dict[day] = DEFAULT_SCHEDULE[day]
        return schedule_dict
    else:
        return DEFAULT_SCHEDULE

def render_schedule_tab():
    """Renders the persistent weekly planner UI."""
    st.subheader("📅 Weekly Workout Planner")
    st.caption("Customized plans save directly to your Google Sheet.")
    
    current_schedule = get_current_schedule()
    selected_edit_day = st.selectbox("Choose Day to Edit", DAYS_OF_WEEK)
    day_data = current_schedule[selected_edit_day]
    
    st.markdown(f"### Edit Plan for **{selected_edit_day}**")
    new_routine_name = st.text_input("Routine Name / Focus", value=day_data["routine"])
    
    updated_exercises = []
    st.markdown("#### Scheduled Exercises")
    
    for idx, ex in enumerate(day_data["exercises"]):
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            name = st.text_input(f"Exercise #{idx+1}", value=ex["name"], key=f"ex_name_{selected_edit_day}_{idx}")
        with c2:
            sets = st.number_input("Sets", min_value=1, max_value=10, value=ex.get("default_sets", 3), key=f"ex_sets_{selected_edit_day}_{idx}")
        with c3:
            reps = st.number_input("Reps", min_value=1, max_value=100, value=ex.get("default_reps", 10), key=f"ex_reps_{selected_edit_day}_{idx}")
        
        if name.strip():
            updated_exercises.append({"name": name.strip(), "default_sets": int(sets), "default_reps": int(reps)})

    with st.expander("➕ Add New Exercise to Day"):
        new_name = st.text_input("New Exercise Name", key=f"new_ex_{selected_edit_day}")
        col_s, col_r = st.columns(2)
        with col_s:
            new_s = st.number_input("Default Sets", min_value=1, max_value=10, value=3, key=f"new_s_{selected_edit_day}")
        with col_r:
            new_r = st.number_input("Default Reps", min_value=1, max_value=100, value=10, key=f"new_r_{selected_edit_day}")
        
        if st.button("Add Exercise Slot"):
            if new_name.strip():
                updated_exercises.append({"name": new_name.strip(), "default_sets": int(new_s), "default_reps": int(new_r)})

    if st.button(f"💾 Save Schedule for {selected_edit_day}", type="primary", use_container_width=True):
        current_schedule[selected_edit_day] = {
            "routine": new_routine_name.strip(),
            "exercises": updated_exercises
        }
        
        # Build DataFrame to write to Google Sheets
        rows = []
        for day_name in DAYS_OF_WEEK:
            d_info = current_schedule[day_name]
            if d_info["exercises"]:
                for ex in d_info["exercises"]:
                    rows.append({
                        "Day": day_name,
                        "Routine": d_info["routine"],
                        "Exercise": ex["name"],
                        "TargetSets": ex["default_sets"],
                        "TargetReps": ex["default_reps"]
                    })
            else:
                rows.append({
                    "Day": day_name,
                    "Routine": d_info["routine"],
                    "Exercise": "",
                    "TargetSets": "",
                    "TargetReps": ""
                })
        
        schedule_df = pd.DataFrame(rows)
        save_schedule_to_sheets(schedule_df)
        st.success(f"Saved {selected_edit_day}'s plan permanently to Google Sheets!")
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Your Current Weekly Plan")
    for day in DAYS_OF_WEEK:
        plan = current_schedule[day]
        if plan["exercises"]:
            ex_summary = ", ".join([f"{e['name']} ({e['default_sets']}x{e['default_reps']})" for e in plan["exercises"]])
        else:
            ex_summary = "No exercises planned"
        st.markdown(f"**{day}** ({plan['routine']}): *{ex_summary}*")
