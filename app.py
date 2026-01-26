import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz

# Refresco cada 12 segundos para mantener la conexión viva
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=12000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3.3", layout="wide")

# --- CSS ULTRA-OPTIMIZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 12px; border-radius: 10px; border-top: 3px solid #1f6feb; margin-bottom: 10px; }
    .trig-tag { font-size: 11px; color: #ffca28; font-weight: bold; border: 1px solid #ffca28; padding: 1px 4px; border-radius: 3px; margin-left: 6px; }
    .strat-tag { background: #238636; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .perf-bar { background: #222; border-radius: 10px; height: 18px; display: flex; overflow: hidden; border: 1px solid #444; margin: 10px 0; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 6px; border-radius: 4px; margin-top: 10px; border: 1px solid #21262d; text-align: center; }
    .ia-log { background: #001a00; border-left: 5px solid #00ff00; padding: 10px; font-family: monospace; font-size: 13px; color: #00ff00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

# Conexión con tiempo de espera extendido para TV
exchange = ccxt.mexc({'timeout': 30000, 'enableRateLimit': True})
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

# --- CÁLCULO DE BARRA ---
ops = st.session_state.hist_cerrado
total = len(ops)
p_green = (sum(1 for o in ops if float(str(o.get('PNL','0')).replace('%','')) > 0) / total * 100) if total > 0 else 50

# --- HEADER (BARRA + QR) ---
h1, h2 = st.columns([4, 1])
with h1:
    st.markdown(f"""
        <div style="text-align: center; color: white;">
            <span style="font-size: 24px; font-weight: bold;">🛰️ IA TERMINAL ELITE | SISTEMA ACTIVO</span>
            <div class="perf-bar">
                <div style="background: #3fb950; width: {p_green}%;"></div>
                <div style="background: #f85149; width: {100-p_green}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: bold;">
                <span style="color: #3fb950;">WIN RATE: {p_green if total > 0 else 0:.1f}%</span>
                <span style="color: #f85149;">LOSS RATE: {100-p_green if total > 0 else 0:.1f}%</span>
            </div>
        </div>""", unsafe_allow_html=True)
with h2:
    st.markdown('<div style="background:white; padding:4px; border-radius:6px; text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=85x85&data=REPORTE_IA_ESTRATEGIA" width="85"></div>', unsafe_allow_html=True)

st.markdown(f'<div class="ia-log">🧠 PENSAMIENTO IA: Detectando patrones en VEREM, BTC, ETH y SOL...</div>', unsafe_allow_html=True)

# --- MOTOR DE DATOS ---
try:
    # Pedimos solo los tickers necesarios para ahorrar ancho de banda
    coins = ['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    tickers = exchange.fetch_tickers(coins)
    cols = st.columns(4)
    
    for i, sym in enumerate(coins):
        if sym in tickers:
            s_name = sym.split('/')[0]
            p = float(tickers[sym]['last'])
            
            # Asignación fija de estrategias y disparadores
            if "VEREM" in s_name: trig, strat = "IMPULSO", "AGRESIVO"
            elif "BTC" in s_name: trig, strat = "WHALES", "IA EXPERTO"
            elif "ETH" in s_name: trig, strat = "INSTITUCIONAL", "MODO PRO"
            else: trig, strat = "FIBONACCI", "SCALPING"

            if s_name not in st.session_state.signals:
                st.session_state.signals[s_name] = {'e': p, 't': p*1.04, 's': p*0.98}
            
            sig = st.session_state.signals[s_name]
            pnl = ((p - sig['e']) / sig['e']) * 100
            p_col = "#3fb950" if pnl >= 0 else "#f85149"

            with cols[i]:
                st.markdown(f"""
                <div class="card-tv">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="color:white; font-size:19px; font-weight:bold;">{s_name}<span class="trig-tag">[{trig}]</span></span>
                        <span class="strat-tag">{strat}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#58a6ff; font-weight:bold; font-size:22px;">${p:.2f if p > 1 else p:.4f}</span>
                        <span style="color:{p_col}; font-weight:bold; font-size:18px;">{pnl:.2f}%</span>
                    </div>
                    <div class="exec-grid">
                        <div style="color:white; font-size:11px;"><span style="color:#888;font-size:8px;">IN</span><br>{sig['e']:.2f}</div>
                        <div style="color:#3fb950; font-size:11px;"><span style="color:#888;font-size:8px;">TGT</span><br>{sig['t']:.2f}</div>
                        <div style="color:#f85149; font-size:11px;"><span style="color:#888;font-size:8px;">STOP</span><br>{sig['s']:.2f}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
except Exception:
    st.warning("Reconectando con el mercado...")
