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
        padding: 10px 20px;
        font-size: 14px;
        border-radius: 10px;
        border: none;
        width: 100%;
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

# ============ STOCK SCORING FUNCTIONS ============
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")
        
        if hist.empty:
            return None
        
        company_name = info.get('longName', info.get('shortName', ticker))
        
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
            'sector': info.get('sector', 'Unknown'),
            'price': hist['Close'].iloc[-1],
            'prev_close': hist['Close'].iloc[-2] if len(hist) >= 2 else hist['Close'].iloc[-1],
            'total_debt': info.get('totalDebt', 0),
            'total_cash': info.get('totalCash', 0),
            'free_cash_flow': info.get('freeCashflow', 0),
            'market_cap': info.get('marketCap', 1),
            'profit_margin': info.get('profitMargins', 0),
            'operating_margin': info.get('operatingMargins', 0),
            'roe': info.get('returnOnEquity', 0),
            'revenue_growth': info.get('revenueGrowth', 0),
            'earnings_growth': info.get('earningsGrowth', 0),
            'beta': info.get('beta', 1),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'hist': hist
        }
    except:
        return None

def calculate_financial_health(data):
    scores = []
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
    
    cash_ratio = data['total_cash'] / data['market_cap'] if data['market_cap'] > 0 else 0
    cash_score = min(1.0, cash_ratio * 5 + 0.3)
    scores.append(cash_score)
    
    fcf_ratio = data['free_cash_flow'] / data['market_cap'] if data['market_cap'] > 0 else 0
    if fcf_ratio > 0.05:
        fcf_score = 0.9
    elif fcf_ratio > 0:
        fcf_score = 0.7
    else:
        fcf_score = 0.4
    scores.append(fcf_score)
    
    return np.mean(scores) * 20

def calculate_profitability(data):
    scores = []
    pm = data['profit_margin']
    if pm > 0.30:
        pm_score = 1.0
    elif pm > 0.20:
        pm_score = 0.75
    elif pm > 0.12:
        pm_score = 0.55
    elif pm > 0.06:
        pm_score = 0.35
    else:
        pm_score = max(0.15, pm * 3)
    scores.append(pm_score)
    
    om = data['operating_margin']
    if om > 0.35:
        om_score = 1.0
    elif om > 0.25:
        om_score = 0.75
    elif om > 0.15:
        om_score = 0.55
    elif om > 0.08:
        om_score = 0.35
    else:
        om_score = max(0.15, om * 2.5)
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
        roe_score = max(0.15, roe * 2.5)
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
    
    scores.append(0.65)
    return np.mean(scores) * 20

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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Add stocks section
    st.markdown('<div class="section-header">Add Stocks to Portfolio</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        # FIXED: Use session state to clear input after adding
        if 'ticker_input_value' not in st.session_state:
            st.session_state.ticker_input_value = ""
        
        ticker_input = st.text_input(
            "Stock ticker or company name", 
            key="main_ticker",
            value=st.session_state.ticker_input_value,
            label_visibility="collapsed", 
            placeholder="Enter ticker (e.g. AAPL, TSLA)"
        ).upper()
    
    with col2:
        shares_input = st.number_input("Shares", min_value=0.001, value=1.0, step=0.1, format="%.3f", label_visibility="collapsed")
    
    with col3:
        add_button = st.button("Add to Portfolio", use_container_width=True)
    
    # FIXED: Only process if button clicked AND ticker exists AND not just added
    if add_button and ticker_input and not st.session_state.get('just_added', False):
        mapped_ticker = COMPANY_TICKER_MAP.get(ticker_input, ticker_input)
        
        if mapped_ticker in st.session_state.portfolio:
            st.warning(f"{mapped_ticker} already in portfolio")
        else:
            with st.spinner('Validating stock...'):
                try:
                    test_stock = yf.Ticker(mapped_ticker)
                    test_hist = test_stock.history(period="5d")
                    
                    if test_hist.empty:
                        st.error("Stock not found")
                    else:
                        # Add to portfolio
                        st.session_state.portfolio.append(mapped_ticker)
                        st.session_state.shares[mapped_ticker] = shares_input
                        
                        # Save to database if logged in
                        if st.session_state.get('authenticated'):
                            save_portfolio_to_db(st.session_state.user.id, st.session_state.portfolio, st.session_state.shares)
                        
                        # Clear input and trigger recalculation
                        st.session_state.ticker_input_value = ""
                        st.session_state.needs_calculation = True
                        st.session_state.just_added = True
                        st.success(f"{mapped_ticker} added!")
                        st.rerun()
                except:
                    st.error("Stock not found")
    elif add_button and not ticker_input:
        st.warning("Please enter a stock ticker")
    
    # Reset the just_added flag
    if 'just_added' in st.session_state and st.session_state.just_added:
        st.session_state.just_added = False
    
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
                
                # Score change if logged in
                score_change_text = ""
                if st.session_state.get('authenticated'):
                    score_change = get_score_change(st.session_state.user.id, stock['ticker'])
                    if score_change and score_change != 0:
                        symbol = "↑" if score_change > 0 else "↓"
                        score_change_text = f'<span style="font-size: 14px; color: #e6e0d5;"> {symbol}{abs(score_change):.1f}</span>'
                
                # Logo
                logo_html = ""
                if stock.get('logo_url'):
                    logo_html = f'<img src="{stock["logo_url"]}" class="company-logo" onerror="this.style.display=\'none\'">'
                
                col_a, col_b, col_c = st.columns([5, 1, 1])
                
                with col_a:
                    st.markdown(f"""
                        <div class="stock-card">
                            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                                {logo_html}
                                <div style="flex: 1;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <div class="company-name">{stock['company_name']}</div>
                                            <div class="stock-ticker">{stock['ticker']} - {stock['shares']} shares</div>
                                        </div>
                                        <div class="stock-score">{stock['final_score']}{score_change_text}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="stock-price">${stock['price']:.2f} <span class="{price_change_class}">{price_change_symbol}{stock['price_change']:.2f}%</span></div>
                            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 12px;">
                                <div class="subscore-container">
                                    <div class="subscore-label">Financial</div>
                                    <div class="subscore-bar"><div class="subscore-fill" style="width: {stock['financial_health']/20*100}%"></div></div>
                                </div>
                                <div class="subscore-container">
                                    <div class="subscore-label">Profit</div>
                                    <div class="subscore-bar"><div class="subscore-fill" style="width: {stock['profitability']/20*100}%"></div></div>
                                </div>
                                <div class="subscore-container">
                                    <div class="subscore-label">Growth</div>
                                    <div class="subscore-bar"><div class="subscore-fill" style="width: {stock['growth']/20*100}%"></div></div>
                                </div>
                                <div class="subscore-container">
                                    <div class="subscore-label">Momentum</div>
                                    <div class="subscore-bar"><div class="subscore-fill" style="width: {stock['momentum']/20*100}%"></div></div>
                                </div>
                                <div class="subscore-container">
                                    <div class="subscore-label">Stability</div>
                                    <div class="subscore-bar"><div class="subscore-fill" style="width: {stock['stability']/20*100}%"></div></div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_b:
                    if st.button("Details", key=f"details_{stock['ticker']}", use_container_width=True):
                        show_stock_details(stock)
                
                with col_c:
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
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Refresh Scores", use_container_width=True):
                    st.session_state.needs_calculation = True
                    st.rerun()
            
            with col2:
                # Export report
                html_report = generate_html_report(st.session_state.stock_scores, portfolio_score)
                st.download_button(
                    label="Export Report",
                    data=html_report,
                    file_name=f"mercato_report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html",
                    use_container_width=True
                )
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
