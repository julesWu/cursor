import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_basic_metrics(impressions_df, clicks_df, conversions_df, campaigns_df):
    """Calculate basic campaign performance metrics"""
    
    # Filter for won impressions only
    won_impressions = impressions_df[impressions_df['impression_outcome'] == 'won'].copy()
    
    # Group by campaign
    impression_metrics = won_impressions.groupby('campaign_id').agg({
        'win_price': ['sum', 'mean', 'count'],
        'timestamp': ['min', 'max']
    }).round(2)
    
    impression_metrics.columns = ['total_spend_raw', 'avg_cpm', 'impressions_served', 'first_impression', 'last_impression']
    
    # Calculate spend (CPM to actual spend)
    impression_metrics['spend'] = (impression_metrics['total_spend_raw'] * impression_metrics['impressions_served'] / 1000).round(2)
    impression_metrics['ecpm'] = (impression_metrics['spend'] / (impression_metrics['impressions_served'] / 1000)).round(2)
    
    # Click metrics
    click_metrics = clicks_df.groupby('campaign_id').agg({
        'click_id': 'count',
        'click_cost': 'sum'
    }).round(2)
    click_metrics.columns = ['clicks', 'click_spend']
    
    # Conversion metrics
    conversion_metrics = conversions_df.groupby('campaign_id').agg({
        'conversion_id': 'count',
        'conversion_value': 'sum'
    }).round(2)
    conversion_metrics.columns = ['conversions', 'conversion_value']
    
    # Combine all metrics
    metrics_df = impression_metrics.join(click_metrics, how='left').fillna(0)
    metrics_df = metrics_df.join(conversion_metrics, how='left').fillna(0)
    
    # Calculate derived metrics
    metrics_df['ctr'] = (metrics_df['clicks'] / metrics_df['impressions_served'] * 100).round(3)
    metrics_df['cpc'] = np.where(metrics_df['clicks'] > 0, 
                                 metrics_df['spend'] / metrics_df['clicks'], 0).round(2)
    metrics_df['cpa'] = np.where(metrics_df['conversions'] > 0,
                                 metrics_df['spend'] / metrics_df['conversions'], 0).round(2)
    metrics_df['roas'] = np.where(metrics_df['spend'] > 0,
                                  metrics_df['conversion_value'] / metrics_df['spend'], 0).round(2)
    metrics_df['conversion_rate'] = np.where(metrics_df['clicks'] > 0,
                                            metrics_df['conversions'] / metrics_df['clicks'] * 100, 0).round(3)
    
    # Add campaign information
    metrics_df = metrics_df.join(campaigns_df.set_index('campaign_id')[['campaign_name', 'advertiser_id', 'budget_total', 'budget_daily', 'objective', 'status']])
    
    return metrics_df.reset_index()

def calculate_revenue_by_channel(impressions_df, campaigns_df, advertisers_df):
    """Calculate revenue breakdown by different channels/dimensions"""
    
    won_impressions = impressions_df[impressions_df['impression_outcome'] == 'won'].copy()
    won_impressions['spend'] = (won_impressions['win_price'] * 1 / 1000).round(2)  # Convert CPM to spend per impression
    
    # Revenue by device type
    device_revenue = won_impressions.groupby('device_type')['spend'].sum().reset_index()
    device_revenue.columns = ['channel', 'revenue']
    device_revenue['channel_type'] = 'device'
    
    # Revenue by auction type
    auction_revenue = won_impressions.groupby('auction_type')['spend'].sum().reset_index()
    auction_revenue.columns = ['channel', 'revenue']
    auction_revenue['channel_type'] = 'auction'
    
    # Revenue by geo (top countries)
    geo_revenue = won_impressions.groupby('geo_country')['spend'].sum().reset_index()
    geo_revenue.columns = ['channel', 'revenue']
    geo_revenue['channel_type'] = 'geo'
    
    # Revenue by industry (join with campaigns and advertisers)
    impression_with_industry = won_impressions.merge(campaigns_df[['campaign_id', 'advertiser_id']], on='campaign_id')
    impression_with_industry = impression_with_industry.merge(advertisers_df[['advertiser_id', 'industry']], on='advertiser_id')
    industry_revenue = impression_with_industry.groupby('industry')['spend'].sum().reset_index()
    industry_revenue.columns = ['channel', 'revenue']
    industry_revenue['channel_type'] = 'industry'
    
    # Combine all revenue data
    all_revenue = pd.concat([device_revenue, auction_revenue, geo_revenue, industry_revenue], ignore_index=True)
    
    return all_revenue

def calculate_margin_analysis(impressions_df, campaigns_df):
    """Calculate buy-side vs sell-side margin analysis"""
    
    won_impressions = impressions_df[impressions_df['impression_outcome'] == 'won'].copy()
    
    # Simulate buy-side and sell-side rates
    # Buy-side = what we pay to publishers (simulate as 70-80% of win price)
    # Sell-side = what advertisers pay us (win price)
    won_impressions['buy_side_cost'] = (won_impressions['win_price'] * np.random.uniform(0.7, 0.8, len(won_impressions))).round(2)
    won_impressions['sell_side_revenue'] = won_impressions['win_price']
    won_impressions['margin'] = (won_impressions['sell_side_revenue'] - won_impressions['buy_side_cost']).round(2)
    won_impressions['margin_pct'] = (won_impressions['margin'] / won_impressions['sell_side_revenue'] * 100).round(2)
    
    # Aggregate by campaign
    margin_by_campaign = won_impressions.groupby('campaign_id').agg({
        'buy_side_cost': 'sum',
        'sell_side_revenue': 'sum',
        'margin': 'sum',
        'margin_pct': 'mean',
        'timestamp': 'count'
    }).round(2)
    
    margin_by_campaign.columns = ['total_buy_cost', 'total_sell_revenue', 'total_margin', 'avg_margin_pct', 'impressions']
    margin_by_campaign['margin_per_impression'] = (margin_by_campaign['total_margin'] / margin_by_campaign['impressions']).round(4)
    
    # Add campaign details
    margin_by_campaign = margin_by_campaign.join(campaigns_df.set_index('campaign_id')[['campaign_name', 'advertiser_id', 'objective']])
    
    return margin_by_campaign.reset_index()

def calculate_pacing_analysis(impressions_df, campaigns_df):
    """Calculate pacing vs budget analysis"""
    
    won_impressions = impressions_df[impressions_df['impression_outcome'] == 'won'].copy()
    won_impressions['spend'] = (won_impressions['win_price'] / 1000).round(2)
    won_impressions['date'] = won_impressions['timestamp'].dt.date
    
    pacing_data = []
    
    for _, campaign in campaigns_df.iterrows():
        campaign_impressions = won_impressions[won_impressions['campaign_id'] == campaign['campaign_id']]
        
        if len(campaign_impressions) == 0:
            continue
            
        # Daily spend
        daily_spend = campaign_impressions.groupby('date')['spend'].sum()
        
        # Calculate cumulative metrics
        total_spend = daily_spend.sum()
        campaign_days = (campaign['end_date'] - campaign['start_date']).days + 1
        days_elapsed = len(daily_spend)
        
        # Pacing metrics
        budget_spent_pct = (total_spend / campaign['budget_total'] * 100) if campaign['budget_total'] > 0 else 0
        time_elapsed_pct = (days_elapsed / campaign_days * 100) if campaign_days > 0 else 0
        
        pacing_status = 'on_pace'
        if budget_spent_pct > time_elapsed_pct + 10:
            pacing_status = 'ahead'
        elif budget_spent_pct < time_elapsed_pct - 10:
            pacing_status = 'behind'
            
        avg_daily_spend = total_spend / days_elapsed if days_elapsed > 0 else 0
        forecasted_spend = avg_daily_spend * campaign_days
        
        pacing_data.append({
            'campaign_id': campaign['campaign_id'],
            'campaign_name': campaign['campaign_name'],
            'budget_total': campaign['budget_total'],
            'budget_daily': campaign['budget_daily'],
            'total_spend': round(total_spend, 2),
            'avg_daily_spend': round(avg_daily_spend, 2),
            'forecasted_spend': round(forecasted_spend, 2),
            'budget_spent_pct': round(budget_spent_pct, 1),
            'time_elapsed_pct': round(time_elapsed_pct, 1),
            'pacing_status': pacing_status,
            'days_active': days_elapsed,
            'total_days': campaign_days
        })
    
    return pd.DataFrame(pacing_data)

def calculate_cash_flow_analysis(impressions_df, campaigns_df, advertisers_df):
    """Calculate Account Receivable/Payable for cash flow health"""
    
    won_impressions = impressions_df[impressions_df['impression_outcome'] == 'won'].copy()
    won_impressions['spend'] = (won_impressions['win_price'] / 1000).round(2)
    
    # Simulate payment terms
    # Advertisers (receivables): typically pay 30-60 days after month end
    # Publishers (payables): we typically pay 30 days after month end
    
    won_impressions['month_year'] = won_impressions['timestamp'].dt.to_period('M')
    
    # Group by advertiser (receivables)
    impression_with_advertiser = won_impressions.merge(campaigns_df[['campaign_id', 'advertiser_id']], on='campaign_id')
    
    receivables = impression_with_advertiser.groupby(['advertiser_id', 'month_year'])['spend'].sum().reset_index()
    receivables = receivables.merge(advertisers_df[['advertiser_id', 'advertiser_name']], on='advertiser_id')
    
    # Simulate aging (some payments overdue)
    current_date = datetime.now().date()
    receivables['due_date'] = receivables['month_year'].dt.end_time.dt.date + timedelta(days=45)  # 45 days payment terms
    receivables['days_outstanding'] = (current_date - receivables['due_date']).dt.days
    receivables['aging_category'] = receivables['days_outstanding'].apply(
        lambda x: 'current' if x <= 0 else ('30_days' if x <= 30 else ('60_days' if x <= 60 else '90_plus_days'))
    )
    
    # Simulate payment status (90% paid, 10% outstanding)
    receivables['payment_status'] = np.random.choice(['paid', 'outstanding'], size=len(receivables), p=[0.9, 0.1])
    receivables['outstanding_amount'] = receivables.apply(
        lambda x: x['spend'] if x['payment_status'] == 'outstanding' else 0, axis=1
    ).round(2)
    
    # Group by publisher for payables (simulate publisher data)
    publishers = won_impressions['publisher_id'].unique()
    publisher_names = {pub_id: f"Publisher {pub_id.split('_')[1]}" for pub_id in publishers}
    
    # Simulate publisher revenue share (70-80% of our revenue)
    won_impressions['publisher_payout'] = (won_impressions['spend'] * np.random.uniform(0.7, 0.8, len(won_impressions))).round(2)
    
    payables = won_impressions.groupby(['publisher_id', 'month_year'])['publisher_payout'].sum().reset_index()
    payables['publisher_name'] = payables['publisher_id'].map(publisher_names)
    payables['due_date'] = payables['month_year'].dt.end_time.dt.date + timedelta(days=30)  # 30 days payment terms
    payables['days_outstanding'] = (current_date - payables['due_date']).dt.days
    payables['aging_category'] = payables['days_outstanding'].apply(
        lambda x: 'current' if x <= 0 else ('30_days' if x <= 30 else ('60_days' if x <= 60 else '90_plus_days'))
    )
    
    # Simulate payment status (95% paid, 5% outstanding for payables)
    payables['payment_status'] = np.random.choice(['paid', 'outstanding'], size=len(payables), p=[0.95, 0.05])
    payables['outstanding_amount'] = payables.apply(
        lambda x: x['publisher_payout'] if x['payment_status'] == 'outstanding' else 0, axis=1
    ).round(2)
    
    return receivables, payables

def create_trend_chart(data, x_col, y_col, title, line_group=None):
    """Create line chart for trends over time"""
    
    if line_group:
        fig = px.line(data, x=x_col, y=y_col, color=line_group, title=title)
    else:
        fig = px.line(data, x=x_col, y=y_col, title=title)
    
    fig.update_layout(
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
        hovermode='x unified'
    )
    
    return fig

def create_revenue_chart(revenue_data, chart_type='bar'):
    """Create revenue visualization by channel"""
    
    if chart_type == 'bar':
        fig = px.bar(revenue_data, x='channel', y='revenue', color='channel_type',
                    title='Revenue by Channel/Partner')
    else:
        fig = px.pie(revenue_data, values='revenue', names='channel',
                    title='Revenue Distribution by Channel')
    
    fig.update_layout(xaxis_title='Channel', yaxis_title='Revenue ($)')
    
    return fig

def create_margin_chart(margin_data):
    """Create margin analysis visualization"""
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Revenue bars
    fig.add_trace(
        go.Bar(x=margin_data['campaign_name'], y=margin_data['total_sell_revenue'], 
               name='Revenue', marker_color='lightblue'),
        secondary_y=False,
    )
    
    # Margin percentage line
    fig.add_trace(
        go.Scatter(x=margin_data['campaign_name'], y=margin_data['avg_margin_pct'],
                  mode='lines+markers', name='Margin %', line=dict(color='red')),
        secondary_y=True,
    )
    
    fig.update_xaxes(title_text="Campaign")
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig.update_yaxes(title_text="Margin (%)", secondary_y=True)
    fig.update_layout(title_text="Revenue vs Margin Analysis by Campaign")
    
    return fig

def create_pacing_chart(pacing_data):
    """Create pacing analysis visualization"""
    
    fig = px.scatter(pacing_data, x='time_elapsed_pct', y='budget_spent_pct',
                    color='pacing_status', size='total_spend',
                    hover_data=['campaign_name', 'total_spend', 'forecasted_spend'],
                    title='Campaign Pacing: Budget Spent vs Time Elapsed')
    
    # Add diagonal line for perfect pacing
    fig.add_shape(type="line", x0=0, y0=0, x1=100, y1=100,
                 line=dict(color="gray", width=2, dash="dash"))
    
    fig.update_layout(
        xaxis_title="Time Elapsed (%)",
        yaxis_title="Budget Spent (%)",
        annotations=[
            dict(x=50, y=50, text="Perfect Pacing", showarrow=False, textangle=-45)
        ]
    )
    
    return fig

def prepare_time_series_data(impressions_df, clicks_df, conversions_df):
    """Prepare time series data for trend analysis"""
    
    won_impressions = impressions_df[impressions_df['impression_outcome'] == 'won'].copy()
    won_impressions['spend'] = (won_impressions['win_price'] / 1000).round(2)
    won_impressions['date'] = won_impressions['timestamp'].dt.date
    
    # Daily aggregations
    daily_impressions = won_impressions.groupby('date').agg({
        'campaign_id': 'count',
        'spend': 'sum',
        'win_price': 'mean'
    }).rename(columns={'campaign_id': 'impressions', 'win_price': 'avg_cpm'}).round(2)
    
    daily_clicks = clicks_df.groupby(clicks_df['timestamp'].dt.date).agg({
        'click_id': 'count',
        'click_cost': 'sum'
    }).rename(columns={'click_id': 'clicks'}).round(2)
    
    daily_conversions = conversions_df.groupby(conversions_df['timestamp'].dt.date).agg({
        'conversion_id': 'count',
        'conversion_value': 'sum'
    }).rename(columns={'conversion_id': 'conversions'}).round(2)
    
    # Combine daily data
    daily_data = daily_impressions.join(daily_clicks, how='left').fillna(0)
    daily_data = daily_data.join(daily_conversions, how='left').fillna(0)
    
    # Calculate derived metrics
    daily_data['ctr'] = (daily_data['clicks'] / daily_data['impressions'] * 100).round(3)
    daily_data['cpc'] = np.where(daily_data['clicks'] > 0, 
                                daily_data['spend'] / daily_data['clicks'], 0).round(2)
    daily_data['cpa'] = np.where(daily_data['conversions'] > 0,
                                daily_data['spend'] / daily_data['conversions'], 0).round(2)
    
    return daily_data.reset_index()

def format_currency(value):
    """Format numbers as currency"""
    return f"${value:,.2f}"

def format_percentage(value):
    """Format numbers as percentage"""
    return f"{value:.2f}%"

def format_number(value):
    """Format large numbers with K/M suffixes"""
    if value >= 1000000:
        return f"{value/1000000:.1f}M"
    elif value >= 1000:
        return f"{value/1000:.1f}K"
    else:
        return f"{value:,.0f}"
