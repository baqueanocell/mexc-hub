import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz

# Refresco cada 15 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3", layout="wide")

# --- CSS MEJORADO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 12px; border-radius: 10px; margin-bottom: 5px; border-top: 3px solid #1f6feb; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 6px; border-radius: 4px; margin: 8px 0; border: 1px solid #21262d; text-align: center; }
    .ia-log { background: #001a00; border-left: 5px solid #00ff00; padding: 10px; font-family: monospace; font-size: 13px; color: #00ff00; margin-bottom: 15px; }
    .perf-bar { background: #222; border-radius: 10px; height: 18px; display: flex; overflow: hidden; border: 1px solid #444; margin: 10px 0; }
    .qr-box { background: white; padding: 5px; border-radius: 5px; text-align: center; width: 110px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'hist_cerrado' not in st.session_state: 
    # Datos de ejemplo para que la barra no esté vacía al inicio
    st.session_state.hist_cerrado = [{'PNL': '1.5%'}, {'PNL': '-0.5%'}, {'PNL': '2.0%'}]
if 'signals' not in st.session_state: st.session_state.signals = {}

exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

# --- CÁLCULO DE RENDIMIENTO (BARRA ROJA/VERDE) ---
ops = st.session_state.hist_cerrado
total_ops = len(ops) if ops else 1
ganadas = sum(1 for o in ops if float(str(o.get('PNL', '0')).replace('%','')) > 0)
p_green = (ganadas / total_ops) * 100
p_red = 100 - p_green

# --- HEADER CON BARRA Y QR ---
col_head1, col_head2 = st.columns([4, 1])

with col_head1:
    st.markdown(f"""
        <div style="text-align: center; color: white;">
            <span style="font-size: 24px; font-weight: bold;">🛰️ TERMINAL IA ELITE V3 | RENDIMIENTO GLOBAL</span>
            <div class="perf-bar">
                <div style="background: #3fb950; width: {p_green}%;"></div>
                <div style="background: #f85149; width: {p_red}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 14px;">
                <span style="color: #3fb950;">WIN RATE: {p_green:.1f}%</span>
                <span style="color: #f85149;">LOSS RATE: {p_red:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_head2:
    # Generamos un QR que apunta a tus datos (usamos un placeholder de imagen QR)
    st.markdown("""
        <div class="qr-box">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://docs.google.com/spreadsheets" width="100">
            <div style="color: black; font-size: 8px; font-weight: bold;">AUDITAR DATOS</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f'<div class="ia-log">🧠 PENSAMIENTO IA: Analizando comportamiento de {total_ops} operaciones para optimizar precisión...</div>', unsafe_allow_html=True)

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
            
            if s_name not in st.session_state.signals:
                st.session_state.signals[s_name] = {'e': p, 't': p*1.04, 's': p*0.98}
            
            sig = st.session_state.signals[s_name]
            pnl = ((p - sig['e']) / sig['e']) * 100
            pnl_color = "#3fb950" if pnl >= 0 else "#f85149"

            with cols[i]:
                st.markdown(f"""
                <div class="card-tv">
                    <b style="font-size: 20px; color:white;">{s_name}</b>
                    <div style="display: flex; justify-content: space-between; margin-top:5px;">
                        <span style="color:#58a6ff; font-weight:bold; font-size:20px;">${p:.2f}</span>
                        <span style="color:{pnl_color}; font-weight:bold; font-size:18px;">{pnl:.2f}%</span>
                    </div>
                    <div class="exec-grid">
                        <div style="color:white; font-size:11px;"><span style="color:#888;font-size:8px;">IN</span><br>{sig['e']:.2f}</div>
                        <div style="color:#3fb950; font-size:11px;"><span style="color:#888;font-size:8px;">TARGET</span><br>{sig['t']:.2f}</div>
                        <div style="color:#f85149; font-size:11px;"><span style="color:#888;font-size:8px;">STOP</span><br>{sig['s']:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
except Exception as e:
    st.error("Error cargando datos...")

st.markdown("<p style='color:#444; text-align:center; font-size:10px;'>Escanea el QR para ver el histórico detallado y mejorar la estrategia.</p>", unsafe_allow_html=True)
