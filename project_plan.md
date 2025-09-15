This project plan should be the source of truth for building this project. All requests and guidelines should be followed and the project should be built to spec based on the requirements below. If clarification is needed, ask prior to changing the plan. Update the project plan through the project with updates.

Goal:
- Build a streamlit app that shows an adtech company's campaign performance. The fake company's name is ACME Corp.

Requirements:
- The app should be interactive with things like filters.
- The app should also have charts showing aspects of the compaign like:
	- revenue by channel/partner
	- eCPM, CPM, CPC, CPA trends
	- Margin Analysis (buy-side vs. sell-side take rates)
	- Pacing vs. Budget (daily/weekly/monthly targets)
	- Account Receivable/Payble (cash flow health across advertisers and publishers)
- Need a readme.md file
- need a requirements.txt file

## Detailed Implementation Specifications ###

### Data Requirements:
-Generate 5 years of quarterly campaign data (2020-2024, 20 quarters total)
- Use Python's faker library along with numpy for realistic patterns

- ## 1. Core Entity Tables

### Advertiser Table
- `advertiser_id` (string, PK)
- `advertiser_name` (string)
- `industry` (string, nullable)
- `account_manager` (string, nullable)

### Campaign Table
- `campaign_id` (string, PK)
- `campaign_name` (string)
- `advertiser_id` (string, FK → advertiser.advertiser_id)
- `start_date` (date)
- `end_date` (date)
- `budget_total` (decimal)
- `budget_daily` (decimal)
- `objective` (string) – awareness, performance, retargeting, etc.
- `status` (string) – active, paused, completed

### Creative Table
- `creative_id` (string, PK)
- `campaign_id` (string, FK → campaign.campaign_id)
- `creative_type` (string) – banner, video, native, etc.
- `dimensions` (string, e.g., "300x250")
- `file_size_kb` (int)
- `click_url` (string)

---

## 2. Fact Tables

### Impression Fact
- `timestamp` (datetime)
- `campaign_id` (string, FK)
- `creative_id` (string, FK)
- `publisher_id` (string)
- `placement_id` (string)
- `device_type` (string) – desktop, mobile, tablet, CTV
- `geo_country` (string)
- `geo_region` (string)
- `geo_city` (string)
- `auction_type` (string) – open, PMP, direct
- `bid_request_id` (string)
- `bid_price` (decimal, CPM)
- `win_price` (decimal, CPM)
- `impression_outcome` (string) – won, lost

### Click Fact
- `click_id` (string, PK)
- `impression_id` (string, FK)
- `timestamp` (datetime)
- `campaign_id` (string, FK)
- `creative_id` (string, FK)
- `publisher_id` (string)
- `device_type` (string)
- `geo_country` (string)
- `click_cost` (decimal, if CPC billing)

### Conversion Fact
- `conversion_id` (string, PK)
- `click_id` (string, FK, nullable)
- `impression_id` (string, FK, nullable)
- `timestamp` (datetime)
- `campaign_id` (string, FK)
- `conversion_type` (string) – purchase, signup, install
- `conversion_value` (decimal)
- `attribution_model` (string) – last_click, view_through, etc.

---

## 3. Metrics to Derive

- **Delivery & Engagement**
  - impressions_served
  - clicks
  - ctr = clicks ÷ impressions
  - viewability_pct
  - video_completion_rate

- **Spend & Efficiency**
  - spend = Σ(win_price × impressions) / 1000
  - ecpm = spend ÷ (impressions / 1000)
  - cpc = spend ÷ clicks
  - cpa = spend ÷ conversions
  - roas = conversion_value ÷ spend

- **Pacing & Budget**
  - daily_spend vs. daily_budget
  - pct_budget_spent_to_date
  - forecasted_spend

- **Attribution**
  - conversions_by_window (1d, 7d, 30d)
  - impressions_vs_click_contribution

---

## 4. Optional Enrichment

- Audience breakdown: age, gender, interests  
- Fraud/IVT: invalid_traffic_pct  
- Brand safety: domain_category, blocked_impressions  
- Engagement depth: dwell_time, bounce_rate  

### App Structure:
- Multi-page Streamlit app with navigation sidebar
- Page 1:
- Page 2:

### Internactive Features:
- Data range filter (quarter, year selection)
- Line item selection for detailed view
- Trends over time

### Chart Types:
- Line charts for trends over time
- Spend charts
- Bar charts for conversion types

### File Structure:
|-- app.py (main Streamlit application)
|-- data_generator.py (fake data generation)
|-- utils.py (helper functions for calculations)
|-- requirements.txt
|-- README.md