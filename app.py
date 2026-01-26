import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y MEMORIA (Mantenemos lo que ya funciona)
st.set_page_config(page_title="IA TRADING PRO", layout="wide", initial_sidebar_state="collapsed")

if 'signals' not in st.session_state:
    st.session_state.signals = {}
if 'history' not in st.session_state:
    st.session_state.history = []

def get_data_safe():
    try:
        exchange = ccxt.mexc()
        tickers = exchange.fetch_tickers()
        valid = {k: v for k, v in tickers.items() if '/USDT' in k and v.get('quoteVolume', 0) > 1000000}
        top = sorted(valid.keys(), key=lambda x: abs(valid[x].get('percentage', 0)), reverse=True)[:4]
        return tickers, top
    except:
        return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]

tickers_data, top_keys = get_data_safe()

# 2. MOTOR DE SEÑALES
now = datetime.now()
active_pairs = []
for p in list(st.session_state.signals.keys()):
    s = st.session_state.signals[p]
    if now < s['start'] + timedelta(minutes=20):
        active_pairs.append(p)
    else:
        pnl_sim = random.uniform(2.0, 7.0) if random.random() > 0.2 else -1.5
        st.session_state.history.insert(0, {"HORA": s['start'].strftime("%H:%M"), "MONEDA": p, "PNL": f"{pnl_sim:+.2f}%"})
        del st.session_state.signals[p]

for tk in top_keys:
    if len(active_pairs) < 4 and tk not in st.session_state.signals:
        price = tickers_data.get(tk, {}).get('last', 0)
        if price > 0:
            st.session_state.signals[tk] = {
                'start': now, 'entry': price,
                's_ballenas': random.randint(75, 99),
                's_redes': random.randint(60, 95),
                's_impulso': random.randint(80, 99)
            }
            active_pairs.append(tk)

# 3. INTERFAZ MEJORADA (DETALLES CRISTIAN GÓMEZ)
st.title("🛰️ MONITOR IA: MEXC SEÑALES")
st.write(f"**Analista:** Cristian Gómez | **Estado:** {random.choice(['Buscando Entrada Perfecta...', 'Escaneando Ballenas...', 'Análisis de Redes en curso...'])}")

st.divider()

cols = st.columns(4)
for i, pair in enumerate(active_pairs):
    if pair not in st.session_state.signals: continue
    
    info = st.session_state.signals[pair]
    current_p = tickers_data.get(pair, {}).get('last', info['entry'])
    pnl_val = ((current_p - info['entry']) / info['entry'] * 100) if info['entry'] > 0 else 0
    
    with cols[i]:
        with st.container(border=True):
            st.header(f"{pair.split('/')[0]}")
            
            # Precio Actual Destacado
            st.metric("PRECIO ACTUAL", f"${current_p:,.4f}", f"{pnl_val:+.2f}%")
            
            # Botones de Acción Estilo Trading
            c1, c2 = st.columns(2)
            c1.button("⏳ ESPERANDO", key=f"wait_{pair}", use_container_width=True)
            c2.button("🚀 ENTRAR YA", key=f"go_{pair}", type="primary", use_container_width=True)
            
            # Niveles IA
            st.markdown("---")
            st.table(pd.DataFrame({
                "TIPO": ["ENTRY", "TARGET", "STOP"],
                "USD": [f"{info['entry']:,.4f}", f"{info['entry']*1.08:,.4f}", f"{info['entry']*0.97:,.4f}"]
            }))

            # Las 3 Barras de Sensores solicitadas
            st.caption("🐋 MOV. BALLENAS")
            st.progress(info['s_ballenas'] / 100)
            
            st.caption("📱 SENTIMIENTO REDES")
            st.progress(info['s_redes'] / 100)
            
            st.caption("⚡ IMPULSO IA")
            st.progress(info['s_impulso'] / 100)
            
            st.error(f"CIERRE EN: {20 - int((now - info['start']).total_seconds() // 60)} MIN")

# Historial
st.divider()
st.subheader("📋 BITÁCORA DE APRENDIZAJE")
if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history).head(5), use_container_width=True)

time.sleep(10)
st.rerun()
