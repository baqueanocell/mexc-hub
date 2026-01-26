import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA ELITE", layout="wide")

# --- CSS SEGURO PARA TV ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    
    .card-tv { 
        background-color: #0d1117; 
        border: 1px solid #30363d; 
        padding: 8px; 
        border-radius: 5px;
        margin-bottom: 2px;
    }
    
    .exec-grid { 
        display: grid; grid-template-columns: 1fr 1fr 1fr; 
        background: #000; padding: 4px; border-radius: 4px; 
        margin: 5px 0; border: 1px solid #21262d; text-align: center;
    }
    
    .bar-text { font-family: monospace; font-size: 10px; line-height: 1.1; }
    .win-bar-box { background: #222; border-radius: 10px; overflow: hidden; height: 12px; display: flex; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR IA ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

def draw_bar(value, color="#1f6feb"):
    # Crea una barra visual usando bloques de texto
    filled = int(value / 10)
    bar = "■" * filled + "□" * (10 - filled)
    return f'<span style="color:{color};">{bar}</span> {value}%'

def get_market():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        df['score'] = (df['percentage'].fillna(0) * 2) + (df['quoteVolume'] / 1000000)
        top = df[df['symbol'].str.contains('/USDT')].sort_values('score', ascending=False)
        
        selected = ['VEREM/USDT']
        for s in top.index:
            if s != 'VEREM/USDT' and len(selected) < 4: selected.append(s)
            
        data = []
        now = datetime.now(tz_arg)
        for sym in selected:
            if sym in tickers:
                t, s_name = tickers[sym], sym.replace('/USDT','')
                p = t['last']
                
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    strat = "FIBONACCI" if abs(t['percentage'] or 0) > 4 else "IA EXPERTO"
                    if "VEREM" in s_name: strat = "AGRESIVO"
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.03, 's': p*0.985, 'strat': strat,
                        'exp': now+timedelta(minutes=20)
                    }
                
                sig = st.session_state.signals[s_name]
                data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": ((p - sig['e']) / sig['e']) * 100,
                    "soc": 80, "ball": 75, "imp": 90
                })
        return data
    except: return []

# --- RENDER PANTALLA ---
data = get_market()
ops = st.session_state.hist_cerrado
ganadas = sum(1 for o in ops if float(o['PNL'].replace('%','')) > 0)
total_ops = len(ops) if len(ops) > 0 else 1
p_green = (ganadas / total_ops) * 100
p_red = 100 - p_green if len(ops) > 0 else 0

# 1. BARRA DE RENDIMIENTO GLOBAL (ROJA Y VERDE)
st.markdown(f"""
    <div style="text-align: center;">
        <span style="font-size: 18px; font-weight: bold; color: white;">🚀 RENDIMIENTO TOTAL DE SESIÓN</span>
        <div class="win-bar-box">
            <div style="background: #3fb950; width: {p_green}%;"></div>
            <div style="background: #f85149; width: {p_red}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: bold; color: white;">
            <span>GANANCIAS: {p_green:.1f}%</span>
            <span>PÉRDIDAS: {p_red:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 2. TOP 4 MONEDAS
cols = st.columns(4)
for i, m in enumerate(data):
    with cols[i]:
        pnl_c = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-tv">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <b style="font-size: 18px; color:white;">{m['n']}</b>
                <span style="background:#238636; font-size:9px; padding:2px 5px; border-radius:3px;">{m['strat']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top:5px;">
                <span style="color:#58a6ff; font-weight:bold;">${m['p']}</span>
                <span style="color:{pnl_c}; font-weight:bold;">{m['pnl']:.2f}%</span>
            </div>
            <div class="exec-grid">
                <div><span style="font-size:7px; color:#888;">E</span><br><b style="font-size:10px;">{m['e']:.2f}</b></div>
                <div><span style="font-size:7px; color:#888;">T</span><br><b style="font-size:10px; color:#3fb950;">{m['t']:.2f}</b></div>
                <div><span style="font-size:7px; color:#888;">S</span><br><b style="font-size:10px; color:#f85149;">{m['s']:.2f}</b></div>
            </div>
            <div class="bar-text">
                REDES: {draw_bar(m['soc'], "#58a6ff")}<br>
                BALLENAS: {draw_bar(m['ball'], "#bc8cff")}<br>
                IMPULSO: {draw_bar(m['imp'], "#3fb950")}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 3. HISTORIAL DE 10 OPERACIONES
st.markdown("<br><b style='color:#8b949e; font-size:14px;'>📜 ÚLTIMAS 10 OPERACIONES</b>", unsafe_allow_html=True)
if ops:
    st.table(pd.DataFrame(ops).head(10))
else:
    st.info("Esperando resultados del ciclo actual...")
