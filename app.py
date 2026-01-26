import streamlit as st
import pandas as pd  # <--- Corregido: ya no dará error
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 15 segundos para máxima estabilidad en TV
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3", layout="wide")

# --- CSS PRO-TV (Optimizado) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 5px; border-radius: 4px; margin: 8px 0; border: 1px solid #21262d; text-align: center; }
    .bar-text { font-family: monospace; font-size: 11px; line-height: 1.3; color: #8b949e; }
    .ia-log { background: #001a00; border-left: 4px solid #00ff00; padding: 8px; font-family: monospace; font-size: 12px; color: #00ff00; margin-bottom: 15px; }
    .trig-tag { font-size: 10px; color: #ffca28; font-weight: bold; border: 1px solid #ffca28; padding: 1px 5px; border-radius: 3px; margin-left: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'last_data' not in st.session_state: st.session_state.last_data = []
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []
if 'ia_thought' not in st.session_state: st.session_state.ia_thought = "Iniciando protocolos de búsqueda..."

exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

def draw_bar(val, col="#1f6feb"):
    fill = int(min(max(val, 0), 100) / 10)
    return f'<span style="color:{col};">{"■"*fill}{"□"*(10-fill)}</span> {int(val)}%'

def process_engine():
    try:
        tickers = exchange.fetch_tickers()
        # Monedas configuradas según tus notas técnicas
        selected = ['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        current_list = []
        now = datetime.now(tz_arg)

        for sym in selected:
            if sym in tickers:
                t = tickers[sym]
                s_name = sym.split('/')[0]
                p = t['last']
                
                # Configuración por tipo de activo
                if "VEREM" in s_name: 
                    trig, strat, soc, ball, imp = "VOLATILIDAD", "AGRESIVO", 90, 40, 95
                elif "BTC" in s_name: 
                    trig, strat, soc, ball, imp = "INSTITUCIONAL", "EXPERTO", 75, 95, 40
                elif "ETH" in s_name: 
                    trig, strat, soc, ball, imp = "BALLENAS", "INSTITUCIONAL", 70, 85, 55
                else: 
                    trig, strat, soc, ball, imp = "IMPULSO", "SCALPING", 80, 65, 85

                # Generar señal si no existe
                if s_name not in st.session_state.signals:
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.035, 's': p*0.982, 'strat': strat,
                        'trig': trig, 'exp': now + timedelta(minutes=20)
                    }
                
                sig = st.session_state.signals[s_name]
                pnl = ((p - sig['e']) / sig['e']) * 100

                # Gestión de Riesgo: Trailing Stop
                if pnl > 1.4:
                    sig['s'] = max(sig['s'], sig['e'] * 1.005)
                    st.session_state.ia_thought = f"🛡️ Ganancia protegida en {s_name}. Stop subido a zona segura."

                current_list.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "trig": sig['trig'], "pnl": pnl,
                    "soc": soc, "ball": ball, "imp": imp
                })
        
        if current_list: st.session_state.last_data = current_list
        return st.session_state.last_data
    except Exception as e:
        st.session_state.ia_thought = f"Conexión inestable... reintentando. ({str(now.strftime('%H:%M:%S'))})"
        return st.session_state.last_data

# --- RENDERIZADO ---
data = process_engine()
ops = st.session_state.hist_cerrado
total_ops = len(ops) if ops else 1
ganadas = sum(1 for o in ops if float(o['PNL'].strip('%')) > 0)
p_green = (ganadas / total_ops) * 100

st.markdown(f"""
    <div style="text-align: center; color: white;">
        <span style="font-size: 20px; font-weight: bold;">🛰️ TERMINAL IA ELITE | {datetime.now(tz_arg).strftime('%H:%M:%S')}</span>
        <div style="background:#222; border-radius:10px; height:14px; display:flex; margin:8px 0; border: 1px solid #444;">
            <div style="background:#3fb950; width:{p_green}%;"></div>
            <div style="background:#f85149; width:{100-p_green}%;"></div>
        </div>
    </div>
    <div class="ia-log">🧠 PENSAMIENTO IA: {st.session_state.ia_thought}</div>
    """, unsafe_allow_html=True)

if data:
    cols = st.columns(4)
    for i, m in enumerate(data):
        with cols[i]:
            pnl_c = "#3fb950" if m['pnl'] >= 0 else "#f85149"
            st.markdown(f"""
            <div class="card-tv">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="font-size: 20px; color:white;">{m['n']}<span class="trig-tag">[{m['trig']}]</span></b>
                    <span style="background:#238636; font-size:10px; padding:3px 6px; border-radius:4px;">{m['strat']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top:8px;">
                    <span style="color:#58a6ff; font-weight:bold; font-size:18px;">${m['p']:.4f if m['p'] < 1 else m['p']:.2f}</span>
                    <span style="color:{pnl_c}; font-weight:bold; font-size:16px;">{m['pnl']:.2f}%</span>
                </div>
                <div class="exec-grid">
                    <div><span style="font-size:8px; color:#888;">ENTRADA</span><br><b style="font-size:11px;">{m['e']:.2f}</b></div>
                    <div><span style="font-size:8px; color:#888;">TARGET</span><br><b style="font-size:11px; color:#3fb950;">{m['t']:.2f}</b></div>
                    <div><span style="font-size:8px; color:#888;">STOP</span><br><b style="font-size:11px; color:#f85149;">{m['s']:.2f}</b></div>
                </div>
                <div class="bar-text">
                    SOCIAL: {draw_bar(m['soc'], "#58a6ff")}<br>
                    BALLENAS: {draw_bar(m['ball'], "#bc8cff")}<br>
                    IMPULSO: {draw_bar(m['imp'], "#3fb950")}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br><b style='color:#8b949e; font-size:14px;'>📜 HISTORIAL DE OPERACIONES</b>", unsafe_allow_html=True)
if ops: st.table(pd.DataFrame(ops).head(10))
else: st.info("Sincronizando con el mercado... las operaciones aparecerán aquí.")
