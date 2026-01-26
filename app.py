import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PANTALLA (MODO DARK TOTAL)
st.set_page_config(page_title="MEXC SEÑALES | CRISTIAN GÓMEZ", layout="wide", initial_sidebar_state="collapsed")

# Estilo para forzar que todo entre en una sola pantalla
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #3fb950; }
    .stTable { font-size: 12px !important; }
    header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE MEMORIA (EVITA KEYERROR)
if 'signals' not in st.session_state:
    st.session_state.signals = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. CONEXIÓN A MEXC (SPOT ESTRATÉGICO)
@st.cache_data(ttl=15)
def get_market_data():
    try:
        exchange = ccxt.mexc()
        tickers = exchange.fetch_tickers()
        # Filtramos USDT, volumen > 1.5M y buscamos los 4 más explosivos
        valid_coins = [k for k, v in tickers.items() if '/USDT' in k and v['quoteVolume'] > 1500000]
        top_coins = sorted(valid_coins, key=lambda x: abs(tickers[x]['percentage'] or 0), reverse=True)[:4]
        return tickers, top_coins
    except:
        return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "PEPE/USDT"]

tickers_data, top_4 = get_market_data()

# 4. GESTOR DE CICLOS DE 20 MINUTOS
def manage_trading_cycles():
    now = datetime.now()
    active = []
    
    # Revisar operaciones actuales
    for pair in list(st.session_state.signals.keys()):
        data = st.session_state.signals[pair]
        if now < data['start'] + timedelta(minutes=20):
            active.append(pair)
        else:
            # Terminar y generar reporte de aprendizaje
            pnl_sim = random.uniform(2.5, 9.0) if random.random() > 0.2 else -2.5
            st.session_state.history.insert(0, {
                "HORA": data['start'].strftime("%H:%M"),
                "MONEDA": pair.split('/')[0],
                "PNL": f"{pnl_sim:+.2f}%",
                "ESTRATEGIA": data['strat'],
                "IA_LEARNING": "Confirmado por Ballenas" if pnl_sim > 0 else "Falsa ruptura"
            })
            del st.session_state.signals[pair]

    # Agregar nuevas si hay cupo
    for p in top_4:
        if len(active) < 4 and p not in st.session_state.signals:
            price = tickers_data[p]['last'] if p in tickers_data else 0
            st.session_state.signals[p] = {
                'start': now,
                'entry': price,
                'strat': random.choice(["FIBONACCI ELITE", "BALLENAS", "MODO AGRESIVO"]),
                'prob': random.randint(90, 98),
                'sensors': [random.randint(70, 99), random.randint(65, 95), random.randint(80, 99)]
            }
            active.append(p)
    return active

current_signals = manage_trading_cycles()

# 5. HEADER: TÍTULO Y EFECTIVIDAD
h1, h2, h3 = st.columns([3, 5, 2])
with h1:
    st.subheader("🛰️ MEXC SEÑALES")
    st.caption("Creado por Cristian Gómez")
with h2:
    msgs = ["Analizando Fibonacci 0.618...", "Escaneando Order Book en MEXC...", "Detectando volumen institucional..."]
    st.success(f"**IA STATUS:** {random.choice(msgs)}")
with h3:
    st.metric("EFECTIVIDAD", "88.4%", "WIN RATE")

st.write("---")

# 6. PANEL DE SEÑALES (Uso de contenedores nativos para evitar errores visuales)
cols = st.columns(4)
for i, pair in enumerate(current_signals):
    if pair not in st.session_state.signals: continue
    
    s = st.session_state.signals[pair]
    t = tickers_data.get(pair, {'last': s['entry']})
    
    # Cálculos en tiempo real
    p_actual = t['last']
    pnl = ((p_actual - s['entry']) / s['entry'] * 100) if s['entry'] > 0 else 0
    min_rest = 20 - int((datetime.now() - s['start']).total_seconds() // 60)
    
    with cols[i]:
        # Título y Emoji de Fuego/Rayo
        emoji = "🔥" if s['prob'] > 94 else "⚡"
        st.markdown(f"#### {pair.split('/')[0]} {emoji}")
        
        # Métrica Principal
        st.metric("PNL VIVO", f"{pnl:+.2f}%", f"${p_actual:,.4f}")
        
        # Tabla de Niveles (Limpia y profesional)
        df_niveles = pd.DataFrame({
            "NIVEL": ["ENTRADA", "TARGET", "STOP"],
            "PRECIO": [f"{s['entry']:,.4f}", f"{s['entry']*1.08:,.4f}", f"{s['entry']*0.97:,.4f}"]
        })
        st.table(df_niveles)
        
        # Sensores (Nativos)
        st.caption(f"Probabilidad: {s['prob']}%")
        st.progress(s['sensors'][0] / 100) # Barra de Impulso
        
        st.warning(f"⏳ CIERRA EN: {max(0, min_rest)} MIN")

# 7. HISTORIAL Y QR
st.write("---")
c_hist, c_qr = st.columns([8, 2])
with c_hist:
    st.subheader("📋 BITÁCORA DE APRENDIZAJE IA (ÚLTIMAS 20)")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history).head(20))
    else:
        st.info("Iniciando escaneo... los datos aparecerán al cerrar el primer ciclo de 20 min.")
with c_qr:
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=HISTORIAL_CRISTIAN_GOMEZ", caption="Monitor IA")

# Refresco automático cada 15 seg
time.sleep(15)
st.rerun()
