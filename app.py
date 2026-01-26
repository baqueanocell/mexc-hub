import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="MEXC Inteligencia IA", layout="wide")

# --- CSS PRO (DISEÑO DE CARTAS SEPARADAS) ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    [data-testid="column"] { width: 49% !important; flex: 1 1 49% !important; min-width: 49% !important; }
    div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; }
    .stProgress > div > div > div > div { height: 2px !important; }
    
    .card-pro { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        padding: 8px; 
        margin-bottom: 6px; 
        border-radius: 6px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .price-big { color: #58a6ff; font-size: 16px !important; font-weight: bold; font-family: monospace; }
    .strategy-tag { 
        font-size: 9px; padding: 2px 5px; border-radius: 3px; 
        background-color: #238636; color: white; font-weight: bold;
    }
    .label-micro { font-size: 7px !important; color: #8b949e; margin-bottom: -15px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'historial_cerrado' not in st.session_state: st.session_state.historial_cerrado = []

def asignar_estrategia(sym, change):
    if "VEREM" in sym: return "Agresivo"
    if "BTC" in sym or "ETH" in sym: return "Fibonacci"
    if abs(change) > 5: return "Impulso Pro"
    return "Experto / Ballenas"

def get_market_data():
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
                p = t['last']
                ch = t['percentage'] or 0
                s_name = sym.replace('/USDT', '')
                
                # Gestión de Señales y Cierre
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['expires']:
                    # Registrar cierre en historial si existía
                    if s_name in st.session_state.signals:
                        old = st.session_state.signals[s_name]
                        pnl_f = ((p - old['entry']) / old['entry']) * 100
                        st.session_state.historial_cerrado.insert(0, {
                            "Hora Cierre": now.strftime("%H:%M"),
                            "Moneda": s_name,
                            "Estrategia": old['strat'],
                            "Resultado": f"{pnl_f:.2f}%"
                        })
                    
                    # Nueva Señal con Estrategia Individual
                    strat = asignar_estrategia(s_name, ch)
                    tp_val = 1.04 if strat == "Agresivo" else 1.025
                    
                    st.session_state.signals[s_name] = {
                        'entry': p, 'tp': p * tp_val, 'sl': p * 0.985,
                        'strat': strat, 'expires': now + timedelta(minutes=20)
                    }
                
                sig = st.session_state.signals[s_name]
                pnl_act = ((p - sig['entry']) / sig['entry']) * 100

                current_data.append({
                    "n": s_name, "p": p, "strat": sig['strat'], "entry": sig['entry'],
                    "tp": sig['tp'], "sl": sig['sl'], "pnl": pnl_act,
                    "soc": min(max(80 + (ch * 1.5), 30), 98), "ball": 75 if ch > 0 else 40, "imp": min(max(ch+50, 10), 95)
                })
        return current_data
    except: return []

# --- INTERFAZ ---
st.markdown(f"### 🤖 MEXC INTELIGENCIA IA <span style='font-size:12px; color:#8b949e;'>{datetime.now(tz_arg).strftime('%H:%M:%S')} ARG</span>", unsafe_allow_html=True)

data = get_market_data()

# RECOMENDACIÓN TOP
if data:
    best = max(data, key=lambda x: x['imp'])
    st.markdown(f"""
    <div style="background: #161b22; padding: 10px; border-radius: 6px; border-left: 4px solid #58a6ff; margin-bottom: 10px;">
        <span class="strategy-tag">{best['strat']}</span><br>
        <b style="font-size:18px; color:white;">{best['n']}</b> <span class="price-big" style="margin-left:10px;">${best['p']}</span>
        <div style="color:{'#3fb950' if best['pnl'] >= 0 else '#f85149'}; font-weight:bold;">PNL: {best['pnl']:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# GRILLA 2 COLUMNAS (MÓVIL VERTICAL)
cols = st.columns(2)
for idx, m in enumerate(data):
    with cols[idx % 2]:
        st.markdown(f"""
        <div class="card-pro">
            <span class="strategy-tag" style="background:#30363d">{m['strat']}</span><br>
            <b style="font-size:13px;">{m['n']}</b> <span class="price-big" style="float:right;">${m['p']}</span><br>
            <span style="font-size:11px; color:{'#3fb950' if m['pnl'] >= 0 else '#f85149'};">PNL: {m['pnl']:.2f}%</span>
            <div style="font-size:8px; color:#8b949e; margin-top:2px;">E: {m['entry']:.3f} | T: {m['tp']:.3f}</div>
            <div class="label-micro">IA SCORE</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="label-micro">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="label-micro">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)

st.write("---")

# --- HISTORIAL DE CIERRES ---
st.subheader("📜 Cierres de Ciclo (20 min)")
if st.session_state.historial_cerrado:
    st.table(pd.DataFrame(st.session_state.historial_cerrado).head(10))
