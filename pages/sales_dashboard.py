import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import sys

# Import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

# Styling for Title with Linear Gradient
st.markdown("""
    <h1>📊 <span class="gradient-title-sales">Sales Overview Dashboard</span></h1>
    <p style='font-size: 1.05rem; color: #64748B; font-weight: 400; margin-top: 0px; margin-bottom: 1.5rem;'>
        Monitor historical sales performance, transaction volume, and geographic distribution across product categories.
    </p>
""", unsafe_allow_html=True)
st.divider()

# Load dataset
DATA_PATH = "train.csv"
df_raw = utils.load_csv(DATA_PATH)

# Fallback synthetic dataset
if df_raw.empty:
    st.warning("⚠️ Using synthetic fallback data: 'train.csv' could not be loaded or is empty.")
    np.random.seed(42)
    dummy_dates = pd.date_range(start="2015-01-01", end="2018-12-31", freq="D")
    n_rows = 2500
    df = pd.DataFrame({
        'Row ID': range(1, n_rows + 1),
        'Order ID': [f"CA-{np.random.randint(2015, 2019)}-{np.random.randint(100000, 999999)}" for _ in range(n_rows)],
        'Order Date': np.random.choice(dummy_dates, n_rows),
        'Region': np.random.choice(['West', 'East', 'Central', 'South'], n_rows, p=[0.35, 0.30, 0.20, 0.15]),
        'Category': np.random.choice(['Furniture', 'Office Supplies', 'Technology'], n_rows, p=[0.25, 0.55, 0.20]),
        'Sales': np.round(np.random.exponential(scale=180.0, size=n_rows) + 4.95, 2)
    })
    df['Order Date'] = pd.to_datetime(df['Order Date'])
else:
    df = df_raw.copy()
    try:
        df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
        if df['Order Date'].isnull().all():
            df['Order Date'] = pd.to_datetime(df_raw['Order Date'], errors='coerce')
    except Exception:
        df['Order Date'] = pd.to_datetime(df_raw['Order Date'], errors='coerce')
    df = df.dropna(subset=['Order Date'])

# Preprocess dates
df['Year'] = df['Order Date'].dt.year.astype(int)
df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)

# Sidebar filters
st.sidebar.markdown("### 🎛️ Dashboard Filters")
regions_list = sorted(list(df['Region'].dropna().unique()))
categories_list = sorted(list(df['Category'].dropna().unique()))

# Region selection logic with "Show All" checkbox and contextual multiselect
show_all_regions = st.sidebar.checkbox("Show All Regions", value=True, help="Display data for all regions.")

if show_all_regions:
    selected_regions = regions_list
    st.sidebar.multiselect(
        "Region Selection:",
        options=regions_list,
        default=[],
        disabled=True,
        help="Uncheck 'Show All Regions' above to filter specific regions."
    )
else:
    selected_regions = st.sidebar.multiselect(
        "Region Selection:",
        options=regions_list,
        default=[regions_list[0]], # Default to first option to avoid empty chart state
        help="Select one or more regions."
    )

# Category selection logic with "Show All" checkbox and contextual multiselect
show_all_categories = st.sidebar.checkbox("Show All Categories", value=True, help="Display data for all categories.")

if show_all_categories:
    selected_categories = categories_list
    st.sidebar.multiselect(
        "Category Selection:",
        options=categories_list,
        default=[],
        disabled=True,
        help="Uncheck 'Show All Categories' above to filter specific categories."
    )
else:
    selected_categories = st.sidebar.multiselect(
        "Category Selection:",
        options=categories_list,
        default=[categories_list[0]], # Default to first option to avoid empty chart state
        help="Select one or more categories."
    )

# Apply filters
filtered_df = df[df['Region'].isin(selected_regions) & df['Category'].isin(selected_categories)]

# Validate filters
if filtered_df.empty:
    st.error("❌ No data matches the selected filters. Please adjust your criteria.")
else:
    # Calculations
    total_sales = filtered_df['Sales'].sum()
    total_orders = filtered_df['Order ID'].nunique()
    avg_sales = filtered_df['Sales'].mean()
    num_regions = filtered_df['Region'].nunique()

    # Custom HTML Card Render Function with vibrant gradients and micro-hover effect
    def render_kpi_card(label, value, icon, color_start, color_end):
        return f"""
        <div style="
            background: linear-gradient(135deg, {color_start} 0%, {color_end} 100%);
            padding: 1.3rem;
            border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: transform 0.2s ease-in-out;
            border: 1px solid rgba(255, 255, 255, 0.1);
        " class="kpi-card">
            <div>
                <div style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; opacity: 0.85;">{label}</div>
                <div style="font-size: 1.65rem; font-weight: 800; margin-top: 0.4rem; letter-spacing: -0.5px;">{value}</div>
            </div>
            <div style="font-size: 2.1rem; background: rgba(255, 255, 255, 0.2); width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 12px;">{icon}</div>
        </div>
        """

    # Injecting CSS for card hovers
    st.markdown("""
        <style>
            .kpi-card:hover {
                transform: translateY(-4px) !important;
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.12) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Render cards in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_kpi_card("Total Sales", f"${total_sales:,.2f}", "💵", "#6366F1", "#4338CA"), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card("Total Orders", f"{total_orders:,}", "📦", "#10B981", "#047857"), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi_card("Average Order Value", f"${avg_sales:,.2f}", "🏷️", "#F59E0B", "#B45309"), unsafe_allow_html=True)
    with col4:
        st.markdown(render_kpi_card("Regions Selected", f"{num_regions}", "🌍", "#EC4899", "#BE185D"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Layout for Charts
    c_row1_1, c_row1_2 = st.columns(2)
    c_row2_1, c_row2_2 = st.columns(2)

    # 1. Total Sales by Year (Bar Chart)
    with c_row1_1:
        st.markdown("<div class='section-header'>Annual Sales Growth</div>", unsafe_allow_html=True)
        yearly_sales = filtered_df.groupby('Year')['Sales'].sum().reset_index()
        fig_year = px.bar(
            yearly_sales,
            x='Year',
            y='Sales',
            color='Sales',
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={'Sales': 'Sales ($)', 'Year': 'Year'},
            text_auto='.3s'
        )
        fig_year.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(type='category', showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
            coloraxis_showscale=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=320
        )
        st.plotly_chart(fig_year, use_container_width=True)

    # 2. Monthly Sales Trend (Interactive Line Chart)
    with c_row1_2:
        st.markdown("<div class='section-header'>Monthly Sales Trend</div>", unsafe_allow_html=True)
        monthly_sales = filtered_df.groupby('YearMonth')['Sales'].sum().reset_index().sort_values('YearMonth')
        fig_month = px.line(
            monthly_sales,
            x='YearMonth',
            y='Sales',
            labels={'Sales': 'Sales ($)', 'YearMonth': 'Period'},
            markers=True
        )
        fig_month.update_traces(
        line=dict(color="#8B5CF6", width=3),
        marker=dict(
        size=7,
        color="#D946EF",
        line=dict(
            color="white",
            width=1.5
                )
            )
        )
        fig_month.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, tickangle=45),
            yaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
            margin=dict(t=10, b=10, l=10, r=10),
            height=320
        )
        st.plotly_chart(fig_month, use_container_width=True)

    # 3. Sales by Region (Donut Chart)
    with c_row2_1:
        st.markdown("<div class='section-header'>Regional Distribution</div>", unsafe_allow_html=True)
        region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
        fig_region = px.pie(
            region_sales,
            values='Sales',
            names='Region',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_region.update_traces(textposition='inside', textinfo='percent+label')
        fig_region.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            height=320,
            showlegend=False
        )
        st.plotly_chart(fig_region, use_container_width=True)

    # 4. Sales by Category (Donut Chart)
    with c_row2_2:
        st.markdown("<div class='section-header'>Category Share</div>", unsafe_allow_html=True)
        category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
        fig_category = px.pie(
            category_sales,
            values='Sales',
            names='Category',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_category.update_traces(textposition='inside', textinfo='percent+label')
        fig_category.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            height=320,
            showlegend=False
        )
        st.plotly_chart(fig_category, use_container_width=True)

# Expander
with st.expander("ℹ️ Data Processing & Methodology Notes"):
    st.markdown("""
    - **Data Source**: Loaded from `train.csv` (representing transactional store history).
    - **KPI Definitions**:
        - **Total Sales**: Cumulative sum of the transaction values (`Sales`) matching selected filters.
        - **Total Orders**: Count of unique `Order ID` fields, accounting for multi-item orders.
        - **Avg. Ticket Size**: Mean value of items purchased in filtered transactions.
    - **Future Enhancements (TODO)**:
        - Link directly to live snowflake database table containing near real-time retail ERP exports.
        - Implement pipeline triggers that update this view dynamically when new batches of transaction CSVs arrive.
    """)
