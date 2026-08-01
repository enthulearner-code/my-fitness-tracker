# modules/schedule.py
import streamlit as st

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def init_schedule():
    """Initializes default schedule in session state if missing."""
    if "workout_schedule" not in st.session_state:
        st.session_state.workout_schedule = {
            "Monday": {
                "routine": "Chest & Triceps", 
                "exercises": [
                    {"name": "Bench Press", "default_sets": 3, "default_reps": 10},
                    {"name": "Incline Dumbbell Press", "default_sets": 3, "default_reps": 12},
                    {"name": "Tricep Pushdown", "default_sets": 3, "default_reps": 12}
                ]
            },
            "Tuesday": {
                "routine": "Back & Biceps", 
                "exercises": [
                    {"name": "Lat Pulldown", "default_sets": 3, "default_reps": 10},
                    {"name": "Seated Cable Row", "default_sets": 3, "default_reps": 12},
                    {"name": "Barbell Curl", "default_sets": 3, "default_reps": 10}
                ]
            },
            "Wednesday": {"routine": "Rest Day / Cardio", "exercises": []},
            "Thursday": {
                "routine": "Legs & Core", 
                "exercises": [
                    {"name": "Squat", "default_sets": 4, "default_reps": 8},
                    {"name": "Leg Press", "default_sets": 3, "default_reps": 12}
                ]
            },
            "Friday": {
                "routine": "Shoulders & Arms", 
                "exercises": [
                    {"name": "Overhead Press", "default_sets": 3, "default_reps": 10},
                    {"name": "Lateral Raise", "default_sets": 4, "default_reps": 15}
                ]
            },
            "Saturday": {"routine": "Active Recovery", "exercises": []},
            "Sunday": {"routine": "Rest Day", "exercises": []},
        }

def render_schedule_tab():
    """Renders the weekly planner UI."""
    st.subheader("📅 Weekly Workout Planner")
    st.caption("Customize your daily routine and target sets/reps below:")
    
    init_schedule()
    selected_edit_day = st.selectbox("Choose Day to Edit", DAYS_OF_WEEK)
    current_day_data = st.session_state.workout_schedule[selected_edit_day]
    
    st.markdown(f"### Edit Plan for **{selected_edit_day}**")
    
    new_routine_name = st.text_input("Routine Name / Focus", value=current_day_data["routine"])
    
    st.markdown("#### Scheduled Exercises")
    
    # Existing exercises manager
    updated_exercises = []
    for idx, ex in enumerate(current_day_data["exercises"]):
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            name = st.text_input(f"Exercise #{idx+1}", value=ex["name"], key=f"ex_name_{selected_edit_day}_{idx}")
        with c2:
            sets = st.number_input("Sets", min_value=1, max_value=10, value=ex.get("default_sets", 3), key=f"ex_sets_{selected_edit_day}_{idx}")
        with c3:
            reps = st.number_input("Reps", min_value=1, max_value=100, value=ex.get("default_reps", 10), key=f"ex_reps_{selected_edit_day}_{idx}")
        
        if name.strip():
            updated_exercises.append({"name": name.strip(), "default_sets": int(sets), "default_reps": int(reps)})

    # Add new exercise slot
    with st.expander("➕ Add New Exercise to Day"):
        new_name = st.text_input("New Exercise Name", key=f"new_ex_{selected_edit_day}")
        col_s, col_r = st.columns(2)
        with col_s:
            new_s = st.number_input("Default Sets", min_value=1, max_value=10, value=3, key=f"new_s_{selected_edit_day}")
        with col_r:
            new_r = st.number_input("Default Reps", min_value=1, max_value=100, value=10, key=f"new_r_{selected_edit_day}")
        
        if st.button("Add to Schedule"):
            if new_name.strip():
                updated_exercises.append({"name": new_name.strip(), "default_sets": int(new_s), "default_reps": int(new_r)})
                st.rerun()

    if st.button(f"Save Schedule for {selected_edit_day}", type="primary", use_container_width=True):
        st.session_state.workout_schedule[selected_edit_day] = {
            "routine": new_routine_name.strip(),
            "exercises": updated_exercises
        }
        st.success(f"Saved plan for {selected_edit_day}!")

    st.markdown("---")
    st.subheader("📋 Your Current Weekly Plan")
    for day in DAYS_OF_WEEK:
        plan = st.session_state.workout_schedule[day]
        if plan["exercises"]:
            ex_summary = ", ".join([f"{e['name']} ({e['default_sets']}x{e['default_reps']})" for e in plan["exercises"]])
        else:
            ex_summary = "No exercises planned"
        st.markdown(f"**{day}** ({plan['routine']}): *{ex_summary}*")
