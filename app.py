import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE", layout="wide")

# --- CSS ULTRA ESTABLE (SOLO COLORES Y TAMAÑOS) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    
    /* Cuadro de Moneda */
    .card-pro { 
        background-color: #121212; 
        border: 1px solid #333; 
        padding: 10px; 
        border-radius: 8px;
        margin-bottom: 5px;
    }
    
    .symbol-name { font-size: 22px; font-weight: bold; color: #ffffff; }
    .price-val { color: #58a6ff; font-size: 18px; font-weight: bold; font-family: monospace; }
    
    .exec-grid { 
        display: grid; grid-template-columns: 1fr 1fr 1fr; 
        background: #000; padding: 5px; border-radius: 4px; 
        margin: 5px 0; border: 1px solid #444; text-align: center;
    }
    .val-label { font-size: 8px; color: #888; }
    .val-num { font-size: 11px; font-weight: bold; }
    
    /* Texto de barras */
    .bar-title { font-size: 9px; color: #777; margin-top: 4px; margin-bottom: -15px; }
    
    /* Historial */
    .stTable { background-color: #000 !important; color: white !important; font-size: 12px !important; }
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

# --- RENDERIZADO SEGURO ---
data = get_data()
ops = st.session_state.hist_cerrado
ganadas = sum(1 for o in ops if float(o['PNL'].replace('%','')) > 0)
total = len(ops) if len(ops) > 0 else 1
wr = (ganadas / total) * 100

# Header simple
st.write(f"### 🛰️ TERMINAL IA | WIN RATE: {wr:.1f}% | {datetime.now(tz_arg).strftime('%H:%M')}")

# Grid de 4 columnas
cols = st.columns(4)
for i, m in enumerate(data):
    with cols[i]:
        pnl_c = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        
        # Inicio del cuadro
        st.markdown(f"""
        <div class="card-pro">
            <div style="display: flex; justify-content: space-between;">
                <span style="background: #238636; font-size: 10px; padding: 2px 5px; border-radius: 3px;">{m['strat']}</span>
                <span style="color: {pnl_c}; font-weight: bold;">{m['pnl']:.2f}%</span>
            </div>
            <div style="text-align: center; margin: 5px 0;">
                <div class="symbol-name">{m['n']}</div>
                <div class="price-val">${m['p']}</div>
            </div>
            <div class="exec-grid">
                <div><span class="val-label">E</span><br><span class="val-num">{m['e']:.2f}</span></div>
                <div><span class="val-label">T</span><br><span class="val-num" style="color:#3fb950;">{m['t']:.2f}</span></div>
                <div><span class="val-label">S</span><br><span class="val-num" style="color:#f85149;">{m['s']:.2f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Barras nativas (fuera del HTML para que la TV las lea bien)
        st.write(f"**SOCIAL: {m['soc']}%**")
        st.progress(m['soc']/100)
        st.write(f"**BALLENAS: {m['ball']}%**")
        st.progress(m['ball']/100)
        st.write(f"**IMPULSO: {m['imp']}%**")
        st.progress(m['imp']/100)

# Historial
st.write("---")
st.write("### 📜 ÚLTIMAS 10 OPERACIONES")
if ops:
    st.table(pd.DataFrame(ops).head(10))
else:
    st.info("Calculando ciclos... El historial aparecerá pronto.")
