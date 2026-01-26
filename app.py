import streamlit as st
import ccxt

st.set_page_config(page_title="IA TERMINAL V3.9", layout="wide")

# 1. ESTILOS (Sin cambios, esto siempre funciona)
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-base { background: #0d1117; border: 1px solid #30363d; padding: 10px; border-radius: 8px; border-top: 3px solid #1f6feb; }
    .sensor-bg { background: #1a1a1a; height: 8px; border-radius: 4px; margin-bottom: 6px; border: 1px solid #333; overflow: hidden; }
    .sensor-f { height: 100%; border-radius: 4px; }
    .label-s { font-size: 9px; color: #888; font-weight: bold; text-transform: uppercase; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# 2. DATOS
ASSETS = {
    'VEREM': {'t': 'IMPULSO', 's': 'AGRESIVO', 'in': 128.16, 'tgt': 132.65, 'sl': 125.80, 'n': 85, 'p': 92, 'w': 78},
    'BTC': {'t': 'WHALES', 's': 'IA EXPERTO', 'in': 87746.0, 'tgt': 90817.0, 'sl': 86166.0, 'n': 70, 'p': 45, 'w': 88},
    'ETH': {'t': 'INSTITUCIONAL', 's': 'MODO PRO', 'in': 2890.72, 'tgt': 2991.90, 'sl': 2838.69, 'n': 60, 'p': 35, 'w': 65},
    'SOL': {'t': 'FIBONACCI', 's': 'SCALPING', 'in': 122.37, 'tgt': 126.65, 'sl': 120.17, 'n': 55, 'p': 40, 'w': 50}
}

# 3. HEADER
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown('<h2 style="color:white;text-align:center;margin:0;">🛰️ TERMINAL IA ELITE | CONTROL TOTAL</h2>', unsafe_allow_html=True)
    st.markdown('<div style="background:#222;height:10px;border-radius:5px;overflow:hidden;"><div style="background:#3fb950;width:75%"></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="background:white;padding:3px;border-radius:5px;text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=REPORTE" width="60"></div>', unsafe_allow_html=True)

# 4. PRECIOS
prices = {}
try:
    mexc = ccxt.mexc({'timeout': 5000})
    ticks = mexc.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    for k, v in ticks.items(): prices[k.split('/')[0]] = v['last']
except: pass

# 5. MONEDAS (Renderizado pieza por pieza para evitar errores)
cols = st.columns(4)
for i, name in enumerate(['VEREM', 'BTC', 'ETH', 'SOL']):
    d = ASSETS[name]
    curr_p = prices.get(name, 0.0)
    pnl = ((curr_p - d['in']) / d['in'] * 100) if curr_p > 0 else 0.0
    pnl_c = "#3fb950" if pnl >= 0 else "#f85149"
    
    with cols[i]:
        # Título
        st.markdown(f'<div class="card-base"><b style="color:white;font-size:16px;">{name}</b> <span style="color:#ffca28;font-size:10px;">[{d["t"]}]</span><span style="background:#238636;color:white;font-size:9px;padding:1px 4px;border-radius:3px;float:right;">{d["s"]}</span>', unsafe_allow_html=True)
        
        # Precio
        st.markdown(f'<div style="display:flex;justify-content:space-between;margin:8px 0;"><span style="color:#58a6ff;font-size:18px;font-weight:bold;">${curr_p:,.2f}</span><span style="color:{pnl_c};font-size:14px;font-weight:bold;">{pnl:.2f}%</span></div>', unsafe_allow_html=True)
        
        # Sensores (Uno por uno)
        st.markdown(f'<div class="label-s">Noticias {d["n"]}%</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["n"]}%;background:#1f6feb;"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label-s">Impulso {d["p"]}%</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["p"]}%;background:#238636;"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label-s">Ballenas {d["w"]}%</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["w"]}%;background:#8957e5;"></div></div>', unsafe_allow_html=True)
        
        # Grilla inferior
        st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;background:#000;padding:4px;border-radius:4px;text-align:center;border:1px solid #21262d;margin-top:5px;font-size:9px;"><div style="color:white;">IN<br>{d["in"]}</div><div style="color:#3fb950;">TGT<br>{d["tgt"]}</div><div style="color:#f85149;">SL<br>{d["sl"]}</div></div></div>', unsafe_allow_html=True)

# 6. HISTORIAL LIMPIO
st.markdown('<div style="margin:10px; padding:8px; background:#161b22; border-radius:8px; border:1px solid #30363d; color:#58a6ff; font-weight:bold; font-size:12px;">📋 HISTORIAL DE OPERACIONES ACTIVAS</div>', unsafe_allow_html=True)
st.table([
    {"ACTIVO": "VEREM/USDT", "ESTRATEGIA": "AGRESIVO", "PNL": "+12.74%", "ESTADO": "TARGET 1"},
    {"ACTIVO": "BTC/USDT", "ESTRATEGIA": "IA EXPERTO", "PNL": "+3.15%", "ESTADO": "TRAILING"}
])

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="v39")
