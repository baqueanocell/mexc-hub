import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Refresco cada 20 minutos (1,200,000 milisegundos)
st_autorefresh(interval=1200000, key="trade_timer")

st.set_page_config(page_title="MEXC Intelligence Slim", layout="wide")

# CSS para barras pequeñas y diseño minimalista
st.markdown("""
    <style>
    .stProgress > div > div > div > div { height: 4px !important; background-color: #00ffcc; }
    .stExpander { border: 1px solid #30363d !important; background-color: #0d1117 !important; }
    h3 { font-size: 1rem !important; margin-bottom: 5px; color: #e6edf3; }
    p { font-size: 0.85rem !important; margin: 0px; }
    </style>
    """, unsafe_allow_html=True)

exchange = ccxt.mexc()

def calcular_niveles(precio):
    entrada = float(precio)
    tp = entrada * 1.03  # +3%
    sl = entrada * 0.985 # -1.5%
    return entrada, tp, sl

def obtener_top_slim():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top_10 = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(10)
        
        datos = []
        for symbol in top_10['symbol']:
            t = tickers[symbol]
            cambio = t['percentage'] if t['percentage'] else 0
            # Barras reales
            impulso = min(max(float(cambio) + 50, 5), 95)
            # Ballenas simplificado para velocidad
            sentimiento = min(max(50 + (cambio * 2), 10), 95)
            
            entrada, tp, sl = calcular_niveles(t['last'])
            
            datos.append({
                "S": symbol.replace('/USDT', ''),
                "P": t['last'],
                "Sent": sentimiento,
                "Ball": 65, # Base estable
                "Imp": impulso,
                "Entrada": entrada, "TP": tp, "SL": sl
            })
        return datos
    except: return []

st.title("🛡️ MEXC SLIM HUB - ESTRATEGIA 20M")
st.caption(f"Próxima actualización de niveles: {datetime.now().strftime('%H:%M:%S')}")

items = obtener_top_slim()

col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("📊 Top 10 Monedas (Barras Slim)")
    for i in items:
        with st.container():
            c_info, c_bars = st.columns([1, 2])
            with c_info:
                st.write(f"**{i['S']}**: `${i['P']:,.4f}`")
            with c_bars:
                # Triple barra mini
                st.progress(i['Sent']/100)
                st.progress(i['Ball']/100)
                st.progress(i['Imp']/100)
            st.divider()

with col_side:
    st.warning("### 🎯 PROPUESTA DE TRADING")
    if items:
        # Sugerimos la moneda con más impulso
        pick = max(items, key=lambda x: x['Imp'])
        st.write(f"**Activo:** {pick['S']}/USDT")
        st.write(f"🛒 **Entrada:** `${pick['Entrada']:,.4f}`")
        st.write(f"✅ **Take Profit:** `${pick['TP']:,.4f}`")
        st.write(f"🛑 **Stop Loss:** `${pick['SL']:,.4f}`")
        st.info("Niveles válidos por los próximos 20 minutos.")
    
    st.divider()
    st.subheader("📑 Resumen de Objetivos")
    st.table(pd.DataFrame(items)[['S', 'TP', 'SL']].head(5))
