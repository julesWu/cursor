import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta, date
import uuid
import random

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

class CampaignDataGenerator:
    def __init__(self):
        self.fake = fake
        self.start_date = datetime(2020, 1, 1)
        self.end_date = datetime(2024, 12, 31)
        
        # Industry categories for advertisers
        self.industries = [
            'E-commerce', 'Finance', 'Healthcare', 'Technology', 'Automotive',
            'Travel', 'Food & Beverage', 'Fashion', 'Gaming', 'Education'
        ]
        
        # Campaign objectives
        self.objectives = ['awareness', 'performance', 'retargeting', 'brand_building', 'lead_generation']
        
        # Creative types and dimensions
        self.creative_types = ['banner', 'video', 'native', 'rich_media', 'audio']
        self.dimensions = ['300x250', '728x90', '160x600', '320x50', '970x250', '300x600', '1920x1080']
        
        # Device types and geo data
        self.device_types = ['desktop', 'mobile', 'tablet', 'CTV']
        self.countries = ['US', 'CA', 'UK', 'DE', 'FR', 'AU', 'JP', 'BR']
        self.auction_types = ['open', 'PMP', 'direct']
        self.conversion_types = ['purchase', 'signup', 'install', 'lead', 'download']
        self.attribution_models = ['last_click', 'view_through', 'first_click', 'linear']
        
        # Generate base entities first
        self.advertisers = self.generate_advertisers()
        self.campaigns = self.generate_campaigns()
        self.creatives = self.generate_creatives()
        
    def generate_advertisers(self, num_advertisers=20):
        """Generate advertiser dimension table"""
        advertisers = []
        for i in range(num_advertisers):
            advertisers.append({
                'advertiser_id': f'ADV_{i+1:04d}',
                'advertiser_name': self.fake.company(),
                'industry': random.choice(self.industries),
                'account_manager': self.fake.name()
            })
        return pd.DataFrame(advertisers)
    
    def generate_campaigns(self, num_campaigns=50):
        """Generate campaign dimension table"""
        campaigns = []
        for i in range(num_campaigns):
            advertiser = self.advertisers.sample(1).iloc[0]
            
            # Generate campaign dates within our 5-year window
            start_date = self.fake.date_between(start_date=self.start_date, end_date=datetime(2024, 6, 30))
            end_date = self.fake.date_between(start_date=start_date, end_date=self.end_date)
            
            # Calculate budget based on campaign duration
            duration_days = (end_date - start_date).days
            daily_budget = random.uniform(100, 10000)
            total_budget = daily_budget * duration_days * random.uniform(0.8, 1.2)  # Add some variance
            
            campaigns.append({
                'campaign_id': f'CAMP_{i+1:06d}',
                'campaign_name': f"{advertiser['advertiser_name']} - {self.fake.catch_phrase()}",
                'advertiser_id': advertiser['advertiser_id'],
                'start_date': start_date,
                'end_date': end_date,
                'budget_total': round(total_budget, 2),
                'budget_daily': round(daily_budget, 2),
                'objective': random.choice(self.objectives),
                'status': random.choices(['active', 'paused', 'completed'], weights=[0.3, 0.1, 0.6])[0]
            })
        return pd.DataFrame(campaigns)
    
    def generate_creatives(self, creatives_per_campaign=3):
        """Generate creative dimension table"""
        creatives = []
        for _, campaign in self.campaigns.iterrows():
            num_creatives = random.randint(1, creatives_per_campaign)
            for j in range(num_creatives):
                creative_type = random.choice(self.creative_types)
                dimension = random.choice(self.dimensions) if creative_type != 'video' else '1920x1080'
                
                creatives.append({
                    'creative_id': f'CREAT_{len(creatives)+1:08d}',
                    'campaign_id': campaign['campaign_id'],
                    'creative_type': creative_type,
                    'dimensions': dimension,
                    'file_size_kb': random.randint(50, 2000),
                    'click_url': self.fake.url()
                })
        return pd.DataFrame(creatives)
    
    def generate_impressions(self, num_impressions=1000000):
        """Generate impression fact table"""
        impressions = []
        publishers = [f'PUB_{i:04d}' for i in range(1, 26)]  # 25 publishers
        placements = [f'PLACE_{i:06d}' for i in range(1, 101)]  # 100 placements
        
        for i in range(num_impressions):
            # Select random campaign and creative
            campaign = self.campaigns.sample(1).iloc[0]
            campaign_creatives = self.creatives[self.creatives['campaign_id'] == campaign['campaign_id']]
            if len(campaign_creatives) == 0:
                continue
                
            creative = campaign_creatives.sample(1).iloc[0]
            
            # Generate timestamp within campaign date range
            campaign_end = datetime.combine(campaign['end_date'], datetime.min.time()) if isinstance(campaign['end_date'], date) else campaign['end_date']
            max_end_date = min(campaign_end, self.end_date)
            
            campaign_start = datetime.combine(campaign['start_date'], datetime.min.time()) if isinstance(campaign['start_date'], date) else campaign['start_date']
            
            timestamp = self.fake.date_time_between(
                start_date=campaign_start,
                end_date=max_end_date
            )
            
            # Generate bid and win prices with realistic patterns
            bid_price = random.uniform(0.50, 15.00)  # CPM
            win_price = bid_price * random.uniform(0.7, 0.95)  # Usually slightly lower than bid
            
            country = random.choice(self.countries)
            region = f"{country}_Region_{random.randint(1, 10)}"
            city = f"{country}_City_{random.randint(1, 50)}"
            
            impressions.append({
                'timestamp': timestamp,
                'campaign_id': campaign['campaign_id'],
                'creative_id': creative['creative_id'],
                'publisher_id': random.choice(publishers),
                'placement_id': random.choice(placements),
                'device_type': random.choice(self.device_types),
                'geo_country': country,
                'geo_region': region,
                'geo_city': city,
                'auction_type': random.choice(self.auction_types),
                'bid_request_id': str(uuid.uuid4()),
                'bid_price': round(bid_price, 2),
                'win_price': round(win_price, 2),
                'impression_outcome': random.choices(['won', 'lost'], weights=[0.25, 0.75])[0]  # 25% win rate
            })
            
        return pd.DataFrame(impressions)
    
    def generate_clicks(self, impressions_df):
        """Generate click fact table based on impressions"""
        # Filter for won impressions only
        won_impressions = impressions_df[impressions_df['impression_outcome'] == 'won'].copy()
        
        # Generate clicks with realistic CTR (0.1% to 3%)
        num_clicks = int(len(won_impressions) * random.uniform(0.001, 0.03))
        clicked_impressions = won_impressions.sample(n=min(num_clicks, len(won_impressions)))
        
        clicks = []
        for _, impression in clicked_impressions.iterrows():
            # Click happens shortly after impression
            click_time = impression['timestamp'] + timedelta(seconds=random.randint(1, 3600))
            
            clicks.append({
                'click_id': str(uuid.uuid4()),
                'impression_id': f"IMP_{len(clicks)+1:010d}",  # Simplified impression ID
                'timestamp': click_time,
                'campaign_id': impression['campaign_id'],
                'creative_id': impression['creative_id'],
                'publisher_id': impression['publisher_id'],
                'device_type': impression['device_type'],
                'geo_country': impression['geo_country'],
                'click_cost': round(impression['win_price'] / 1000, 4)  # Convert CPM to per-click cost
            })
        
        return pd.DataFrame(clicks)
    
    def generate_conversions(self, clicks_df, impressions_df):
        """Generate conversion fact table"""
        conversions = []
        
        # Click-through conversions (higher conversion rate)
        click_conversions = int(len(clicks_df) * random.uniform(0.02, 0.15))  # 2-15% conversion rate
        converting_clicks = clicks_df.sample(n=min(click_conversions, len(clicks_df)))
        
        for _, click in converting_clicks.iterrows():
            # Conversion happens within 7 days of click
            conversion_time = click['timestamp'] + timedelta(hours=random.randint(1, 168))
            
            # Generate conversion value based on campaign objective
            if random.random() < 0.7:  # 70% have monetary value
                conversion_value = random.uniform(10, 500)
            else:
                conversion_value = 0  # Non-monetary conversions (signups, installs)
            
            conversions.append({
                'conversion_id': str(uuid.uuid4()),
                'click_id': click['click_id'],
                'impression_id': click['impression_id'],
                'timestamp': conversion_time,
                'campaign_id': click['campaign_id'],
                'conversion_type': random.choice(self.conversion_types),
                'conversion_value': round(conversion_value, 2),
                'attribution_model': random.choice(self.attribution_models)
            })
        
        # View-through conversions (lower conversion rate)
        won_impressions = impressions_df[impressions_df['impression_outcome'] == 'won']
        view_conversions = int(len(won_impressions) * random.uniform(0.001, 0.005))  # 0.1-0.5% view-through rate
        converting_impressions = won_impressions.sample(n=min(view_conversions, len(won_impressions)))
        
        for _, impression in converting_impressions.iterrows():
            conversion_time = impression['timestamp'] + timedelta(hours=random.randint(1, 720))  # Within 30 days
            
            conversion_value = random.uniform(5, 200) if random.random() < 0.5 else 0
            
            conversions.append({
                'conversion_id': str(uuid.uuid4()),
                'click_id': None,
                'impression_id': f"IMP_{len(conversions)+1:010d}",
                'timestamp': conversion_time,
                'campaign_id': impression['campaign_id'],
                'conversion_type': random.choice(self.conversion_types),
                'conversion_value': round(conversion_value, 2),
                'attribution_model': 'view_through'
            })
        
        return pd.DataFrame(conversions)
    
    def generate_all_data(self):
        """Generate complete dataset"""
        print("Generating impressions...")
        impressions = self.generate_impressions(50000)  # 50K impressions for fast loading
        
        print("Generating clicks...")
        clicks = self.generate_clicks(impressions)
        
        print("Generating conversions...")
        conversions = self.generate_conversions(clicks, impressions)
        
        return {
            'advertisers': self.advertisers,
            'campaigns': self.campaigns,
            'creatives': self.creatives,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions
        }

def generate_campaign_data():
    """Main function to generate all campaign data"""
    generator = CampaignDataGenerator()
    return generator.generate_all_data()

if __name__ == "__main__":
    # Test the data generation
    data = generate_campaign_data()
    
    print("\nData Summary:")
    for table_name, df in data.items():
        print(f"{table_name}: {len(df)} records")
    
    print("\nSample data preview:")
    print("\nAdvertisers:")
    print(data['advertisers'].head())
    
    print("\nCampaigns:")
    print(data['campaigns'].head())
    
    print("\nImpressions:")
    print(data['impressions'].head())
