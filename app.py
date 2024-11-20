import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Configure page settings
st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for better appearance
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize exchange in session state
if 'exchange' not in st.session_state:
    st.session_state.exchange = ccxt.binance({'enableRateLimit': True})

# Cache the data fetching function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_crypto_data(symbol, timeframe='1d', limit=90):
    """Fetch cryptocurrency OHLCV data with caching"""
    try:
        ohlcv = st.session_state.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def format_price(price):
    """Format price with appropriate decimals"""
    if price >= 1000:
        return f"${price:,.2f}"
    else:
        return f"${price:.4f}"

def main():
    st.title("🚀 Cryptocurrency Dashboard")
    
    # Sidebar controls
    st.sidebar.header("📊 Dashboard Settings")
    
    # Add refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.experimental_rerun()
    
    days = st.sidebar.selectbox(
        "📅 Select Time Period",
        options=[7, 30, 90],
        default=30
    )
    
    # Add loading animation
    with st.spinner('📊 Loading market data...'):
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        crypto_data = {}
        
        # Fetch data for all symbols
        for symbol in symbols:
            df = fetch_crypto_data(symbol, limit=days)
            if df is not None:
                crypto_data[symbol] = df
    
    # Create price chart
    fig = go.Figure()
    
    colors = {
        'BTC/USDT': '#f7931a',
        'ETH/USDT': '#62688f',
        'SOL/USDT': '#00ff9d'
    }
    
    for symbol, df in crypto_data.items():
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['close'],
                name=symbol.split('/')[0],
                line=dict(color=colors[symbol]),
                fill='tonexty',
                fillcolor=f"rgba{tuple(list(int(colors[symbol].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}"
            )
        )
    
    fig.update_layout(
        title="Cryptocurrency Prices",
        xaxis_title="Date",
        yaxis_title="Price (USDT)",
        hovermode='x unified',
        height=600,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Display chart with loading state
    chart_placeholder = st.empty()
    with st.spinner('📈 Updating chart...'):
        chart_placeholder.plotly_chart(fig, use_container_width=True)
    
    # Display metrics
    st.header("📊 Market Overview")
    col1, col2, col3 = st.columns(3)
    
    for symbol, df in crypto_data.items():
        current_price = df['close'].iloc[-1]
        price_change = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
        daily_high = df['high'].iloc[-1]
        daily_low = df['low'].iloc[-1]
        
        if symbol == 'BTC/USDT':
            with col1:
                st.metric("Bitcoin", 
                         format_price(current_price),
                         f"{price_change:+.2f}%")
                st.caption(f"24h High: {format_price(daily_high)}")
                st.caption(f"24h Low: {format_price(daily_low)}")
        elif symbol == 'ETH/USDT':
            with col2:
                st.metric("Ethereum",
                         format_price(current_price),
                         f"{price_change:+.2f}%")
                st.caption(f"24h High: {format_price(daily_high)}")
                st.caption(f"24h Low: {format_price(daily_low)}")
        else:
            with col3:
                st.metric("Solana",
                         format_price(current_price),
                         f"{price_change:+.2f}%")
                st.caption(f"24h High: {format_price(daily_high)}")
                st.caption(f"24h Low: {format_price(daily_low)}")
    
    # Add last updated timestamp
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()