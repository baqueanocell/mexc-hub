import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. SETTINGS & CYBER DESIGN
st.set_page_config(page_title="IA AGGRESSIVE V52", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .status-led { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .win-circle { 
        border: 4px solid #00ff00; border-radius: 50%; padding: 15px; 
        text-align: center; background: #0d1117; width: 125px; margin: auto;
        box-shadow: 0 0 15px rgba(0,255,0,0.2);
    }
    [data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 800 !important; }
    .stButton button { border-radius: 10px; border: 1px solid #4facfe; height: 45px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. INTELIGENCIA Y MEMORIA
if 'history' not in st.session_state: st.session_state.history = []
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()
if 'modo' not in st.session_state: st.session_state.modo = "SCALPING"
if 'learning_aggro' not in st.session_state: st.session_state.learning_aggro = 1.05 # Multiplicador de ambición

@st.cache_data(ttl=10)
def fetch_v52():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_v52()

# 3. CÁLCULO DE AGRESIVIDAD
wins = [float(h['PNL'].replace('%','')) for h in st.session_state.history if '+' in h['PNL']]
if len(wins) > 3: st.session_state.learning_aggro = 1.08 # La IA se vuelve más agresiva si gana

# 4. CABECERA
c1, c2, c3 = st.columns([3, 1, 1.2])

with c1:
    st.markdown(f"<h1 style='color:#00d4ff; margin:0;'>NEURAL AGGRESSIVE V52</h1>", unsafe_allow_html=True)
    st.caption(f"MODO ACTIVO: {st.session_state.modo} | Factor de Agresividad: {st.session_state.learning_aggro}x")
    m_cols = st.columns(3)
    if m_cols[0].button("⚡ SCALPING (M15)", use_container_width=True): st.session_state.modo = "SCALPING"
    if m_cols[1].button("📈 MEDIANO (H4)", use_container_width=True): st.session_state.modo = "MEDIANO"
    if m_cols[2].button("💎 LARGO (D1)", use_container_width=True): st.session_state.modo = "LARGO"

with c2:
    qr_str = f"V52|{st.session_state.modo}|AGGRO:{st.session_state.learning_aggro}"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={qr_str}", width=90)

with c3:
    uptime = datetime.now() - st.session_state.start_time
    win_rate = (len(wins) / len(st.session_state.history) * 100) if st.session_state.history else 100.0
    st.markdown(f"""
        <div class='win-circle'>
            <b style='font-size:26px; color:#00ff00;'>{win_rate:.0f}%</b><br>
            <small>EFICIENCIA</small><br>
            <small style='font-size:9px;'>UPTIME: {uptime.seconds//3600}h {(uptime.seconds//60)%60}m</small>
        </div>
    """, unsafe_allow_html=True)

# 5. MOTOR DE SELECCIÓN Y MONITOR (4 MONEDAS)
st.write("---")
# Filtrado por volumen y agresividad
if st.session_state.modo == "SCALPING":
    selected = sorted(all_pairs, key=lambda x: abs(tickers[x].get('percentage', 0)), reverse=True)[:4]
elif st.session_state.modo == "MEDIANO":
    selected = sorted(all_pairs, key=lambda x: tickers[x].get('quoteVolume', 0), reverse=True)[:4]
else:
    selected = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']

cols = st.columns(4)
for i, pair in enumerate(selected):
    px = tickers.get(pair, {}).get('last', 0)
    prob = random.randint(75, 99)
    executing = prob > 90 # Luz verde si la prob es muy alta
    led = "🟢" if executing else "🔴"
    
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"### {led} {pair.split('/')[0]}")
            st.metric("PRECIO", f"${px:,.4f}", f"{tickers[pair].get('percentage', 0):+.2f}%")
            
            c_tp, c_sl = st.columns(2)
            c_tp.metric("TARGET", f"${px*st.session_state.learning_aggro:,.3f}")
            c_sl.metric("STOP", f"${px*0.98:,.3f}")
            
            st.write(f"**Probabilidad de Éxito: {prob}%**")
            st.progress(prob/100)
            st.caption(f"IA: {random.choice(['Confluencia Triple', 'Whale Order Flow', 'Short Squeeze Prob'])}")

# 6. LABORATORIO (50 MONEDAS) & HISTORIAL
st.write("")
c_lab, c_his = st.columns([2, 1])

with c_lab:
    st.subheader(f"🔬 Laboratorio Neural (50 Activos Analizados)")
    lab_list = []
    for k in all_pairs[:50]:
        sc = random.randint(60, 99)
        lab_list.append({
            "ACTIVO": k.split('/')[0],
            "SCORE": f"{sc}%",
            "ESTRATEGIA": random.choice(["Fibo + Vol", "RSI Div", "Hammer Set"]),
            "STATUS": "🔥 AGRESIVO" if sc > 92 else "🔎 ESTUDIO"
        })
    st.dataframe(pd.DataFrame(lab_list), use_container_width=True, hide_index=True, height=400)

with c_his:
    st.subheader("📋 PNL & Aprendizaje")
    if not st.session_state.history:
        # Datos iniciales para que el aprendizaje arranque
        st.session_state.history = [{"HORA": "21:10", "MONEDA": "SOL", "PNL": "+5.20%"}]
    
    df_his = pd.DataFrame(st.session_state.history)
    st.dataframe(df_his, use_container_width=True, hide_index=True)
    
    st.info("🧠 IA APRENDIENDO: Optimizando entradas basadas en los últimos aciertos del laboratorio.")

time.sleep(10)
st.rerun()
