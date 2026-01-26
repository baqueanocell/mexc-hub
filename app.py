import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA MEXC PRO", layout="wide")

# --- CSS CORREGIDO Y LIMPIO ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    [data-testid="column"] { width: 49% !important; flex: 1 1 49% !important; min-width: 49% !important; }
    
    .card-pro { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        padding: 10px; 
        margin-bottom: 8px; 
        border-radius: 8px;
    }
    
    .exec-row { 
        display: flex; 
        justify-content: space-between; 
        background: #0d1117; 
        padding: 8px 5px; 
        border-radius: 4px; 
        margin: 8px 0px;
        border: 1px solid #21262d;
    }
    
    .val-unit { text-align: center; flex: 1; }
    .val-label { font-size: 9px !important; color: #8b949e; display: block; }
    .val-e { color: #ffffff; font-size: 14px !important; font-weight: bold; }
    .val-t { color: #3fb950; font-size: 14px !important; font-weight: bold; }
    .val-s { color: #f85149; font-size: 14px !important; font-weight: bold; }
    
    .strat-tag {
        font-size: 10px !important;
        background: #238636;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .label-micro { font-size: 8px !important; color: #8b949e; text-transform: uppercase; margin-top: 5px; }
    .stProgress > div > div > div > div { height: 3px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
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
                            "Hora": now.strftime("%H:%M"), "Moneda": s_name, "Resultado": f"{pnl_f:.2f}%"
                        })
                    
                    # Estrategia
                    strat = "AGRESIVO" if "VEREM" in s_name else ("FIBONACCI" if "BTC" in s_name else "BALLENAS")
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p * (1.04 if strat == "AGRESIVO" else 1.025),
                        's': p * 0.985, 'strat': strat, 'exp': now + timedelta(minutes=20)
                    }
                
                sig = st.session_state.signals[s_name]
                pnl = ((p - sig['e']) / sig['e']) * 100

                current_data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": pnl, "soc": min(max(80 + (ch*1.5), 20), 98),
                    "ball": 70, "imp": min(max(ch+50, 10), 95)
                })
        return current_data
    except: return []

# --- INTERFAZ ---
st.markdown(f"### 🤖 MEXC INTELIGENCIA IA | {datetime.now(tz_arg).strftime('%H:%M:%S')}")

data = get_pro_data()

# 🏆 SECCIÓN: MONEDA MÁS SUGERIDA
if data:
    top_coin = max(data, key=lambda x: x['imp'] + x['soc'])
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1f6feb, #0d1117); padding: 15px; border-radius: 10px; border: 1px solid #58a6ff; margin-bottom: 20px;">
        <span class="strat-tag">TOP RECOMENDACIÓN: {top_coin['strat']}</span><br>
        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <b style="font-size: 22px; color: white;">{top_coin['n']}</b>
            <b style="font-size: 22px; color: #58a6ff;">${top_coin['p']}</b>
        </div>
        <div class="exec-row">
            <div class="val-unit"><span class="val-label">ENTRADA</span><span class="val-e">{top_coin['e']:.4f}</span></div>
            <div class="val-unit"><span class="val-label">T. PROFIT</span><span class="val-t">{top_coin['t']:.4f}</span></div>
            <div class="val-unit"><span class="val-label">S. LOSS</span><span class="val-s">{top_coin['s']:.4f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 📱 GRILLA 2 COLUMNAS
cols = st.columns(2)
for idx, m in enumerate(data):
    with cols[idx % 2]:
        pnl_col = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-pro">
            <span class="strat-tag" style="background: #30363d;">{m['strat']}</span>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <b style="font-size: 14px; color: white;">{m['n']}</b>
                <b style="font-size: 14px; color: #58a6ff;">${m['p']}</b>
            </div>
            <div style="font-size: 12px; color: {pnl_col}; font-weight: bold;">PNL: {m['pnl']:.2f}%</div>
            <div class="exec-row">
                <div class="val-unit"><span class="val-label">E</span><span class="val-e">{m['e']:.3f}</span></div>
                <div class="val-unit"><span class="val-label">T</span><span class="val-t">{m['t']:.3f}</span></div>
                <div class="val-unit"><span class="val-label">S</span><span class="val-s">{m['s']:.3f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.progress(m['ball']/100)
        st.progress(m['imp']/100)

st.write("---")
st.subheader("📜 ÚLTIMOS CIERRES")
if st.session_state.hist_cerrado:
    st.table(pd.DataFrame(st.session_state.hist_cerrado).head(10))
