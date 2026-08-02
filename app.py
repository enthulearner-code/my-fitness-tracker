# app.py
import streamlit as st
from modules.database import load_data
from modules.workouts import render_workouts_tab
from modules.schedule import render_schedule_tab
from modules.body_metrics import render_body_metrics_tab
from modules.progress import render_progress_tab
from modules.attendance_ui import render_attendance_tab

# Page Configuration
st.set_page_config(
    page_title="FitTrack - Personal Log",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Styling
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 720px;
    }
    .app-header { text-align: center; margin-bottom: 1.2rem; }
    .app-title { font-size: 2rem; font-weight: 800; color: #1E293B; margin: 0; }
    .app-subtitle { color: #64748B; font-size: 0.95rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background-color: #F1F5F9; padding: 6px; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { height: 44px; border-radius: 8px; font-weight: 600; color: #475569; border: none; padding: 0 12px; }
    .stTabs [aria-selected="true"] { background-color: #2563EB !important; color: #FFFFFF !important; box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2); }
    </style>
""", unsafe_allow_html=True)

# Title Header
st.markdown("""
    <div class="app-header">
        <h1 class="app-title">⚡ FitTrack</h1>
        <p class="app-subtitle">Workout Planner & Body Measurement Journal</p>
    </div>
""", unsafe_allow_html=True)

# Tab Navigation
tab_today, tab_progress, tab_plan, tab_body, tab_attendance, tab_data = st.tabs([
    "🏋️ Log Today", 
    "📊 Progress Overview",
    "📅 Plan Schedule", 
    "📐 Body Metrics", 
    "✅ Attendance",
    "📋 History"
])

with tab_today:
    render_workouts_tab()

with tab_plan:
    render_schedule_tab()

with tab_body:
    render_body_metrics_tab()

with tab_data:
    st.subheader("📋 All Logs (Google Sheets)")
    df_all = load_data()
    
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
