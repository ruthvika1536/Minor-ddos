from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import joblib
import numpy as np
import pickle
import os
import tensorflow as tf  # For loading DNN model

app = FastAPI()

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chi-Square Paths
CHI_MODEL_DIR = os.path.join(BASE_DIR, "models")
CHI_FEATURE_INDICES_PATH = os.path.join(BASE_DIR, "feature_indices.pkl")
CHI_TOP_FEATURES_PATH = os.path.join(BASE_DIR, "top_features.pkl")
CHI_DNN_MODEL_PATH = os.path.join(CHI_MODEL_DIR, "dnn_model_chi.h5")
CHI_SCALER_PATH = os.path.join(CHI_MODEL_DIR, "scaler.pkl")

# RL Paths
RL_MODEL_DIR = os.path.join(BASE_DIR, "models_rl")
RL_FEATURE_INDICES_PATH = os.path.join(RL_MODEL_DIR, "feature_indices_rl.pkl")
RL_TOP_FEATURES_PATH = os.path.join(RL_MODEL_DIR, "top_features_rl.pkl")
RL_DNN_MODEL_PATH = os.path.join(RL_MODEL_DIR, "dnn_model_rl.h5")

# Load Chi-Square Feature Indices
with open(CHI_FEATURE_INDICES_PATH, "rb") as f:
    feature_indices_chi = pickle.load(f)

# Load RL Feature Indices
with open(RL_FEATURE_INDICES_PATH, "rb") as f:
    feature_indices_rl = pickle.load(f)

# Load Chi-Square Models
def load_model(model_dir, model_name):
    model_path = os.path.join(model_dir, f"{model_name}.pkl")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        raise FileNotFoundError(f"Model file {model_name}.pkl not found.")

chi_models = {
    "DecisionTreeChi": load_model(CHI_MODEL_DIR, "DecisionTreeChi"),
    "RandomForestChi": load_model(CHI_MODEL_DIR, "RandomForestChi"),
    "XGBoostChi": load_model(CHI_MODEL_DIR, "XGBoostChi")
}

# Load RL Models
rl_models = {
    "DecisionTreeRL": load_model(RL_MODEL_DIR, "DecisionTreeRl"),
    "RandomForestRL": load_model(RL_MODEL_DIR, "RandomForestRl"),
    "XGBoostRL": load_model(RL_MODEL_DIR, "XGBoostRl")
}

# Load DNN models
dnn_model_chi = tf.keras.models.load_model(CHI_DNN_MODEL_PATH)
dnn_model_rl = tf.keras.models.load_model(RL_DNN_MODEL_PATH)

# Load Scaler for Chi-Square models
scaler_chi = joblib.load(CHI_SCALER_PATH)

# Define request model
class PredictionRequest(BaseModel):
    features: List[List[float]]  # Accepts multiple feature arrays
    method: str  # "chi" or "rl"

# Define response model
class PredictionResponse(BaseModel):
    predictions: Dict[str, List[str]]

@app.post("/predict", response_model=PredictionResponse)
async def predict(data: PredictionRequest):
    try:
        # Convert input to numpy array
        raw_features = np.array(data.features, dtype=np.float32)

        # Select appropriate feature indices based on method
        if data.method.lower() == "chi":
            selected_features = raw_features[:, feature_indices_chi]
            models = chi_models
            dnn_model = dnn_model_chi
            scaled_features = scaler_chi.transform(selected_features)  # Scale for DNN
        elif data.method.lower() == "rl":
            selected_features = raw_features[:, feature_indices_rl]
            models = rl_models
            scaled_features = selected_features  # RL does not require scaling
            dnn_model = dnn_model_rl
        else:
            raise HTTPException(status_code=400, detail="Invalid method. Use 'chi' or 'rl'.")

        # Store model predictions
        predictions = {}

        for model_name, model in models.items():
            pred = model.predict(selected_features)
            predictions[model_name] = ["DDoS" if p == 1 else "Benign" for p in pred]

        # DNN Model Prediction
        dnn_pred = dnn_model.predict(scaled_features)
        dnn_pred_labels = ["DDoS" if p > 0.5 else "Benign" for p in dnn_pred.flatten()]
        predictions["DNN"] = dnn_pred_labels

        return {"predictions": predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run API when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
