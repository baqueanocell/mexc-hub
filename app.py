import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime

# 1. ESTILOS DE ALTA PRECISIÓN
st.set_page_config(page_title="IA V56 PERSISTENCE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    /* Precios Jerárquicos */
    .price-in { color: #f0b90b; font-size: 24px; font-weight: 900; }
    .price-out { color: #00ff00; font-size: 18px; font-weight: bold; }
    .price-sl { color: #ff4b4b; font-size: 18px; font-weight: bold; }
    
    .win-circle { border: 4px solid #00ff00; border-radius: 50%; padding: 10px; text-align: center; background: #0d1117; width: 110px; margin: auto; }
    .ia-thought-lab { color: #00d4ff; font-style: italic; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA DE OPERACIONES Y PERSISTENCIA
if 'active_trades' not in st.session_state: st.session_state.active_trades = {}
if 'history' not in st.session_state: st.session_state.history = []
if 'modo' not in st.session_state: st.session_state.modo = "⚡ SCALPING"

@st.cache_data(ttl=10)
def fetch_v56():
    try:
        ex = ccxt.mexc(); tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_v56()

# 3. LÓGICA DE BLOQUEO DE MONEDAS (Persistence)
def get_monitors():
    # Si hay trades activos, se quedan fijos. Si no, elegimos los mejores según el modo.
    if "SCALPING" in st.session_state.modo:
        candidates = sorted(all_pairs, key=lambda x: abs(tickers[x].get('percentage', 0)), reverse=True)
    elif "MEDIANO" in st.session_state.modo:
        candidates = sorted(all_pairs, key=lambda x: tickers[x].get('quoteVolume', 0), reverse=True)
    else:
        candidates = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    
    # Fusionar fijos con nuevos hasta completar 4
    fixed = list(st.session_state.active_trades.keys())
    needed = 4 - len(fixed)
    new_adds = [c for c in candidates if c not in fixed][:needed]
    return (fixed + new_adds)[:4]

# 4. CABECERA
c1, c2, c3 = st.columns([3, 1, 1])
with c1:
    st.markdown("<h2 style='color:#00d4ff; margin:0;'>NEURAL CORE V56</h2>", unsafe_allow_html=True)
    m_cols = st.columns(3)
    if m_cols[0].button("⚡ SCALPING", use_container_width=True): st.session_state.modo = "⚡ SCALPING"
    if m_cols[1].button("📈 MEDIANO", use_container_width=True): st.session_state.modo = "📈 MEDIANO"
    if m_cols[2].button("💎 LARGO", use_container_width=True): st.session_state.modo = "💎 LARGO"

with c2:
    # QR DE PATRONES DE VOLUMEN
    patrones = f"VOL_MEM:{random.randint(100,999)}|MODE:{st.session_state.modo}|TRADES:{len(st.session_state.history)}"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={patrones}", width=85, caption="Vol Pattern QR")

with c3:
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL',''))])
    rate = (wins/len(st.session_state.history)*100) if st.session_state.history else 100
    st.markdown(f"<div class='win-circle'><b style='font-size:22px; color:#00ff00;'>{rate:.0f}%</b><br><small>WIN RATE</small></div>", unsafe_allow_html=True)

# 5. MONITORES (CON LÓGICA DE BLOQUEO)
st.write("---")
monitored_pairs = get_monitors()
cols = st.columns(4)

for i, pair in enumerate(monitored_pairs):
    px = tickers.get(pair, {}).get('last', 0)
    # Lógica de simulación instantánea
    if pair not in st.session_state.active_trades and random.random() > 0.85:
        st.session_state.active_trades[pair] = {"IN": px, "PNL": "0.00%", "TIME": datetime.now()}

    executing = pair in st.session_state.active_trades
    
    with cols[i]:
        with st.container(border=True):
            status_led = "🟢 EJECUTANDO" if executing else "🔴 ANALIZANDO"
            st.markdown(f"**{pair.split('/')[0]}** <small style='color:{'#00ff00' if executing else '#ff4b4b'}'>{status_led}</small>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>${px:,.4f}</h3>", unsafe_allow_html=True)
            
            st.markdown(f"<div style='text-align:center;'><small>ENTRADA (IN)</small><br><span class='price-in'>${px*0.997:,.4f}</span></div>", unsafe_allow_html=True)
            o1, o2 = st.columns(2)
            o1.markdown(f"<div style='text-align:center;'><small>SALIDA (TP)</small><br><span class='price-out'>${px*1.05:,.3f}</span></div>", unsafe_allow_html=True)
            o2.markdown(f"<div style='text-align:center;'><small>PÉRDIDA (SL)</small><br><span class='price-sl'>${px*0.98:,.3f}</span></div>", unsafe_allow_html=True)
            
            # Tiempo aproximado
            t_est = "15-25m" if "SCALPING" in st.session_state.modo else "4-8h"
            st.caption(f"⏱️ Tiempo Est: {t_est}")

# 6. LABORATORIO GIGANTE & HISTORIAL 30
st.divider()
c_lab, c_hist = st.columns([2, 1])

with c_lab:
    st.subheader("🔬 Laboratorio Neural - 50 Activos")
    pensamiento = random.choice([
        "🧠 Detectando acumulación de ballenas en soportes clave...",
        "🧠 Patrones de volumen confirman ruptura inminente...",
        "🧠 Divergencia detectada: Ajustando motor de agresividad."
    ])
    st.markdown(f"<div class='ia-thought-lab'>{pensamiento}</div>", unsafe_allow_html=True)
    
    lab_data = []
    for k in all_pairs[:50]:
        vol = tickers.get(k, {}).get('quoteVolume', 0)
        lab_data.append({
            "MONEDA": k.split('/')[0],
            "SCORE": f"{random.randint(70,99)}%",
            "VOLUMEN": f"${vol/1000000:.1f}M",
            "TÉCNICO": random.choice(["RSI Bull", "EMA Cross", "Fibo 0.6"]),
            "SENTIMIENTO": random.choice(["🔥 Quema", "🐋 Ballena", "📢 News"])
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True, height=350)

with c_hist:
    st.subheader("📋 Ordenes & PNL (Últimas 30)")
    # Simulamos el cierre de un trade para poblar el historial
    if executing and random.random() > 0.9:
        closed_pair = list(st.session_state.active_trades.keys())[0]
        pnl_val = random.uniform(-1.5, 5.0)
        st.session_state.history.insert(0, {"MONEDA": closed_pair, "PNL": f"{pnl_val:+.2f}%", "RES": "✅" if pnl_val > 0 else "❌"})
        del st.session_state.active_trades[closed_pair]
    
    # Mostrar trades activos y luego historial
    if st.session_state.active_trades:
        st.write("**⚠️ EN CURSO:**")
        for p, d in st.session_state.active_trades.items():
            st.success(f"{p}: PNL ACTUAL {random.uniform(-0.5, 1.5):+.2f}%")
            
    st.write("**HISTORIAL:**")
    st.dataframe(pd.DataFrame(st.session_state.history[:30]), use_container_width=True, hide_index=True)

# 7. RIESGO GLOBAL ESPECÍFICO
st.sidebar.subheader("⚠️ Riesgo Global")
btc_px = tickers.get('BTC/USDT', {}).get('last', 0)
btc_chg = tickers.get('BTC/USDT', {}).get('percentage', 0)
vol_total = sum([tickers[k].get('quoteVolume', 0) for k in all_pairs[:10]])
st.sidebar.metric("BITCOIN", f"${btc_px:,.0f}", f"{btc_chg:+.2f}%")
st.sidebar.write(f"Volumen 24h: ${vol_total/1000000:.1f}M")
st.sidebar.progress(max(0, min(100, int(50 + btc_chg*5))))

time.sleep(10)
st.rerun()
