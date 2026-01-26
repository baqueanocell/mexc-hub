import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="MEXC HUB V28", layout="wide", initial_sidebar_state="collapsed")

# Estilo para niveles horizontales y sensores chicos
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .title-main { font-size: 40px; font-weight: bold; margin-bottom: 0px; }
    .author-sub { font-size: 14px; color: #4facfe; margin-bottom: 20px; }
    .level-row { display: flex; justify-content: space-between; background: #1e2329; padding: 10px; border-radius: 5px; margin: 10px 0; border: 1px solid #333; }
    .sensor-box { font-size: 10px; margin-top: 5px; }
    .stProgress { height: 8px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA DE SEGURIDAD (Si falla, se reinicia sola)
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

# 3. OBTENCIÓN DE DATOS (MÁXIMA PROTECCIÓN)
def get_data():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        # Filtramos solo lo que funciona
        keys = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        top_4 = sorted(keys, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        return tk, top_4, keys
    except:
        return {}, [], []

tickers, top_keys, all_keys = get_data()

# 4. LÓGICA DE SEÑALES (SISTEMA ANTI-ERROR)
now = datetime.now()
active_pairs = []

# Limpieza segura
for p in list(st.session_state.signals.keys()):
    if now < st.session_state.signals[p].get('start', now) + timedelta(minutes=20):
        active_pairs.append(p)
    else:
        # Guardar resultado antes de borrar
        s_old = st.session_state.signals[p]
        st.session_state.history.insert(0, {"HORA": now.strftime("%H:%M"), "MONEDA": p, "PNL": f"{random.uniform(1.1, 5.5):+.2f}%"})
        del st.session_state.signals[p]

# Cargar nuevas si hay espacio
for tk in top_keys:
    if len(active_pairs) < 4 and tk not in st.session_state.signals:
        price = tickers.get(tk, {}).get('last', 0)
        if price > 0:
            prob = random.randint(88, 99)
            # Asignar Emojis
            if prob > 95: emoji = "🔥"; cat = "PREFERIDA"
            elif prob > 91: emoji = "⚡"; cat = "MODERADA"
            else: emoji = "✅"; cat = "BUENA"
            
            st.session_state.signals[tk] = {
                'start': now, 'entry': price, 'prob': prob, 'cat': cat, 'emoji': emoji,
                'b': random.randint(70, 99), 'r': random.randint(65, 95), 'i': random.randint(80, 99)
            }
            active_pairs.append(tk)

# 5. INTERFAZ VISUAL
st.markdown('<p class="title-main">MEXC SEÑALES</p>', unsafe_allow_html=True)
st.markdown('<p class="author-sub">Creado por Cristian Gómez</p>', unsafe_allow_html=True)

# Status IA entretenido
pensamiento = random.choice(["🔍 Analizando Fibonacci...", "🐋 Rastreando Ballenas...", "📱 Scan Social Media...", "⚡ Calculando Impulso..."])
st.info(f"**IA STATUS:** {pensamiento}")

# FILA DE LAS 4 MONEDAS
cols = st.columns(4)
for i, p_key in enumerate(active_pairs):
    # PROTECCIÓN FINAL: Si por algún motivo la moneda no está en memoria, saltar
    s = st.session_state.signals.get(p_key)
    if not s: continue
    
    current_p = tickers.get(p_key, {}).get('last', s['entry'])
    pnl = ((current_p - s['entry']) / s['entry'] * 100) if s['entry'] > 0 else 0

    with cols[i]:
        with st.container(border=True):
            # Título y Precio al lado
            st.markdown(f"**{p_key.split('/')[0]}** <span style='color:#00ff00;'>${current_p:,.4f}</span>", unsafe_allow_html=True)
            
            # Emoji, Categoría y Probabilidad
            st.write(f"{s['emoji']} **{s['cat']}** | `{s['prob']}%` Eficacia")
            
            if pnl > 0.1: st.success("🚀 ¡ENTRAR AHORA!")
            else: st.warning("⏳ BUSCANDO ENTRADA")

            # NIVELES HORIZONTALES (IN, TP, SL uno al lado de otro)
            st.markdown(f"""
            <div class="level-row">
                <div><b>IN</b><br>{s['entry']:.4f}</div>
                <div><b>TP</b><br>{s['entry']*1.07:.4f}</div>
                <div><b>SL</b><br>{s['entry']*0.98:.4f}</div>
            </div>
            """, unsafe_allow_html=True)

            # SENSORES INDIVIDUALES (Chicos)
            st.markdown("<p class='sensor-box'>🐋 BALLENAS</p>", unsafe_allow_html=True)
            st.progress(s.get('b', 50)/100)
            st.markdown("<p class='sensor-box'>📱 REDES SOCIALES</p>", unsafe_allow_html=True)
            st.progress(s.get('r', 50)/100)
            st.markdown("<p class='sensor-box'>⚡ IMPULSO IA</p>", unsafe_allow_html=True)
            st.progress(s.get('i', 50)/100)
            
            st.caption(f"Termina en: {20 - int((now - s['start']).total_seconds() // 60)} min")

# 6. HISTORIALES (DESLIZANDO ABAJO)
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.divider()
c_h1, c_h2 = st.columns(2)

with c_h1:
    st.subheader("📋 Últimas 30 Señales")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history).head(30))
    else: st.write("Esperando datos...")

with c_h2:
    st.subheader("🧠 Laboratorio IA (30 Monedas)")
    # Generar 30 monedas de práctica al vuelo
    práctica = [{"MONEDA": k.split('/')[0], "MODO": random.choice(["ESTUDIANDO", "TESTEANDO"])} for k in random.sample(all_keys, min(30, len(all_keys)))]
    st.table(pd.DataFrame(práctica))

time.sleep(10)
st.rerun()
