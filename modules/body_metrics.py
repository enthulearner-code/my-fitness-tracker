# modules/body_metrics.py
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.database import append_entry, load_data

def render_body_metrics_tab():
    """Renders body measurements logging and charts tab."""
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
    
    df_all = load_data()
    df_body = df_all[df_all["Category"] == "Body Measurement"] if not df_all.empty else pd.DataFrame()
    
    if not df_body.empty and "Item" in df_body.columns:
        metrics = df_body["Item"].dropna().unique()
        selected_metric = st.selectbox("Select Metric to View Trend", metrics, key="metric_select")
        
        m_chart_df = df_body[df_body["Item"] == selected_metric].copy()
        m_chart_df["Value"] = pd.to_numeric(m_chart_df["Value"], errors="coerce")
        m_chart_df = m_chart_df.sort_values("Date")
        
        if not m_chart_df.empty:
            latest_val = m_chart_df.iloc[-1]["Value"]
            st.metric(label=f"Current {selected_metric}", value=f"{latest_val}")
            st.line_chart(m_chart_df.set_index("Date")["Value"])
    else:
        st.info("No body measurement entries logged yet.")
