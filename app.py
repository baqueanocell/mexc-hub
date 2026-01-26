import streamlit as st
import ccxt
import time

# 1. CONFIGURACIÓN LIMPIA
st.set_page_config(page_title="IA TERMINAL V4.7", layout="wide")

# Estilo básico para fondo negro y letras blancas
st.markdown("<style> .stApp {background-color: #000000;} h1,h2,h3,p {color: white !important;} </style>", unsafe_allow_html=True)

# 2. LÓGICA DE DATOS (Precios de Entrada/Salida)
if 'reloj' not in st.session_state: st.session_state.reloj = time.time()
minutos_activos = int((time.time() - st.session_state.reloj) // 60) + 1

DATOS = {
    'VEREM': {'in': 128.16, 'tgt': 132.65, 'sl': 125.80, 't': minutos_activos},
    'BTC':   {'in': 87746.0, 'tgt': 90817.0, 'sl': 86166.0, 't': 15},
    'ETH':   {'in': 2890.72, 'tgt': 2991.90, 'sl': 2838.69, 't': 45},
    'SOL':   {'in': 122.37, 'tgt': 126.65, 'sl': 120.17, 't': 3}
}

# 3. HEADER
st.title("🛰️ IA TERMINAL ELITE | CONTROL TOTAL")
st.success(f"🧠 PENSAMIENTO IA: Sistema sincronizado. Monitoreando MEXC en tiempo real... (Activo hace {minutos_activos} min)")

# 4. CUADROS DE SEÑALES (Usando columnas nativas para evitar errores de texto)
cols = st.columns(4)

# Intentar obtener precios reales
precios_mexc = {}
try:
    exchange = ccxt.mexc()
    ticks = exchange.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    for k, v in ticks.items(): precios_mexc[k.split('/')[0]] = v['last']
except:
    pass

for i, (moneda, info) in enumerate(DATOS.items()):
    p_actual = precios_mexc.get(moneda, 0.0)
    pnl = ((p_actual - info['in']) / info['in'] * 100) if p_actual > 0 else 0.0
    
    with cols[i]:
        # Contenedor visual simple
        with st.container(border=True):
            # Título y Tiempo
            st.markdown(f"### {moneda} `{info['t']} min`")
            
            # Precio y PNL
            color_pnl = "green" if pnl >= 0 else "red"
            st.markdown(f"## ${p_actual:,.2f}")
            st.markdown(f":{color_pnl}[**{pnl:.2f}%**]")
            
            # FUEGO SI ES RECIENTE
            if info['t'] < 10:
                st.markdown("### 🔥 ¡ENTRAR AHORA!")
            else:
                st.markdown("⏳ MONITOREANDO")

            st.divider()
            
            # PRECIOS DE OPERACIÓN (Lo que pediste)
            st.write("**NIVELES DE TRADING:**")
            st.info(f"ENTRADA: {info['in']}")
            st.success(f"TARGET: {info['tgt']}")
            st.error(f"STOP: {info['sl']}")

# 5. TABLA DE HISTORIAL (Sin HTML para evitar el error NameError)
st.markdown("---")
st.subheader("📋 RESUMEN DE SEÑALES")
st.table([
    {"ACTIVO": "VEREM/USDT", "DURACIÓN": f"{minutos_activos}m", "ESTADO": "ACTIVA 🔥"},
    {"ACTIVO": "SOL/USDT", "DURACIÓN": "3m", "ESTADO": "FIRE 🔥"},
    {"ACTIVO": "BTC/USDT", "DURACIÓN": "15m", "ESTADO": "TARGET 1 OK"}
])

# 6. REFRESCO AUTOMÁTICO (Método Nativo que NO da error rojo)
time.sleep(15)
st.rerun()
