"""
Mercato - Portfolio Health Analyzer
Daily portfolio scoring with beautiful blue UI
"""

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import base64
from io import BytesIO
from PIL import Image

# Page config
st.set_page_config(
    page_title="Mercato",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Blue Mercato theme
st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Main theme */
    .main {
        background-color: #f8fafc;
    }
    
    /* Welcome screen */
    .welcome-container {
        text-align: center;
        padding: 60px 20px;
    }
    
    .logo-container {
        margin: 40px 0;
    }
    
    .welcome-title {
        font-size: 48px;
        font-weight: 700;
        color: #1e3a8a;
        margin: 20px 0;
    }
    
    .welcome-subtitle {
        font-size: 24px;
        color: #64748b;
        margin: 20px 0;
        line-height: 1.6;
    }
    
    /* Portfolio Health Score - Big number */
    .health-score-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 50px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(30, 58, 138, 0.3);
        margin: 30px 0;
    }
    
    .health-score-label {
        color: #dbeafe;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 10px;
    }
    
    .health-score-number {
        color: white;
        font-size: 96px;
        font-weight: 800;
        line-height: 1;
        margin: 20px 0;
    }
    
    .health-score-subtext {
        color: #bfdbfe;
        font-size: 16px;
        margin-top: 10px;
    }
    
    /* Insight cards */
    .insight-card {
        background: white;
        padding: 20px 25px;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        margin: 15px 0;
    }
    
    .insight-text {
        color: #1e293b;
        font-size: 18px;
        line-height: 1.6;
    }
    
    /* Stock list cards */
    .stock-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        margin: 12px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stock-card:hover {
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
        transform: translateY(-2px);
    }
    
    .stock-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .stock-ticker {
        font-size: 24px;
        font-weight: 700;
        color: #1e3a8a;
    }
    
    .stock-score {
        font-size: 32px;
        font-weight: 700;
        color: #3b82f6;
    }
    
    .stock-price {
        font-size: 18px;
        color: #64748b;
        margin: 5px 0;
    }
    
    .price-change-positive {
        color: #10b981;
        font-weight: 600;
    }
    
    .price-change-negative {
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Sub-score bars */
    .subscore-container {
        margin: 8px 0;
    }
    
    .subscore-label {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 5px;
    }
    
    .subscore-bar {
        background: #e2e8f0;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .subscore-fill {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 12px 32px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
    
    /* Loading screen */
    .loading-container {
        text-align: center;
        padding: 80px 20px;
    }
    
    .loading-text {
        font-size: 28px;
        color: #1e3a8a;
        margin: 30px 0;
        font-weight: 600;
    }
    
    /* Section headers */
    .section-header {
        font-size: 24px;
        font-weight: 700;
        color: #1e3a8a;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #3b82f6;
    }
    
    /* Detail view */
    .detail-score-big {
        text-align: center;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px;
        border-radius: 16px;
        color: white;
        margin: 20px 0;
    }
    
    .detail-score-number {
        font-size: 72px;
        font-weight: 800;
        margin: 15px 0;
    }
    
    .subscore-detail {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    .subscore-detail-label {
        font-size: 18px;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 10px;
    }
    
    .subscore-detail-number {
        font-size: 36px;
        font-weight: 700;
        color: #3b82f6;
        display: inline-block;
        margin-right: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SCORING FUNCTIONS ============

def get_stock_data(ticker):
    """Get financial data for a stock"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")
        
        if hist.empty:
            return None
        
        return {
            'ticker': ticker,
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
    """Financial Health Score (0-20)"""
    scores = []
    debt_ratio = data['total_debt'] / data['market_cap'] if data['market_cap'] > 0 else 1
    # Less harsh - most companies have 0.3-0.5 debt ratio
    debt_score = max(0, min(1, 1.2 - (debt_ratio * 0.8)))
    scores.append(debt_score)
    
    cash_ratio = data['total_cash'] / data['market_cap'] if data['market_cap'] > 0 else 0
    # More generous with cash scoring
    cash_score = min(1, cash_ratio * 8)
    scores.append(cash_score)
    
    fcf_ratio = data['free_cash_flow'] / data['market_cap'] if data['market_cap'] > 0 else 0
    # More generous with FCF, add baseline
    fcf_score = min(1, max(0, (fcf_ratio * 15) + 0.3))
    scores.append(fcf_score)
    
    return np.mean(scores) * 20


def calculate_profitability(data):
    """Profitability Score (0-20)"""
    scores = []
    # More generous - 20% margin = full score
    profit_score = min(1, max(0, data['profit_margin'] * 5 + 0.2))
    scores.append(profit_score)
    
    # More generous on operating margin
    op_score = min(1, max(0, data['operating_margin'] * 4 + 0.2))
    scores.append(op_score)
    
    # More generous on ROE - 15% ROE = ~0.66 score
    roe_score = min(1, max(0, data['roe'] * 4 + 0.1))
    scores.append(roe_score)
    
    return np.mean(scores) * 20


def calculate_growth(data):
    """Growth Score (0-20)"""
    scores = []
    # More generous - 10% growth = good score
    rev_score = min(1, max(0, (data['revenue_growth'] + 0.05) * 3.5))
    scores.append(rev_score)
    
    # More generous on earnings growth
    earn_score = min(1, max(0, (data['earnings_growth'] + 0.05) * 3.5))
    scores.append(earn_score)
    
    # Give credit for consistent performance
    scores.append(0.6)
    return np.mean(scores) * 20


def calculate_momentum(data):
    """Momentum Score (0-20)"""
    try:
        hist = data['hist']
        if hist is None or hist.empty:
            return 10.0
        
        scores = []
        spy = yf.Ticker('SPY')
        spy_hist = spy.history(period='1y')
        
        if len(hist) >= 21:
            stock_1m = (hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1)
            spy_1m = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[-21] - 1)
            momentum_1m = stock_1m - spy_1m
            score_1m = min(1, max(0, (momentum_1m + 0.1) / 0.2))
            scores.append(score_1m)
        
        if len(hist) >= 63:
            stock_3m = (hist['Close'].iloc[-1] / hist['Close'].iloc[-63] - 1)
            spy_3m = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[-63] - 1)
            momentum_3m = stock_3m - spy_3m
            score_3m = min(1, max(0, (momentum_3m + 0.15) / 0.3))
            scores.append(score_3m)
        
        return np.mean(scores) * 20 if scores else 10.0
    except:
        return 10.0


def calculate_stability(data):
    """Stability Score (0-20)"""
    scores = []
    # More balanced beta scoring - beta of 1.0 = 0.65 score
    beta_score = max(0, min(1, 1.5 - (data['beta'] * 0.5))) if data['beta'] > 0 else 0.65
    scores.append(beta_score)
    
    high = data['fifty_two_week_high']
    low = data['fifty_two_week_low']
    price = data['price']
    
    if high > 0 and low > 0 and price > 0:
        volatility = (high - low) / price
        # Less harsh on volatility
        vol_score = max(0, min(1, 1.3 - (volatility / 1.5)))
        scores.append(vol_score)
    
    try:
        hist = data['hist']
        if hist is not None and not hist.empty:
            rolling_max = hist['Close'].expanding().max()
            drawdown = (hist['Close'] - rolling_max) / rolling_max
            max_dd = abs(drawdown.min())
            # Less harsh on drawdowns
            dd_score = max(0, 1 - (max_dd / 0.6))
            scores.append(dd_score)
    except:
        scores.append(0.6)
    
    return np.mean(scores) * 20


def score_stock(ticker):
    """Score a single stock"""
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
    """Calculate overall portfolio score"""
    if not stock_scores:
        return 0
    
    avg_score = np.mean([s['final_score'] for s in stock_scores])
    
    sectors = set(s['sector'] for s in stock_scores)
    num_sectors = len(sectors)
    if num_sectors <= 1:
        div_adj = 0.85
    elif num_sectors >= 5:
        div_adj = 1.0
    else:
        div_adj = 0.85 + (num_sectors - 1) * 0.0375
    
    weighted_stability = np.mean([s['stability'] for s in stock_scores])
    stab_adj = 0.9 + (weighted_stability / 20) * 0.1
    
    portfolio_score = avg_score * div_adj * stab_adj
    
    return round(portfolio_score, 1)


def generate_insights(stock_scores):
    """Generate daily insights"""
    insights = []
    
    if not stock_scores:
        return insights
    
    # Best and worst performers
    sorted_stocks = sorted(stock_scores, key=lambda x: x['final_score'], reverse=True)
    best = sorted_stocks[0]
    worst = sorted_stocks[-1]
    
    insights.append(f"{best['ticker']} is your top performer with a score of {best['final_score']}/100")
    
    if len(stock_scores) > 1:
        insights.append(f"{worst['ticker']} needs attention with a score of {worst['final_score']}/100")
    
    # Momentum check
    avg_momentum = np.mean([s['momentum'] for s in stock_scores])
    if avg_momentum > 15:
        insights.append(f"Strong momentum across your portfolio")
    elif avg_momentum < 8:
        insights.append(f"Weak momentum - market conditions unfavorable")
    
    # Price changes
    positive_movers = sum(1 for s in stock_scores if s['price_change'] > 0)
    if positive_movers == len(stock_scores):
        insights.append(f"All stocks gained value today")
    elif positive_movers > len(stock_scores) / 2:
        insights.append(f"{positive_movers} out of {len(stock_scores)} stocks gained today")
    
    return insights


# ============ SCREEN FUNCTIONS ============

def show_welcome():
    """Welcome screen - Screen 1"""
    st.markdown("""
        <div class="welcome-container">
            <div class="logo-container">
                <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDE1MCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik03NSAyMEw1MCA2MFYxMzBINzVWMTMwSDEwMFY2MEw3NSAyMFoiIGZpbGw9IiMzYjgyZjYiLz4KPHBhdGggZD0iTTM1IDQwTDIwIDYwVjEzMEgzNVYxMzBINTBWNjBMMzUgNDBaIiBmaWxsPSIjMWU2YmI0Ii8+CjxwYXRoIGQ9Ik0xMTUgNDBMMTAwIDYwVjEzMEgxMTVWMTMwSDEzMFY2MEwxMTUgNDBaIiBmaWxsPSIjNjBhNWZhIi8+Cjwvc3ZnPgo=" width="120"/>
            </div>
            <div class="welcome-title">Welcome to Mercato</div>
            <div class="welcome-subtitle">
                Mercato gives you a daily Portfolio Health Score<br/>
                based on the quality of your stocks.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Get Started", use_container_width=True):
            st.session_state.screen = 'add_stocks'
            st.rerun()


def show_add_stocks():
    """Add stocks screen - Screen 2"""
    st.markdown('<div class="welcome-title" style="text-align: center; margin-bottom: 40px;">Add Your Stocks</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        ticker_input = st.text_input("Enter stock ticker (e.g., AAPL)", key="ticker_input").upper()
        
        if st.button("➕ Add Stock", use_container_width=True):
            if ticker_input and ticker_input not in st.session_state.portfolio:
                st.session_state.portfolio.append(ticker_input)
                st.success(f"Added {ticker_input}")
                st.rerun()
            elif ticker_input in st.session_state.portfolio:
                st.warning(f"{ticker_input} already in portfolio")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Show current portfolio
        if st.session_state.portfolio:
            st.markdown('<div class="section-header">Your Portfolio</div>', unsafe_allow_html=True)
            
            for ticker in st.session_state.portfolio:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f'<div class="stock-ticker">{ticker}</div>', unsafe_allow_html=True)
                with col_b:
                    if st.button("✕", key=f"remove_{ticker}"):
                        st.session_state.portfolio.remove(ticker)
                        st.rerun()
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            if st.button("Continue →", use_container_width=True):
                if st.session_state.portfolio:
                    st.session_state.screen = 'calculating'
                    st.rerun()
                else:
                    st.warning("Add at least one stock to continue")


def show_calculating():
    """Loading screen - Screen 3"""
    st.markdown("""
        <div class="loading-container">
            <div class="loading-text">Analyzing your portfolio...</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress_bar = st.progress(0)
    
    # Calculate scores
    stock_scores = []
    total = len(st.session_state.portfolio)
    
    for i, ticker in enumerate(st.session_state.portfolio):
        progress_bar.progress((i + 1) / total)
        score = score_stock(ticker)
        if score:
            stock_scores.append(score)
    
    st.session_state.stock_scores = stock_scores
    
    # Auto-proceed to dashboard
    st.session_state.screen = 'dashboard'
    st.rerun()


def show_dashboard():
    """Main dashboard - Screen 4"""
    if not st.session_state.stock_scores:
        st.session_state.screen = 'add_stocks'
        st.rerun()
        return
    
    # Header with logo
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.markdown('<img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCAxNTAgMTUwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNNzUgMjBMNTAgNjBWMTMwSDc1VjEzMEgxMDBWNjBMNzUgMjBaIiBmaWxsPSIjM2I4MmY2Ii8+CjxwYXRoIGQ9Ik0zNSA0MEwyMCA2MFYxMzBIMzVWMTMwSDUwVjYwTDM1IDQwWiIgZmlsbD0iIzFlNmJiNCIvPgo8cGF0aCBkPSJNMTE1IDQwTDEwMCA2MFYxMzBIMTE1VjEzMEgxMzBWNjBMMTE1IDQwWiIgZmlsbD0iIzYwYTVmYSIvPgo8L3N2Zz4K" width="60"/>', unsafe_allow_html=True)
    with col_title:
        st.markdown('<div style="font-size: 32px; font-weight: 700; color: #1e3a8a; padding-top: 15px;">Mercato</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section A - Portfolio Health Score
    portfolio_score = calculate_portfolio_score(st.session_state.stock_scores)
    
    st.markdown(f"""
        <div class="health-score-container">
            <div class="health-score-label">PORTFOLIO HEALTH SCORE</div>
            <div class="health-score-number">{portfolio_score}</div>
            <div class="health-score-subtext">out of 100</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Section B - Daily Insights
    st.markdown('<div class="section-header">Daily Insights</div>', unsafe_allow_html=True)
    
    insights = generate_insights(st.session_state.stock_scores)
    for insight in insights:
        st.markdown(f'<div class="insight-card"><div class="insight-text">{insight}</div></div>', unsafe_allow_html=True)
    
    # Section C - Stock List
    st.markdown('<div class="section-header">Your Stocks</div>', unsafe_allow_html=True)
    
    # Sort by score
    sorted_stocks = sorted(st.session_state.stock_scores, key=lambda x: x['final_score'], reverse=True)
    
    for stock in sorted_stocks:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f'<div class="stock-ticker">{stock["ticker"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stock-price">${stock["price"]:.2f}</div>', unsafe_allow_html=True)
                
                change_class = "price-change-positive" if stock["price_change"] >= 0 else "price-change-negative"
                sign = "+" if stock["price_change"] >= 0 else ""
                st.markdown(f'<div class="{change_class}">{sign}{stock["price_change"]:.2f}%</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div class="stock-score">{stock["final_score"]}</div>', unsafe_allow_html=True)
            
            # Mini subscores
            cols = st.columns(5)
            subscores = [
                ('Fin', stock['financial_health']),
                ('Prof', stock['profitability']),
                ('Grow', stock['growth']),
                ('Mom', stock['momentum']),
                ('Stab', stock['stability'])
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
            
            if st.button(f"View Details →", key=f"view_{stock['ticker']}", use_container_width=True):
                st.session_state.selected_stock = stock['ticker']
                st.session_state.screen = 'stock_detail'
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    # Bottom buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add More Stocks", use_container_width=True):
            st.session_state.screen = 'manage'
            st.rerun()
    with col2:
        if st.button("🔄 Refresh Scores", use_container_width=True):
            st.session_state.screen = 'calculating'
            st.rerun()


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
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.screen = 'dashboard'
        st.rerun()
    
    # Stock header
    st.markdown(f'<div class="welcome-title" style="text-align: center;">{stock["ticker"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-subtitle" style="text-align: center;">{stock["sector"]}</div>', unsafe_allow_html=True)
    
    # Section A - Stock Health Score
    st.markdown(f"""
        <div class="detail-score-big">
            <div class="health-score-label">STOCK HEALTH SCORE</div>
            <div class="detail-score-number">{stock["final_score"]}</div>
            <div class="health-score-subtext">out of 100</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Section B - Sub-Scores
    st.markdown('<div class="section-header">Score Breakdown</div>', unsafe_allow_html=True)
    
    subscores = [
        ('Financial Health', stock['financial_health']),
        ('Profitability', stock['profitability']),
        ('Growth', stock['growth']),
        ('Momentum', stock['momentum']),
        ('Stability', stock['stability'])
    ]
    
    for label, score in subscores:
        st.markdown(f"""
            <div class="subscore-detail">
                <div class="subscore-detail-label">{label}</div>
                <div>
                    <span class="subscore-detail-number">{score}</span>
                    <span style="color: #94a3b8; font-size: 18px;">/20</span>
                </div>
                <div class="subscore-bar" style="height: 12px; margin-top: 10px;">
                    <div class="subscore-fill" style="width: {(score/20)*100}%"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Section C - Price Chart
    st.markdown('<div class="section-header">Price Chart</div>', unsafe_allow_html=True)
    
    timeframe = st.radio("Timeframe", ["1D", "1W", "1M", "6M"], horizontal=True, key="timeframe")
    
    periods = {"1D": "1d", "1W": "5d", "1M": "1mo", "6M": "6mo"}
    hist = stock['hist']
    
    if timeframe != "1D":
        ticker_obj = yf.Ticker(stock['ticker'])
        hist = ticker_obj.history(period=periods[timeframe])
    
    if not hist.empty:
        fig = go.Figure()
        
        # Main price line
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#3b82f6', width=2),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)',
            hovertemplate='<b>%{x|%b %d, %Y}</b><br>Price: $%{y:.2f}<extra></extra>'
        ))
        
        # Add volume bars if available
        if 'Volume' in hist.columns:
            fig.add_trace(go.Bar(
                x=hist.index,
                y=hist['Volume'],
                name='Volume',
                marker=dict(color='rgba(59, 130, 246, 0.3)'),
                yaxis='y2',
                hovertemplate='Volume: %{y:,.0f}<extra></extra>'
            ))
        
        # Add moving average
        if len(hist) >= 20:
            ma20 = hist['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=ma20,
                mode='lines',
                name='20-Day MA',
                line=dict(color='#f59e0b', width=1, dash='dash'),
                hovertemplate='20-Day MA: $%{y:.2f}<extra></extra>'
            ))
        
        # Update layout with better styling
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(
                showgrid=True,
                gridcolor='#f1f5f9',
                title='Date',
                titlefont=dict(size=12, color='#64748b')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#f1f5f9',
                title='Price ($)',
                titlefont=dict(size=12, color='#64748b'),
                side='left'
            ),
            yaxis2=dict(
                showgrid=False,
                side='right',
                overlaying='y',
                title='Volume',
                titlefont=dict(size=10, color='#94a3b8')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10)
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)


def show_manage():
    """Manage portfolio screen"""
    st.markdown('<div class="welcome-title" style="text-align: center;">Manage Portfolio</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Add new stocks
        st.markdown('<div class="section-header">Add Stocks</div>', unsafe_allow_html=True)
        ticker_input = st.text_input("Enter ticker", key="manage_ticker").upper()
        
        if st.button("➕ Add Stock", key="add_manage", use_container_width=True):
            if ticker_input and ticker_input not in st.session_state.portfolio:
                st.session_state.portfolio.append(ticker_input)
                st.success(f"Added {ticker_input}")
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Current stocks
        st.markdown('<div class="section-header">Current Stocks</div>', unsafe_allow_html=True)
        
        for ticker in st.session_state.portfolio:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f'<div class="stock-ticker">{ticker}</div>', unsafe_allow_html=True)
            with col_b:
                if st.button("Remove", key=f"remove_manage_{ticker}"):
                    st.session_state.portfolio.remove(ticker)
                    # Remove from scores too
                    st.session_state.stock_scores = [s for s in st.session_state.stock_scores if s['ticker'] != ticker]
                    st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.screen = 'dashboard'
            st.rerun()


# ============ MAIN APP ============

def main():
    # Initialize session state
    if 'screen' not in st.session_state:
        st.session_state.screen = 'welcome'
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'stock_scores' not in st.session_state:
        st.session_state.stock_scores = []
    if 'selected_stock' not in st.session_state:
        st.session_state.selected_stock = None
    
    # Route to appropriate screen
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
