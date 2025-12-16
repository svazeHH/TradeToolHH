import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO

# ============================================================================
# EDLP RATE CONFIGURATION - Permanent rates by retailer and product group
# ============================================================================
# To add or update EDLP rates:
# 1. Add retailer name as key (must match GEOGRAPHY column in data)
# 2. Add product groups as nested dict (must match Product Group column)
# 3. Set rate as dollar amount per unit (e.g., 0.40 = $0.40 per unit)
#
# Example: If Publix pays $0.40 EDLP on every 32oz Core unit sold:
#   'Publix': {'32oz Core': 0.40}
#
# Rates are automatically applied to all units sold during promo period
# ============================================================================

EDLP_RATES = {
    "AC - ALBERTSONSCO ACME - RMA": {
        '10oz Core': 0.25,
        '12oz/4pk CCW': 1.05,
    },
    "AC - ALBERTSONSCO INTERMOUNTAIN DIV W/ SLC - RMA": {
        '16oz Core': 0.40,
        '32oz/6pk CCW': 0.80,
    },
    "AC - ALBERTSONSCO NORCAL DIV W/ HAWAII - RMA": {
        '10oz Core': 0.15,
        '16oz Core': 0.17,
        '16oz Innovation': 0.17,
        '32oz Core': 0.32,
    },
    "AC - ALBERTSONSCO PORTLAND, OR DIV - RMA": {
        '16oz Core': 0.46,
    },
    "AC - ALBERTSONSCO SHAWS DIV W/ STAR MARKET - RMA": {
        '16oz Core': 0.20,
        '32oz Core': 0.72,
    },
    "AC - ALBERTSONSCO SOUTHERN CALIFORNIA DIV - RMA": {
        '10oz Core': 0.15,
        '16oz Core': 0.17,
        '16oz Innovation': 0.17,
        '32oz Core': 0.32,
    },
    "AC - ALBERTSONSCO SOUTHERN DIV - RMA": {
        '10oz/6pk Smoothie': 0.22,
        '16oz Core': 0.36,
        '16oz Innovation': 0.36,
        '32oz Core': 0.66,
    },
    "AC - ALBERTSONSCO MID-ATLANTIC DIV - RMA": {
        '10oz Core': 0.22,
        '16oz Core': 0.36,
        '16oz Innovation': 0.36,
        '32oz Core': 0.70,
        '32oz/6pk Smoothie': 0.70,
    },
    "AD - AHOLD GIANT CARLISLE DIV - RMA": {
        '24oz/6pk Traditional PBY': 0.62,
    },
    "AD - DELHAIZE FOOD LION CORP - RMA": {
        '16oz Innovation': 0.17,
        '32oz Core': 0.52,
    },
    "ASSOCIATED WHOLESALE GROCERS CORP - SRMA": {
        '16oz Innovation': 0.46,
    },
    "BIG Y - RMA": {
        '16oz Core': 0.16,
        '32oz Core': 0.32,
    },
    "BJS CORP - RMA": {
        '10oz 6ct': 0.69,
    },
    "GELSONS MARKETS - TOTAL US": {
        '10oz Core': 0.06,
        '10oz/6pk Smoothie': 0.03,
        '16oz Core': 0.11,
        '16oz Innovation': 0.11,
        '24oz/6pk Traditional PBY': 0.06,
        '32oz Core': 0.32,
        '4.4oz/8pk Traditional PBY': 0.05,
    },
    "KROGER CORP - RMA": {
        '24oz/6pk Traditional PBY': 0.55,
    },
    "MOTHERS MARKET - TOTAL US": {
        '16oz Core': 0.26,
        '32oz Core': 0.52,
    },
    "PUBLIX CORP - RMA": {
        '16oz Core': 0.18,
        '16oz Innovation': 0.18,
        '32oz Core': 0.65,
        '32oz/6pk Innovation': 0.69,
    },
    "RALEYS - TOTAL US": {
        '24oz/6pk Traditional PBY': 0.45,
    },
    "SOUTHEASTERN GROCERS CORP - RMA": {
        '16oz Core': 0.30,
        '16oz Innovation': 0.30,
        '32oz Core': 0.60,
    },
    "SPROUTS FARMERS MARKET - TOTAL US W/O PL": {
        '10oz Core': 0.02,
        '10oz/6pk Smoothie': 0.40,
        '16oz Innovation': 0.38,
        '24oz/6pk Traditional PBY': 0.65,
        '32oz Core': 0.06,
        '4.4oz/8pk Traditional PBY': 0.01,
    },
    "STATER BROS CORP - RMA": {
        '16oz Core': 0.35,
        '16oz Innovation': 0.35,
        '32oz Core': 0.70,
    },
    "TARGET CORP W/ AK/HI - RMA": {
        '12oz/4pk CCW': 0.47,
    },
    "WAKEFERN CORP W/O PRICE RITE - RMA": {
        '10oz Core': 0.10,
        '24oz/6pk Traditional PBY': 0.65,
        '32oz Core': 0.36,
        '4.4oz/8pk Traditional PBY': 0.12,
    },
    "WALMART CORP - RMA": {
        '16oz Core': 0.51,
        '32oz Core': 0.72,
    },
    "WEGMANS CORP W/O NYC - RMA": {
        '10oz/6pk Smoothie': 0.36,
        '16oz Core': 0.38,
        '16oz Innovation': 0.38,
        '32oz Core': 0.72,
    },
}
# ============================================================================

# Page configuration
st.set_page_config(
    page_title="Harmless Harvest Post-Promo Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern sleek CSS with green color scheme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    }
    .main {
        padding: 2rem 3rem;
    }
    
    /* Typography */
    h1 {
        color: #7cb342;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #7cb342 0%, #558b2f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    h2 {
        color: #2c3e50;
        font-weight: 700;
        font-size: 1.5rem;
        margin: 2rem 0 1rem 0;
        letter-spacing: -0.01em;
    }
    h3 {
        color: #7cb342;
        font-weight: 600;
        font-size: 1.125rem;
        margin-bottom: 0.75rem;
        letter-spacing: -0.01em;
    }
    p, span, div, li {
        color: #475569;
        line-height: 1.6;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.03);
    }
    [data-testid="stSidebar"] h2 {
        color: #7cb342;
        border-bottom: 2px solid #7cb342;
        padding-bottom: 0.75rem;
        font-size: 1.125rem;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #7cb342 0%, #689f38 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.9375rem;
        padding: 0.875rem 2rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px rgba(124, 179, 66, 0.25);
        letter-spacing: 0.01em;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #689f38 0%, #558b2f 100%);
        box-shadow: 0 6px 20px rgba(124, 179, 66, 0.35);
        transform: translateY(-1px);
    }
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stDateInput>div>div>input,
    .stSelectbox>div>div>div,
    .stMultiSelect>div>div>div {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important;
        color: #2c3e50 !important;
        padding: 0.625rem 0.875rem !important;
        font-size: 0.9375rem !important;
        transition: all 0.2s ease;
    }
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stDateInput>div>div>input:focus {
        border-color: #7cb342 !important;
        box-shadow: 0 0 0 3px rgba(124, 179, 66, 0.1) !important;
        outline: none !important;
    }
    
    /* Dropdown menus */
    [data-baseweb="select"] > div,
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
    }
    [data-baseweb="menu"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1) !important;
    }
    ul[role="listbox"] {
        background-color: #ffffff !important;
        padding: 0.5rem !important;
    }
    li[role="option"] {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        border-radius: 6px !important;
        margin: 2px 0 !important;
        padding: 0.5rem 0.75rem !important;
    }
    li[role="option"]:hover {
        background-color: #f0f9ff !important;
    }
    
    /* Labels */
    label {
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #1e293b;
        font-size: 2.25rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    [data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 600;
        font-size: 0.8125rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricDelta"] {
        color: #7cb342;
        font-weight: 600;
    }
    
    /* Period Cards */
    .period-card {
        background: #ffffff;
        border: none;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 0.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .period-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 4px;
        transition: width 0.3s ease;
    }
    .period-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.06);
        transform: translateY(-4px);
    }
    .period-card.pre::before {
        background: linear-gradient(180deg, #9e9e9e 0%, #757575 100%);
    }
    .period-card.during::before {
        background: linear-gradient(180deg, #7cb342 0%, #689f38 100%);
    }
    .period-card.post::before {
        background: linear-gradient(180deg, #e57b8f 0%, #d5536e 100%);
    }
    .period-card:hover::before {
        width: 8px;
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        border-radius: 12px;
        border: none;
        border-left: 4px solid;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
        padding: 0 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.9375rem;
        padding: 1rem 1.5rem;
        border-radius: 10px 10px 0 0;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #7cb342 !important;
        background: linear-gradient(180deg, rgba(124, 179, 66, 0.08) 0%, rgba(124, 179, 66, 0.02) 100%);
        border-bottom: 3px solid #7cb342 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 12px;
        color: #2c3e50;
        font-weight: 600;
        padding: 1rem 1.25rem;
        transition: all 0.2s ease;
    }
    .streamlit-expanderHeader:hover {
        border-color: #7cb342;
        background: #f8fef5;
        box-shadow: 0 2px 8px rgba(124, 179, 66, 0.1);
    }
    
    /* Text Area */
    .stTextArea textarea {
        background-color: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 12px;
        color: #2c3e50;
        font-size: 0.9375rem;
        padding: 0.875rem;
        line-height: 1.6;
    }
    .stTextArea textarea:focus {
        border-color: #7cb342;
        box-shadow: 0 0 0 3px rgba(124, 179, 66, 0.1);
        outline: none;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 2.5rem 0;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #7cb342;
        background: #f8fef5;
    }
    
    /* Success/Info Messages */
    .stSuccess {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
        border-left: 4px solid #7cb342 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'weekly_data' not in st.session_state:
    st.session_state.weekly_data = None
if 'promo_analyses' not in st.session_state:
    st.session_state.promo_analyses = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

def load_weekly_data(uploaded_file):
    """Load and process weekly sales data"""
    try:
        df = pd.read_excel(uploaded_file)
        if 'Week Ending' in df.columns:
            df['Week Ending'] = pd.to_datetime(df['Week Ending'])
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def calculate_promo_periods(start_date, end_date):
    """Calculate pre, during, and post promo periods"""
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    promo_days = (end_date - start_date).days + 1
    pre_end = start_date - timedelta(days=1)
    pre_start = pre_end - timedelta(days=promo_days - 1)
    post_start = end_date + timedelta(days=1)
    post_end = post_start + timedelta(days=promo_days - 1)
    return {
        'pre_start': pre_start,
        'pre_end': pre_end,
        'promo_start': start_date,
        'promo_end': end_date,
        'post_start': post_start,
        'post_end': post_end,
        'promo_days': promo_days
    }

def get_period_sales(df, retailer, product_groups, start_date, end_date, promo_days):
    """Get sales for a specific period with proration"""
    if isinstance(product_groups, str):
        product_groups = [product_groups]
    
    filtered_df = df[
        (df['GEOGRAPHY'] == retailer) &
        (df['Product Group'].isin(product_groups))
    ].copy()
    
    if filtered_df.empty:
        return 0, 0
    
    period_data = filtered_df[
        (filtered_df['Week Ending'] >= start_date) &
        (filtered_df['Week Ending'] <= end_date + timedelta(days=7))
    ].copy()
    
    if period_data.empty:
        return 0, 0
    
    total_dollars = 0
    total_units = 0
    
    for _, row in period_data.iterrows():
        week_end = row['Week Ending']
        week_start = week_end - timedelta(days=6)
        overlap_start = max(week_start, start_date)
        overlap_end = min(week_end, end_date)
        
        if overlap_start <= overlap_end:
            overlap_days = (overlap_end - overlap_start).days + 1
            proration_factor = overlap_days / 7.0
            total_dollars += row['Dollars'] * proration_factor
            total_units += row['Units'] * proration_factor
    
    return total_dollars, total_units

def calculate_edlp_spend(retailer, product_groups, units):
    """Calculate EDLP spend based on hardcoded rates"""
    if isinstance(product_groups, str):
        product_groups = [product_groups]
    
    total_edlp = 0
    
    # Check if retailer has any EDLP rates configured
    if retailer in EDLP_RATES:
        for product_group in product_groups:
            # Check if this specific product group has an EDLP rate
            if product_group in EDLP_RATES[retailer]:
                rate_per_unit = EDLP_RATES[retailer][product_group]
                total_edlp += units * rate_per_unit
    
    return total_edlp

def get_edlp_rate(retailer, product_group):
    """Get EDLP rate for a specific retailer/product combination"""
    if retailer in EDLP_RATES:
        if product_group in EDLP_RATES[retailer]:
            return EDLP_RATES[retailer][product_group]
    return 0.0

def calculate_metrics(pre_sales, promo_sales, post_sales, trade_spend, flat_fee, pre_units, promo_units, post_units, gross_margin_pct, edlp_spend):
    """Calculate lift and ROI metrics"""
    total_trade_spend = trade_spend + flat_fee + edlp_spend
    
    # Lift calculations - UNIT BASED
    during_lift = ((promo_units - pre_units) / pre_units * 100) if pre_units > 0 else 0
    post_lift = ((post_units - pre_units) / pre_units * 100) if pre_units > 0 else 0
    
    # Incremental calculations
    incremental_sales = promo_sales - pre_sales
    incremental_units = promo_units - pre_units
    incremental_profit = incremental_sales * (gross_margin_pct / 100)
    
    # ROI = (Incremental Profit - Total Trade Spend) / Total Trade Spend × 100
    roi = ((incremental_profit - total_trade_spend) / total_trade_spend * 100) if total_trade_spend > 0 else 0
    
    return {
        'during_lift': during_lift,
        'post_lift': post_lift,
        'incremental_sales': incremental_sales,
        'incremental_units': incremental_units,
        'incremental_profit': incremental_profit,
        'gross_margin_pct': gross_margin_pct,
        'roi': roi,
        'edlp_spend': edlp_spend
    }

def create_performance_chart(pre_sales, promo_sales, post_sales):
    """Create modern bar chart"""
    fig = go.Figure(data=[
        go.Bar(
            x=['Pre-Promo', 'During Promo', 'Post-Promo'],
            y=[pre_sales, promo_sales, post_sales],
            marker=dict(
                color=['#9e9e9e', '#7cb342', '#e57b8f'],
                line=dict(color='rgba(255, 255, 255, 0)', width=0)
            ),
            text=[f'${pre_sales:,.0f}', f'${promo_sales:,.0f}', f'${post_sales:,.0f}'],
            textposition='outside',
            textfont=dict(size=15, color='#2c3e50', family='Inter', weight=600)
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Sales Performance',
            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Inter', 'weight': 700}
        },
        yaxis_title='Sales ($)',
        yaxis=dict(
            gridcolor='#f1f5f9',
            showline=False,
            zeroline=False
        ),
        xaxis=dict(
            showline=False,
            showgrid=False
        ),
        height=400,
        showlegend=False,
        template='plotly_white',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#475569', family='Inter'),
        margin=dict(t=50, b=20, l=20, r=20)
    )
    return fig

def create_lift_gauge(actual_lift, expected_lift):
    """Create modern gauge chart for unit lift"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=actual_lift,
        delta={
            'reference': expected_lift,
            'suffix': '%',
            'font': {'size': 18, 'family': 'Inter', 'weight': 600}
        },
        title={
            'text': "Unit Lift vs Expected",
            'font': {'size': 18, 'color': '#2c3e50', 'family': 'Inter', 'weight': 600}
        },
        number={'font': {'size': 44, 'family': 'Inter', 'weight': 700}},
        gauge={
            'axis': {
                'range': [None, max(actual_lift * 1.2, expected_lift * 1.5)],
                'tickfont': {'size': 14, 'family': 'Inter'}
            },
            'bar': {'color': "#7cb342", 'thickness': 0.8},
            'bgcolor': "#f8f9fa",
            'borderwidth': 0,
            'steps': [
                {'range': [0, expected_lift], 'color': "#f1f5f9"},
                {'range': [expected_lift, expected_lift * 2], 'color': "#e8f5e9"}
            ],
            'threshold': {
                'line': {'color': "#e57b8f", 'width': 5},
                'thickness': 0.8,
                'value': expected_lift
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        paper_bgcolor='white',
        font={'color': "#2c3e50", 'family': 'Inter'},
        margin=dict(t=50, b=20, l=20, r=20)
    )
    return fig

def export_to_excel(analyses):
    """Export analyses to Excel"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        summary_data = []
        for analysis in analyses:
            if isinstance(analysis['product_group'], list):
                product_group_str = ', '.join(analysis['product_group'])
            else:
                product_group_str = str(analysis['product_group'])
            
            summary_data.append({
                'Analysis Date': analysis['analysis_date'],
                'Retailer': analysis['retailer'],
                'Product Group(s)': product_group_str,
                'Promo Start': analysis['periods']['promo_start'].strftime('%Y-%m-%d'),
                'Promo End': analysis['periods']['promo_end'].strftime('%Y-%m-%d'),
                'Promo Days': analysis['periods']['promo_days'],
                'Pre-Promo Sales': analysis['pre_sales'],
                'Pre-Promo Units': analysis['pre_units'],
                'During Promo Sales': analysis['promo_sales'],
                'During Promo Units': analysis['promo_units'],
                'During Incr Dollars': analysis['promo_sales'] - analysis['pre_sales'],
                'During Incr Units': analysis['promo_units'] - analysis['pre_units'],
                'Post-Promo Sales': analysis['post_sales'],
                'Post-Promo Units': analysis['post_units'],
                'Post Incr Dollars': analysis['post_sales'] - analysis['pre_sales'],
                'Post Incr Units': analysis['post_units'] - analysis['pre_units'],
                'Gross Margin %': analysis['gross_margin_pct'],
                'Incremental Profit': analysis['metrics']['incremental_profit'],
                'EDLP Spend': analysis['metrics']['edlp_spend'],
                'Trade Spend': analysis['trade_spend'],
                'Flat Fee': analysis['flat_fee'],
                'Total Spend': analysis['trade_spend'] + analysis['flat_fee'] + analysis['metrics']['edlp_spend'],
                'Expected Lift %': analysis['expected_lift'],
                'Actual During Lift %': analysis['metrics']['during_lift'],
                'Actual Post Lift %': analysis['metrics']['post_lift'],
                'Expected ROI %': analysis['expected_roi'],
                'Actual ROI %': analysis['metrics']['roi'],
                'Incremental Sales': analysis['metrics']['incremental_sales'],
                'Notes': analysis['notes']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Summary']
        
        for idx, col in enumerate(summary_df.columns):
            max_length = max(summary_df[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
    
    output.seek(0)
    return output

def main():
    # Header
    st.markdown("<h1>Harmless Harvest Post-Promo Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.125rem; color: #64748b; margin-top: -0.5rem;'>Trade spend performance analytics</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📁 Sales Consumption Data")
        
        uploaded_file = st.file_uploader(
            "Upload Weekly Sales Data",
            type=['xlsx', 'xls'],
            help="Upload syndicated weekly sales data"
        )
        
        if uploaded_file:
            if st.session_state.weekly_data is None:
                with st.spinner("Loading..."):
                    st.session_state.weekly_data = load_weekly_data(uploaded_file)
                    if st.session_state.weekly_data is not None:
                        st.success(f"✅ {len(st.session_state.weekly_data):,} rows loaded")
            else:
                st.success(f"✅ {len(st.session_state.weekly_data):,} rows loaded")
                if st.button("🔄 Reload Data", use_container_width=True):
                    st.session_state.weekly_data = load_weekly_data(uploaded_file)
                    st.rerun()
        
        st.markdown("---")
        st.markdown("## ⚙️ EDLP Rates")
        
        with st.expander("View Configured EDLP Rates", expanded=False):
            st.caption("Everyday low price discount rates applied per unit sold")
            
            if EDLP_RATES:
                for retailer, products in list(EDLP_RATES.items())[:5]:  # Show first 5
                    st.markdown(f"**{retailer}:**")
                    for product, rate in list(products.items())[:3]:  # Show first 3 products
                        st.write(f"  • {product}: ${rate:.2f}/unit")
                st.caption(f"...and {len(EDLP_RATES) - 5} more retailers configured")
            else:
                st.info("No EDLP rates configured")
        
        st.markdown("---")
        st.markdown("## 📊 Analysis Summary")
        st.metric("Total Analyses", len(st.session_state.promo_analyses))
        
        if st.session_state.promo_analyses:
            if st.button("📥 Export All", use_container_width=True):
                excel_data = export_to_excel(st.session_state.promo_analyses)
                st.download_button(
                    "⬇️ Download Excel",
                    excel_data,
                    f"promo_analyses_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    # Main content
    if st.session_state.weekly_data is None:
        st.info("👈 Upload your weekly sales data to begin analysis")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📂</div>
                <h3 style="margin-bottom: 0.5rem;">Upload Data</h3>
                <p style="color: #64748b; font-size: 0.9375rem;">Load syndicated sales consumption file</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
                <h3 style="margin-bottom: 0.5rem;">Configure</h3>
                <p style="color: #64748b; font-size: 0.9375rem;">Select products & promo dates</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <h3 style="margin-bottom: 0.5rem;">Analyze</h3>
                <p style="color: #64748b; font-size: 0.9375rem;">View lift metrics & ROI</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        tab1, tab2 = st.tabs(["➕ New Analysis", "📋 All Analyses"])
        
        with tab1:
            df = st.session_state.weekly_data
            retailers = sorted(df['GEOGRAPHY'].dropna().unique())
            product_groups = sorted(df['Product Group'].dropna().unique())
            
            st.markdown("## 🎯 Promotion Configuration")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### Product & Retailer")
                retailer = st.selectbox("Retailer", retailers)
                product_group = st.multiselect("Product Group(s)", product_groups, help="Select one or more product groups")
                
                st.markdown("### Timing")
                date_col1, date_col2 = st.columns(2)
                with date_col1:
                    promo_start = st.date_input("Promo Start Date")
                with date_col2:
                    promo_end = st.date_input("Promo End Date")
            
            with col2:
                st.markdown("### Financial Inputs")
                trade_spend = st.number_input(
                    "Item-Level Trade Spend ($)",
                    0.0,
                    step=100.0,
                    help="Total promotional trade spend: discounts, off-invoice, scan-based allowances (EDLP rates auto-applied from config)"
                )
                
                # Show EDLP info if configured
                if retailer and product_group:
                    edlp_info = []
                    for pg in product_group:
                        rate = get_edlp_rate(retailer, pg)
                        if rate > 0:
                            edlp_info.append(f"{pg}: ${rate:.2f}/unit")
                    if edlp_info:
                        st.info(f"💡 **EDLP rates configured:**\n\n" + "\n\n".join(edlp_info) + "\n\n*Applied automatically to all units sold*")
                
                flat_fee = st.number_input(
                    "Additional Fees ($)",
                    0.0,
                    step=100.0,
                    help="Slotting fees, display fees, co-op advertising"
                )
                gross_margin_pct = st.number_input(
                    "Gross Margin (%)",
                    0.0,
                    100.0,
                    30.0,
                    step=5.0,
                    help="Gross margin = (Net Price - COGS) / Net Price × 100"
                )
                
                st.markdown("### Performance Expectations")
                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    expected_lift = st.number_input("Expected Lift (%)", 0.0, step=5.0)
                with exp_col2:
                    expected_roi = st.number_input(
                        "Expected ROI (%)",
                        -100.0,
                        step=10.0,
                        help="Expected return on trade spend investment"
                    )
            
            st.markdown("---")
            
            if st.button("🔍 Run Analysis", type="primary", use_container_width=True):
                if not product_group:
                    st.error("⚠️ Please select at least one product group")
                elif promo_start >= promo_end:
                    st.error("⚠️ End date must be after start date")
                else:
                    with st.spinner("Analyzing promotion performance..."):
                        periods = calculate_promo_periods(promo_start, promo_end)
                        
                        pre_sales, pre_units = get_period_sales(df, retailer, product_group, periods['pre_start'], periods['pre_end'], periods['promo_days'])
                        promo_sales, promo_units = get_period_sales(df, retailer, product_group, periods['promo_start'], periods['promo_end'], periods['promo_days'])
                        post_sales, post_units = get_period_sales(df, retailer, product_group, periods['post_start'], periods['post_end'], periods['promo_days'])
                        
                        # Calculate EDLP spend for promo period
                        edlp_spend = calculate_edlp_spend(retailer, product_group, promo_units)
                        
                        metrics = calculate_metrics(pre_sales, promo_sales, post_sales, trade_spend, flat_fee, pre_units, promo_units, post_units, gross_margin_pct, edlp_spend)
                        product_group_display = ', '.join(product_group) if isinstance(product_group, list) else product_group
                        
                        st.session_state.current_analysis = {
                            'retailer': retailer,
                            'product_group': product_group,
                            'product_group_display': product_group_display,
                            'periods': periods,
                            'pre_sales': pre_sales,
                            'promo_sales': promo_sales,
                            'post_sales': post_sales,
                            'pre_units': pre_units,
                            'promo_units': promo_units,
                            'post_units': post_units,
                            'trade_spend': trade_spend,
                            'flat_fee': flat_fee,
                            'gross_margin_pct': gross_margin_pct,
                            'expected_lift': expected_lift,
                            'expected_roi': expected_roi,
                            'metrics': metrics
                        }
                        st.rerun()
            
            if st.session_state.current_analysis:
                st.success("✅ Analysis Complete")
                st.markdown("---")
                
                a = st.session_state.current_analysis
                
                st.markdown("## 📊 Performance Results")
                
                # Period comparison cards
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""<div class='period-card pre'>
                    <h3 style='color: #64748b; margin:0; font-size: 1rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Pre-Promo Baseline</h3>
                    <p style='color: #94a3b8; font-size: 0.875rem; margin: 0.25rem 0 1rem 0;'>{a['periods']['pre_start'].strftime('%b %d')} - {a['periods']['pre_end'].strftime('%b %d, %Y')}</p>
                    </div>""", unsafe_allow_html=True)
                    st.metric("Sales", f"${a['pre_sales']:,.0f}")
                    st.caption("Baseline performance")
                    st.metric("Units", f"{a['pre_units']:,.0f}")
                
                with col2:
                    st.markdown(f"""<div class='period-card during'>
                    <h3 style='color: #7cb342; margin:0; font-size: 1rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>During Promotion</h3>
                    <p style='color: #8bc34a; font-size: 0.875rem; margin: 0.25rem 0 1rem 0;'>{a['periods']['promo_start'].strftime('%b %d')} - {a['periods']['promo_end'].strftime('%b %d, %Y')}</p>
                    </div>""", unsafe_allow_html=True)
                    st.metric("Sales", f"${a['promo_sales']:,.0f}", delta=f"+${a['promo_sales'] - a['pre_sales']:,.0f}")
                    st.caption(f"Incremental: ${a['promo_sales'] - a['pre_sales']:,.0f}")
                    st.metric("Units", f"{a['promo_units']:,.0f}")
                
                with col3:
                    st.markdown(f"""<div class='period-card post'>
                    <h3 style='color: #e57b8f; margin:0; font-size: 1rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Post-Promo</h3>
                    <p style='color: #f48ba7; font-size: 0.875rem; margin: 0.25rem 0 1rem 0;'>{a['periods']['post_start'].strftime('%b %d')} - {a['periods']['post_end'].strftime('%b %d, %Y')}</p>
                    </div>""", unsafe_allow_html=True)
                    st.metric("Sales", f"${a['post_sales']:,.0f}", delta=f"+${a['post_sales'] - a['pre_sales']:,.0f}")
                    st.caption(f"Incremental: ${a['post_sales'] - a['pre_sales']:,.0f}")
                    st.metric("Units", f"{a['post_units']:,.0f}")
                
                st.markdown("---")
                
                # Trade Spend Breakdown Section
                st.markdown("### 💰 Trade Spend Breakdown")
                
                breakdown_col1, breakdown_col2 = st.columns(2)
                
                with breakdown_col1:
                    st.metric("Item-Level Trade Spend", f"${a['trade_spend']:,.0f}")
                    st.caption("Promotional discounts and allowances")
                    
                    st.metric("Additional Fees", f"${a['flat_fee']:,.0f}")
                    st.caption("Slotting, display, co-op advertising")
                    
                    if a['metrics']['edlp_spend'] > 0:
                        st.metric("EDLP Spend", f"${a['metrics']['edlp_spend']:,.0f}")
                        st.caption(f"Everyday discount: {a['promo_units']:,.0f} units sold")
                
                with breakdown_col2:
                    total_investment = a['trade_spend'] + a['flat_fee'] + a['metrics']['edlp_spend']
                    st.metric("**Total Trade Investment**", f"**${total_investment:,.0f}**")
                    st.caption("Sum of all trade spend components")
                    
                    # Show percentage breakdown
                    if total_investment > 0:
                        st.markdown("**Breakdown:**")
                        promo_pct = (a['trade_spend'] / total_investment * 100) if total_investment > 0 else 0
                        fee_pct = (a['flat_fee'] / total_investment * 100) if total_investment > 0 else 0
                        edlp_pct = (a['metrics']['edlp_spend'] / total_investment * 100) if total_investment > 0 else 0
                        
                        st.write(f"• Promo: {promo_pct:.1f}%")
                        st.write(f"• Fees: {fee_pct:.1f}%")
                        if a['metrics']['edlp_spend'] > 0:
                            st.write(f"• EDLP: {edlp_pct:.1f}%")
                
                st.markdown("---")
                
                # Metrics section
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 📈 Lift Analysis")
                    during_diff = a['metrics']['during_lift'] - a['expected_lift']
                    st.metric("During Promo", f"{a['metrics']['during_lift']:.1f}%", f"{during_diff:+.1f}%")
                    st.metric("Post Promo", f"{a['metrics']['post_lift']:.1f}%")
                    
                    st.markdown("---")
                    st.metric("Expected Lift", f"{a['expected_lift']:.1f}%")
                    st.metric("Incremental Units", f"{a['metrics']['incremental_units']:,.0f}")
                    st.caption("Units above baseline during promo")
                
                with col2:
                    st.markdown("### 💵 Financial Performance")
                    roi_diff = a['metrics']['roi'] - a['expected_roi']
                    st.metric("Actual ROI", f"{a['metrics']['roi']:.1f}%", f"{roi_diff:+.1f}%")
                    st.metric("Expected ROI", f"{a['expected_roi']:.1f}%")
                    
                    st.markdown("---")
                    st.metric("Incremental Revenue", f"${a['metrics']['incremental_sales']:,.0f}")
                    st.metric("Incremental Profit", f"${a['metrics']['incremental_profit']:,.0f}")
                    st.caption(f"Based on {a['gross_margin_pct']:.0f}% gross margin")
                
                st.markdown("---")
                
                # Charts
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(create_performance_chart(a['pre_sales'], a['promo_sales'], a['post_sales']), use_container_width=True)
                with col2:
                    st.plotly_chart(create_lift_gauge(a['metrics']['during_lift'], a['expected_lift']), use_container_width=True)
                
                st.markdown("---")
                
                # Notes section
                st.markdown("### 📝 Analysis Notes")
                notes = st.text_area(
                    "Document key insights and recommendations",
                    height=120,
                    placeholder="e.g., Strong performance during promo but post-promo dip indicates forward buying..."
                )
                
                if st.button("💾 Save Analysis", type="primary", use_container_width=True):
                    a['notes'] = notes
                    a['analysis_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    st.session_state.promo_analyses.append(a.copy())
                    st.session_state.current_analysis = None
                    st.success("✅ Analysis saved successfully!")
                    st.rerun()
        
        with tab2:
            st.markdown("## 📋 Saved Analyses")
            
            if not st.session_state.promo_analyses:
                st.info("No saved analyses yet. Create your first analysis in the 'New Analysis' tab!")
            else:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                avg_lift = sum(a['metrics']['during_lift'] for a in st.session_state.promo_analyses) / len(st.session_state.promo_analyses)
                avg_roi = sum(a['metrics']['roi'] for a in st.session_state.promo_analyses) / len(st.session_state.promo_analyses)
                total_spend = sum(a['trade_spend'] + a['flat_fee'] + a['metrics']['edlp_spend'] for a in st.session_state.promo_analyses)
                total_incremental = sum(a['metrics']['incremental_sales'] for a in st.session_state.promo_analyses)
                
                with col1:
                    st.metric("Average Lift", f"{avg_lift:.1f}%")
                with col2:
                    st.metric("Average ROI", f"{avg_roi:.1f}%")
                with col3:
                    st.metric("Total Investment", f"${total_spend:,.0f}")
                with col4:
                    st.metric("Total Incremental", f"${total_incremental:,.0f}")
                
                st.markdown("---")
                
                # Individual analysis cards
                for idx, a in enumerate(st.session_state.promo_analyses):
                    if isinstance(a['product_group'], list):
                        product_display = ', '.join(a['product_group'])
                    else:
                        product_display = str(a['product_group'])
                    
                    with st.expander(f"**{a['retailer']}** • {product_display} • {a['periods']['promo_start'].strftime('%b %d')} - {a['periods']['promo_end'].strftime('%b %d, %Y')}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**Pre-Promo**")
                            st.write(f"Sales: ${a['pre_sales']:,.0f}")
                            st.caption("Baseline period")
                            st.write(f"Units: {a['pre_units']:,.0f}")
                        
                        with col2:
                            st.markdown("**During Promo**")
                            st.write(f"Sales: ${a['promo_sales']:,.0f}")
                            st.caption(f"Incremental: ${a['promo_sales'] - a['pre_sales']:,.0f}")
                            st.write(f"Units: {a['promo_units']:,.0f}")
                            st.write(f"Lift: {a['metrics']['during_lift']:.1f}%")
                        
                        with col3:
                            st.markdown("**Post-Promo**")
                            st.write(f"Sales: ${a['post_sales']:,.0f}")
                            st.caption(f"Incremental: ${a['post_sales'] - a['pre_sales']:,.0f}")
                            st.write(f"Units: {a['post_units']:,.0f}")
                            st.write(f"Lift: {a['metrics']['post_lift']:.1f}%")
                        
                        st.markdown("---")
                        st.markdown("**Financial Performance**")
                        perf_col1, perf_col2 = st.columns(2)
                        with perf_col1:
                            st.write(f"Gross Margin: {a['gross_margin_pct']:.0f}%")
                            st.write(f"Expected Lift: {a['expected_lift']:.1f}%")
                            st.write(f"Expected ROI: {a['expected_roi']:.1f}%")
                            if a['metrics']['edlp_spend'] > 0:
                                st.write(f"EDLP Spend: ${a['metrics']['edlp_spend']:,.0f}")
                        with perf_col2:
                            st.write(f"Actual ROI: {a['metrics']['roi']:.1f}%")
                            st.write(f"Incremental Sales: ${a['metrics']['incremental_sales']:,.0f}")
                            st.write(f"Incremental Profit: ${a['metrics']['incremental_profit']:,.0f}")
                        
                        if a.get('notes'):
                            st.markdown("---")
                            st.markdown("**Notes:**")
                            st.write(a['notes'])
                        
                        if st.button(f"🗑️ Delete Analysis", key=f"del_{idx}"):
                            st.session_state.promo_analyses.pop(idx)
                            st.rerun()

if __name__ == "__main__":
    main()
