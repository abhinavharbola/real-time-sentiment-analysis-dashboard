#!/bin/bash
# Initializes the distributed system by launching the API, feeder, and dashboard

echo "Starting FastAPI Backend..."
uvicorn backend.main_api:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "Waiting for API to initialize..."
sleep 5

echo "Starting Data Feeder pipeline..."
python pipeline/data_feeder.py &
FEEDER_PID=$!

echo "Starting Streamlit Dashboard!..."
streamlit run app.py

trap "kill $API_PID $FEEDER_PID" EXIT