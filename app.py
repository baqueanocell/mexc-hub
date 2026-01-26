import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="TERMINAL IA", layout="wide")

# --- CSS ULTRA-ESTABLE PARA TV (FONDO NEGRO Y SIN ERRORES) ---
st.markdown("""
    <style>
    /* Fondo Negro Total */
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    
    /* Grilla de 5 columnas estable */
    [data-testid="column"] { 
        min-width: 180px !important; 
    }
    
    .card-pro { 
        background-color: #121212; 
        border: 1px solid #333; 
        padding: 10px; 
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    .price-val { color: #58a6ff; font-size: 16px; font-weight: bold; font-family: monospace; }
    
    .exec-grid { 
        display: grid; 
        grid-template-columns: 1fr 1fr 1fr; 
        background: #000; 
        padding: 5px; 
        border-radius: 3px;
        text-align: center;
        margin: 5px 0;
    }
    
    .label-x { font-size: 9px; color: #888; }
    .val-e { color: #fff; font-size: 13px; font-weight: bold; }
    .val-t { color: #00ff00; font-size: 13px; font-weight: bold; }
    .val-s { color: #ff0000; font-size: 13px; font-weight: bold; }
    
    .strat-tag { font-size: 10px; background: #1b5e20; color: #fff; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
    .bar-name { font-size: 8px; color: #666; margin-top: 5px; margin-bottom: -12px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR IA ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

def get_market():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(9)
        symbols = list(top['symbol'].values)
        if 'VEREM/USDT' not in symbols: symbols.insert(0, 'VEREM/USDT')
        
        data = []
        now = datetime.now(tz_arg)

        for sym in symbols[:10]:
            if sym in tickers:
                t = tickers[sym]
                p, ch = t['last'], (t['percentage'] or 0)
                s_name = sym.replace('/USDT', '')
                
                # Nueva señal o mantenimiento
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    if s_name in st.session_state.signals:
                        old = st.session_state.signals[s_name]
                        res = ((p - old['e']) / old['e']) * 100
                        st.session_state.hist_cerrado.insert(0, {"Hora": now.strftime("%H:%M"), "Moneda": s_name, "PNL": f"{res:.2f}%"})
                    
                    strat = "AGRESIVO" if "VEREM" in s_name else "EXPERTO"
                    st.session_state.signals[s_name] = {'e': p, 't': p*1.03, 's': p*0.985, 'strat': strat, 'exp': now+timedelta(minutes=20)}
                
                sig = st.session_state.signals[s_name]
                data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": ((p - sig['e']) / sig['e']) * 100,
                    "soc": min(max(70 + ch, 10), 98), "ball": 75, "imp": min(max(50 + ch, 10), 95)
                })
        return data
    except: return []

# --- PANTALLA ---
st.write(f"### 🤖 TERMINAL IA | {datetime.now(tz_arg).strftime('%H:%M:%S')}")

items = get_market()
cols = st.columns(5)

for i, m in enumerate(items):
    with cols[i % 5]:
        pnl_color = "#00ff00" if m['pnl'] >= 0 else "#ff0000"
        st.markdown(f"""
        <div class="card-pro">
            <span class="strat-tag">{m['strat']}</span>
            <div style="display: flex; justify-content: space-between; margin-top:5px;">
                <b style="color:white; font-size:15px;">{m['n']}</b>
                <span class="price-val">${m['p']}</span>
            </div>
            <div style="color:{pnl_color}; font-size:12px; font-weight:bold;">PNL: {m['pnl']:.2f}%</div>
            <div class="exec-grid">
                <div><span class="label-x">E</span><br><span class="val-e">{m['e']:.2f}</span></div>
                <div><span class="label-x">T</span><br><span class="val-t">{m['t']:.2f}</span></div>
                <div><span class="label-x">S</span><br><span class="val-s">{m['s']:.2f}</span></div>
            </div>
            <div class="bar-name">IA SOCIAL</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="bar-name">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="bar-name">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)

st.write("---")
if st.session_state.hist_cerrado:
    st.markdown("### 📜 ÚLTIMOS CIERRES")
    st.table(pd.DataFrame(st.session_state.hist_cerrado).head(5))
