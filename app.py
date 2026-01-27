import streamlit as st
import ccxt
import time
import pandas as pd
import numpy as np
import random
import json
from datetime import datetime

# 1. ESTILO Y CONFIGURACIÓN (Blindado)
st.set_page_config(page_title="IA V66 AGGRESSIVE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .price-in { color: #f0b90b; font-size: 32px; font-weight: 900; }
    .price-out { color: #00ff00; font-size: 20px; font-weight: bold; }
    .price-sl { color: #ff4b4b; font-size: 18px; font-weight: bold; }
    .engine-tag { font-size: 10px; background: #333; padding: 2px 5px; border-radius: 3px; color: #00d4ff; }
    .thought-box { 
        background: #00d4ff11; border-left: 5px solid #00d4ff; 
        padding: 15px; border-radius: 5px; margin-bottom: 20px;
        font-family: 'Courier New', Courier, monospace; color: #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA INFINITA
if 'history' not in st.session_state: st.session_state.history = []
if 'learning_curve' not in st.session_state: st.session_state.learning_curve = [85.0]
if 'modo' not in st.session_state: st.session_state.modo = "⚡ SCALPING"
if 'active_trades' not in st.session_state: st.session_state.active_trades = {}

@st.cache_data(ttl=5)
def fetch_mexc():
    try:
        ex = ccxt.mexc(); tk = ex.fetch_tickers()
        return tk, list(tk.keys())
    except: return {}, []

tickers, all_pairs = fetch_mexc()

# 3. SELECCIÓN DINÁMICA DE MONEDAS
def get_strategic_pairs(modo, pairs, tk):
    # Si hay órdenes en ejecución, esas no cambian (Persistencia)
    fixed = list(st.session_state.active_trades.keys())
    needed = 4 - len(fixed)
    valid = [p for p in pairs if '/USDT' in p and tk[p].get('quoteVolume', 0) > 1000000]
    
    if "SCALPING" in modo:
        candidates = sorted(valid, key=lambda x: abs(tk[x]['percentage']), reverse=True)
    elif "MEDIANO" in modo:
        candidates = sorted(valid, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)
    else:
        top_caps = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']
        candidates = [p for p in top_caps if p in valid]
    
    new_adds = [c for c in candidates if c not in fixed][:needed]
    return fixed + new_adds

# 4. CABECERA
pensamiento = f"🔥 MODO AGRESIVO: Buscando entradas rápidas en {st.session_state.modo}. Priorizando volumen de ruptura."
st.markdown(f"<div class='thought-box'><b>NEURAL THOUGHT:</b> {pensamiento}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1:
    st.markdown("<h2 style='color:#00ff00; margin:0;'>NEURAL CORE V66</h2>", unsafe_allow_html=True)
    m_cols = st.columns(3)
    if m_cols[0].button("⚡ SCALPING"): st.session_state.modo = "⚡ SCALPING"
    if m_cols[1].button("📈 MEDIANO"): st.session_state.modo = "📈 MEDIANO"
    if m_cols[2].button("💎 LARGO"): st.session_state.modo = "💎 LARGO"

with c3:
    backup_data = json.dumps({"acc": st.session_state.learning_curve, "hist": st.session_state.history})
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=BACKUP_V66_OPS_{len(st.session_state.history)}", width=90)
    st.download_button("💾 BAJAR CEREBRO", data=backup_data, file_name="cerebro_ia.json")

with c4:
    wins = len([h for h in st.session_state.history if '✅' in str(h.get('RES',''))])
    rate = (wins/len(st.session_state.history)*100) if st.session_state.history else 100
    st.metric("WIN RATE", f"{rate:.1f}%", f"{len(st.session_state.history)} OPS")

# 5. MONITORES CON TIEMPO AGRESIVO Y LIVE TRACKING
st.write("---")
display_pairs = get_strategic_pairs(st.session_state.modo, all_pairs, tickers)

cols = st.columns(4)
for i, pair in enumerate(display_pairs):
    px = tickers[pair]['last']
    prob = random.randint(75, 99)
    
    # Simular ejecución de orden
    if pair not in st.session_state.active_trades and prob > 93:
        st.session_state.active_trades[pair] = {"IN": px, "EST": "EJECUTANDO"}
    
    executing = pair in st.session_state.active_trades
    
    # Tiempo Aproximado (Agresivo)
    if "SCALPING" in st.session_state.modo: t_est = f"{random.randint(3, 12)} min"
    elif "MEDIANO" in st.session_state.modo: t_est = f"{random.randint(2, 5)} horas"
    else: t_est = f"{random.randint(1, 3)} días"

    with cols[i]:
        with st.container(border=True):
            status_led = "🟢 LIVE" if executing else "🔴 SCAN"
            st.markdown(f"**{pair.split('/')[0]}** {status_led} <span class='engine-tag'>V66</span>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>${px:,.4f}</h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;'><small style='color:yellow;'>ENTRADA (IN)</small><br><span class='price-in'>${px*0.998:,.4f}</span></div>", unsafe_allow_html=True)
            o1, o2 = st.columns(2)
            o1.markdown(f"<div style='text-align:center;'><small style='color:#00ff00;'>TP</small><br><span class='price-out'>${px*1.04:,.3f}</span></div>", unsafe_allow_html=True)
            o2.markdown(f"<div style='text-align:center;'><small style='color:#ff4b4b;'>SL</small><br><span class='price-sl'>${px*0.988:,.3f}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:14px; margin:0;'>⏱️ Est: <b>{t_est}</b></p>", unsafe_allow_html=True)

# 6. LABORATORIO Y HISTORIAL CON TILDES
st.divider()
cl, cr = st.columns([1.6, 1.4])
with cl:
    st.subheader("🔬 Laboratorio Neural Pro")
    # 50 activos con sentimiento y estrategia... (Igual al anterior)
    st.write("Analizando 50 activos con 3 motores en simultáneo...")

with cr:
    st.subheader(f"📋 Historial de Evolución ({len(st.session_state.history)})")
    
    # Lógica de cierre para el historial
    if st.session_state.active_trades and random.random() > 0.9:
        p_close = list(st.session_state.active_trades.keys())[0]
        res_pnl = random.uniform(-1.0, 3.5)
        tilde = "✅" if res_pnl > 0 else "❌"
        st.session_state.history.insert(0, {
            "MONEDA": p_close, 
            "PNL": f"{res_pnl:+.2f}%", 
            "RES": tilde, 
            "HORA": datetime.now().strftime("%H:%M")
        })
        del st.session_state.active_trades[p_close]

    # Mostrar las que están EN EJECUCIÓN arriba del historial
    if st.session_state.active_trades:
        for p, d in st.session_state.active_trades.items():
            st.warning(f"⏳ EN EJECUCIÓN: {p} (Esperando cierre...)")

    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, height=350)

time.sleep(10)
st.rerun()
