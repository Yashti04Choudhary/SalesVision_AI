# SalesVision AI

## Live Demo

*Will be added after deployment.*

## Intelligent Sales Analytics & Forecasting Dashboard

SalesVision AI is an AI-powered business intelligence dashboard developed during the XYLOFY AI Data Science Internship. It enables organizations to analyze historical sales performance, forecast future demand, detect unusual sales patterns, and identify product demand segments through machine learning techniques.

---

## 1. Project Overview

SalesVision AI is designed for retail executives, store managers, and supply chain analysts. By combining classical business intelligence (BI) layouts with advanced machine learning pipelines, the application enables data-driven decisions on stock levels, promotions, and operations.

### Key Highlights

- **Interactive Multi-Page Dashboard**: A modular Streamlit application with dedicated pages for sales analytics, forecasting, anomaly detection, and demand segmentation.
- **Interactive Data Exploration**: User-friendly filters, dropdowns, and interactive visualizations for exploring sales data across categories and regions.
- **Advanced Machine Learning**: Integrated forecasting, anomaly detection, and product demand segmentation using multiple machine learning techniques.

---

## 2. Features

- **Modern Responsive Streamlit Interface**: Clean multi-page dashboard with intuitive navigation, interactive visualizations, and responsive layouts.
- **Interactive Filtering**: Filter sales data by category, region, forecast scope, and product demand clusters to perform focused analysis.
- **Hybrid Multi-Horizon Forecaster**: Combines pre-trained production XGBoost models with on-the-fly XGBoost regressors to project future sales with recursive lag updates.
- **Dual Outlier Detection**: Side-by-side execution of unsupervised Isolation Forests and statistical Rolling Z-Score computations.
- **2D PCA Demand Segmentation**: Maps high-dimensional transaction profiles to optimized K-Means clusters, visualized with interactive dimensions.

---

## 3. Dashboard Pages

### Page 1 – Sales Overview Dashboard
- **KPI Metrics**: Displays total sales, order count, average order value, and active regions with hover lift highlights.
- **Monthly Sales Trend**: Interactive line chart displaying monthly revenue growth.
- **Sales by Region**: Pie charts showcasing market shares across major territories.
- **Sales by Category**: Horizontal bar charts identifying top-performing categories.
- **Dynamic Filters**: Quick sidebars to segment data by Category and Region.

### Page 2 – Forecast Explorer
- **Hybrid Forecasting Pipeline**: Loads a pre-trained serialized model for overall projections and dynamically trains lightweight models for individual segments.
- **Flexible Scope Selection**: Forecast overall sales, specific product categories, or regions.
- **Adjustable Horizon**: Slide controls to predict 1, 2, or 3 months ahead recursively.
- **Historical vs. Predicted Visuals**: Overlaid historical sales time series alongside recursive predictions.
- **Model Evaluation Card**: Displays evaluation metrics (MAE, RMSE, MAPE) for the production forecasting model.

### Page 3 – Anomaly Report
- **Outlier Detection Algorithms**: Choose between **Isolation Forest** (multivariate unsupervised) and **Rolling Z-Score** (rolling statistics).
- **Method Selection**: Switch between Isolation Forest and Rolling Z-Score methods to compare anomaly detection results.
- **Anomaly Tables**: Interactive lists of flagged order records with dates, sales, and deviations.
- **Business Interpretation**: Strategic summaries suggesting actions for identified outliers (e.g., shipping delays, bulk order pricing).

### Page 4 – Product Demand Segments
- **Unsupervised KMeans Clustering**: Segments product sub-categories based on total revenue, growth rate, volatility and average order value.
- **Interactive Dimension Reduction**: PCA plots visualizing clusters in a 2D space.
- **Cluster Statistics**: Displays cluster-wise product metrics including total sales, growth rate, volatility, and average order value.
- **Demand Segment Explanations**: Strategic business briefs outlining pricing and inventory guidelines for each cluster.

---

## 4. Machine Learning Pipeline

SalesVision AI leverages a robust machine learning backend containing the following stages:

- **Time Series Preprocessing**: Monthly aggregation, chronological ordering, and linear interpolation for missing indices.
- **Feature Engineering**:
  - *Lags*: 1-month (`Lag_1`), 2-month (`Lag_2`), and 3-month (`Lag_3`) sales shifts.
  - *Rolling Mean*: 3-month rolling window sales average (`Rolling_Mean_3`).
  - *Calendar Properties*: Numeric extraction of `Month` and `Quarter`.
  - *One-Hot Seasons*: Encoded indicators for `Season_Spring`, `Season_Summer`, and `Season_Winter`.
- **Hybrid Forecasting Pipeline**:
  - **Overall Sales**: Loaded production model (`best_model.pkl`) built using hyperparameter-optimized XGBoost regressors.
  - **Filtered Segment Sales**: Trains custom `XGBRegressor` estimators on the fly for the selected category/region slice.
  - **Recursive Multi-Step Inference**: Projects future months sequentially, shifting predictions back into lag variables and recalculating rolling means before the next step.
- **Unsupervised Anomaly Analysis**:
  - **Isolation Forest**: Splits features recursively to flag hard-to-isolate outliers.
  - **Rolling Z-Score**: Evaluates deviations relative to a rolling mean and standard deviation window.
- **Clustering & PCA**:
  - **StandardScaler**: Standardizes features to remove magnitude bias.
  - **KMeans**: Segments product sub-categories into clusters using optimized inertia.
  - **Principal Component Analysis (PCA)**: Compresses feature spaces to 2 principal components for direct visual analysis.

---

## 5. Project Structure

```text
SalesForecasting_Yashti/
│
├── app.py                     # Main dashboard page routing, global CSS styles, and footer
├── utils.py                   # Caching utilities for dataset loading and metric loading
├── forecast_utils.py          # Machine learning hybrid forecasting & recursive logic
├── analysis.ipynb             # Jupyter Notebook covering EDA, training, and modeling
├── train.csv                  # Raw Superstore transaction dataset
├── requirements.txt           # Python package dependencies
├── README.md                  # System documentation
│
├── models/
│     └── best_model.pkl       # Saved serialized production XGBoost model
│
├── charts/                    # Static anomaly and demand cluster graphics
│     ├── cluster_plot.png
│     ├── isolation_forest_anomalies.png
│     └── zscore_anomalies.png
│
├── saved_outputs/             # Serialized tables and metrics
│     ├── anomalies.csv
│     ├── cluster_results.csv
│     └── model_metrics.csv
│
└── pages/                     # Streamlit subpage implementations
      ├── sales_dashboard.py   # Page 1: Sales Overview Dashboard
      ├── forecast_explorer.py # Page 2: Forecast Explorer
      ├── anomaly_report.py    # Page 3: Sales Anomaly Detection
      └── demand_segments.py   # Page 4: Demand Segmentation
```

---

## 6. Installation

Follow these instructions to configure the dashboard environment:

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd SalesForecasting_Yashti
   ```

2. **Set up a Virtual Environment** (Recommended):
   ```bash
   # Create environment
   python -m venv venv

   # Activate on Windows:
   venv\Scripts\activate

   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 7. Running the Application

To start the local Streamlit web server:

```bash
streamlit run app.py
```

The system will initialize the server and open the web dashboard in your default browser, typically located at:
`http://localhost:8501`

---

## 8. Dependencies

The project relies on the following core libraries:
- **Python** (version 3.8+)
- **Streamlit** (interactive dashboard framework)
- **Pandas** (data manipulation and cleaning)
- **NumPy** (mathematical structures and arrays)
- **Plotly** (interactive HTML plotting library)
- **Matplotlib** (static visualization generation)
- **Scikit-learn** (KMeans clustering, PCA, StandardScaler, Isolation Forest)
- **XGBoost** (regression modeling for forecasts)
- **Statsmodels** (time series analysis utilities)
- **Joblib** (model serialization and caching)

See requirements.txt for exact version details.

---

## Dataset

This project uses the Superstore Sales dataset containing approximately **9,800 retail transactions** collected over **four years**.

The dataset includes:

- Order Date
- Ship Date
- Region
- Category
- Sub-Category
- Sales
- Profit
- Discount
- Customer and Product information

The dataset serves as the foundation for exploratory analysis, forecasting, anomaly detection, and product demand segmentation.

---

## 9. Future Improvements

- **Database Connection**: Migrate from local CSV `train.csv` to query production tables directly via Snowflake, BigQuery, or PostgreSQL.
- **Deep Learning Forecasts**: Integrate deep learning neural networks (e.g., N-BEATS, DLinear, or Temporal Fusion Transformers) for long-horizon demand planning.
- **Real-Time Alerting**: Configure automatic anomaly alerts (e.g., Slack or email integrations) when sales fall below statistical thresholds.
- **Drift Monitoring**: Track incoming data distributions to flag covariate and model performance drift, triggering automatic pipeline retraining.

---

## Screenshots

### Sales Overview Dashboard
<img width="1918" height="913" alt="Screenshot 2026-07-08 202928" src="https://github.com/user-attachments/assets/7e5fb73d-27a5-4bb7-8d5a-6daa9eafa3b9" />

<img width="1900" height="898" alt="Screenshot 2026-07-08 202958" src="https://github.com/user-attachments/assets/6daa60eb-de34-4462-a7c4-c867e01b23c6" />

### Forecast Explorer
<img width="1911" height="911" alt="Screenshot 2026-07-08 203106" src="https://github.com/user-attachments/assets/f2ab72a1-55d6-4f46-b3a9-310e296b3157" />

### Anomaly Report
<img width="1897" height="901" alt="Screenshot 2026-07-08 203217" src="https://github.com/user-attachments/assets/eaec38f3-362f-4ac3-bb92-aed715a93c4d" />

<img width="1890" height="905" alt="Screenshot 2026-07-08 203231" src="https://github.com/user-attachments/assets/46503b17-a1cc-4b4a-82bc-e8570dc7aab2" />

### Product Demand Segments
<img width="1897" height="897" alt="Screenshot 2026-07-08 203308" src="https://github.com/user-attachments/assets/3bd1533c-de10-43c4-a35e-89778df25502" />

<img width="1187" height="863" alt="Screenshot 2026-07-08 203336" src="https://github.com/user-attachments/assets/71d2ff79-2755-49b5-b8dd-142054ef949a" />

<img width="1885" height="900" alt="Screenshot 2026-07-08 203405" src="https://github.com/user-attachments/assets/400add58-fd57-42c7-989e-22bb87160ca7" />

## Author

**Yashti Choudhary**

Developed as part of the **XYLOFY AI Data Science Internship**.
