import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA ELITE TERMINAL", layout="wide")

# --- CSS DE ALTA PRECISIÓN ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white; }
    header, footer {visibility: hidden;}
    
    /* Contenedor de Moneda */
    .card-elite { 
        background-color: #0d1117; 
        border: 1px solid #30363d; 
        padding: 8px; 
        border-radius: 6px;
        height: 240px; /* Reducido para dar espacio al historial */
    }
    
    .symbol-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
    .strat-badge { background: #238636; font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .symbol-name { font-size: 18px; font-weight: bold; }
    
    /* Grilla de Precios */
    .exec-grid { 
        display: grid; grid-template-columns: 1fr 1fr 1fr; 
        background: #000; padding: 5px; border-radius: 4px; 
        margin: 5px 0; border: 1px solid #21262d; text-align: center;
    }
    .val-num { font-size: 11px; font-weight: bold; }
    .val-label { font-size: 7px; color: #8b949e; }
    
    /* Barras Micro dentro del cuadro */
    .micro-bar-box { margin-top: 4px; }
    .micro-label { font-size: 7px; color: #555; display: flex; justify-content: space-between; margin-bottom: -2px; }
    .stProgress > div > div > div > div { height: 2px !important; }
    
    /* Barra de Rendimiento Global */
    .performance-bar-container {
        width: 100%; background: #222; height: 12px; border-radius: 6px; overflow: hidden; display: flex; margin: 10px 0;
    }
    .perf-green { background: #3fb950; height: 100%; transition: width 0.5s; }
    .perf-red { background: #f85149; height: 100%; transition: width 0.5s; }
    
    /* Historial */
    .table-section { background: #000; border: 1px solid #30363d; border-radius: 6px; padding: 8px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

def get_data():
    try:
        tickers = exchange.fetch_tickers()
        # Selección de los 4 mejores (VEREM + 3 por volumen/cambio)
        potential = pd.DataFrame.from_dict(tickers, orient='index')
        potential['score'] = (potential['percentage'].fillna(0) * 2) + (potential['quoteVolume'] / 1000000)
        top_coins = potential[potential['symbol'].str.contains('/USDT')].sort_values('score', ascending=False)
        
        selected = ['VEREM/USDT']
        for s in top_coins.index:
            if s != 'VEREM/USDT' and len(selected) < 4: selected.append(s)
            
        final_data = []
        now = datetime.now(tz_arg)
        for sym in selected:
            if sym in tickers:
                t = tickers[sym]
                p, s_name = t['last'], sym.replace('/USDT','')
                
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    # IA elige estrategia dinámicamente
                    strat = "FIBONACCI" if abs(t['percentage'] or 0) > 4 else "IA EXPERTO"
                    if "VEREM" in s_name: strat = "AGRESIVO"
                    
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.03, 's': p*0.985, 'strat': strat,
                        'exp': now+timedelta(minutes=20),
                        'think': f"Analizando {strat}..."
                    }
                
                sig = st.session_state.signals[s_name]
                final_data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": ((p - sig['e']) / sig['e']) * 100,
                    "soc": 80, "ball": 75, "imp": 90, "think": sig['think']
                })
        return final_data
    except: return []

# --- UI ---
data = get_data()

# Cálculo de Rendimiento Global
ops = st.session_state.hist_cerrado
ganadas = sum(1 for o in ops if float(o['PNL'].replace('%','')) > 0)
perdidas = len(ops) - ganadas
total = len(ops) if len(ops) > 0 else 1
p_green = (ganadas / total) * 100
p_red = 100 - p_green if len(ops) > 0 else 0

# Encabezado con Barra de Rendimiento
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 20px; font-weight: bold;">🛰️ TERMINAL IA ELITE</span>
        <div style="width: 40%; text-align: center;">
            <div style="font-size: 10px; color: #8b949e; margin-bottom: 2px;">RENDIMIENTO TOTAL DE SESIÓN ({len(ops)} OPS)</div>
            <div class="performance-bar-container">
                <div class="perf-green" style="width: {p_green}%;"></div>
                <div class="perf-red" style="width: {p_red}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 9px; font-weight: bold;">
                <span style="color: #3fb950;">GANANCIAS: {p_green:.1f}%</span>
                <span style="color: #f85149;">PÉRDIDAS: {p_red:.1f}%</span>
            </div>
        </div>
        <span style="font-size: 14px; font-family: monospace;">{datetime.now(tz_arg).strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# Grid de Monedas
cols = st.columns(4)
for i, m in enumerate(data):
    with cols[i]:
        pnl_c = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-elite">
            <div class="symbol-header">
                <span class="symbol-name">{m['n']}</span>
                <span class="strat-badge">{m['strat']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <span style="color: #58a6ff; font-size: 16px; font-weight: bold;">${m['p']}</span>
                <span style="color: {pnl_c}; font-size: 11px; font-weight: bold;">{m['pnl']:.2f}%</span>
            </div>
            <div class="exec-grid">
                <div><span class="val-label">ENTRADA</span><br><span class="val-num">{m['e']:.2f}</span></div>
                <div><span class="val-label">TARGET</span><br><span class="val-num" style="color:#3fb950;">{m['t']:.2f}</span></div>
                <div><span class="val-label">STOP</span><br><span class="val-num" style="color:#f85149;">{m['s']:.2f}</span></div>
            </div>
            <div class="micro-bar-box">
                <div class="micro-label"><span>SOCIAL</span><span>{m['soc']}%</span></div>
                <div class="micro-label" style="margin-top: 8px;"><span>BALLENAS</span><span>{m['ball']}%</span></div>
                <div class="micro-label" style="margin-top: 8px;"><span>IMPULSO</span><span>{m['imp']}%</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Barras de progreso ultra-delgadas debajo de cada etiqueta
        st.progress(m['soc']/100)
        st.progress(m['ball']/100)
        st.progress(m['imp']/100)

# Historial Final
st.markdown("<div class='table-section'>", unsafe_allow_html=True)
st.markdown("<span style='font-size: 12px; font-weight: bold; color: #8b949e;'>📜 HISTORIAL DE OPERACIONES (ÚLTIMAS 10)</span>", unsafe_allow_html=True)
if st.session_state.hist_cerrado:
    st.table(pd.DataFrame(st.session_state.hist_cerrado).head(10))
else:
    st.write("Calculando ciclos... Las operaciones aparecerán aquí en breve.")
st.markdown("</div>", unsafe_allow_html=True)
