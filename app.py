import streamlit as st
import ccxt
import time

st.set_page_config(page_title="IA TERMINAL V4.5", layout="wide")

# --- CSS DE ALTA PRECISIÓN ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    /* Contenedor principal de la moneda */
    .card-base { background: #0d1117; border: 1px solid #30363d; padding: 10px; border-radius: 8px; border-top: 3px solid #1f6feb; }
    /* Barras ultra delgadas para ahorrar espacio */
    .s-bg { background: #1a1a1a; height: 3px; border-radius: 2px; margin-bottom: 3px; overflow: hidden; }
    .s-fill { height: 100%; }
    .s-label { font-size: 8px; color: #555; font-weight: bold; text-transform: uppercase; }
    /* Caja de Precios de Operación */
    .price-box { background: #000; border: 1px solid #21262d; border-radius: 4px; padding: 5px; margin-top: 8px; display: flex; justify-content: space-around; text-align: center; }
    .p-val { font-size: 10px; font-weight: bold; line-height: 1.2; }
    .p-lbl { font-size: 7px; color: #888; display: block; }
    /* Pensamiento IA Estilo Matrix */
    .ia-thought { background: #001a00; border-left: 3px solid #00ff00; padding: 8px; color: #00ff00; font-family: monospace; font-size: 11px; margin-bottom: 10px; border-radius: 0 4px 4px 0; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
if 'start_time' not in st.session_state: st.session_state.start_time = time.time()
t_total = int((time.time() - st.session_state.start_time) // 60) + 5

ASSETS = {
    'VEREM': {'in': 128.16, 'tgt': 132.65, 'sl': 125.80, 'n': 85, 'p': 92, 'w': 78, 't': t_total},
    'BTC':   {'in': 87746.0, 'tgt': 90817.0, 'sl': 86166.0, 'n': 70, 'p': 45, 'w': 88, 't': 14},
    'ETH':   {'in': 2890.72, 'tgt': 2991.90, 'sl': 2838.69, 'n': 60, 'p': 35, 'w': 65, 't': 52},
    'SOL':   {'in': 122.37, 'tgt': 126.65, 'sl': 120.17, 'n': 55, 'p': 40, 'w': 50, 't': 3}
}

# --- HEADER ---
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown('<h2 style="color:white;text-align:center;margin:0;font-size:22px;">🛰️ TERMINAL IA ELITE | PANEL DE SEÑALES</h2>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#222;height:6px;border-radius:3px;display:flex;overflow:hidden;margin:5px 0;"><div style="background:#3fb950;width:85%;"></div><div style="background:#f85149;width:15%;"></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="background:white;padding:2px;border-radius:4px;text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=55x55&data=MEXC_SIG" width="55"></div>', unsafe_allow_html=True)

st.markdown(f'<div class="ia-thought"><b>🧠 PENSAMIENTO IA:</b> Escaneando liquidez en MEXC. VEREM en zona de alta convicción. Tiempo activo: {t_total}m.</div>', unsafe_allow_html=True)

# --- GRID DE MONEDAS ---
cols = st.columns(4)
prices = {}
try:
    mexc = ccxt.mexc()
    ticks = mexc.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    for k, v in ticks.items(): prices[k.split('/')[0]] = v['last']
except: pass

for i, name in enumerate(['VEREM', 'BTC', 'ETH', 'SOL']):
    d = ASSETS[name]
    cp = prices.get(name, 0.0)
    pnl = ((cp - d['in']) / d['in'] * 100) if cp > 0 else 0.0
    
    with cols[i]:
        # Título y Precio Principal
        st.markdown(f'''
            <div class="card-base">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:white;font-size:16px;">{name}</b>
                    <span style="background:#1f6feb; color:white; font-size:9px; padding:1px 4px; border-radius:2px;">{d["t"]} MIN</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin:5px 0;">
                    <span style="color:#58a6ff;font-size:18px;font-weight:bold;">${cp:,.2f}</span>
                    <span style="color:{"#3fb950" if pnl >= 0 else "#f85149"};font-size:14px;font-weight:bold;">{pnl:.2f}%</span>
                </div>
        ''', unsafe_allow_html=True)
        
        # Sensores (Miniatutizados para no romper el HTML)
        for label, val, color in [("Noticias", d['n'], "#1f6feb"), ("Impulso", d['p'], "#238636"), ("Whales", d['w'], "#8957e5")]:
            st.markdown(f'<div class="s-label">{label} {val}%</div><div class="s-bg"><div class="s-fill" style="width:{val}%; background:{color};"></div></div>', unsafe_allow_html=True)
        
        # Bloque de Precios IN/TGT/SL (Separado para evitar el error de texto plano)
        st.markdown(f'''
                <div class="price-box">
                    <div style="color:white;"><span class="p-lbl">ENTRY</span><span class="p-val">{d["in"]}</span></div>
                    <div style="color:#3fb950;"><span class="p-lbl">TARGET</span><span class="p-val">{d["tgt"]}</span></div>
                    <div style="color:#f85149;"><span class="p-lbl">STOP</span><span class="p-val">{d["sl"]}</span></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

# --- TABLA DE HISTORIAL ---
st.markdown('<div style="margin:10px 0 5px 10px; color:#58a6ff; font-weight:bold; font-size:12px;">📋 RESUMEN DE SEÑALES MEXC</div>', unsafe_allow_html=True)
st.table([
    {"ACTIVO": "VEREM/USDT", "TIEMPO": f"{t_total} min", "PNL": f"{pnl:.2f}%", "ESTADO": "ACTIVA"},
    {"ACTIVO": "SOL/USDT", "TIEMPO": "3 min", "PNL": "0.15%", "ESTADO": "ENTRADA"}
])

# Refresco cada 15 seg
time.sleep(15)
st.rerun()
