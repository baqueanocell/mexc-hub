import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta

# Configuración de Refresco (10 segundos)
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="MEXC Inteligencia IA", layout="wide", initial_sidebar_state="collapsed")

# CSS para forzar 2 columnas en móvil y diseño profesional
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    /* Forzar 2 columnas en móviles */
    [data-testid="column"] {
        width: 49% !important;
        flex: 1 1 49% !important;
        min-width: 49% !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
    }
    /* Estilo de Tarjeta */
    .stProgress > div > div > div > div { height: 2px !important; }
    .card-pro {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 4px;
        padding: 5px;
        margin-bottom: 2px;
    }
    .label-bar { font-size: 8px !important; color: #8b949e; margin-bottom: -15px; text-transform: uppercase; }
    .price-val { color: #58a6ff; font-family: monospace; font-size: 11px !important; }
    h1, h2, h3 { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

exchange = ccxt.mexc()

# Historial en memoria de sesión
if 'hist_ia' not in st.session_state: st.session_state.hist_ia = []
if 'timer_ia' not in st.session_state: st.session_state.timer_ia = datetime.now()

def fetch_data():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top_vol = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(9)
        
        symbols = list(top_vol['symbol'].values)
        if 'VEREM/USDT' not in symbols: symbols.insert(0, 'VEREM/USDT')
        
        res = []
        for sym in symbols[:10]:
            if sym in tickers:
                t = tickers[sym]
                p, ch = t['last'], (t['percentage'] or 0)
                res.append({
                    "n": sym.replace('/USDT', ''), "p": p,
                    "s": min(max(70 + (ch * 2), 15), 98),
                    "b": 65 + (ch * 0.5), "i": min(max(ch + 50, 5), 95),
                    "tp": p * 1.025, "sl": p * 0.985
                })
        
        # Lógica de registro cada 20 min
        if datetime.now() >= st.session_state.timer_ia:
            best = max(res, key=lambda x: x['i'])
            st.session_state.hist_ia.insert(0, {"H": datetime.now().strftime("%H:%M"), "M": best['n'], "P": best['p']})
            st.session_state.timer_ia = datetime.now() + timedelta(minutes=20)
        return res
    except: return []

# --- HEADER ---
st.markdown("### 🤖 MEXC INTELIGENCIA IA")
data = fetch_data()

# --- MONEDA RECOMENDADA (TOP) ---
if data:
    best_coin = max(data, key=lambda x: x['b'] + x['i'])
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1f6feb, #0d1117); padding: 10px; border-radius: 8px; border: 1px solid #58a6ff;">
        <span style="font-size: 12px; color: #adbac7;">🎯 RECOMENDACIÓN IA:</span><br>
        <b style="font-size: 18px; color: white;">{best_coin['n']} @ ${best_coin['p']}</b><br>
        <span style="color: #3fb950; font-size: 11px;">TP: {best_coin['tp']:.4f}</span> | <span style="color: #f85149; font-size: 11px;">SL: {best_coin['sl']:.4f}</span>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- GRID 2 COLUMNAS (MÓVIL VERTICAL) ---
cols = st.columns(2)
for idx, m in enumerate(data):
    with cols[idx % 2]:
        st.markdown(f"""
        <div class="card-pro">
            <b style="font-size: 12px;">{m['n']}</b> <span class="price-val">${m['p']}</span>
            <div class="label-bar">SOCIAL</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['s']/100)
        st.markdown('<div class="label-bar">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['b']/100)
        st.markdown('<div class="label-bar">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['i']/100)
        st.markdown(f"<div style='font-size:9px; text-align:center; color:#3fb950;'>OBJ: {m['tp']:.3f}</div>", unsafe_allow_html=True)

st.write("---")

# --- HISTORIAL ---
st.caption("📜 HISTORIAL DE SEÑALES (20 MIN)")
if st.session_state.hist_ia:
    st.dataframe(pd.DataFrame(st.session_state.hist_ia).head(5), use_container_width=True)
