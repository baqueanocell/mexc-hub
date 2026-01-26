import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA MEXC PRO", layout="wide")

# --- CSS DE ALTA DENSIDAD (HORIZONTAL + ESTRATEGIA) ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    [data-testid="column"] { width: 49% !important; flex: 1 1 49% !important; min-width: 49% !important; }
    
    .card-pro { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        padding: 8px; 
        margin-bottom: 6px; 
        border-radius: 6px;
    }
    
    .price-main { color: #58a6ff; font-size: 15px !important; font-weight: bold; font-family: monospace; }
    
    /* Caja de Ejecución Horizontal */
    .exec-row { 
        display: flex; 
        justify-content: space-between; 
        background: #0d1117; 
        padding: 6px 4px; 
        border-radius: 4px; 
        margin: 5px 0px;
        border: 1px solid #21262d;
    }
    .val-unit { text-align: center; line-height: 1; }
    .val-label { font-size: 8px !important; color: #8b949e; display: block; margin-bottom: 2px; }
    .val-e { color: #ffffff; font-size: 13px !important; font-weight: bold; }
    .val-t { color: #3fb950; font-size: 13px !important; font-weight: bold; }
    .val-s { color: #f85149; font-size: 13px !important; font-weight: bold; }
    
    /* Estrategia */
    .strat-tag {
        font-size: 8px !important;
        background: #238636;
        color: white;
        padding: 1px 4px;
        border-radius: 3px;
        text-transform: uppercase;
        font-weight: bold;
    }
    
    .label-micro { font-size: 7px !important; color: #8b949e; text-transform: uppercase; margin-bottom: -15px; }
    .stProgress > div > div > div > div { height: 2px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA ---
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
                
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    if s_name in st.session_state.signals:
                        old = st.session_state.signals[s_name]
                        pnl_f = ((p - old['e']) / old['e']) * 100
                        st.session_state.hist_cerrado.insert(0, {
                            "Hora": now.strftime("%H:%M"), "Moneda": s_name, "Estrat": old['strat'], "PNL": f"{pnl_f:.2f}%"
                        })
                    
                    # Asignación de Estrategia
                    if "VEREM" in s_name: strat = "AGRESIVO"
                    elif "BTC" in s_name or "ETH" in s_name: strat = "FIBONACCI"
                    else: strat = "BALLENAS"
                    
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p * (1.035 if strat == "AGRESIVO" else 1.02),
                        's': p * 0.988, 'strat': strat, 'exp': now + timedelta(minutes=20)
                    }
                
                sig = st.session_state.signals[s_name]
                pnl = ((p - sig['e']) / sig['e']) * 100

                current_data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": pnl, "soc": min(max(80 + (ch*1.5), 20), 98),
                    "ball": 75 if ch > 0 else 45, "imp": min(max(ch+50, 5), 95)
                })
        return current_data
    except: return []

# --- UI ---
st.markdown(f"### 🤖 MEXC IA | {datetime.now(tz_arg).strftime('%H:%M:%S')}")

data = get_pro_data()

cols = st.columns(2)
for idx, m in enumerate(data):
    with cols[idx % 2]:
        pnl_color = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-pro">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <span class="strat-tag">{m['strat']}</span><br>
                    <b style="font-size:13px; color:white;">{m['n']}</b>
                </div>
                <div style="text-align: right;">
                    <span class="price-main">${m['p']}</span><br>
                    <span style="font-size:11px; color:{pnl_color}; font-weight:bold;">{m['pnl']:.2f}%</span>
                </div>
            </div>
            
            <div class="exec-row">
                <div class="val-unit"><span class="val-label">ENTRADA</span><span class="val-e">{m['e']:.3f}</span></div>
                <div class="val-unit"><span class="val-label">T. PROFIT</span><span class="val-t">{m['t']:.3f}</span></div>
                <div class="val-unit"><span class="val-label">S. LOSS</span><span class="val-s">{m['s']:.3f}</span></div>
            </div>

            <div class="label-micro">IA SCORE</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="label-micro">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="label-micro">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)

st.write("---")
st.markdown("### 📜 CIERRES DE CICLO (20 MIN)")
if st.session_state.hist_cerrado:
    st.table(pd.DataFrame(st.session_state.hist_cerrado).head(10))
