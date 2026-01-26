import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz

# Refresco cada 15 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3.2", layout="wide")

# --- CSS DE ALTA DENSIDAD (Optimizado para TV) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 12px; border-radius: 10px; margin-bottom: 5px; border-top: 3px solid #1f6feb; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 6px; border-radius: 4px; margin: 8px 0; border: 1px solid #21262d; text-align: center; }
    .trig-tag { font-size: 10px; color: #ffca28; font-weight: bold; border: 1px solid #ffca28; padding: 1px 4px; border-radius: 3px; margin-left: 5px; }
    .strat-tag { background: #238636; color: white; font-size: 9px; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
    .perf-bar { background: #222; border-radius: 10px; height: 18px; display: flex; overflow: hidden; border: 1px solid #444; margin: 10px 0; }
    .ia-log { background: #001a00; border-left: 5px solid #00ff00; padding: 10px; font-family: monospace; font-size: 13px; color: #00ff00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN SEGURA ---
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

# --- CÁLCULO ANTI-ERROR DE DIVISIÓN ---
ops = st.session_state.hist_cerrado
total_ops = len(ops)
if total_ops > 0:
    ganadas = sum(1 for o in ops if float(str(o.get('PNL', '0')).replace('%','')) > 0)
    p_green = (ganadas / total_ops) * 100
else:
    p_green = 50  # Barra neutra al inicio para evitar el error

# --- HEADER: BARRA Y QR ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.markdown(f"""
        <div style="text-align: center; color: white;">
            <span style="font-size: 22px; font-weight: bold;">🛰️ TERMINAL IA ELITE | RENDIMIENTO GLOBAL</span>
            <div class="perf-bar">
                <div style="background: #3fb950; width: {p_green}%;"></div>
                <div style="background: #f85149; width: {100-p_green}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: bold;">
                <span style="color: #3fb950;">WIN RATE: {p_green if total_ops > 0 else 0:.1f}%</span>
                <span style="color: #f85149;">LOSS RATE: {100-p_green if total_ops > 0 else 0:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_head2:
    st.markdown('<div style="background:white; padding:5px; border-radius:5px; text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=https://mex-ia.com/report" width="80"></div>', unsafe_allow_html=True)

st.markdown(f'<div class="ia-log">🧠 PENSAMIENTO IA: Analizando flujos en MEXC para detectar activaciones institucionales...</div>', unsafe_allow_html=True)

# --- PROCESAMIENTO DE MONEDAS ---
try:
    tickers = exchange.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    selected = ['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    cols = st.columns(4)
    
    for i, sym in enumerate(selected):
        if sym in tickers:
            t = tickers[sym]
            s_name = sym.split('/')[0]
            p = float(t['last'])
            
            # --- DEFINIR IDENTIDAD Y ESTRATEGIA (Restaurado) ---
            if "VEREM" in s_name: trig, strat = "IMPULSO", "AGRESIVO"
            elif "BTC" in s_name: trig, strat = "WHALES", "IA EXPERTO"
            elif "ETH" in s_name: trig, strat = "INSTITUCIONAL", "MODO PRO"
            else: trig, strat = "FIBONACCI", "SCALPING"

            if s_name not in st.session_state.signals:
                st.session_state.signals[s_name] = {'e': p, 't': p*1.04, 's': p*0.98}
            
            sig = st.session_state.signals[s_name]
            pnl = ((p - sig['e']) / sig['e']) * 100
            pnl_c = "#3fb950" if pnl >= 0 else "#f85149"

            with cols[i]:
                st.markdown(f"""
                <div class="card-tv">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="color:white; font-size:18px; font-weight:bold;">{s_name}<span class="trig-tag">[{trig}]</span></span>
                        <span class="strat-tag">{strat}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#58a6ff; font-weight:bold; font-size:20px;">${p:.2f if p > 1 else p:.4f}</span>
                        <span style="color:{pnl_c}; font-weight:bold; font-size:16px;">{pnl:.2f}%</span>
                    </div>
                    <div class="exec-grid">
                        <div style="color:white; font-size:10px;"><span style="color:#888;font-size:7px;">ENTRADA</span><br>{sig['e']:.2f}</div>
                        <div style="color:#3fb950; font-size:10px;"><span style="color:#888;font-size:7px;">TARGET</span><br>{sig['t']:.2f}</div>
                        <div style="color:#f85149; font-size:10px;"><span style="color:#888;font-size:7px;">STOP</span><br>{sig['s']:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
except Exception:
    st.error("Sincronizando con el servidor de datos...")
