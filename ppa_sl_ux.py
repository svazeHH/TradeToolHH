import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Harmless Harvest Post-Promo Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with proper color scheme and better UX
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background-color: #ffffff;
    }
    .main {
        padding: 1rem 2rem;
        background-color: #ffffff;
    }
    
    /* Typography */
    h1 {
        color: #7cb342;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    h2 {
        color: #5a8c2f;
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    h3 {
        color: #7cb342;
        font-weight: 600;
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
    }
    p, span, div, li {
        color: #2c3e50;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-right: 2px solid #e0e0e0;
    }
    [data-testid="stSidebar"] h2 {
        color: #7cb342;
        border-bottom: 3px solid #7cb342;
        padding-bottom: 0.5rem;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #7cb342 0%, #689f38 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(124, 179, 66, 0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #689f38 0%, #5a8c2f 100%);
        box-shadow: 0 6px 12px rgba(124, 179, 66, 0.3);
        transform: translateY(-2px);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stDateInput>div>div>input,
    .stSelectbox>div>div>div,
    .stMultiSelect>div>div>div {
        background-color: #ffffff !important;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        color: #2c3e50;
        padding: 0.5rem;
    }
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stDateInput>div>div>input:focus {
        border-color: #7cb342;
        box-shadow: 0 0 0 2px rgba(124, 179, 66, 0.1);
    }
    
    /* Dropdown menus */
    [data-baseweb="select"] > div,
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    [data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    ul[role="listbox"] {
        background-color: #ffffff !important;
    }
    li[role="option"] {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
    }
    li[role="option"]:hover {
        background-color: #f8f9fa !important;
    }
    
    /* Labels */
    label {
        color: #5a8c2f !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        color: #5a8c2f;
        font-weight: 600;
        font-size: 0.95rem;
    }
    div[data-testid="stMetricDelta"] {
        color: #7cb342;
    }
    
    /* Metric Cards */
    .metric-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Period Cards */
    .period-card {
        background: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .period-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .period-card.pre {
        border-left: 5px solid #9e9e9e;
    }
    .period-card.during {
        border-left: 5px solid #7cb342;
    }
    .period-card.post {
        border-left: 5px solid #e57b8f;
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 5px solid;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #e0e0e0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #9e9e9e;
        font-weight: 600;
        padding: 1rem 1.5rem;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #7cb342 !important;
        background-color: #f8f9fa;
        border-bottom: 3px solid #7cb342 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        color: #2c3e50;
        font-weight: 600;
    }
    .streamlit-expanderHeader:hover {
        border-color: #7cb342;
    }
    
    /* Text Area */
    .stTextArea textarea {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        color: #2c3e50;
    }
    .stTextArea textarea:focus {
        border-color: #7cb342;
        box-shadow: 0 0 0 2px rgba(124, 179, 66, 0.1);
    }
    
    /* Divider */
    hr {
        border-top: 2px solid #e0e0e0;
        margin: 2rem 0;
    }
    
    /* Caption text */
    .caption {
        color: #757575;
        font-size: 0.85rem;
        font-style: italic;
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

def calculate_metrics(pre_sales, promo_sales, post_sales, trade_spend, flat_fee, pre_units, promo_units, post_units):
    """Calculate lift and ROI metrics"""
    total_trade_spend = trade_spend + flat_fee
    
    during_lift_dollars = ((promo_sales - pre_sales) / pre_sales * 100) if pre_sales > 0 else 0
    post_lift_dollars = ((post_sales - pre_sales) / pre_sales * 100) if pre_sales > 0 else 0
    during_lift_units = ((promo_units - pre_units) / pre_units * 100) if pre_units > 0 else 0
    post_lift_units = ((post_units - pre_units) / pre_units * 100) if pre_units > 0 else 0
    
    incremental_sales = promo_sales - pre_sales
    roi = (incremental_sales / total_trade_spend * 100) if total_trade_spend > 0 else 0
    
    return {
        'during_lift_dollars': during_lift_dollars,
        'post_lift_dollars': post_lift_dollars,
        'during_lift_units': during_lift_units,
        'post_lift_units': post_lift_units,
        'incremental_sales': incremental_sales,
        'roi': roi
    }

def create_performance_chart(pre_sales, promo_sales, post_sales):
    """Create bar chart"""
    fig = go.Figure(data=[
        go.Bar(
            x=['Pre-Promo', 'During Promo', 'Post-Promo'],
            y=[pre_sales, promo_sales, post_sales],
            marker_color=['#bdbdbd', '#7cb342', '#e57b8f'],
            text=[f'${pre_sales:,.0f}', f'${promo_sales:,.0f}', f'${post_sales:,.0f}'],
            textposition='outside',
            textfont=dict(size=14, color='#2c3e50')
        )
    ])
    
    fig.update_layout(
        title={'text': 'Sales Performance', 'font': {'size': 18, 'color': '#5a8c2f'}},
        yaxis_title='Sales ($)',
        height=400,
        showlegend=False,
        template='plotly_white',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#2c3e50')
    )
    return fig

def create_lift_gauge(actual_lift, expected_lift):
    """Create gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=actual_lift,
        delta={'reference': expected_lift, 'suffix': '%'},
        title={'text': "Dollar Lift vs Expected", 'font': {'size': 16, 'color': '#5a8c2f'}},
        gauge={
            'axis': {'range': [None, max(actual_lift * 1.2, expected_lift * 1.5)]},
            'bar': {'color': "#7cb342"},
            'steps': [
                {'range': [0, expected_lift], 'color': "#f0f0f0"},
                {'range': [expected_lift, expected_lift * 2], 'color': "#e8f5e9"}
            ],
            'threshold': {
                'line': {'color': "#e57b8f", 'width': 4},
                'thickness': 0.75,
                'value': expected_lift
            }
        }
    ))
    
    fig.update_layout(height=350, paper_bgcolor='white', font={'color': "#2c3e50"})
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
                'During Promo Sales': analysis['promo_sales'],
                'During Incr Dollars': analysis['promo_sales'] - analysis['pre_sales'],
                'Post-Promo Sales': analysis['post_sales'],
                'Post Incr Dollars': analysis['post_sales'] - analysis['pre_sales'],
                'Trade Spend': analysis['trade_spend'],
                'Flat Fee': analysis['flat_fee'],
                'Total Spend': analysis['trade_spend'] + analysis['flat_fee'],
                'Expected Lift %': analysis['expected_lift'],
                'Actual During Lift % ($)': analysis['metrics']['during_lift_dollars'],
                'Actual During Lift % (Units)': analysis['metrics']['during_lift_units'],
                'Actual Post Lift % ($)': analysis['metrics']['post_lift_dollars'],
                'Actual Post Lift % (Units)': analysis['metrics']['post_lift_units'],
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
    st.markdown("""
        <h1 style='margin-left: 15px; color: #7cb342;'>Harmless Harvest Post-Promo Analysis</h1>
    </div>
    """, unsafe_allow_html=True)
   
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📁 Data Management")
        
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
                        st.success(f"✅ {len(st.session_state.weekly_data):,} rows")
            else:
                st.success(f"✅ {len(st.session_state.weekly_data):,} rows")
                if st.button("🔄 Reload"):
                    st.session_state.weekly_data = load_weekly_data(uploaded_file)
                    st.rerun()
        
        st.markdown("---")
        st.markdown("## 📊 Summary")
        st.metric("Total Analyses", len(st.session_state.promo_analyses))
        
        if st.session_state.promo_analyses:
            if st.button("📥 Export", use_container_width=True):
                excel_data = export_to_excel(st.session_state.promo_analyses)
                st.download_button(
                    "⬇️ Download",
                    excel_data,
                    f"promo_analyses_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    # Main content
    if st.session_state.weekly_data is None:
        st.info("👈 Upload your weekly sales data to begin")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style="text-align: center;">
                <h3>📂 Upload</h3>
                <p>Load shared syndicated sales data file</p>
            </div>
                """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="text-align: center;">
                <h3>🎯 Analyze</h3>
                <p>Select product groups & in-store promo dates</p>
            </div>
                """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div style="text-align: center;">
                <h3>📊 Results</h3>
                <p>View sales performance, lift & ROI</p>
            </div>
                """, unsafe_allow_html=True)
    else:
        tab1, tab2 = st.tabs(["➕ New Analysis", "📋 All Analyses"])
        
        with tab1:
            df = st.session_state.weekly_data
            retailers = sorted(df['GEOGRAPHY'].dropna().unique())
            product_groups = sorted(df['Product Group'].dropna().unique())
            
            st.markdown("## 🎯 Promotion Details")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### Product & Retailer")
                retailer = st.selectbox("Retailer", retailers)
                product_group = st.multiselect("Product Group(s)", product_groups, help="Select one or more")
                
                st.markdown("### Timing")
                date_col1, date_col2 = st.columns(2)
                with date_col1:
                    promo_start = st.date_input("Start")
                with date_col2:
                    promo_end = st.date_input("End")
            
            with col2:
                st.markdown("### Financial")
                trade_spend = st.number_input("Item-Level Trade Spend ($)", 0.0, step=100.0)
                flat_fee = st.number_input("Additional Fees ($)", 0.0, step=100.0)
                
                st.markdown("### Expectations")
                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    expected_lift = st.number_input("Lift (%)", 0.0, 30.0, step=5.0)
                with exp_col2:
                    expected_roi = st.number_input("ROI (%)", 0.0, 150.0, step=10.0)
            
            st.markdown("---")
            
            if st.button("🔍 Calculate", type="primary", use_container_width=True):
                if not product_group:
                    st.error("⚠️ Select at least one product group")
                elif promo_start >= promo_end:
                    st.error("⚠️ End date must be after start date")
                else:
                    with st.spinner("Analyzing..."):
                        periods = calculate_promo_periods(promo_start, promo_end)
                        
                        pre_sales, pre_units = get_period_sales(df, retailer, product_group, periods['pre_start'], periods['pre_end'], periods['promo_days'])
                        promo_sales, promo_units = get_period_sales(df, retailer, product_group, periods['promo_start'], periods['promo_end'], periods['promo_days'])
                        post_sales, post_units = get_period_sales(df, retailer, product_group, periods['post_start'], periods['post_end'], periods['promo_days'])
                        
                        metrics = calculate_metrics(pre_sales, promo_sales, post_sales, trade_spend, flat_fee, pre_units, promo_units, post_units)
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
                            'expected_lift': expected_lift,
                            'expected_roi': expected_roi,
                            'metrics': metrics
                        }
                        st.rerun()
            
            if st.session_state.current_analysis:
                st.success("✅ Complete!")
                st.markdown("---")
                
                a = st.session_state.current_analysis
                
                st.markdown("## 📊 Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""<div class='period-card pre'><h3 style='color: #757575; margin:0;'>Pre-Promo</h3>
                    <p style='color: #9e9e9e; font-size: 0.9rem;'>{a['periods']['pre_start'].strftime('%m/%d')} - {a['periods']['pre_end'].strftime('%m/%d')}</p></div>""", unsafe_allow_html=True)
                    st.metric("Sales", f"${a['pre_sales']:,.0f}")
                    st.caption("Baseline")
                    st.metric("Units", f"{a['pre_units']:,.0f}")
                
                with col2:
                    st.markdown(f"""<div class='period-card during'><h3 style='color: #7cb342; margin:0;'>During Promo</h3>
                    <p style='color: #689f38; font-size: 0.9rem;'>{a['periods']['promo_start'].strftime('%m/%d')} - {a['periods']['promo_end'].strftime('%m/%d')}</p></div>""", unsafe_allow_html=True)
                    st.metric("Sales", f"${a['promo_sales']:,.0f}")
                    st.caption(f"Incr: ${a['promo_sales'] - a['pre_sales']:,.0f}")
                    st.metric("Units", f"{a['promo_units']:,.0f}")
                
                with col3:
                    st.markdown(f"""<div class='period-card post'><h3 style='color: #e57b8f; margin:0;'>Post-Promo</h3>
                    <p style='color: #e57b8f; font-size: 0.9rem;'>{a['periods']['post_start'].strftime('%m/%d')} - {a['periods']['post_end'].strftime('%m/%d')}</p></div>""", unsafe_allow_html=True)
                    st.metric("Sales", f"${a['post_sales']:,.0f}")
                    st.caption(f"Incr: ${a['post_sales'] - a['pre_sales']:,.0f}")
                    st.metric("Units", f"{a['post_units']:,.0f}")
                
                st.markdown("---")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 📈 Lift")
                    st.markdown("**Dollars**")
                    during_diff = a['metrics']['during_lift_dollars'] - a['expected_lift']
                    st.metric("During ($)", f"{a['metrics']['during_lift_dollars']:.1f}%", f"{during_diff:+.1f}%")
                    st.metric("Post ($)", f"{a['metrics']['post_lift_dollars']:.1f}%")
                    
                    st.markdown("**Units**")
                    st.metric("During (Units)", f"{a['metrics']['during_lift_units']:.1f}%")
                    st.metric("Post (Units)", f"{a['metrics']['post_lift_units']:.1f}%")
                    st.markdown("---")
                    st.metric("Expected", f"{a['expected_lift']:.1f}%")
                
                with col2:
                    st.markdown("### 💵 ROI")
                    roi_diff = a['metrics']['roi'] - a['expected_roi']
                    st.metric("Actual", f"{a['metrics']['roi']:.1f}%", f"{roi_diff:+.1f}%")
                    st.metric("Expected", f"{a['expected_roi']:.1f}%")
                    st.metric("Incremental", f"${a['metrics']['incremental_sales']:,.0f}")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(create_performance_chart(a['pre_sales'], a['promo_sales'], a['post_sales']), use_container_width=True)
                with col2:
                    st.plotly_chart(create_lift_gauge(a['metrics']['during_lift_dollars'], a['expected_lift']), use_container_width=True)
                
                st.markdown("---")
                st.markdown("### 📝 Notes")
                notes = st.text_area("Document insights", height=150, placeholder="Key learnings, recommendations...")
                
                if st.button("💾 Save", type="primary", use_container_width=True):
                    a['notes'] = notes
                    a['analysis_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    st.session_state.promo_analyses.append(a.copy())
                    st.session_state.current_analysis = None
                    st.success("✅ Saved!")
                    st.rerun()
        
        with tab2:
            st.markdown("## 📋 All Analyses")
            
            if not st.session_state.promo_analyses:
                st.info("No analyses yet. Create one in the 'New Analysis' tab!")
            else:
                col1, col2, col3, col4 = st.columns(4)
                
                avg_lift = sum(a['metrics']['during_lift_dollars'] for a in st.session_state.promo_analyses) / len(st.session_state.promo_analyses)
                avg_roi = sum(a['metrics']['roi'] for a in st.session_state.promo_analyses) / len(st.session_state.promo_analyses)
                total_spend = sum(a['trade_spend'] + a['flat_fee'] for a in st.session_state.promo_analyses)
                total_incremental = sum(a['metrics']['incremental_sales'] for a in st.session_state.promo_analyses)
                
                with col1:
                    st.metric("Avg Lift", f"{avg_lift:.1f}%")
                with col2:
                    st.metric("Avg ROI", f"{avg_roi:.1f}%")
                with col3:
                    st.metric("Total Spend", f"${total_spend:,.0f}")
                with col4:
                    st.metric("Total Incr", f"${total_incremental:,.0f}")
                
                st.markdown("---")
                
                for idx, a in enumerate(st.session_state.promo_analyses):
                    if isinstance(a['product_group'], list):
                        product_display = ', '.join(a['product_group'])
                    else:
                        product_display = str(a['product_group'])
                    
                    with st.expander(f"**{a['retailer']}** - {product_display} ({a['periods']['promo_start'].strftime('%m/%d/%Y')} - {a['periods']['promo_end'].strftime('%m/%d/%Y')})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**Pre**")
                            st.write(f"Sales: ${a['pre_sales']:,.0f}")
                            st.caption("Baseline")
                            st.write(f"Units: {a['pre_units']:,.0f}")
                        
                        with col2:
                            st.markdown("**During**")
                            st.write(f"Sales: ${a['promo_sales']:,.0f}")
                            st.caption(f"Incr: ${a['promo_sales'] - a['pre_sales']:,.0f}")
                            st.write(f"Units: {a['promo_units']:,.0f}")
                            st.write(f"Lift ($): {a['metrics']['during_lift_dollars']:.1f}%")
                            st.write(f"Lift (U): {a['metrics']['during_lift_units']:.1f}%")
                        
                        with col3:
                            st.markdown("**Post**")
                            st.write(f"Sales: ${a['post_sales']:,.0f}")
                            st.caption(f"Incr: ${a['post_sales'] - a['pre_sales']:,.0f}")
                            st.write(f"Units: {a['post_units']:,.0f}")
                            st.write(f"Lift ($): {a['metrics']['post_lift_dollars']:.1f}%")
                            st.write(f"Lift (U): {a['metrics']['post_lift_units']:.1f}%")
                        
                        st.markdown("**Performance**")
                        perf_col1, perf_col2 = st.columns(2)
                        with perf_col1:
                            st.write(f"Expected Lift: {a['expected_lift']:.1f}%")
                            st.write(f"Expected ROI: {a['expected_roi']:.1f}%")
                        with perf_col2:
                            st.write(f"Actual ROI: {a['metrics']['roi']:.1f}%")
                            st.write(f"Incremental: ${a['metrics']['incremental_sales']:,.0f}")
                        
                        if a.get('notes'):
                            st.markdown("**Notes:**")
                            st.write(a['notes'])
                        
                        if st.button(f"🗑️ Delete", key=f"del_{idx}"):
                            st.session_state.promo_analyses.pop(idx)
                            st.rerun()

if __name__ == "__main__":
    main()
