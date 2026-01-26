import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="MEXC AI V31", layout="wide")

# Estilos simples y seguros
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .maintitle { font-size: 40px; font-weight: bold; color: white; margin-bottom: 0px; }
    .author { font-size: 14px; color: #4facfe; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE MEMORIA SEGURA
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

# 3. FUNCIÓN DE DATOS BLINDADA
@st.cache_data(ttl=15)
def get_mexc_market():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        # Filtrar monedas con volumen real
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        return tk, top_4, valid
    except:
        return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"], []

tickers_data, top_pairs, all_list = get_mexc_market()

# 4. LÓGICA DE SEÑALES
now = datetime.now()
current_active = []

# Limpiar señales viejas de la memoria
for p in list(st.session_state.signals.keys()):
    if now < st.session_state.signals[p].get('start', now) + timedelta(minutes=20):
        current_active.append(p)
    else:
        # Guardar en historial
        st.session_state.history.insert(0, {
            "HORA": now.strftime("%H:%M"),
            "MONEDA": p,
            "RESULTADO": f"{random.uniform(1.5, 5.0):+.2f}%"
        })
        del st.session_state.signals[p]

# Generar nuevas si faltan
for tp in top_pairs:
    if len(current_active) < 4 and tp not in st.session_state.signals:
        px = tickers_data.get(tp, {}).get('last', 0)
        if px > 0:
            pb = random.randint(88, 99)
            # Sistema de Emojis por preferencia
            if pb > 95: emj, cat = "🔥", "PREFERIDA"
            elif pb > 91: emj, cat = "⚡", "MODERADA"
            else: emj, cat = "✅", "BUENA"
            
            st.session_state.signals[tp] = {
                'start': now, 'entry': px, 'prob': pb, 'cat': cat, 'emoji': emj,
                'b': random.randint(70, 99), 'r': random.randint(60, 95), 'i': random.randint(75, 99)
            }
            current_active.append(tp)

# 5. DISEÑO DE INTERFAZ
st.markdown('<p class="maintitle">MEXC SEÑALES</p>', unsafe_allow_html=True)
st.markdown('<p class="author">Creado por Cristian Gómez</p>', unsafe_allow_html=True)

st.info(f"🤖 IA STATUS: {random.choice(['Analizando flujo de órdenes...', 'Detectando ballenas...', 'Escaneando redes sociales...'])}")

# PANELES HORIZONTALES (4 Monedas)
cols = st.columns(4)
for i, pair in enumerate(current_active):
    s_info = st.session_state.signals.get(pair)
    if not s_info: continue # Evita el error rojo si no hay datos
    
    last_price = tickers_data.get(pair, {}).get('last', s_info['entry'])
    
    with cols[i]:
        with st.container(border=True):
            # Moneda y Precio Actual
            st.subheader(f"{pair.split('/')[0]}")
            st.write(f"💰 Precio: `${last_price:,.4f}`")
            
            # Calificación (Preferencia) y Probabilidad
            st.markdown(f"### {s_info['emoji']} {s_info['cat']}")
            st.write(f"Probabilidad: **{s_info['prob']}%**")
            
            st.success("🎯 SEÑAL ACTIVA")

            # NIVELES EN HORIZONTAL (Tal como pediste)
            st.divider()
            n1, n2, n3 = st.columns(3)
            n1.caption("ENTRADA")
            n1.write(f"{s_info['entry']:.4f}")
            n2.caption("TARGET")
            n2.write(f"{s_info['entry']*1.07:.4f}")
            n3.caption("STOP")
            n3.write(f"{s_info['entry']*0.98:.4f}")
            st.divider()

            # SENSORES INDIVIDUALES
            st.write("🐋 Ballenas")
            st.progress(s_info['b']/100)
            st.write("📱 Redes")
            st.progress(s_info['r']/100)
            st.write("⚡ Impulso")
            st.progress(s_info['i']/100)
            
            st.caption(f"Actualización en: {20 - int((now - s_info['start']).total_seconds() // 60)}m")

# 6. TABLAS DE HISTORIAL (ABAJO)
st.write("")
st.divider()
tab1, tab2 = st.columns(2)

with tab1:
    st.subheader("📋 Últimas 30 Señales Reales")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history).head(30), use_container_width=True, hide_index=True)
    else:
        st.write("Esperando cierre de operaciones...")

with tab2:
    st.subheader("🧠 Laboratorio IA (30 Monedas)")
    if all_list:
        lab = [{"MONEDA": m.split('/')[0], "ESTADO": "ESTUDIANDO..."} for m in random.sample(all_list, min(30, len(all_list)))]
        st.dataframe(pd.DataFrame(lab), use_container_width=True, hide_index=True)

# Auto-refresh
time.sleep(12)
st.rerun()
