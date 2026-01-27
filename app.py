import streamlit as st
import ccxt
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CREDENCIALES (Pégalas aquí)
# ==========================================
API_KEY = mx0vglHNLQOSn5bqCk
SECRET_KEY = a4e4387971ac48e1b623992031dd8057
MONTO_USDT = 10 
# ==========================================

st.set_page_config(page_title="IA V71 FULL AUTO", layout="wide")

# Conexión al motor de MEXC
@st.cache_resource
def conectar():
    try:
        return ccxt.mexc({'apiKey': API_KEY, 'secret': SECRET_KEY, 'options': {'defaultType': 'spot'}})
    except: return None

mexc = conectar()

# --- LÓGICA DE CICLO COMPLETO (Compra + Venta Programada) ---
def ciclo_completo_mexc(symbol, p_in, p_tp, p_sl):
    try:
        # 1. Ejecutar Compra al mercado para asegurar entrada inmediata
        qty = MONTO_USDT / p_in
        buy_order = mexc.create_market_buy_order(symbol, MONTO_USDT)
        st.toast(f"✅ COMPRADO: {symbol}", icon='💰')
        
        # Esperar un segundo para que se procese la compra
        import time; time.sleep(1)
        
        # 2. Colocar Orden de Venta (Take Profit)
        # Nota: En MEXC Spot, si no hay OCO disponible via API, colocamos el TP.
        mexc.create_limit_sell_order(symbol, qty, p_tp)
        st.success(f"🎯 VENTA PROGRAMADA (TP): ${p_tp}")
        
        # Guardar en historial real
        st.session_state.history.insert(0, {
            "MONEDA": symbol, "ENTRADA": p_in, "TP": p_tp, "SL": p_sl, "RES": "⏳ LIVE"
        })
    except Exception as e:
        st.error(f"Falla en el ciclo: {e}")

# --- INTERFAZ DE MONITORES ---
st.markdown("<h2 style='color:#00ff00;'>NEURAL CORE V71 - AUTO-EXIT</h2>", unsafe_allow_html=True)

if 'history' not in st.session_state: st.session_state.history = []

cols = st.columns(4)
pares = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'MX/USDT']

for i, p in enumerate(pares):
    with cols[i]:
        with st.container(border=True):
            try:
                # Obtener precio real para los cálculos
                val = mexc.fetch_ticker(p)['last']
                tp = val * 1.02 # +2% Ganancia
                sl = val * 0.99 # -1% Pérdida
            except: val = 0.0; tp=0.0; sl=0.0
            
            st.write(f"**{p}**")
            st.markdown(f"<span style='color:#f0b90b; font-size:24px;'>${val:,.2f}</span>", unsafe_allow_html=True)
            
            if st.button(f"🚀 INICIAR CICLO", key=p):
                ciclo_completo_mexc(p, val, tp, sl)

st.divider()
st.subheader("📋 Registro de Órdenes en MEXC")
st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
