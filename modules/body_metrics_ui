import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import os

def render_body_silhouette_tab():
    st.header("👤 Body Measurement Visualizer")
    st.write("Track your physical changes over time.")

    # 1. Mock Data (Later, you can connect this to conn.read("Metrics"))
    measurements = {
        "Neck": 16.0, "Shoulders": 48.5, "Chest": 42.0,
        "Biceps (L)": 14.5, "Biceps (R)": 14.5,
        "Waist": 33.0, "Hips": 39.0,
        "Thigh (L)": 23.5, "Thigh (R)": 23.5,
        "Calf (L)": 15.0, "Calf (R)": 15.0
    }
    unit = "in" 

    # 2. Load the background image
    # We use a relative path assuming the image is in the root directory, outside 'modules/'
    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'body_outline.png')
    
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        st.error("⚠️ Image not found. Please ensure 'body_outline.png' is saved in your main project folder.")
        return

    # 3. Define Coordinates (Calibrated for the new light-grey silhouette)
    coords = {
        "Neck": (0.5, 0.82),
        "Shoulders": (0.5, 0.73),
        "Chest": (0.5, 0.65),
        "Biceps (L)": (0.28, 0.58), 
        "Biceps (R)": (0.72, 0.58),
        "Waist": (0.5, 0.52),
        "Hips": (0.5, 0.44),
        "Thigh (L)": (0.38, 0.35),
        "Thigh (R)": (0.62, 0.35),
        "Calf (L)": (0.38, 0.15),
        "Calf (R)": (0.62, 0.15)
    }

    # 4. Build the Plotly Figure
    fig = go.Figure()

    fig.add_layout_image(
        dict(
            source=img, xref="x", yref="y", x=0, y=1,
            sizex=1, sizey=1, sizing="stretch",
            opacity=0.8, layer="below"
        )
    )

    # 5. Add Annotations
    for body_part, value in measurements.items():
        x_pos, y_pos = coords.get(body_part, (0.5, 0.5))
        
        fig.add_annotation(
            x=x_pos, y=y_pos,
            text=f"<b>{value}{unit}</b>", 
            showarrow=False,
            font=dict(size=14, color="white"),
            bgcolor="rgba(40, 167, 69, 0.9)", # Green badges
            bordercolor="#ffffff", borderwidth=2, borderpad=4,
            hovertext=body_part 
        )

    # Clean up layout
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 1]),
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 1]),
        height=650, margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)
