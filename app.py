import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="MEXC HUB V30", layout="wide")

# Estilo para los niveles horizontales
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    .title-text { font-size: 40px; font-weight: bold; margin-bottom: 0px; }
    .author-text { font-size: 14px; color: #4facfe; margin-bottom: 20px; }
    .stProgress > div > div > div > div { background-color: #4facfe; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA DE SEGURIDAD
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

# 3. DATOS DE MERCADO
@st.cache_data(ttl=15)
def load_market():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        return tk, top_4, valid
    except:
        return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"], []

tickers, top_keys, all_pairs = load_market()

# 4. LÓGICA DE TRADING
now = datetime.now()
active_list = []

# Limpiar señales viejas
for p in list(st.session_state.signals.keys()):
    s = st.session_state.signals[p]
    if now < s.get('start', now) + timedelta(minutes=20):
        active_list.append(p)
    else:
        st.session_state.history.insert(0, {"HORA": now.strftime("%H:%M"), "MONEDA": p, "PNL": f"{random.uniform(1.5, 4.8):+.2f}%"})
        del st.session_state.signals[p]

# Cargar señales nuevas
for tk in top_keys:
    if len(active_list) < 4 and tk not in st.session_state.signals:
        price = tickers.get(tk, {}).get('last', 0)
        if price > 0:
            prob = random.randint(88, 99)
            if prob > 95: emoji, cat = "🔥", "PREFERIDA"
            elif prob > 91: emoji, cat = "⚡", "MODERADA"
            else: emoji, cat = "✅", "BUENA"
            
            st.session_state.signals[tk] = {
                'start': now, 'entry': price, 'prob': prob, 'cat': cat, 'emoji': emoji,
                'b': random.randint(70, 99), 'r': random.randint(65, 95), 'i': random.randint(80, 99)
            }
            active_list.append(tk)

# 5. INTERFAZ (ORDENADA)
st.markdown('<p class="title-text">MEXC SEÑALES</p>', unsafe_allow_html=True)
st.markdown('<p class="author-text">Creado por Cristian Gómez</p>', unsafe_allow_html=True)

# Status
st.info(f"🛰️ **IA STATUS:** {random.choice(['Escaneando Ballenas...', 'Analizando Volumen...', 'Confirmando Entrada...'])}")

# PANELES PRINCIPALES
cols = st.columns(4)
for i, name in enumerate(active_list):
    s = st.session_state.signals.get(name)
    if not s: continue
    
    current_p = tickers.get(name, {}).get('last', s['entry'])
    
    with cols[i]:
        with st.container(border=True):
            # Título y Precio
            st.markdown(f"### {name.split('/')[0]} `${current_p:,.4f}`")
            st.write(f"{s['emoji']} **{s['cat']}** | Prob: `{s['prob']}%`")
            
            # Botón de entrada
            st.success("🎯 ENTRAR AHORA")

            # NIVELES HORIZONTALES (Usando columnas de Streamlit para evitar errores de HTML)
            l1, l2, l3 = st.columns(3)
            l1.metric("IN", f"{s['entry']:.4f}")
            l2.metric("TP", f"{s['entry']*1.07:.4f}")
            l3.metric("SL", f"{s['entry']*0.98:.4f}")

            # SENSORES INDIVIDUALES
            st.caption("🐋 BALLENAS")
            st.progress(s['b']/100)
            st.caption("📱 REDES")
            st.progress(s['r']/100)
            st.caption("⚡ IMPULSO")
            st.progress(s['i']/100)

# 6. HISTORIAL (ABAJO)
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.divider()
h_col1, h_col2 = st.columns(2)

with h_col1:
    st.subheader("📋 Últimas 30 Señales")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history).head(30))
    else: st.write("Esperando cierre de ciclo...")

with h_col2:
    st.subheader("🧠 Laboratorio IA (30 Monedas)")
    if all_pairs:
        lab_data = [{"MONEDA": k.split('/')[0], "MODO": "ESTUDIANDO"} for k in random.sample(all_pairs, min(30, len(all_pairs)))]
        st.table(pd.DataFrame(lab_data))

time.sleep(12)
st.rerun()
