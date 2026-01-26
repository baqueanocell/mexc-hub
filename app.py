import streamlit as st
import ccxt
import pytz

# Configuración base
st.set_page_config(page_title="IA TERMINAL ELITE V3.5", layout="wide")

# --- ESTILOS TV BOX ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 12px; border-top: 4px solid #1f6feb; margin-bottom: 10px; }
    .trig-tag { font-size: 11px; color: #ffca28; font-weight: bold; border: 1px solid #ffca28; padding: 1px 4px; border-radius: 4px; margin-left: 5px; }
    .strat-tag { background: #238636; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold; float: right; }
    .perf-bar { background: #222; border-radius: 10px; height: 18px; display: flex; overflow: hidden; border: 1px solid #444; margin: 10px 0; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 8px; border-radius: 6px; margin-top: 15px; border: 1px solid #21262d; text-align: center; }
    .ia-log { background: #001a00; border-left: 5px solid #00ff00; padding: 12px; font-family: monospace; font-size: 13px; color: #00ff00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'signals' not in st.session_state:
    st.session_state.signals = {
        'VEREM': {'e': 128.16, 't': 132.65, 's': 128.80, 'trig': 'IMPULSO', 'strat': 'AGRESIVO'},
        'BTC': {'e': 87746.0, 't': 90817.0, 's': 86166.0, 'trig': 'WHALES', 'strat': 'IA EXPERTO'},
        'ETH': {'e': 2890.72, 't': 2991.90, 's': 2838.69, 'trig': 'INSTITUCIONAL', 'strat': 'MODO PRO'},
        'SOL': {'e': 122.37, 't': 126.65, 's': 120.17, 'trig': 'FIBONACCI', 'strat': 'SCALPING'}
    }

# --- HEADER FIJO ---
h1, h2 = st.columns([4, 1])
with h1:
    st.markdown("""
        <div style="text-align: center; color: white;">
            <span style="font-size: 24px; font-weight: bold;">🛰️ IA TERMINAL ELITE | SISTEMA ACTIVO</span>
            <div class="perf-bar"><div style="background: #3fb950; width: 50%;"></div><div style="background: #f85149; width: 50%;"></div></div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: bold;">
                <span style="color: #3fb950;">WIN RATE: 50.0%</span>
                <span style="color: #f85149;">LOSS RATE: 50.0%</span>
            </div>
        </div>""", unsafe_allow_html=True)
with h2:
    st.markdown('<div style="background:white; padding:5px; border-radius:8px; text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=85x85&data=REPORTE" width="85"></div>', unsafe_allow_html=True)

st.markdown('<div class="ia-log">🧠 PENSAMIENTO IA: Escaneando bloques en tiempo real... Cuadros forzados activos.</div>', unsafe_allow_html=True)

# --- CONEXIÓN SEGURA ---
prices = {}
try:
    exchange = ccxt.mexc({'timeout': 10000})
    tickers = exchange.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    for k, v in tickers.items():
        prices[k.split('/')[0]] = float(v['last'])
except:
    pass # Si falla la conexión, los precios simplemente no se actualizan, pero el código sigue

# --- DIBUJO DE CUADROS ---
cols = st.columns(4)
for i, (name, data) in enumerate(st.session_state.signals.items()):
    current_p = prices.get(name, 0.0)
    pnl = ((current_p - data['e']) / data['e'] * 100) if current_p > 0 else 0.0
    pnl_col = "#3fb950" if pnl >= 0 else "#f85149"
    
    # Formateo manual para evitar el ValueError de Streamlit
    p_str = f"{current_p:.2f}" if current_p > 1 else f"{current_p:.4f}"
    
    with cols[i]:
        st.markdown(f"""
        <div class="card-tv">
            <div>
                <span class="strat-tag">{data['strat']}</span>
                <span style="color:white; font-size:20px; font-weight:bold;">{name}<span class="trig-tag">[{data['trig']}]</span></span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                <span style="color:#58a6ff; font-weight:bold; font-size:22px;">${p_str}</span>
                <span style="color:{pnl_col}; font-weight:bold; font-size:18px;">{pnl:.2f}%</span>
            </div>
            <div class="exec-grid">
                <div style="color:white; font-size:11px;"><span style="color:#888;font-size:8px;">IN</span><br>{data['e']}</div>
                <div style="color:#3fb950; font-size:11px;"><span style="color:#888;font-size:8px;">TGT</span><br>{data['t']}</div>
                <div style="color:#f85149; font-size:11px;"><span style="color:#888;font-size:8px;">STOP</span><br>{data['s']}</div>
            </div>
        </div>""", unsafe_allow_html=True)

# Refresco automático al final para no interrumpir el dibujo
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="f")
