import streamlit as st
import pandas as pd
import os
import sys

# Import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Styling for Title with Linear Gradient
st.markdown("""
    <h1>🎯 <span class="gradient-title-segments">Demand Segmentation</span></h1>
    <p style='font-size: 1.05rem; color: #64748B; font-weight: 400; margin-top: 0px; margin-bottom: 1.5rem;'>
        Categorize product sub-categories into clusters based on volume, growth profile, volatility, and order value.
    </p>
""", unsafe_allow_html=True)
st.divider()

# Paths
CLUSTER_IMAGE_PATH = "charts/cluster_plot.png"
CLUSTER_CSV_PATH = "saved_outputs/cluster_results.csv"

# Top: Display cluster visualization
st.markdown("<div class='section-header'>Cluster Visualization (K-Means Clustering)</div>", unsafe_allow_html=True)
if os.path.exists(CLUSTER_IMAGE_PATH):
    st.image(CLUSTER_IMAGE_PATH, caption="Sub-Category Demand Segments projected in PCA Space", use_container_width=True)
else:
    st.warning(f"⚠️ Cluster visualization plot not found at `{CLUSTER_IMAGE_PATH}`. Please run clustering pipeline to generate this chart.")

st.markdown("---")

# Bottom: Interactive table
st.markdown("<div class='section-header'>Demand Segmentation Analysis Table</div>", unsafe_allow_html=True)

# TODO: Load cluster_results.csv which contains output metrics of the clustering notebook
cluster_df = utils.load_csv(CLUSTER_CSV_PATH)

if not cluster_df.empty:
    # Rename columns to match requested names
    column_mapping = {
        'Sub-Category': 'Sub Category',
        'Cluster': 'Cluster',
        'Total_Sales': 'Total Sales',
        'Growth_Rate': 'Growth Rate',
        'Volatility': 'Volatility',
        'Average_Order_Value': 'Average Order Value'
    }
    
    # Apply mapping
    renamed_df = cluster_df.rename(columns=column_mapping)
    
    # Target columns
    display_cols = ['Sub Category', 'Cluster', 'Total Sales', 'Growth Rate', 'Volatility', 'Average Order Value']
    display_cols = [col for col in display_cols if col in renamed_df.columns]
    
    final_df = renamed_df[display_cols].copy()
    
    # Dynamic Cluster Filter
    all_clusters = sorted(list(final_df['Cluster'].unique()))
    selected_clusters = st.multiselect(
        "Filter by Cluster Segments:",
        options=all_clusters,
        default=all_clusters,
        help="Select which demand clusters to focus on."
    )
    
    # Filter table
    filtered_table = final_df[final_df['Cluster'].isin(selected_clusters)]
    
    # Sort options
    sort_col = st.selectbox(
        "Sort Table By:",
        options=display_cols,
        index=0
    )
    sort_order = st.radio("Sort Order:", options=["Ascending", "Descending"], index=1, horizontal=True)
    
    filtered_table = filtered_table.sort_values(by=sort_col, ascending=(sort_order == "Ascending"))
    
    # Style and format columns
    styled_table = filtered_table.style.format({
        'Total Sales': '${:,.2f}',
        'Growth Rate': '{:.2f}%',
        'Volatility': '{:,.2f}',
        'Average Order Value': '${:,.2f}'
    })
    
    # Display table
    st.dataframe(styled_table, use_container_width=True)
    
    # Summary of cluster descriptions styled as beautiful themed cards
    st.markdown("##### 📝 Cluster Profile Explanations")
    
    def render_profile_card(title, body, color_hex, bg_rgba):
        return f"""
        <div style='background-color: {bg_rgba}; border-left: 4px solid {color_hex}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; height: 90%;'>
            <h5 style='color: {color_hex}; margin: 0 0 0.4rem 0; font-weight: 700; font-size: 0.95rem;'>{title}</h5>
            <p style='margin: 0; font-size: 0.85rem; color: #334155; line-height: 1.4;'>{body}</p>
        </div>
        """
        
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.markdown(render_profile_card(
            "Cluster 0: High-Volume Stabilizers",
            "High Total Sales, low to moderate growth rate, and stable volatility. Represents core product offerings (e.g., Phones, Chairs, Storage) with highly predictable demand.",
            "#6366F1", "rgba(99, 102, 241, 0.07)"
        ), unsafe_allow_html=True)
        st.markdown(render_profile_card(
            "Cluster 2: Low-Volume Long-Tail",
            "Lower overall sales but steady transaction volume. Often inexpensive items or low growth category fillers (e.g., Art, Fasteners, Envelopes) that require basic inventory management.",
            "#F59E0B", "rgba(245, 158, 11, 0.07)"
        ), unsafe_allow_html=True)
    with c_col2:
        st.markdown(render_profile_card(
            "Cluster 1: High-Growth Rockets",
            "Outstanding Growth Rate, high volatility, and strong average order value. These are high-margin, emerging items (e.g., Copiers) representing volatile, seasonal spikes.",
            "#10B981", "rgba(16, 185, 129, 0.07)"
        ), unsafe_allow_html=True)
        st.markdown(render_profile_card(
            "Cluster 3: High-Value Capital Units",
            "High Average Order Value, negative or highly volatile growth rates. These are capital-intensive machines with sporadic transaction intervals (e.g., Machines) requiring project-based fulfillment.",
            "#EC4899", "rgba(236, 72, 153, 0.07)"
        ), unsafe_allow_html=True)

else:
    st.warning("⚠️ No cluster segmentation data loaded. Ensure 'saved_outputs/cluster_results.csv' is generated and populated.")
    
    # Placeholder table for preview purposes
    st.info("💡 Displaying placeholder segmentation layout.")
    placeholder_df = pd.DataFrame([
        {"Sub Category": "Copiers", "Cluster": 1, "Total Sales": 146248.09, "Growth Rate": 479.73, "Volatility": 5500.77, "Average Order Value": 2215.88},
        {"Sub Category": "Phones", "Cluster": 0, "Total Sales": 327782.45, "Growth Rate": 35.56, "Volatility": 4052.72, "Average Order Value": 374.18},
        {"Sub Category": "Fasteners", "Cluster": 2, "Total Sales": 3001.96, "Growth Rate": 30.47, "Volatility": 48.74, "Average Order Value": 14.03}
    ])
    st.dataframe(
        placeholder_df.style.format({
            'Total Sales': '${:,.2f}',
            'Growth Rate': '{:.2f}%',
            'Volatility': '{:,.2f}',
            'Average Order Value': '${:,.2f}'
        }),
        use_container_width=True
    )
