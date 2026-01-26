import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import time

# Configuración de la conexión
exchange = ccxt.mexc()

# --- AUTO-REFRESCO (Cada 30 segundos) ---
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=30000, key="datarefresh")

def obtener_datos(symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        ob = exchange.fetch_order_book(symbol, limit=10)
        compras = sum([b[1] for b in ob['bids']])
        ventas = sum([a[1] for a in ob['asks']])
        fuerza_ballenas = (compras / (compras + ventas)) * 100
        return {
            "precio": ticker['last'],
            "cambio": ticker['percentage'],
            "ballenas": fuerza_ballenas
        }
    except: return None

# --- UI ---
st.set_page_config(page_title="MEXC Intelligence Hub", layout="wide")
st.title("🛡️ MEXC INTELLIGENCE HUB")
st.caption(f"MODO LIVE | Última actualización: {datetime.now().strftime('%H:%M:%S')}")

col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("📊 Monitor de Confluencia")
    monedas = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    datos_actuales = {}
    
    for coin in monedas:
        d = obtener_datos(coin)
        if d:
            datos_actuales[coin] = d
            with st.container():
                st.write(f"### {coin}: **${d['precio']:,.2f}**")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"🔵 Ballenas: {int(d['ballenas'])}%")
                    st.progress(d['ballenas']/100)
                with c2:
                    st.write(f"⚡ Impulso: {int(d['cambio']+50)}%")
                    st.progress(min(max((d['cambio']+50)/100, 0), 1))
                st.divider()

with col_side:
    st.success("### 🚀 SEÑALES DE IA")
    # Lógica de señales reales
    for coin, d in datos_actuales.items():
        if d['ballenas'] > 65 and d['cambio'] > 0:
            st.warning(f"🔥 COMPRA SUGERIDA: {coin}")
            st.write(f"Precio: ${d['precio']}")
    
    st.subheader("📜 Historial de Sesión")
    # Aquí creamos una tabla que simula el registro de la sesión actual
    registro = []
    for coin, d in datos_actuales.items():
        if d['ballenas'] > 50:
            registro.append({"Hora": datetime.now().strftime('%H:%M'), "Moneda": coin, "Fuerza": f"{int(d['ballenas'])}%", "Estado": "Analizando"})
    
    st.table(pd.DataFrame(registro))
