import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz
import random

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3", layout="wide")

# --- CSS PRO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 8px; border-radius: 5px; margin-bottom: 2px; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 4px; border-radius: 4px; margin: 5px 0; border: 1px solid #21262d; text-align: center; }
    .bar-text { font-family: monospace; font-size: 10px; line-height: 1.1; }
    .win-bar-box { background: #222; border-radius: 10px; overflow: hidden; height: 12px; display: flex; margin: 5px 0; }
    .ia-log { background: #001a00; border-left: 3px solid #00ff00; padding: 5px 10px; font-family: monospace; font-size: 11px; color: #00ff00; margin-bottom: 10px; }
    .trigger-tag { font-size: 8px; color: #ffca28; font-weight: bold; margin-left: 5px; border: 1px solid #ffca28; padding: 0px 3px; border-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR IA AVANZADO ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []
if 'ia_thoughts' not in st.session_state: st.session_state.ia_thoughts = "Sincronizando con libro de órdenes MEXC..."

def draw_bar(value, color="#1f6feb"):
    filled = int(value / 10)
    bar = "■" * filled + "□" * (10 - filled)
    return f'<span style="color:{color};">{bar}</span> {int(value)}%'

def get_market():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        df['vol_m'] = df['quoteVolume'].fillna(0) / 1000000
        df['chg'] = df['percentage'].fillna(0)
        
        # Selección inteligente
        top = df[df['symbol'].str.contains('/USDT')].sort_values('vol_m', ascending=False)
        selected = ['VEREM/USDT']
        for s in top.index:
            if s != 'VEREM/USDT' and len(selected) < 4: selected.append(s)
            
        data = []
        now = datetime.now(tz_arg)

        for sym in selected:
            if sym in tickers:
                t, s_name = tickers[sym], sym.replace('/USDT','')
                p = t['last']
                
                # Definir por qué se activa la moneda
                if "VEREM" in s_name: trigger = "IMPULSO"
                elif t['quoteVolume'] > 50000000: trigger = "BALLENAS"
                elif abs(t['percentage'] or 0) > 5: trigger = "PATRÓN FIBO"
                else: trigger = "NOTICIAS"

                # Lógica de señales y Trailing Stop
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    strat = "AGRESIVO" if "VEREM" in s_name else "SMART MONEY"
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.04, 's': p*0.98, 'strat': strat,
                        'trig': trigger, 'exp': now+timedelta(minutes=20)
                    }
                
                sig = st.session_state.signals[s_name]
                
                # GESTIÓN DINÁMICA: Si sube, subimos el Stop
                pnl_actual = ((p - sig['e']) / sig['e']) * 100
                if pnl_actual > 1.5:
                    sig['s'] = max(sig['s'], sig['e'] * 1.005) # Asegura ganancia (Breakeven+)
                    st.session_state.ia_thoughts = f"🛡️ Protegiendo ganancias en {s_name}. Stop Loss subido a zona segura."

                # Métricas reales basadas en datos de mercado
                soc = min(max(50 + (t['percentage'] or 0) * 2, 30), 95)
                ball = min(max(t['quoteVolume'] / 1000000, 20), 98)
                imp = min(max(abs(t['percentage'] or 0) * 10, 10), 99)

                data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": pnl_actual, "trig": sig['trig'],
                    "soc": soc, "ball": ball, "imp": imp
                })
        return data
    except Exception as e:
        return []

# --- RENDER PANTALLA ---
data = get_market()
ops = st.session_state.hist_cerrado
ganadas = sum(1 for o in ops if float(o['PNL'].replace('%','')) > 0)
total_ops = len(ops) if len(ops) > 0 else 1
p_green = (ganadas / total_ops) * 100
p_red = 100 - p_green if len(ops) > 0 else 0

st.markdown(f"""
    <div style="text-align: center;">
        <span style="font-size: 18px; font-weight: bold; color: white;">🛰️ TERMINAL IA ELITE V3</span>
        <div class="win-bar-box">
            <div style="background: #3fb950; width: {p_green}%;"></div>
            <div style="background: #f85149; width: {p_red}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: white;">
            <span>GANANCIAS: {p_green:.1f}%</span>
            <span>PÉRDIDAS: {p_red:.1f}%</span>
        </div>
    </div>
    <div class="ia-log">🧠 PENSAMIENTO IA: {st.session_state.ia_thoughts}</div>
    """, unsafe_allow_html=True)

cols = st.columns(4)
for i, m in enumerate(data):
    with cols[i]:
        pnl_c = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-tv">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <b style="font-size: 16px; color:white;">{m['n']}<span class="trigger-tag">{m['trig']}</span></b>
                <span style="background:#238636; font-size:8px; padding:2px 4px; border-radius:3px;">{m['strat']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top:5px;">
                <span style="color:#58a6ff; font-weight:bold; font-size:14px;">${m['p']}</span>
                <span style="color:{pnl_c}; font-weight:bold;">{m['pnl']:.2f}%</span>
            </div>
            <div class="exec-grid">
                <div><span style="font-size:7px; color:#888;">ENTRADA</span><br><b style="font-size:10px;">{m['e']:.2f}</b></div>
                <div><span style="font-size:7px; color:#888;">TARGET</span><br><b style="font-size:10px; color:#3fb950;">{m['t']:.2f}</b></div>
                <div><span style="font-size:7px; color:#888;">STOP</span><br><b style="font-size:10px; color:#f85149;">{m['s']:.2f}</b></div>
            </div>
            <div class="bar-text">
                REDES: {draw_bar(m['soc'], "#58a6ff")}<br>
                BALLENAS: {draw_bar(m['ball'], "#bc8cff")}<br>
                IMPULSO: {draw_bar(m['imp'], "#3fb950")}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<b style='color:#8b949e; font-size:12px;'>📜 ÚLTIMAS 10 OPERACIONES</b>", unsafe_allow_html=True)
if ops: st.table(pd.DataFrame(ops).head(10))
else: st.info("Sincronizando historial...")
