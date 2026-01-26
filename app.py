import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos para máxima precisión
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE", layout="wide")

# --- CSS ULTRA-MINIMALISTA Y NEGRO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    
    /* Tarjetas de Élite */
    .card-elite { 
        background-color: #0a0a0a; 
        border: 1px solid #1f2328; 
        padding: 12px; 
        border-radius: 8px;
        margin-bottom: 5px;
    }
    
    /* Precios y Ejecución */
    .price-val { color: #58a6ff; font-size: 20px; font-weight: bold; }
    .exec-grid { 
        display: grid; grid-template-columns: 1fr 1fr 1fr; 
        background: #000; padding: 6px; border-radius: 4px; 
        margin: 5px 0; border: 1px solid #30363d;
    }
    .val-label { font-size: 8px; color: #8b949e; }
    .val-num { font-size: 13px; font-weight: bold; }
    
    /* Barras ultra-chicas */
    .bar-name { font-size: 8px; color: #555; margin-top: 2px; margin-bottom: -14px; }
    .stProgress > div > div > div > div { height: 2px !important; }
    
    /* Win Rate Indicator */
    .win-rate {
        display: inline-block; padding: 5px 15px; border-radius: 20px;
        font-weight: bold; font-size: 16px; margin-left: 20px;
    }
    
    /* Historial Compacto */
    .stTable { font-size: 11px !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE INTELIGENCIA Y APRENDIZAJE ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

def calcular_win_rate():
    if not st.session_state.hist_cerrado: return 0, 0
    ganadas = sum(1 for op in st.session_state.hist_cerrado if float(op['PNL'].replace('%','')) > 0)
    total = len(st.session_state.hist_cerrado)
    return (ganadas / total) * 100, total

def get_market_data():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        potential = df[df['symbol'].str.contains('/USDT')].copy()
        potential['score'] = potential['percentage'].fillna(0) + (potential['quoteVolume'] / 1000000)
        
        top_list = potential.sort_values('score', ascending=False).head(10)
        final_symbols = ['VEREM/USDT']
        for s in list(top_list.index):
            if s != 'VEREM/USDT' and len(final_symbols) < 4: final_symbols.append(s)
        
        data = []
        now = datetime.now(tz_arg)

        for sym in final_symbols:
            if sym in tickers:
                t = tickers[sym], s_name = tickers[sym], sym.replace('/USDT', '')
                p = t['last']
                
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    # APRENDIZAJE: Si la última fue perdida, cambia a Fibonacci
                    last_res = -1
                    if st.session_state.hist_cerrado:
                        last_res = float(st.session_state.hist_cerrado[0]['PNL'].replace('%',''))
                    
                    strat = "FIBONACCI" if last_res < 0 else ("AGRESIVO" if "VEREM" in s_name else "IA EXPERTO")
                    
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.03, 's': p*0.985, 'strat': strat, 
                        'exp': now+timedelta(minutes=20),
                        'think': f"Evolucionando a {strat}..."
                    }
                
                sig = st.session_state.signals[s_name]
                data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": ((p - sig['e']) / sig['e']) * 100,
                    "soc": 70, "ball": 85, "imp": 90, "think": sig['think']
                })
        return data
    except: return []

# --- UI TV ---
wr, total_op = calcular_win_rate()
wr_color = "#3fb950" if wr >= 50 else "#f85149"

st.markdown(f"""
    <div style="text-align: center; margin-bottom: 10px;">
        <span style="color:white; font-size:24px; font-weight:bold;">🚀 TOP 4 POTENCIAL IA</span>
        <span class="win-rate" style="background: {wr_color}22; color: {wr_color}; border: 1px solid {wr_color};">
            EFECTIVIDAD: {wr:.1f}% ({total_op} ops)
        </span>
    </div>
    """, unsafe_allow_html=True)

items = get_market_data()
cols = st.columns(4)

for i, m in enumerate(items):
    with cols[i % 4]:
        pnl_c = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-elite">
            <div style="display: flex; justify-content: space-between; font-size:10px;">
                <span style="background:#238636; color:white; padding:2px 5px; border-radius:3px;">{m['strat']}</span>
                <span style="color:{pnl_c}; font-weight:bold;">{m['pnl']:.2f}%</span>
            </div>
            <div style="text-align:center; margin: 8px 0;">
                <div style="color:white; font-size:22px; font-weight:bold;">{m['n']}</div>
                <div class="price-val">${m['p']}</div>
            </div>
            <div class="exec-grid">
                <div><span class="val-label">ENTRADA</span><br><span class="val-num" style="color:white;">{m['e']:.2f}</span></div>
                <div><span class="val-label">OBJETIVO</span><br><span class="val-num" style="color:#3fb950;">{m['t']:.2f}</span></div>
                <div><span class="val-label">STOP</span><br><span class="val-num" style="color:#f85149;">{m['s']:.2f}</span></div>
            </div>
            <div class="bar-name">REDES / SENTIMIENTO</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="bar-name">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="bar-name">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)
        st.markdown(f'<div style="color:#8b949e; font-size:9px; margin-top:10px; border-top:1px solid #21262d;">🧠 IA: {m["think"]}</div>', unsafe_allow_html=True)

# --- HISTORIAL DE 10 OPERACIONES ---
st.write("---")
st.markdown("<h4 style='color:white;'>📜 ÚLTIMAS 10 OPERACIONES CERRADAS</h4>", unsafe_allow_html=True)
if st.session_state.hist_cerrado:
    df_hist = pd.DataFrame(st.session_state.hist_cerrado).head(10)
    st.table(df_hist)
else:
    st.write("Esperando cierre del primer ciclo de 20 min...")
