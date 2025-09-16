# ACME Corp - Campaign Performance Dashboard

A comprehensive Streamlit dashboard for analyzing adtech campaign performance, built specifically for ACME Corp to monitor and optimize advertising campaigns across multiple channels and partners.

## 🎯 Features

### Multi-Page Dashboard
- **Campaign Overview**: Key performance indicators, trends, and detailed campaign metrics
- **Revenue Analysis**: Channel performance, device breakdown, geography, and industry analysis  
- **Margin & Pacing**: Buy-side vs sell-side margin analysis and budget pacing monitoring
- **Cash Flow Analysis**: Account receivables/payables tracking and financial health monitoring

### Interactive Features
- **Date range filtering** for custom time period analysis
- **Multi-select filters** for advertisers, campaign status, and device types
- **Real-time metric calculations** with automatic data refresh
- **Responsive charts and visualizations** using Plotly

### Key Metrics & Analytics
- **Performance Metrics**: CTR, CPC, CPA, eCPM, ROAS, conversion rates
- **Revenue Analysis**: Channel partner performance, device optimization
- **Margin Analysis**: Profit margins, buy-side vs sell-side take rates  
- **Pacing Analysis**: Budget vs spend tracking, forecasting
- **Cash Flow**: AR/AP aging, payment health across advertisers and publishers

## 📊 Data Overview

The dashboard generates realistic campaign data spanning **5 years (2020-2024)** with:

- **50 advertisers** across 10 industry verticals
- **200+ campaigns** with varying objectives and budgets
- **500K+ impressions** with realistic win rates and pricing
- **Click and conversion data** with industry-standard rates
- **Multi-dimensional breakdowns** by device, geography, auction type

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Databricks environment (for deployment)

### Installation

1. **Clone or download** the project files to your Databricks workspace

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**:
   ```bash
   streamlit run app.py
   ```

4. **Access the dashboard** at `http://localhost:8501` (or your Databricks app URL)

### Quick Start
The application will automatically generate sample data on first run. No additional setup required!

## 📁 Project Structure

```
├── app.py              # Main Streamlit application with multi-page navigation
├── data_generator.py   # Synthetic campaign data generation using Faker
├── utils.py           # Metric calculations and chart generation utilities  
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🔧 Key Components

### Data Generator (`data_generator.py`)
Generates realistic AdTech data including:
- **Advertiser entities** with industry classifications
- **Campaign hierarchies** with budgets and objectives  
- **Creative assets** with multiple formats and dimensions
- **Impression fact tables** with bid/win prices and outcomes
- **Click and conversion events** with realistic attribution

### Utility Functions (`utils.py`) 
Provides calculation engines for:
- **Core performance metrics** (CTR, CPC, CPA, eCPM, ROAS)
- **Revenue analysis** by channel, device, geography
- **Margin calculations** with buy/sell-side breakdowns
- **Pacing analysis** with budget vs actual tracking
- **Cash flow modeling** with AR/AP aging simulation

### Main Application (`app.py`)
Features a responsive multi-page interface with:
- **Sidebar navigation** and filtering controls
- **Interactive visualizations** using Plotly charts
- **Real-time metric updates** based on filter selections
- **Data tables** with formatted currency and percentage displays

## 📈 Dashboard Pages

### 1. Campaign Overview
- Executive KPI summary with total spend, impressions, CTR, conversions, ROAS
- Time series trend analysis for spend, eCPM, CTR, CPC, conversions, CPA
- Detailed campaign performance table with sortable metrics

### 2. Revenue Analysis  
- Revenue breakdown by channel type (device, auction, geography, industry)
- Interactive charts showing performance across different dimensions
- Device-specific optimization insights and geographic performance

### 3. Margin & Pacing
- Buy-side vs sell-side margin analysis with profitability insights
- Campaign pacing visualization showing budget vs time elapsed
- Pacing status distribution and forecasting for budget management

### 4. Cash Flow Analysis
- Account receivables tracking with aging analysis
- Account payables monitoring for publisher payments  
- Monthly cash flow trends and outstanding balance management

## 🎨 Customization

### Adding New Metrics
1. Extend calculation functions in `utils.py`
2. Add new chart types and visualizations
3. Update the main dashboard in `app.py` with new displays

### Modifying Data Generation
1. Adjust parameters in `data_generator.py` for different scales
2. Add new dimensions or entities as needed
3. Modify data relationships and business logic

### Styling and Branding
1. Update CSS styles in `app.py` for custom theming
2. Modify color schemes in Plotly charts
3. Add company logos and branding elements

## 📋 Technical Requirements

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis  
- **NumPy**: Numerical computing and calculations
- **Plotly**: Interactive data visualization
- **Faker**: Realistic fake data generation
- **Python 3.8+**: Core runtime environment

## 🐛 Troubleshooting

### Common Issues

**Data Loading Errors**: If the dashboard fails to load data, check that all dependencies are properly installed.

**Memory Issues**: For large datasets, consider reducing the number of impressions generated in `data_generator.py`.

**Performance**: Use Streamlit's caching (`@st.cache_data`) to improve load times with large datasets.

## 📝 Support

For questions, issues, or feature requests, please contact the ACME Corp data team or submit feedback through your organization's standard channels.

---

**Built with ❤️ for ACME Corp AdTech Analytics**
