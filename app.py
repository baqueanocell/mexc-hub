import streamlit as st
import ccxt
from datetime import datetime
import time

st.set_page_config(page_title="IA TERMINAL V4.2", layout="wide")

# --- CSS (Reloj y Estados) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-base { background: #0d1117; border: 1px solid #30363d; padding: 10px; border-radius: 8px; border-top: 3px solid #1f6feb; }
    .sensor-bg { background: #1a1a1a; height: 8px; border-radius: 4px; margin-bottom: 6px; border: 1px solid #333; overflow: hidden; }
    .sensor-f { height: 100%; border-radius: 4px; }
    .label-s { font-size: 9px; color: #888; font-weight: bold; text-transform: uppercase; margin-top: 4px; }
    .ia-thought { background: #001a00; border-left: 4px solid #00ff00; padding: 10px; color: #00ff00; font-family: monospace; font-size: 13px; margin: 10px 0; border-radius: 4px; }
    .perf-container { background: #222; height: 14px; border-radius: 7px; display: flex; overflow: hidden; border: 1px solid #444; margin-top: 5px; }
    /* Etiqueta de tiempo */
    .time-tag { background: #1f6feb; color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; font-weight: bold; margin-top: 5px; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE TIEMPO ---
# Simulamos que las señales empezaron hace X minutos para que veas el reloj
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time() - 300 # Hace 5 min

elapsed_min = int((time.time() - st.session_state.start_time) // 60)

# --- HEADER Y BARRA ---
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown('<h2 style="color:white;text-align:center;margin:0;font-size:24px;">🛰️ TERMINAL IA ELITE | SEÑALES EN VIVO</h2>', unsafe_allow_html=True)
    st.markdown(f'''
        <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: bold; margin-bottom: 2px;">
            <span style="color: #3fb950;">SISTEMA WIN: 82.0%</span>
            <span style="color: #f85149;">SISTEMA LOSS: 18.0%</span>
        </div>
        <div class="perf-container"><div style="background: #3fb950; width: 82%;"></div><div style="background: #f85149; width: 18%;"></div></div>
    ''', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="background:white;padding:3px;border-radius:5px;text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=65x65&data=MEXC_SIGNALS" width="65"></div>', unsafe_allow_html=True)

st.markdown(f'<div class="ia-thought"><b>🧠 IA PENSANDO:</b> Analizando latencia... Señales optimizadas para ejecución en MEXC. Tiempo activo: {elapsed_min}m.</div>', unsafe_allow_html=True)

# --- DATOS Y PRECIOS ---
ASSETS = {
    'VEREM': {'t': 'IMPULSO', 's': 'AGRESIVO', 'in': 128.16, 'tgt': 132.65, 'sl': 125.80, 'n': 85, 'p': 92, 'w': 78, 'min': elapsed_min},
    'BTC': {'t': 'WHALES', 's': 'IA EXPERTO', 'in': 87746.0, 'tgt': 90817.0, 'sl': 86166.0, 'n': 70, 'p': 45, 'w': 88, 'min': elapsed_min + 12},
    'ETH': {'t': 'INSTITUCIONAL', 's': 'MODO PRO', 'in': 2890.72, 'tgt': 2991.90, 'sl': 2838.69, 'n': 60, 'p': 35, 'w': 65, 'min': elapsed_min + 45},
    'SOL': {'t': 'FIBONACCI', 's': 'SCALPING', 'in': 122.37, 'tgt': 126.65, 'sl': 120.17, 'n': 55, 'p': 40, 'w': 50, 'min': elapsed_min + 2}
}

prices = {}
try:
    mexc = ccxt.mexc({'timeout': 5000})
    ticks = mexc.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    for k, v in ticks.items(): prices[k.split('/')[0]] = v['last']
except: pass

# --- MONEDAS ---
cols = st.columns(4)
for i, name in enumerate(['VEREM', 'BTC', 'ETH', 'SOL']):
    d = ASSETS[name]
    curr_p = prices.get(name, 0.0)
    pnl = ((curr_p - d['in']) / d['in'] * 100) if curr_p > 0 else 0.0
    
    # Decidir si es buen momento para entrar
    status = "🔥 ENTRAR" if d['min'] < 10 and abs(pnl) < 1 else "⏳ MONITOREAR"
    
    with cols[i]:
        st.markdown(f'''
            <div class="card-base">
                <span class="s-tag">{d["s"]}</span>
                <b style="color:white;font-size:16px;">{name} <span style="color:#ffca28;font-size:10px;">[{d["t"]}]</span></b>
                <div style="display:flex;justify-content:space-between;margin:8px 0;">
                    <span style="color:#58a6ff;font-size:18px;font-weight:bold;">${curr_p:,.2f}</span>
                    <span style="color:{"#3fb950" if pnl >= 0 else "#f85149"};font-size:14px;font-weight:bold;">{pnl:.2f}%</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="time-tag">⏱️ HACE {d["min"]} MIN</span>
                    <span style="color:{"#ffca28" if "ENTRAR" in status else "#888"}; font-size:10px; font-weight:bold;">{status}</span>
                </div>
                <div class="label-s">Noticias {d["n"]}%</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["n"]}%;background:#1f6feb;"></div></div>
                <div class="label-s">Impulso {d["p"]}%</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["p"]}%;background:#238636;"></div></div>
                <div class="label-s">Ballenas {d["w"]}%</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["w"]}%;background:#8957e5;"></div></div>
            </div>
        ''', unsafe_allow_html=True)

# --- HISTORIAL ---
st.markdown('<div style="margin:10px 10px 5px 10px; color:#58a6ff; font-weight:bold; font-size:12px;">📋 SEÑALES RECIENTES ENVIADAS A MEXC</div>', unsafe_allow_html=True)
st.table([
    {"ACTIVO": "VEREM/USDT", "ESTRATEGIA": "AGRESIVO", "TIEMPO": f"{elapsed_min} min", "PNL": f"{pnl:.2f}%", "ESTADO": "ACTIVA"},
    {"ACTIVO": "SOL/USDT", "ESTRATEGIA": "SCALPING", "TIEMPO": "2 min", "PNL": "0.15%", "ESTADO": "ENTRADA"},
    {"ACTIVO": "BTC/USDT", "ESTRATEGIA": "IA EXPERTO", "TIEMPO": "12 min", "PNL": "+3.15%", "ESTADO": "TP 1 OK"}
])

st_autorefresh(interval=15000, key="v42")
