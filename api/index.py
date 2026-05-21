from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
from pathlib import Path

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data
DATA_PATH = Path(__file__).resolve().parent.parent / "q-vercel-latency.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    telemetry = json.load(f)

# Request schema
class MetricsRequest(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/")
async def calculate_metrics(request: MetricsRequest):

    results = []

    for region in request.regions:

        region_data = [
            row for row in telemetry
            if row["region"] == region
        ]

        latencies = [row["latency_ms"] for row in region_data]
        uptimes = [row["uptime_pct"] for row in region_data]

        avg_latency = round(sum(latencies) / len(latencies), 2)

        p95_latency = round(float(np.percentile(latencies, 95)), 2)

        avg_uptime = round(sum(uptimes) / len(uptimes), 3)

        breaches = sum(
            1 for row in region_data
            if row["latency_ms"] > request.threshold_ms
        )

        results.append({
            "region": region,
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        })

    return {"results": results}