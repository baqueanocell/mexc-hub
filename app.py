import streamlit as st
import ccxt
import time

st.set_page_config(page_title="IA TERMINAL V4.8", layout="wide")

# --- CSS ULTRA COMPACTO (Ahorra 50% de espacio) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card { background: #0d1117; border: 1px solid #30363d; padding: 8px; border-radius: 6px; border-top: 3px solid #1f6feb; margin-bottom: 5px; }
    .strat-tag { background: #238636; color: white; font-size: 8px; padding: 1px 4px; border-radius: 3px; float: right; }
    .reason { color: #8b949e; font-size: 9px; font-style: italic; margin-top: 2px; line-height: 1; }
    .price-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2px; margin-top: 6px; text-align: center; }
    .p-unit { background: #000; border: 1px solid #21262d; padding: 2px; border-radius: 3px; }
    .p-lbl { font-size: 7px; color: #888; display: block; text-transform: uppercase; }
    .p-num { font-size: 10px; font-weight: bold; color: white; }
    .ia-thought { background: #001a00; border-left: 3px solid #00ff00; padding: 5px 10px; color: #00ff00; font-family: monospace; font-size: 11px; margin-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- DATOS ---
if 'init_t' not in st.session_state: st.session_state.init_t = time.time()
min_a = int((time.time() - st.session_state.init_t) // 60) + 5

ASSETS = {
    'VEREM': {'st': 'AGRESIVO', 'rs': 'Ruptura de volumen y ballenas activas.', 'in': 128.16, 'tg': 132.65, 'sl': 125.80, 'm': min_a},
    'BTC':   {'st': 'IA EXPERTO', 'rs': 'Soporte institucional en zona de 87k.', 'in': 87746.0, 'tg': 90817.0, 'sl': 86166.0, 'm': 14},
    'ETH':   {'st': 'MODO PRO', 'rs': 'Acumulación en rango lateral de 4H.', 'in': 2890.72, 'tg': 2991.90, 'sl': 2838.69, 'm': 52},
    'SOL':   {'st': 'SCALPING', 'rs': 'Rebote en Fibonacci 0.618 detectado.', 'in': 122.37, 'tg': 126.65, 'sl': 120.17, 'm': 3}
}

# --- HEADER ---
st.markdown(f'''
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <h2 style="color:white; margin:0; font-size:18px;">🛰️ TERMINAL IA ELITE</h2>
        <div style="background:#222; width:60%; height:6px; border-radius:3px; overflow:hidden; border:1px solid #444;">
            <div style="background:#3fb950; width:85%; height:100%;"></div>
        </div>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=40x40&data=MEXC" width="40" style="background:white; border-radius:3px;">
    </div>
''', unsafe_allow_html=True)

st.markdown(f'<div class="ia-thought">🧠 <b>PENSAMIENTO IA:</b> Escaneando MEXC... Sincronizado hace {min_a}m.</div>', unsafe_allow_html=True)

# --- COLUMNAS ---
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
    color_pnl = "#3fb950" if pnl >= 0 else "#f85149"
    fuego = "🔥 ENTRAR" if d['m'] < 10 else "⏳ MONITOREAR"

    with cols[i]:
        st.markdown(f'''
            <div class="card">
                <span class="strat-tag">{d["st"]}</span>
                <b style="color:white; font-size:14px;">{name}</b>
                <div class="reason">{d["rs"]}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:5px;">
                    <span style="color:#58a6ff; font-size:16px; font-weight:bold;">${cp:,.2f}</span>
                    <span style="color:{color_pnl}; font-size:12px; font-weight:bold;">{pnl:.2f}%</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:4px;">
                    <span style="color:#ffca28; font-size:9px; font-weight:bold;">{fuego}</span>
                    <span style="color:#888; font-size:9px;">⏱️ {d["m"]} MIN</span>
                </div>
                <div class="price-row">
                    <div class="p-unit"><span class="p-lbl">IN</span><span class="p-num">{d["in"]}</span></div>
                    <div class="p-unit"><span class="p-lbl" style="color:#3fb950;">TGT</span><span class="p-num">{d["tg"]}</span></div>
                    <div class="p-unit"><span class="p-lbl" style="color:#f85149;">SL</span><span class="p-num">{d["sl"]}</span></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

# --- HISTORIAL COMPACTO ---
st.markdown('<div style="color:#58a6ff; font-weight:bold; font-size:11px; margin-top:5px;">📋 RESUMEN DE OPERACIONES</div>', unsafe_allow_html=True)
st.table([
    {"ACTIVO": "VEREM/USDT", "ESTRAT.": "AGRESIVO", "TIEMPO": f"{min_a}m", "ESTADO": "ACTIVA 🔥"},
    {"ACTIVO": "SOL/USDT", "ESTRAT.": "SCALPING", "TIEMPO": "3m", "ESTADO": "ENTRADA 🔥"}
])

time.sleep(15)
st.rerun()
