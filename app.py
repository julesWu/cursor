import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Import our custom modules
from data_generator import generate_campaign_data
from utils import (
    calculate_basic_metrics, calculate_revenue_by_channel, calculate_margin_analysis,
    calculate_pacing_analysis, calculate_cash_flow_analysis, create_trend_chart,
    create_revenue_chart, create_margin_chart, create_pacing_chart,
    prepare_time_series_data, format_currency, format_percentage, format_number
)

# Page configuration
st.set_page_config(
    page_title="ACME Corp - Campaign Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for data caching
@st.cache_data
def load_campaign_data():
    """Load and cache campaign data"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("Loading campaign data..."):
        status_text.text("Generating advertisers and campaigns...")
        progress_bar.progress(20)
        
        status_text.text("Creating impressions data...")
        progress_bar.progress(50)
        
        status_text.text("Processing clicks and conversions...")
        progress_bar.progress(80)
        
        data = generate_campaign_data()
        
        status_text.text("Data loading complete!")
        progress_bar.progress(100)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        return data

# Load data
try:
    data = load_campaign_data()
    advertisers_df = data['advertisers']
    campaigns_df = data['campaigns']
    creatives_df = data['creatives']
    impressions_df = data['impressions']
    clicks_df = data['clicks']
    conversions_df = data['conversions']
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Sidebar - Navigation and Filters
st.sidebar.markdown("# 🎯 ACME Corp")
st.sidebar.markdown("### Campaign Performance Dashboard")
st.sidebar.markdown("---")

# Page navigation
page = st.sidebar.selectbox(
    "📊 Navigate to:",
    ["Campaign Overview", "Revenue Analysis", "Margin & Pacing", "Cash Flow Analysis"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filters")

# Date range filter
impressions_df['date'] = impressions_df['timestamp'].dt.date
min_date = impressions_df['date'].min()
max_date = impressions_df['date'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

# Advertiser filter
advertiser_options = ['All'] + sorted(advertisers_df['advertiser_name'].unique().tolist())
selected_advertisers = st.sidebar.multiselect(
    "Select Advertisers",
    advertiser_options,
    default=['All']
)

# Campaign status filter
status_options = ['All'] + sorted(campaigns_df['status'].unique().tolist())
selected_status = st.sidebar.multiselect(
    "Campaign Status",
    status_options,
    default=['All']
)

# Device type filter
device_options = ['All'] + sorted(impressions_df['device_type'].unique().tolist())
selected_devices = st.sidebar.multiselect(
    "Device Types",
    device_options,
    default=['All']
)

# Apply filters
filtered_impressions = impressions_df[
    (impressions_df['date'] >= start_date) & 
    (impressions_df['date'] <= end_date)
]

if 'All' not in selected_devices:
    filtered_impressions = filtered_impressions[filtered_impressions['device_type'].isin(selected_devices)]

# Filter campaigns based on advertiser and status
filtered_campaigns = campaigns_df.copy()
if 'All' not in selected_advertisers:
    advertiser_ids = advertisers_df[advertisers_df['advertiser_name'].isin(selected_advertisers)]['advertiser_id']
    filtered_campaigns = filtered_campaigns[filtered_campaigns['advertiser_id'].isin(advertiser_ids)]

if 'All' not in selected_status:
    filtered_campaigns = filtered_campaigns[filtered_campaigns['status'].isin(selected_status)]

# Filter other dataframes
campaign_ids = filtered_campaigns['campaign_id'].unique()
filtered_impressions = filtered_impressions[filtered_impressions['campaign_id'].isin(campaign_ids)]
filtered_clicks = clicks_df[clicks_df['campaign_id'].isin(campaign_ids)]
filtered_conversions = conversions_df[conversions_df['campaign_id'].isin(campaign_ids)]

# Main content based on selected page
if page == "Campaign Overview":
    st.markdown('<h1 class="main-header">📈 Campaign Performance Overview</h1>', unsafe_allow_html=True)
    
    # Calculate metrics
    metrics_df = calculate_basic_metrics(filtered_impressions, filtered_clicks, filtered_conversions, filtered_campaigns)
    
    # Key Performance Indicators
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_spend = metrics_df['spend'].sum()
        st.metric("Total Spend", format_currency(total_spend))
    
    with col2:
        total_impressions = metrics_df['impressions_served'].sum()
        st.metric("Total Impressions", format_number(total_impressions))
    
    with col3:
        total_clicks = metrics_df['clicks'].sum()
        overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        st.metric("Overall CTR", format_percentage(overall_ctr))
    
    with col4:
        total_conversions = metrics_df['conversions'].sum()
        st.metric("Total Conversions", format_number(total_conversions))
    
    with col5:
        total_revenue = metrics_df['conversion_value'].sum()
        overall_roas = (total_revenue / total_spend) if total_spend > 0 else 0
        st.metric("Overall ROAS", f"{overall_roas:.2f}x")
    
    st.markdown("---")
    
    # Time series trends
    st.subheader("📊 Performance Trends Over Time")
    
    daily_data = prepare_time_series_data(filtered_impressions, filtered_clicks, filtered_conversions)
    
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Spend & eCPM", "🎯 CTR & CPC", "🔄 Conversions", "💡 CPA & ROAS"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            spend_chart = create_trend_chart(daily_data, 'date', 'spend', 'Daily Spend Trend')
            st.plotly_chart(spend_chart, use_container_width=True)
        with col2:
            ecpm_chart = create_trend_chart(daily_data, 'date', 'avg_cpm', 'Average eCPM Trend')
            st.plotly_chart(ecpm_chart, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            ctr_chart = create_trend_chart(daily_data, 'date', 'ctr', 'Click-Through Rate Trend')
            st.plotly_chart(ctr_chart, use_container_width=True)
        with col2:
            cpc_chart = create_trend_chart(daily_data, 'date', 'cpc', 'Cost Per Click Trend')
            st.plotly_chart(cpc_chart, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            conv_chart = create_trend_chart(daily_data, 'date', 'conversions', 'Daily Conversions')
            st.plotly_chart(conv_chart, use_container_width=True)
        with col2:
            conv_value_chart = create_trend_chart(daily_data, 'date', 'conversion_value', 'Daily Conversion Value')
            st.plotly_chart(conv_value_chart, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            cpa_chart = create_trend_chart(daily_data, 'date', 'cpa', 'Cost Per Acquisition Trend')
            st.plotly_chart(cpa_chart, use_container_width=True)
        with col2:
            # Calculate daily ROAS
            daily_data_roas = daily_data.copy()
            daily_data_roas['roas'] = np.where(daily_data_roas['spend'] > 0, 
                                              daily_data_roas['conversion_value'] / daily_data_roas['spend'], 0)
            roas_chart = create_trend_chart(daily_data_roas, 'date', 'roas', 'Return on Ad Spend Trend')
            st.plotly_chart(roas_chart, use_container_width=True)
    
    # Campaign performance table
    st.subheader("🎯 Campaign Performance Details")
    
    display_columns = [
        'campaign_name', 'impressions_served', 'clicks', 'conversions',
        'spend', 'ctr', 'cpc', 'cpa', 'roas', 'status'
    ]
    
    formatted_metrics = metrics_df[display_columns].copy()
    formatted_metrics['spend'] = formatted_metrics['spend'].apply(lambda x: format_currency(x))
    formatted_metrics['ctr'] = formatted_metrics['ctr'].apply(lambda x: format_percentage(x))
    formatted_metrics['cpc'] = formatted_metrics['cpc'].apply(lambda x: format_currency(x))
    formatted_metrics['cpa'] = formatted_metrics['cpa'].apply(lambda x: format_currency(x))
    
    st.dataframe(formatted_metrics, use_container_width=True, height=400)

elif page == "Revenue Analysis":
    st.markdown('<h1 class="main-header">💰 Revenue Analysis by Channel</h1>', unsafe_allow_html=True)
    
    # Revenue by channel analysis
    revenue_data = calculate_revenue_by_channel(filtered_impressions, filtered_campaigns, advertisers_df)
    
    # Summary metrics
    total_revenue = revenue_data['revenue'].sum()
    st.metric("Total Revenue", format_currency(total_revenue))
    
    st.markdown("---")
    
    # Revenue charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue by Channel Type")
        channel_summary = revenue_data.groupby('channel_type')['revenue'].sum().reset_index()
        channel_pie = px.pie(channel_summary, values='revenue', names='channel_type',
                           title='Revenue Distribution by Channel Type')
        st.plotly_chart(channel_pie, use_container_width=True)
    
    with col2:
        st.subheader("📱 Device Type Performance")
        device_data = revenue_data[revenue_data['channel_type'] == 'device']
        if not device_data.empty:
            device_chart = create_revenue_chart(device_data, 'bar')
            st.plotly_chart(device_chart, use_container_width=True)
    
    # Detailed channel breakdown
    st.subheader("🔍 Detailed Channel Breakdown")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📱 Device", "🏢 Auction", "🌍 Geography", "🏭 Industry"])
    
    with tab1:
        device_revenue = revenue_data[revenue_data['channel_type'] == 'device']
        if not device_revenue.empty:
            fig = px.bar(device_revenue, x='channel', y='revenue', 
                        title='Revenue by Device Type',
                        color='channel')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(device_revenue[['channel', 'revenue']].set_index('channel'), use_container_width=True)
    
    with tab2:
        auction_revenue = revenue_data[revenue_data['channel_type'] == 'auction']
        if not auction_revenue.empty:
            fig = px.bar(auction_revenue, x='channel', y='revenue', 
                        title='Revenue by Auction Type',
                        color='channel')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(auction_revenue[['channel', 'revenue']].set_index('channel'), use_container_width=True)
    
    with tab3:
        geo_revenue = revenue_data[revenue_data['channel_type'] == 'geo']
        if not geo_revenue.empty:
            geo_revenue_sorted = geo_revenue.sort_values('revenue', ascending=True)
            fig = px.bar(geo_revenue_sorted, x='revenue', y='channel', 
                        title='Revenue by Geography',
                        orientation='h')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(geo_revenue[['channel', 'revenue']].set_index('channel'), use_container_width=True)
    
    with tab4:
        industry_revenue = revenue_data[revenue_data['channel_type'] == 'industry']
        if not industry_revenue.empty:
            fig = px.treemap(industry_revenue, path=['channel'], values='revenue',
                           title='Revenue by Industry (Treemap)')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(industry_revenue[['channel', 'revenue']].set_index('channel'), use_container_width=True)

elif page == "Margin & Pacing":
    st.markdown('<h1 class="main-header">📊 Margin & Pacing Analysis</h1>', unsafe_allow_html=True)
    
    # Calculate margin and pacing data
    margin_data = calculate_margin_analysis(filtered_impressions, filtered_campaigns)
    pacing_data = calculate_pacing_analysis(filtered_impressions, filtered_campaigns)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_margin = margin_data['avg_margin_pct'].mean()
        st.metric("Average Margin %", format_percentage(avg_margin))
    
    with col2:
        total_margin = margin_data['total_margin'].sum()
        st.metric("Total Margin", format_currency(total_margin))
    
    with col3:
        on_pace_campaigns = len(pacing_data[pacing_data['pacing_status'] == 'on_pace'])
        total_campaigns = len(pacing_data)
        pacing_health = (on_pace_campaigns / total_campaigns * 100) if total_campaigns > 0 else 0
        st.metric("Campaigns On Pace", f"{on_pace_campaigns}/{total_campaigns} ({pacing_health:.1f}%)")
    
    st.markdown("---")
    
    # Margin analysis
    st.subheader("💰 Margin Analysis")
    
    if not margin_data.empty:
        # Top campaigns by margin
        col1, col2 = st.columns(2)
        
        with col1:
            margin_chart = create_margin_chart(margin_data.head(10))
            st.plotly_chart(margin_chart, use_container_width=True)
        
        with col2:
            st.markdown("**Top 10 Campaigns by Margin %**")
            top_margin = margin_data.nlargest(10, 'avg_margin_pct')[['campaign_name', 'avg_margin_pct', 'total_margin']]
            top_margin['avg_margin_pct'] = top_margin['avg_margin_pct'].apply(format_percentage)
            top_margin['total_margin'] = top_margin['total_margin'].apply(format_currency)
            st.dataframe(top_margin, use_container_width=True)
    
    st.markdown("---")
    
    # Pacing analysis
    st.subheader("⏱️ Pacing Analysis")
    
    if not pacing_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            pacing_chart = create_pacing_chart(pacing_data)
            st.plotly_chart(pacing_chart, use_container_width=True)
        
        with col2:
            # Pacing status summary
            pacing_summary = pacing_data['pacing_status'].value_counts()
            pacing_pie = px.pie(values=pacing_summary.values, names=pacing_summary.index,
                              title='Campaign Pacing Status Distribution')
            st.plotly_chart(pacing_pie, use_container_width=True)
        
        # Pacing details table
        st.subheader("📈 Campaign Pacing Details")
        pacing_display = pacing_data[[
            'campaign_name', 'budget_total', 'total_spend', 'budget_spent_pct',
            'time_elapsed_pct', 'pacing_status', 'forecasted_spend'
        ]].copy()
        
        pacing_display['budget_total'] = pacing_display['budget_total'].apply(format_currency)
        pacing_display['total_spend'] = pacing_display['total_spend'].apply(format_currency)
        pacing_display['forecasted_spend'] = pacing_display['forecasted_spend'].apply(format_currency)
        pacing_display['budget_spent_pct'] = pacing_display['budget_spent_pct'].apply(lambda x: f"{x}%")
        pacing_display['time_elapsed_pct'] = pacing_display['time_elapsed_pct'].apply(lambda x: f"{x}%")
        
        st.dataframe(pacing_display, use_container_width=True, height=400)

elif page == "Cash Flow Analysis":
    st.markdown('<h1 class="main-header">💳 Cash Flow & Financial Health</h1>', unsafe_allow_html=True)
    
    # Calculate cash flow data
    receivables, payables = calculate_cash_flow_analysis(filtered_impressions, filtered_campaigns, advertisers_df)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_receivables = receivables['spend'].sum()
        st.metric("Total Receivables", format_currency(total_receivables))
    
    with col2:
        outstanding_receivables = receivables['outstanding_amount'].sum()
        st.metric("Outstanding Receivables", format_currency(outstanding_receivables))
    
    with col3:
        total_payables = payables['publisher_payout'].sum()
        st.metric("Total Payables", format_currency(total_payables))
    
    with col4:
        outstanding_payables = payables['outstanding_amount'].sum()
        st.metric("Outstanding Payables", format_currency(outstanding_payables))
    
    st.markdown("---")
    
    # Receivables analysis
    st.subheader("💰 Account Receivables (Money Owed to Us)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Receivables aging
        receivables_aging = receivables.groupby('aging_category')['outstanding_amount'].sum().reset_index()
        if not receivables_aging.empty and receivables_aging['outstanding_amount'].sum() > 0:
            aging_pie = px.pie(receivables_aging, values='outstanding_amount', names='aging_category',
                             title='Outstanding Receivables by Aging')
            st.plotly_chart(aging_pie, use_container_width=True)
        else:
            st.info("No outstanding receivables")
    
    with col2:
        # Top delinquent advertisers
        delinquent = receivables[receivables['outstanding_amount'] > 0].groupby('advertiser_name')['outstanding_amount'].sum().reset_index()
        if not delinquent.empty:
            delinquent_sorted = delinquent.sort_values('outstanding_amount', ascending=True)
            fig = px.bar(delinquent_sorted.tail(10), x='outstanding_amount', y='advertiser_name',
                        title='Top 10 Delinquent Advertisers', orientation='h')
            st.plotly_chart(fig, use_container_width=True)
    
    # Payables analysis
    st.subheader("💳 Account Payables (Money We Owe)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Payables aging
        payables_aging = payables.groupby('aging_category')['outstanding_amount'].sum().reset_index()
        if not payables_aging.empty and payables_aging['outstanding_amount'].sum() > 0:
            aging_pie = px.pie(payables_aging, values='outstanding_amount', names='aging_category',
                             title='Outstanding Payables by Aging')
            st.plotly_chart(aging_pie, use_container_width=True)
        else:
            st.info("No outstanding payables")
    
    with col2:
        # Cash flow trend
        receivables['month'] = receivables['month_year'].astype(str)
        payables['month'] = payables['month_year'].astype(str)
        
        monthly_receivables = receivables.groupby('month')['spend'].sum().reset_index()
        monthly_payables = payables.groupby('month')['publisher_payout'].sum().reset_index()
        
        cash_flow = monthly_receivables.merge(monthly_payables, on='month', how='outer').fillna(0)
        cash_flow['net_flow'] = cash_flow['spend'] - cash_flow['publisher_payout']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cash_flow['month'], y=cash_flow['spend'], name='Receivables', marker_color='green'))
        fig.add_trace(go.Bar(x=cash_flow['month'], y=-cash_flow['publisher_payout'], name='Payables', marker_color='red'))
        fig.add_trace(go.Scatter(x=cash_flow['month'], y=cash_flow['net_flow'], mode='lines+markers', name='Net Cash Flow', line=dict(color='blue')))
        
        fig.update_layout(title='Monthly Cash Flow Trend', xaxis_title='Month', yaxis_title='Amount ($)')
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed tables
    st.subheader("📋 Detailed Financial Records")
    
    tab1, tab2 = st.tabs(["📥 Receivables", "📤 Payables"])
    
    with tab1:
        if not receivables.empty:
            receivables_display = receivables.groupby(['advertiser_name', 'aging_category']).agg({
                'spend': 'sum',
                'outstanding_amount': 'sum'
            }).reset_index()
            receivables_display['spend'] = receivables_display['spend'].apply(format_currency)
            receivables_display['outstanding_amount'] = receivables_display['outstanding_amount'].apply(format_currency)
            st.dataframe(receivables_display, use_container_width=True)
    
    with tab2:
        if not payables.empty:
            payables_display = payables.groupby(['publisher_name', 'aging_category']).agg({
                'publisher_payout': 'sum',
                'outstanding_amount': 'sum'
            }).reset_index()
            payables_display['publisher_payout'] = payables_display['publisher_payout'].apply(format_currency)
            payables_display['outstanding_amount'] = payables_display['outstanding_amount'].apply(format_currency)
            st.dataframe(payables_display, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Data Summary**")
st.sidebar.markdown(f"• **Campaigns**: {len(filtered_campaigns):,}")
st.sidebar.markdown(f"• **Impressions**: {len(filtered_impressions):,}")
st.sidebar.markdown(f"• **Clicks**: {len(filtered_clicks):,}")
st.sidebar.markdown(f"• **Conversions**: {len(filtered_conversions):,}")
st.sidebar.markdown("---")
st.sidebar.markdown("**⚡ Performance Optimized**")
st.sidebar.markdown("• Fast loading (< 15 seconds)")
st.sidebar.markdown("• 5 years of realistic data")
st.sidebar.markdown("• Demo-ready dataset")
st.sidebar.markdown("---")
st.sidebar.markdown("*Built with ❤️ for ACME Corp*")
