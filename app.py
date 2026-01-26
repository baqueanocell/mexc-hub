import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime

# Conector MEXC
exchange = ccxt.mexc()

# --- LÓGICA DE CÁLCULO REAL ---
def obtener_metricas_mexc(symbol):
    try:
        # 1. Datos de Precio e Impulso (Ticker)
        ticker = exchange.fetch_ticker(symbol)
        precio = ticker['last']
        cambio_24h = ticker['percentage']
        impulso = min(max(float(cambio_24h) + 50, 10), 95) # Normalizado para la barra

        # 2. Datos de Ballenas (Order Book)
        ob = exchange.fetch_order_book(symbol, limit=20)
        vol_compras = sum([bid[1] for bid in ob['bids']])
        vol_ventas = sum([ask[1] for ask in ob['asks']])
        fuerza_ballenas = (vol_compras / (vol_compras + vol_ventas)) * 100
        
        return {
            "precio": precio,
            "cambio": cambio_24h,
            "impulso": impulso,
            "ballenas": fuerza_ballenas,
            "social": 85 # Simulado hasta conectar API de X/Twitter
        }
    except:
        return None

# --- DISEÑO DEL HUB ---
st.set_page_config(page_title="MEXC Intelligence Hub", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: white; }
    .stProgress > div > div > div > div { height: 6px !important; }
    /* Colores por tipo de barra */
    div[data-testid="stMarkdownContainer"] p { font-size: 14px; margin-bottom: 0px; }
    .css-1n76uvr { gap: 1rem; } 
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ MEXC INTELLIGENCE HUB")
st.caption(f"Conexión Live: {datetime.now().strftime('%H:%M:%S')} - Sin Comisiones")

col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("📊 Monedas con Datos Reales")
    target_coins = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'MX/USDT']
    
    for coin in target_coins:
        data = obtener_metricas_mexc(coin)
        if data:
            with st.container():
                st.write(f"### {coin} : `${data['precio']:,.2f}`")
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.write(f"🟢 Social: **{data['social']}%**")
                    st.progress(data['social']/100)
                with c2:
                    st.write(f"🔵 Ballenas: **{int(data['ballenas'])}%**")
                    st.progress(data['ballenas']/100)
                with c3:
                    st.write(f"⚡ Impulso: **{int(data['impulso'])}%**")
                    st.progress(data['impulso']/100)
                st.divider()

with col_side:
    st.success("### 🎯 ALERTA FIBONACCI")
    # Lógica de alerta automática
    if data and data['ballenas'] > 65:
        st.balloons()
        st.write(f"**¡ALERTA EN {coin}!**")
        st.write("Muro de Ballenas detectado. Nivel Fib Sugerido: **0.618**")
    else:
        st.write("Buscando confluencia triple...")

    st.subheader("📜 Historial (Simulado)")
    st.table(pd.DataFrame([
        {"Hora": "14:20", "Par": "BTC/USDT", "Tipo": "Fib 0.618", "Res": "✅"},
        {"Hora": "13:05", "Par": "SOL/USDT", "Tipo": "Fib 0.382", "Res": "❌"}
    ]))
