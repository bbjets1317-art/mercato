"""
Mercato - The Market Made Simple
Light blue design with Mercato logo
"""

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import base64

# Load logo as base64
try:
    with open('mercato_logo.png', 'rb') as f:
        LOGO_BASE64 = base64.b64encode(f.read()).decode()
except:
    # Fallback SVG if logo file not found
    LOGO_BASE64 = None, timedelta

# Page config
st.set_page_config(
    page_title="Mercato",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Light Blue Mercato Design
st.markdown("""
    <style>
    /* Brand Colors */
    :root {
        --beige: #F9F8F6;
        --blue: #343967;
        --white: #FFFFFF;
        --gray-light: #F5F5F5;
        --gray-medium: #E0E0E0;
        --gray-dark: #666666;
    }
    
    /* Global Font */
    * {
        font-family: Georgia, serif !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
    
    /* Main background - Gradient old money beige */
    .main {
        background: linear-gradient(135deg, #f5f0e8 0%, #e6e0d5 50%, #d9d0c1 100%);
        min-height: 100vh;
        padding: 20px 0;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Welcome screen */
    .welcome-container {
        text-align: center;
        padding: 100px 20px;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .welcome-logo {
        margin-bottom: 30px;
    }
    
    .welcome-title {
        font-size: 72px;
        font-weight: 700;
        color: #343967;
        margin: 20px 0;
        letter-spacing: -2px;
    }
    
    .welcome-tagline {
        font-size: 28px;
        color: #343967;
        margin: 20px 0;
        font-weight: 400;
        font-style: italic;
    }
    
    /* Loading screen - BLUE */
    .loading-screen {
        background: #343967;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 9999;
    }
    
    .loading-content {
        text-align: center;
        color: white;
    }
    
    .loading-logo {
        margin-bottom: 40px;
    }
    
    .loading-text {
        font-size: 32px;
        color: white;
        margin: 30px 0;
        font-weight: 500;
    }
    
    .loading-subtext {
        font-size: 18px;
        color: #F9F8F6;
        font-style: italic;
    }
    
    /* Portfolio Health Score - Elegant navy */
    .health-score-container {
        background: #343967;
        padding: 60px 40px;
        border-radius: 20px;
        text-align: center;
        margin: 40px auto;
        max-width: 600px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(230, 224, 213, 0.2);
    }
    
    .health-score-label {
        color: #e6e0d5;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    
    .health-score-number {
        color: #e6e0d5;
        font-size: 140px;
        font-weight: 200;
        line-height: 1;
        margin: 20px 0;
        font-family: Georgia, serif;
    }
    
    .health-score-subtext {
        color: #d0c9bc;
        font-size: 18px;
        margin-top: 10px;
        font-weight: 400;
    }
    
    /* Insight cards - Navy with gold accent */
    .insight-card {
        background: #343967;
        padding: 20px 26px;
        border-radius: 14px;
        margin: 12px 0;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
        border: 1px solid rgba(230, 224, 213, 0.15);
        border-left: 3px solid #c9a961;
    }
    
    .insight-text {
        color: #f5f0e8;
        font-size: 16px;
        line-height: 1.6;
        font-weight: 500;
        letter-spacing: -0.1px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* Stock cards - Navy with elegant styling */
    .stock-card {
        background: #343967;
        padding: 22px 26px;
        border-radius: 14px;
        margin: 12px 0;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
        transition: all 0.3s ease;
        border: 1px solid rgba(230, 224, 213, 0.15);
    }
    
    .stock-card:hover {
        border-color: #c9a961;
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
        transform: translateY(-3px);
    }
    
    .stock-header-row {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 14px;
    }
    
    .company-logo {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        object-fit: contain;
        background: #F5F5F5;
        padding: 7px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }
    
    .company-info {
        flex: 1;
    }
    
    .company-name {
        font-size: 20px;
        font-weight: 600;
        color: #e6e0d5;
        margin-bottom: 3px;
        line-height: 1.3;
        letter-spacing: -0.3px;
    }
    
    .stock-ticker {
        font-size: 13px;
        font-weight: 600;
        color: #c9a961;
        letter-spacing: 1.2px;
        text-transform: uppercase;
    }
    
    .stock-score {
        font-size: 56px;
        font-weight: 200;
        color: #e6e0d5;
        text-align: right;
    }
    
    .stock-price {
        font-size: 20px;
        color: #e6e0d5;
        margin: 12px 0 6px 0;
        font-weight: 500;
    }
    
    .price-change-positive {
        color: #10b981;
        font-weight: 600;
        font-size: 16px;
    }
    
    .price-change-negative {
        color: #ef4444;
        font-weight: 600;
        font-size: 16px;
    }
    
    /* Sub-score bars - Beige labels on navy cards */
    .subscore-container {
        margin: 12px 0;
    }
    
    .subscore-label {
        color: #e6e0d5;
        font-size: 12px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }
    
    .subscore-bar {
        background: #2a2f52;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .subscore-fill {
        background: linear-gradient(90deg, #e6e0d5 0%, #d0c9bc 100%);
        height: 100%;
        border-radius: 4px;
        transition: width 0.8s ease;
    }
    
    /* Buttons - Navy with gold hover */
    .stButton > button {
        background: linear-gradient(135deg, #343967 0%, #2a2f52 100%);
        color: white;
        border: 1px solid rgba(201, 169, 97, 0.3);
        padding: 16px 32px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2a2f52 0%, #343967 100%);
        border-color: #c9a961;
        box-shadow: 0 6px 20px rgba(201, 169, 97, 0.3);
        transform: translateY(-2px);
    }
    
    /* Section headers - Navy */
    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #343967;
        margin: 35px 0 18px 0;
        padding-bottom: 10px;
        border-bottom: 2.5px solid #343967;
        letter-spacing: -0.5px;
    }
    
    /* Detail view - Elegant navy */
    .detail-score-big {
        text-align: center;
        background: linear-gradient(135deg, #343967 0%, #2a2f52 100%);
        padding: 60px;
        border-radius: 20px;
        margin: 30px auto;
        max-width: 600px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(230, 224, 213, 0.2);
    }
    
    .detail-score-number {
        font-size: 120px;
        font-weight: 200;
        margin: 20px 0;
        color: #e6e0d5;
    }
    
    .subscore-detail {
        background: #343967;
        padding: 28px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(230, 224, 213, 0.2);
    }
    
    .subscore-detail-label {
        font-size: 18px;
        font-weight: 600;
        color: #e6e0d5;
        margin-bottom: 16px;
        letter-spacing: -0.3px;
    }
    
    .subscore-detail-number {
        font-size: 48px;
        font-weight: 200;
        color: #e6e0d5;
        display: inline-block;
        margin-right: 8px;
    }
    
    /* Header logo */
    .header-container {
        background: linear-gradient(135deg, #343967 0%, #2a2f52 100%);
        padding: 24px 32px;
        border-radius: 16px;
        margin-bottom: 40px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(230, 224, 213, 0.2);
    }
    
    .mercato-logo-text {
        font-size: 32px;
        font-weight: 700;
        color: #e6e0d5;
        letter-spacing: -1px;
    }
    
    .mercato-logo-img {
        width: 44px;
        height: 44px;
        border-radius: 8px;
    }
    
    /* Input fields - Elegant white */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #d9d0c1;
        padding: 16px;
        font-size: 16px;
        background: white;
        color: #343967 !important;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #c9a961;
        box-shadow: 0 4px 12px rgba(201, 169, 97, 0.2);
        color: #343967 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #999999 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #343967 0%, #c9a961 100%);
    }
    </style>
""", unsafe_allow_html=True)


# ============ SCORING FUNCTIONS (Same as before) ============

def get_stock_data(ticker):
    """Get financial data for a stock"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")
        
        if hist.empty:
            return None
        
        company_name = info.get('longName', info.get('shortName', ticker))
        logo_url = f"https://logo.clearbit.com/{info.get('website', '').replace('https://', '').replace('http://', '').split('/')[0]}"
        
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
    except Exception as e:
        st.error(f"Error fetching {ticker}: {e}")
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
    if pm > 0.30:  # Exceptional - very few companies
        pm_score = 1.0
    elif pm > 0.20:  # Great
        pm_score = 0.75
    elif pm > 0.12:  # Good
        pm_score = 0.55
    elif pm > 0.06:  # Average
        pm_score = 0.35
    else:
        pm_score = max(0.15, pm * 3)
    scores.append(pm_score)
    
    om = data['operating_margin']
    if om > 0.35:  # Exceptional
        om_score = 1.0
    elif om > 0.25:  # Great
        om_score = 0.75
    elif om > 0.15:  # Good
        om_score = 0.55
    elif om > 0.08:  # Average
        om_score = 0.35
    else:
        om_score = max(0.15, om * 2.5)
    scores.append(om_score)
    
    roe = data['roe']
    if roe > 0.25:  # Exceptional
        roe_score = 1.0
    elif roe > 0.18:  # Great
        roe_score = 0.75
    elif roe > 0.12:  # Good
        roe_score = 0.55
    elif roe > 0.06:  # Average
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
        
        # 1-month momentum - more balanced
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
        
        # 3-month momentum - more balanced
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
    
    # Beta scoring - more generous
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
    
    # 52-week range volatility - more balanced
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
    
    # Drawdown - more forgiving
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
    
    positive_movers = sum(1 for s in stock_scores if s['price_change'] > 0)
    if positive_movers > len(stock_scores) / 2:
        insights.append(f"{positive_movers} of {len(stock_scores)} stocks gained today")
    
    return insights


# ============ SCREEN FUNCTIONS ============

def show_welcome():
    """Welcome screen"""
    logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" style="width: 120px; height: 120px; border-radius: 16px;"/>' if LOGO_BASE64 else '<svg width=120 height=120 viewBox="0 0 150 150" fill="none"><path d="M75 20L50 60V130H75V130H100V60L75 20Z" fill="#343967"/><path d="M35 40L20 60V130H35V130H50V60L35 40Z" fill="#343967"/><path d="M115 40L100 60V130H115V130H130V60L115 40Z" fill="#343967"/></svg>'
    
    st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-logo">
                {logo_html}
            </div>
            <div class="welcome-title">Mercato</div>
            <div class="welcome-tagline">The market made simple</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Get Started", use_container_width=True):
            st.session_state.screen = 'add_stocks'
            st.rerun()


def show_add_stocks():
    """Add stocks screen"""
    st.markdown('<div class="welcome-title" style="text-align: center; font-size: 48px; margin-bottom: 30px; color: #343967;">Add Your Stocks</div>', unsafe_allow_html=True)
    
    # Initialize shares dict if not exists
    if 'shares' not in st.session_state:
        st.session_state.shares = {}
    
    # Action buttons at top
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Stock", use_container_width=True, key="add_stock_top"):
            st.session_state.show_add_form = not st.session_state.get('show_add_form', False)
    with col2:
        if st.session_state.portfolio:
            if st.button("Continue to Dashboard", use_container_width=True):
                st.session_state.screen = 'calculating'
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Show add form if toggled
    if st.session_state.get('show_add_form', False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="section-header">Add New Stock</div>', unsafe_allow_html=True)
            ticker_input = st.text_input("Stock ticker (e.g., AAPL, TSLA)", key="ticker_input").upper()
            shares_input = st.number_input("Number of shares (optional)", min_value=0.0, value=0.0, step=0.1, format="%.3f", key="shares_input", help="Leave as 0 if you don't want to track shares")
            
            if st.button("Add to Portfolio", use_container_width=True):
                if ticker_input:
                    if ticker_input in st.session_state.portfolio:
                        st.warning(f"{ticker_input} already in portfolio")
                    else:
                        # Validate ticker first
                        with st.spinner('Validating...'):
                            try:
                                test_stock = yf.Ticker(ticker_input)
                                test_hist = test_stock.history(period="5d")
                                
                                # Check if we got valid price data
                                if test_hist.empty or len(test_hist) == 0:
                                    st.error(f"Stock not available")
                                else:
                                    # Stock is valid - add to portfolio with shares
                                    st.session_state.portfolio.append(ticker_input)
                                    if shares_input > 0:
                                        st.session_state.shares[ticker_input] = shares_input
                                    else:
                                        st.session_state.shares[ticker_input] = None
                                    st.success(f"{ticker_input} added successfully")
                                    st.session_state.show_add_form = False
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Stock not available")
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Show portfolio list
    if st.session_state.portfolio:
        st.markdown('<div class="section-header">Your Portfolio</div>', unsafe_allow_html=True)
        
        for ticker in st.session_state.portfolio:
            shares = st.session_state.shares.get(ticker)
            
            # Get stock data for daily change
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    price_change = current_price - prev_price
                    price_change_pct = (price_change / prev_price) * 100
                    
                    # Calculate total gain/loss if shares provided
                    if shares and shares > 0:
                        total_change = price_change * shares
                        change_color = "#10b981" if total_change >= 0 else "#ef4444"
                        sign = "+" if total_change >= 0 else ""
                        shares_display = f"{shares} shares • {sign}${total_change:.2f} today"
                    else:
                        change_color = "#10b981" if price_change >= 0 else "#ef4444"
                        sign = "+" if price_change >= 0 else ""
                        shares_display = f"${current_price:.2f} • {sign}${price_change:.2f} ({sign}{price_change_pct:.2f}%)"
                else:
                    shares_display = f"{shares} shares" if shares else "Tracking"
                    change_color = "#666666"
            except:
                shares_display = f"{shares} shares" if shares else "Tracking"
                change_color = "#666666"
            
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.markdown(f'''
                    <div style="background: #343967; padding: 16px 20px; border-radius: 12px; margin: 8px 0;">
                        <div style="color: #e6e0d5; font-size: 20px; font-weight: 600; font-family: Georgia;">{ticker}</div>
                        <div style="color: {change_color}; font-size: 14px; font-family: Georgia; margin-top: 4px;">{shares_display}</div>
                    </div>
                ''', unsafe_allow_html=True)
            with col_b:
                if st.button("Remove", key=f"remove_{ticker}", use_container_width=True):
                    st.session_state.portfolio.remove(ticker)
                    if ticker in st.session_state.shares:
                        del st.session_state.shares[ticker]
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)



def show_calculating():
    """Loading screen - Blue with logo"""
    logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" style="width: 100px; height: 100px; border-radius: 16px;"/>' if LOGO_BASE64 else '<svg width=100 height=100 viewBox="0 0 150 150" fill="none"><path d="M75 20L50 60V130H75V130H100V60L75 20Z" fill="#F9F8F6"/><path d="M35 40L20 60V130H35V130H50V60L35 40Z" fill="#F9F8F6"/><path d="M115 40L100 60V130H115V130H130V60L115 40Z" fill="#F9F8F6"/></svg>'
    
    st.markdown(f"""
        <div class="loading-content">
            <div class="loading-logo">
                {logo_html}
            </div>
            <div class="loading-text">Mercato</div>
            <div class="loading-subtext">The market made simple</div>
        </div>
    """, unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    stock_scores = []
    total = len(st.session_state.portfolio)
    
    for i, ticker in enumerate(st.session_state.portfolio):
        progress_bar.progress((i + 1) / total)
        score = score_stock(ticker)
        if score:
            stock_scores.append(score)
    
    st.session_state.stock_scores = stock_scores
    st.session_state.screen = 'dashboard'
    st.rerun()


def show_dashboard():
    """Main dashboard"""
    if not st.session_state.stock_scores:
        st.session_state.screen = 'add_stocks'
        st.rerun()
        return
    
    # Header with Mercato logo
    logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" class="mercato-logo-img"/>' if LOGO_BASE64 else '<svg width=44 height=44 viewBox="0 0 150 150" fill="none"><path d="M75 20L50 60V130H75V130H100V60L75 20Z" fill="#343967"/><path d="M35 40L20 60V130H35V130H50V60L35 40Z" fill="#343967"/><path d="M115 40L100 60V130H115V130H130V60L115 40Z" fill="#343967"/></svg>'
    
    st.markdown(f"""
        <div class="header-container">
            <div style="display: flex; align-items: center; gap: 16px;">
                {logo_html}
                <span class="mercato-logo-text">Mercato</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action buttons at top
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add More Stocks", use_container_width=True):
            st.session_state.screen = 'manage'
            st.rerun()
    with col2:
        if st.button("Refresh Scores", use_container_width=True):
            st.session_state.screen = 'calculating'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Calculate portfolio value and daily change
    total_value = 0
    total_daily_change = 0
    stocks_with_shares = 0
    
    for stock in st.session_state.stock_scores:
        ticker = stock['ticker']
        shares = st.session_state.shares.get(ticker)
        
        if shares and shares > 0:
            stocks_with_shares += 1
            current_price = stock['price']
            price_change = stock['price_change'] / 100 * current_price  # Convert % to $
            
            stock_value = current_price * shares
            stock_daily_change = price_change * shares
            
            total_value += stock_value
            total_daily_change += stock_daily_change
    
    # Show portfolio value summary if user has shares entered
    if stocks_with_shares > 0:
        daily_change_pct = (total_daily_change / (total_value - total_daily_change)) * 100 if (total_value - total_daily_change) != 0 else 0
        change_color = "#10b981" if total_daily_change >= 0 else "#ef4444"
        sign = "+" if total_daily_change >= 0 else ""
        
        st.markdown(f"""
            <div style="background: #343967; padding: 30px; border-radius: 16px; margin-bottom: 30px; text-align: center; border: 1px solid rgba(230, 224, 213, 0.2);">
                <div style="color: #d0c9bc; font-size: 14px; font-family: Georgia; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">
                    Portfolio Value
                </div>
                <div style="color: #e6e0d5; font-size: 48px; font-weight: 200; font-family: Georgia; margin: 10px 0;">
                    ${total_value:,.2f}
                </div>
                <div style="color: {change_color}; font-size: 24px; font-family: Georgia; margin-top: 10px;">
                    {sign}${abs(total_daily_change):,.2f} ({sign}{daily_change_pct:.2f}%)
                </div>
                <div style="color: #d0c9bc; font-size: 14px; font-family: Georgia; margin-top: 8px;">
                    Today
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Portfolio Health Score
    portfolio_score = calculate_portfolio_score(st.session_state.stock_scores)
    
    # Create gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = portfolio_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Portfolio Health Score", 'font': {'size': 24, 'color': '#e6e0d5', 'family': 'Georgia'}},
        number = {'font': {'size': 60, 'color': '#e6e0d5', 'family': 'Georgia'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#e6e0d5", 'tickfont': {'color': '#e6e0d5', 'family': 'Georgia'}},
            'bar': {'color': "#e6e0d5", 'thickness': 0.75},
            'bgcolor': "#2a2f52",
            'borderwidth': 2,
            'bordercolor': "#e6e0d5",
            'steps': [
                {'range': [0, 40], 'color': '#5a4a42'},
                {'range': [40, 70], 'color': '#6b5d52'},
                {'range': [70, 100], 'color': '#8b7d6b'}
            ],
            'threshold': {
                'line': {'color': "#e6e0d5", 'width': 4},
                'thickness': 0.75,
                'value': portfolio_score
            }
        }
    ))
    
    fig_gauge.update_layout(
        paper_bgcolor = "#343967",
        plot_bgcolor = "#343967",
        font = {'color': "#e6e0d5", 'family': 'Georgia'},
        height = 350,
        margin = dict(l=20, r=20, t=80, b=20)
    )
    
    # Display gauge in a navy container
    st.markdown("""
        <div class="health-score-container" style="padding: 40px 20px;">
        </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    st.markdown(f"""
        <div style="text-align: center; color: #343967; font-size: 18px; margin-top: -20px; margin-bottom: 40px;">
            <b>Score: {portfolio_score} / 100</b>
        </div>
    """, unsafe_allow_html=True)
    
    # Insights
    st.markdown('<div class="section-header">Daily Insights</div>', unsafe_allow_html=True)
    
    insights = generate_insights(st.session_state.stock_scores)
    for insight in insights:
        st.markdown(f'<div class="insight-card"><div class="insight-text">{insight}</div></div>', unsafe_allow_html=True)
    
    # Stock List
    st.markdown('<div class="section-header">Your Stocks</div>', unsafe_allow_html=True)
    
    sorted_stocks = sorted(st.session_state.stock_scores, key=lambda x: x['final_score'], reverse=True)
    
    for stock in sorted_stocks:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
                <div class="stock-card">
                    <div class="stock-header-row">
                        <img src="{stock['logo_url']}" class="company-logo" onerror="this.style.display='none'"/>
                        <div class="company-info">
                            <div class="company-name">{stock['company_name']}</div>
                            <div class="stock-ticker">{stock['ticker']}</div>
                        </div>
                    </div>
                    <div class="stock-price">${stock["price"]:.2f}</div>
            """, unsafe_allow_html=True)
            
            change_class = "price-change-positive" if stock["price_change"] >= 0 else "price-change-negative"
            sign = "+" if stock["price_change"] >= 0 else ""
            st.markdown(f'<div class="{change_class}">{sign}{stock["price_change"]:.2f}%</div>', unsafe_allow_html=True)
            
            # Show daily gain/loss if shares are tracked
            ticker = stock['ticker']
            shares = st.session_state.shares.get(ticker)
            if shares and shares > 0:
                price_change_dollars = stock["price_change"] / 100 * stock["price"]
                daily_change = price_change_dollars * shares
                change_color = "#10b981" if daily_change >= 0 else "#ef4444"
                sign_dollar = "+" if daily_change >= 0 else ""
                
                st.markdown(f"""
                    <div style="color: {change_color}; font-size: 16px; margin-top: 8px; font-weight: 600;">
                        {shares} shares • {sign_dollar}${abs(daily_change):.2f} today
                    </div>
                """, unsafe_allow_html=True)
            
            # Sub-scores
            cols = st.columns(5)
            subscores = [
                ('Financial', stock['financial_health']),
                ('Profit', stock['profitability']),
                ('Growth', stock['growth']),
                ('Momentum', stock['momentum']),
                ('Stability', stock['stability'])
            ]
            
            for col, (label, score) in zip(cols, subscores):
                with col:
                    st.markdown(f"""
                        <div class="subscore-container">
                            <div class="subscore-label">{label}</div>
                            <div class="subscore-bar">
                                <div class="subscore-fill" style="width: {(score/20)*100}%"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'<div class="stock-score" style="padding-top: 20px;">{stock["final_score"]}</div>', unsafe_allow_html=True)
            if st.button("View Details", key=f"view_{stock['ticker']}", use_container_width=True):
                st.session_state.selected_stock = stock['ticker']
                st.session_state.screen = 'stock_detail'
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)


def show_stock_detail():
    """Stock detail screen"""
    if not st.session_state.selected_stock:
        st.session_state.screen = 'dashboard'
        st.rerun()
        return
    
    stock = next((s for s in st.session_state.stock_scores if s['ticker'] == st.session_state.selected_stock), None)
    
    if not stock:
        st.session_state.screen = 'dashboard'
        st.rerun()
        return
    
    if st.button("← Back"):
        st.session_state.screen = 'dashboard'
        st.rerun()
    
    st.markdown(f"""
        <div style="text-align: center; margin-top: 40px;">
            <img src="{stock['logo_url']}" style="width: 80px; height: 80px; border-radius: 16px; margin-bottom: 20px; background: white; padding: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" onerror="this.style.display='none'"/>
            <div class="welcome-title" style="font-size: 42px; margin-top: 10px;">{stock['company_name']}</div>
            <div class="welcome-tagline" style="font-size: 20px;">{stock['ticker']} • {stock['sector']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Show current price and daily change
    price_change_dollars = stock["price_change"] / 100 * stock["price"]
    change_color = "#10b981" if stock["price_change"] >= 0 else "#ef4444"
    sign = "+" if stock["price_change"] >= 0 else ""
    
    # Get shares if available
    ticker = stock['ticker']
    shares = st.session_state.shares.get(ticker)
    
    # Always show shares input field
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #343967; margin: 20px 0;">', unsafe_allow_html=True)
        st.markdown('<div style="color: #343967; font-size: 16px; font-weight: 600; font-family: Georgia; margin-bottom: 12px;">Track Your Position</div>', unsafe_allow_html=True)
        
        current_shares = float(shares) if shares and shares > 0 else 0.0
        new_shares = st.number_input("Number of shares", min_value=0.0, value=current_shares, step=0.1, format="%.3f", key=f"shares_{ticker}", help="Enter 0 to stop tracking position")
        
        if st.button("Update Position", use_container_width=True, key=f"update_pos_{ticker}"):
            if new_shares > 0:
                st.session_state.shares[ticker] = new_shares
            else:
                st.session_state.shares[ticker] = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show position value/price based on whether shares are tracked
    if shares and shares > 0:
        # Show position value and gain/loss
        position_value = stock["price"] * shares
        daily_change = price_change_dollars * shares
        
        st.markdown(f"""
            <div style="background: #343967; padding: 30px; border-radius: 16px; margin: 20px auto; max-width: 600px; text-align: center; border: 1px solid rgba(230, 224, 213, 0.2);">
                <div style="color: #d0c9bc; font-size: 14px; font-family: Georgia; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">
                    Your Position
                </div>
                <div style="color: #e6e0d5; font-size: 42px; font-weight: 200; font-family: Georgia; margin: 10px 0;">
                    ${position_value:,.2f}
                </div>
                <div style="color: #d0c9bc; font-size: 16px; font-family: Georgia; margin-bottom: 20px;">
                    {shares} shares at ${stock["price"]:.2f}
                </div>
                <div style="color: {change_color}; font-size: 28px; font-family: Georgia; margin-top: 10px;">
                    {sign}${abs(daily_change):,.2f}
                </div>
                <div style="color: #d0c9bc; font-size: 14px; font-family: Georgia; margin-top: 8px;">
                    Today ({sign}{stock["price_change"]:.2f}%)
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Just show price info
        st.markdown(f"""
            <div style="background: #343967; padding: 30px; border-radius: 16px; margin: 20px auto; max-width: 600px; text-align: center; border: 1px solid rgba(230, 224, 213, 0.2);">
                <div style="color: #d0c9bc; font-size: 14px; font-family: Georgia; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">
                    Current Price
                </div>
                <div style="color: #e6e0d5; font-size: 42px; font-weight: 200; font-family: Georgia; margin: 10px 0;">
                    ${stock["price"]:.2f}
                </div>
                <div style="color: {change_color}; font-size: 24px; font-family: Georgia; margin-top: 10px;">
                    {sign}${abs(price_change_dollars):.2f} ({sign}{stock["price_change"]:.2f}%)
                </div>
                <div style="color: #d0c9bc; font-size: 14px; font-family: Georgia; margin-top: 8px;">
                    Today
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="detail-score-big">
            <div class="health-score-label">Stock Health Score</div>
            <div class="detail-score-number">{stock["final_score"]}</div>
            <div class="health-score-subtext">out of 100</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Score Breakdown</div>', unsafe_allow_html=True)
    
    subscores = [
        ('Financial Health', stock['financial_health']),
        ('Profitability', stock['profitability']),
        ('Growth', stock['growth']),
        ('Momentum', stock['momentum']),
        ('Stability', stock['stability'])
    ]
    
    for label, score in subscores:
        width_pct = (score/20)*100
        st.markdown(f"""
            <div class="subscore-detail">
                <div class="subscore-detail-label">{label}</div>
                <div>
                    <span class="subscore-detail-number">{score}</span>
                    <span style="color: #6C757D; font-size: 20px;">/20</span>
                </div>
                <div class="subscore-bar" style="height: 10px; margin-top: 16px;">
                    <div class="subscore-fill" style="width: {width_pct}%"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Price Chart</div>', unsafe_allow_html=True)
    
    # Chart view toggle
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Line View", use_container_width=True, key="line_view"):
            st.session_state.chart_view = 'line'
    with col2:
        if st.button("Candle View", use_container_width=True, key="candle_view"):
            st.session_state.chart_view = 'candle'
    
    # Initialize chart view and timeframe if not set
    if 'chart_view' not in st.session_state:
        st.session_state.chart_view = 'line'
    if 'chart_timeframe' not in st.session_state:
        st.session_state.chart_timeframe = '1 Year'
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Timeframe selector
    timeframes = ["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year"]
    default_index = timeframes.index(st.session_state.chart_timeframe)
    
    timeframe = st.radio("", timeframes, horizontal=True, key="timeframe", index=default_index)
    
    # Update stored timeframe
    if timeframe != st.session_state.chart_timeframe:
        st.session_state.chart_timeframe = timeframe
    
    periods = {"1 Day": "1d", "1 Week": "5d", "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y"}
    intervals = {"1 Day": "5m", "1 Week": "15m", "1 Month": "1h", "3 Months": "1d", "6 Months": "1d", "1 Year": "1d"}
    
    ticker_obj = yf.Ticker(stock['ticker'])
    hist = ticker_obj.history(period=periods[timeframe], interval=intervals[timeframe])
    
    if not hist.empty:
        fig = go.Figure()
        
        if st.session_state.chart_view == 'line':
            # Simple line chart
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name='Price',
                line=dict(color='#343967', width=3),
                fill='tozeroy',
                fillcolor='rgba(52, 57, 103, 0.1)',
                hovertemplate='<b>%{x|%B %d, %I:%M %p}</b><br>Price: $%{y:.2f}<extra></extra>'
            ))
            
            chart_type = "Line Chart"
        else:
            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='Price',
                increasing_line_color='#10b981',
                decreasing_line_color='#ef4444',
                increasing_fillcolor='#10b981',
                decreasing_fillcolor='#ef4444',
                increasing_line_width=2,
                decreasing_line_width=2,
                hovertemplate='<b>%{x|%B %d, %I:%M %p}</b><br><br>' +
                             'Open: $%{open:.2f}<br>' +
                             'High: $%{high:.2f}<br>' +
                             'Low: $%{low:.2f}<br>' +
                             'Close: $%{close:.2f}<br>' +
                             '<extra></extra>'
            ))
            
            chart_type = "Candlestick Chart"
        
        # Add 20-day moving average only for longer timeframes
        if timeframe in ["1 Month", "3 Months", "6 Months", "1 Year"] and len(hist) >= 20:
            ma20 = hist['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=ma20,
                mode='lines',
                name='20-Day Average',
                line=dict(color='#c9a961', width=2.5),
                hovertemplate='<b>%{x|%B %d}</b><br>Average: $%{y:.2f}<extra></extra>'
            ))
        
        # Clean layout - minimal clutter
        fig.update_layout(
            height=480,
            margin=dict(l=65, r=40, t=20, b=60),
            plot_bgcolor='white',
            paper_bgcolor='#e6e0d5',
            hovermode='x unified',
            showlegend=False,
            xaxis_rangeslider_visible=False,
            font=dict(family='Georgia', color='#343967', size=14)
        )
        
        # Date format based on timeframe
        if timeframe == "1 Day":
            tickformat = '%I:%M %p'
            dtick = 3600000  # 1 hour in milliseconds
        elif timeframe == "1 Week":
            tickformat = '%b %d<br>%I:%M %p'
            dtick = None
        else:
            tickformat = '%b %d<br>%Y'
            dtick = None
        
        # Minimal x-axis
        fig.update_xaxes(
            showgrid=True,
            gridcolor='rgba(52, 57, 103, 0.05)',
            showline=True,
            linecolor='#343967',
            linewidth=1.5,
            tickformat=tickformat,
            tickfont=dict(size=11, family='Georgia', color='#343967'),
            dtick=dtick
        )
        
        # Minimal y-axis
        fig.update_yaxes(
            showgrid=True,
            gridcolor='rgba(52, 57, 103, 0.05)',
            showline=True,
            linecolor='#343967',
            linewidth=1.5,
            tickprefix='$',
            tickfont=dict(size=12, family='Georgia', color='#343967')
        )
        
        st.plotly_chart(fig, use_container_width=True)


def show_manage():
    """Manage portfolio"""
    st.markdown('<div class="welcome-title" style="text-align: center; font-size: 42px; color: #343967;">Manage Portfolio</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Initialize shares dict if not exists
        if 'shares' not in st.session_state:
            st.session_state.shares = {}
            
        st.markdown('<div class="section-header">Add Stocks</div>', unsafe_allow_html=True)
        ticker_input = st.text_input("Enter ticker", key="manage_ticker").upper()
        shares_input = st.number_input("Number of shares", min_value=0.001, value=1.0, step=0.1, format="%.3f", key="manage_shares")
        
        if st.button("Add Stock", key="add_manage", use_container_width=True):
            if ticker_input:
                if ticker_input in st.session_state.portfolio:
                    st.warning(f"{ticker_input} already in portfolio")
                else:
                    # Validate ticker first
                    with st.spinner('Validating...'):
                        try:
                            test_stock = yf.Ticker(ticker_input)
                            test_hist = test_stock.history(period="5d")
                            
                            # Check if we got valid price data
                            if test_hist.empty or len(test_hist) == 0:
                                st.error(f"Stock not available")
                            else:
                                # Stock is valid - add to portfolio with shares
                                st.session_state.portfolio.append(ticker_input)
                                st.session_state.shares[ticker_input] = shares_input
                                st.success(f"{ticker_input} added successfully")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Stock not available")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">Current Stocks</div>', unsafe_allow_html=True)
        
        for ticker in st.session_state.portfolio:
            shares = st.session_state.shares.get(ticker, 1.0)
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f'<div class="company-name" style="color: #343967;">{ticker} - {shares} shares</div>', unsafe_allow_html=True)
            with col_b:
                if st.button("Remove", key=f"remove_manage_{ticker}"):
                    st.session_state.portfolio.remove(ticker)
                    st.session_state.stock_scores = [s for s in st.session_state.stock_scores if s['ticker'] != ticker]
                    st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.screen = 'dashboard'
            st.rerun()


def main():
    if 'screen' not in st.session_state:
        st.session_state.screen = 'welcome'
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'stock_scores' not in st.session_state:
        st.session_state.stock_scores = []
    if 'selected_stock' not in st.session_state:
        st.session_state.selected_stock = None
    
    if st.session_state.screen == 'welcome':
        show_welcome()
    elif st.session_state.screen == 'add_stocks':
        show_add_stocks()
    elif st.session_state.screen == 'calculating':
        show_calculating()
    elif st.session_state.screen == 'dashboard':
        show_dashboard()
    elif st.session_state.screen == 'stock_detail':
        show_stock_detail()
    elif st.session_state.screen == 'manage':
        show_manage()


if __name__ == "__main__":
    main()
