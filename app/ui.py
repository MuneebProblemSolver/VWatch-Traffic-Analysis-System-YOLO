"""VWatch UI Application"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import tempfile
from app.ai.processor import process_video, finalize_violations
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="VWatch AI Traffic System",
    page_icon="🚦",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .signal-red {
        background: #ff4444;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        animation: pulse 1s infinite;
    }
    .signal-green {
        background: #00C851;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚦 VWatch AI Traffic System</h1>
    <p>Intelligent Traffic Violation Detection System</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/traffic-light.png")
    st.markdown("## Control Panel")
    
    uploaded_file = st.file_uploader(
        "Upload Traffic Video",
        type=["mp4", "avi", "mov", "mkv"],
        help="Upload video for violation detection"
    )

# Main content
if uploaded_file:
    # Save temp file
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    tfile.close()
    
    st.success(f"Processing video: {uploaded_file.name}")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎥 Live Feed", "📸 Violations", "📊 Analytics"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Live Processing")
            video_placeholder = st.empty()
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        with col2:
            st.markdown("### Signal Status")
            signal_placeholder = st.empty()
            st.markdown("### Live Counter")
            counter_placeholder = st.empty()
    
    with tab2:
        st.markdown("### Detected Violations")
        violations_grid = st.container()
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Signal Pattern")
            chart1 = st.empty()
        with col2:
            st.markdown("### Violation Summary")
            chart2 = st.empty()
    
    # Process video
    tracked_vehicles = {}
    signal_history = []
    frame_count = 0

    # Add this after processing starts
    with st.expander("🔍 Debug Information"):
     debug_placeholder = st.empty()
    
    try:
        for frame, signal, progress, tracked in process_video(tfile.name):
            frame_count += 1
            tracked_vehicles = tracked
            
            # Update display
            video_placeholder.image(frame, channels="BGR", use_column_width=True)
            progress_bar.progress(progress)
            status_text.text(f"Processing: {int(progress * 100)}%")
            
            # Signal display
            if signal == "RED":
                signal_placeholder.markdown(
                    '<div class="signal-red">🔴 RED SIGNAL - VIOLATION ACTIVE</div>',
                    unsafe_allow_html=True
                )
            else:
                signal_placeholder.markdown(
                    '<div class="signal-green">🟢 GREEN SIGNAL - NORMAL</div>',
                    unsafe_allow_html=True
                )
            
            signal_history.append(1 if signal == "RED" else 0)
            counter_placeholder.metric("Violations Found", len(tracked_vehicles))
        
        # Complete
        progress_bar.empty()
        status_text.success("✅ Processing Complete!")
        
        # Finalize violations
        violations, report_path = finalize_violations(tracked_vehicles)
        
        # Show violations
        with tab2:
            if violations:
                cols = st.columns(3)
                for idx, v in enumerate(violations):
                    with cols[idx % 3]:
                        st.markdown(f"**Violation #{idx+1}**")
                        st.markdown(f"🚗 Plate: {v['plate']}")
                        st.image(v["image"], use_column_width=True)
            else:
                st.success("✅ No violations detected!")
                st.balloons()
        
        # Analytics
        with tab3:
            with chart1:
                if signal_history:
                    fig, ax = plt.subplots(figsize=(6, 3))
                    ax.plot(signal_history[:500], color='red', linewidth=1)
                    ax.set_xlabel('Frame')
                    ax.set_ylabel('Signal (1=RED)')
                    ax.set_title('Traffic Signal Pattern')
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
            
            with chart2:
                if violations:
                    fig, ax = plt.subplots(figsize=(6, 3))
                    plates = [v['plate'][:8] for v in violations]
                    ax.bar(plates, [1] * len(violations), color='red', alpha=0.7)
                    ax.set_xlabel('License Plate')
                    ax.set_ylabel('Count')
                    ax.set_title('Violations by Vehicle')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
        
        # Download button
        st.markdown("---")
        if os.path.exists(report_path):
            with open(report_path, "rb") as f:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=f,
                    file_name=f"VWatch_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
    
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        st.exception(e)
    
    finally:
        # Cleanup
        os.unlink(tfile.name)

else:
    # Welcome screen
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h2>👋 Welcome to VWatch AI</h2>
        <p>Upload a traffic video to start detection</p>
        <div style='font-size: 100px;'>🚦</div>
    </div>
    """, unsafe_allow_html=True)