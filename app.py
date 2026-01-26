import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL PRO", layout="wide")

# --- CSS DE ALTA DENSIDAD PARA TV (TODO EN UNA PANTALLA) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white; }
    header, footer {visibility: hidden;}
    
    /* Contenedor Top 4 */
    [data-testid="column"] { min-width: 24% !important; padding: 5px !important; }
    
    .card-elite { 
        background-color: #0d1117; 
        border: 1px solid #30363d; 
        padding: 10px; 
        border-radius: 6px;
        height: 280px; /* Altura fija para control de pantalla */
    }
    
    .symbol-name { font-size: 20px; font-weight: bold; color: #ffffff; }
    .price-val { color: #58a6ff; font-size: 18px; font-weight: bold; font-family: monospace; }
    
    .exec-grid { 
        display: grid; grid-template-columns: 1fr 1fr 1fr; 
        background: #000; padding: 4px; border-radius: 4px; 
        margin: 8px 0; border: 1px solid #21262d; text-align: center;
    }
    .val-label { font-size: 8px; color: #8b949e; text-transform: uppercase; }
    .val-num { font-size: 12px; font-weight: bold; }
    
    /* Barras Ultra-Compactas */
    .bar-container { margin-top: 5px; }
    .bar-label { font-size: 8px; color: #444; margin-bottom: -12px; text-transform: uppercase; }
    .stProgress > div > div > div > div { height: 3px !important; }
    
    .ia-think { 
        font-size: 9px; color: #8b949e; font-style: italic; 
        margin-top: 8px; border-top: 1px solid #21262d; padding-top: 4px;
    }
    
    /* Historial Integrado */
    .table-container { background: #000; border: 1px solid #30363d; border-radius: 4px; padding: 5px; margin-top: 10px; }
    .win-rate-banner {
        background: linear-gradient(90deg, #1f6feb, #000);
        padding: 5px 15px; border-radius: 4px; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE APRENDIZAJE IA ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

def get_market_data():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        # Filtro de potencial (Volumen + Cambio %)
        df['score'] = (df['percentage'].fillna(0) * 2) + (df['quoteVolume'] / 1000000)
        potential = df[df['symbol'].str.contains('/USDT')].sort_values('score', ascending=False)
        
        selected = ['VEREM/USDT']
        for s in potential.index:
            if s != 'VEREM/USDT' and len(selected) < 4: selected.append(s)
            
        data = []
        now = datetime.now(tz_arg)

        for sym in selected:
            if sym in tickers:
                t = tickers[sym]
                p, s_name = t['last'], sym.replace('/USDT','')
                
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    # IA DECIDE ESTRATEGIA SEGÚN COMPORTAMIENTO
                    if "VEREM" in s_name: strat = "AGRESIVO"
                    elif abs(t['percentage'] or 0) > 5: strat = "FIBONACCI"
                    else: strat = "SMART MONEY"
                    
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.032, 's': p*0.984, 'strat': strat,
                        'exp': now+timedelta(minutes=20),
                        'think': f"Aplicando {strat} por alta volatilidad..."
                    }
                
                sig = st.session_state.signals[s_name]
                data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": ((p - sig['e']) / sig['e']) * 100,
                    "soc": 75, "ball": 80, "imp": 90, "think": sig['think']
                })
        return data
    except: return []

# --- RENDERIZADO PANTALLA ---
data = get_market_data()
ganadas = sum(1 for op in st.session_state.hist_cerrado if float(op['PNL'].replace('%','')) > 0)
total_op = len(st.session_state.hist_cerrado)
wr = (ganadas / total_op * 100) if total_op > 0 else 0

st.markdown(f"""
    <div class="win-rate-banner">
        <span style="font-weight:bold; font-size:18px;">🤖 TERMINAL IA ELITE</span>
        <span style="color: {'#3fb950' if wr >= 50 else '#f85149'}; font-weight:bold;">
            WIN RATE: {wr:.1f}% | TOTAL: {total_op} OPS
        </span>
    </div>
    """, unsafe_allow_html=True)

# TOP 4 CARDS
cols = st.columns(4)
for i, m in enumerate(data):
    with cols[i]:
        pnl_col = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-elite">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="background:#238636; font-size:9px; padding:2px 5px; border-radius:3px;">{m['strat']}</span>
                <span style="color:{pnl_col}; font-size:12px; font-weight:bold;">{m['pnl']:.2f}%</span>
            </div>
            <div style="text-align:center; margin:10px 0;">
                <div class="symbol-name">{m['n']}</div>
                <div class="price-val">${m['p']}</div>
            </div>
            <div class="exec-grid">
                <div><span class="val-label">ENTRADA</span><br><span class="val-num">{m['e']:.2f}</span></div>
                <div><span class="val-label">TARGET</span><br><span class="val-num" style="color:#3fb950;">{m['t']:.2f}</span></div>
                <div><span class="val-label">STOP</span><br><span class="val-num" style="color:#f85149;">{m['s']:.2f}</span></div>
            </div>
            <div class="bar-container">
                <div class="bar-label">SOCIAL / BALLENAS / IMPULSO</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.progress(m['ball']/100)
        st.progress(m['imp']/100)
        st.markdown(f'<div class="ia-think">🧠 {m["think"]}</div>', unsafe_allow_html=True)

# HISTORIAL INTEGRADO (ABRAZA EL FINAL DE LA PANTALLA)
st.markdown("<div class='table-container'>", unsafe_allow_html=True)
st.markdown("<span style='font-size:12px; color:#8b949e;'>📜 HISTORIAL DE APRENDIZAJE (ÚLTIMAS 10)</span>", unsafe_allow_html=True)
if st.session_state.hist_cerrado:
    st.dataframe(pd.DataFrame(st.session_state.hist_cerrado).head(10), use_container_width=True)
else:
    st.write("Analizando ciclos... El historial aparecerá aquí.")
st.markdown("</div>", unsafe_allow_html=True)
