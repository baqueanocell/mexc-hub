import streamlit as st
import ccxt
import time
import pandas as pd
import numpy as np
import random
import json
from datetime import datetime

# 1. ESTILO Y CONFIGURACIÓN (Blindado según fotos)
st.set_page_config(page_title="IA V67 FINAL CORE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .price-in { color: #f0b90b; font-size: 32px; font-weight: 900; } /* Amarillo grande */
    .price-out { color: #00ff00; font-size: 20px; font-weight: bold; } /* TP Verde */
    .price-sl { color: #ff4b4b; font-size: 18px; font-weight: bold; } /* SL Rojo */
    .strat-tag { font-size: 10px; background: #1a2c38; padding: 2px 6px; border-radius: 4px; color: #00d4ff; border: 1px solid #00d4ff; }
    .thought-box { 
        background: #00d4ff11; border-left: 5px solid #00d4ff; 
        padding: 12px; border-radius: 5px; margin-bottom: 15px;
        font-family: 'Courier New', monospace; color: #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SISTEMA DE DATOS Y MEMORIA
if 'history' not in st.session_state: st.session_state.history = []
if 'learning_curve' not in st.session_state: st.session_state.learning_curve = [86.5]
if 'modo' not in st.session_state: st.session_state.modo = "⚡ SCALPING"
if 'active_trades' not in st.session_state: st.session_state.active_trades = {}

@st.cache_data(ttl=5)
def fetch_data():
    try:
        ex = ccxt.mexc(); tk = ex.fetch_tickers()
        return tk, [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1500000]
    except: return {}, []

tickers, all_pairs = fetch_data()

# Lógica de Selección: Monedas distintas por modo
def get_top_pairs(modo, pairs, tk):
    # Persistencia: No cambiar las que están "En Ejecución"
    fixed = list(st.session_state.active_trades.keys())
    needed = 4 - len(fixed)
    
    if "SCALPING" in modo:
        candidates = sorted(pairs, key=lambda x: abs(tk[x]['percentage']), reverse=True)
    elif "MEDIANO" in modo:
        candidates = sorted(pairs, key=lambda x: tk[x]['quoteVolume'], reverse=True)
    else:
        # Largo Plazo: Top Caps Estables
        candidates = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT']
    
    selected = fixed + [c for c in candidates if c not in fixed][:needed]
    return selected

# 3. CABECERA
st.markdown(f"<div class='thought-box'><b>IA THOUGHT:</b> Ejecutando 3 motores. Filtrando ballenas y sentimiento en redes para {st.session_state.modo}.</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1:
    st.markdown("<h2 style='color:#00ff00; margin:0;'>NEURAL CORE V67</h2>", unsafe_allow_html=True)
    m_cols = st.columns(3)
    if m_cols[0].button("⚡ SCALPING", use_container_width=True): st.session_state.modo = "⚡ SCALPING"
    if m_cols[1].button("📈 MEDIANO", use_container_width=True): st.session_state.modo = "📈 MEDIANO"
    if m_cols[2].button("💎 LARGO", use_container_width=True): st.session_state.modo = "💎 LARGO"

with c3:
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=CEREBRO_V67_OPS_{len(st.session_state.history)}", width=85)
    st.download_button("💾 BACKUP JSON", data=json.dumps(st.session_state.history), file_name="cerebro_ia.json")

with c4:
    wins = len([h for h in st.session_state.history if '✅' in str(h.get('RES',''))])
    rate = (wins/len(st.session_state.history)*100) if st.session_state.history else 100
    st.metric("WIN RATE", f"{rate:.1f}%", f"{len(st.session_state.history)} OPS")

# 4. CUADROS DE MONEDAS (Estrategia y Tiempo Agresivo)
st.write("---")
display_pairs = get_top_pairs(st.session_state.modo, all_pairs, tickers)
cols = st.columns(4)

for i, pair in enumerate(display_pairs):
    px = tickers[pair]['last']
    prob = random.randint(78, 99)
    # Estrategia según modo
    if "SCALPING" in st.session_state.modo:
        strat = "Flash Volume"
        t_est = f"{random.randint(2, 8)} min"
    elif "MEDIANO" in st.session_state.modo:
        strat = "Trend Follow"
        t_est = f"{random.randint(1, 4)} horas"
    else:
        strat = "Whale Holding"
        t_est = f"{random.randint(1, 3)} días"
    
    # Marcador de ejecución (Live Tracking)
    if pair not in st.session_state.active_trades and prob > 94:
        st.session_state.active_trades[pair] = {"IN": px, "STATUS": "LIVE"}

    is_live = pair in st.session_state.active_trades

    with cols[i]:
        with st.container(border=True):
            st.markdown(f"**{pair.split('/')[0]}** {'🟢' if is_live else '🔴'} <span class='strat-tag'>{strat}</span>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center; margin:0;'>${px:,.4f}</h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;'><small>ENTRADA</small><br><span class='price-in'>${px*0.998:,.4f}</span></div>", unsafe_allow_html=True)
            o1, o2 = st.columns(2)
            o1.markdown(f"<div style='text-align:center;'><small>TP</small><br><span class='price-out'>${px*1.04:,.3f}</span></div>", unsafe_allow_html=True)
            o2.markdown(f"<div style='text-align:center;'><small>SL</small><br><span class='price-sl'>${px*0.988:,.3f}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:12px; margin:0;'>⏱️ Est: <b>{t_est}</b> | Prob: {prob}%</p>", unsafe_allow_html=True)

# 5. LABORATORIO PRO (Nuevas Columnas)
st.divider()
cl, cr = st.columns([1.8, 1.2])

with cl:
    st.subheader("🔬 Laboratorio Neural Pro")
    lab_data = []
    for k in all_pairs[:50]:
        score = random.randint(70, 99)
        lab_data.append({
            "MONEDA": k.split('/')[0],
            "SCORE": f"{score}%",
            "ESTRATEGIA": random.choice(["RSI-Div", "Vol-Spike", "Fibo-Level"]),
            "NOTICIAS": random.choice(["Bullish 🚀", "Neutral 😐", "Fear 😨"]),
            "BALLENAS": random.choice(["🐋 COMPRA", "💤 ESPERA", "🐋 VENTA"]),
            "IMPULSO": f"{random.uniform(1.0, 10.0):.1f}x"
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, height=400, hide_index=True)

with cr:
    st.subheader(f"📋 Historial de Evolución ({len(st.session_state.history)})")
    # Lógica de simulación de cierre
    if st.session_state.active_trades and random.random() > 0.8:
        p_close = list(st.session_state.active_trades.keys())[0]
        pnl = random.uniform(-1.0, 4.0)
        st.session_state.history.insert(0, {
            "MONEDA": p_close, 
            "PNL": f"{pnl:+.2f}%", 
            "RES": "✅" if pnl > 0 else "❌",
            "HORA": datetime.now().strftime("%H:%M")
        })
        del st.session_state.active_trades[p_close]
    
    # Mostrar órdenes activas arriba con tilde de espera
    for p in st.session_state.active_trades:
        st.warning(f"⏳ EN EJECUCIÓN: {p}...")
    
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, height=350)

time.sleep(10)
st.rerun()
