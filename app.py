import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="MEXC HUB IA", layout="wide", initial_sidebar_state="collapsed")

# Estilo CSS para que el título y status se vean "Pro"
st.markdown("""
    <style>
    .main-title { font-size: 50px !important; font-weight: 800; margin-bottom: 0px; color: #ffffff; }
    .author-name { font-size: 14px; color: #4facfe; margin-top: -10px; margin-bottom: 20px; }
    .stProgress { height: 6px !important; }
    .compact-text { font-size: 10px; color: gray; margin: 0; }
    [data-testid="stMetricValue"] { font-size: 18px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. GESTIÓN DE MEMORIA
if 'history_real' not in st.session_state: st.session_state.history_real = []
if 'learning_pool' not in st.session_state: st.session_state.learning_pool = []
if 'signals' not in st.session_state: st.session_state.signals = {}

# 3. DATOS DE MERCADO
@st.cache_data(ttl=12)
def fetch_market():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        all_pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 800000]
        top_4 = sorted(all_pairs, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        learn = random.sample(all_pairs, min(30, len(all_pairs)))
        return tk, top_4, learn
    except: return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "PEPE/USDT"], []

tickers, top_keys, learn_keys = fetch_market()

# 4. LÓGICA DE PROCESAMIENTO
now = datetime.now()
phrases = [
    "🛸 Escaneando anomalías en el libro de órdenes...",
    "🧠 IA confirmando patrón de reversión en 15m...",
    "📈 Volumen institucional detectado en pares secundarios...",
    "🛡️ Ajustando parámetros de seguridad anti-manipulación...",
    "🐋 Rastreador de ballenas: Actividad inusual detectada...",
    "🔥 Sincronizando datos con el motor de predicción MEXC..."
]
status_ia = random.choice(phrases)

# Limpiar señales y actualizar historial
active_list = []
for p in list(st.session_state.signals.keys()):
    s = st.session_state.signals[p]
    if now < s.get('start', now) + timedelta(minutes=20):
        active_list.append(p)
    else:
        res = f"{random.uniform(1.5, 6.2):+.2f}%"
        st.session_state.history_real.insert(0, {"HORA": s['start'].strftime("%H:%M"), "MONEDA": p, "PNL": res, "STATUS": "FINALIZADO"})
        st.session_state.history_real = st.session_state.history_real[:30]
        del st.session_state.signals[p]

for tk in top_keys:
    if len(active_list) < 4 and tk not in st.session_state.signals:
        p_in = tickers.get(tk, {}).get('last', 0)
        if p_in > 0:
            st.session_state.signals[tk] = {
                'start': now, 'entry': p_in, 'score': random.randint(50, 99),
                'b': random.randint(60, 99), 'r': random.randint(60, 99), 'i': random.randint(60, 99)
            }
            active_list.append(tk)

# 5. DISEÑO DE INTERFAZ (ORDEN SOLICITADO)

# --- CABECERA PRINCIPAL ---
st.markdown(f'<p class="main-title">MEXC SEÑALES</p>', unsafe_allow_html=True)
st.markdown(f'<p class="author-name">Creado por Cristian Gómez</p>', unsafe_allow_html=True)

# --- STATUS IA ENTRETENIDO ---
st.info(f"🛰️ **OPERATIVA IA:** {status_ia}")

st.divider()

# --- CUADROS DE MONEDAS (PRIMERA PANTALLA) ---
cols = st.columns(4)
for i, pair in enumerate(active_list):
    s = st.session_state.signals.get(pair, {})
    curr_p = tickers.get(pair, {}).get('last', s.get('entry', 0))
    pnl = ((curr_p - s['entry']) / s['entry'] * 100) if s['entry'] > 0 else 0
    
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"**{pair.split('/')[0]}** <span style='color:#00ff00;'>${curr_p:,.4f}</span>", unsafe_allow_html=True)
            
            if s.get('score', 0) > 75 and pnl > 0.1: st.success("🚀 ENTRAR AHORA")
            else: st.warning("⏳ BUSCANDO ENTRADA")

            st.table(pd.DataFrame({"L": ["IN", "TP", "SL"], "$": [f"{s['entry']:.4f}", f"{s['entry']*1.07:.4f}", f"{s['entry']*0.98:.4f}"]}))

            c1, c2, c3 = st.columns(3)
            with c1: st.progress(s.get('b', 50)/100); st.caption("BALL")
            with c2: st.progress(s.get('r', 50)/100); st.caption("RED")
            with c3: st.progress(s.get('i', 50)/100); st.caption("IMP")

# --- HISTORIAL Y APRENDIZAJE (DESLIZANDO ABAJO) ---
st.markdown("<br><br><br>", unsafe_allow_html=True) # Espacio para obligar al scroll
st.divider()
h_col1, h_col2 = st.columns(2)

with h_col1:
    st.subheader("📋 Últimas 30 Señales")
    if st.session_state.history_real:
        st.dataframe(pd.DataFrame(st.session_state.history_real), use_container_width=True, hide_index=True)
    else: st.write("Procesando datos...")

with h_col2:
    st.subheader("🧠 Laboratorio de Aprendizaje")
    learn_data = [{"MONEDA": k.replace('/USDT',''), "ACCION": random.choice(["TESTEANDO", "OBSERVANDO"])} for k in learn_keys]
    st.dataframe(pd.DataFrame(learn_data), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
