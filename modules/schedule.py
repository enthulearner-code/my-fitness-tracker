# modules/schedule.py

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
    
    # Render existing exercises
    for idx, ex in enumerate(day_data["exercises"]):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 0.5])
        with c1:
            name = st.text_input(f"Exercise #{idx+1}", value=ex["name"], key=f"ex_name_{selected_edit_day}_{idx}")
        with c2:
            sets = st.number_input("Sets", min_value=1, max_value=10, value=ex.get("default_sets", 3), key=f"ex_sets_{selected_edit_day}_{idx}")
        with c3:
            reps = st.number_input("Reps", min_value=1, max_value=100, value=ex.get("default_reps", 10), key=f"ex_reps_{selected_edit_day}_{idx}")
        with c4:
            st.write("") # Spacer
            st.write("")
            # Delete button for individual exercise
            if st.button("🗑️", key=f"del_{selected_edit_day}_{idx}"):
                day_data["exercises"].pop(idx)
                # Helper to flush back to sheets
                _save_all_schedule(current_schedule)
                st.rerun()

        if name.strip():
            updated_exercises.append({"name": name.strip(), "default_sets": int(sets), "default_reps": int(reps)})

    # Section to Add a New Exercise
    st.markdown("---")
    with st.expander("➕ Add New Exercise Slot", expanded=True):
        new_name = st.text_input("New Exercise Name", key=f"new_ex_{selected_edit_day}")
        col_s, col_r = st.columns(2)
        with col_s:
            new_s = st.number_input("Default Sets", min_value=1, max_value=10, value=3, key=f"new_s_{selected_edit_day}")
        with col_r:
            new_r = st.number_input("Default Reps", min_value=1, max_value=100, value=10, key=f"new_r_{selected_edit_day}")
        
        if st.button("Add to Day's Schedule", type="secondary", use_container_width=True):
            if new_name.strip():
                # Add to updated list
                updated_exercises.append({
                    "name": new_name.strip(), 
                    "default_sets": int(new_s), 
                    "default_reps": int(new_r)
                })
                current_schedule[selected_edit_day] = {
                    "routine": new_routine_name.strip(),
                    "exercises": updated_exercises
                }
                # Persist directly to Google Sheets
                _save_all_schedule(current_schedule)
                st.success(f"Added '{new_name.strip()}' to {selected_edit_day}!")
                st.rerun()
            else:
                st.warning("Please enter an exercise name.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"💾 Save All Routine & Exercise Changes for {selected_edit_day}", type="primary", use_container_width=True):
        current_schedule[selected_edit_day] = {
            "routine": new_routine_name.strip(),
            "exercises": updated_exercises
        }
        _save_all_schedule(current_schedule)
        st.success(f"Saved {selected_edit_day}'s plan permanently!")
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


def _save_all_schedule(current_schedule):
    """Helper function to compile and write schedule dict to Google Sheets."""
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
