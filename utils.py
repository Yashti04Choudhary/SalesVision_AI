import streamlit as st
import pandas as pd
import joblib
import os

@st.cache_data
def load_csv(file_path: str) -> pd.DataFrame:
    """
    Loads a CSV file from the given path.
    Handles missing files gracefully by showing a Streamlit warning and returning an empty DataFrame.
    """
    if not os.path.exists(file_path):
        st.warning(f"⚠️ Data file not found: `{file_path}`. Please verify that the file exists.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"❌ Error loading file `{file_path}`: {str(e)}")
        return pd.DataFrame()

@st.cache_resource
def load_model(model_path: str):
    """
    Loads a pre-trained model using joblib.
    Handles missing model file gracefully and returns None with a Streamlit warning.
    """
    if not os.path.exists(model_path):
        st.warning(f"⚠️ Model file not found: `{model_path}`. Please ensure the model is trained and saved.")
        return None
    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"❌ Error loading model from `{model_path}`: {str(e)}")
        return None

def load_metrics(metrics_path: str) -> pd.DataFrame:
    """
    Loads model evaluation metrics from CSV.
    If the file is missing, returns a DataFrame with placeholder metrics.
    """
    # TODO: Connect this to your training pipeline's evaluation outputs
    if not os.path.exists(metrics_path):
        st.warning(f"⚠️ Evaluation metrics file not found: `{metrics_path}`. Showing default placeholders.")
        # Default placeholder metrics
        return pd.DataFrame([{
            "Model": "Prophet",
            "MAE": 11232.49,
            "RMSE": 14032.41,
            "MAPE": 22.88
        }])
    try:
        return pd.read_csv(metrics_path)
    except Exception as e:
        st.error(f"❌ Error loading metrics from `{metrics_path}`: {str(e)}")
        return pd.DataFrame([{
            "Model": "Prophet",
            "MAE": 11232.49,
            "RMSE": 14032.41,
            "MAPE": 22.88
        }])
