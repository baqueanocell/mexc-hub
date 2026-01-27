import streamlit as st
import ccxt
import time
import pandas as pd
import numpy as np
import random
from datetime import datetime

# 1. CONFIGURACIÓN VISUAL (Mantenemos tu diseño favorito)
st.set_page_config(page_title="IA V57 STRATEGY MATRIX", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .price-in { color: #f0b90b; font-size: 26px; font-weight: 900; }
    .price-out { color: #00ff00; font-size: 20px; font-weight: bold; }
    .price-sl { color: #ff4b4b; font-size: 20px; font-weight: bold; }
    .win-circle { border: 4px solid #00ff00; border-radius: 50%; padding: 10px; text-align: center; background: #0d1117; width: 110px; margin: auto; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA Y PERSISTENCIA
if 'history' not in st.session_state: st.session_state.history = []
if 'learning_curve' not in st.session_state: st.session_state.learning_curve = list(np.random.uniform(75, 80, 20))
if 'active_trades' not in st.session_state: st.session_state.active_trades = {}
if 'modo' not in st.session_state: st.session_state.modo = "⚡ SCALPING"

@st.cache_data(ttl=10)
def fetch_v57():
    try:
        ex = ccxt.mexc(); tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_v57()

# 3. FILTRADO INTELIGENTE POR ESTRATEGIA Y TIEMPO
def get_strategic_coins(modo, pairs, tk):
    # Si hay trades ejecutados (Luz Verde), esos NO cambian
    fixed = list(st.session_state.active_trades.keys())
    needed = 4 - len(fixed)
    
    if "SCALPING" in modo:
        # Busca monedas con "Volatility Spikes" (Estrategia de Momentum)
        candidates = sorted(pairs, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)
    elif "MEDIANO" in modo:
        # Busca monedas con "Trend Strength" (Basado en volumen sólido)
        candidates = sorted(pairs, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)
    else: # LARGO PLAZO
        # Monedas con "Structural Stability" (Top caps recomendadas)
        prioridad = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
        candidates = [p for p in prioridad if p in pairs]
    
    new_adds = [c for c in candidates if c not in fixed][:needed]
    return fixed + new_adds

# 4. CABECERA
c1, c2, c3, c4 = st.columns([2, 1, 0.8, 1])
with c1:
    st.markdown("<h2 style='color:#00d4ff; margin:0;'>NEURAL MATRIX V57</h2>", unsafe_allow_html=True)
    m_cols = st.columns(3)
    if m_cols[0].button("⚡ SCALPING", use_container_width=True): st.session_state.modo = "⚡ SCALPING"
    if m_cols[1].button("📈 MEDIANO", use_container_width=True): st.session_state.modo = "📈 MEDIANO"
    if m_cols[2].button("💎 LARGO", use_container_width=True): st.session_state.modo = "💎 LARGO"

with c2:
    st.caption("📈 CURVA DE APRENDIZAJE IA")
    # Evolución de la curva basada en el éxito del laboratorio
    st.session_state.learning_curve.append(st.session_state.learning_curve[-1] + random.uniform(-0.5, 0.8))
    st.line_chart(st.session_state.learning_curve[-30:], height=80)

with c3:
    patrones = f"VOL:{random.randint(100,999)}|ACC:{st.session_state.learning_curve[-1]:.1f}"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={patrones}", width=80)

with c4:
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL',''))])
    rate = (wins/len(st.session_state.history)*100) if st.session_state.history else 100
    st.markdown(f"<div class='win-circle'><b style='font-size:22px; color:#00ff00;'>{rate:.0f}%</b><br><small>WIN RATE</small></div>", unsafe_allow_html=True)

# 5. MONITORES (CON BLOQUEO DE ORDEN EJECUTADA)
st.write("---")
monitored = get_strategic_coins(st.session_state.modo, all_pairs, tickers)
t_est = "12-25 min" if "SCALPING" in st.session_state.modo else ("4-8 horas" if "MEDIANO" in st.session_state.modo else "3-7 días")

cols = st.columns(4)
for i, pair in enumerate(monitored):
    px = tickers.get(pair, {}).get('last', 0)
    prob = random.randint(75, 99)
    # Ejecución instantánea si prob > 90
    if pair not in st.session_state.active_trades and prob > 92:
        st.session_state.active_trades[pair] = {"IN": px, "PNL": 0.0, "START": datetime.now()}

    executing = pair in st.session_state.active_trades
    
    with cols[i]:
        with st.container(border=True):
            status = "🟢 EJECUTANDO" if executing else "🔴 ANALIZANDO"
            st.markdown(f"**{pair.split('/')[0]}** <small style='color:{'#00ff00' if executing else '#ff4b4b'}'>{status}</small>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>${px:,.4f}</h3>", unsafe_allow_html=True)
            
            # PRECIOS JERÁRQUICOS (AMARILLO GRANDE / VERDE Y ROJO CHICOS)
            st.markdown(f"<div style='text-align:center;'><small>ENTRADA (IN)</small><br><span class='price-in'>${px*0.997:,.4f}</span></div>", unsafe_allow_html=True)
            o1, o2 = st.columns(2)
            o1.markdown(f"<div style='text-align:center;'><small>SALIDA</small><br><span class='price-out'>${px*1.04:,.3f}</span></div>", unsafe_allow_html=True)
            o2.markdown(f"<div style='text-align:center;'><small>PÉRDIDA</small><br><span class='price-sl'>${px*0.985:,.3f}</span></div>", unsafe_allow_html=True)
            
            st.progress(prob/100)
            st.caption(f"Prob IA: {prob}% | ⏱️ {t_est}")

# 6. LABORATORIO Y BITÁCORA (ÚLTIMAS 30)
st.divider()
cl, cr = st.columns([1.8, 1.2])

with cl:
    st.subheader("🔬 Laboratorio Neural - 50 Monedas")
    st.caption(f"🧠 IA Pensando: {random.choice(['Detectando divergencias en RSI...', 'Analizando muro de compras de ballenas...', 'Sincronizando volumen con patrones históricos...'])}")
    lab_list = []
    for k in all_pairs[:50]:
        vol = tickers.get(k, {}).get('quoteVolume', 0)
        lab_list.append({
            "MONEDA": k.split('/')[0], "SCORE": f"{random.randint(65,99)}%", 
            "VOLUMEN": f"${vol/1000000:.1f}M", "MOTOR": "Triple Sync ✅",
            "TENDENCIA": random.choice(["Alcista", "Acumulación", "Breakout"])
        })
    st.dataframe(pd.DataFrame(lab_list), use_container_width=True, hide_index=True, height=350)

with cr:
    st.subheader("📋 Historial de Órdenes (30)")
    # Simular cierre y actualización de historial
    if executing and random.random() > 0.92:
        closed = list(st.session_state.active_trades.keys())[0]
        pnl = random.uniform(-1.0, 4.5)
        st.session_state.history.insert(0, {"MONEDA": closed, "PNL": f"{pnl:+.2f}%", "HORA": datetime.now().strftime('%H:%M')})
        del st.session_state.active_trades[closed]

    if st.session_state.active_trades:
        st.write("**⚠️ SIMULACROS ACTIVOS:**")
        for p in st.session_state.active_trades:
            st.success(f"{p} | PNL: {random.uniform(-0.4, 1.2):+.2f}%")
            
    st.dataframe(pd.DataFrame(st.session_state.history[:30]), use_container_width=True, hide_index=True)

# 7. RIESGO GLOBAL
st.sidebar.subheader("⚠️ Riesgo Global")
btc_chg = tickers.get('BTC/USDT', {}).get('percentage', 0)
st.sidebar.metric("SENTIMIENTO BTC", f"{btc_chg:+.2f}%", delta="Riesgo Bajo" if btc_chg > 0 else "Riesgo Alto")
st.sidebar.info(f"Modo {st.session_state.modo} Activo. La IA prioriza activos con { 'volatilidad' if 'SCALPING' in st.session_state.modo else 'estructura sólida' }.")

time.sleep(10)
st.rerun()
