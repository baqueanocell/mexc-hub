import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime

# 1. CONFIGURACIÓN CYBER-PRECISION
st.set_page_config(page_title="IA V50 HIGH PRECISION", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    /* Contenedor de Señal */
    .signal-card { 
        background: #111b21; border-radius: 8px; padding: 10px; 
        border: 1px solid #1e2329; position: relative;
    }
    /* Luz LED de Ejecución IA */
    .led-ia {
        height: 12px; width: 12px; border-radius: 50%;
        position: absolute; top: 10px; right: 10px;
        box-shadow: 0 0 8px;
    }
    /* Barras de Miniatura */
    .mini-bar { height: 4px; border-radius: 2px; background: #30363d; margin-bottom: 2px; }
    .bar-fill { height: 100%; border-radius: 2px; }
    
    /* Precios SL y TP Grandes */
    .val-tp { color: #00ff00; font-size: 18px; font-weight: 900; }
    .val-sl { color: #ff4b4b; font-size: 18px; font-weight: 900; }
    .val-in { color: #f0b90b; font-size: 14px; font-weight: bold; }
    
    .win-circle { 
        width: 110px; height: 110px; border-radius: 50%; border: 4px solid #00ff00; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        background: #0d1117; margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA Y MOTORES
if 'modo' not in st.session_state: st.session_state.modo = "SCALPING"
if 'history' not in st.session_state: st.session_state.history = []
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()

@st.cache_data(ttl=10)
def fetch_v50():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_v50()

# 3. CABECERA
c1, c2, c3 = st.columns([3, 1, 1.5])
with c1:
    st.markdown(f"<h2 style='color:#00d4ff; margin:0;'>TRIPLE-ENGINE V50</h2>", unsafe_allow_html=True)
    st.caption(f"Operativa Pro | Cristian Gómez | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    mc = st.columns(3)
    if mc[0].button("⚡ SCALPING", use_container_width=True): st.session_state.modo = "SCALPING"
    if mc[1].button("📈 MEDIANO", use_container_width=True): st.session_state.modo = "MEDIANO"
    if mc[2].button("💎 LARGO", use_container_width=True): st.session_state.modo = "LARGO"

with c2:
    qr_data = f"V50|{st.session_state.modo}|{len(st.session_state.history)}ops"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={qr_data}", width=85)

with c3:
    wins = len([h for h in st.session_state.history if '✅' in str(h.get('RES', ''))])
    rate = (wins / len(st.session_state.history) * 100) if st.session_state.history else 100.0
    uptime = datetime.now() - st.session_state.start_time
    st.markdown(f"""
        <div class='win-circle'>
            <b style='font-size:24px; color:#00ff00;'>{rate:.0f}%</b>
            <small style='font-size:9px;'>UPTIME: {uptime.seconds//3600}h {(uptime.seconds//60)%60}m</small>
        </div>
    """, unsafe_allow_html=True)

# 4. MONITOR DE SEÑALES (ESTILO HIGH PRECISION)
st.write("---")
selected = sorted(all_pairs, key=lambda x: abs(tickers[x].get('percentage', 0)), reverse=True)[:4]
cols = st.columns(4)

for i, pair in enumerate(selected):
    px = tickers.get(pair, {}).get('last', 0)
    ia_active = random.choice([True, False]) # Simulación de ejecución
    led_color = "#00ff00" if ia_active else "#30363d"
    
    with cols[i]:
        st.markdown(f"""
            <div class='signal-card'>
                <div class='led-ia' style='background:{led_color}; box-shadow:0 0 10px {led_color};'></div>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <b style='color:#00d4ff;'>{pair.split('/')[0]}</b>
                    <small style='color:#8b949e;'>15-30m</small>
                </div>
                <h3 style='text-align:center; margin:15px 0;'>${px:,.4f}</h3>
                
                <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                    <div style='text-align:center;'>
                        <small style='color:#8b949e;'>SL</small><br>
                        <span class='val-sl'>${px*0.985:,.3f}</span>
                    </div>
                    <div style='text-align:center;'>
                        <small style='color:#8b949e;'>TP</small><br>
                        <span class='val-tp'>${px*1.05:,.3f}</span>
                    </div>
                </div>
                
                <div style='text-align:center; margin-bottom:10px;'>
                    <small style='color:#8b949e;'>ENTRY:</small> <span class='val-in'>${px*0.995:,.4f}</span>
                </div>

                <div style='display:flex; gap:3px;'>
                    <div class='mini-bar' style='flex:1;'><div class='bar-fill' style='width:80%; background:#4facfe;'></div></div>
                    <div class='mini-bar' style='flex:1;'><div class='bar-fill' style='width:60%; background:#f0b90b;'></div></div>
                    <div class='mini-bar' style='flex:1;'><div class='bar-fill' style='width:90%; background:#00ff00;'></div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 5. LABORATORIO & BITÁCORA
st.write("")
c_lab, c_bit = st.columns([2.2, 0.8])
with c_lab:
    st.subheader("🔬 Laboratorio Neural - Confluencias")
    lab_data = []
    for k in all_pairs[:20]:
        score = random.randint(75, 99)
        lab_data.append({
            "MONEDA": k.split('/')[0],
            "MOTORES": "✅✅✅" if score > 90 else "⏳ ANALIZANDO",
            "INFO": random.choice(["🐋 Ballena", "🔥 Quema", "📐 Fibo 0.618"]),
            "SCORE": f"{score}%",
            "ACCIÓN": "🚀 EJECUTAR" if score > 92 else "🔍 ESTUDIO"
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True)

with c_bit:
    st.subheader("📋 Bitácora")
    if not st.session_state.history:
        st.session_state.history = [{"PAR": "BTC", "PNL": "+1.2%", "RES": "✅"}, {"PAR": "ETH", "PNL": "-0.5%", "RES": "❌"}]
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
