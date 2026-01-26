import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

# Configuración de página para aprovechar todo el ancho de la TV
st.set_page_config(page_title="IA MEXC TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# --- CSS ESPECIAL PARA TV (FONDO NEGRO ABSOLUTO Y GRILLA DENSA) ---
st.markdown("""
    <style>
    /* Fondo Negro Absoluto en toda la app */
    .main, .block-container, stApp { 
        background-color: #000000 !important; 
    }
    
    /* Forzar 4 o 5 columnas en pantallas grandes */
    [data-testid="column"] { 
        min-width: 200px !important; 
        flex: 1 1 18% !important; 
    }
    
    .card-pro { 
        background-color: #0d1117; 
        border: 1px solid #1f2328; 
        padding: 6px; 
        margin-bottom: 5px; 
        border-radius: 4px;
    }
    
    /* Números y Textos optimizados para TV */
    .price-main { color: #58a6ff; font-size: 14px !important; font-weight: bold; font-family: monospace; }
    .exec-row { 
        display: flex; 
        justify-content: space-between; 
        background: #000000; 
        padding: 4px; 
        border-radius: 3px; 
        margin: 4px 0px;
        border: 1px solid #30363d;
    }
    .val-unit { text-align: center; flex: 1; }
    .val-label { font-size: 8px !important; color: #8b949e; display: block; }
    .val-e { color: #ffffff; font-size: 12px !important; font-weight: bold; }
    .val-t { color: #3fb950; font-size: 12px !important; font-weight: bold; }
    .val-s { color: #f85149; font-size: 12px !important; font-weight: bold; }
    
    .strat-tag { font-size: 8px !important; background: #238636; color: white; padding: 1px 4px; border-radius: 2px; }
    .label-bar { font-size: 7px !important; color: #8b949e; margin-bottom: -16px; margin-top: 2px; }
    .stProgress > div > div > div > div { height: 2px !important; }
    
    /* Historial compacto */
    .stTable { font-size: 10px !important; background-color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA IA ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

def get_data():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        top_vol = df[df['symbol'].str.contains('/USDT')].sort_values('quoteVolume', ascending=False).head(9)
        symbols = list(top_vol['symbol'].values)
        if 'VEREM/USDT' not in symbols: symbols.insert(0, 'VEREM/USDT')
        
        current_data = []
        now = datetime.now(tz_arg)

        for sym in symbols[:10]:
            if sym in tickers:
                t = tickers[sym]
                p, ch = t['last'], (t['percentage'] or 0)
                s_name = sym.replace('/USDT', '')
                
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    if s_name in st.session_state.signals:
                        old = st.session_state.signals[s_name]
                        pnl_f = ((p - old['e']) / old['e']) * 100
                        st.session_state.hist_cerrado.insert(0, {"H": now.strftime("%H:%M"), "M": s_name, "PNL": f"{pnl_f:.2f}%", "ST": old['strat']})
                    
                    strat = "AGRESIVO" if "VEREM" in s_name else "BALLENAS"
                    st.session_state.signals[s_name] = {'e': p, 't': p*1.025, 's': p*0.985, 'strat': strat, 'exp': now+timedelta(minutes=20)}
                
                sig = st.session_state.signals[s_name]
                current_data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": ((p - sig['e']) / sig['e']) * 100,
                    "soc": min(max(80 + (ch*1.5), 20), 98), "ball": 70, "imp": min(max(ch+50, 10), 95)
                })
        return current_data
    except: return []

# --- INTERFAZ TV ---
st.markdown(f"<h3 style='color:white; margin-top:-30px;'>🤖 IA TERMINAL | {datetime.now(tz_arg).strftime('%H:%M')} ARG</h3>", unsafe_allow_html=True)

data = get_data()

# GRILLA DE 5 COLUMNAS PARA TV
cols = st.columns(5)
for idx, m in enumerate(data):
    with cols[idx % 5]:
        pnl_c = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-pro">
            <span class="strat-tag">{m['strat']}</span>
            <div style="display: flex; justify-content: space-between; margin-top: 2px;">
                <b style="font-size: 12px; color: white;">{m['n']}</b>
                <b class="price-main">${m['p']}</b>
            </div>
            <div style="font-size: 10px; color: {pnl_c}; font-weight: bold;">PNL: {m['pnl']:.2f}%</div>
            <div class="exec-row">
                <div class="val-unit"><span class="val-label">E</span><span class="val-e">{m['e']:.2f}</span></div>
                <div class="val-unit"><span class="val-label">T</span><span class="val-t">{m['t']:.2f}</span></div>
                <div class="val-unit"><span class="val-label">S</span><span class="val-s">{m['s']:.2f}</span></div>
            </div>
            <div class="label-bar">IA SOCIAL</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="label-bar">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="label-bar">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)

st.write("---")

# HISTORIAL EN TV (Más compacto)
if st.session_state.hist_cerrado:
    st.markdown("<span style='color:gray; font-size:12px;'>📜 ÚLTIMOS CIERRES</span>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.hist_cerrado).head(6), use_container_width=True)
