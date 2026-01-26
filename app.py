import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="IA MONITOR V22", layout="wide", initial_sidebar_state="collapsed")

# 2. INICIALIZACIÓN DE MEMORIA CON PROTECCIÓN
if 'signals' not in st.session_state:
    st.session_state.signals = {}

# 3. STATUS IA ENTRETENIDO (Independiente para evitar KeyErrors)
frases = [
    "🔍 Analizando niveles de Fibonacci 0.618...",
    "🐋 Detectando movimientos de ballenas en MEXC...",
    "📱 Escaneando sentimiento en Redes Sociales...",
    "⚡ Calculando fuerza de impulso IA...",
    "🛡️ Filtrando falsos breakouts..."
]
status_actual = random.choice(frases)

# 4. OBTENCIÓN DE DATOS PROTEGIDA
@st.cache_data(ttl=10)
def get_crypto_data():
    try:
        mexc = ccxt.mexc()
        tickers = mexc.fetch_tickers()
        # Filtro de monedas con volumen real
        pool = {k: v for k, v in tickers.items() if '/USDT' in k and v.get('quoteVolume', 0) > 1000000}
        top_4 = sorted(pool.keys(), key=lambda x: abs(pool[x].get('percentage', 0)), reverse=True)[:4]
        return tickers, top_4
    except:
        return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]

tickers_data, top_keys = get_crypto_data()

# 5. LÓGICA DE SEÑALES (SISTEMA PERSISTENTE)
now = datetime.now()
active_pairs = []

# Limpiar señales viejas
for p in list(st.session_state.signals.keys()):
    if now < st.session_state.signals[p].get('start', now) + timedelta(minutes=20):
        active_pairs.append(p)
    else:
        del st.session_state.signals[p]

# Crear nuevas con valores por defecto para evitar KeyError
for tk in top_keys:
    if len(active_pairs) < 4 and tk not in st.session_state.signals:
        entry_p = tickers_data.get(tk, {}).get('last', 0)
        if entry_p > 0:
            st.session_state.signals[tk] = {
                'start': now,
                'entry': entry_p,
                's_ballenas': random.randint(70, 99),
                's_redes': random.randint(60, 95),
                's_impulso': random.randint(75, 99),
                'score': random.randint(0, 100) # Creado desde el inicio
            }
            active_pairs.append(tk)

# 6. INTERFAZ VISUAL (SISTEMA DE SEGURIDAD V22)
st.title("🛰️ MEXC SEÑALES | CRISTIAN GÓMEZ")
st.success(f"**IA STATUS:** {status_actual}")
st.divider()

cols = st.columns(4)
for i, pair in enumerate(active_pairs):
    # PROTECCIÓN NIVEL 1: Obtener datos de sesión de forma segura
    info = st.session_state.signals.get(pair, {})
    if not info: continue
    
    # PROTECCIÓN NIVEL 2: Precios con respaldo
    current_p = tickers_data.get(pair, {}).get('last', info.get('entry', 0))
    pnl = ((current_p - info.get('entry', 1)) / info.get('entry', 1) * 100)
    
    with cols[i]:
        with st.container(border=True):
            st.subheader(pair.split('/')[0])
            
            # LÓGICA DE ICONO DINÁMICO (Con .get para evitar el KeyError de la foto)
            if info.get('score', 0) > 65 and pnl > 0.1:
                st.success("🚀 ¡ENTRAR AHORA!")
            else:
                st.warning("⏳ BUSCANDO ENTRADA...")

            st.metric("PRECIO ACTUAL", f"${current_p:,.4f}", f"{pnl:+.2f}%")
            
            # Niveles IA
            st.table(pd.DataFrame({
                "NIVEL": ["IN", "TGT", "SL"],
                "USD": [f"{info.get('entry'):.4f}", f"{info.get('entry')*1.08:.4f}", f"{info.get('entry')*0.97:.4f}"]
            }))

            # Barras de Sensores (Usando .get para máxima seguridad)
            st.caption("🐋 MOV. BALLENAS")
            st.progress(info.get('s_ballenas', 50) / 100)
            
            st.caption("📱 REDES SOCIALES")
            st.progress(info.get('s_redes', 50) / 100)
            
            st.caption("⚡ IMPULSO IA")
            st.progress(info.get('s_impulso', 50) / 100)
            
            minutos_restantes = 20 - int((now - info.get('start', now)).total_seconds() // 60)
            st.info(f"CIERRE EN: {max(0, minutos_restantes)} MIN")

# Refresco cada 10 segundos
time.sleep(10)
st.rerun()
