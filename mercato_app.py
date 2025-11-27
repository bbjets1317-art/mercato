"""
Mercato - The Market Made Simple
All bugs fixed + features added
"""

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import BytesIO
import requests
from bs4 import BeautifulSoup

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except:
    SUPABASE_AVAILABLE = False

# ============ SUPABASE SETUP ============
def init_supabase():
    if not SUPABASE_AVAILABLE:
        return None
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except:
        pass
    return None

supabase = init_supabase()

# ============ AUTH FUNCTIONS ============
def sign_up(email, password):
    if not supabase:
        return {"error": "Database not configured"}
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return response
    except Exception as e:
        return {"error": str(e)}

def sign_in(email, password):
    if not supabase:
        return {"error": "Database not configured"}
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response
    except Exception as e:
        return {"error": str(e)}

def sign_out():
    if supabase:
        try:
            supabase.auth.sign_out()
        except:
            pass
    st.session_state.user = None
    st.session_state.authenticated = False

def get_user():
    if not supabase:
        return None
    try:
        user = supabase.auth.get_user()
        if user and hasattr(user, 'user') and user.user:
            return user.user
        return None
    except:
        return None

# ============ DATABASE FUNCTIONS ============
def save_portfolio_to_db(user_id, portfolio, shares_dict):
    if not supabase or not user_id:
        return False
    try:
        supabase.table("portfolios").delete().eq("user_id", str(user_id)).execute()
        for ticker in portfolio:
            data = {
                "user_id": str(user_id),
                "ticker": ticker.upper(),
                "shares": float(shares_dict.get(ticker, 1.0))
            }
            supabase.table("portfolios").insert(data).execute()
        return True
    except:
        return False

def load_portfolio_from_db(user_id):
    if not supabase:
        return [], {}
    try:
        response = supabase.table("portfolios").select("*").eq("user_id", str(user_id)).execute()
        if response.data:
            portfolio = [item['ticker'] for item in response.data]
            shares = {item['ticker']: item['shares'] for item in response.data}
            return portfolio, shares
        return [], {}
    except:
        return [], {}

def save_score_to_history(user_id, ticker, score_data):
    if not supabase or not user_id:
        return False
    try:
        data = {
            "user_id": str(user_id),
            "ticker": ticker.upper(),
            "score": float(score_data['final_score']),
            "financial_health": float(score_data['financial_health']),
            "profitability": float(score_data['profitability']),
            "growth": float(score_data['growth']),
            "momentum": float(score_data['momentum']),
            "stability": float(score_data['stability']),
            "price": float(score_data['price'])
        }
        supabase.table("score_history").insert(data).execute()
        return True
    except:
        return False

def get_score_change(user_id, ticker):
    if not supabase or not user_id:
        return None
    try:
        response = supabase.table("score_history").select("score").eq(
            "user_id", str(user_id)
        ).eq("ticker", ticker).order("calculated_at", desc=True).limit(2).execute()
        
        if response.data and len(response.data) >= 2:
            return float(response.data[0]['score']) - float(response.data[1]['score'])
        return None
    except:
        return None

# ============ S&P 500 SECTOR STOCKS & AUTOCOMPLETE ============
@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_sp500_stocks():
    """Fetch S&P 500 stocks from Wikipedia, use hardcoded backup if fails"""
    try:
        # Try to fetch from Wikipedia
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'id': 'constituents'})
            
            if table:
                df = pd.read_html(str(table))[0]
                
                # Group by sector
                sector_stocks = {}
                for sector in df['GICS Sector'].unique():
                    tickers = df[df['GICS Sector'] == sector]['Symbol'].tolist()
                    # Clean tickers (replace dots with dashes for Yahoo Finance)
                    tickers = [t.replace('.', '-') if '.' in t else t for t in tickers]
                    sector_stocks[sector] = tickers
                
                # Map Wikipedia sector names to our display names
                sector_name_map = {
                    'Information Technology': 'Technology',
                    'Financials': 'Financial Services',
                    'Health Care': 'Healthcare',
                    'Consumer Discretionary': 'Consumer Cyclical',
                    'Consumer Staples': 'Consumer Defensive',
                    'Materials': 'Basic Materials'
                }
                
                # Remap sector names
                mapped_sectors = {}
                for sector, tickers in sector_stocks.items():
                    display_name = sector_name_map.get(sector, sector)
                    mapped_sectors[display_name] = tickers
                
                return mapped_sectors
    except Exception as e:
        st.warning(f"Could not fetch live S&P 500 data from Wikipedia, using backup list")
    
    # Return hardcoded backup if fetch fails
    return {
        'Technology': ['AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'CSCO', 'ADBE', 'CRM', 'INTC', 'AMD', 'QCOM', 'TXN', 'IBM', 'NOW', 'INTU', 'AMAT', 'MU', 'LRCX', 'ADI', 'KLAC', 'SNPS', 'CDNS', 'MCHP', 'FTNT', 'ANSS', 'ADSK', 'ROP', 'KEYS', 'HPQ', 'NTAP', 'MPWR', 'ZBRA', 'ENPH', 'TYL', 'GDDY', 'AKAM', 'SWKS', 'JNPR', 'FFIV', 'GEN', 'TRMB', 'TER', 'SMCI', 'GLW', 'HPE', 'STX', 'WDC', 'DELL', 'PANW', 'CRWD', 'ZS', 'DDOG', 'NET', 'SNOW', 'MDB', 'WDAY', 'TEAM', 'HUBS', 'ZI', 'BILL'],
        'Financial Services': ['BRK.B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'AXP', 'C', 'SPGI', 'BLK', 'SCHW', 'CB', 'MMC', 'PGR', 'AON', 'USB', 'TFC', 'PNC', 'AIG', 'MET', 'PRU', 'AFL', 'ALL', 'TRV', 'AJG', 'HIG', 'CINF', 'WTW', 'MCO', 'CME', 'ICE', 'MSCI', 'COF', 'DFS', 'SYF', 'FITB', 'HBAN', 'RF', 'KEY', 'CFG', 'NTRS', 'STT', 'BK', 'BEN', 'IVZ', 'TROW', 'L', 'GL', 'RJF', 'CBOE', 'FDS', 'MKTX', 'EG', 'AMP', 'LNC', 'WRB', 'RGA', 'FNF'],
        'Healthcare': ['UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY', 'AMGN', 'GILD', 'CVS', 'CI', 'ISRG', 'VRTX', 'REGN', 'HUM', 'BSX', 'MDT', 'ELV', 'ZTS', 'SYK', 'BDX', 'MCK', 'HCA', 'COR', 'A', 'IQV', 'RMD', 'DXCM', 'EW', 'IDXX', 'MTD', 'ALGN', 'BAX', 'CRL', 'CAH', 'VTRS', 'WAT', 'DGX', 'LH', 'HOLX', 'TECH', 'TFX', 'PKI', 'BIO', 'STE', 'PODD', 'INCY', 'EXAS', 'MRNA', 'BIIB', 'ILMN', 'ZBH', 'CTLT', 'WST', 'COO', 'HSIC', 'DVA'],
        'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TGT', 'TJX', 'CMG', 'BKNG', 'GM', 'F', 'MAR', 'ORLY', 'AZO', 'YUM', 'ROST', 'DHI', 'LEN', 'HLT', 'EBAY', 'APTV', 'DG', 'POOL', 'BBY', 'ULTA', 'DRI', 'GPC', 'LVS', 'MGM', 'WYNN', 'CCL', 'RCL', 'NCLH', 'EXPE', 'ABNB', 'UBER', 'LYFT', 'DASH', 'ETSY', 'W', 'CHWY', 'CVNA', 'KMX', 'AN', 'PAG', 'AAP', 'DKS', 'FL', 'FIVE', 'BURL', 'LULU', 'GPS', 'RL', 'PVH', 'VFC', 'TPR', 'CPRI'],
        'Consumer Defensive': ['WMT', 'PG', 'KO', 'PEP', 'COST', 'PM', 'MO', 'CL', 'KMB', 'GIS', 'MDLZ', 'ADM', 'KR', 'SYY', 'STZ', 'HSY', 'K', 'CHD', 'CLX', 'CAG', 'TSN', 'CPB', 'HRL', 'SJM', 'MKC', 'LW', 'TAP', 'KDP', 'BG', 'MNST', 'KHC', 'KVUE', 'EL', 'POST', 'FLO', 'LANC', 'COKE', 'DPS', 'FIZZ', 'CELH'],
        'Industrials': ['CAT', 'GE', 'UPS', 'HON', 'BA', 'LMT', 'RTX', 'UNP', 'DE', 'MMM', 'GD', 'NOC', 'FDX', 'WM', 'CSX', 'NSC', 'EMR', 'ETN', 'ITW', 'PH', 'CMI', 'TT', 'ROK', 'CARR', 'OTIS', 'JCI', 'PCAR', 'IR', 'FAST', 'DOV', 'AME', 'VRSK', 'IEX', 'XYL', 'LDOS', 'SNA', 'GNRC', 'PWR', 'J', 'EXPD', 'CHRW', 'JBHT', 'ODFL', 'TXT', 'HWM', 'ALLE', 'AOS', 'FTV', 'BLDR', 'SWK', 'MAS', 'FBHS', 'WHR', 'NDSN', 'SSD', 'ITT', 'FLS', 'AIT', 'CR', 'GWW'],
        'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HES', 'KMI', 'WMB', 'PXD', 'HAL', 'DVN', 'BKR', 'FANG', 'MRO', 'APA', 'CTRA', 'EQT', 'OKE', 'TRGP', 'LNG', 'CHK', 'AR', 'PR', 'RRC', 'NOV', 'FTI'],
        'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'PEG', 'XEL', 'ED', 'WEC', 'ES', 'AWK', 'DTE', 'PPL', 'FE', 'EIX', 'ETR', 'AEE', 'CMS', 'NI', 'LNT', 'EVRG', 'PNW', 'NRG', 'VST', 'CNP', 'ATO', 'OGE', 'SWX'],
        'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'SPG', 'WELL', 'DLR', 'O', 'AVB', 'VICI', 'EQR', 'SBAC', 'VTR', 'INVH', 'ARE', 'MAA', 'KIM', 'DOC', 'HST', 'UDR', 'REG', 'BXP', 'CPT', 'FRT', 'ESS', 'VNO', 'AIV', 'EGP', 'SLG'],
        'Basic Materials': ['LIN', 'APD', 'ECL', 'SHW', 'NEM', 'FCX', 'NUE', 'DOW', 'DD', 'ALB', 'CTVA', 'PPG', 'VMC', 'MLM', 'BALL', 'AVY', 'IP', 'PKG', 'AMCR', 'CE', 'CF', 'MOS', 'EMN', 'FMC', 'IFF', 'SEE', 'WRK', 'AA', 'X', 'STLD'],
        'Communication Services': ['META', 'GOOGL', 'GOOG', 'NFLX', 'DIS', 'CMCSA', 'T', 'TMUS', 'VZ', 'EA', 'CHTR', 'TTWO', 'OMC', 'IPG', 'NWSA', 'NWS', 'FOXA', 'FOX', 'PARA', 'WBD', 'LYV', 'MTCH', 'LUMN', 'NYT', 'DISH', 'ATVI', 'ZM', 'PINS', 'SNAP', 'RBLX']
    }

# Load S&P 500 stocks (will fetch from Wikipedia or use backup)
SP500_SECTOR_STOCKS = fetch_sp500_stocks()

# Popular stocks for search autocomplete
POPULAR_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'V', 'JNJ',
    'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'CRM', 'NFLX', 'CSCO', 'INTC', 'AMD',
    'SPY', 'QQQ', 'VOO', 'VTI', 'IWM', 'EEM', 'GLD', 'TLT', 'AGG', 'VNQ', 'XLF', 'XLE', 'XLK', 'XLV']

# ============ COMPANY TICKER MAP ============
COMPANY_TICKER_MAP = {
    'APPLE': 'AAPL', 'MICROSOFT': 'MSFT', 'GOOGLE': 'GOOGL', 'ALPHABET': 'GOOGL',
    'AMAZON': 'AMZN', 'TESLA': 'TSLA', 'META': 'META', 'FACEBOOK': 'META',
    'NVIDIA': 'NVDA', 'NETFLIX': 'NFLX', 'DISNEY': 'DIS', 'WALMART': 'WMT',
    'VISA': 'V', 'MASTERCARD': 'MA', 'JPMORGAN': 'JPM', 'BANK OF AMERICA': 'BAC',
    'COCA COLA': 'KO', 'PEPSI': 'PEP', 'NIKE': 'NKE', 'STARBUCKS': 'SBUX',
    'BOEING': 'BA', 'INTEL': 'INTC', 'AMD': 'AMD', 'ORACLE': 'ORCL',
    'SALESFORCE': 'CRM', 'ADOBE': 'ADBE', 'UBER': 'UBER', 'AIRBNB': 'ABNB',
    'SPOTIFY': 'SPOT', 'SNAP': 'SNAP', 'ZOOM': 'ZM', 'SHOPIFY': 'SHOP',
    'COINBASE': 'COIN', 'PALANTIR': 'PLTR', 'RIVIAN': 'RIVN', 'TARGET': 'TGT'
}

# Load logo
try:
    with open('mercato_logo.png', 'rb') as f:
        LOGO_BASE64 = base64.b64encode(f.read()).decode()
except:
    LOGO_BASE64 = None

# Page config
st.set_page_config(page_title="Mercato", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# ============ CSS WITH BETTER VISIBILITY ============
st.markdown("""
    <style>
    :root {
        --beige: #F9F8F6;
        --blue: #343967;
    }
    
    * { font-family: Georgia, serif !important; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
    
    .main {
        background: #ffffff;
        padding: 10px 0;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1100px !important;
    }
    
    .element-container { margin-bottom: 0.5rem !important; }
    .row-widget { margin-bottom: 0.5rem !important; }
    
    .welcome-title {
        font-size: 48px;
        font-weight: 700;
        color: #343967;
        margin: 10px 0;
        text-align: center;
    }
    
    .welcome-tagline {
        font-size: 20px;
        color: #343967;
        margin: 10px 0;
        text-align: center;
        font-style: italic;
    }
    
    .health-score-container {
        background: #343967;
        padding: 30px 25px;
        border-radius: 16px;
        text-align: center;
        margin: 15px auto;
        max-width: 500px;
    }
    
    .health-score-number {
        color: #e6e0d5;
        font-size: 80px;
        font-weight: 200;
        margin: 10px 0;
    }
    
    .health-score-subtext {
        color: #d0c9bc;
        font-size: 16px;
    }
    
    .insight-card {
        background: #343967;
        padding: 12px 18px;
        border-radius: 10px;
        margin: 8px 0;
    }
    
    .insight-text {
        color: #f5f0e8;
        font-size: 14px;
        line-height: 1.4;
    }
    
    .stock-card {
        background: #343967;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }
    
    .stock-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    
    .company-logo {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        object-fit: contain;
        background: white;
        padding: 5px;
        margin-right: 12px;
    }
    
    .company-name {
        font-size: 18px;
        font-weight: 600;
        color: #e6e0d5;
        margin-bottom: 2px;
    }
    
    .stock-ticker {
        font-size: 12px;
        color: #d0c9bc;
        letter-spacing: 1px;
    }
    
    .stock-score {
        font-size: 42px;
        font-weight: 200;
        color: #e6e0d5;
    }
    
    .stock-price {
        font-size: 16px;
        color: #e6e0d5;
        margin: 6px 0;
    }
    
    .price-change-positive { color: #10b981; font-weight: 600; }
    .price-change-negative { color: #ef4444; font-weight: 600; }
    
    /* FIXED: Better visibility for subscores */
    .subscore-container { margin: 10px 0; }
    .subscore-label { 
        color: #e6e0d5; 
        font-size: 11px; 
        margin-bottom: 6px; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .subscore-bar { 
        background: rgba(230, 224, 213, 0.3); 
        height: 8px; 
        border-radius: 4px; 
        overflow: hidden; 
    }
    .subscore-fill { 
        background: #e6e0d5; 
        height: 100%; 
        border-radius: 4px; 
    }
    
    .stButton > button {
        background: #343967;
        color: white;
        padding: 10px 15px;
        font-size: 13px;
        border-radius: 10px;
        border: none;
        width: 100%;
        white-space: nowrap;
        min-width: fit-content;
    }
    
    .stButton > button:hover {
        background: #2a2f52;
        transform: translateY(-1px);
    }
    
    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: #343967;
        margin: 15px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #343967;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #d9d0c1;
        padding: 10px;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #d9d0c1;
        padding: 10px;
    }
    
    /* Logo header */
    .logo-header {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }
    
    .logo-header img {
        width: 50px;
        height: 50px;
        margin-right: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SECTOR BENCHMARKS FOR INDUSTRY ADJUSTMENT ============
SECTOR_BENCHMARKS = {
    'Technology': {'profit_margin': 0.20, 'operating_margin': 0.25, 'growth': 0.15},
    'Financial Services': {'profit_margin': 0.20, 'operating_margin': 0.30, 'growth': 0.08},
    'Healthcare': {'profit_margin': 0.12, 'operating_margin': 0.18, 'growth': 0.10},
    'Consumer Cyclical': {'profit_margin': 0.08, 'operating_margin': 0.10, 'growth': 0.08},
    'Consumer Defensive': {'profit_margin': 0.05, 'operating_margin': 0.08, 'growth': 0.05},
    'Industrials': {'profit_margin': 0.08, 'operating_margin': 0.12, 'growth': 0.06},
    'Energy': {'profit_margin': 0.10, 'operating_margin': 0.15, 'growth': 0.05},
    'Utilities': {'profit_margin': 0.10, 'operating_margin': 0.15, 'growth': 0.03},
    'Real Estate': {'profit_margin': 0.15, 'operating_margin': 0.20, 'growth': 0.05},
    'Basic Materials': {'profit_margin': 0.10, 'operating_margin': 0.15, 'growth': 0.05},
    'Communication Services': {'profit_margin': 0.15, 'operating_margin': 0.20, 'growth': 0.10},
}

# Default benchmark for unknown sectors
DEFAULT_BENCHMARK = {'profit_margin': 0.12, 'operating_margin': 0.15, 'growth': 0.08}

def get_sector_benchmark(sector):
    """Get benchmark for a sector, or return default"""
    return SECTOR_BENCHMARKS.get(sector, DEFAULT_BENCHMARK)

# ============ STOCK SCORING FUNCTIONS ============
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")
        
        if hist.empty:
            return None
        
        company_name = info.get('longName', info.get('shortName', ticker))
        
        # Detect if this is an ETF
        quote_type = info.get('quoteType', '')
        is_etf = quote_type == 'ETF' or 'fund' in company_name.lower() or 'etf' in company_name.lower()
        
        # Get logo URL
        logo_url = None
        website = info.get('website', '')
        if website:
            domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            logo_url = f"https://logo.clearbit.com/{domain}"
        
        return {
            'ticker': ticker,
            'company_name': company_name,
            'logo_url': logo_url,
            'sector': info.get('sector', 'ETF' if is_etf else 'Unknown'),
            'is_etf': is_etf,
            'price': hist['Close'].iloc[-1],
            'prev_close': hist['Close'].iloc[-2] if len(hist) >= 2 else hist['Close'].iloc[-1],
            'total_debt': info.get('totalDebt', 0) if not is_etf else 0,
            'total_cash': info.get('totalCash', 0) if not is_etf else 0,
            'free_cash_flow': info.get('freeCashflow', 0) if not is_etf else 0,
            'market_cap': info.get('marketCap', info.get('totalAssets', 1)),
            'profit_margin': info.get('profitMargins', 0) if not is_etf else 0,
            'operating_margin': info.get('operatingMargins', 0) if not is_etf else 0,
            'roe': info.get('returnOnEquity', 0) if not is_etf else 0,
            'revenue_growth': info.get('revenueGrowth', 0) if not is_etf else 0,
            'earnings_growth': info.get('earningsGrowth', 0) if not is_etf else 0,
            'beta': info.get('beta', 1),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'hist': hist
        }
    except:
        return None

def calculate_financial_health(data):
    scores = []
    weights = []
    
    # Debt Score (30% weight)
    debt_ratio = data['total_debt'] / data['market_cap'] if data['market_cap'] > 0 else 1
    if debt_ratio < 0.2:
        debt_score = 1.0
    elif debt_ratio < 0.5:
        debt_score = 0.85
    elif debt_ratio < 0.8:
        debt_score = 0.65
    else:
        debt_score = 0.4
    scores.append(debt_score)
    weights.append(0.30)
    
    # Cash Score (30% weight)
    cash_ratio = data['total_cash'] / data['market_cap'] if data['market_cap'] > 0 else 0
    cash_score = min(1.0, cash_ratio * 5 + 0.3)
    scores.append(cash_score)
    weights.append(0.30)
    
    # FCF Score (40% weight - MORE IMPORTANT)
    fcf_ratio = data['free_cash_flow'] / data['market_cap'] if data['market_cap'] > 0 else 0
    if fcf_ratio > 0.05:
        fcf_score = 0.9
    elif fcf_ratio > 0:
        fcf_score = 0.7
    else:
        fcf_score = 0.4
    scores.append(fcf_score)
    weights.append(0.40)
    
    # Weighted average
    weighted_score = sum(s * w for s, w in zip(scores, weights))
    return weighted_score * 20

def calculate_profitability(data):
    scores = []
    
    # Get sector benchmark
    benchmark = get_sector_benchmark(data.get('sector', 'Unknown'))
    
    # Profit Margin Score (sector-adjusted)
    pm = data['profit_margin']
    pm_benchmark = benchmark['profit_margin']
    
    # Compare to sector benchmark
    if pm > pm_benchmark * 2:  # 2x sector average = excellent
        pm_score = 1.0
    elif pm > pm_benchmark * 1.5:  # 1.5x sector average = great
        pm_score = 0.85
    elif pm > pm_benchmark:  # Above sector average = good
        pm_score = 0.70
    elif pm > pm_benchmark * 0.7:  # Slightly below average
        pm_score = 0.50
    elif pm > 0:  # Profitable but weak
        pm_score = 0.35
    else:  # Unprofitable
        pm_score = 0.20
    scores.append(pm_score)
    
    # Operating Margin Score (sector-adjusted)
    om = data['operating_margin']
    om_benchmark = benchmark['operating_margin']
    
    if om > om_benchmark * 2:
        om_score = 1.0
    elif om > om_benchmark * 1.5:
        om_score = 0.85
    elif om > om_benchmark:
        om_score = 0.70
    elif om > om_benchmark * 0.7:
        om_score = 0.50
    elif om > 0:
        om_score = 0.35
    else:
        om_score = 0.20
    scores.append(om_score)
    
    # ROE Score (universal - not sector-specific)
    roe = data['roe']
    if roe > 0.25:
        roe_score = 1.0
    elif roe > 0.18:
        roe_score = 0.75
    elif roe > 0.12:
        roe_score = 0.55
    elif roe > 0.06:
        roe_score = 0.35
    else:
        roe_score = max(0.15, roe * 2.5) if roe > 0 else 0.15
    scores.append(roe_score)
    
    return np.mean(scores) * 20

def calculate_growth(data):
    scores = []
    
    # Revenue Growth
    rev = data['revenue_growth']
    if rev > 0.2:
        rev_score = 1.0
    elif rev > 0.1:
        rev_score = 0.8
    elif rev > 0.05:
        rev_score = 0.65
    elif rev > 0:
        rev_score = 0.5
    else:
        rev_score = 0.35
    scores.append(rev_score)
    
    # Earnings Growth
    earn = data['earnings_growth']
    if earn > 0.2:
        earn_score = 1.0
    elif earn > 0.1:
        earn_score = 0.8
    elif earn > 0.05:
        earn_score = 0.65
    elif earn > 0:
        earn_score = 0.5
    else:
        earn_score = 0.35
    scores.append(earn_score)
    
    # FIXED: Removed hardcoded 0.65
    # Add market cap size adjustment
    market_cap = data['market_cap']
    if market_cap > 200_000_000_000:  # $200B+ mega cap
        size_bonus = 0.15  # Bonus for maintaining growth at huge size
    elif market_cap > 10_000_000_000:  # $10B+ large cap
        size_bonus = 0.05
    elif market_cap < 2_000_000_000:  # <$2B small cap
        size_penalty = -0.1  # Penalty for small cap (easier to grow)
        size_bonus = size_penalty
    else:
        size_bonus = 0
    
    base_score = np.mean(scores)
    adjusted_score = min(1.0, max(0.2, base_score + size_bonus))
    
    return adjusted_score * 20

def calculate_momentum(data):
    try:
        hist = data['hist']
        if hist is None or hist.empty:
            return 12.0
        
        scores = []
        spy = yf.Ticker('SPY')
        spy_hist = spy.history(period='1y')
        
        if len(hist) >= 21:
            stock_1m = (hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1)
            spy_1m = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[-21] - 1)
            rel_momentum = stock_1m - spy_1m
            
            if rel_momentum > 0.08:
                score_1m = 1.0
            elif rel_momentum > 0.03:
                score_1m = 0.85
            elif rel_momentum > -0.02:
                score_1m = 0.7
            elif rel_momentum > -0.06:
                score_1m = 0.55
            else:
                score_1m = 0.4
            scores.append(score_1m)
        
        if len(hist) >= 63:
            stock_3m = (hist['Close'].iloc[-1] / hist['Close'].iloc[-63] - 1)
            spy_3m = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[-63] - 1)
            rel_momentum = stock_3m - spy_3m
            
            if rel_momentum > 0.15:
                score_3m = 1.0
            elif rel_momentum > 0.05:
                score_3m = 0.85
            elif rel_momentum > -0.05:
                score_3m = 0.7
            elif rel_momentum > -0.12:
                score_3m = 0.55
            else:
                score_3m = 0.4
            scores.append(score_3m)
        
        return np.mean(scores) * 20 if scores else 12.0
    except:
        return 12.0

def calculate_stability(data):
    scores = []
    
    beta = data['beta']
    if beta < 0.7:
        beta_score = 1.0
    elif beta < 1.0:
        beta_score = 0.85
    elif beta < 1.3:
        beta_score = 0.7
    elif beta < 1.6:
        beta_score = 0.55
    else:
        beta_score = 0.4
    scores.append(beta_score)
    
    high = data['fifty_two_week_high']
    low = data['fifty_two_week_low']
    price = data['price']
    
    if high > 0 and low > 0 and price > 0:
        vol_range = (high - low) / low
        if vol_range < 0.25:
            vol_score = 1.0
        elif vol_range < 0.4:
            vol_score = 0.85
        elif vol_range < 0.6:
            vol_score = 0.7
        elif vol_range < 0.85:
            vol_score = 0.55
        else:
            vol_score = 0.4
        scores.append(vol_score)
    
    try:
        hist = data['hist']
        if hist is not None and not hist.empty:
            rolling_max = hist['Close'].expanding().max()
            drawdown = (hist['Close'] - rolling_max) / rolling_max
            max_dd = abs(drawdown.min())
            
            if max_dd < 0.12:
                dd_score = 1.0
            elif max_dd < 0.20:
                dd_score = 0.85
            elif max_dd < 0.30:
                dd_score = 0.7
            elif max_dd < 0.45:
                dd_score = 0.55
            else:
                dd_score = 0.4
            scores.append(dd_score)
    except:
        scores.append(0.7)
    
    return np.mean(scores) * 20

def score_stock(ticker):
    data = get_stock_data(ticker)
    
    if data is None:
        return None
    
    # Check if ETF
    is_etf = data.get('is_etf', False)
    
    if is_etf:
        # ETFs don't have fundamentals, so only score momentum and stability
        financial_health = 10.0  # Neutral score
        profitability = 10.0  # Neutral score
        growth = 10.0  # Neutral score
        momentum = calculate_momentum(data)
        stability = calculate_stability(data)
    else:
        # Normal stock scoring
        financial_health = calculate_financial_health(data)
        profitability = calculate_profitability(data)
        growth = calculate_growth(data)
        momentum = calculate_momentum(data)
        stability = calculate_stability(data)
    
    final_score = financial_health + profitability + growth + momentum + stability
    price_change = ((data['price'] - data['prev_close']) / data['prev_close']) * 100
    
    return {
        'ticker': ticker,
        'company_name': data['company_name'],
        'logo_url': data['logo_url'],
        'sector': data['sector'],
        'is_etf': is_etf,
        'price': data['price'],
        'price_change': price_change,
        'financial_health': round(financial_health, 1),
        'profitability': round(profitability, 1),
        'growth': round(growth, 1),
        'momentum': round(momentum, 1),
        'stability': round(stability, 1),
        'final_score': round(final_score, 1),
        'hist': data['hist']
    }

def calculate_portfolio_score(stock_scores):
    if not stock_scores:
        return 0
    
    avg_score = np.mean([s['final_score'] for s in stock_scores])
    
    sectors = set(s['sector'] for s in stock_scores)
    num_sectors = len(sectors)
    if num_sectors <= 1:
        div_adj = 0.88
    elif num_sectors >= 5:
        div_adj = 1.0
    else:
        div_adj = 0.88 + (num_sectors - 1) * 0.03
    
    weighted_stability = np.mean([s['stability'] for s in stock_scores])
    stab_adj = 0.92 + (weighted_stability / 20) * 0.08
    
    portfolio_score = avg_score * div_adj * stab_adj
    
    return round(portfolio_score, 1)

def generate_insights(stock_scores):
    insights = []
    
    if not stock_scores:
        return insights
    
    sorted_stocks = sorted(stock_scores, key=lambda x: x['final_score'], reverse=True)
    best = sorted_stocks[0]
    worst = sorted_stocks[-1]
    
    insights.append(f"Top performer: {best['company_name']} ({best['final_score']}/100)")
    
    if len(stock_scores) > 1:
        insights.append(f"Needs attention: {worst['company_name']} ({worst['final_score']}/100)")
    
    avg_momentum = np.mean([s['momentum'] for s in stock_scores])
    if avg_momentum > 15:
        insights.append(f"Strong momentum across portfolio")
    elif avg_momentum < 8:
        insights.append(f"Weak momentum detected")
    
    return insights

# ============ EXPORT FUNCTION ============
def generate_html_report(stock_scores, portfolio_score):
    """Generate HTML report for export"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Mercato Portfolio Report</title>
        <style>
            body {{
                font-family: Georgia, serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                text-align: center;
                background: #343967;
                color: #e6e0d5;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 36px;
            }}
            .portfolio-score {{
                font-size: 64px;
                font-weight: 200;
                margin: 20px 0;
            }}
            .stock {{
                background: white;
                padding: 20px;
                margin: 15px 0;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .stock-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            .stock-name {{
                font-size: 20px;
                font-weight: 600;
                color: #343967;
            }}
            .stock-score {{
                font-size: 36px;
                color: #343967;
                font-weight: 200;
            }}
            .subscores {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 15px;
                margin-top: 15px;
            }}
            .subscore {{
                text-align: center;
            }}
            .subscore-label {{
                font-size: 11px;
                text-transform: uppercase;
                color: #666;
                margin-bottom: 5px;
            }}
            .subscore-value {{
                font-size: 18px;
                font-weight: 600;
                color: #343967;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Mercato Portfolio Report</h1>
            <div class="portfolio-score">{portfolio_score}/100</div>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
    """
    
    for stock in stock_scores:
        html += f"""
        <div class="stock">
            <div class="stock-header">
                <div>
                    <div class="stock-name">{stock['company_name']}</div>
                    <div style="color: #666; font-size: 13px;">{stock['ticker']} - {stock['shares']} shares</div>
                </div>
                <div class="stock-score">{stock['final_score']}</div>
            </div>
            <div style="margin: 10px 0;">
                <strong>Price:</strong> ${stock['price']:.2f} 
                <span style="color: {'#10b981' if stock['price_change'] >= 0 else '#ef4444'}">
                    {'+' if stock['price_change'] >= 0 else ''}{stock['price_change']:.2f}%
                </span>
            </div>
            <div class="subscores">
                <div class="subscore">
                    <div class="subscore-label">Financial Health</div>
                    <div class="subscore-value">{stock['financial_health']}/20</div>
                </div>
                <div class="subscore">
                    <div class="subscore-label">Profitability</div>
                    <div class="subscore-value">{stock['profitability']}/20</div>
                </div>
                <div class="subscore">
                    <div class="subscore-label">Growth</div>
                    <div class="subscore-value">{stock['growth']}/20</div>
                </div>
                <div class="subscore">
                    <div class="subscore-label">Momentum</div>
                    <div class="subscore-value">{stock['momentum']}/20</div>
                </div>
                <div class="subscore">
                    <div class="subscore-label">Stability</div>
                    <div class="subscore-value">{stock['stability']}/20</div>
                </div>
            </div>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return html

# ============ SCORE DESCRIPTIONS ============
SCORE_DESCRIPTIONS = {
    "Financial Health": "Can the company pay its bills? Looks at cash reserves, debt levels, and ability to withstand downturns.",
    "Profitability": "How much money does it keep? Higher margins mean more money kept from each sale.",
    "Growth": "Is it getting bigger? Shows how quickly revenue, earnings, and cash flow are expanding.",
    "Momentum": "Is the stock price trending up? Tracks recent stock performance compared to the market.",
    "Stability": "How risky/volatile is it? Lower volatility means less risk and steadier performance."
}

# ============ DIALOG SCREENS ============

@st.dialog("Welcome to Mercato")
def show_initial_login_dialog():
    """Initial login dialog"""
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><div style="font-size: 18px; color: #343967;">Sign in to save your portfolio, or skip to use without saving</div></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="dialog_login_email")
        password = st.text_input("Password", type="password", key="dialog_login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True):
                if email and password:
                    with st.spinner("Logging in..."):
                        result = sign_in(email, password)
                        if hasattr(result, 'user') and result.user:
                            st.session_state.user = result.user
                            st.session_state.authenticated = True
                            
                            # Load saved portfolio
                            portfolio, shares = load_portfolio_from_db(result.user.id)
                            if portfolio:
                                st.session_state.portfolio = portfolio
                                st.session_state.shares = shares
                            
                            st.session_state.started = True
                            st.success("Logged in!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                else:
                    st.error("Please enter email and password")
        
        with col2:
            if st.button("Skip - Use Without Saving", use_container_width=True):
                st.session_state.skip_login = True
                st.session_state.started = True
                st.rerun()
    
    with tab2:
        email = st.text_input("Email", key="dialog_signup_email")
        password = st.text_input("Password", type="password", key="dialog_signup_password")
        password2 = st.text_input("Confirm Password", type="password", key="dialog_signup_password2")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign Up", use_container_width=True):
                if email and password and password2:
                    if password != password2:
                        st.error("Passwords don't match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            result = sign_up(email, password)
                            if hasattr(result, 'user') and result.user:
                                st.session_state.user = result.user
                                st.session_state.authenticated = True
                                st.session_state.started = True
                                st.success("Account created!")
                                st.rerun()
                            else:
                                error_msg = result.get('error', 'Sign up failed')
                                st.error(f"Error: {error_msg}")
                else:
                    st.error("Please fill in all fields")
        
        with col2:
            if st.button("Skip", use_container_width=True, key="skip2"):
                st.session_state.skip_login = True
                st.session_state.started = True
                st.rerun()


@st.dialog("Stock Details")
def show_stock_details(stock):
    """Show detailed stock breakdown"""
    st.markdown(f'<div style="text-align: center; font-size: 24px; font-weight: 600; color: #343967; margin-bottom: 20px;">{stock["company_name"]}</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="background: #343967; padding: 40px; border-radius: 16px; text-align: center; margin-bottom: 20px;">
            <div style="color: #e6e0d5; font-size: 72px; font-weight: 200;">{stock['final_score']}</div>
            <div style="color: #d0c9bc; font-size: 16px;">Overall Score</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="font-size: 18px; font-weight: 600; color: #343967; margin: 20px 0 10px 0;">Score Breakdown</div>', unsafe_allow_html=True)
    
    for label, score in [
        ("Financial Health", stock['financial_health']),
        ("Profitability", stock['profitability']),
        ("Growth", stock['growth']),
        ("Momentum", stock['momentum']),
        ("Stability", stock['stability'])
    ]:
        width_pct = (score / 20) * 100
        description = SCORE_DESCRIPTIONS.get(label, '')
        
        st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 10px; margin: 12px 0; border: 2px solid #343967;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div style="color: #343967; font-size: 18px; font-weight: 600;">{label}</div>
                    <div>
                        <span style="color: #343967; font-size: 32px; font-weight: 200;">{score}</span>
                        <span style="color: #666; font-size: 16px;">/20</span>
                    </div>
                </div>
                <div style="background: rgba(230, 224, 213, 0.3); height: 12px; border-radius: 6px; overflow: hidden; margin: 12px 0;">
                    <div style="background: #343967; height: 100%; width: {width_pct}%; border-radius: 6px;"></div>
                </div>
                <div style="color: #666; font-size: 14px; line-height: 1.5; margin-top: 8px;">
                    {description}
                </div>
            </div>
        """, unsafe_allow_html=True)


@st.dialog("Price Chart")
def show_price_chart(stock):
    """Show price chart with different timeframes"""
    st.markdown(f'<div style="text-align: center; font-size: 24px; font-weight: 600; color: #343967; margin-bottom: 20px;">{stock["company_name"]} ({stock["ticker"]})</div>', unsafe_allow_html=True)
    
    # Timeframe selector
    timeframe = st.radio(
        "Select timeframe",
        ["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "5 Years"],
        horizontal=True,
        index=5  # Default to 1 Year
    )
    
    periods = {"1 Day": "1d", "1 Week": "5d", "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "5 Years": "5y"}
    intervals = {"1 Day": "5m", "1 Week": "15m", "1 Month": "1h", "3 Months": "1d", "6 Months": "1d", "1 Year": "1d", "5 Years": "1wk"}
    
    try:
        ticker_obj = yf.Ticker(stock['ticker'])
        hist = ticker_obj.history(period=periods[timeframe], interval=intervals[timeframe])
        
        if not hist.empty:
            fig = go.Figure()
            
            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='Price',
                increasing_line_color='#10b981',
                decreasing_line_color='#ef4444'
            ))
            
            fig.update_layout(
                height=400,
                margin=dict(l=50, r=20, t=20, b=40),
                plot_bgcolor='white',
                paper_bgcolor='#f5f5f5',
                xaxis_rangeslider_visible=False,
                font=dict(family='Georgia', color='#343967')
            )
            
            fig.update_xaxes(showgrid=True, gridcolor='rgba(52, 57, 103, 0.1)')
            fig.update_yaxes(showgrid=True, gridcolor='rgba(52, 57, 103, 0.1)', tickprefix='$')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Price stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current", f"${hist['Close'].iloc[-1]:.2f}")
            with col2:
                change = hist['Close'].iloc[-1] - hist['Close'].iloc[0]
                change_pct = (change / hist['Close'].iloc[0]) * 100
                st.metric("Change", f"${change:.2f}", f"{change_pct:+.2f}%")
            with col3:
                st.metric("High", f"${hist['High'].max():.2f}")
    except Exception as e:
        st.error(f"Could not load price data: {e}")


@st.dialog("Sector Comparison", width="large")
def show_sector_comparison(stock):
    """Show how stock ranks in its sector - ALL stocks"""
    st.markdown(f'<div style="text-align: center; font-size: 24px; font-weight: 600; color: #343967; margin-bottom: 10px;">{stock["company_name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center; font-size: 16px; color: #666; margin-bottom: 20px;">Sector: {stock["sector"]}</div>', unsafe_allow_html=True)
    
    # Get ALL stocks in same sector
    sector_stocks = SP500_SECTOR_STOCKS.get(stock['sector'], [])
    
    if not sector_stocks:
        st.warning("Sector comparison not available for this stock")
        return
    
    with st.spinner(f'Analyzing all {len(sector_stocks)} stocks in {stock["sector"]}...'):
        # Score ALL stocks in sector
        sector_scores = []
        for ticker in sector_stocks:
            try:
                score_result = score_stock(ticker)
                if score_result:
                    sector_scores.append(score_result)
            except:
                continue
        
        if not sector_scores:
            st.error("Could not load sector data")
            return
        
        # Sort by overall score
        sector_scores.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Find current stock's rank
        current_rank = next((i+1 for i, s in enumerate(sector_scores) if s['ticker'] == stock['ticker']), None)
        
        # Show rank at top
        if current_rank:
            st.markdown(f"""
                <div style="background: #343967; padding: 30px; border-radius: 16px; text-align: center; margin: 20px 0;">
                    <div style="color: #e6e0d5; font-size: 18px; margin-bottom: 10px;">Rank in {stock['sector']}</div>
                    <div style="color: #e6e0d5; font-size: 72px; font-weight: 200;">#{current_rank}</div>
                    <div style="color: #d0c9bc; font-size: 16px;">out of {len(sector_scores)} stocks</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Show full leaderboard
        st.markdown(f'<div style="font-size: 18px; font-weight: 600; color: #343967; margin: 20px 0;">Full {stock["sector"]} Leaderboard</div>', unsafe_allow_html=True)
        
        for i, s in enumerate(sector_scores):
            is_current = s['ticker'] == stock['ticker']
            bg_color = '#343967' if is_current else 'white'
            text_color = '#e6e0d5' if is_current else '#343967'
            border = '3px solid #e6e0d5' if is_current else '1px solid #ddd'
            
            st.markdown(f"""
                <div style="background: {bg_color}; padding: 15px; border-radius: 10px; margin: 8px 0; border: {border}; display: flex; justify-content: space-between; align-items: center;">
                    <div style="color: {text_color};">
                        <span style="font-weight: 600; font-size: 18px;">#{i+1}</span>
                        <span style="margin-left: 15px; font-size: 16px;">{s['company_name']}</span>
                        <span style="margin-left: 10px; font-size: 14px; opacity: 0.8;">({s['ticker']})</span>
                    </div>
                    <div style="font-size: 24px; font-weight: 200; color: {text_color};">{s['final_score']}</div>
                </div>
            """, unsafe_allow_html=True)


@st.dialog("Portfolio Score History")
def show_portfolio_history():
    """Show portfolio score over time for logged-in users"""
    user = st.session_state.get('user')
    
    if not user:
        st.warning("Login required to view portfolio history")
        return
    
    # Select timeframe
    days = st.selectbox("Timeframe", [7, 14, 30, 60, 90], format_func=lambda x: f"{x} days", index=2)
    
    with st.spinner('Loading history...'):
        history = get_portfolio_score_history(user.id, days=days)
        
        if not history:
            st.info("No history available yet. Refresh your scores a few times over the next few days to see your portfolio's performance over time.")
            return
        
        # Create chart
        dates = [h[0] for h in history]
        scores = [h[1] for h in history]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name='Portfolio Score',
            line=dict(color='#343967', width=3),
            marker=dict(size=8, color='#343967'),
            fill='tozeroy',
            fillcolor='rgba(52, 57, 103, 0.1)'
        ))
        
        fig.update_layout(
            height=350,
            margin=dict(l=50, r=20, t=20, b=40),
            plot_bgcolor='white',
            paper_bgcolor='#f5f5f5',
            font=dict(family='Georgia', color='#343967'),
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=True, gridcolor='rgba(52, 57, 103, 0.1)')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(52, 57, 103, 0.1)', title="Score")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats
        if len(scores) > 1:
            change = scores[-1] - scores[0]
            change_pct = (change / scores[0]) * 100 if scores[0] != 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Score", f"{scores[-1]:.1f}")
            with col2:
                st.metric("Change", f"{change:+.1f}", f"{change_pct:+.1f}%")
            with col3:
                st.metric("Peak", f"{max(scores):.1f}")


@st.dialog("Stock Preview")
def show_stock_preview(ticker):
    """Show stock preview before adding to portfolio"""
    with st.spinner(f'Loading {ticker}...'):
        score_result = score_stock(ticker)
        
        if not score_result:
            st.error("Could not load stock data")
            return
        
        # Display stock info
        etf_badge = '<span style="background: #10b981; color: white; font-size: 12px; padding: 3px 8px; border-radius: 4px; margin-left: 10px;">ETF</span>' if score_result.get('is_etf') else ''
        st.markdown(f'<div style="text-align: center; font-size: 28px; font-weight: 600; color: #343967; margin-bottom: 5px;">{score_result["company_name"]}{etf_badge}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; font-size: 16px; color: #666; margin-bottom: 20px;">{score_result["ticker"]} - {score_result["sector"]}</div>', unsafe_allow_html=True)
        
        # Score
        st.markdown(f"""
            <div style="background: #343967; padding: 30px; border-radius: 16px; text-align: center; margin: 20px 0;">
                <div style="color: #e6e0d5; font-size: 64px; font-weight: 200;">{score_result['final_score']}</div>
                <div style="color: #d0c9bc; font-size: 16px;">Overall Score</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Subscores
        col1, col2, col3, col4, col5 = st.columns(5)
        subscores = [
            (col1, "Financial", score_result['financial_health']),
            (col2, "Profit", score_result['profitability']),
            (col3, "Growth", score_result['growth']),
            (col4, "Momentum", score_result['momentum']),
            (col5, "Stability", score_result['stability'])
        ]
        
        for col, label, score in subscores:
            with col:
                st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: 600; color: #343967;">{score}</div>
                        <div style="font-size: 11px; color: #666; text-transform: uppercase;">{label}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Add button
        shares = st.number_input("Number of shares", min_value=0.001, value=1.0, step=0.1, format="%.3f")
        
        if st.button("Add to Portfolio", use_container_width=True, type="primary"):
            if ticker not in st.session_state.portfolio:
                st.session_state.portfolio.append(ticker)
                st.session_state.shares[ticker] = shares
                
                # Save if logged in
                if st.session_state.get('authenticated'):
                    save_portfolio_to_db(st.session_state.user.id, st.session_state.portfolio, st.session_state.shares)
                
                st.session_state.needs_calculation = True
                st.success(f"{ticker} added!")
                st.rerun()
            else:
                st.warning(f"{ticker} already in portfolio")


def show_welcome_screen():
    """Welcome screen with logo"""
    if LOGO_BASE64:
        st.markdown(f"""
            <div style="text-align: center; padding: 80px 20px;">
                <div style="margin-bottom: 30px;">
                    <img src="data:image/png;base64,{LOGO_BASE64}" style="width: 100px; height: 100px; border-radius: 16px;"/>
                </div>
                <div class="welcome-title">Mercato</div>
                <div class="welcome-tagline">The market made simple</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 100px 20px;">
                <div class="welcome-title">Mercato</div>
                <div class="welcome-tagline">The market made simple</div>
            </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Get Started", use_container_width=True, key="get_started"):
            show_initial_login_dialog()

def show_main_app():
    """Main app screen with all fixes"""
    
    # Header
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        if st.session_state.get('authenticated'):
            user_email = st.session_state.user.email.split('@')[0]
            st.markdown(f'<div style="color: #343967; font-size: 13px; padding: 10px;">Logged in: {user_email}</div>', unsafe_allow_html=True)
    
    with col2:
        if LOGO_BASE64:
            st.markdown(f'''
                <div class="logo-header">
                    <img src="data:image/png;base64,{LOGO_BASE64}"/>
                    <div>
                        <div class="welcome-title" style="font-size: 28px; text-align: left; margin: 0;">Mercato</div>
                        <div class="welcome-tagline" style="font-size: 14px; text-align: left; margin: 0;">The market made simple</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('<div class="welcome-title" style="font-size: 32px;">Mercato</div>', unsafe_allow_html=True)
            st.markdown('<div class="welcome-tagline" style="font-size: 16px;">The market made simple</div>', unsafe_allow_html=True)
    
    with col3:
        if st.session_state.get('authenticated'):
            if st.button("Logout", use_container_width=True):
                sign_out()
                st.session_state.started = False
                st.rerun()
        else:
            if st.button("Login", use_container_width=True, type="primary"):
                show_initial_login_dialog()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Add stocks section
    st.markdown('<div class="section-header">Add Stocks to Portfolio</div>', unsafe_allow_html=True)
    
    # Single search bar with autocomplete
    ticker_input = st.text_input(
        "Search stocks", 
        placeholder="Start typing a ticker or company name (e.g. AAPL, TSLA)...",
        key="stock_search",
        label_visibility="collapsed"
    ).upper().strip()
    
    # Show autocomplete suggestions as user types
    if ticker_input and len(ticker_input) >= 1:
        matches = [t for t in POPULAR_STOCKS if ticker_input in t]
        
        if matches:
            st.markdown('<div style="font-size: 12px; color: #666; margin: 5px 0 10px 0;">Quick select:</div>', unsafe_allow_html=True)
            
            # Show matching tickers in compact grid
            num_matches = min(len(matches), 10)
            cols_per_row = 5
            for i in range(0, num_matches, cols_per_row):
                cols = st.columns(cols_per_row)
                for j, ticker in enumerate(matches[i:i+cols_per_row]):
                    with cols[j]:
                        if st.button(ticker, key=f"auto_{ticker}_{i}", use_container_width=True):
                            # Directly add the clicked ticker
                            if ticker not in st.session_state.portfolio:
                                with st.spinner(f'Adding {ticker}...'):
                                    try:
                                        test_stock = yf.Ticker(ticker)
                                        test_hist = test_stock.history(period="5d")
                                        
                                        if not test_hist.empty:
                                            st.session_state.portfolio.append(ticker)
                                            st.session_state.shares[ticker] = 1.0  # Default 1 share
                                            
                                            if st.session_state.get('authenticated'):
                                                save_portfolio_to_db(st.session_state.user.id, st.session_state.portfolio, st.session_state.shares)
                                            
                                            st.session_state.needs_calculation = True
                                            st.success(f"✓ {ticker} added!")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Stock '{ticker}' not found")
                                    except:
                                        st.error(f"❌ Could not add '{ticker}'")
                            else:
                                st.warning(f"{ticker} already in portfolio")
    
    # Shares input and Search button
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        shares_input = st.number_input("Shares", min_value=0.001, value=1.0, step=0.1, format="%.3f", label_visibility="collapsed", key="shares_main")
    with col3:
        search_clicked = st.button("Add", use_container_width=True, type="primary", key="search_btn")
    
    # Process manual search button
    if search_clicked:
        if ticker_input:
            mapped_ticker = COMPANY_TICKER_MAP.get(ticker_input, ticker_input)
            
            if mapped_ticker in st.session_state.portfolio:
                st.warning(f"{mapped_ticker} already in portfolio")
            else:
                with st.spinner(f'Adding {mapped_ticker}...'):
                    try:
                        test_stock = yf.Ticker(mapped_ticker)
                        test_hist = test_stock.history(period="5d")
                        
                        if test_hist.empty:
                            st.error(f"❌ Stock '{mapped_ticker}' not found")
                        else:
                            # Add to portfolio
                            st.session_state.portfolio.append(mapped_ticker)
                            st.session_state.shares[mapped_ticker] = shares_input
                            
                            # Save if logged in
                            if st.session_state.get('authenticated'):
                                save_portfolio_to_db(st.session_state.user.id, st.session_state.portfolio, st.session_state.shares)
                            
                            st.session_state.needs_calculation = True
                            st.success(f"✓ {mapped_ticker} added!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Could not add '{mapped_ticker}' - stock may not exist")
        else:
            st.warning("Please enter a stock ticker")
    
    # Portfolio display
    if st.session_state.portfolio:
        st.markdown('<div class="section-header">Your Portfolio</div>', unsafe_allow_html=True)
        
        # Calculate scores if needed
        if st.session_state.get('needs_calculation', True):
            with st.spinner('Analyzing portfolio...'):
                stock_scores = []
                for ticker in st.session_state.portfolio:
                    score_result = score_stock(ticker)
                    if score_result:
                        score_result['shares'] = st.session_state.shares.get(ticker, 1.0)
                        stock_scores.append(score_result)
                        
                        # Save to history if logged in
                        if st.session_state.get('authenticated'):
                            save_score_to_history(st.session_state.user.id, ticker, score_result)
                
                st.session_state.stock_scores = stock_scores
                st.session_state.needs_calculation = False
        
        # Display portfolio
        if st.session_state.stock_scores:
            portfolio_score = calculate_portfolio_score(st.session_state.stock_scores)
            
            # Portfolio score
            st.markdown(f"""
                <div class="health-score-container">
                    <div class="health-score-number">{portfolio_score}</div>
                    <div class="health-score-subtext">Portfolio Score</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Action buttons at top
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Refresh Scores", use_container_width=True, key="refresh_top"):
                    st.session_state.needs_calculation = True
                    st.rerun()
            
            with col2:
                if st.button("Portfolio History", use_container_width=True, key="history_top"):
                    show_portfolio_history()
            
            with col3:
                # Export report
                html_report = generate_html_report(st.session_state.stock_scores, portfolio_score)
                st.download_button(
                    label="Export Report",
                    data=html_report,
                    file_name=f"mercato_report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True,
                    key="export_top"
                )
            
            # Insights
            insights = generate_insights(st.session_state.stock_scores)
            if insights:
                for insight in insights:
                    st.markdown(f'<div class="insight-card"><div class="insight-text">{insight}</div></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Sort options
            col_sort1, col_sort2 = st.columns([3, 2])
            with col_sort1:
                st.markdown('<div style="font-size: 14px; font-weight: 600; color: #343967; padding: 10px 0;">Sort by:</div>', unsafe_allow_html=True)
            with col_sort2:
                sort_option = st.selectbox(
                    "Sort by",
                    ["Overall Score", "Financial Health", "Profitability", "Growth", "Momentum", "Stability"],
                    label_visibility="collapsed",
                    key="sort_option"
                )
            
            # Sort stocks based on selection
            sort_map = {
                "Overall Score": "final_score",
                "Financial Health": "financial_health",
                "Profitability": "profitability",
                "Growth": "growth",
                "Momentum": "momentum",
                "Stability": "stability"
            }
            
            sorted_stocks = sorted(
                st.session_state.stock_scores, 
                key=lambda x: x[sort_map[sort_option]], 
                reverse=True
            )
            
            # Stock cards with FIXED visibility
            for stock in sorted_stocks:
                price_change_class = "price-change-positive" if stock['price_change'] >= 0 else "price-change-negative"
                price_change_symbol = "+" if stock['price_change'] >= 0 else ""
                
                # Score change if logged in (simple text, no HTML inside)
                score_change_display = ""
                if st.session_state.get('authenticated'):
                    score_change = get_score_change(st.session_state.user.id, stock['ticker'])
                    if score_change and score_change != 0:
                        symbol = "↑" if score_change > 0 else "↓"
                        score_change_display = f" {symbol}{abs(score_change):.1f}"
                
                # Company logo (keep it simple)
                logo_display = ""
                if stock.get('logo_url'):
                    logo_display = f'<img src="{stock["logo_url"]}" class="company-logo" onerror="this.style.display=\'none\'" />'
                
                # ETF badge (simple HTML, no emoji)
                etf_display = ""
                if stock.get('is_etf'):
                    etf_display = '<span style="background: #10b981; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; margin-left: 8px; font-weight: 600;">ETF</span>'
                
                col_a, col_b = st.columns([4, 1])
                
                with col_a:
                    # Build HTML string carefully
                    html_parts = []
                    html_parts.append('<div class="stock-card">')
                    html_parts.append('  <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">')
                    
                    # Logo (if exists)
                    if logo_display:
                        html_parts.append(f'    {logo_display}')
                    
                    html_parts.append('    <div style="flex: 1;">')
                    html_parts.append('      <div style="display: flex; justify-content: space-between; align-items: center;">')
                    html_parts.append('        <div>')
                    html_parts.append(f'          <div class="company-name">{stock["company_name"]}{etf_display}</div>')
                    html_parts.append(f'          <div class="stock-ticker">{stock["ticker"]} - {stock["shares"]} shares</div>')
                    html_parts.append('        </div>')
                    html_parts.append(f'        <div class="stock-score">{stock["final_score"]}{score_change_display}</div>')
                    html_parts.append('      </div>')
                    html_parts.append('    </div>')
                    html_parts.append('  </div>')
                    html_parts.append(f'  <div class="stock-price">${stock["price"]:.2f} <span class="{price_change_class}">{price_change_symbol}{stock["price_change"]:.2f}%</span></div>')
                    html_parts.append('  <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 12px;">')
                    
                    # Subscores
                    for label, key in [('Financial', 'financial_health'), ('Profit', 'profitability'), ('Growth', 'growth'), ('Momentum', 'momentum'), ('Stability', 'stability')]:
                        width = stock[key] / 20 * 100
                        html_parts.append('    <div class="subscore-container">')
                        html_parts.append(f'      <div class="subscore-label">{label}</div>')
                        html_parts.append(f'      <div class="subscore-bar"><div class="subscore-fill" style="width: {width}%"></div></div>')
                        html_parts.append('    </div>')
                    
                    html_parts.append('  </div>')
                    html_parts.append('</div>')
                    
                    st.markdown('\n'.join(html_parts), unsafe_allow_html=True)
                
                with col_b:
                    # 2x2 button grid
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Chart", key=f"chart_{stock['ticker']}", use_container_width=True):
                            show_price_chart(stock)
                        if st.button("Details", key=f"details_{stock['ticker']}", use_container_width=True):
                            show_stock_details(stock)
                    with btn_col2:
                        if st.button("Compare", key=f"compare_{stock['ticker']}", use_container_width=True):
                            show_sector_comparison(stock)
                        if st.button("Remove", key=f"remove_{stock['ticker']}", use_container_width=True):
                            st.session_state.portfolio.remove(stock['ticker'])
                            if stock['ticker'] in st.session_state.shares:
                                del st.session_state.shares[stock['ticker']]
                            st.session_state.stock_scores = [s for s in st.session_state.stock_scores if s['ticker'] != stock['ticker']]
                            
                            # Update database if logged in
                            if st.session_state.get('authenticated'):
                                save_portfolio_to_db(st.session_state.user.id, st.session_state.portfolio, st.session_state.shares)
                            
                            st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
    else:
        st.info("Add stocks to your portfolio to get started")

# ============ MAIN ============
def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'shares' not in st.session_state:
        st.session_state.shares = {}
    if 'stock_scores' not in st.session_state:
        st.session_state.stock_scores = []
    if 'skip_login' not in st.session_state:
        st.session_state.skip_login = False
    if 'needs_calculation' not in st.session_state:
        st.session_state.needs_calculation = True
    if 'started' not in st.session_state:
        st.session_state.started = False
    if 'ticker_input_value' not in st.session_state:
        st.session_state.ticker_input_value = ""
    
    # Check if user is logged in from previous session
    if not st.session_state.authenticated and supabase:
        user = get_user()
        if user:
            st.session_state.user = user
            st.session_state.authenticated = True
            st.session_state.started = True
            
            # Load saved portfolio
            portfolio, shares = load_portfolio_from_db(user.id)
            if portfolio:
                st.session_state.portfolio = portfolio
                st.session_state.shares = shares
                st.session_state.needs_calculation = True
    
    # Show appropriate screen
    if not st.session_state.started:
        show_welcome_screen()
    else:
        show_main_app()


if __name__ == "__main__":
    main()

