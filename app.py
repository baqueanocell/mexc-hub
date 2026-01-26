import streamlit as st
import ccxt

st.set_page_config(page_title="IA TERMINAL V3.8", layout="wide")

# --- CSS DEFINITIVO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card { background: #0d1117; border: 1px solid #30363d; padding: 12px; border-radius: 10px; border-top: 4px solid #1f6feb; margin-bottom: 8px; }
    .t-tag { color: #ffca28; font-size: 10px; font-weight: bold; border: 1px solid #ffca28; padding: 1px 3px; border-radius: 3px; }
    .s-tag { background: #238636; color: white; font-size: 9px; padding: 1px 5px; border-radius: 3px; float: right; }
    .sensor-bg { background: #1a1a1a; height: 10px; border-radius: 5px; margin: 2px 0 8px 0; border: 1px solid #333; overflow: hidden; }
    .sensor-fill { height: 100%; border-radius: 5px; }
    .sensor-label { font-size: 9px; color: #888; font-weight: bold; text-transform: uppercase; display: block; }
    .hist-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; background: #07090c; padding: 6px; border-bottom: 1px solid #1a1a1a; font-family: monospace; font-size: 11px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- DATOS ESTÁTICOS ---
ASSETS = {
    'VEREM': {'t': 'IMPULSO', 's': 'AGRESIVO', 'in': 128.16, 'tgt': 132.65, 'sl': 125.80, 'n': 85, 'p': 92, 'w': 78},
    'BTC': {'t': 'WHALES', 's': 'IA EXPERTO', 'in': 87746.0, 'tgt': 90817.0, 'sl': 86166.0, 'n': 70, 'p': 45, 'w': 88},
    'ETH': {'t': 'INSTITUCIONAL', 's': 'MODO PRO', 'in': 2890.72, 'tgt': 2991.90, 'sl': 2838.69, 'n': 60, 'p': 35, 'w': 65},
    'SOL': {'t': 'FIBONACCI', 's': 'SCALPING', 'in': 122.37, 'tgt': 126.65, 'sl': 120.17, 'n': 55, 'p': 40, 'w': 50}
}

# --- HEADER ---
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown('<h2 style="color:white;text-align:center;margin:0;font-size:22px;">🛰️ IA TERMINAL ELITE | CONTROL TOTAL</h2>', unsafe_allow_html=True)
    st.markdown('<div style="background:#222;height:12px;border-radius:6px;overflow:hidden;margin:5px 0;border:1px solid #444;"><div style="background:#3fb950;width:75%"></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div style="background:white;padding:3px;border-radius:5px;text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=65x65&data=REPORTE" width="65"></div>', unsafe_allow_html=True)

# --- PRECIOS ---
prices = {}
try:
    mexc = ccxt.mexc({'timeout': 5000})
    ticks = mexc.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    for k, v in ticks.items(): prices[k.split('/')[0]] = v['last']
except: pass

# --- MONEDAS (Renderizado corregido) ---
cols = st.columns(4)
for i, name in enumerate(['VEREM', 'BTC', 'ETH', 'SOL']):
    d = ASSETS[name]
    curr_p = prices.get(name, 0.0)
    pnl = ((curr_p - d['in']) / d['in'] * 100) if curr_p > 0 else 0.0
    pnl_c = "#3fb950" if pnl >= 0 else "#f85149"
    
    with cols[i]:
        # Título y Precio
        st.markdown(f'''
            <div class="card">
                <div><span class="s-tag">{d["s"]}</span><b style="color:white;font-size:18px;">{name} <span class="t-tag">[{d["t"]}]</span></b></div>
                <div style="display:flex;justify-content:space-between;margin:10px 0;"><span style="color:#58a6ff;font-size:20px;font-weight:bold;">${curr_p:,.2f}</span><span style="color:{pnl_c};font-size:16px;font-weight:bold;">{pnl:.2f}%</span></div>
                
                <span class="sensor-label">Noticias</span><div class="sensor-bg"><div class="sensor-fill" style="width:{d["n"]}%; background:#1f6feb;"></div></div>
                <span class="sensor-label">Impulso</span><div class="sensor-bg"><div class="sensor-fill" style="width:{d["p"]}%; background:#238636;"></div></div>
                <span class="sensor-label">Ballenas</span><div class="sensor-bg"><div class="sensor-fill" style="width:{d["w"]}%; background:#8957e5;"></div></div>
                
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;background:#000;padding:5px;border-radius:5px;text-align:center;border:1px solid #21262d;margin-top:5px;">
                    <div style="color:white;font-size:9px;"><span style="color:#888;font-size:7px;">IN</span><br>{d["in"]}</div>
                    <div style="color:#3fb950;font-size:9px;"><span style="color:#888;font-size:7px;">TGT</span><br>{d["tgt"]}</div>
                    <div style="color:#f85149;font-size:9px;"><span style="color:#888;font-size:7px;">SL</span><br>{d["sl"]}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

# --- HISTORIAL (Renderizado corregido) ---
st.markdown('<b style="color:#58a6ff; font-size:14px; margin-left:10px;">📋 HISTORIAL ÚLTIMAS OPERACIONES (SINCRO QR)</b>', unsafe_allow_html=True)
st.markdown('''
    <div style="border: 1px solid #30363d; border-radius: 8px; overflow: hidden; margin: 0 10px;">
        <div class="hist-row" style="background:#161b22; color:#888; font-weight:bold;">
            <div>ACTIVO</div><div>ESTRATEGIA</div><div>DURACIÓN</div><div>PNL NETO</div>
        </div>
        <div class="hist-row" style="color:#3fb950;"><div>VEREM/USDT</div><div>AGRESIVO</div><div>14m 22s</div><div>+12.74%</div></div>
        <div class="hist-row" style="color:#3fb950;"><div>BTC/USDT</div><div>IA EXPERTO</div><div>02h 45m</div><div>+3.15%</div></div>
    </div>
''', unsafe_allow_html=True)

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="v38")
