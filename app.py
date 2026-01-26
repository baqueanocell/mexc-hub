import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta

# 1. Configuración y Refresco de 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="MEXC Dual-Terminal", layout="wide")

# CSS para tarjetas compactas y nombres de barras
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    .stProgress > div > div > div > div { height: 3px !important; }
    .card {
        background-color: #161b22;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    .coin-title { color: #ffffff; font-size: 16px; font-weight: bold; }
    .label-bar { font-size: 9px; color: #8b949e; margin-bottom: -5px; }
    </style>
    """, unsafe_allow_html=True)

exchange = ccxt.mexc()

# 2. Lógica de Historial (Usamos session_state para que no se borre al refrescar)
if 'historial_trades' not in st.session_state:
    st.session_state.historial_trades = []
if 'last_history_update' not in st.session_state:
    st.session_state.last_history_update = datetime.now()

def obtener_datos():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top_10 = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(10)
        
        datos = []
        for symbol in top_10['symbol']:
            t = tickers[symbol]
            p = t['last']
            ch = t['percentage'] or 0
            # Barras
            datos.append({
                "sym": symbol.replace('/USDT', ''), "price": p,
                "soc": min(max(50 + (ch * 2), 10), 95),
                "ball": 72, "imp": min(max(float(ch) + 50, 5), 98),
                "tp": p * 1.02, "sl": p * 0.99
            })
        
        # Guardar en historial cada 20 minutos
        ahora = datetime.now()
        if ahora - st.session_state.last_history_update > timedelta(minutes=20):
            best = max(datos, key=lambda x: x['imp'])
            nuevo_registro = {
                "Hora": ahora.strftime("%H:%M"),
                "Moneda": best['sym'],
                "Precio": best['price'],
                "Resultado": "Analizando..." # Se evaluaría en el siguiente ciclo
            }
            st.session_state.historial_trades.insert(0, nuevo_registro)
            st.session_state.last_history_update = ahora
            
        return datos
    except: return []

# --- UI ---
st.markdown(f"### 🛡️ TERMINAL 2X5 <span style='float:right; font-size:12px;'>LIVE: {datetime.now().strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

items = obtener_datos()

# GRID DE 2 COLUMNAS
cols = st.columns(2)
for idx, m in enumerate(items):
    with cols[idx % 2]:
        st.markdown(f"""
        <div class="card">
            <span class="coin-title">{m['sym']}</span> <span style="color:#58a6ff; float:right;">${m['price']}</span><br>
            <div class="label-bar">SOCIAL</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="label-bar">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="label-bar">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)
        st.markdown(f"<span style='color:#3fb950; font-size:10px;'>TP: {m['tp']:.4f}</span> | <span style='color:#f85149; font-size:10px;'>SL: {m['sl']:.4f}</span>", unsafe_allow_html=True)

st.write("---")

# --- SECCIÓN HISTORIAL ---
st.subheader("📜 Historial de Recomendaciones (Cada 20M)")
if st.session_state.historial_trades:
    st.table(pd.DataFrame(st.session_state.historial_trades).head(5))
else:
    st.info("Esperando primer ciclo de 20 minutos para registrar señales...")
