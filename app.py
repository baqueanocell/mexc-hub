import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA MEXC PRO", layout="wide")

# --- CSS DE ALTA JERARQUÍA (NÚMEROS GRANDES) ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    [data-testid="column"] { width: 49% !important; flex: 1 1 49% !important; min-width: 49% !important; }
    
    /* Tarjeta Compacta con Foco en Números */
    .card-pro { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        padding: 10px; 
        margin-bottom: 8px; 
        border-radius: 8px;
    }
    
    /* Precios y Ejecución */
    .price-main { color: #58a6ff; font-size: 18px !important; font-weight: bold; font-family: monospace; }
    .exec-box { background: #0d1117; padding: 5px; border-radius: 4px; margin-top: 5px; border: 1px solid #21262d; }
    .val-e { color: #ffffff; font-size: 15px !important; font-weight: bold; }
    .val-t { color: #3fb950; font-size: 15px !important; font-weight: bold; }
    .val-s { color: #f85149; font-size: 15px !important; font-weight: bold; }
    
    .label-micro { font-size: 8px !important; color: #8b949e; text-transform: uppercase; margin-bottom: -15px; }
    .stProgress > div > div > div > div { height: 2px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE MERCADO ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []

def get_pro_data():
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
                
                # Gestión de Ciclos de 20 min
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    if s_name in st.session_state.signals:
                        old = st.session_state.signals[s_name]
                        pnl_f = ((p - old['e']) / old['e']) * 100
                        st.session_state.hist_cerrado.insert(0, {
                            "Hora": now.strftime("%H:%M"), "Moneda": s_name, "Resultado": f"{pnl_f:.2f}%"
                        })
                    
                    # Estrategia según moneda
                    strat = "Agresivo" if "VEREM" in s_name else "Scalping"
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p * (1.035 if strat == "Agresivo" else 1.02),
                        's': p * 0.988, 'exp': now + timedelta(minutes=20)
                    }
                
                sig = st.session_state.signals[s_name]
                pnl = ((p - sig['e']) / sig['e']) * 100

                current_data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "pnl": pnl, "soc": min(max(80 + (ch*1.5), 20), 98),
                    "ball": 75 if ch > 0 else 45, "imp": min(max(ch+50, 5), 95)
                })
        return current_data
    except: return []

# --- UI ---
st.markdown(f"### 🤖 MEXC INTELIGENCIA IA | {datetime.now(tz_arg).strftime('%H:%M:%S')}")

data = get_pro_data()

# GRILLA 2 COLUMNAS
cols = st.columns(2)
for idx, m in enumerate(data):
    with cols[idx % 2]:
        pnl_color = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-pro">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <b style="font-size:15px; color:white;">{m['n']}</b>
                <span class="price-main">${m['p']}</span>
            </div>
            <div style="font-size:12px; color:{pnl_color}; font-weight:bold; margin-bottom:5px;">
                PNL: {m['pnl']:.2f}%
            </div>
            <div class="exec-box">
                <span style="color:#8b949e; font-size:10px;">ORDEN IA:</span><br>
                <span class="val-e">E: {m['e']:.4f}</span><br>
                <span class="val-t">T: {m['t']:.4f}</span><br>
                <span class="val-s">S: {m['s']:.4f}</span>
            </div>
            <div class="label-micro" style="margin-top:10px;">SOCIAL</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="label-micro">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="label-micro">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)

st.write("---")

# --- HISTORIAL ---
st.markdown("### 📜 CIERRES DE OPERACIÓN (20 MIN)")
if st.session_state.hist_cerrado:
    st.table(pd.DataFrame(st.session_state.hist_cerrado).head(10))
