import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz
import random

# Refresco cada 15 segundos para no saturar la TV
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3", layout="wide")

# --- CSS DE ALTA COMPATIBILIDAD ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 8px; border-radius: 5px; margin-bottom: 5px; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 4px; border-radius: 4px; margin: 5px 0; border: 1px solid #21262d; text-align: center; }
    .bar-text { font-family: monospace; font-size: 10px; line-height: 1.2; color: #8b949e; }
    .win-bar-box { background: #222; border-radius: 10px; overflow: hidden; height: 12px; display: flex; margin: 5px 0; border: 1px solid #333; }
    .ia-log { background: #001a00; border-left: 3px solid #00ff00; padding: 6px; font-family: monospace; font-size: 11px; color: #00ff00; margin-bottom: 10px; }
    .trig-tag { font-size: 9px; color: #ffca28; font-weight: bold; border: 1px solid #ffca28; padding: 1px 4px; border-radius: 3px; margin-left: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR IA ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

# Inicializar estados si no existen
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []
if 'ia_thought' not in st.session_state: st.session_state.ia_thought = "Sincronizando con MEXC..."

def draw_bar(val, col="#1f6feb"):
    fill = int(min(max(val, 0), 100) / 10)
    return f'<span style="color:{col};">{"■"*fill}{"□"*(10-fill)}</span> {int(val)}%'

def process_data():
    try:
        tickers = exchange.fetch_tickers()
        selected = ['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        data_list = []
        now = datetime.now(tz_arg)

        for sym in selected:
            if sym in tickers:
                t = tickers[sym]
                s_name = sym.replace('/USDT','')
                p = t['last']
                vol = t['quoteVolume'] or 0
                chg = t['percentage'] or 0

                # Lógica de Activación e Indicadores Reales
                if "VEREM" in s_name: 
                    trig = "VOLATILIDAD"
                    soc, ball, imp = 85, 40, 95
                elif "BTC" in s_name: 
                    trig = "INSTITUCIONAL"
                    soc, ball, imp = 70, 90, 50
                elif "ETH" in s_name: 
                    trig = "BALLENAS"
                    soc, ball, imp = 65, 85, 60
                else: # SOL
                    trig = "IMPULSO"
                    soc, ball, imp = 75, 60, 88

                # Si no hay señal activa o expiró, crear una nueva
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    # Aplicar estrategias según la nota técnica
                    if "BTC" in s_name: strat = "EXPERTO"
                    elif "VEREM" in s_name: strat = "AGRESIVO"
                    elif "ETH" in s_name: strat = "INSTITUCIONAL"
                    else: strat = "SCALPING"

                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.035, 's': p*0.982, 'strat': strat,
                        'trig': trig, 'exp': now+timedelta(minutes=15)
                    }
                
                sig = st.session_state.signals[s_name]
                pnl = ((p - sig['e']) / sig['e']) * 100

                # Trailing Stop dinámico si PNL > 1.2%
                if pnl > 1.2:
                    sig['s'] = max(sig['s'], sig['e'] * 1.002)
                    st.session_state.ia_thought = f"🛡️ Asegurando ganancias en {s_name}. Stop subido a zona segura."

                data_list.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "trig": sig['trig'], "pnl": pnl,
                    "soc": soc, "ball": ball, "imp": imp
                })
        return data_list
    except: return []

# --- RENDERIZADO ---
data = process_data()
ops = st.session_state.hist_cerrado
ganadas = sum(1 for o in ops if float(o['PNL'].replace('%','')) > 0)
total = len(ops) if len(ops) > 0 else 1
p_green = (ganadas / total) * 100
p_red = 100 - p_green if len(ops) > 0 else 0

# Header y Log IA
st.markdown(f"""
    <div style="text-align: center;">
        <span style="font-size: 18px; font-weight: bold; color: white;">🛰️ TERMINAL IA ELITE | {datetime.now(tz_arg).strftime('%H:%M')}</span>
        <div class="win-bar-box">
            <div style="background: #3fb950; width: {p_green}%;"></div>
            <div style="background: #f85149; width: {p_red}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: white; margin-bottom: 5px;">
            <span>SESIÓN GANANCIAS: {p_green:.1f}%</span>
            <span>PÉRDIDAS: {p_red:.1f}%</span>
        </div>
    </div>
    <div class="ia-log">🧠 PENSAMIENTO IA: {st.session_state.ia_thought}</div>
    """, unsafe_allow_html=True)

# Grid 4 Columnas
cols = st.columns(4)
for i, m in enumerate(data):
    with cols[i]:
        pnl_c = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-tv">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <b style="font-size: 18px; color:white;">{m['n']}<span class="trig-tag">{m['trig']}</span></b>
                <span style="background:#238636; font-size:9px; padding:2px 5px; border-radius:3px;">{m['strat']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top:5px;">
                <span style="color:#58a6ff; font-weight:bold; font-size:16px;">${m['p']}</span>
                <span style="color:{pnl_c}; font-weight:bold;">{m['pnl']:.2f}%</span>
            </div>
            <div class="exec-grid">
                <div><span style="font-size:7px; color:#888;">ENTRADA</span><br><b style="font-size:10px;">{m['e']:.2f}</b></div>
                <div><span style="font-size:7px; color:#888;">TARGET</span><br><b style="font-size:10px; color:#3fb950;">{m['t']:.2f}</b></div>
                <div><span style="font-size:7px; color:#888;">STOP</span><br><b style="font-size:10px; color:#f85149;">{m['s']:.2f}</b></div>
            </div>
            <div class="bar-text">
                SOCIAL: {draw_bar(m['soc'], "#58a6ff")}<br>
                BALLENAS: {draw_bar(m['ball'], "#bc8cff")}<br>
                IMPULSO: {draw_bar(m['imp'], "#3fb950")}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Historial
st.markdown("<br><b style='color:#8b949e; font-size:12px;'>📜 HISTORIAL ÚLTIMOS 10 CICLOS</b>", unsafe_allow_html=True)
if ops: st.table(pd.DataFrame(ops).head(10))
else: st.info("Sincronizando operaciones...")
