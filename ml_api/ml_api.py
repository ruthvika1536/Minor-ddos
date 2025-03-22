from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import joblib
import numpy as np
import pickle
import os

app = FastAPI()

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
FEATURE_INDICES_PATH = os.path.join(BASE_DIR, "feature_indices.pkl")
TOP_FEATURES_PATH = os.path.join(BASE_DIR, "top_features.pkl")

# Load selected feature indices
with open(FEATURE_INDICES_PATH, "rb") as f:
    feature_indices = pickle.load(f)

# Load top feature names (optional, useful for debugging)
with open(TOP_FEATURES_PATH, "rb") as f:
    top_features = pickle.load(f)

# Load models dynamically
def load_model(model_name):
    model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        raise FileNotFoundError(f"Model file {model_name}.pkl not found.")

models = {
    "DecisionTreeChi": load_model("DecisionTreeChi"),
    "RandomForestChi": load_model("RandomForestChi"),
    "XGBoostChi": load_model("XGBoostChi")
}

# Define request model
class PredictionRequest(BaseModel):
    features: List[List[float]]  # Accepts multiple feature arrays

# Define response model
class PredictionResponse(BaseModel):
    predictions: Dict[str, List[str]]

@app.post("/predict", response_model=PredictionResponse)
async def predict(data: PredictionRequest):
    try:
        # Convert input to numpy array
        raw_features = np.array(data.features, dtype=np.float32)

        # Select only top features based on saved indices
        selected_features = raw_features[:, feature_indices]

        # Store model predictions
        predictions = {}

        for model_name, model in models.items():
            pred = model.predict(selected_features)
            predictions[model_name] = ["DDoS" if p == 1 else "Benign" for p in pred]

        return {"predictions": predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run API when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
