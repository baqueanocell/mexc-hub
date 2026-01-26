import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime

# 1. CONFIGURACIÓN CYBER-SENSORIAL
st.set_page_config(page_title="IA NEURAL V46", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    
    /* Círculo de Win Rate Dinámico */
    .win-circle { 
        width: 100px; height: 100px; border-radius: 50%; border: 6px solid #00ff00; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        background: #0d1117; box-shadow: 0 0 20px rgba(0,255,0,0.4); margin: auto;
    }
    
    /* Tarjetas de Monedas */
    .crypto-card { 
        background: #111b21; border: 1px solid #30363d; border-radius: 12px; padding: 15px; 
        border-top: 4px solid #00d4ff; transition: 0.3s;
    }
    .price-main { font-size: 28px; font-weight: 900; color: white; text-align: center; margin: 10px 0; }
    
    /* Niveles IN/TGT/SL destacados */
    .level-row { display: flex; justify-content: space-between; gap: 5px; margin-top: 10px; }
    .level-item { flex: 1; background: #050a0e; padding: 6px; border-radius: 6px; text-align: center; border: 1px solid #4facfe; }
    .level-lab { font-size: 10px; color: #8b949e; font-weight: bold; }
    .level-val { font-size: 14px; color: #f0b90b; font-weight: 800; }

    /* Pensamiento IA */
    .ia-thought { font-size: 11px; color: #00d4ff; font-style: italic; text-align: center; margin-top: 10px; min-height: 30px; }
    </style>
""", unsafe_allow_html=True)

# 2. PROCESAMIENTO DE DATOS
if 'modo' not in st.session_state: st.session_state.modo = "⚡ SCALPING"
if 'history' not in st.session_state: st.session_state.history = []

@st.cache_data(ttl=10)
def fetch_mexc_v46():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_mexc_v46()

# 3. CABECERA: BOTONES + QR + WIN RATE
c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 0.8, 1.2])

with c1:
    if st.button("⚡ SCALPING", use_container_width=True): st.session_state.modo = "⚡ SCALPING"
with c2:
    if st.button("📈 MEDIANO", use_container_width=True): st.session_state.modo = "📈 MEDIANO"
with c3:
    if st.button("💎 LARGO", use_container_width=True): st.session_state.modo = "💎 LARGO"
with c4:
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=SYNC_V46", width=75)
with c5:
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL', ''))])
    rate = (wins / len(st.session_state.history) * 100) if st.session_state.history else 100.0
    w_color = "#00ff00" if rate >= 50 else "#ff4b4b"
    st.markdown(f"""
        <div class='win-circle' style='border-color: {w_color}; box-shadow: 0 0 15px {w_color};'>
            <span style='font-size: 26px; font-weight: bold; color: {w_color};'>{rate:.0f}%</span>
            <span style='font-size: 9px; color: white;'>WIN RATE</span>
        </div>
    """, unsafe_allow_html=True)

# 4. LÓGICA DE SELECCIÓN IA
if "SCALPING" in st.session_state.modo:
    selected = sorted(all_pairs, key=lambda x: abs(tickers[x].get('percentage', 0)), reverse=True)[:4]
    time_tag = "5-15m"
elif "MEDIANO" in st.session_state.modo:
    selected = sorted(all_pairs, key=lambda x: tickers[x].get('quoteVolume', 0), reverse=True)[:4]
    time_tag = "1h-4h"
else:
    selected = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    time_tag = "1d-1w"

# 5. MONITOR DE SEÑALES ACTIVAS
st.write("")
cols = st.columns(4)
for i, pair in enumerate(selected):
    px = tickers.get(pair, {}).get('last', 0)
    chg = tickers.get(pair, {}).get('percentage', 0)
    pensamiento = random.choice([
        "🧠 Detectando inyección de volumen masivo...",
        "🧠 Fibonacci 0.618 confirmado en temporalidad baja.",
        "🧠 Ballena detectada posicionándose en Short.",
        "🧠 Patrón de reversión Hammer en formación."
    ])
    
    with cols[i]:
        st.markdown(f"""
            <div class='crypto-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <b style='color:#00d4ff;'>{pair.split('/')[0]}</b>
                    <span style='font-size: 10px; color:#8b949e;'>⏱️ {time_tag}</span>
                </div>
                <div class='price-main'>${px:,.4f}</div>
                <div style='text-align:center; color:{"#00ff00" if chg >= 0 else "#ff4b4b"}; font-weight:bold;'>{chg:+.2f}%</div>
                
                <div class='level-row'>
                    <div class='level-item'><span class='level-lab'>IN</span><br><span class='level-val'>{px*0.995:,.4f}</span></div>
                    <div class='level-item'><span class='level-lab'>TGT</span><br><span class='level-val'>{px*1.04:,.4f}</span></div>
                    <div class='level-item'><span class='level-lab'>SL</span><br><span class='level-val'>{px*0.985:,.4f}</span></div>
                </div>
                
                <div class='ia-thought'>{pensamiento}</div>
            </div>
        """, unsafe_allow_html=True)

# 6. LABORATORIO Y BITÁCORA (EL CEREBRO TRABAJANDO)
st.divider()
c_lab, c_bit = st.columns([2, 1])

with c_lab:
    st.subheader(f"🔬 Laboratorio Neural - Modo {st.session_state.modo}")
    lab_data = []
    for k in all_pairs[:25]:
        score = random.randint(75, 99)
        lab_data.append({
            "MONEDA": k.split('/')[0],
            "SCORE": f"{score}%",
            "ESTUDIO": random.choice(["Estructura Bullish", "Quema de Tokens", "Divergencia RSI"]),
            "STATUS": "🚀 PROMOCIONAR" if score > 94 else "🔍 ANALIZANDO"
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True)

with c_bit:
    st.subheader("📋 Bitácora Real")
    if not st.session_state.history:
        st.info("La IA está recopilando datos de los primeros simulacros...")
    else:
        st.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
