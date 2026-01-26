import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz

# Refresco cada 15 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3.4", layout="wide")

# --- CSS DE ALTA VISIBILIDAD ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 12px; border-top: 4px solid #1f6feb; margin-bottom: 10px; min-height: 180px; }
    .trig-tag { font-size: 12px; color: #ffca28; font-weight: bold; border: 1px solid #ffca28; padding: 2px 5px; border-radius: 4px; margin-left: 8px; }
    .strat-tag { background: #238636; color: white; font-size: 11px; padding: 3px 8px; border-radius: 5px; font-weight: bold; float: right; }
    .perf-bar { background: #222; border-radius: 10px; height: 20px; display: flex; overflow: hidden; border: 1px solid #444; margin: 10px 0; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 8px; border-radius: 6px; margin-top: 15px; border: 1px solid #21262d; text-align: center; }
    .ia-log { background: #001a00; border-left: 5px solid #00ff00; padding: 12px; font-family: monospace; font-size: 14px; color: #00ff00; margin-bottom: 10px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

# Conexión optimizada
exchange = ccxt.mexc({'timeout': 60000, 'enableRateLimit': True})
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

# --- HEADER: RENDIMIENTO Y QR ---
ops = st.session_state.hist_cerrado
total = len(ops)
p_green = (sum(1 for o in ops if float(str(o.get('PNL','0')).replace('%','')) > 0) / total * 100) if total > 0 else 50

h1, h2 = st.columns([4, 1])
with h1:
    st.markdown(f"""
        <div style="text-align: center; color: white;">
            <span style="font-size: 26px; font-weight: bold;">🛰️ IA TERMINAL ELITE | SISTEMA ACTIVO</span>
            <div class="perf-bar"><div style="background: #3fb950; width: {p_green}%;"></div><div style="background: #f85149; width: {100-p_green}%;"></div></div>
            <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: bold;">
                <span style="color: #3fb950;">WIN RATE: {p_green if total > 0 else 0:.1f}%</span>
                <span style="color: #f85149;">LOSS RATE: {100-p_green if total > 0 else 0:.1f}%</span>
            </div>
        </div>""", unsafe_allow_html=True)
with h2:
    st.markdown('<div style="background:white; padding:5px; border-radius:8px; text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=90x90&data=ANALISIS_IA_MOVIL" width="90"></div>', unsafe_allow_html=True)

st.markdown(f'<div class="ia-log">🧠 PENSAMIENTO IA: Escaneando bloques en MEXC... Monitoreo en tiempo real activado.</div>', unsafe_allow_html=True)

# --- RENDERIZADO DE CUADROS (FUERA DEL TRY PARA FORZAR APARICIÓN) ---
coins = ['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT']
cols = st.columns(4)

try:
    tickers = exchange.fetch_tickers(coins)
except:
    tickers = {}

for i, sym in enumerate(coins):
    s_name = sym.split('/')[0]
    # Datos por defecto si falla la conexión momentáneamente
    p = float(tickers[sym]['last']) if sym in tickers else 0.0
    
    # Estrategias Fijas
    if "VEREM" in s_name: trig, strat = "IMPULSO", "AGRESIVO"
    elif "BTC" in s_name: trig, strat = "WHALES", "IA EXPERTO"
    elif "ETH" in s_name: trig, strat = "INSTITUCIONAL", "MODO PRO"
    else: trig, strat = "FIBONACCI", "SCALPING"

    if s_name not in st.session_state.signals:
        st.session_state.signals[s_name] = {'e': p if p > 0 else 100.0, 't': p*1.04 if p > 0 else 104.0, 's': p*0.98 if p > 0 else 98.0}
    
    sig = st.session_state.signals[s_name]
    pnl = ((p - sig['e']) / sig['e']) * 100 if p > 0 else 0.0
    p_col = "#3fb950" if pnl >= 0 else "#f85149"

    with cols[i]:
        st.markdown(f"""
        <div class="card-tv">
            <div>
                <span class="strat-tag">{strat}</span>
                <span style="color:white; font-size:22px; font-weight:bold;">{s_name}<span class="trig-tag">[{trig}]</span></span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                <span style="color:#58a6ff; font-weight:bold; font-size:24px;">${p:.2f if p > 1 else p:.4f}</span>
                <span style="color:{p_col}; font-weight:bold; font-size:20px;">{pnl:.2f}%</span>
            </div>
            <div class="exec-grid">
                <div style="color:white; font-size:12px;"><span style="color:#888;font-size:9px;">ENTRADA</span><br>{sig['e']:.2f}</div>
                <div style="color:#3fb950; font-size:12px;"><span style="color:#888;font-size:9px;">TARGET</span><br>{sig['t']:.2f}</div>
                <div style="color:#f85149; font-size:12px;"><span style="color:#888;font-size:9px;">STOP</span><br>{sig['s']:.2f}</div>
            </div>
        </div>""", unsafe_allow_html=True)

if not tickers:
    st.warning("⚠️ Sincronizando precios... los cuadros se actualizarán en breve.")
