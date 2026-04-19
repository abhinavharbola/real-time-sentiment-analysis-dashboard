# Interactive Streamlit dashboard visualizing live sentiment analytics, 
# KPI tracking across temporal windows, and automated system alerts

import streamlit as st
import time
from utils.metrics import fetch_temporal_data, calculate_kpis
from utils.alerts import check_and_trigger_alerts

st.set_page_config(page_title="Real-Time Sentiment Dashboard", layout="wide")

st.title("Live Sentiment Analytics Dashboard")

time_window = st.sidebar.selectbox("Select Temporal Window", options=[1, 6, 24], format_func=lambda x: f"Last {x} Hour(s)")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 3)

placeholder = st.empty()

while True:
    df = fetch_temporal_data(hours=time_window)
    kpis = calculate_kpis(df)
    
    with placeholder.container():
        check_and_trigger_alerts(df)
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Total Processed", f"{kpis['total_records']:,}")
        col2.metric("Positive Sentiment", f"{kpis['positive_pct']}%")
        col3.metric("Negative Sentiment", f"{kpis['negative_pct']}%")
        col4.metric("Avg Latency", f"{kpis['avg_latency_ms']} ms")
        col5.metric("Avg Confidence", f"{kpis['avg_confidence']:.3f}")
        col6.metric("Throughput (req/min)", f"{kpis['throughput_per_min']:,.1f}")
        
        if not df.empty:
            st.subheader("Recent Activity Stream")
            st.dataframe(
                df[['timestamp', 'text', 'sentiment', 'confidence', 'latency_ms']].tail(15).iloc[::-1], 
                use_container_width=True,
                hide_index=True
            )
    
    time.sleep(refresh_rate)