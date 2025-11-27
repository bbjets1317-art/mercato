"""
Mercato - The Market Made Simple
Enhanced with: Daily tracking, Portfolio history, Image upload
"""

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import base64
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
import pytesseract

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
    """Save individual stock score to history"""
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

def save_portfolio_score_to_history(user_id, portfolio_score, stock_scores):
    """Save overall portfolio score snapshot"""
    if not supabase or not user_id:
        return False
    try:
        # Calculate portfolio metrics
        total_value = sum(s['price'] * s['shares'] for s in stock_scores)
        avg_financial = np.mean([s['financial_health'] for s in stock_scores])
        avg_profit = np.mean([s['profitability'] for s in stock_scores])
        avg_growth = np.mean([s['growth'] for s in stock_scores])
        avg_momentum = np.mean([s['momentum'] for s in stock_scores])
        avg_stability = np.mean([s['stability'] for s in stock_scores])
        
        data = {
            "user_id": str(user_id),
            "portfolio_score": float(portfolio_score),
            "total_value": float(total_value),
            "num_stocks": len(stock_scores),
            "avg_financial_health": float(avg_financial),
            "avg_profitability": float(avg_profit),
            "avg_growth": float(avg_growth),
            "avg_momentum": float(avg_momentum),
            "avg_stability": float(avg_stability)
        }
        supabase.table("portfolio_history").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error saving portfolio history: {e}")
        return False

def get_portfolio_history(user_id, days=365):
    """Get portfolio score history for past X days"""
    if not supabase or not user_id:
        return []
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        response = supabase.table("portfolio_history").select(
            "calculated_at, portfolio_score, total_value"
        ).eq("user_id", str(user_id)).gte(
            "calculated_at", cutoff_date
        ).order("calculated_at", desc=False).execute()
        
        if response.data:
            return [(item['calculated_at'], item['portfolio_score'], item['total_value']) for item in response.data]
        return []
    except:
        return []

def get_stock_score_history(user_id, ticker, days=365):
    """Get individual stock score history"""
    if not supabase or not user_id:
        return []
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        response = supabase.table("score_history").select(
            "calculated_at, score, price"
        ).eq("user_id", str(user_id)).eq(
            "ticker", ticker
        ).gte("calculated_at", cutoff_date).order("calculated_at", desc=False).execute()
        
        if response.data:
            return [(item['calculated_at'], item['score'], item['price']) for item in response.data]
        return []
    except:
        return []

def get_score_change(user_id, ticker):
    """Get score change from previous calculation"""
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

def check_and_run_daily_update(user_id):
    """Check if daily update needs to run (at 4 PM ET market close)"""
    if not supabase or not user_id:
        return False
    
    try:
        # Get last update time
        response = supabase.table("portfolio_history").select(
            "calculated_at"
        ).eq("user_id", str(user_id)).order("calculated_at", desc=True).limit(1).execute()
        
        now = datetime.now()
        
        # Check if it's after 4 PM ET (market close)
        market_close_time = time(16, 0)  # 4:00 PM
        
        if response.data:
            last_update = datetime.fromisoformat(response.data[0]['calculated_at'].replace('Z', '+00:00'))
            
            # If last update was today after 4 PM, skip
            if last_update.date() == now.date() and last_update.time() > market_close_time:
                return False
        
        # Run update if it's after 4 PM and hasn't been done today
        if now.time() > market_close_time:
            return True
        
        return False
    except:
        return False

# ============ IMAGE PROCESSING FOR PORTFOLIO UPLOAD ============
def extract_tickers_from_image(image):
    """Extract stock tickers from uploaded portfolio screenshot"""
    try:
        # Convert to PIL Image if needed
        if not isinstance(image, Image.Image):
            image = Image.open(image)
        
        # Use OCR to extract text
        text = pytesseract.image_to_string(image)
        
        # Find all potential tickers (1-5 uppercase letters)
        potential_tickers = re.findall(r'\b[A-Z]{1,5}\b', text)
        
        # Filter to valid tickers by checking against known stocks
        valid_tickers = []
        for ticker in set(potential_tickers):
            # Skip common words that might be mistaken for tickers
            if ticker in ['USD', 'ETF', 'STOCK', 'PRICE', 'VALUE', 'TOTAL', 'CASH', 'DATE', 'TIME']:
                continue
            
            # Quick validation - try to fetch the ticker
            try:
                test_stock = yf.Ticker(ticker)
                test_hist = test_stock.history(period="5d")
                if not test_hist.empty:
                    valid_tickers.append(ticker)
            except:
                continue
        
        return valid_tickers
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return []

# ============ S&P 500 SECTOR STOCKS & AUTOCOMPLETE ============
@st.cache_data(ttl=86400)
def fetch_sp500_stocks():
    """Fetch S&P 500 stocks from Wikipedia, use hardcoded backup if fails"""
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'id': 'constituents'})
            
            if table:
                df = pd.read_html(str(table))[0]
                
                sector_stocks = {}
                for sector in df['GICS Sector'].unique():
                    tickers = df[df['GICS Sector'] == sector]['Symbol'].tolist()
                    tickers = [t.replace('.', '-') if '.' in t else t for t in tickers]
                    sector_stocks[sector] = tickers
                
                sector_name_map = {
                    'Information Technology': 'Technology',
                    'Financials': 'Financial Services',
                    'Health Care': 'Healthcare',
                    'Consumer Discretionary': 'Consumer Cyclical',
                    'Consumer Staples': 'Consumer Defensive',
                    'Materials': 'Basic Materials'
                }
                
                mapped_sectors = {}
                for sector, tickers in sector_stocks.items():
                    display_name = sector_name_map.get(sector, sector)
                    mapped_sectors[display_name] = tickers
                
                return mapped_sectors
    except Exception as e:
        st.warning(f"Could not fetch live S&P 500 data, using backup list")
    
    return {
        'Technology': ['AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'CSCO', 'ADBE', 'CRM', 'INTC', 'AMD'],
        'Financial Services': ['BRK.B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'AXP', 'C'],
        'Healthcare': ['UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY'],
        'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TGT', 'TJX', 'CMG'],
        'Consumer Defensive': ['WMT', 'PG', 'KO', 'PEP', 'COST', 'PM', 'MO', 'CL', 'KMB', 'GIS'],
        'Industrials': ['CAT', 'GE', 'UPS', 'HON', 'BA', 'LMT', 'RTX', 'UNP', 'DE', 'MMM'],
        'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HES'],
        'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'PEG', 'XEL', 'ED'],
        'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'SPG', 'WELL', 'DLR', 'O', 'AVB'],
        'Basic Materials': ['LIN', 'APD', 'ECL', 'SHW', 'NEM', 'FCX', 'NUE', 'DOW', 'DD', 'ALB'],
        'Communication Services': ['META', 'GOOGL', 'GOOG', 'NFLX', 'DIS', 'CMCSA', 'T', 'TMUS', 'VZ', 'EA']
    }

SP500_SECTOR_STOCKS = fetch_sp500_stocks()

POPULAR_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'V', 'JNJ',
    'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'CRM', 'NFLX', 'CSCO', 'INTC', 'AMD',
    'SPY', 'QQQ', 'VOO', 'VTI', 'IWM', 'EEM', 'GLD', 'TLT', 'AGG', 'VNQ']

COMPANY_TICKER_MAP = {
    'APPLE': 'AAPL', 'MICROSOFT': 'MSFT', 'GOOGLE': 'GOOGL', 'ALPHABET': 'GOOGL',
    'AMAZON': 'AMZN', 'TESLA': 'TSLA', 'META': 'META', 'FACEBOOK': 'META',
    'NVIDIA': 'NVDA', 'NETFLIX': 'NFLX', 'DISNEY': 'DIS', 'WALMART': 'WMT'
}

# Load logo
try:
    with open('mercato_logo.png', 'rb') as f:
        LOGO_BASE64 = base64.b64encode(f.read()).decode()
except:
    LOGO_BASE64 = None

st.set_page_config(page_title="Mercato", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# ============ CSS ============
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

# ============ SECTOR BENCHMARKS ============
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

DEFAULT_BENCHMARK = {'profit_margin': 0.12, 'operating_margin': 0.15, 'growth': 0.08}

def get_sector_benchmark(sector):
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
        quote_type = info.get('quoteType', '')
        is_etf = quote_type == 'ETF' or 'fund' in company_name.lower() or 'etf' in company_name.lower()
        
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
    
    cash_ratio = data['total_cash'] / data['market_cap'] if data['market_cap'] > 0 else 0
    cash_score = min(1.0, cash_ratio * 5 + 0.3)
    scores.append(cash_score)
    weights.append(0.30)
    
    fcf_ratio = data['free_cash_flow'] / data['market_cap'] if data['market_cap'] > 0 else 0
    if fcf_ratio > 0.05:
        fcf_score = 0.9
    elif fcf_ratio > 0:
        fcf_score = 0.7
    else:
        fcf_score = 0.4
    scores.append(fcf_score)
    weights.append(0.40)
    
    weighted_score = sum(s * w for s, w in zip(scores, weights))
    return weighted_score * 20

def calculate_profitability(data):
    scores = []
    benchmark = get_sector_benchmark(data.get('sector', 'Unknown'))
    
    pm = data['profit_margin']
    pm_benchmark = benchmark['profit_margin']
    
    if pm > pm_benchmark * 2:
        pm_score = 1.0
    elif pm > pm_benchmark * 1.5:
        pm_score = 0.85
    elif pm > pm_benchmark:
        pm_score = 0.70
    elif pm > pm_benchmark * 0.7:
        pm_score = 0.50
    elif pm > 0:
        pm_score = 0.35
    else:
        pm_score = 0.20
    scores.append(pm_score)
    
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
    
    market_cap = data['market_cap']
    if market_cap > 200_000_000_000:
        size_bonus = 0.15
    elif market_cap > 10_000_000_000:
        size_bonus = 0.05
    elif market_cap < 2_000_000_000:
        size_bonus = -0.1
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
    
    is_etf = data.get('is_etf', False)
    
    if is_etf:
        financial_health = 10.0
        profitability = 10.0
        growth = 10.0
        momentum = calculate_momentum(data)
        stability = calculate_stability(data)
    else:
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
    st.markdown(f'<div style="text-align: center; font-size: 24px; font-weight: 600; color: #343967; margin-bottom: 20px;">{stock["company_name"]} ({stock["ticker"]})</div>', unsafe_allow_html=True)
    
    timeframe = st.radio(
        "Select timeframe",
        ["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "5 Years"],
        horizontal=True,
        index=5
    )
    
    periods = {"1 Day": "1d", "1 Week": "5d", "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "5 Years": "5y"}
    intervals = {"1 Day": "5m", "1 Week": "15m", "1 Month": "1h", "3 Months": "1d", "6 Months": "1d", "1 Year": "1d", "5 Years": "1wk"}
    
    try:
        ticker_obj = yf.Ticker(stock['ticker'])
        hist = ticker_obj.history(period=periods[timeframe], interval=intervals[timeframe])
        
        if not hist.empty:
            fig = go.Figure()
            
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
    st.markdown(f'<div style="text-align: center; font-size: 24px; font-weight: 600; color: #343967; margin-bottom: 10px;">{stock["company_name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: center; font-size: 16px; color: #666; margin-bottom: 20px;">Sector: {stock["sector"]}</div>', unsafe_allow_html=True)
    
    sector_stocks = SP500_SECTOR_STOCKS.get(stock['sector'], [])
    
    if not sector_stocks:
        st.warning("Sector comparison not available for this stock")
        return
    
    with st.spinner(f'Analyzing all {len(sector_stocks)} stocks in {stock["sector"]}...'):
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
        
        sector_scores.sort(key=lambda x: x['final_score'], reverse=True)
        current_rank = next((i+1 for i, s in enumerate(sector_scores) if s['ticker'] == stock['ticker']), None)
        
        if current_rank:
            st.markdown(f"""
                <div style="background: #343967; padding: 30px; border-radius: 16px; text-align: center; margin: 20px 0;">
                    <div style="color: #e6e0d5; font-size: 18px; margin-bottom: 10px;">Rank in {stock['sector']}</div>
                    <div style="color: #e6e0d5; font-size: 72px; font-weight: 200;">#{current_rank}</div>
                    <div style="color: #d0c9bc; font-size: 16px;">out of {len(sector_scores)} stocks</div>
                </div>
            """, unsafe_allow_html=True)
        
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


@st.dialog("Portfolio History", width="large")
def show_portfolio_history_dialog():
    """Show portfolio score and value over time"""
    user = st.session_state.get('user')
    
    if not user:
        st.warning("Login required to view portfolio history")
        return
    
    days = st.selectbox("Timeframe", [7, 14, 30, 60, 90, 180, 365], format_func=lambda x: f"{x} days" if x < 365 else "1 year", index=6)
    
    with st.spinner('Loading history...'):
        history = get_portfolio_history(user.id, days=days)
        
        if not history:
            st.info("No history available yet. Your portfolio score is automatically tracked daily at market close (4 PM ET). Check back tomorrow to see your first data point!")
            return
        
        dates = [datetime.fromisoformat(h[0].replace('Z', '+00:00')) for h in history]
        scores = [h[1] for h in history]
        values = [h[2] for h in history]
        
        # Create dual-axis chart
        fig = go.Figure()
        
        # Portfolio Score
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name='Portfolio Score',
            line=dict(color='#343967', width=3),
            marker=dict(size=8, color='#343967'),
            yaxis='y'
        ))
        
        # Portfolio Value
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8, color='#10b981'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            height=400,
            margin=dict(l=50, r=50, t=20, b=40),
            plot_bgcolor='white',
            paper_bgcolor='#f5f5f5',
            font=dict(family='Georgia', color='#343967'),
            yaxis=dict(
                title="Score",
                titlefont=dict(color='#343967'),
                tickfont=dict(color='#343967'),
                showgrid=True,
                gridcolor='rgba(52, 57, 103, 0.1)'
            ),
            yaxis2=dict(
                title="Value ($)",
                titlefont=dict(color='#10b981'),
                tickfont=dict(color='#10b981'),
                overlaying='y',
                side='right',
                showgrid=False
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(showgrid=True, gridcolor='rgba(52, 57, 103, 0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats
        if len(scores) > 1:
            score_change = scores[-1] - scores[0]
            score_change_pct = (score_change / scores[0]) * 100 if scores[0] != 0 else 0
            value_change = values[-1] - values[0]
            value_change_pct = (value_change / values[0]) * 100 if values[0] != 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Score", f"{scores[-1]:.1f}")
            with col2:
                st.metric("Score Change", f"{score_change:+.1f}", f"{score_change_pct:+.1f}%")
            with col3:
                st.metric("Current Value", f"${values[-1]:,.2f}")
            with col4:
                st.metric("Value Change", f"${value_change:+,.2f}", f"{value_change_pct:+.1f}%")


@st.dialog("Stock History", width="large")
def show_stock_history_dialog(ticker):
    """Show individual stock score history"""
    user = st.session_state.get('user')
    
    if not user:
        st.warning("Login required to view stock history")
        return
    
    days = st.selectbox("Timeframe", [7, 14, 30, 60, 90, 180, 365], format_func=lambda x: f"{x} days" if x < 365 else "1 year", index=5, key=f"stock_hist_{ticker}")
    
    with st.spinner(f'Loading {ticker} history...'):
        history = get_stock_score_history(user.id, ticker, days=days)
        
        if not history:
            st.info(f"No history available for {ticker} yet. Score history is automatically tracked daily at market close.")
            return
        
        dates = [datetime.fromisoformat(h[0].replace('Z', '+00:00')) for h in history]
        scores = [h[1] for h in history]
        prices = [h[2] for h in history]
        
        # Create dual-axis chart
        fig = go.Figure()
        
        # Score
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name='Score',
            line=dict(color='#343967', width=3),
            marker=dict(size=8, color='#343967'),
            yaxis='y'
        ))
        
        # Price
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines+markers',
            name='Price',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8, color='#10b981'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            height=400,
            margin=dict(l=50, r=50, t=20, b=40),
            plot_bgcolor='white',
            paper_bgcolor='#f5f5f5',
            font=dict(family='Georgia', color='#343967'),
            yaxis=dict(
                title="Score",
                titlefont=dict(color='#343967'),
                tickfont=dict(color='#343967'),
                showgrid=True,
                gridcolor='rgba(52, 57, 103, 0.1)'
            ),
            yaxis2=dict(
                title="Price ($)",
                titlefont=dict(color='#10b981'),
                tickfont=dict(color='#10b981'),
                overlaying='y',
                side='right',
                showgrid=False,
                tickprefix='$'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(showgrid=True, gridcolor='rgba(52, 57, 103, 0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats
        if len(scores) > 1:
            score_change = scores[-1] - scores[0]
            price_change = prices[-1] - prices[0]
            price_change_pct = (price_change / prices[0]) * 100 if prices[0] != 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Score", f"{scores[-1]:.1f}")
            with col2:
                st.metric("Score Change", f"{score_change:+.1f}")
            with col3:
                st.metric("Current Price", f"${prices[-1]:.2f}")
            with col4:
                st.metric("Price Change", f"${price_change:+.2f}", f"{price_change_pct:+.1f}%")


@st.dialog("Upload Portfolio Screenshot")
def show_portfolio_upload_dialog():
    """Upload portfolio image and extract tickers"""
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><div style="font-size: 18px; color: #343967;">Upload a screenshot of your portfolio to automatically extract stock tickers</div></div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'], key="portfolio_image")
    
    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Portfolio", use_column_width=True)
        
        if st.button("Extract Tickers", use_container_width=True, type="primary"):
            with st.spinner("Analyzing image..."):
                tickers = extract_tickers_from_image(image)
                
                if tickers:
                    st.success(f"Found {len(tickers)} potential stocks!")
                    
                    st.markdown('<div style="font-size: 14px; font-weight: 600; color: #343967; margin: 15px 0;">Select stocks to add:</div>', unsafe_allow_html=True)
                    
                    # Show tickers with checkboxes
                    selected_tickers = []
                    for ticker in tickers:
                        if st.checkbox(f"{ticker}", value=True, key=f"cb_{ticker}"):
                            selected_tickers.append(ticker)
                    
                    if st.button("Add Selected Stocks", use_container_width=True):
                        added = []
                        for ticker in selected_tickers:
                            if ticker not in st.session_state.portfolio:
                                st.session_state.portfolio.append(ticker)
                                st.session_state.shares[ticker] = 1.0
                                added.append(ticker)
                        
                        if added:
                            # Save if logged in
                            if st.session_state.get('authenticated'):
                                save_portfolio_to_db(st.session_state.user.id, st.session_state.portfolio, st.session_state.shares)
                            
                            st.session_state.needs_calculation = True
                            st.success(f"Added {len(added)} stocks: {', '.join(added)}")
                            st.rerun()
                        else:
                            st.info("All selected stocks already in portfolio")
                else:
                    st.error("No valid stock tickers found in image. Make sure the image clearly shows ticker symbols.")


def show_welcome_screen():
    """Welcome screen"""
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
    """Main app screen"""
    
    # Check for daily update if logged in
    if st.session_state.get('authenticated') and st.session_state.portfolio:
        if check_and_run_daily_update(st.session_state.user.id):
            with st.spinner('Running daily portfolio update...'):
                # Calculate scores
                stock_scores = []
                for ticker in st.session_state.portfolio:
                    score_result = score_stock(ticker)
                    if score_result:
                        score_result['shares'] = st.session_state.shares.get(ticker, 1.0)
                        stock_scores.append(score_result)
                        save_score_to_history(st.session_state.user.id, ticker, score_result)
                
                if stock_scores:
                    portfolio_score = calculate_portfolio_score(stock_scores)
                    save_portfolio_score_to_history(st.session_state.user.id, portfolio_score, stock_scores)
    
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
    
    # Upload portfolio button
    if st.button("📤 Upload Portfolio Screenshot", use_container_width=False, key="upload_btn"):
        show_portfolio_upload_dialog()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Search bar
    ticker_input = st.text_input(
        "Search stocks", 
        placeholder="Start typing a ticker or company name (e.g. AAPL, TSLA)...",
        key="stock_search",
        label_visibility="collapsed"
    ).upper().strip()
    
    # Autocomplete
    if ticker_input and len(ticker_input) >= 1:
        matches = [t for t in POPULAR_STOCKS if ticker_input in t]
        
        if matches:
            st.markdown('<div style="font-size: 12px; color: #666; margin: 5px 0 10px 0;">Quick select:</div>', unsafe_allow_html=True)
            
            num_matches = min(len(matches), 10)
            cols_per_row = 5
            for i in range(0, num_matches, cols_per_row):
                cols = st.columns(cols_per_row)
                for j, ticker in enumerate(matches[i:i+cols_per_row]):
                    with cols[j]:
                        if st.button(ticker, key=f"auto_{ticker}_{i}", use_container_width=True):
                            if ticker not in st.session_state.portfolio:
                                with st.spinner(f'Adding {ticker}...'):
                                    try:
                                        test_stock = yf.Ticker(ticker)
                                        test_hist = test_stock.history(period="5d")
                                        
                                        if not test_hist.empty:
                                            st.session_state.portfolio.append(ticker)
                                            st.session_state.shares[ticker] = 1.0
                                            
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
    
    # Manual add
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        shares_input = st.number_input("Shares", min_value=0.001, value=1.0, step=0.1, format="%.3f", label_visibility="collapsed", key="shares_main")
    with col3:
        search_clicked = st.button("Add", use_container_width=True, type="primary", key="search_btn")
    
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
                            st.session_state.portfolio.append(mapped_ticker)
                            st.session_state.shares[mapped_ticker] = shares_input
                            
                            if st.session_state.get('authenticated'):
                                save_portfolio_to_db(st.session_state.user.id, st.session_state.portfolio, st.session_state.shares)
                            
                            st.session_state.needs_calculation = True
                            st.success(f"✓ {mapped_ticker} added!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Could not add '{mapped_ticker}'")
        else:
            st.warning("Please enter a stock ticker")
    
    # Portfolio display
    if st.session_state.portfolio:
        st.markdown('<div class="section-header">Your Portfolio</div>', unsafe_allow_html=True)
        
        # Calculate scores
        if st.session_state.get('needs_calculation', True):
            with st.spinner('Analyzing portfolio...'):
                stock_scores = []
                for ticker in st.session_state.portfolio:
                    score_result = score_stock(ticker)
                    if score_result:
                        score_result['shares'] = st.session_state.shares.get(ticker, 1.0)
                        stock_scores.append(score_result)
                        
                        if st.session_state.get('authenticated'):
                            save_score_to_history(st.session_state.user.id, ticker, score_result)
                
                st.session_state.stock_scores = stock_scores
                st.session_state.needs_calculation = False
                
                # Save portfolio snapshot if logged in
                if st.session_state.get('authenticated') and stock_scores:
                    portfolio_score = calculate_portfolio_score(stock_scores)
                    save_portfolio_score_to_history(st.session_state.user.id, portfolio_score, stock_scores)
        
        if st.session_state.stock_scores:
            portfolio_score = calculate_portfolio_score(st.session_state.stock_scores)
            
            # Portfolio score
            st.markdown(f"""
                <div class="health-score-container">
                    <div class="health-score-number">{portfolio_score}</div>
                    <div class="health-score-subtext">Portfolio Score</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Refresh Scores", use_container_width=True, key="refresh_top"):
                    st.session_state.needs_calculation = True
                    st.rerun()
            
            with col2:
                if st.button("Portfolio History", use_container_width=True, key="history_top"):
                    show_portfolio_history_dialog()
            
            with col3:
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
            
            # Stock cards
            for stock in sorted_stocks:
                price_change_class = "price-change-positive" if stock['price_change'] >= 0 else "price-change-negative"
                price_change_symbol = "+" if stock['price_change'] >= 0 else ""
                
                score_change_display = ""
                if st.session_state.get('authenticated'):
                    score_change = get_score_change(st.session_state.user.id, stock['ticker'])
                    if score_change and score_change != 0:
                        symbol = "↑" if score_change > 0 else "↓"
                        score_change_display = f" {symbol}{abs(score_change):.1f}"
                
                logo_display = ""
                if stock.get('logo_url'):
                    logo_display = f'<img src="{stock["logo_url"]}" class="company-logo" onerror="this.style.display=\'none\'" />'
                
                etf_display = ""
                if stock.get('is_etf'):
                    etf_display = '<span style="background: #10b981; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; margin-left: 8px; font-weight: 600;">ETF</span>'
                
                col_a, col_b = st.columns([4, 1])
                
                with col_a:
                    html_parts = []
                    html_parts.append('<div class="stock-card">')
                    html_parts.append('  <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">')
                    
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
                    # 3x2 button grid with history
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Chart", key=f"chart_{stock['ticker']}", use_container_width=True):
                            show_price_chart(stock)
                        if st.button("Details", key=f"details_{stock['ticker']}", use_container_width=True):
                            show_stock_details(stock)
                        if st.button("History", key=f"hist_{stock['ticker']}", use_container_width=True):
                            show_stock_history_dialog(stock['ticker'])
                    with btn_col2:
                        if st.button("Compare", key=f"compare_{stock['ticker']}", use_container_width=True):
                            show_sector_comparison(stock)
                        if st.button("Remove", key=f"remove_{stock['ticker']}", use_container_width=True):
                            st.session_state.portfolio.remove(stock['ticker'])
                            if stock['ticker'] in st.session_state.shares:
                                del st.session_state.shares[stock['ticker']]
                            st.session_state.stock_scores = [s for s in st.session_state.stock_scores if s['ticker'] != stock['ticker']]
                            
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
    
    # Check if logged in from previous session
    if not st.session_state.authenticated and supabase:
        user = get_user()
        if user:
            st.session_state.user = user
            st.session_state.authenticated = True
            st.session_state.started = True
            
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
