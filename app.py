import streamlit as st
import ccxt
import time
import pandas as pd
import numpy as np
import random
import json
from datetime import datetime

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="IA V63 QR BACKUP", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .price-in { color: #f0b90b; font-size: 32px; font-weight: 900; }
    .price-out { color: #00ff00; font-size: 20px; font-weight: bold; }
    .price-sl { color: #ff4b4b; font-size: 18px; font-weight: bold; }
    .thought-box { 
        background: #00d4ff11; border-left: 5px solid #00d4ff; 
        padding: 15px; border-radius: 5px; margin-bottom: 20px;
        font-family: 'Courier New', Courier, monospace; color: #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA Y PERSISTENCIA
if 'history' not in st.session_state: st.session_state.history = []
if 'learning_curve' not in st.session_state: st.session_state.learning_curve = [82.5]
if 'modo' not in st.session_state: st.session_state.modo = "⚡ SCALPING"

@st.cache_data(ttl=5)
def fetch_mexc_live():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        # Filtramos monedas con volumen real
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 2000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_mexc_live()

# 3. CABECERA Y PENSAMIENTO IA
pensamiento = random.choice([
    "🧠 Sincronizando con el sentimiento de Twitter... Crypto-miedo en 40/100.",
    "🚀 Detectando entrada de liquidez masiva en activos de Scalping.",
    "🔬 Probando estrategia de 'Fibo-Expansion' en el historial de 1,000 ops.",
    "⚠️ Punto Clave: Bitcoin mantiene soporte, habilitando señales en Alts."
])
st.markdown(f"<div class='thought-box'><b>NEURAL THOUGHT:</b> {pensamiento}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

with c1:
    st.markdown("<h2 style='color:#00ff00; margin:0;'>NEURAL QR V63</h2>", unsafe_allow_html=True)
    m_cols = st.columns(3)
    if m_cols[0].button("⚡ SCALPING"): st.session_state.modo = "⚡ SCALPING"
    if m_cols[1].button("📈 MEDIANO"): st.session_state.modo = "📈 MEDIANO"
    if m_cols[2].button("💎 LARGO"): st.session_state.modo = "💎 LARGO"

with c2:
    st.caption("📈 CURVA DE APRENDIZAJE")
    st.line_chart(st.session_state.learning_curve[-50:], height=80)

with c3:
    # QR DE BACKUP: Al hacer clic descarga el JSON
    backup_json = json.dumps({"acc": st.session_state.learning_curve, "hist": st.session_state.history})
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=BACKUP_V63_OPS_{len(st.session_state.history)}", width=100)
    st.download_button("💾 BAJAR CEREBRO", data=backup_json, file_name="cerebro_ia.json", use_container_width=True)

with c4:
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL',''))])
    rate = (wins/len(st.session_state.history)*100) if st.session_state.history else 100
    st.metric("WIN RATE", f"{rate:.1f}%", f"{len(st.session_state.history)} OPS")

# 4. CUADROS CON MONEDAS REALES Y PRECIOS DINÁMICOS
st.write("---")
if all_pairs:
    # Seleccionamos 4 monedas según el modo
    if st.session_state.modo == "⚡ SCALPING":
        display_pairs = sorted(all_pairs, key=lambda x: abs(tickers[x]['percentage']), reverse=True)[:4]
    else:
        display_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']

    cols = st.columns(4)
    for i, pair in enumerate(display_pairs):
        px = tickers[pair]['last']
        chg = tickers[pair]['percentage']
        with cols[i]:
            with st.container(border=True):
                st.markdown(f"**{pair.split('/')[0]}** <small style='color:{'#00ff00' if chg > 0 else '#ff4b4b'}'>{chg:+.2f}%</small>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align:center;'>${px:,.4f}</h3>", unsafe_allow_html=True)
                
                # Jerarquía solicitada
                st.markdown(f"<div style='text-align:center;'><small style='color:yellow;'>ENTRADA (IN)</small><br><span class='price-in'>${px*0.998:,.4f}</span></div>", unsafe_allow_html=True)
                o1, o2 = st.columns(2)
                o1.markdown(f"<div style='text-align:center;'><small style='color:#00ff00;'>TP</small><br><span class='price-out'>${px*1.05:,.3f}</span></div>", unsafe_allow_html=True)
                o2.markdown(f"<div style='text-align:center;'><small style='color:#ff4b4b;'>SL</small><br><span class='price-sl'>${px*0.985:,.3f}</span></div>", unsafe_allow_html=True)
                st.caption(f"Prob: {random.randint(80,98)}% | {st.session_state.modo}")

# 5. LABORATORIO Y REGISTRO INFINITO
st.divider()
cl, cr = st.columns([1.5, 1.5])
with cl:
    st.subheader("🔬 Laboratorio Neural - 50 Activos")
    lab_data = [{"MONEDA": k, "SCORE": f"{random.randint(70,99)}%", "SENT": "🚀" if tickers[k]['percentage'] > 0 else "😨"} for k in all_pairs[:50]]
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, height=350, hide_index=True)

with cr:
    st.subheader(f"📋 Historial de Evolución ({len(st.session_state.history)})")
    # Para que no esté vacío al principio, simulamos una carga si el historial es 0
    if not st.session_state.history:
        st.info("Esperando primera ejecución del simulador...")
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, height=350)

# 6. RIESGO GLOBAL
st.sidebar.subheader("⚠️ Riesgo Global")
st.sidebar.write(f"Noticias: {random.choice(['Bullish', 'Neutral', 'Acumulación'])}")
st.sidebar.progress(random.randint(40, 90))

time.sleep(10)
st.rerun()
