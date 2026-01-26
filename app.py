import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE", layout="wide")

# --- CSS DE PRECISIÓN (BARRAS DENTRO DEL CUADRO) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white; }
    header, footer {visibility: hidden;}
    
    /* Cuadro de Moneda */
    .card-pro { 
        background-color: #0d1117; 
        border: 1px solid #30363d; 
        padding: 10px; 
        border-radius: 8px;
        height: 260px; /* Altura controlada */
    }
    
    .symbol-name { font-size: 20px; font-weight: bold; color: white; }
    .price-val { color: #58a6ff; font-size: 18px; font-weight: bold; font-family: monospace; }
    
    /* Grilla de Entrada/TP/SL */
    .exec-grid { 
        display: grid; grid-template-columns: 1fr 1fr 1fr; 
        background: #000; padding: 6px; border-radius: 4px; 
        margin: 8px 0; border: 1px solid #21262d; text-align: center;
    }
    .val-label { font-size: 7px; color: #8b949e; }
    .val-num { font-size: 11px; font-weight: bold; }
    
    /* SISTEMA DE BARRAS INTERNAS (HTML) */
    .bar-row { margin-top: 6px; }
    .bar-text { font-size: 8px; color: #8b949e; display: flex; justify-content: space-between; margin-bottom: 2px; }
    .bar-bg { background: #21262d; height: 4px; border-radius: 2px; width: 100%; overflow: hidden; }
    .bar-fill { background: #1f6feb; height: 100%; border-radius: 2px; }

    /* Barra de Rendimiento Superior */
    .perf-container { width: 100%; background: #161b22; height: 14px; border-radius: 7px; display: flex; overflow: hidden; border: 1px solid #30363d; }
    .p-green { background: #238636; height: 100%; transition: 0.5s; }
    .p-red { background: #da3633; height: 100%; transition: 0.5s; }
    
    /* Historial */
    .hist-box { background: #000; border: 1px solid #30363d; padding: 10px; border-radius: 8px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

def get_data():
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
                        'exp': now+timedelta(minutes=20),
                        'think': f"Operando con {strat}..."
                    }
                
                sig = st.session_state.signals[s_name]
                data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": ((p - sig['e']) / sig['e']) * 100,
                    "soc": 78, "ball": 85, "imp": 92, "think": sig['think']
                })
        return data
    except: return []

# --- RENDERIZADO ---
data = get_data()
ops = st.session_state.hist_cerrado
ganadas = sum(1 for o in ops if float(o['PNL'].replace('%','')) > 0)
total = len(ops) if len(ops) > 0 else 1
p_green = (ganadas / total) * 100
p_red = 100 - p_green if len(ops) > 0 else 0

# Header con Barra Global
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
        <b style="font-size: 18px;">🛰️ TERMINAL IA ELITE</b>
        <div style="width: 50%; text-align: center;">
            <div class="perf-container">
                <div class="p-green" style="width: {p_green}%;"></div>
                <div class="p-red" style="width: {p_red}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 9px; margin-top: 2px;">
                <span style="color: #3fb950;">GANANCIAS: {p_green:.1f}%</span>
                <span style="color: #f85149;">PÉRDIDAS: {p_red:.1f}%</span>
            </div>
        </div>
        <b style="font-size: 14px;">{datetime.now(tz_arg).strftime('%H:%M')}</b>
    </div>
    """, unsafe_allow_html=True)

# Grid Top 4
cols = st.columns(4)
for i, m in enumerate(data):
    with cols[i]:
        pnl_c = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        # Diseño de barra interna personalizada
        def render_bar(label, value):
            return f"""
            <div class="bar-row">
                <div class="bar-text"><span>{label}</span><span>{value}%</span></div>
                <div class="bar-bg"><div class="bar-fill" style="width: {value}%;"></div></div>
            </div>"""

        st.markdown(f"""
        <div class="card-pro">
            <div style="display: flex; justify-content: space-between;">
                <span style="background: #238636; font-size: 8px; padding: 2px 5px; border-radius: 3px; font-weight: bold;">{m['strat']}</span>
                <span style="color: {pnl_c}; font-size: 11px; font-weight: bold;">{m['pnl']:.2f}%</span>
            </div>
            <div style="text-align: center; margin: 8px 0;">
                <div class="symbol-name">{m['n']}</div>
                <div class="price-val">${m['p']}</div>
            </div>
            <div class="exec-grid">
                <div><span class="val-label">ENTRADA</span><br><span class="val-num">{m['e']:.2f}</span></div>
                <div><span class="val-label">TARGET</span><br><span class="val-num" style="color:#3fb950;">{m['t']:.2f}</span></div>
                <div><span class="val-label">STOP</span><br><span class="val-num" style="color:#f85149;">{m['s']:.2f}</span></div>
            </div>
            {render_bar("SOCIAL", m['soc'])}
            {render_bar("BALLENAS", m['ball'])}
            {render_bar("IMPULSO", m['imp'])}
            <div style="font-size: 8px; color: #444; margin-top: 8px; font-style: italic;">🧠 {m['think']}</div>
        </div>
        """, unsafe_allow_html=True)

# Historial (Ocupa el resto de la pantalla)
st.markdown("<div class='hist-box'>", unsafe_allow_html=True)
st.markdown("<b style='font-size: 12px; color: #8b949e;'>📜 ÚLTIMAS 10 OPERACIONES</b>", unsafe_allow_html=True)
if ops:
    st.table(pd.DataFrame(ops).head(10))
else:
    st.write("Analizando mercado... El historial aparecerá aquí.")
st.markdown("</div>", unsafe_allow_html=True)
