import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Refresco cada 20 min para recalcular señales
st_autorefresh(interval=1200000, key="trade_timer")

st.set_page_config(page_title="MEXC Intelligence Micro", layout="wide")

# Estilo Ultra-Slim
st.markdown("""
    <style>
    .stProgress > div > div > div > div { height: 3px !important; }
    .stMarkdown p { font-size: 0.75rem !important; line-height: 1.2 !important; margin: 0px !important; }
    .css-1r6slb0 { padding: 0.5rem 1rem; }
    div[data-testid="stExpander"] { border: none !important; background: transparent !important; }
    hr { margin: 0.5em 0px !important; }
    </style>
    """, unsafe_allow_html=True)

exchange = ccxt.mexc()

def obtener_data():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top_10 = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(10)
        
        lista = []
        for symbol in top_10['symbol']:
            t = tickers[symbol]
            cambio = t['percentage'] if t['percentage'] else 0
            
            # Cálculos de barras
            sent = min(max(50 + (cambio * 1.5), 10), 95)
            imp = min(max(float(cambio) + 50, 5), 95)
            
            # Ballenas (Lógica de Order Book rápida)
            ob = exchange.fetch_order_book(symbol, limit=5)
            b = (sum([bid[1] for bid in ob['bids']]) / (sum([bid[1] for bid in ob['bids']]) + sum([ask[1] for ask in ob['asks']]))) * 100
            
            precio = t['last']
            lista.append({
                "S": symbol.replace('/USDT', ''), "P": precio,
                "Sent": sent, "Ball": b, "Imp": imp,
                "TP": precio * 1.025, "SL": precio * 0.988
            })
        return lista
    except: return []

st.title("⚡ MEXC MICRO-HUB")
data = obtener_data()

col1, col2 = st.columns([1.5, 1])

with col1:
    st.write("### 📊 Top 10 Performance")
    for m in data:
        c_label, c_s, c_b, c_i = st.columns([1, 1, 1, 1])
        with c_label: st.write(f"**{m['S']}** `${m['P']}`")
        with c_s: 
            st.caption(f"Soc: {int(m['Sent'])}%")
            st.progress(m['Sent']/100)
        with c_b: 
            st.caption(f"Ball: {int(m['Ball'])}%")
            st.progress(m['Ball']/100)
        with c_i: 
            st.caption(f"Imp: {int(m['Imp'])}%")
            st.progress(m['Imp']/100)
        st.divider()

with col2:
    # LÓGICA DE LA MEJOR MONEDA
    if data:
        mejor = max(data, key=lambda x: x['Ball'] + x['Imp'])
        st.error(f"### 🚀 MEJOR OPORTUNIDAD: {mejor['S']}")
        
        # Tarjeta de Señal
        st.info(f"""
        **NIVELES PARA LOS PRÓXIMOS 20M:**
        - 🛒 **Entrada:** ${mejor['P']}
        - ✅ **Take Profit:** ${mejor['TP']:.4f}
        - 🛑 **Stop Loss:** ${mejor['SL']:.4f}
        """)
        
        st.write("---")
        st.subheader("🎯 Resumen TP/SL")
        resumen = pd.DataFrame(data)[['S', 'TP', 'SL']].head(6)
        st.table(resumen)
