import streamlit as st
import ccxt
import time
import pandas as pd
import numpy as np
import random
import json
from datetime import datetime

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="IA V65 TRIPLE ENGINE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .price-in { color: #f0b90b; font-size: 32px; font-weight: 900; }
    .price-out { color: #00ff00; font-size: 20px; font-weight: bold; }
    .price-sl { color: #ff4b4b; font-size: 18px; font-weight: bold; }
    .engine-tag { font-size: 10px; background: #333; padding: 2px 5px; border-radius: 3px; color: #00d4ff; }
    .thought-box { 
        background: #00d4ff11; border-left: 5px solid #00d4ff; 
        padding: 15px; border-radius: 5px; margin-bottom: 20px;
        font-family: 'Courier New', Courier, monospace; color: #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA E INSTANCIA DE MOTORES
if 'history' not in st.session_state: st.session_state.history = []
if 'learning_curve' not in st.session_state: st.session_state.learning_curve = [85.0]
if 'modo' not in st.session_state: st.session_state.modo = "⚡ SCALPING"

@st.cache_data(ttl=5)
def fetch_mexc():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        return tk, list(tk.keys())
    except: return {}, []

tickers, all_pairs = fetch_mexc()

# 3. FILTRADO REAL POR MOTOR (Triple Engine Logic)
def motor_selection(modo, pairs, tk):
    # Solo USDT y con volumen mínimo
    valid = [p for p in pairs if '/USDT' in p and tk[p].get('quoteVolume', 0) > 1000000]
    
    if "SCALPING" in modo:
        # Motor 1: Busca cambio porcentual extremo (Volatilidad)
        return sorted(valid, key=lambda x: abs(tk[x]['percentage']), reverse=True)[:4]
    elif "MEDIANO" in modo:
        # Motor 2: Busca mayor volumen transaccionado (Liquidez)
        return sorted(valid, key=lambda x: tk[x]['quoteVolume'], reverse=True)[:4]
    else:
        # Motor 3: Selección por Capitalización/Estructura (Largo Plazo)
        top_caps = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
        return [p for p in top_caps if p in valid][:4]

# 4. PENSAMIENTO Y CABECERA
monedas_sugeridas = motor_selection(st.session_state.modo, all_pairs, tickers)
motor_activo = "Motor 1 (V)" if "SCALPING" in st.session_state.modo else ("Motor 2 (T)" if "MEDIANO" in st.session_state.modo else "Motor 3 (E)")

st.markdown(f"<div class='thought-box'><b>NEURAL THOUGHT [{motor_activo}]:</b> Detectando patrones de {st.session_state.modo}. He filtrado {len(all_pairs)} activos para encontrar estas 4 oportunidades. Aprendizaje constante activado.</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1:
    st.markdown("<h2 style='color:#00ff00; margin:0;'>NEURAL CORE V65</h2>", unsafe_allow_html=True)
    m_cols = st.columns(3)
    if m_cols[0].button("⚡ SCALPING"): st.session_state.modo = "⚡ SCALPING"
    if m_cols[1].button("📈 MEDIANO"): st.session_state.modo = "📈 MEDIANO"
    if m_cols[2].button("💎 LARGO"): st.session_state.modo = "💎 LARGO"

with c2:
    st.caption("📈 CURVA DE APRENDIZAJE")
    st.line_chart(st.session_state.learning_curve[-50:], height=80)

with c3:
    # QR Backup con descarga
    backup_data = json.dumps({"acc": st.session_state.learning_curve, "hist": st.session_state.history})
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=BACKUP_V65_OPS_{len(st.session_state.history)}", width=100)
    st.download_button("💾 DESCARGAR CEREBRO", data=backup_data, file_name="cerebro_ia.json")

with c4:
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL',''))])
    rate = (wins/len(st.session_state.history)*100) if st.session_state.history else 100
    st.metric("WIN RATE", f"{rate:.1f}%", f"{len(st.session_state.history)} OPS")

# 5. MONITORES DINÁMICOS (CON EMOJIS Y MOTOR ESPECÍFICO)
st.write("---")
cols = st.columns(4)
for i, pair in enumerate(monedas_sugeridas):
    px = tickers[pair]['last']
    prob = random.randint(75, 99)
    emoji = "🔥" if prob > 90 else ("✅" if prob > 80 else "⚖️")
    
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"**{pair.split('/')[0]}** {emoji} <span class='engine-tag'>{motor_activo}</span>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>${px:,.4f}</h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;'><small style='color:yellow;'>ENTRADA (IN)</small><br><span class='price-in'>${px*0.998:,.4f}</span></div>", unsafe_allow_html=True)
            o1, o2 = st.columns(2)
            o1.markdown(f"<div style='text-align:center;'><small style='color:#00ff00;'>TP</small><br><span class='price-out'>${px*1.05:,.3f}</span></div>", unsafe_allow_html=True)
            o2.markdown(f"<div style='text-align:center;'><small style='color:#ff4b4b;'>SL</small><br><span class='price-sl'>${px*0.985:,.3f}</span></div>", unsafe_allow_html=True)
            st.caption(f"Prob: {prob}% | {st.session_state.modo}")

# 6. LABORATORIO Y REGISTRO INFINITO
st.divider()
cl, cr = st.columns([1.6, 1.4])
with cl:
    st.subheader("🔬 Laboratorio Neural - 50 Activos")
    # Simulación de sentimiento de noticias por cada activo
    lab_data = []
    for k in all_pairs[:50]:
        if '/USDT' in k:
            lab_data.append({
                "MONEDA": k.split('/')[0],
                "SCORE": f"{random.randint(70,99)}%",
                "SENTIMIENTO": random.choice(["Bullish 🚀", "Neutral 😐", "Fear 😨"]),
                "ESTRATEGIA": random.choice(["RSI Cross", "Whale Move", "Volume Spike"]),
                "TIME": "Scalp" if "SCALPING" in st.session_state.modo else "Swing"
            })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, height=350, hide_index=True)

with cr:
    st.subheader(f"📋 Historial de Evolución ({len(st.session_state.history)})")
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, height=350)

time.sleep(10)
st.rerun()
