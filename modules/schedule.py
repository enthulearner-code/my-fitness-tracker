# modules/schedule.py
import streamlit as st

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def init_schedule():
    """Initializes default schedule in session state if missing."""
    if "workout_schedule" not in st.session_state:
        st.session_state.workout_schedule = {
            "Monday": {"routine": "Chest & Triceps", "exercises": ["Bench Press", "Incline Dumbbell Press", "Tricep Pushdown"]},
            "Tuesday": {"routine": "Back & Biceps", "exercises": ["Lat Pulldown", "Seated Cable Row", "Barbell Curl"]},
            "Wednesday": {"routine": "Rest Day / Cardio", "exercises": []},
            "Thursday": {"routine": "Legs & Core", "exercises": ["Squat", "Leg Press", "Plank"]},
            "Friday": {"routine": "Shoulders & Arms", "exercises": ["Overhead Press", "Lateral Raise", "Hammer Curl"]},
            "Saturday": {"routine": "Active Recovery", "exercises": []},
            "Sunday": {"routine": "Rest Day", "exercises": []},
        }

def render_schedule_tab():
    """Renders the weekly planner UI."""
    st.subheader("📅 Weekly Workout Planner")
    st.caption("Customize your daily routine and scheduled exercises below:")
    
    init_schedule()
    selected_edit_day = st.selectbox("Choose Day to Edit", DAYS_OF_WEEK)
    current_day_data = st.session_state.workout_schedule[selected_edit_day]
    
    with st.form("edit_schedule_form"):
        new_routine_name = st.text_input("Routine Name / Focus", value=current_day_data["routine"])
        exercises_raw = st.text_area(
            "Planned Exercises (One per line)",
            value="\n".join(current_day_data["exercises"]),
            height=120,
            help="Type each exercise name on a new line"
        )
        
        save_plan = st.form_submit_button(f"Save Schedule for {selected_edit_day}", type="primary", use_container_width=True)
        
        if save_plan:
            parsed_ex = [e.strip() for e in exercises_raw.split("\n") if e.strip()]
            st.session_state.workout_schedule[selected_edit_day] = {
                "routine": new_routine_name.strip(),
                "exercises": parsed_ex
            }
            st.success(f"Updated schedule for {selected_edit_day}!")

    st.markdown("---")
    st.subheader("📋 Your Current Weekly Plan")
    for day in DAYS_OF_WEEK:
        plan = st.session_state.workout_schedule[day]
        ex_list_str = ", ".join(plan["exercises"]) if plan["exercises"] else "No exercises planned"
        st.markdown(f"**{day}** ({plan['routine']}): *{ex_list_str}*")
