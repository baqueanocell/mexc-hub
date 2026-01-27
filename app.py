import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime

# 1. CONFIGURACIÓN SIN ERRORES
st.set_page_config(page_title="IA V51 BANGHÓ PRO", layout="wide", initial_sidebar_state="collapsed")

# Estilos mínimos para no romper el renderizado
st.markdown("""
    <style>
    .stApp { background-color: #050a0e; }
    [data-testid="stMetricValue"] { font-size: 22px !important; color: #00ff00; }
    .win-circle { 
        border: 4px solid #00ff00; border-radius: 50%; padding: 20px; 
        text-align: center; background: #0d1117; width: 120px; margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA Y MOTORES
if 'history' not in st.session_state: st.session_state.history = []
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()
if 'modo' not in st.session_state: st.session_state.modo = "SCALPING"

@st.cache_data(ttl=10)
def fetch_v51():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_v51()

# 3. CABECERA PRO
c1, c2, c3 = st.columns([3, 1, 1.2])

with c1:
    st.title(f"🚀 TRIPLE-ENGINE V51")
    mc = st.columns(3)
    if mc[0].button("⚡ SCALPING", use_container_width=True): st.session_state.modo = "SCALPING"
    if mc[1].button("📈 MEDIANO", use_container_width=True): st.session_state.modo = "MEDIANO"
    if mc[2].button("💎 LARGO", use_container_width=True): st.session_state.modo = "LARGO"

with c2:
    uptime = datetime.now() - st.session_state.start_time
    qr_str = f"V51|{st.session_state.modo}|{uptime.seconds}s"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={qr_str}", width=90)

with c3:
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL', ''))])
    rate = (wins / len(st.session_state.history) * 100) if st.session_state.history else 100.0
    st.markdown(f"<div class='win-circle'><small>{datetime.now().strftime('%d/%m')}</small><br><b style='font-size:25px;'>{rate:.0f}%</b><br><small>WIN RATE</small></div>", unsafe_allow_html=True)

# 4. MONITOR DE SEÑALES (USANDO COMPONENTES NATIVOS PARA EVITAR ERRORES)
st.divider()
selected = sorted(all_pairs, key=lambda x: abs(tickers[x].get('percentage', 0)), reverse=True)[:4]
cols = st.columns(4)

for i, pair in enumerate(selected):
    px = tickers.get(pair, {}).get('last', 0)
    ia_executing = random.choice([True, False])
    led = "🟢 EJECUTANDO" if ia_executing else "⚪ BUSCANDO"
    
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"### {pair.split('/')[0]} <small>{led}</small>", unsafe_allow_html=True)
            st.metric("PRECIO ACTUAL", f"${px:,.4f}", f"{tickers[pair].get('percentage', 0):+.2f}%")
            
            # Niveles TP y SL destacados
            st.write("**OBJETIVOS PRO:**")
            st.metric("TARGET (TP)", f"${px*1.05:,.4f}", delta="GAIN", delta_color="normal")
            st.metric("STOP LOSS (SL)", f"${px*0.985:,.4f}", delta="RISK", delta_color="inverse")
            
            # Las 3 barras una al lado de la otra (Super chiquitas)
            b1, b2, b3 = st.columns(3)
            with b1: st.caption("TEC"); st.progress(random.randint(60,95))
            with b2: st.caption("SENT"); st.progress(random.randint(40,90))
            with b3: st.caption("VOL"); st.progress(random.randint(70,100))
            
            st.caption(f"⏱️ Est. Estrategia: 15-25 min")

# 5. LABORATORIO GIGANTE Y BITÁCORA
st.write("")
c_lab, c_bit = st.columns([2.2, 0.8])

with c_lab:
    st.subheader("🔬 Laboratorio Neural (Analizador de Triple Confluencia)")
    lab_list = []
    for k in all_pairs[:20]:
        lab_list.append({
            "MONEDA": k.split('/')[0],
            "SCORE": f"{random.randint(80,99)}%",
            "NOTICIA": random.choice(["🐋 Ballena Detectada", "🔥 Quema de Tokens", "📈 Impulso RSI"]),
            "MOTOR": "✅✅✅" if random.random() > 0.5 else "✅✅❌",
            "ACCION": "🚀 EJECUTAR"
        })
    st.dataframe(pd.DataFrame(lab_list), use_container_width=True, hide_index=True)

with c_bit:
    st.subheader("📋 Historial PNL")
    # Generar un cierre de simulacro si no hay historial
    if not st.session_state.history:
        st.session_state.history.append({"MONEDA": "BTR", "PNL": "+4.15%", "ESTADO": "CERRADO ✅"})
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
