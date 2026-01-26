import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta

# 1. Configuración de Refresco de 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="MEXC Inteligencia IA", layout="wide")

# CSS Avanzado para "Cards" pequeñas (2 por fila) y barras micro
st.markdown("""
    <style>
    .main { background-color: #080a0f; }
    .stProgress > div > div > div > div { height: 3px !important; border-radius: 2px; }
    
    /* Estilo de Tarjeta Compacta */
    .coin-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 8px;
        margin-bottom: 8px;
    }
    
    .coin-name { color: #ffffff; font-size: 13px; font-weight: bold; }
    .coin-price { color: #58a6ff; font-size: 13px; float: right; font-family: monospace; }
    .bar-label { font-size: 9px; color: #8b949e; margin-top: 2px; margin-bottom: -4px; text-transform: uppercase; }
    
    /* Ajuste de márgenes para que entren 2 */
    .block-container { padding: 0.5rem 1rem !important; }
    div[data-testid="column"] { padding: 0px 4px !important; }
    </style>
    """, unsafe_allow_html=True)

exchange = ccxt.mexc()

# Lógica de Historial Persistente
if 'historial_ia' not in st.session_state:
    st.session_state.historial_ia = []
if 'proximo_analisis' not in st.session_state:
    st.session_state.proximo_analisis = datetime.now()

def obtener_datos_pro():
    try:
        tickers = exchange.fetch_tickers()
        # Seleccionamos Top volumen + nuestra moneda especial
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top_df = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(9)
        
        simbolos = list(top_df['symbol'].values)
        if 'VEREM/USDT' not in simbolos:
            simbolos.insert(0, 'VEREM/USDT') # Forzamos VEREM al inicio
        
        final_data = []
        for symbol in simbolos[:10]: # Mantenemos el Top 10 incluyendo VEREM
            if symbol in tickers:
                t = tickers[symbol]
                p = t['last']
                ch = t['percentage'] or 0
                
                final_data.append({
                    "sym": symbol.replace('/USDT', ''),
                    "price": p,
                    "soc": min(max(70 + (ch * 1.5), 10), 98), # Simulación IA
                    "ball": 75 + (ch * 0.2),
                    "imp": min(max(float(ch) + 50, 5), 98),
                    "tp": p * 1.025,
                    "sl": p * 0.988
                })
        
        # Registro en historial cada 20 minutos
        ahora = datetime.now()
        if ahora >= st.session_state.proximo_analisis:
            if final_data:
                pick = max(final_data, key=lambda x: x['imp'])
                st.session_state.historial_ia.insert(0, {
                    "Hora": ahora.strftime("%H:%M"),
                    "Moneda": pick['sym'],
                    "Señal": "COMPRA" if pick['imp'] > 50 else "NEUTRAL",
                    "Precio": pick['price']
                })
                st.session_state.proximo_analisis = ahora + timedelta(minutes=20)
                
        return final_data
    except: return []

# --- INTERFAZ ---
st.markdown(f"### 🤖 MEXC INTELIGENCIA IA <span style='float:right; font-size:12px; color:#8b949e;'>REFRESCO 10S</span>", unsafe_allow_html=True)

items = obtener_datos_pro()

# Grilla 2x5 (Dos columnas de tarjetas)
cols = st.columns(2)
for idx, m in enumerate(items):
    with cols[idx % 2]:
        st.markdown(f"""
        <div class="coin-card">
            <span class="coin-name">{m['sym']}</span> 
            <span class="coin-price">${m['price']}</span>
            <div class="bar-label">Social IA</div>
            <div style="height:10px"></div>
        </div>
        """, unsafe_allow_html=True)
        # Ponemos las barras justo debajo de cada etiqueta dentro de la columna
        st.progress(m['soc']/100)
        st.markdown('<div class="bar-label">Ballenas</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="bar-label">Impulso</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)
        st.markdown(f"<div style='font-size:10px; margin-top:5px; color:#3fb950;'>TP: {m['tp']:.4f} | <span style='color:#f85149;'>SL: {m['sl']:.4f}</span></div>", unsafe_allow_html=True)

st.write("---")

# --- HISTORIAL DE RECOMENDACIONES ---
st.subheader("📜 Registro de Señales (Cada 20M)")
if st.session_state.historial_ia:
    df_hist = pd.DataFrame(st.session_state.historial_ia).head(10)
    st.table(df_hist)
else:
    st.info("Iniciando análisis de mercado... Primera señal en camino.")
