from contextlib import asynccontextmanager
import math
import os
from pathlib import Path

import boto3
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

FEATURE_NAMES = [
    "age", "workclass", "education_num", "marital_status", "occupation",
    "relationship", "sex", "capital_gain", "capital_loss", "hours_per_week",
]
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = Path(os.getenv("MODEL_PATH", "~/models/model.joblib")).expanduser()


def download_model():
    """Use the EC2 IAM role or the standard AWS credential chain."""
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = MODEL_PATH.with_suffix(".download")
    boto3.client("s3").download_file(
        os.environ["ARTIFACT_BUCKET"], MODEL_KEY, str(temporary_path))
    temporary_path.replace(MODEL_PATH)
    print("Model downloaded from S3.")


@asynccontextmanager
async def lifespan(app):
    download_model()
    app.state.model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(lifespan=lifespan)


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    if not hasattr(app.state, "model"):
        raise HTTPException(status_code=503, detail="Model is not ready")
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    if len(req.features) != len(FEATURE_NAMES):
        raise HTTPException(status_code=400, detail="Expected 10 features (adult income)")
    if not all(math.isfinite(value) for value in req.features):
        raise HTTPException(status_code=400, detail="Features must be finite numbers")
    if not hasattr(app.state, "model"):
        raise HTTPException(status_code=503, detail="Model is not ready")
    prediction = int(app.state.model.predict(pd.DataFrame([req.features], columns=FEATURE_NAMES))[0])
    return {"prediction": prediction,
            "label": "thu_nhap_cao" if prediction == 1 else "thu_nhap_thap"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
