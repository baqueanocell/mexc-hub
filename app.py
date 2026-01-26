import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Refresco cada 20 min para niveles de trading
st_autorefresh(interval=1200000, key="trade_timer")

st.set_page_config(page_title="MEXC Pro Terminal", layout="wide")

# CSS para convertir la app en una grilla compacta
st.markdown("""
    <style>
    .main { background-color: #080a0f; }
    /* Barras ultra delgadas */
    .stProgress > div > div > div > div { height: 2px !important; }
    /* Texto tipo terminal */
    p, span, div { font-family: 'Roboto Mono', monospace; font-size: 11px !important; color: #848e9c !important; }
    .coin-name { font-size: 14px !important; color: #ffffff !important; font-weight: bold; }
    .price-up { color: #00ffcc !important; font-weight: bold; }
    /* Quitar espacios innecesarios */
    .block-container { padding: 1rem !important; }
    hr { margin: 0.3rem 0px !important; border-top: 1px solid #1e2329; }
    </style>
    """, unsafe_allow_html=True)

exchange = ccxt.mexc()

def get_market_data():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top_10 = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(10)
        
        results = []
        for symbol in top_10['symbol']:
            t = tickers[symbol]
            p = t['last']
            change = t['percentage'] or 0
            # Simulación inteligente de barras
            s = min(max(50 + (change * 1.5), 10), 95)
            i = min(max(float(change) + 50, 5), 95)
            
            # Niveles de Trading
            results.append({
                "sym": symbol.replace('/USDT', ''), "price": p,
                "sent": s, "ball": 70, "imp": i,
                "tp": p * 1.02, "sl": p * 0.99
            })
        return results
    except: return []

# --- ENCABEZADO ---
st.markdown(f"### ⚡ MEXC INTELLIGENCE HUB <span style='float:right; font-size:10px;'>{datetime.now().strftime('%H:%M')}</span>", unsafe_allow_html=True)

data = get_market_data()

# --- MEJOR OPORTUNIDAD (DESTACADA) ---
if data:
    best = max(data, key=lambda x: x['imp'])
    with st.container():
        st.markdown(f"""
        <div style="background-color: #1e2329; padding: 10px; border-radius: 5px; border-left: 4px solid #00ffcc;">
            <span style="color: #00ffcc;">🔥 ALERTA TOP: {best['sym']}</span><br>
            <span>ENTRADA: {best['price']} | <b>TP: {best['tp']:.4f}</b> | SL: {best['sl']:.4f}</span>
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# --- GRILLA DE 10 RECTÁNGULOS ---
for m in data:
    # Cada moneda es un "rectángulo" compacto
    col_name, col_price, col_bars, col_targets = st.columns([0.8, 1, 2, 1.5])
    
    with col_name:
        st.markdown(f"<span class='coin-name'>{m['sym']}</span>", unsafe_allow_html=True)
    
    with col_price:
        st.markdown(f"<span class='price-up'>${m['price']}</span>", unsafe_allow_html=True)
        
    with col_bars:
        # Tres micro-barras en una sola columna para ahorrar espacio
        st.progress(m['sent']/100)
        st.progress(m['ball']/100)
        st.progress(m['imp']/100)
        
    with col_targets:
        st.markdown(f"T: {m['tp']:.2f} | S: {m['sl']:.2f}", unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
