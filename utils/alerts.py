# Evaluates real-time data streams against predefined thresholds 
# to trigger automated alerts for anomaly detection and operational health monitoring

import streamlit as st
import pandas as pd

def check_and_trigger_alerts(df: pd.DataFrame):
    if df.empty:
        return

    recent_df = df.tail(100)
    
    if len(recent_df) >= 50:
        negative_ratio = len(recent_df[recent_df['sentiment'] == 'NEGATIVE']) / len(recent_df)
        if negative_ratio > 0.70:
            st.error(f"🚨 ALERT: High Negative Sentiment Detected! ({negative_ratio*100:.1f}% in last 100 records)")

    avg_latency = recent_df['latency_ms'].mean()
    if avg_latency > 200:
        st.warning(f"⚠️ WARNING: Inference Latency Degradation. Current avg: {avg_latency:.1f}ms")
        
    error_count = len(recent_df[recent_df['confidence'] < 0.50])
    if error_count > 20:
        st.info(f"NOTICE: Elevated low-confidence predictions ({error_count} in recent batch).")