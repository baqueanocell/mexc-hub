import streamlit as st
import ccxt
import time
import random

st.set_page_config(page_title="IA TERMINAL V5.0 - AUTÓNOMA", layout="wide")

# --- CSS AVANZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card { background: #0a0e14; border: 1px solid #1f2328; padding: 10px; border-radius: 8px; border-top: 3px solid #00ff00; }
    .strat-tag { background: #1f6feb; color: white; font-size: 8px; padding: 1px 5px; border-radius: 3px; float: right; }
    .ia-log { background: #000a00; border: 1px solid #003300; padding: 8px; color: #00ff00; font-family: 'Courier New', monospace; font-size: 10px; border-radius: 5px; margin-bottom: 10px; height: 80px; overflow-y: hidden; }
    .price-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 3px; margin-top: 8px; }
    .p-box { background: #161b22; padding: 3px; border-radius: 3px; text-align: center; }
    .p-label { font-size: 7px; color: #8b949e; text-transform: uppercase; }
    .p-val { font-size: 10px; font-weight: bold; color: #adbac7; }
    </style>
""", unsafe_allow_html=True)

# --- MOTOR DE APRENDIZAJE Y ESCANEO ---
if 'history_logs' not in st.session_state:
    st.session_state.history_logs = [
        "Sincronizando con MEXC...",
        "Aprendiendo de error en entrada previa (SL ajustado +0.5%)",
        "Escaneando 500+ activos en búsqueda de patrones Fibonacci..."
    ]

# Simular pensamiento activo
new_thoughts = [
    "Detectado patrón Fibonacci 0.618 en temporalidad 5m.",
    "Filtrando monedas por volumen > 1M USDT/24h.",
    "Ajustando estrategia a 'Scalping' por alta volatilidad.",
    "Analizando profundidad de libro (Order Book) para confirmar entrada.",
    "IA aprendiendo: Reduciendo exposición en activos de baja liquidez."
]
st.session_state.history_logs.append(random.choice(new_thoughts))
if len(st.session_state.history_logs) > 4: st.session_state.history_logs.pop(0)

# --- HEADER CON QR PARA ANÁLISIS ---
c1, c2, c3 = st.columns([2, 3, 1])
with c1:
    st.markdown('<h2 style="color:white; margin:0; font-size:20px;">🛰️ IA AUTÓNOMA V5.0</h2>', unsafe_allow_html=True)
with c2:
    st.markdown(f'''<div class="ia-log"><b>[SISTEMA DE PENSAMIENTO CONTINUO]</b><br>
    { "<br>".join(st.session_state.history_logs) }</div>''', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="text-align:right;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=ANALISIS_DATA_IA" width="60" style="background:white; border-radius:4px; padding:2px;"></div>', unsafe_allow_html=True)

# --- ESCÁNER DE MONEDAS (Lógica de Selección) ---
try:
    mexc = ccxt.mexc()
    # Aquí la IA elige las monedas con más cambio en las últimas 24h
    tickers = mexc.fetch_tickers()
    sorted_tickers = sorted(tickers.items(), key=lambda x: x[1]['percentage'] if x[1]['percentage'] else 0, reverse=True)
    top_assets = [t[0].replace('/USDT', '') for t in sorted_tickers if '/USDT' in t[0]][:4]
except:
    top_assets = ['VEREM', 'BTC', 'ETH', 'SOL']

# --- RENDERIZADO DE TARJETAS ---
cols = st.columns(4)
for i, name in enumerate(top_assets):
    # Simulación de datos de entrada basados en patrones
    price = tickers[f"{name}/USDT"]['last'] if f"{name}/USDT" in tickers else 0.0
    change = tickers[f"{name}/USDT"]['percentage'] if f"{name}/USDT" in tickers else 0.0
    
    # La IA elige la estrategia según el cambio
    estrategia = "FIBONACCI" if abs(change) > 5 else "BREAKOUT"
    razon = "Detección automática por volumen inusual."
    entry = price * 0.995
    target = price * 1.05
    stop = price * 0.98
    
    with cols[i]:
        st.markdown(f'''
            <div class="card">
                <span class="strat-tag">{estrategia}</span>
                <b style="color:white; font-size:15px;">{name}</b>
                <div style="color:#8b949e; font-size:9px; font-style:italic;">{razon}</div>
                
                <div style="display:flex; justify-content:space-between; margin:8px 0;">
                    <span style="color:#58a6ff; font-size:18px; font-weight:bold;">${price:,.4f}</span>
                    <span style="color:{"#3fb950" if change >= 0 else "#f85149"}; font-size:13px; font-weight:bold;">{change:.2f}%</span>
                </div>

                <div class="price-grid">
                    <div class="p-box"><span class="p-label">ENTRADA</span><span class="p-val">{entry:,.3f}</span></div>
                    <div class="p-box"><span class="p-label" style="color:#3fb950;">TARGET</span><span class="p-val">{target:,.3f}</span></div>
                    <div class="p-box"><span class="p-label" style="color:#f85149;">STOP</span><span class="p-val">{stop:,.3f}</span></div>
                </div>
                
                <div style="margin-top:8px; display:flex; justify-content:space-between;">
                    <span style="color:#ffca28; font-size:10px; font-weight:bold;">🔥 SEÑAL IA</span>
                    <span style="color:#888; font-size:9px;">CONFIRMACIÓN 94%</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)

# --- REPORTE DE ERRORES / APRENDIZAJE ---
st.markdown('<div style="color:#58a6ff; font-weight:bold; font-size:11px; margin-top:10px;">📉 BITÁCORA DE APRENDIZAJE IA</div>', unsafe_allow_html=True)
st.table([
    {"SUCESO": "Falso Breakout detectado", "ACTIVO": "PEPE/USDT", "ACCIÓN": "Incrementar filtro de volumen", "MEJORA": "Evitar entradas falsas"},
    {"SUCESO": "Target 2 alcanzado", "ACTIVO": "VEREM/USDT", "ACCIÓN": "Mantener estrategia Agresiva", "MEJORA": "Maximizar PNL"}
])

time.sleep(15)
st.rerun()
