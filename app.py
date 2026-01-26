import streamlit as st
import ccxt
import time

st.set_page_config(page_title="IA TERMINAL V4.4", layout="wide")

# --- CSS ULTRA COMPACTO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-base { background: #0d1117; border: 1px solid #30363d; padding: 8px; border-radius: 8px; border-top: 3px solid #1f6feb; }
    /* Barras mucho más chicas */
    .sensor-bg { background: #1a1a1a; height: 4px; border-radius: 2px; margin-bottom: 4px; overflow: hidden; }
    .sensor-f { height: 100%; }
    .label-s { font-size: 8px; color: #666; font-weight: bold; text-transform: uppercase; margin-top: 2px; }
    /* Grilla de precios de entrada/salida */
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 4px; border-radius: 4px; text-align: center; border: 1px solid #21262d; margin-top: 8px; }
    .ia-thought { background: #001a00; border-left: 3px solid #00ff00; padding: 8px; color: #00ff00; font-family: monospace; font-size: 12px; margin-bottom: 10px; }
    .time-tag { background: #1f6feb; color: white; font-size: 9px; padding: 1px 4px; border-radius: 2px; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE TIEMPO ---
if 'init_time' not in st.session_state: st.session_state.init_time = time.time()
t_act = int((time.time() - st.session_state.init_time) // 60) + 5

# --- HEADER Y BARRA ---
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown('<h2 style="color:white;text-align:center;margin:0;font-size:20px;">🛰️ TERMINAL IA ELITE | SEÑALES MEXC</h2>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#222;height:8px;border-radius:4px;display:flex;overflow:hidden;margin-top:5px;"><div style="background:#3fb950;width:85%;"></div><div style="background:#f85149;width:15%;"></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="background:white;padding:2px;border-radius:4px;text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=50x50&data=MEXC" width="50"></div>', unsafe_allow_html=True)

st.markdown(f'<div class="ia-thought"><b>🧠 PENSAMIENTO IA:</b> Escaneando niveles críticos. Órdenes listas para ejecutar.</div>', unsafe_allow_html=True)

# --- DATOS ---
ASSETS = {
    'VEREM': {'in': 128.16, 'tgt': 132.65, 'sl': 125.80, 'n': 85, 'p': 92, 'w': 78, 'm': t_act},
    'BTC':   {'in': 87746.0, 'tgt': 90817.0, 'sl': 86166.0, 'n': 70, 'p': 45, 'w': 88, 'm': 14},
    'ETH':   {'in': 2890.72, 'tgt': 2991.90, 'sl': 2838.69, 'n': 60, 'p': 35, 'w': 65, 'm': 52},
    'SOL':   {'in': 122.37, 'tgt': 126.65, 'sl': 120.17, 'n': 55, 'p': 40, 'w': 50, 'm': 3}
}

prices = {}
try:
    mexc = ccxt.mexc()
    ticks = mexc.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    for k, v in ticks.items(): prices[k.split('/')[0]] = v['last']
except: pass

# --- MONEDAS ---
cols = st.columns(4)
for i, name in enumerate(['VEREM', 'BTC', 'ETH', 'SOL']):
    d = ASSETS[name]
    cp = prices.get(name, 0.0)
    pnl = ((cp - d['in']) / d['in'] * 100) if cp > 0 else 0.0
    
    with cols[i]:
        st.markdown(f'''
            <div class="card-base">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:white;font-size:15px;">{name}</b>
                    <span class="time-tag">{d["m"]}M</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin:5px 0;">
                    <span style="color:#58a6ff;font-size:17px;font-weight:bold;">${cp:,.2f}</span>
                    <span style="color:{"#3fb950" if pnl >= 0 else "#f85149"};font-size:13px;font-weight:bold;">{pnl:.2f}%</span>
                </div>
                
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px;">
                    <div><div class="label-s">Not</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["n"]}%;background:#1f6feb;"></div></div></div>
                    <div><div class="label-s">Imp</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["p"]}%;background:#238636;"></div></div></div>
                    <div><div class="label-s">Ball</div><div class="sensor-bg"><div class="sensor-f" style="width:{d["w"]}%;background:#8957e5;"></div></div></div>
                </div>

                <div class="exec-grid">
                    <div style="color:white;font-size:9px;"><span style="color:#888;font-size:7px;">ENTRY</span><br>{d["in"]}</div>
                    <div style="color:#3fb950;font-size:9px;"><span style="color:#888;font-size:7px;">TARGET</span><br>{d["tgt"]}</div>
                    <div style="color:#f85149;font-size:9px;"><span style="color:#888;font-size:7px;">STOP</span><br>{d["sl"]}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

# --- HISTORIAL ---
st.table([
    {"ACTIVO": "VEREM/USDT", "TIEMPO": f"{t_act} min", "PNL": f"{pnl:.2f}%", "ESTADO": "ENTRY"},
    {"ACTIVO": "SOL/USDT", "TIEMPO": "3 min", "PNL": "0.15%", "ESTADO": "CONFIRMADO"}
])

time.sleep(15)
st.rerun()
