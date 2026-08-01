import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# 1. PAGE & STYLING CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="FitTrack - Personal Log",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern card UI and touch-friendly mobile navigation
st.markdown("""
    <style>
    /* Clean background & spacing */
    .main .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 720px;
    }
    
    /* Header Styling */
    .app-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .app-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1E293B;
        margin: 0;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.95rem;
    }

    /* Tab bar aesthetic */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        font-weight: 600;
        color: #475569;
        border: none;
        padding: 0 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
    }
    
    /* Form containers */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. GOOGLE SHEETS CONNECTION & DATA HELPERS
# ---------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(ttl="0s")
        df = df.dropna(how="all")
        if df.empty:
            return pd.DataFrame(columns=["Date", "Category", "Item", "Value", "Notes"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Date", "Category", "Item", "Value", "Notes"])

def append_entry(date_str, category, item, value, notes):
    existing_df = load_data()
    new_row = pd.DataFrame([{
        "Date": date_str,
        "Category": category,
        "Item": item,
        "Value": float(value),
        "Notes": notes
    }])
    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    conn.update(data=updated_df)
    st.cache_data.clear()

# Title Header
st.markdown("""
    <div class="app-header">
        <h1 class="app-title">⚡ FitTrack</h1>
        <p class="app-subtitle">Personal Fitness & Body Measurement Journal</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. TABS NAVIGATION
# ---------------------------------------------------------
tab_workout, tab_body, tab_data = st.tabs(["🏋️ Workouts", "📐 Body Metrics", "📋 History"])

# =========================================================
# TAB 1: WORKOUT TRACKER
# =========================================================
with tab_workout:
    st.subheader("🏋️ Log Workout")
    
    with st.form("workout_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            w_date = st.date_input("Date", datetime.now(), key="w_date")
        with col2:
            w_exercise = st.text_input("Exercise Name", placeholder="e.g. Bench Press", key="w_ex")
            
        col3, col4 = st.columns(2)
        with col3:
            w_weight = st.number_input("Weight / Load (kg)", min_value=0.0, step=0.5, key="w_val")
        with col4:
            w_reps_sets = st.text_input("Sets & Reps", placeholder="e.g. 3 sets x 10 reps", key="w_sets")
            
        w_notes = st.text_area("Notes", placeholder="How did it feel? Rest time, RPE...", height=70, key="w_notes")
        
        # Combine reps/sets into notes if provided
        final_notes = f"[{w_reps_sets}] {w_notes}".strip() if w_reps_sets else w_notes
        
        submit_workout = st.form_submit_button("Save Workout", type="primary", use_container_width=True)
        
        if submit_workout:
            if w_exercise and w_weight > 0:
                append_entry(w_date.strftime("%Y-%m-%d"), "Workout", w_exercise.strip().title(), w_weight, final_notes)
                st.success(f"Logged {w_exercise}: {w_weight} kg")
            else:
                st.error("Please enter an exercise name and a weight > 0.")

    st.markdown("---")
    st.subheader("📈 Exercise Progression")
    
    df_all = load_data()
    df_workouts = df_all[df_all["Category"] == "Workout"] if not df_all.empty else pd.DataFrame()
    
    if not df_workouts.empty and "Item" in df_workouts.columns:
        exercises = df_workouts["Item"].dropna().unique()
        selected_ex = st.selectbox("Select Exercise to View Trend", exercises, key="ex_select")
        
        chart_df = df_workouts[df_workouts["Item"] == selected_ex].copy()
        chart_df["Value"] = pd.to_numeric(chart_df["Value"], errors="coerce")
        chart_df = chart_df.sort_values("Date")
        
        if not chart_df.empty:
            st.line_chart(chart_df.set_index("Date")["Value"])
            
            # Show recent history table for this exercise
            st.caption(f"Recent logs for {selected_ex}:")
            st.dataframe(
                chart_df[["Date", "Value", "Notes"]].rename(columns={"Value": "Weight (kg)"}),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No workout entries logged yet.")

# =========================================================
# TAB 2: BODY MEASUREMENT TRACKER
# =========================================================
with tab_body:
    st.subheader("📐 Log Body Measurement")
    
    with st.form("body_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            b_date = st.date_input("Date", datetime.now(), key="b_date")
        with col2:
            b_metric = st.selectbox("Metric", [
                "Weight (kg)", 
                "Waist (cm)", 
                "Chest (cm)", 
                "Biceps (cm)", 
                "Body Fat (%)", 
                "Hips (cm)", 
                "Thighs (cm)"
            ], key="b_metric")
            
        b_value = st.number_input("Value", min_value=0.0, step=0.1, format="%.1f", key="b_val")
        b_notes = st.text_area("Notes", placeholder="Morning measurement, fasted, etc.", height=70, key="b_notes")
        
        submit_body = st.form_submit_button("Save Measurement", type="primary", use_container_width=True)
        
        if submit_body:
            if b_value > 0:
                append_entry(b_date.strftime("%Y-%m-%d"), "Body Measurement", b_metric, b_value, b_notes)
                st.success(f"Logged {b_metric}: {b_value}")
            else:
                st.error("Please enter a value greater than 0.")

    st.markdown("---")
    st.subheader("📊 Body Metric Trends")
    
    df_body = df_all[df_all["Category"] == "Body Measurement"] if not df_all.empty else pd.DataFrame()
    
    if not df_body.empty and "Item" in df_body.columns:
        metrics = df_body["Item"].dropna().unique()
        selected_metric = st.selectbox("Select Metric to View Trend", metrics, key="metric_select")
        
        m_chart_df = df_body[df_body["Item"] == selected_metric].copy()
        m_chart_df["Value"] = pd.to_numeric(m_chart_df["Value"], errors="coerce")
        m_chart_df = m_chart_df.sort_values("Date")
        
        if not m_chart_df.empty:
            # Latest value indicator card
            latest_val = m_chart_df.iloc[-1]["Value"]
            st.metric(label=f"Current {selected_metric}", value=f"{latest_val}")
            
            st.line_chart(m_chart_df.set_index("Date")["Value"])
    else:
        st.info("No body measurement entries logged yet.")

# =========================================================
# TAB 3: HISTORY & RAW DATA
# =========================================================
with tab_data:
    st.subheader("📋 All Logs (Google Sheets)")
    
    if not df_all.empty:
        st.dataframe(df_all.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
        
        csv_data = df_all.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV Backup",
            data=csv_data,
            file_name="fitness_tracker_backup.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("Your Google Sheet is currently empty.")
