import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="MEXC Inteligencia IA", layout="wide", initial_sidebar_state="collapsed")

# CSS para diseño profesional de 2 columnas y estados de trading
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    [data-testid="column"] { width: 49% !important; flex: 1 1 49% !important; min-width: 49% !important; }
    div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; }
    .card-pro { background-color: #161b22; border: 1px solid #30363d; border-radius: 4px; padding: 5px; margin-bottom: 2px; }
    .label-bar { font-size: 8px !important; color: #8b949e; margin-bottom: -15px; text-transform: uppercase; }
    .price-val { color: #58a6ff; font-family: monospace; font-size: 11px !important; }
    .status-active { color: #00ffcc; font-weight: bold; font-size: 10px; }
    .pnl-pos { color: #3fb950; font-weight: bold; }
    .pnl-neg { color: #f85149; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

exchange = ccxt.mexc()

# --- LÓGICA DE PERSISTENCIA DE SEÑALES ---
if 'signals' not in st.session_state:
    st.session_state.signals = {}

def get_data():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top_vol = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(9)
        symbols = list(top_vol['symbol'].values)
        if 'VEREM/USDT' not in symbols: symbols.insert(0, 'VEREM/USDT')
        
        current_data = []
        now = datetime.now()

        for sym in symbols[:10]:
            if sym in tickers:
                t = tickers[sym]
                p = t['last']
                ch = t['percentage'] or 0
                s_name = sym.replace('/USDT', '')

                # Si no existe señal para esta moneda o ya expiró (20 min), creamos una nueva
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['expires']:
                    st.session_state.signals[s_name] = {
                        'entry': p,
                        'tp': p * 1.02,
                        'sl': p * 0.99,
                        'expires': now + timedelta(minutes=20),
                        'active': False
                    }
                
                sig = st.session_state.signals[s_name]
                
                # Lógica de activación y PnL
                pnl = ((p - sig['entry']) / sig['entry']) * 100
                if abs(p - sig['entry']) / sig['entry'] < 0.001: # Si el precio toca la entrada
                    sig['active'] = True

                current_data.append({
                    "n": s_name, "p": p, "ch": ch,
                    "entry": sig['entry'], "tp": sig['tp'], "sl": sig['sl'],
                    "active": sig['active'], "pnl": pnl,
                    "soc": min(max(75 + (ch * 1.5), 20), 98),
                    "ball": 70, "imp": min(max(ch + 50, 10), 95)
                })
        return current_data
    except: return []

# --- UI ---
st.markdown("### 🤖 MEXC INTELIGENCIA IA")
data = get_data()

# RECOMENDACIÓN DESTACADA
if data:
    best = max(data, key=lambda x: x['imp'])
    status_msg = f"<span class='pnl-pos'>GANANCIA: {best['pnl']:.2f}%</span>" if best['pnl'] >= 0 else f"<span class='pnl-neg'>PÉRDIDA: {best['pnl']:.2f}%</span>"
    st.markdown(f"""
    <div style="background: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #00ffcc;">
        <b style="color:white;">🎯 TOP SEÑAL: {best['n']}</b> | ENTRADA: {best['entry']:.4f}<br>
        {status_msg if best['active'] else '⏳ ESPERANDO ENTRADA...'}
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# GRILLA 2 COLUMNAS
cols = st.columns(2)
for idx, m in enumerate(data):
    with cols[idx % 2]:
        pnl_class = "pnl-pos" if m['pnl'] >= 0 else "pnl-neg"
        st.markdown(f"""
        <div class="card-pro">
            <b style="font-size:11px;">{m['n']}</b> <span class="price-val">${m['p']}</span>
            <div style="font-size:9px; color:#00ffcc;">
                E: {m['entry']:.3f} | T: {m['tp']:.3f} | S: {m['sl']:.3f}
            </div>
            {f"<div class='{pnl_class}' style='font-size:10px;'>PNL: {m['pnl']:.2f}%</div>" if m['active'] else ""}
            <div class="label-bar">IA SOCIAL</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="label-bar">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="label-bar">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)
