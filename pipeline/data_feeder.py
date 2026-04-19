# Asynchronous data simulator that reads from the sentiment dataset and fires 
# concurrent HTTP POST requests to the FastAPI backend, designed to stress-test 
# throughput and validate the 50+ concurrent request capability.

import asyncio
import aiohttp
import pandas as pd
import random
import time

API_URL = "http://localhost:8000/predict"
CSV_PATH = "data/sentiment_data.csv"
BATCH_SIZE = 16
CONCURRENT_REQUESTS = 50

async def send_batch(session, texts):
    payload = {"texts": texts}
    try:
        async with session.post(API_URL, json=payload) as response:
            return await response.json()
    except Exception as e:
        return {"error": str(e)}

async def simulate_stream():
    try:
        df = pd.read_csv(CSV_PATH, encoding='latin-1', header=None)
        all_texts = df.iloc[:, -1].dropna().tolist()
        print(f"Loaded {len(all_texts)} records from dataset.")
    except Exception as e:
        print(f"Failed to load CSV: {e}. Using fallback data.")
        all_texts = ["This product is amazing!"] * 1000 + ["I am very disappointed."] * 1000

    async with aiohttp.ClientSession() as session:
        while True:
            start_time = time.time()
            tasks = []
            
            for _ in range(CONCURRENT_REQUESTS):
                batch = random.sample(all_texts, BATCH_SIZE)
                tasks.append(send_batch(session, batch))
            
            results = await asyncio.gather(*tasks)
            
            elapsed = time.time() - start_time
            success_count = sum(1 for r in results if "error" not in r)
            
            print(f"Sent {CONCURRENT_REQUESTS} batches ({CONCURRENT_REQUESTS * BATCH_SIZE} texts) in {elapsed:.2f}s. Success: {success_count}/{CONCURRENT_REQUESTS}")
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(simulate_stream())