

import asyncio
import httpx
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

async def test_fmp_api():
    """Test the Financial Modeling Prep API endpoint"""
    
    # Get API key from environment
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        print("❌ FMP_API_KEY not found in .env file")
        return
    
    # API endpoint
    endpoint = "https://financialmodelingprep.com/stable/income-statement"
    
    # Parameters
    params = {
        "symbol": "META",
        "apikey": api_key,
        "limit": 5  # Get last 5 years of data
    }
    
    print(f"🔍 Testing Financial Modeling Prep API...")
    print(f"📊 Symbol: META")
    print(f"🔗 Endpoint: {endpoint}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params)
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ API call successful!")
                print(f"📈 Retrieved {len(data)} income statements")
                
                # Display first income statement (most recent)
                if data:
                    latest = data[0]
                    print(f"\n📊 Latest Income Statement ({latest.get('date', 'N/A')}):")
                    print(f"  Revenue: ${latest.get('revenue', 0):,}")
                    print(f"  Net Income: ${latest.get('netIncome', 0):,}")
                    print(f"  Gross Profit: ${latest.get('grossProfit', 0):,}")
                    print(f"  Operating Income: ${latest.get('operatingIncome', 0):,}")
                    
                    # Show all available fields
                    print(f"\n🔍 Available fields:")
                    for key, value in latest.items():
                        if isinstance(value, (int, float)) and value != 0:
                            print(f"  {key}: {value:,}")
                
                # Save raw data to file for inspection
                with open("meta_income_statements.json", "w") as f:
                    json.dump(data, f, indent=2)
                print(f"\n💾 Raw data saved to: meta_income_statements.json")
                
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")

async def test_different_symbols():
    """Test API with different stock symbols"""
    
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        return
        
    symbols = ["AAPL", "GOOGL", "TSLA", "MSFT"]
    endpoint = "https://financialmodelingprep.com/stable/income-statement"
    
    print(f"\n🔍 Testing multiple symbols...")
    
    for symbol in symbols:
        try:
            params = {
                "symbol": symbol,
                "apikey": api_key,
                "limit": 1  # Just get latest
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        latest = data[0]
                        print(f"✅ {symbol}: Revenue ${latest.get('revenue', 0):,} ({latest.get('date', 'N/A')})")
                    else:
                        print(f"⚠️  {symbol}: No data available")
                else:
                    print(f"❌ {symbol}: API error {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")

async def main():
    """Main test function"""
    print("🚀 Financial Modeling Prep API Test")
    print("=" * 50)
    
    # Test META income statements
    await test_fmp_api()
    
    # Test multiple symbols
    await test_different_symbols()
    
    print("\n✅ API testing completed!")

if __name__ == "__main__":
    asyncio.run(main())