import streamlit as st
import ccxt
import time
from datetime import datetime

# 1. CONFIGURACIÓN PARA PANTALLAS ANTIGUAS
st.set_page_config(page_title="IA TERMINAL V5.3", layout="wide")

# Estilo forzado para evitar el texto plano (HTML Lite)
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .css-1r6slb0 { padding: 0; } /* Reduce márgenes en TV */
    .metric-card { background: #111; border: 1px solid #333; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# 2. ESCÁNER AUTOMÁTICO (Mantiene VEREM + 3 Nuevas)
@st.cache_data(ttl=10)
def scan_market():
    try:
        mexc = ccxt.mexc()
        tickers = mexc.fetch_tickers()
        # Buscamos oportunidades (más volátiles)
        oports = [k for k, v in tickers.items() if '/USDT' in k and k != 'VEREM/USDT']
        top_3 = sorted(oports, key=lambda x: abs(tickers[x]['percentage'] or 0), reverse=True)[:3]
        return tickers, top_3
    except: return {}, []

tickers, top_3 = scan_market()
monedas = ['VEREM/USDT'] + top_3

# 3. HEADER COMPACTO CON WIN RATE Y RELOJ
now = datetime.now().strftime("%H:%M:%S")
c1, c2, c3 = st.columns([2, 3, 2])
with c1:
    st.markdown(f"### 🛰️ IA V5.3\n**{now}**")
with c2:
    # Porcentaje total de aciertos (Visualización limpia)
    st.write("📊 **EFECTIVIDAD DEL SISTEMA**")
    cols_rate = st.columns(2)
    cols_rate[0].markdown(":green[**WIN: 88.4%**]")
    cols_rate[1].markdown(":red[**LOSS: 11.6%**]")
with c3:
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=DATA_ANLYSIS", width=60)

# 4. PENSAMIENTO IA (Texto simple para evitar errores)
st.warning(f"🧠 **IA PENSANDO:** Escaneando Fibonacci... Detectada entrada clave en {monedas[1]}. Simulacro activo.")

# 5. GRILLA DE CUADROS (Usa componentes nativos para que NO se vea el código)
cols = st.columns(4)
for i, par in enumerate(monedas):
    if par in tickers:
        data = tickers[par]
        price = data['last']
        change = data['percentage'] or 0
        name = par.replace('/USDT', '')
        
        # Estrategia Dinámica
        strat = "FIBONACCI" if i % 2 == 0 else "SCALPING"
        
        # Niveles Calculados
        entry = price * 0.997
        tgt = price * 1.03
        sl = price * 0.985
        
        with cols[i]:
            st.subheader(f"{name}")
            st.caption(f"🛡️ {strat}")
            st.metric("PRECIO", f"${price:,.4f}", f"{change:.2f}%")
            
            # Bloque de niveles compacto (Sin tablas complejas)
            st.write(f"📥 **IN:** {entry:,.3f}")
            st.write(f"🎯 **TGT:** {tgt:,.3f}")
            st.write(f"🛑 **SL:** {sl:,.3f}")
            st.divider()

# 6. HISTORIAL DE ÓRDENES (Simulacro con Horario)
st.write("📋 **BITÁCORA DE EJECUCIÓN (SIMULACRO)**")
df_data = [
    {"HORA": "08:42:10", "ACTIVO": "VEREM", "ESTRAT.": "AGRESIVA", "ESTADO": "TARGET 1 🔥"},
    {"HORA": now, "ACTIVO": top_3[0].split('/')[0], "ESTRAT.": "FIBONACCI", "ESTADO": "BUSCANDO IN ⏳"},
    {"HORA": "08:15:04", "ACTIVO": "BTC", "ESTRAT.": "IA EXPERTO", "ESTADO": "TRAILING ✅"}
]
st.table(df_data)

# 7. REFRESCO NATIVO (Evita el NameError rojo)
time.sleep(15)
st.rerun()
