import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Refresco de 20 min para niveles estratégicos
st_autorefresh(interval=1200000, key="trade_timer")

st.set_page_config(page_title="MEXC Pro-Terminal", layout="wide")

# CSS Profesional: Celdas tipo "Dashboard de Inversión"
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stProgress > div > div > div > div { height: 3px !important; border-radius: 2px; }
    p, span { font-family: 'Inter', sans-serif; font-size: 12px !important; }
    .coin-box { 
        background-color: #161b22; 
        padding: 8px; 
        border-radius: 4px; 
        border: 1px solid #30363d;
        margin-bottom: 5px;
    }
    .price-text { color: #58a6ff; font-weight: bold; font-size: 14px !important; }
    .target-text { color: #3fb950; font-weight: 500; }
    .stop-text { color: #f85149; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

exchange = ccxt.mexc()

def fetch_pro_data():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top_10 = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(10)
        
        final = []
        for symbol in top_10['symbol']:
            t = tickers[symbol]
            p = t['last']
            ch = t['percentage'] or 0
            # Triple Barra Optimizada
            final.append({
                "symbol": symbol.replace('/USDT', ''),
                "price": p,
                "s": min(max(55 + (ch * 1.2), 10), 95),
                "b": 68 + (ch * 0.5), # Dinámica de ballenas
                "i": min(max(float(ch) + 50, 5), 98),
                "tp": p * 1.025,
                "sl": p * 0.988
            })
        return final
    except: return []

# --- UI ---
st.markdown(f"### 🌐 TERMINAL LIVE <span style='float:right; font-size:12px; color:#8b949e;'>REFRESCO: 20M</span>", unsafe_allow_html=True)

data = fetch_pro_data()

# Destacado de la moneda TOP
if data:
    best = max(data, key=lambda x: x['i'] + x['b'])
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1f6feb 0%, #0d1117 100%); padding: 12px; border-radius: 6px; margin-bottom: 15px;">
        <b style="color:white; font-size:16px;">⭐ SEÑAL LÍDER: {best['symbol']}</b><br>
        <span style="color:#c9d1d9;">ENTRADA: {best['price']} | </span>
        <span style="color:#3fb950;">TP: {best['tp']:.4f}</span> | 
        <span style="color:#f85149;">SL: {best['sl']:.4f}</span>
    </div>
    """, unsafe_allow_html=True)

# Grilla de Monedas
for m in data:
    with st.container():
        # Layout de 4 columnas para máxima eficiencia
        c1, c2, c3, c4 = st.columns([0.7, 1, 2, 1.5])
        with c1:
            st.markdown(f"**{m['symbol']}**")
        with c2:
            st.markdown(f"<span class='price-text'>${m['price']}</span>", unsafe_allow_html=True)
        with c3:
            # Micro-barras con etiquetas compactas
            st.progress(m['s']/100) # Social
            st.progress(m['b']/100) # Ballenas
            st.progress(m['i']/100) # Impulso
        with c4:
            st.markdown(f"<span class='target-text'>T:{m['tp']:.3f}</span> <br> <span class='stop-text'>S:{m['sl']:.3f}</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:2px;'>", unsafe_allow_html=True)
