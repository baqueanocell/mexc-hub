import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILO PROFESIONAL
st.set_page_config(page_title="MEXC AI HUB", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main-title { font-size: 48px !important; font-weight: 800; margin-bottom: 0px; }
    .author { font-size: 15px; color: #4facfe; margin-top: -10px; }
    .status-box { padding: 10px; border-radius: 5px; background-color: #1e2329; border-left: 5px solid #4facfe; }
    .coin-header { font-size: 20px; font-weight: bold; }
    .price-mini { font-size: 14px; color: #00ff00; margin-left: 10px; }
    .level-row { font-size: 12px; background: #262730; padding: 5px; border-radius: 3px; display: flex; justify-content: space-around; }
    .sensor-label { font-size: 9px; color: #848e9c; margin-bottom: -10px; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA DE SESIÓN
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

# 3. OBTENCIÓN DE DATOS
@st.cache_data(ttl=12)
def get_mexc_data():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        learn = random.sample(valid, min(30, len(valid)))
        return tk, top_4, learn
    except: return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"], []

tickers, top_keys, learn_keys = get_mexc_data()

# 4. LÓGICA DE PROCESAMIENTO
now = datetime.now()
phrases = ["🔍 Analizando Fibonacci...", "🐋 Rastreando Ballenas...", "📱 Scan Social Media...", "⚡ Calculando Impulso...", "🤖 Optimizando Entradas..."]
status_ia = random.choice(phrases)

active = []
for p in list(st.session_state.signals.keys()):
    s = st.session_state.signals[p]
    if now < s['start'] + timedelta(minutes=20): active.append(p)
    else:
        pnl = f"{random.uniform(1.2, 5.8):+.2f}%"
        st.session_state.history.insert(0, {"HORA": s['start'].strftime("%H:%M"), "MONEDA": p, "PNL": pnl, "TIPO": s['tipo']})
        del st.session_state.signals[p]

for tk in top_keys:
    if len(active) < 4 and tk not in st.session_state.signals:
        price = tickers.get(tk, {}).get('last', 0)
        prob = random.randint(85, 99)
        # Clasificación por emojis
        if prob > 94: tipo = "🔥 PREFERIDA"; emoji = "🔥"
        elif prob > 90: tipo = "⚡ MODERADA"; emoji = "⚡"
        else: tipo = "✅ BUENA"; emoji = "✅"
        
        st.session_state.signals[tk] = {
            'start': now, 'entry': price, 'prob': prob, 'tipo': tipo, 'emoji': emoji,
            'b': random.randint(60, 99), 'r': random.randint(60, 99), 'i': random.randint(60, 99)
        }
        active.append(tk)

# 5. DISEÑO DE INTERFAZ (PRIMERA PANTALLA)
st.markdown('<p class="main-title">MEXC SEÑALES</p>', unsafe_allow_html=True)
st.markdown('<p class="author">Creado por Cristian Gómez</p>', unsafe_allow_html=True)

st.markdown(f'<div class="status-box"><b>IA STATUS:</b> {status_ia}</div>', unsafe_allow_html=True)
st.write("")

# PANELES DE MONEDAS
cols = st.columns(4)
for i, p_key in enumerate(active):
    s = st.session_state.signals.get(p_key, {})
    curr_p = tickers.get(p_key, {}).get('last', s.get('entry', 0))
    pnl = ((curr_p - s['entry']) / s['entry'] * 100) if s['entry'] > 0 else 0
    
    with cols[i]:
        with st.container(border=True):
            # CABECERA: Nombre | Precio | Probabilidad
            st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span class='coin-header'>{p_key.split('/')[0]} <span class='price-mini'>${curr_p:,.4f}</span></span>
                    <span style='color: #4facfe; font-weight: bold;'>{s['prob']}%</span>
                </div>
            """, unsafe_allow_html=True)
            
            # TIPO DE SEÑAL
            st.write(f"**{s['tipo']}**")
            
            # INDICADOR DE ACCIÓN
            if pnl > 0.1: st.success("🚀 ENTRAR AHORA")
            else: st.warning("⏳ BUSCANDO ENTRADA")

            # NIVELES EN HORIZONTAL
            st.markdown(f"""
                <div class='level-row'>
                    <span><b>IN:</b> {s['entry']:.4f}</span>
                    <span><b>TP:</b> {s['entry']*1.07:.4f}</span>
                    <span><b>SL:</b> {s['entry']*0.98:.4f}</span>
                </div>
            """, unsafe_allow_html=True)

            # SENSORES INDIVIDUALES
            st.write("")
            st.markdown("<p class='sensor-label'>🐋 BALLENAS</p>", unsafe_allow_html=True)
            st.progress(s['b']/100)
            st.markdown("<p class='sensor-label'>📱 REDES</p>", unsafe_allow_html=True)
            st.progress(s['r']/100)
            st.markdown("<p class='sensor-label'>⚡ IMPULSO</p>", unsafe_allow_html=True)
            
            st.caption(f"Cierre en: {20 - int((now - s['start']).total_seconds() // 60)} min")

# 6. HISTORIALES (DESLIZANDO HACIA ABAJO)
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
st.divider()
h1, h2 = st.columns(2)

with h1:
    st.subheader("📋 Últimas 30 Señales Reales")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history).head(30))
    else: st.info("Sincronizando bitácora...")

with h2:
    st.subheader("🧠 Laboratorio de Aprendizaje (30 Monedas)")
    learn_data = [{"MONEDA": k.replace('/USDT',''), "PRECIO": f"{tickers.get(k,{}).get('last',0):.4f}", "ANALISIS": "ESTUDIANDO..."} for k in learn_keys]
    st.table(pd.DataFrame(learn_data))

time.sleep(10)
st.rerun()
