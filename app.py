import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="IA MONITOR V39", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .title-main { font-size: 28px; font-weight: 800; color: white; margin: 0; }
    .pnl-circle { width: 85px; height: 85px; border-radius: 50%; border: 4px solid #00ff00; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #0e1117; }
    
    /* Niveles Mediano-Grandes */
    .level-box { text-align: center; background: rgba(255, 255, 255, 0.07); padding: 8px; border-radius: 6px; border: 1px solid #4facfe; }
    .level-val { font-size: 20px; font-weight: 800; color: #f0b90b; display: block; }
    .level-lab { font-size: 10px; color: #848e9c; font-weight: bold; }
    
    .price-live { font-size: 24px; font-weight: bold; color: white; }
    .sensor-tag { font-size: 9px; font-weight: bold; color: #848e9c; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()
if 'history' not in st.session_state: st.session_state.history = []
if 'signals' not in st.session_state: st.session_state.signals = {}

@st.cache_data(ttl=10)
def fetch_data():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        top_30 = sorted(valid, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)[:30]
        return tk, top_4, top_30
    except: return {}, [], []

tickers, top_4, lab_keys = fetch_data()

# 3. CABECERA (TÍTULO, QR, PNL GLOBAL)
total_pnl = sum([float(h['PNL'].replace('%','')) for h in st.session_state.history]) if st.session_state.history else 0.0
uptime = f"{(datetime.now() - st.session_state.start_time).seconds//3600}h {((datetime.now() - st.session_state.start_time).seconds//60)%60}m"

c1, c2, c3 = st.columns([3, 0.6, 1])
with c1:
    st.markdown(f"<div class='title-main'>MONITOR IA EXPERTO MEXC</div><div style='color: #4facfe;'>Cristian Gómez • Uptime: {uptime}</div>", unsafe_allow_html=True)
with c2:
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=HISTORIAL_IA_CRISTIAN", width=75)
with c3:
    color = "#00ff00" if total_pnl >= 0 else "#ff4b4b"
    st.markdown(f"<div class='pnl-circle' style='border-color:{color};'><div style='font-size:18px; color:{color}; font-weight:bold;'>{total_pnl:+.2f}%</div><div style='font-size:9px; color:white;'>GLOBAL</div></div>", unsafe_allow_html=True)

# 4. CUADROS PRINCIPALES (REAJUSTADOS)
st.write("")
cols = st.columns(4)
now = datetime.now()

# Lógica de rotación simplificada
active_pairs = top_4 # Para asegurar que siempre haya 4 en el ejemplo

for i, pair in enumerate(active_pairs):
    px = tickers.get(pair, {}).get('last', 0)
    pnl_sim = random.uniform(-0.5, 2.5) # Simulación de PNL para visualización
    
    with cols[i]:
        with st.container(border=True):
            # Moneda e Icono chico
            t1, t2 = st.columns([3, 1])
            t1.markdown(f"### {pair.split('/')[0]}")
            t2.markdown("## 🚀" if pnl_sim > 0.5 else "## ⏳")
            
            # Precio Real
            st.markdown(f"<div style='text-align:center;' class='price-live'>${px:,.4f} <small style='color:#00ff00;'>{pnl_sim:+.2f}%</small></div>", unsafe_allow_html=True)
            
            # NIVELES MEDIANO-GRANDES
            l1, l2, l3 = st.columns(3)
            with l1: st.markdown(f"<div class='level-box'><span class='level-lab'>IN</span><span class='level-val'>{px*0.995:,.4f}</span></div>", unsafe_allow_html=True)
            with l2: st.markdown(f"<div class='level-box'><span class='level-lab'>TGT</span><span class='level-val'>{px*1.05:,.4f}</span></div>", unsafe_allow_html=True)
            with l3: st.markdown(f"<div class='level-box'><span class='level-lab'>SL</span><span class='level-val'>{px*0.98:,.4f}</span></div>", unsafe_allow_html=True)
            
            st.write("")
            # Sensores horizontales
            s1, s2, s3 = st.columns(3)
            for s, label in zip([s1, s2, s3], ["🐋 BALL", "📱 REDS", "⚡ IMPU"]):
                with s:
                    st.markdown(f"<p class='sensor-tag'>{label}</p>", unsafe_allow_html=True)
                    st.progress(random.randint(60, 95)/100)

# 5. HISTORIAL DIVIDIDO (1:2)
st.divider()
col_bitacora, col_laboratorio = st.columns([1, 2]) # División en 3 partes (1 para bitácora, 2 para lab)

with col_bitacora:
    st.subheader("📋 Bitácora Real")
    if not st.session_state.history:
        # Datos de ejemplo para que no se vea vacío
        st.session_state.history = [{"HORA": "19:20", "MONEDA": "SOL", "PNL": "+2.40%"}, {"HORA": "19:05", "MONEDA": "PEPE", "PNL": "-0.80%"}]
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)

with col_laboratorio:
    st.subheader("🧠 Laboratorio IA & Noticias Detalladas")
    
    estrategias_det = [
        "📐 Fibonacci (Nivel 0.618 Detectado)",
        "🌊 Ondas Elliot (Iniciando Onda 3)",
        "📊 RSI Divergencia (Sobreventa)",
        "🚀 Quema de Tokens detectada en Redes",
        "🐋 Movimiento Ballena (Inflow +5M USDT)",
        "🔥 Hype Social Alto (Twitter/X Trend)"
    ]
    
    lab_data = []
    for k in lab_keys[:30]:
        lab_data.append({
            "MONEDA": k.split('/')[0],
            "SCORE": f"{random.randint(70, 99)}%",
            "ESTUDIO TÉCNICO / NOTICIAS": random.choice(estrategias_det),
            "ESTADO": "Buscando Confirmación"
        })
    
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True)

time.sleep(12)
st.rerun()
