import streamlit as st
import pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 12 segundos para estabilidad total
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=12000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3", layout="wide")

# --- CSS DE ALTA COMPATIBILIDAD (Corregido para TV) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 8px; border-radius: 5px; margin-bottom: 5px; min-height: 180px; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 4px; border-radius: 4px; margin: 5px 0; border: 1px solid #21262d; text-align: center; }
    .bar-text { font-family: monospace; font-size: 10px; line-height: 1.2; color: #8b949e; }
    .ia-log { background: #001a00; border-left: 3px solid #00ff00; padding: 6px; font-family: monospace; font-size: 11px; color: #00ff00; margin-bottom: 10px; }
    .trig-tag { font-size: 9px; color: #ffca28; font-weight: bold; border: 1px solid #ffca28; padding: 1px 4px; border-radius: 3px; margin-left: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE MEMORIA ---
if 'last_data' not in st.session_state: st.session_state.last_data = []
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'hist_cerrado' not in st.session_state: st.session_state.hist_cerrado = []
if 'ia_thought' not in st.session_state: st.session_state.ia_thought = "Escaneando mercados..."

exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

def draw_bar(val, col="#1f6feb"):
    fill = int(min(max(val, 0), 100) / 10)
    return f'<span style="color:{col};">{"■"*fill}{"□"*(10-fill)}</span> {int(val)}%'

def process_engine():
    try:
        tickers = exchange.fetch_tickers()
        selected = ['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        current_list = []
        now = datetime.now(tz_arg)

        for sym in selected:
            if sym in tickers:
                t = tickers[sym]
                s_name = sym.split('/')[0]
                p = t['last']
                
                # Asignar disparador por tipo de moneda
                if "VEREM" in s_name: trig, soc, ball, imp = "VOLATILIDAD", 88, 45, 96
                elif "BTC" in s_name: trig, soc, ball, imp = "INSTITUCIONAL", 72, 92, 45
                elif "ETH" in s_name: trig, soc, ball, imp = "BALLENAS", 68, 86, 58
                else: trig, soc, ball, imp = "IMPULSO", 78, 62, 85

                if s_name not in st.session_state.signals:
                    # Estrategias según activo: BTC (Experto), VEREM (Agresivo), ETH (Institucional)
                    if "BTC" in s_name: strat = "EXPERTO"
                    elif "VEREM" in s_name: strat = "AGRESIVO"
                    elif "ETH" in s_name: strat = "INSTITUCIONAL"
                    else: strat = "SCALPING"

                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.038, 's': p*0.981, 'strat': strat,
                        'trig': trig, 'exp': now+timedelta(minutes=15)
                    }
                
                sig = st.session_state.signals[s_name]
                pnl = ((p - sig['e']) / sig['e']) * 100

                # Lógica de Trailing Stop activa
                if pnl > 1.3:
                    sig['s'] = max(sig['s'], sig['e'] * 1.003)
                    st.session_state.ia_thought = f"🛡️ Ganancia protegida en {s_name}. Stop subido automáticamente."

                current_list.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "trig": sig['trig'], "pnl": pnl,
                    "soc": soc, "ball": ball, "imp": imp
                })
        
        if current_list:
            st.session_state.last_data = current_list
        return st.session_state.last_data
    except:
        return st.session_state.last_data # Si falla el internet, devolver lo último que vimos

# --- RENDERIZADO ---
data = process_engine()
ops = st.session_state.hist_cerrado
total = len(ops) if ops else 1
p_green = (sum(1 for o in ops if float(o['PNL'].strip('%')) > 0) / total) * 100 if ops else 0

# UI Principal
st.markdown(f"""
    <div style="text-align: center; color: white;">
        <span style="font-size: 18px; font-weight: bold;">🛰️ TERMINAL IA ELITE | {datetime.now(tz_arg).strftime('%H:%M')}</span>
        <div style="background:#222; border-radius:10px; height:12px; display:flex; margin:5px 0;">
            <div style="background:#3fb950; width:{p_green}%;"></div>
            <div style="background:#f85149; width:{100-p_green}%;"></div>
        </div>
    </div>
    <div class="ia-log">🧠 PENSAMIENTO IA: {st.session_state.ia_thought}</div>
    """, unsafe_allow_html=True)

# Grid de Monedas
if data:
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
                    <span style="color:#58a6ff; font-weight:bold; font-size:16px;">${m['p']:.4f if m['p'] < 1 else m['p']:.2f}</span>
                    <span style="color:{pnl_c}; font-weight:bold;">{m['pnl']:.2f}%</span>
                </div>
                <div class="exec-grid">
                    <div><span style="font-size:7px; color:#888;">IN</span><br><b style="font-size:10px;">{m['e']:.2f}</b></div>
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
else:
    st.warning("Aguardando respuesta del servidor MEXC...")
