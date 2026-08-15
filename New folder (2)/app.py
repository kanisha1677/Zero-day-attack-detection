"""
Zero-Day Network Attack Detection Dashboard
Streamlit-based real-time alert dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from detection_system import DetectionSystem

# Page configuration
st.set_page_config(
    page_title="Zero-Day Attack Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-card {
        border-left: 4px solid #ff4b4b;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #fff5f5;
        border-radius: 0.5rem;
    }
    .normal-card {
        border-left: 4px solid #00cc00;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f0fff0;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'detection_system' not in st.session_state:
    with st.spinner('Initializing Detection System...'):
        try:
            st.session_state.detection_system = DetectionSystem()
            st.session_state.detection_system.load_models()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"Failed to initialize system: {e}")
            st.session_state.initialized = False

if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []

if 'last_detection_time' not in st.session_state:
    st.session_state.last_detection_time = datetime.now()

# Header
st.markdown('<p class="main-header">🛡️ Zero-Day Network Attack Detection System</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Detection threshold
    detection_threshold = st.slider(
        "Detection Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Confidence threshold for attack detection"
    )
    
    # Time range filter
    st.subheader("📅 Time Range Filter")
    time_range = st.selectbox(
        "Select Time Range",
        ["Last 1 hour", "Last 24 hours", "Last 7 days", "Custom range"],
        help="Filter alerts by time range"
    )
    
    if time_range == "Custom range":
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
    
    # Attack type filter
    st.subheader("🎯 Attack Type Filter")
    attack_types = st.multiselect(
        "Filter by Attack Type",
        ["DoS", "Probe", "R2L", "U2R"],
        default=["DoS", "Probe", "R2L", "U2R"]
    )
    
    st.divider()
    
    # System information
    st.subheader("ℹ️ System Info")
    if st.session_state.initialized:
        st.success("✅ System Active")
        st.info(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.error("❌ System Offline")

# Main content area
if not st.session_state.initialized:
    st.error("⚠️ Detection system not initialized. Please check configuration.")
    st.stop()

# Metrics row
col1, col2, col3, col4 = st.columns(4)

detection_system = st.session_state.detection_system
metrics = detection_system.get_metrics()

with col1:
    st.metric(
        label="Total Detections",
        value=metrics['total_detections'],
        delta=None
    )

with col2:
    st.metric(
        label="Attack Detections",
        value=metrics['attack_detections'],
        delta=None
    )

with col3:
    # Requirement 8, AC5: Detection rate per minute
    detection_rate = metrics.get('detection_rate', 0.0)
    st.metric(
        label="Detection Rate",
        value=f"{detection_rate:.1f}/min",
        delta=None
    )

with col4:
    # Requirement 8, AC5: Processing latency (95th percentile)
    latency = metrics['processing_latency_milliseconds']
    st.metric(
        label="Latency (95th %ile)",
        value=f"{latency:.0f} ms",
        delta=None
    )

st.divider()

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["🚨 Real-Time Detection", "📊 Analytics", "🧪 Manual Test", "📖 About"])

with tab1:
    st.header("Real-Time Alerts")
    
    # Alert display area
    alert_container = st.container()
    
    # Requirement 8, AC1: Display alerts within 1 second
    if st.session_state.detection_history:
        # Filter by time range
        now = datetime.now()
        if time_range == "Last 1 hour":
            cutoff = now - timedelta(hours=1)
        elif time_range == "Last 24 hours":
            cutoff = now - timedelta(days=1)
        elif time_range == "Last 7 days":
            cutoff = now - timedelta(days=7)
        else:
            cutoff = datetime.min
        
        filtered_detections = [
            d for d in st.session_state.detection_history
            if datetime.fromisoformat(d['timestamp']) >= cutoff
        ]
        
        # Filter by attack type
        if attack_types:
            filtered_detections = [
                d for d in filtered_detections
                if d['decision'] == 'Normal' or any(
                    d.get('classifications', {}).get('random_forest', {}).get('class') in attack_types or
                    d.get('classifications', {}).get('xgboost', {}).get('class') in attack_types
                )
            ]
        
        with alert_container:
            for detection in reversed(filtered_detections[-10:]):  # Show last 10
                # Requirement 8, AC2: Display classification, confidence, timestamp
                timestamp = datetime.fromisoformat(detection['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                decision = detection['decision']
                confidence = detection['confidence']
                
                # Determine attack class
                attack_class = "Normal"
                if decision == "Attack":
                    rf_class = detection.get('classifications', {}).get('random_forest', {}).get('class', 'Unknown')
                    xgb_class = detection.get('classifications', {}).get('xgboost', {}).get('class', 'Unknown')
                    attack_class = rf_class if rf_class != 'Normal' else xgb_class
                
                card_class = "alert-card" if decision == "Attack" else "normal-card"
                
                with st.container():
                    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                    
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    
                    with col_a:
                        icon = "🚨" if decision == "Attack" else "✅"
                        st.markdown(f"**{icon} {decision}** - {attack_class}")
                        st.caption(f"🕐 {timestamp}")
                    
                    with col_b:
                        st.metric("Confidence", f"{confidence:.2f}")
                    
                    with col_c:
                        if st.button("Details", key=f"detail_{detection['timestamp']}"):
                            st.session_state.selected_detection = detection
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Requirement 8, AC3: Display SHAP explanations
                if decision == "Attack" and detection.get('explanation'):
                    with st.expander("📊 Explainability Details"):
                        explanation = detection['explanation']
                        
                        if explanation.get('top_features'):
                            # Create horizontal bar chart for top features
                            features_df = pd.DataFrame(explanation['top_features'])
                            
                            fig = go.Figure(go.Bar(
                                x=features_df['shap_value'],
                                y=features_df['feature'],
                                orientation='h',
                                marker=dict(
                                    color=features_df['shap_value'],
                                    colorscale='RdYlGn',
                                    reversescale=True
                                )
                            ))
                            
                            fig.update_layout(
                                title="Feature Importance (SHAP Values)",
                                xaxis_title="SHAP Value",
                                yaxis_title="Feature",
                                height=400,
                                yaxis={'categoryorder': 'total ascending'}
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show positive and negative contributions
                            col_pos, col_neg = st.columns(2)
                            
                            with col_pos:
                                st.markdown("**✅ Positive Contributions (Support Attack)**")
                                for feat in explanation['positive_contributions'][:5]:
                                    st.write(f"• {feat['feature']}: +{feat['shap_value']:.4f}")
                            
                            with col_neg:
                                st.markdown("**❌ Negative Contributions (Oppose Attack)**")
                                for feat in explanation['negative_contributions'][:5]:
                                    st.write(f"• {feat['feature']}: {feat['shap_value']:.4f}")
    else:
        st.info("No detections yet. Use the 'Manual Test' tab to test the system.")

with tab2:
    st.header("Analytics Dashboard")
    
    if st.session_state.detection_history:
        # Create DataFrame from history
        df = pd.DataFrame(st.session_state.detection_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Detection trend over time
        st.subheader("📈 Detection Trend")
        
        detection_counts = df.groupby([df['timestamp'].dt.floor('5min'), 'decision']).size().reset_index(name='count')
        detection_counts.columns = ['timestamp', 'decision', 'count']
        
        fig_trend = px.line(
            detection_counts,
            x='timestamp',
            y='count',
            color='decision',
            title='Detections Over Time (5-minute intervals)',
            labels={'count': 'Number of Detections', 'timestamp': 'Time'}
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Attack type distribution
        st.subheader("🎯 Attack Type Distribution")
        
        attack_df = df[df['decision'] == 'Attack'].copy()
        if not attack_df.empty:
            attack_df['attack_type'] = attack_df.apply(
                lambda row: row.get('classifications', {}).get('random_forest', {}).get('class', 'Unknown'),
                axis=1
            )
            
            attack_counts = attack_df['attack_type'].value_counts()
            
            fig_pie = px.pie(
                values=attack_counts.values,
                names=attack_counts.index,
                title='Attack Types Distribution'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No attacks detected yet.")
        
        # Confidence distribution
        st.subheader("📊 Confidence Score Distribution")
        
        fig_hist = px.histogram(
            df,
            x='confidence',
            color='decision',
            nbins=20,
            title='Confidence Score Distribution',
            labels={'confidence': 'Confidence Score', 'count': 'Frequency'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
    else:
        st.info("No data available for analytics yet.")

with tab3:
    st.header("Manual Network Traffic Test")
    
    st.write("Test the detection system by entering network traffic data:")
    
    with st.form("test_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            packet_size = st.number_input("Packet Size (bytes)", min_value=0, value=1000)
            byte_count = st.number_input("Byte Count", min_value=0, value=5000)
            duration_seconds = st.number_input("Duration (seconds)", min_value=0.0, value=1.5)
        
        with col2:
            protocol_type = st.selectbox("Protocol Type", ["tcp", "udp", "icmp"])
            flag_status = st.selectbox("Flag Status", ["SF", "S0", "REJ", "RSTO", "SH"])
            service_type = st.selectbox("Service Type", ["http", "ftp", "smtp", "ssh", "telnet", "other"])
        
        submit_button = st.form_submit_button("🔍 Analyze Traffic")
        
        if submit_button:
            # Create traffic data
            traffic_data = {
                'timestamp': datetime.now().isoformat(),
                'packet_size': packet_size,
                'byte_count': byte_count,
                'duration_seconds': duration_seconds,
                'protocol_type': protocol_type,
                'flag_status': flag_status,
                'service_type': service_type
            }
            
            with st.spinner('Analyzing network traffic...'):
                result = detection_system.process_traffic(traffic_data)
                
                # Add to history
                st.session_state.detection_history.append(result)
                st.session_state.last_detection_time = datetime.now()
            
            # Display result
            st.success("Analysis Complete!")
            
            decision = result['decision']
            confidence = result['confidence']
            
            if decision == "Attack":
                st.error(f"🚨 **ATTACK DETECTED** - Confidence: {confidence:.2f}")
            else:
                st.success(f"✅ **NORMAL TRAFFIC** - Confidence: {confidence:.2f}")
            
            # Show detailed results
            with st.expander("📋 Detailed Results"):
                st.json(result)

with tab4:
    st.header("About the System")
    
    st.markdown("""
    ### 🛡️ Zero-Day Network Attack Detection System
    
    This system uses advanced machine learning techniques to detect previously unknown network attacks through pattern analysis.
    
    #### 🔬 Detection Models
    
    **Anomaly Detection:**
    - **Isolation Forest**: Detects outliers in network traffic patterns
    - **Autoencoder**: Identifies complex non-linear anomalies using neural networks
    
    **Attack Classification:**
    - **Random Forest**: Classifies attack types using ensemble decision trees
    - **XGBoost**: Advanced gradient boosting for accurate predictions
    
    **Ensemble Voting**: Combines all model predictions for robust final decisions
    
    **SHAP Explainability**: Provides interpretable explanations for each detection
    
    #### 📊 Attack Types
    
    - **DoS** (Denial of Service): Overwhelming system resources
    - **Probe**: Network scanning and reconnaissance
    - **R2L** (Remote to Local): Unauthorized remote access attempts
    - **U2R** (User to Root): Privilege escalation attacks
    
    #### ⚡ Performance
    
    - **Throughput**: 1000+ samples/second
    - **Latency**: <2 seconds end-to-end
    - **Concurrent Processing**: 100 samples simultaneously
    
    #### 🔧 Technologies
    
    - Python, Streamlit, Scikit-learn, XGBoost, TensorFlow
    - SHAP for explainability
    - Plotly for visualizations
    
    ---
    
    **System Status**: ✅ Operational
    """)

# Auto-refresh option
st.sidebar.divider()
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (5s)", value=False)

if auto_refresh:
    import time
    time.sleep(5)
    st.rerun()

# Footer
st.divider()
st.caption("Zero-Day Network Attack Detection System | Powered by AI & Machine Learning")
