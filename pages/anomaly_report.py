import streamlit as st
import pandas as pd
import os
import sys

# Import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Styling for Title with Linear Gradient
st.markdown("""
    <h1>🚨 <span class="gradient-title-anomaly">Sales Anomaly Detection</span></h1>
    <p style='font-size: 1.05rem; color: #64748B; font-weight: 400; margin-top: 0px; margin-bottom: 1.5rem;'>
        Identify and investigate unusual spikes or drops in weekly sales performance using machine learning and statistical methods.
    </p>
""", unsafe_allow_html=True)
st.divider()

# Paths
IF_CSV_PATH = "saved_outputs/if_anomalies.csv"
IF_IMAGE_PATH = "saved_outputs/isolation_forest_anomalies.png"
ZSCORE_IMAGE_PATH = "saved_outputs/zscore_anomalies.png"
ZSCORE_CSV_PATH = "saved_outputs/z_anomalies.csv"

# Method selector in columns or radio buttons
method = st.radio(
    "Select Anomaly Detection Method:",
    options=["Isolation Forest", "Rolling Z-Score"],
    index=0,
    horizontal=True,
    help="Toggle between unsupervised machine learning (Isolation Forest) and statistical thresholding (Rolling Z-Score)."
)

# Display corresponding image based on selection
st.markdown("<div class='section-header'>Anomaly Visualization Chart</div>", unsafe_allow_html=True)
if method == "Isolation Forest":
    if os.path.exists(IF_IMAGE_PATH):
        st.image(IF_IMAGE_PATH, caption="Isolation Forest Anomaly Highlights (Outliers in Red)", use_container_width=True)
    else:
        st.warning(f"⚠️ Isolation Forest visualization not found at `{IF_IMAGE_PATH}`. Please check your pipeline outputs.")
else:
    if os.path.exists(ZSCORE_IMAGE_PATH):
        st.image(ZSCORE_IMAGE_PATH, caption="Rolling Z-Score Anomaly Highlights (Outliers in Red)", use_container_width=True)
    else:
        st.warning(f"⚠️ Rolling Z-Score visualization not found at `{ZSCORE_IMAGE_PATH}`. Please check your pipeline outputs.")

st.markdown("---")

# Display corresponding anomaly table
st.markdown("<div class='section-header'>Detected Anomalies Table</div>", unsafe_allow_html=True)

# Load anomalies
if method == "Isolation Forest":
    anomalies_df = utils.load_csv(IF_CSV_PATH)
    if not anomalies_df.empty:
        # Prepare table
        display_df = anomalies_df.copy()
        if 'Order Date' in display_df.columns:
            display_df = display_df.rename(columns={'Order Date': 'Date'})
        else:
            display_df['Date'] = display_df.index
            
        display_df['Method'] = "Isolation Forest"
        
        # Select target columns
        target_cols = ['Date', 'Sales', 'Method']
        target_cols = [col for col in target_cols if col in display_df.columns]
        table_df = display_df[target_cols]
        
        # Style dataframe with colorful alert borders
        st.dataframe(
            table_df.style.format({'Sales': '${:,.2f}'}),
            use_container_width=True
        )
        st.markdown(f"""
            <div style='background-color: rgba(239, 68, 68, 0.08); border-left: 4px solid #EF4444; padding: 1rem; border-radius: 8px;'>
                <p style='margin:0; font-size:0.92rem; color: #991B1B; font-weight:600;'>
                    💡 Detected <b>{len(table_df)}</b> major anomalies using the Isolation Forest algorithm. 
                    These dates represent high probability sales outliers.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No Isolation Forest anomalies loaded. Ensure 'saved_outputs/anomalies.csv' is generated and populated.")

else: # Rolling Z-Score selected
    zscore_df = utils.load_csv(ZSCORE_CSV_PATH)
    if not zscore_df.empty:
        display_df = zscore_df.copy()

        if 'Order Date' in display_df.columns:
            display_df = display_df.rename(columns={'Order Date': 'Date'})
        else:
            display_df['Date'] = display_df.index

        display_df['Method'] = "Rolling Z-Score"

        target_cols = ['Date', 'Sales', 'Method']
        target_cols = [c for c in target_cols if c in display_df.columns]

        st.dataframe(
            display_df[target_cols].style.format({'Sales': '${:,.2f}'}),
            use_container_width=True
        )

        st.markdown(f"""
        <div style='background-color: rgba(245,158,11,0.08);
                    border-left:4px solid #F59E0B;
                    padding:1rem;
                    border-radius:8px;'>
            <p style='margin:0;font-size:0.92rem;
                    color:#92400E;font-weight:600;'>
                💡 Detected <b>{len(display_df)}</b> anomalies using the
                Rolling Z-Score method.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No Rolling Z-Score anomalies found. Ensure 'saved_outputs/z_anomalies.csv' is generated and populated.")

# Diagnostic Insights Expander
with st.expander("🔍 Anomaly Detection & Mitigation Guide"):
    st.markdown("""
    ### Business Implications of Anomalies
    Anomalies represent critical events in retail sales operations. They can be classified into:
    1. **Demand Spikes**: Caused by corporate purchase orders, bulk institutional buys, or successful promotion campaigns (e.g. March 2015, September 2015).
    2. **Demand Drops**: Caused by supply chain disruptions, warehouse inventory stockouts, or calendar disruptions (e.g. holidays or post-holiday lulls).
    
    ### How to Respond
    * **Spikes**: Analyze underlying product sub-categories to identify high-volume accounts and prepare buffers for future seasons.
    * **Drops**: Check ERP logs for delivery delays or logistics failures on the flagged dates.
    """)
