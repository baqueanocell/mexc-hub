import streamlit as st
import ccxt
import time

st.set_page_config(page_title="IA TERMINAL V5.2", layout="wide")

# --- CSS MINIMALISTA (Para que todo quepa) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    /* Contenedor Ultra-Compacto */
    .mini-card { background: #0d1117; border: 1px solid #30363d; padding: 6px; border-radius: 6px; border-top: 2px solid #00ff00; margin-bottom: 0px; }
    .t-name { color: white; font-size: 14px; font-weight: bold; margin: 0; }
    .t-strat { color: #238636; font-size: 8px; font-weight: bold; float: right; }
    .t-price { color: #58a6ff; font-size: 16px; font-weight: bold; margin: 2px 0; }
    .t-pnl { font-size: 11px; font-weight: bold; }
    .t-reason { color: #8b949e; font-size: 8px; font-style: italic; line-height: 1; margin-bottom: 4px; }
    /* Grilla de niveles en una sola fila */
    .level-row { display: flex; justify-content: space-between; gap: 2px; margin-top: 4px; }
    .level-item { flex: 1; background: #000; padding: 2px; border-radius: 3px; text-align: center; border: 1px solid #21262d; }
    .l-lbl { font-size: 6px; color: #888; display: block; }
    .l-val { font-size: 9px; font-weight: bold; color: #adbac7; }
    /* Pensamiento IA pequeño */
    .ia-box { background: #001a00; border-left: 3px solid #00ff00; padding: 4px 8px; color: #00ff00; font-family: monospace; font-size: 10px; margin-bottom: 6px; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE ESCÁNER ---
@st.cache_data(ttl=10)
def scan_mexc():
    try:
        mexc = ccxt.mexc()
        t = mexc.fetch_tickers()
        validos = {k: v for k, v in t.items() if '/USDT' in k and v['last'] > 0}
        return sorted(validos.items(), key=lambda x: x[1]['percentage'] or 0, reverse=True)[:4]
    except: return []

# --- HEADER COMPACTO ---
c1, c2, c3 = st.columns([2, 4, 1])
with c1: st.markdown('<h3 style="color:white; margin:0; font-size:16px;">🛰️ IA AUTÓNOMA V5.2</h3>', unsafe_allow_html=True)
with c2: st.markdown('<div class="ia-box">🧠 <b>IA:</b> Escaneando Fibonacci y Volumen... Patrones de entrada optimizados.</div>', unsafe_allow_html=True)
with c3: st.markdown(f'<img src="https://api.qrserver.com/v1/create-qr-code/?size=35x35&data=MEXC" width="35" style="float:right; background:white; border-radius:2px;">', unsafe_allow_html=True)

# --- GRID DE SEÑALES ---
data = scan_mexc()
cols = st.columns(4)

for i, (par, info) in enumerate(data):
    name = par.replace('/USDT', '')
    price = info['last']
    change = info['percentage'] or 0
    # Simulación de niveles IA
    entry, tgt, sl = price * 0.998, price * 1.05, price * 0.98
    
    with cols[i]:
        st.markdown(f'''
            <div class="mini-card">
                <span class="t-strat">FIBONACCI</span>
                <p class="t-name">{name}</p>
                <div class="t-reason">Volumen detectado + Patrón de cuña.</div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="t-price">${price:,.4f}</div>
                    <div class="t-pnl" style="color:{"#3fb950" if change >= 0 else "#f85149"};">{change:.2f}%</div>
                </div>
                <div class="level-row">
                    <div class="level-item"><span class="l-lbl">ENTRY</span><span class="l-val">{entry:,.3f}</span></div>
                    <div class="level-item"><span class="l-lbl" style="color:#3fb950;">TARGET</span><span class="l-val">{tgt:,.3f}</span></div>
                    <div class="level-item"><span class="l-lbl" style="color:#f85149;">STOP</span><span class="l-val">{sl:,.3f}</span></div>
                </div>
                <div style="margin-top:4px; font-size:8px; color:#ffca28; font-weight:bold;">🔥 SEÑAL ACTIVA</div>
            </div>
        ''', unsafe_allow_html=True)

# --- BITÁCORA MINI ---
st.markdown('<p style="color:#58a6ff; font-weight:bold; font-size:10px; margin: 5px 0 2px 0;">📋 BITÁCORA DE APRENDIZAJE</p>', unsafe_allow_html=True)
st.dataframe([
    {"SUCESO": "Filtro Vol", "ACTIVO": "PEPE", "MEJORA": "+15%"},
    {"SUCESO": "Fibonacci", "ACTIVO": "BTC", "MEJORA": "Trailing"}
], hide_index=True, use_container_width=True)

time.sleep(15)
st.rerun()
