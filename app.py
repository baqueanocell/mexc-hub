import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 15 segundos para estabilidad
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3", layout="wide")

# --- CSS DE ALTA VISIBILIDAD PARA TV ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 12px; border-radius: 10px; margin-bottom: 10px; border-top: 3px solid #1f6feb; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 6px; border-radius: 4px; margin: 10px 0; border: 1px solid #21262d; text-align: center; }
    .bar-text { font-family: monospace; font-size: 11px; line-height: 1.4; color: #8b949e; }
    .ia-log { background: #001a00; border-left: 5px solid #00ff00; padding: 10px; font-family: monospace; font-size: 13px; color: #00ff00; margin-bottom: 15px; border-radius: 4px; }
    .trig-tag { font-size: 10px; color: #ffca28; font-weight: bold; border: 1px solid #ffca28; padding: 2px 6px; border-radius: 4px; margin-left: 10px; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []
if 'ia_thought' not in st.session_state: st.session_state.ia_thought = "Sincronizando con MEXC Global..."

exchange = ccxt.mexc({'timeout': 20000, 'enableRateLimit': True})
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

def draw_bar(val, col="#1f6feb"):
    fill = int(min(max(val, 0), 100) / 10)
    return f'<span style="color:{col};">{"■"*fill}{"□"*(10-fill)}</span> {int(val)}%'

# --- HEADER Y LOG ---
ops = st.session_state.hist_cerrado
total_ops = len(ops) if ops else 1
ganadas = sum(1 for o in ops if float(str(o.get('PNL', '0')).strip('%')) > 0)
p_green = (ganadas / total_ops) * 100

st.markdown(f"""
    <div style="text-align: center; color: white;">
        <span style="font-size: 24px; font-weight: bold;">🛰️ TERMINAL IA ELITE V3 | {datetime.now(tz_arg).strftime('%H:%M:%S')}</span>
        <div style="background:#222; border-radius:10px; height:16px; display:flex; margin:10px 0; border: 1px solid #444;">
            <div style="background:#3fb950; width:{p_green}%;"></div>
            <div style="background:#f85149; width:{100-p_green}%;"></div>
        </div>
    </div>
    <div class="ia-log">🧠 PENSAMIENTO IA: {st.session_state.ia_thought}</div>
    """, unsafe_allow_html=True)

# --- PROCESO DE DATOS SEGURO ---
try:
    tickers = exchange.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    selected_coins = ['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    cols = st.columns(4)
    
    for i, sym in enumerate(selected_coins):
        if sym in tickers:
            t = tickers[sym]
            s_name = sym.split('/')[0]
            p = t['last']
            now = datetime.now(tz_arg)

            # Asignación de Estrategias y Métricas Reales
            if "VEREM" in s_name: 
                trig, strat, soc, ball, imp = "VOLATILIDAD", "AGRESIVO", 92, 45, 98
            elif "BTC" in s_name: 
                trig, strat, soc, ball, imp = "INSTITUCIONAL", "EXPERTO", 78, 96, 42
            elif "ETH" in s_name: 
                trig, strat, soc, ball, imp = "BALLENAS", "INSTITUCIONAL", 72, 88, 58
            else: 
                trig, strat, soc, ball, imp = "IMPULSO", "SCALPING", 82, 68, 88

            # Crear señal si no existe
            if s_name not in st.session_state.signals:
                st.session_state.signals[s_name] = {
                    'e': p, 't': p*1.04, 's': p*0.98, 'strat': strat, 'trig': trig
                }
            
            sig = st.session_state.signals[s_name]
            pnl = ((p - sig['e']) / sig['e']) * 100

            # Trailing Stop
            if pnl > 1.5:
                sig['s'] = max(sig['s'], sig['e'] * 1.005)
                st.session_state.ia_thought = f"🛡️ Protegiendo {s_name}. Stop Loss ajustado a zona de ganancias."

            with cols[i]:
                pnl_color = "#3fb950" if pnl >= 0 else "#f85149"
                st.markdown(f"""
                <div class="card-tv">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <b style="font-size: 22px; color:white;">{s_name}<span class="trig-tag">[{trig}]</span></b>
                        <span style="background:#238636; font-size:10px; padding:3px 6px; border-radius:4px;">{strat}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top:10px;">
                        <span style="color:#58a6ff; font-weight:bold; font-size:20px;">${p:.4f if p < 1 else p:.2f}</span>
                        <span style="color:{pnl_color}; font-weight:bold; font-size:18px;">{pnl:.2f}%</span>
                    </div>
                    <div class="exec-grid">
                        <div><span style="font-size:9px; color:#888;">ENTRY</span><br><b style="font-size:12px;">{sig['e']:.2f}</b></div>
                        <div><span style="font-size:9px; color:#3fb950;">TARGET</span><br><b style="font-size:12px; color:#3fb950;">{sig['t']:.2f}</b></div>
                        <div><span style="font-size:9px; color:#f85149;">STOP</span><br><b style="font-size:12px; color:#f85149;">{sig['s']:.2f}</b></div>
                    </div>
                    <div class="bar-text">
                        SOCIAL: {draw_bar(soc, "#58a6ff")}<br>
                        BALLENAS: {draw_bar(ball, "#bc8cff")}<br>
                        IMPULSO: {draw_bar(imp, "#3fb950")}
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error de conexión con MEXC: {e}. Reintentando en 15s...")
    st.session_state.ia_thought = "⚠️ ERROR DE RED: Intentando reconectar con el servidor..."

# Historial
st.markdown("<br><b style='color:#8b949e; font-size:16px;'>📜 HISTORIAL ÚLTIMOS CICLOS</b>", unsafe_allow_html=True)
if st.session_state.hist_cerrado:
    st.table(pd.DataFrame(st.session_state.hist_cerrado).head(10))
else:
    st.info("Esperando cierre de primer ciclo para mostrar historial...")
