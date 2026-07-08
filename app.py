import streamlit as st
import os

# Set page config (MUST be called only once, at the start of the main script)
st.set_page_config(
    page_title="SalesVision AI - Sales Analytics & Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for Active Workspace/Tab & Theme
if 'top_tab' not in st.session_state:
    st.session_state.top_tab = "Executive Overview"

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Base CSS (shared across themes)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Apply modern typography globally */
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Shift main container up to eliminate gap at the top */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        pointer-events: none; /* Make header clicks pass through to content */
    }
    header[data-testid="stHeader"] button {
        pointer-events: auto; /* Enable sidebar toggle clicks */
    }
    section.main {
        z-index: 999999 !important;
    }
    .main .block-container {
        padding-top: 0rem !important;
        margin-top: -3.75rem !important;
    }
    
    /* Top Navbar container styling */
    div[data-testid="stVerticalBlock"] > div:first-child > div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        padding: 0.8rem 1.5rem !important;
        margin-bottom: 1.2rem !important;
        transition: all 0.3s ease !important;
    }
    
    /* Custom divider line styling */
    hr {
        margin: 1.2rem 0 !important;
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, rgba(99, 102, 241, 0) 0%, rgba(99, 102, 241, 0.3) 50%, rgba(99, 102, 241, 0) 100%) !important;
    }
    
    /* Top Navbar button general styling */
    div[data-testid="column"] button {
        border-radius: 8px !important;
        height: 42px !important;
        font-family: 'Outfit', sans-serif !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 0.95rem !important;
    }
    
    /* Global Streamlit button styling overrides */
    button[data-testid="baseButton-secondary"], 
    button[data-testid="baseButton-primary"] {
        border-radius: 8px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    button[data-testid="baseButton-secondary"]:hover, 
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08) !important;
    }
    
    /* Theme Toggle circular button styling */
    div[data-testid="column"]:nth-child(6) button {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.15rem !important;
    }
    
    /* User popover avatar styling */
    div[data-testid="column"]:nth-child(7) div[data-testid="stPopover"] button {
        background-color: #6366F1 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.15rem !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2) !important;
    }
    div[data-testid="column"]:nth-child(7) div[data-testid="stPopover"] button svg {
        display: none !important; /* Hide dropdown arrow */
    }
    
    /* Style container headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 1rem;
        padding-left: 12px;
        transition: all 0.3s ease;
    }
    
    /* Gradient text styling for page headers */
    .gradient-title-sales {
        background: linear-gradient(135deg, #6366F1 0%, #06B6D4 100%) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        display: inline-block !important;
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        padding-bottom: 0px;
    }
    .gradient-title-forecast {
        background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        display: inline-block !important;
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        padding-bottom: 0px;
    }
    .gradient-title-anomaly {
        background: linear-gradient(135deg, #EF4444 0%, #F59E0B 100%) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        display: inline-block !important;
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        padding-bottom: 0px;
    }
    .gradient-title-segments {
        background: linear-gradient(135deg, #10B981 0%, #3B82F6 100%) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        display: inline-block !important;
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        padding-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

# Theme-Specific Styles injection
if not st.session_state.dark_mode:
    # ---------------- DAY (LIGHT) THEME STYLE ----------------
    st.markdown("""
    <style>
        /* Top linear gradient accent bar */
        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #6366F1 0%, #EC4899 50%, #06B6D4 100%);
            z-index: 9999999;
        }
        
        /* Vibrant sky blue and lavender wash background for entire app */
        div[data-testid="stAppViewContainer"], 
        section.main {
            background: linear-gradient(135deg, #EEF2F6 0%, #E0E7FF 50%, #E0F2FE 100%) !important;
        }
        
        /* Sidebar light theme with lavender gradient bottom wash */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(245,243,255,0.9) 100%) !important;
            border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
            box-shadow: 2px 0 15px rgba(99, 102, 241, 0.04) !important;
        }
        section[data-testid="stSidebar"] span, 
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #475569 !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] div[role="button"] {
            color: #475569 !important;
        }
        section[data-testid="stSidebar"] div[role="button"]:hover {
            background-color: #ECE9FC !important; /* Soft lavender hover */
            border-left: 3px solid #6366F1 !important;
            padding-left: 12px !important;
            color: #4338CA !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stSidebarNavLinkActive"] {
            background: rgba(99, 102, 241, 0.12) !important;
            border-left: 4px solid #6366F1 !important;
            color: #4F46E5 !important;
            font-weight: 700 !important;
        }
        
        /* Top Navbar container (Glassmorphic) */
        div[data-testid="stVerticalBlock"] > div:first-child > div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.08) !important;
            position: sticky !important;
            top: 0 !important;
            z-index: 999999 !important;
            width: 100vw !important;
            margin-left: calc(-50vw + 50%) !important;
            margin-right: calc(-50vw + 50%) !important;
            border-radius: 0px !important; /* Full width border flush */
        }
        
        /* Brand text styling */
        .brand-title {
            color: #1E293B !important;
        }
        .brand-subtitle {
            color: #64748B !important;
        }
        
        /* Inactive navbar buttons */
        div[data-testid="column"]:nth-child(3) button,
        div[data-testid="column"]:nth-child(4) button {
            background-color: #FFFFFF !important;
            color: #475569 !important;
            border: 1px solid #E2E8F0 !important;
            font-weight: 500 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        }
        div[data-testid="column"]:nth-child(3) button:hover,
        div[data-testid="column"]:nth-child(4) button:hover {
            background-color: #1E3A8A !important; /* Dark Blue */
            border-color: #1E3A8A !important;
            color: #FFFFFF !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.25) !important;
        }
        
        /* Theme Toggle button */
        div[data-testid="column"]:nth-child(6) button {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            color: #F59E0B !important; /* Gold sun */
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        }
        div[data-testid="column"]:nth-child(6) button:hover {
            background-color: #1E3A8A !important; /* Dark Blue */
            border-color: #1E3A8A !important;
            color: #FFFFFF !important;
            transform: scale(1.05) !important;
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2) !important;
        }
        
        /* User popover avatar hover */
        div[data-testid="column"]:nth-child(7) div[data-testid="stPopover"] button:hover {
            background-color: #1E3A8A !important; /* Dark Blue */
            color: #FFFFFF !important;
            transform: scale(1.05) !important;
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.25) !important;
        }
        
        /* Custom styled selectboxes for light mode */
        div[data-baseweb="select"] {
            border-radius: 8px !important;
            border: 1px solid rgba(99, 102, 241, 0.25) !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 2px 4px rgba(99,102,241,0.02) !important;
            transition: all 0.2s ease !important;
        }
        div[data-baseweb="select"]:hover {
            border-color: #6366F1 !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.05) !important;
        }
        
        /* Custom multiselect tag styling (Indigo-Pink gradient) */
        span[data-baseweb="tag"] {
            background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%) !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 6px rgba(99,102,241,0.2) !important;
            border: none !important;
        }
        
        /* Expanders styling in light mode */
        div[data-testid="stExpander"] {
            background-color: #FFFFFF !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stExpander"]:hover {
            box-shadow: 0 6px 15px rgba(99, 102, 241, 0.04) !important;
            border-color: rgba(99, 102, 241, 0.3) !important;
        }
        
        /* Card container styling in light mode */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.03) !important;
            transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        }
        /* Exclude top navbar container from hover lift */
        div[data-testid="stVerticalBlock"] > div:first-child > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: none !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.08) !important;
        }
        
        .section-header {
            color: #0F172A;
            border-left: 4px solid #6366F1;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # ---------------- NIGHT (DARK) THEME STYLE ----------------
    st.markdown("""
    <style>
        /* Top linear gradient accent bar */
        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #F43F5E 0%, #8B5CF6 50%, #3B82F6 100%);
            z-index: 9999999;
        }
        
        /* Deep dark blue/slate cosmic background for entire app */
        div[data-testid="stAppViewContainer"], 
        section.main {
            background: linear-gradient(135deg, #090D1A 0%, #0F172A 50%, #151030 100%) !important;
        }
        
        /* Force texts in main area to be light in dark mode */
        .main p, .main span, .main label, .main h1, .main h2, .main h3, .main h4, .main h5, .main h6, .main li {
            color: #F1F5F9 !important;
        }
        
        /* Sidebar deep dark style */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #090D1A 0%, #151030 100%) !important;
            border-right: 1px solid #1E293B !important;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2) !important;
        }
        section[data-testid="stSidebar"] span, 
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #E2E8F0 !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] div[role="button"] {
            color: #94A3B8 !important;
        }
        section[data-testid="stSidebar"] div[role="button"]:hover {
            background-color: #1E293B !important;
            border-left: 3px solid #F43F5E !important;
            padding-left: 12px !important;
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stSidebarNavLinkActive"] {
            background: rgba(244, 63, 94, 0.12) !important;
            border-left: 4px solid #F43F5E !important;
            color: #F43F5E !important;
            font-weight: 700 !important;
        }
        
        /* Top Navbar container in dark mode (Glassmorphic Dark) */
        div[data-testid="stVerticalBlock"] > div:first-child > div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: rgba(21, 16, 48, 0.8) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(244, 63, 94, 0.15) !important;
            box-shadow: 0 10px 35px rgba(0, 0, 0, 0.4) !important;
            position: sticky !important;
            top: 0 !important;
            z-index: 999999 !important;
            width: 100vw !important;
            margin-left: calc(-50vw + 50%) !important;
            margin-right: calc(-50vw + 50%) !important;
            border-radius: 0px !important; /* Full width border flush */
        }
        
        /* Brand text styling */
        .brand-title {
            color: #FFFFFF !important;
        }
        .brand-subtitle {
            color: #94A3B8 !important;
        }
        
        /* Inactive navbar buttons in dark mode */
        div[data-testid="column"]:nth-child(3) button,
        div[data-testid="column"]:nth-child(4) button {
            background-color: rgba(21, 16, 48, 0.6) !important;
            color: #94A3B8 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            font-weight: 500 !important;
        }
        div[data-testid="column"]:nth-child(3) button:hover,
        div[data-testid="column"]:nth-child(4) button:hover {
            background-color: #38BDF8 !important; /* Light Blue */
            border-color: #38BDF8 !important;
            color: #0B0F19 !important; /* Dark Text */
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3) !important;
        }
        
        /* Theme Toggle button in dark mode */
        div[data-testid="column"]:nth-child(6) button {
            background-color: rgba(21, 16, 48, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #818CF8 !important; /* Indigo moon */
        }
        div[data-testid="column"]:nth-child(6) button:hover {
            background-color: #38BDF8 !important; /* Light Blue */
            border-color: #38BDF8 !important;
            color: #0B0F19 !important;
            transform: scale(1.05) !important;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2) !important;
        }
        
        /* User popover avatar hover in dark mode */
        div[data-testid="column"]:nth-child(7) div[data-testid="stPopover"] button:hover {
            background-color: #38BDF8 !important; /* Light Blue */
            color: #0B0F19 !important;
            transform: scale(1.05) !important;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3) !important;
        }
        
        /* Custom styled selectboxes for dark mode */
        div[data-baseweb="select"] {
            border-radius: 8px !important;
            border: 1px solid #334155 !important;
            background-color: #171F30 !important;
            transition: all 0.2s ease !important;
        }
        div[data-baseweb="select"]:hover {
            border-color: #F43F5E !important;
            box-shadow: 0 4px 12px rgba(244, 63, 94, 0.1) !important;
        }
        div[data-baseweb="select"] div {
            color: #F1F5F9 !important; /* Input text color */
        }
        div[role="listbox"] {
            background-color: #171F30 !important; /* Dropdown popup background */
            border: 1px solid #334155 !important;
        }
        div[role="listbox"] li {
            color: #E2E8F0 !important;
        }
        div[role="listbox"] li:hover {
            background-color: #1E293B !important;
        }
        
        /* Sliders styling in dark mode */
        div[data-testid="stSlider"] {
            color: #F1F5F9 !important;
        }
        div[data-testid="stSlider"] div[role="slider"] {
            background-color: #F43F5E !important; /* Rose slider handle */
        }
        
        /* Expanders styling in dark mode */
        div[data-testid="stExpander"] {
            background-color: #171F30 !important;
            border: 1px solid #1E293B !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stExpander"]:hover {
            border-color: rgba(244, 63, 94, 0.3) !important;
            box-shadow: 0 6px 15px rgba(244, 63, 94, 0.08) !important;
        }
        div[data-testid="stExpander"] details {
            color: #F1F5F9 !important;
        }
        
        /* Custom multiselect tag styling in dark mode (Neon Rose-Purple gradient) */
        span[data-baseweb="tag"] {
            background: linear-gradient(135deg, #F43F5E 0%, #8B5CF6 100%) !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3) !important;
            border: none !important;
        }
        
        .section-header {
            color: #FFFFFF !important;
            border-left: 4px solid #F43F5E !important; /* Rose accent */
        }
        
        /* Style Plotly text in dark mode globally via SVG text fills */
        .js-plotly-plot .xtick text, 
        .js-plotly-plot .ytick text, 
        .js-plotly-plot .gtitle, 
        .js-plotly-plot .legendtext,
        .js-plotly-plot .g-xtitle text,
        .js-plotly-plot .g-ytitle text {
            fill: #E2E8F0 !important;
        }
        
        /* Custom styles for Streamlit DataFrames in dark mode */
        div[data-testid="stDataFrame"] {
            background-color: #171F30 !important;
            border: 1px solid #1E293B !important;
        }
        div[data-testid="stDataFrame"] td, 
        div[data-testid="stDataFrame"] th {
            color: #E2E8F0 !important;
            border-color: #1E293B !important;
        }
        
        /* Card container styling in dark mode */
        div[data-testid="stMetric"], 
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #171F30 !important;
            border: 1px solid #1E293B !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
            transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        }
        /* Exclude top navbar container from hover lift */
        div[data-testid="stVerticalBlock"] > div:first-child > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: none !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(244, 63, 94, 0.15) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Dynamic CSS to style the active tab
active_btn = 3 if st.session_state.top_tab == "Executive Overview" else 4
active_gradient = "linear-gradient(135deg, #F43F5E 0%, #BE123C 100%)" if st.session_state.dark_mode else "linear-gradient(135deg, #6366F1 0%, #EC4899 100%)"
active_shadow = "rgba(244, 63, 94, 0.3)" if st.session_state.dark_mode else "rgba(99, 102, 241, 0.25)"

# Dynamic active button hover style (vice versa hover matching)
if not st.session_state.dark_mode:
    # Day mode active button hovers to Dark Blue
    active_hover_style = """
        background: #1E3A8A !important;
        border-color: #1E3A8A !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.25) !important;
    """
else:
    # Night mode active button hovers to Light Blue
    active_hover_style = """
        background: #38BDF8 !important;
        border-color: #38BDF8 !important;
        color: #0B0F19 !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3) !important;
    """

st.markdown(f"""
<style>
    div[data-testid="column"]:nth-child({active_btn}) button {{
        background: {active_gradient} !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 10px {active_shadow} !important;
    }}
    div[data-testid="column"]:nth-child({active_btn}) button:hover {{
        {active_hover_style}
    }}
</style>
""", unsafe_allow_html=True)

# Define top bar layout inside a bordered container
with st.container(border=True):
    col_brand, col_space, col_tab1, col_tab2, col_space2, col_theme, col_user = st.columns(
        [2.5, 0.2, 1.8, 1.8, 1.2, 0.6, 0.9]
    )
    
    # Left: Brand section (SalesVision AI)
    with col_brand:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding-top: 2px;">
            <span style="font-size: 1.8rem; line-height: 1;">🔮</span>
            <div style="display: flex; flex-direction: column; line-height: 1.1;">
                <span class="brand-title" style="font-size: 1.1rem; font-weight: 800; letter-spacing: -0.3px; transition: all 0.3s ease;">SalesVision AI</span>
                <span class="brand-subtitle" style="font-size: 0.68rem; font-weight: 600; letter-spacing: 0.2px; transition: all 0.3s ease;">Intelligent Sales Analytics & Forecasting Dashboard</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Center: Two Navigation Tabs
    with col_tab1:
        if st.button("🏠 Executive Overview", key="tab_exec", use_container_width=True):
            st.session_state.top_tab = "Executive Overview"
            st.rerun()
            
    with col_tab2:
        if st.button("📊 Advanced Analytics", key="tab_adv", use_container_width=True):
            st.session_state.top_tab = "Advanced Analytics"
            st.rerun()
            
    # Right Actions: Theme Toggle + User Avatar popover
    with col_theme:
        theme_icon = "☀️" if not st.session_state.dark_mode else "🌙"
        if st.button(theme_icon, key="theme_btn", help="Toggle Dashboard Theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
            
    with col_user:
        user_popover = st.popover("👤", help="User Settings & Profile")
        with user_popover:
            st.markdown("""
            <div style="text-align: center; padding: 0.5rem 0; border-bottom: 1px solid #F1F5F9; margin-bottom: 0.5rem;">
                <div style="font-weight: 700; color: #0F172A; font-size: 0.9rem;">Retail Manager Account</div>
                <div style="font-size: 0.72rem; color: #64748B;">administrator@salesvision.ai</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Placeholder action buttons
            if st.button("👤 View Profile", use_container_width=True):
                st.toast("Profile view requested (placeholder)", icon="👤")
            if st.button("⚙️ System Settings", use_container_width=True):
                st.toast("System settings opened (placeholder)", icon="⚙️")
            st.divider()
            if st.button("🚪 Sign Out", use_container_width=True, type="primary"):
                st.toast("Signed out successfully (placeholder)", icon="🚪")

# Define pages under the multipage architecture
sales_dashboard = st.Page("pages/sales_dashboard.py", title="Sales Overview", icon="📊")
forecast_explorer = st.Page("pages/forecast_explorer.py", title="Forecast Explorer", icon="📈")
anomaly_report = st.Page("pages/anomaly_report.py", title="Anomaly Report", icon="🚨")
demand_segments = st.Page("pages/demand_segments.py", title="Product Demand Segments", icon="🎯")

# Set up Contextual Workspace Navigation Sidebar based on Selected top_tab
if st.session_state.top_tab == "Executive Overview":
    with st.sidebar:
        st.markdown("""
        <div style="padding-top: 0.8rem; padding-bottom: 0.5rem; margin-bottom: 1rem; border-bottom: 1px solid #F1F5F9;">
            <span style="font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">🏠 Executive Workspace</span>
        </div>
        """, unsafe_allow_html=True)
    pg = st.navigation({
        "Executive Overview": [sales_dashboard]
    })
else:
    with st.sidebar:
        st.markdown("""
        <div style="padding-top: 0.8rem; padding-bottom: 0.5rem; margin-bottom: 1rem; border-bottom: 1px solid #F1F5F9;">
            <span style="font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">📊 Analytics Workspace</span>
        </div>
        """, unsafe_allow_html=True)
    pg = st.navigation({
        "Advanced Analytics": [forecast_explorer, anomaly_report, demand_segments]
    })

# Run the page routing
pg.run()

# Thin separator line and responsive footer
st.markdown("<hr style='margin: 2.5rem 0 1.2rem 0 !important; opacity: 0.15;'>", unsafe_allow_html=True)

is_dark = st.session_state.get("dark_mode", False)
footer_bg = "rgba(21, 16, 48, 0.8)" if is_dark else "rgba(255, 255, 255, 0.85)"
footer_border = "rgba(244, 63, 94, 0.15)" if is_dark else "rgba(226, 232, 240, 0.8)"
footer_text = "#94A3B8" if is_dark else "#64748B"
footer_brand = "#FFFFFF" if is_dark else "#1E293B"

footer_html = f"""
<div style="
    background-color: {footer_bg};
    backdrop-filter: blur(12px) !important;
    border: 1px solid {footer_border} !important;
    border-radius: 12px;
    padding: 1.2rem 2rem;
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    transition: all 0.3s ease;
">
    <div style="display: flex; flex-direction: column; line-height: 1.4;">
        <span style="font-weight: 800; color: {footer_brand}; font-size: 0.95rem; letter-spacing: -0.3px;">🔮 SalesVision AI</span>
        <span style="font-size: 0.75rem; color: {footer_text}; font-weight: 500;">Intelligent Sales Analytics & Forecasting Dashboard</span>
    </div>
    <div style="font-size: 0.78rem; color: {footer_text}; font-weight: 600; text-align: right;">
        © 2026 Yashti Choudhary
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
