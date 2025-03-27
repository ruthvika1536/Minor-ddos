from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import joblib
import numpy as np
import pickle
import os
import tensorflow as tf  # For loading DNN model

app = FastAPI()

# Define paths for RL models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models_rl")
FEATURE_INDICES_PATH = os.path.join(MODEL_DIR, "feature_indices_rl.pkl")

# Load selected feature indices
with open(FEATURE_INDICES_PATH, "rb") as f:
    feature_indices = pickle.load(f)
print("Feature Indices (RL):", feature_indices)
print("Feature Indices Length (RL):", len(feature_indices))


# Load models dynamically
def load_model(model_name):
    model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        raise FileNotFoundError(f"Model file {model_name}.pkl not found.")

models = {
    "DecisionTreeRL": load_model("decisiontree_rl"),
    "RandomForestRL": load_model("randomforest_rl"),  # <--- Added Random Forest
    "XGBoostRL": load_model("xgboost_rl"),
}

# Load DNN model
DNN_MODEL_PATH = os.path.join(MODEL_DIR, "dnn_rl.h5")
dnn_model = tf.keras.models.load_model(DNN_MODEL_PATH)

# Define request model
class PredictionRequest(BaseModel):
    features: List[List[float]]  # Accepts multiple feature arrays

# Define response model
class PredictionResponse(BaseModel):
    predictions: Dict[str, List[str]]

@app.post("/predict_rl", response_model=PredictionResponse)
async def predict(data: PredictionRequest):
    try:
        # Convert input to numpy array
        raw_features = np.array(data.features, dtype=np.float32)
        print("Feature Indices Length:", len(feature_indices))
        print("Feature Indices:", feature_indices)

        # Select only relevant features based on saved indices
        selected_features = raw_features[:, feature_indices]

        # Store model predictions
        predictions = {}

        for model_name, model in models.items():
            pred = model.predict(selected_features)
            predictions[model_name] = ["DDoS" if p == 1 else "Benign" for p in pred]

        # DNN Model Prediction
        dnn_pred = dnn_model.predict(selected_features)  # No scaling applied
        dnn_pred_labels = ["DDoS" if p > 0.5 else "Benign" for p in dnn_pred.flatten()]
        predictions["DNN"] = dnn_pred_labels  # Add DNN predictions to response

        return {"predictions": predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run API when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)
