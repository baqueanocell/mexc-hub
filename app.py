import streamlit as st
import ccxt

st.set_page_config(page_title="IA TERMINAL V4.1", layout="wide")

# --- CSS MEJORADO (Pensamiento IA + Barra Dinámica) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-base { background: #0d1117; border: 1px solid #30363d; padding: 10px; border-radius: 8px; border-top: 3px solid #1f6feb; }
    .sensor-bg { background: #1a1a1a; height: 8px; border-radius: 4px; margin-bottom: 6px; border: 1px solid #333; overflow: hidden; }
    .sensor-f { height: 100%; border-radius: 4px; }
    .label-s { font-size: 9px; color: #888; font-weight: bold; text-transform: uppercase; margin-top: 4px; }
    /* Pensamiento IA */
    .ia-thought { background: #001a00; border-left: 4px solid #00ff00; padding: 10px; color: #00ff00; font-family: monospace; font-size: 13px; margin: 10px 0; border-radius: 4px; }
    /* Barra de Rendimiento */
    .perf-container { background: #222; height: 14px; border-radius: 7px; display: flex; overflow: hidden; border: 1px solid #444; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- DATOS DEL HISTORIAL (Controlan la barra) ---
historial_data = [
    {"ACTIVO": "VEREM/USDT", "ESTRATEGIA": "AGRESIVO", "PNL": "+12.74%", "ESTADO": "TARGET 2"},
    {"ACTIVO": "BTC/USDT", "ESTRATEGIA": "IA EXPERTO", "PNL": "-3.15%", "ESTADO": "TRAILING"},
    {"ACTIVO": "SOL/USDT", "ESTRATEGIA": "SCALPING", "PNL": "+5.20%", "ESTADO": "CERRADO"},
]

# Cálculo dinámico de la barra
total_ops = len(historial_data)
ganadas = sum(1 for op in historial_data if "+" in op["PNL"])
win_rate = (ganadas / total_ops * 100) if total_ops > 0 else 50

# --- HEADER ---
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown('<h2 style="color:white;text-align:center;margin:0;font-size:24px;">🛰️ TERMINAL IA ELITE | CONTROL TOTAL</h2>', unsafe_allow_html=True)
    # Barra Dinámica
    st.markdown(f'''
        <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: bold; margin-bottom: 2px;">
            <span style="color: #3fb950;">SISTEMA WIN: {win_rate:.1f}%</span>
            <span style="color: #f85149;">SISTEMA LOSS: {100-win_rate:.1f}%</span>
        </div>
        <div class="perf-container">
            <div style="background: #3fb950; width: {win_rate}%;"></div>
            <div style="background: #f85149; width: {100-win_rate}%;"></div>
        </div>
    ''', unsafe_allow_html=True)

with c2:
    st.markdown(f'<div style="background:white;padding:3px;border-radius:5px;text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=65x65&data=REPORT_LIVE" width="65"></div>', unsafe_allow_html=True)

# --- PENSAMIENTO IA ---
st.markdown(f'''
    <div class="ia-thought">
        <b>🧠 IA PENSANDO:</b> Detectada alta presión de compra en VEREM. BTC manteniendo soporte en zona Whales. 
        Escaneando 4 activos... Sincronización con MEXC Global exitosa.
    </div>
''', unsafe_allow_html=True)

# --- PRECIOS ---
ASSETS = {
    'VEREM': {'t': 'IMPULSO', 's': 'AGRESIVO', 'in': 128.16, 'tgt': 132.65, 'sl': 125.80, 'n': 85, 'p': 92, 'w': 78},
    'BTC': {'t': 'WHALES', 's': 'IA EXPERTO', 'in': 87746.0, 'tgt': 90817.0, 'sl': 86166.0, 'n': 70, 'p': 45, 'w': 88},
    'ETH': {'t': 'INSTITUCIONAL', 's': 'MODO PRO', 'in': 2890.72, 'tgt': 2991.90, 'sl': 2838.69, 'n': 60, 'p': 35, 'w': 65},
    'SOL': {'t': 'FIBONACCI', 's': 'SCALPING', 'in': 122.37, 'tgt': 126.65, 'sl': 120.17, 'n': 55, 'p': 40, 'w': 50}
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
    pnl_c = "#3fb950" if pnl >= 0 else "#f85149"
    
    with cols[i]:
        st.markdown(f'<div class="card-base"><b style="color:white;font-size:16px;">{name}</b> <span style="color:#ffca28;font-size:10px;">[{d["t"]}]</span><span style="background:#238636;color:white;font-size:9px;padding:1px 4px;border-radius:3px;float:right;">{d["s"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;justify-content:space-between;margin:8px 0;"><span style="color:#58a6ff;font-size:18px;font-weight:bold;">${curr_p:,.2f}</span><span style="color:{pnl_c};font-size:14px;font-weight:bold;">{pnl:.2f}%</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label-s">Noticias {d["n"]}%</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["n"]}%;background:#1f6feb;"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label-s">Impulso {d["p"]}%</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["p"]}%;background:#238636;"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label-s">Ballenas {d["w"]}%</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["w"]}%;background:#8957e5;"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;background:#000;padding:4px;border-radius:4px;text-align:center;border:1px solid #21262d;margin-top:5px;font-size:9px;"><div style="color:white;">IN<br>{d["in"]}</div><div style="color:#3fb950;">TGT<br>{d["tgt"]}</div><div style="color:#f85149;">SL<br>{d["sl"]}</div></div></div>', unsafe_allow_html=True)

# --- HISTORIAL ---
st.markdown('<div style="margin:10px 0 5px 10px; color:#58a6ff; font-weight:bold; font-size:12px;">📋 HISTORIAL DE OPERACIONES ACTIVAS</div>', unsafe_allow_html=True)
st.table(historial_data)

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="v41")
