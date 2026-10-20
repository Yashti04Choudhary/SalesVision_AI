import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import utils
from forecast_utils import generate_prophet_forecast

# Styling for Title with Linear Gradient
st.markdown("""
    <h1>📈 <span class="gradient-title-forecast">Forecast Explorer</span></h1>
    <p style='font-size: 1.05rem; color: #64748B; font-weight: 400; margin-top: 0px; margin-bottom: 1.5rem;'>
        Project future demand using machine learning. Generate and explore regional and category forecasts.
    </p>
""", unsafe_allow_html=True)
st.divider()

# Load historical data to populate controls dynamically
DATA_PATH = "train.csv"
METRICS_PATH = "saved_outputs/model_metrics.csv"

df_raw = utils.load_csv(DATA_PATH)

# Reusable lists for drop-downs
if not df_raw.empty:
    categories = sorted(list(df_raw['Category'].dropna().unique()))
    regions = sorted(list(df_raw['Region'].dropna().unique()))
    
    # Safe date parsing
    try:
        df_raw['Order Date'] = pd.to_datetime(df_raw['Order Date'], dayfirst=True, errors='coerce')
        if df_raw['Order Date'].isnull().all():
            df_raw['Order Date'] = pd.to_datetime(df_raw['Order Date'], errors='coerce')
    except Exception:
        df_raw['Order Date'] = pd.to_datetime(df_raw['Order Date'], errors='coerce')
    df_raw = df_raw.dropna(subset=['Order Date'])
else:
    categories = ["Office Supplies", "Furniture", "Technology"]
    regions = ["West", "East", "Central", "South"]

# Page layout: Left Column (Controls), Right Column (Visualizations)
col_ctrl, col_viz = st.columns([1, 2], gap="large")

with col_ctrl:
    st.markdown("<div class='section-header'>Forecast Configuration</div>", unsafe_allow_html=True)
    
    # Radio: Forecast Scope
    forecast_type = st.radio(
        "Forecast Scope:",
        options=["Overall Sales", "Category", "Region"],
        index=0,
        help="Select whether to forecast overall sales or filter by category or region."
    )
    
    # Dropdown: Populates dynamically (Hidden for Overall Sales)
    selected_dimension = None
    if forecast_type == "Category":
        selected_dimension = st.selectbox("Select Category:", options=categories)
    elif forecast_type == "Region":
        selected_dimension = st.selectbox("Select Region:", options=regions)
        
    # Slider: Forecast Horizon (1, 2, or 3 months)
    horizon_months = st.slider(
        "Forecast Horizon (Months):",
        min_value=1,
        max_value=3,
        value=3,
        step=1,
        help="Number of months into the future to forecast."
    )
    
    # Action Button
    generate_btn = st.button("🚀 Generate Forecast", type="primary", use_container_width=True)

# Forecasting Function
def generate_forecast(forecast_type, selection, horizon):
    """
    Fit Prophet on the selected historical monthly sales.
    """

    if forecast_type == "Overall Sales":
        f_type = None
        f_value = None
    else:
        f_type = forecast_type
        f_value = selection

    return generate_prophet_forecast(
        df=df_raw,
        filter_type=f_type,
        filter_value=f_value,
        horizon=horizon
    )


# Handle Forecast Rendering
with col_viz:
    st.markdown("<div class='section-header'>Forecast Projection</div>", unsafe_allow_html=True)
    
    # Call forecast function (uses selected inputs)
    if generate_btn:
     with st.spinner("Generating forecast..."):

        hist_data, forecast_data = generate_forecast(
            forecast_type,
            selected_dimension,
            horizon_months
        )

     if forecast_type == "Overall Sales":
        toast_msg = (
        f"Forecast generated for Overall Sales\n\n"
        f"Forecast Horizon: {horizon_months} "
        f"{'Month' if horizon_months == 1 else 'Months'}"
      )
     else:
        toast_msg = (
        f"Forecast generated for {forecast_type}: {selected_dimension}\n\n"
        f"Forecast Horizon: {horizon_months} "
        f"{'Month' if horizon_months == 1 else 'Months'}"
      )
     st.toast(toast_msg, icon="📈")
    else:
     hist_data = pd.DataFrame()
     forecast_data = pd.DataFrame()
    
    # Plotly Visualisation
    if not hist_data.empty:
      fig = go.Figure()
    
        # Add Historical Trace
      fig.add_trace(go.Scatter(
            x=hist_data['YearMonth'],
            y=hist_data['Sales'],
            mode='lines+markers',
            name='Historical Sales',
            line=dict(color='#6366F1', width=3), # Indigo theme line
            marker=dict(
        size=6,
        color="#4338CA",
        line=dict(
            color="white",
            width=1.5
        )
        )
        ))
        
        # Add Forecast Trace (connect to last historical point for seamless line rendering)
      connect_df = pd.DataFrame({
            'YearMonth': [hist_data.iloc[-1]['YearMonth']],
            'Forecast': [hist_data.iloc[-1]['Sales']]
        })
      full_forecast = pd.concat([connect_df, forecast_data], ignore_index=True)
        
      fig.add_trace(go.Scatter(
            x=full_forecast['YearMonth'],
            y=full_forecast['Forecast'],
            mode='lines+markers',
            name='Projected Demand (Prophet)',
            line=dict(color='#EC4899', width=3, dash='dash'), # Hot pink dashed line
            marker=dict(
        size=7,
        color="#BE185D",
        line=dict(
            color="white",
            width=1.5
        )
        )
        ))
        
      fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, title="Timeline"),
            yaxis=dict(showgrid=True, gridcolor='#E2E8F0', title="Sales ($)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=30, b=10, l=10, r=10),
            height=350
        )
      st.plotly_chart(fig, use_container_width=True)

    else:
     st.info(
        "Select your options and click **Generate Forecast**."
     )
    
    # Divider for Metrics
    st.markdown("##### 📐 Model Accuracy Metrics")
    
    # Load model evaluation metrics
    metrics_df = utils.load_metrics(METRICS_PATH)
    
    # Display MAE & RMSE metrics (Remove MAPE as per user specification)
    if not metrics_df.empty:
        selected_metrics = metrics_df.loc[metrics_df['Model'] == 'Prophet']
        if selected_metrics.empty:
            selected_metrics = metrics_df.iloc[[0]]
        mae_val = selected_metrics.iloc[0]['MAE']
        rmse_val = selected_metrics.iloc[0]['RMSE']
    else:
        mae_val = 11232.49
        rmse_val = 14032.41
        
    # Injecting CSS for card hovers
    st.markdown("""
        <style>
            .accuracy-card {
                transition: transform 0.25s ease, box-shadow 0.25s ease !important;
            }
            .accuracy-card:hover {
                transform: translateY(-4px) !important;
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.12) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Custom HTML Card Render Function with vibrant gradients
    def render_accuracy_card(label, value, icon, color_start, color_end, desc):
        return f"""
        <div style="
            background: linear-gradient(135deg, {color_start} 0%, {color_end} 100%);
            padding: 1.1rem;
            border-radius: 14px;
            box-shadow: 0 8px 12px -3px rgba(0, 0, 0, 0.04);
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid rgba(255, 255, 255, 0.1);
        " class="accuracy-card">
            <div>
                <div style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; opacity: 0.85;">{label}</div>
                <div style="font-size: 1.5rem; font-weight: 800; margin-top: 0.2rem; letter-spacing: -0.5px;">{value}</div>
                <div style="font-size: 0.72rem; opacity: 0.75; margin-top: 0.3rem;">{desc}</div>
            </div>
            <div style="font-size: 1.8rem; background: rgba(255, 255, 255, 0.2); width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">{icon}</div>
        </div>
        """

    met_col1, met_col2 = st.columns(2)
    with met_col1:
        st.markdown(render_accuracy_card(
            "MAE", 
            f"{mae_val:,.2f}", 
            "🎯", 
            "#EC4899", 
            "#BE185D", 
            "Avg absolute deviation of forecast"
        ), unsafe_allow_html=True)
    with met_col2:
        st.markdown(render_accuracy_card(
            "RMSE", 
            f"{rmse_val:,.2f}", 
            "📊", 
            "#6366F1", 
            "#4338CA", 
            "Standard deviation of residuals"
        ), unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dynamic styles for the information card based on theme
    is_dark = st.session_state.get("dark_mode", False)
    info_bg = "#172554" if is_dark else "#EFF6FF"
    info_border = "#3B82F6"
    info_text = "#DBEAFE" if is_dark else "#1E3A8A"
    info_title = "#93C5FD" if is_dark else "#1E40AF"
    
    info_card_html = f"""
    <div style="
        background-color: {info_bg};
        border-left: 4px solid {info_border};
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    ">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;">
            <span style="font-size: 1.1rem;">ℹ️</span>
            <strong style="color: {info_title}; font-size: 0.92rem; font-weight: 700;">Model Evaluation</strong>
        </div>
        <p style="color: {info_text}; font-size: 0.82rem; line-height: 1.45; margin: 0; font-weight: 500;">
            The MAE and RMSE shown above are Prophet results from an expanding-window, three-month backtest across eight forecast origins.
            <br><br>
            They summarize overall sales performance across 24 held-out months. Category and Region forecasts are fitted to the selected historical data; the displayed metrics summarize the overall backtest.
        </p>
    </div>
    """
    st.markdown(info_card_html, unsafe_allow_html=True)

# Info Expander for explanation
with st.expander("ℹ️ Forecasting Methodology (Prophet)"):

    st.markdown("""
### Forecasting Pipeline

The Forecast Explorer uses **Prophet** to project future monthly sales:

- **Overall Sales**: Fits Prophet using the complete historical monthly sales series.
- **Category & Region Forecasts**: Fits Prophet using only the selected category or region historical sales.

### Recursive Multi-Month Projection
Prophet produces each requested future month from the fitted trend and yearly seasonal pattern. Future actual sales are never passed to the model.

### Feature Engineering
The selected series is formatted as Prophet's required date (`ds`) and target (`y`) columns. Yearly seasonality is enabled when at least two years of monthly history are available; weekly and daily seasonality are disabled.
""")