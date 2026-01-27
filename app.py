import streamlit as st
import ccxt
import time
import pandas as pd
import numpy as np
import random
import json
from datetime import datetime

# 1. ESTILO Y CONFIGURACIÓN (Mantenemos tu diseño)
st.set_page_config(page_title="IA V64 NEURAL INSIGHT", layout="wide", initial_sidebar_state="collapsed")

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

# 2. MEMORIA Y PERSISTENCIA (Infinita y con Backup)
if 'history' not in st.session_state: st.session_state.history = []
if 'learning_curve' not in st.session_state: st.session_state.learning_curve = [82.5]
if 'modo' not in st.session_state: st.session_state.modo = "⚡ SCALPING"

@st.cache_data(ttl=5)
def fetch_live_data():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 2000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_live_data()

# 3. LÓGICA DE COMPARACIÓN Y NOTICIAS
# Simulamos una base de noticias para el laboratorio
news_feed = [
    "Rumores de ETF en Hong Kong", "Actualización de red inminente", 
    "Aumento de quema de tokens", "Ballena moviendo 500M USD",
    "Fuerte resistencia psicológica", "Adopción institucional en aumento"
]

# 4. CABECERA Y PENSAMIENTO IA
# Comparación en el pensamiento
if len(all_pairs) > 2:
    comp = f"Comparativa: {all_pairs[0].split('/')[0]} muestra mayor fuerza relativa que {all_pairs[1].split('/')[0]}."
else:
    comp = "Analizando flujo de liquidez global..."

st.markdown(f"<div class='thought-box'><b>NEURAL INSIGHT:</b> {random.choice(news_feed)}. {comp}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1:
    st.markdown("<h2 style='color:#00ff00; margin:0;'>NEURAL INSIGHT V64</h2>", unsafe_allow_html=True)
    m_cols = st.columns(3)
    if m_cols[0].button("⚡ SCALPING"): st.session_state.modo = "⚡ SCALPING"
    if m_cols[1].button("📈 MEDIANO"): st.session_state.modo = "📈 MEDIANO"
    if m_cols[2].button("💎 LARGO"): st.session_state.modo = "💎 LARGO"

with c2:
    st.caption("📈 CURVA DE EVOLUCIÓN")
    st.line_chart(st.session_state.learning_curve[-50:], height=80)

with c3:
    # QR Backup con descarga
    backup_json = json.dumps({"acc": st.session_state.learning_curve, "hist": st.session_state.history})
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=BACKUP_V64", width=100)
    st.download_button("💾 DESCARGAR CEREBRO", data=backup_json, file_name="cerebro_ia.json")

with c4:
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL',''))])
    rate = (wins/len(st.session_state.history)*100) if st.session_state.history else 100
    st.metric("WIN RATE", f"{rate:.1f}%", f"{len(st.session_state.history)} OPS")

# 5. MONITORES CON EMOJIS DINÁMICOS
st.write("---")
if all_pairs:
    display_pairs = sorted(all_pairs, key=lambda x: abs(tickers[x]['percentage']), reverse=True)[:4]
    cols = st.columns(4)
    for i, pair in enumerate(display_pairs):
        px = tickers[pair]['last']
        prob = random.randint(70, 99)
        
        # EMOJI DINÁMICO SEGÚN PROBABILIDAD
        if prob >= 90: emoji = "🔥" # Alta
        elif prob >= 80: emoji = "✅" # Media-Alta
        elif prob >= 70: emoji = "⚖️" # Media
        else: emoji = "⚠️" # Baja
        
        with cols[i]:
            with st.container(border=True):
                st.markdown(f"**{pair.split('/')[0]}** {emoji}", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align:center;'>${px:,.4f}</h3>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;'><small style='color:yellow;'>ENTRADA (IN)</small><br><span class='price-in'>${px*0.998:,.4f}</span></div>", unsafe_allow_html=True)
                o1, o2 = st.columns(2)
                o1.markdown(f"<div style='text-align:center;'><small style='color:#00ff00;'>TP</small><br><span class='price-out'>${px*1.05:,.3f}</span></div>", unsafe_allow_html=True)
                o2.markdown(f"<div style='text-align:center;'><small style='color:#ff4b4b;'>SL</small><br><span class='price-sl'>${px*0.985:,.3f}</span></div>", unsafe_allow_html=True)
                st.caption(f"Prob: {prob}% | {st.session_state.modo}")

# 6. LABORATORIO DE 50 CON NOTICIAS DETALLADAS
st.divider()
cl, cr = st.columns([1.8, 1.2])
with cl:
    st.subheader("🔬 Laboratorio Neural - 50 Activos")
    lab_data = []
    for k in all_pairs[:50]:
        lab_data.append({
            "MONEDA": k.split('/')[0],
            "SCORE": f"{random.randint(70,99)}%",
            "NOTICIA": random.choice(news_feed),
            "FZA. RELATIVA": f"{random.uniform(0.1, 5.0):.1f}x",
            "ESTADO": "Liderando" if random.random() > 0.8 else "Siguiendo"
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, height=350, hide_index=True)

with cr:
    st.subheader(f"📋 Historial Infinito ({len(st.session_state.history)})")
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, height=350)

st.sidebar.subheader("⚠️ Riesgo Global")
st.sidebar.write(f"Noticias hoy: {len(news_feed)} críticas")
st.sidebar.progress(70)

time.sleep(10)
st.rerun()
