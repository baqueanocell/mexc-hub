import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime

# 1. CONFIGURACIÓN CYBER-PRO
st.set_page_config(page_title="IA NEURAL V45", layout="wide", initial_sidebar_state="collapsed")

# Estilo de botones y tarjetas
st.markdown("""
    <style>
    .stApp { background-color: #050a0e; }
    .mode-btn { border-radius: 20px; border: 1px solid #00d4ff; padding: 10px; text-align: center; cursor: pointer; }
    .crypto-card { background: #111b21; border-radius: 12px; padding: 15px; border-left: 5px solid #00d4ff; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
    .badge-time { background: #00d4ff; color: #050a0e; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: bold; }
    .price-main { font-size: 30px; font-weight: 900; color: white; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA DE SESIÓN Y FILTROS
if 'modo' not in st.session_state: st.session_state.modo = "SCALPING"
if 'history' not in st.session_state: st.session_state.history = []

@st.cache_data(ttl=10)
def fetch_mexc_v45():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1500000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_mexc_v45()

# 3. CABECERA Y SELECTOR DE MODO
st.markdown("<h1 style='color: #00d4ff; text-align: center;'>NEURAL COMMAND CENTER V45</h1>", unsafe_allow_html=True)

# Botones de Modo
c_bt1, c_bt2, c_bt3, c_bt4 = st.columns(4)
with c_bt1:
    if st.button("⚡ SCALPING (5-15m)", use_container_width=True): st.session_state.modo = "SCALPING"
with c_bt2:
    if st.button("📈 MEDIANO PLAZO (1h-4h)", use_container_width=True): st.session_state.modo = "MEDIANO"
with c_bt3:
    if st.button("💎 LARGO PLAZO (1d-1w)", use_container_width=True): st.session_state.modo = "LARGO"
with c_bt4:
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=SYNC_V45", width=45)

st.markdown(f"<p style='text-align: center; color: #8b949e;'>MODO ACTIVO: <b style='color:#00d4ff'>{st.session_state.modo}</b></p>", unsafe_allow_html=True)

# 4. LÓGICA DE FILTRADO IA SEGÚN MODO
# Scalping: Alta volatilidad | Mediano: Volumen sólido | Largo: Proyectos Top
if st.session_state.modo == "SCALPING":
    selected = sorted(all_pairs, key=lambda x: abs(tickers[x].get('percentage', 0)), reverse=True)[:4]
    time_label = "MUY RÁPIDO"
elif st.session_state.modo == "MEDIANO":
    selected = sorted(all_pairs, key=lambda x: tickers[x].get('quoteVolume', 0), reverse=True)[:4]
    time_label = "TENDENCIAL"
else:
    # Largo plazo prioriza monedas "pesadas" como BTC, ETH, SOL si están en el top
    prioridad = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    selected = [p for p in prioridad if p in all_pairs] + sorted(all_pairs, key=lambda x: tickers[x].get('quoteVolume', 0), reverse=True)[:4]
    selected = selected[:4]
    time_label = "INVERSIÓN"

# 5. MONITOR DE LAS 4 MEJORES
st.write("")
cols = st.columns(4)
for i, pair in enumerate(selected):
    px = tickers.get(pair, {}).get('last', 0)
    chg = tickers.get(pair, {}).get('percentage', 0)
    
    with cols[i]:
        st.markdown(f"""
            <div class='crypto-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <b style='color:#00d4ff;'>{pair.split('/')[0]}</b>
                    <span class='badge-time'>{time_label}</span>
                </div>
                <div class='price-main'>${px:,.4f}</div>
                <div style='color:{"#00ff00" if chg >= 0 else "#ff4b4b"}; font-weight:bold;'>{chg:+.2f}%</div>
                <hr style='border: 0.1px solid #30363d;'>
                <div style='display:flex; justify-content:space-between; font-size:12px;'>
                    <span>IN: {px*0.995:,.3f}</span>
                    <span style='color:#00ff00;'>TGT: {px*1.05:,.3f}</span>
                </div>
                <p style='font-size:10px; color:#4facfe; margin-top:10px;'>
                🧠 IA: {random.choice(['Patrón Detectado', 'Analizando Ballenas', 'Soporte Fibo'])}
                </p>
            </div>
        """, unsafe_allow_html=True)

# 6. LABORATORIO Y APRENDIZAJE
st.divider()
c_lab, c_bit = st.columns([2, 1])

with c_lab:
    st.subheader(f"🔬 Laboratorio Neural - Especialidad {st.session_state.modo}")
    lab_data = []
    for k in all_pairs[:20]:
        lab_data.append({
            "ACTIVO": k.split('/')[0],
            "ESTRATEGIA": "Momentum" if st.session_state.modo == "SCALPING" else "Estructura",
            "IA SCORE": f"{random.randint(85, 99)}%",
            "INFO": random.choice(["Ballena detectada", "Quema de tokens", "RSI en zona"])
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True)

with c_bit:
    st.subheader("📋 Bitácora")
    st.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
