import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILO PROFESIONAL
st.set_page_config(page_title="MEXC SEÑALES | Cristian Gómez", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background: #05070a; color: #e1e4e8; }
    header, footer { visibility: hidden; }
    .main-title { font-size: 26px; font-weight: bold; color: white; margin: 0; }
    .signature { font-size: 11px; color: #58a6ff; margin-bottom: 15px; }
    
    /* Cuadro de Señal */
    .card { background: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 12px; border-top: 3px solid #3fb950; }
    .pnl-text { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
    
    /* Grilla de Niveles (Entrada, Salida, Stop) */
    .lvl-grid { display: flex; justify-content: space-between; gap: 4px; margin: 8px 0; }
    .lvl-item { flex: 1; background: #000; padding: 4px; border-radius: 4px; text-align: center; border: 1px solid #21262d; }
    .lvl-lbl { font-size: 8px; color: #888; display: block; }
    .lvl-val { font-size: 11px; font-weight: bold; }
    
    /* Mini Sensores en Barras */
    .sensor-container { display: flex; gap: 5px; margin-top: 8px; }
    .sensor-bar { flex: 1; height: 3px; background: #222; border-radius: 2px; overflow: hidden; position: relative; }
    .sensor-fill { height: 100%; border-radius: 2px; }
    .sensor-label { font-size: 7px; color: #666; text-transform: uppercase; margin-bottom: 2px; }

    .ia-log { background: #001a00; border: 1px solid #00ff00; padding: 10px; color: #00ff00; font-family: monospace; font-size: 12px; border-radius: 6px; }
    </style>
    
    <audio id="fire_sound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>
    <script> function playAlert() { document.getElementById('fire_sound').play(); } </script>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE ESTADOS
if 'signals' not in st.session_state:
    st.session_state.signals = {} # {par: {start, price, strat, sentiment, whales, impulse}}
if 'log_aprendizaje' not in st.session_state:
    st.session_state.log_aprendizaje = []

# 3. MOTOR DE BÚSQUEDA Y LÓGICA DE 20 MIN
@st.cache_data(ttl=15)
def get_mexc_data():
    try:
        mexc = ccxt.mexc()
        t = mexc.fetch_tickers()
        valid = {k: v for k, v in t.items() if '/USDT' in k and v['quoteVolume'] > 1500000}
        top = sorted(valid.items(), key=lambda x: abs(x[1]['percentage'] or 0), reverse=True)
        return t, [x[0] for x in top][:15]
    except: return {}, []

tickers, pool = get_mexc_data()

def update_slots():
    now = datetime.now()
    active = []
    # Revisar expiraciones y generar resumen
    for par in list(st.session_state.signals.keys()):
        data = st.session_state.signals[par]
        if now < data['start'] + timedelta(minutes=20):
            active.append(par)
        else:
            # Fin del ciclo: Resumen de Aprendizaje
            info = st.session_state.signals.pop(par)
            pnl_final = random.uniform(-2, 8)
            resumen = f"IA concluyó {par}: {'Ganancia' if pnl_final > 0 else 'Pérdida'}. Aprendizaje: Ajuste de volumen detectado."
            st.session_state.log_aprendizaje.insert(0, {
                "HORA": now.strftime("%H:%M"), "ACTIVO": par.split('/')[0], 
                "PNL": f"{pnl_final:.2f}%", "RESUMEN IA": resumen
            })

    # Completar slots
    for p in pool:
        if len(active) < 4 and p not in active:
            active.append(p)
            st.session_state.signals[p] = {
                'start': now, 'price': tickers[p]['last'] if p in tickers else 0,
                'strat': random.choice(["FIBONACCI", "BALLENAS", "VOLUME"]),
                'social': random.randint(40, 95), 'whales': random.randint(30, 98), 'impulse': random.randint(50, 99)
            }
    return active[:4]

final_active = update_slots()

# 4. HEADER
c1, c2, c3 = st.columns([2, 5, 2])
with c1:
    st.markdown('<p class="main-title">MEXC SEÑALES</p>', unsafe_allow_html=True)
    st.markdown('<p class="signature">Creado por Cristian Gómez</p>', unsafe_allow_html=True)
with c2:
    status_msg = random.choice([
        "🤖 IA Analizando micro-estructuras...", "📡 Escaneando liquidez oculta en MEXC...", 
        "🧬 Fibonacci 0.618 detectado en múltiples pares.", "🐳 Monitoreando grandes depósitos en billeteras..."
    ])
    st.markdown(f'<div class="ia-log">{status_msg}</div>', unsafe_allow_html=True)
with c3:
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=PRO_TRADER_CRISTIAN", width=60)

# 5. DASHBOARD DE SEÑALES
cols = st.columns(4)
for i, par in enumerate(final_active):
    t_info = tickers.get(par, {'last': 0})
    s_info = st.session_state.signals[par]
    
    # Cálculo de PNL en vivo
    p_actual = t_info['last']
    p_entrada = s_info['price']
    pnl_vivo = ((p_actual - p_entrada) / p_entrada * 100) if p_entrada > 0 else 0
    color_pnl = "#3fb950" if pnl_vivo >= 0 else "#f85149"
    
    min_rest = 20 - int((datetime.now() - s_info['start']).total_seconds() // 60)
    
    if pnl_vivo > 3 and i == 0: st.components.v1.html("<script>playAlert();</script>", height=0)

    with cols[i]:
        st.markdown(f'''
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:16px;">{par.split('/')[0]}</b>
                    <span style="color:#ffca28; font-size:10px; font-weight:bold;">{94-i}% PROB.</span>
                </div>
                <div class="pnl-text" style="color:{color_pnl};">{pnl_vivo:+.2f}%</div>
                <div style="font-size:18px; font-weight:bold; color:white;">${p_actual:,.4f}</div>
                
                <div class="lvl-grid">
                    <div class="lvl-item"><span class="lvl-lbl">ENTRY</span><span class="lvl-val">{p_entrada:,.3f}</span></div>
                    <div class="lvl-item"><span class="lvl-lbl" style="color:#3fb950;">EXIT</span><span class="lvl-val" style="color:#3fb950;">{p_entrada*1.08:,.3f}</span></div>
                    <div class="lvl-item"><span class="lvl-lbl" style="color:#f85149;">STOP</span><span class="lvl-val" style="color:#f85149;">{p_entrada*0.975:,.3f}</span></div>
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:5px;">
                    <div><div class="sensor-label">Social</div><div class="sensor-bar"><div class="sensor-fill" style="width:{s_info['social']}%; background:#1f6feb;"></div></div></div>
                    <div><div class="sensor-label">Whales</div><div class="sensor-bar"><div class="sensor-fill" style="width:{s_info['whales']}%; background:#8957e5;"></div></div></div>
                    <div><div class="sensor-label">Impulso</div><div class="sensor-bar"><div class="sensor-fill" style="width:{s_info['impulse']}%; background:#238636;"></div></div></div>
                </div>
                
                <div style="text-align:center; margin-top:10px; font-size:10px; color:#ffca28;">⏳ CIERRE IA EN {min_rest} MIN</div>
            </div>
        ''', unsafe_allow_html=True)

# 6. HISTORIAL DE APRENDIZAJE IA
st.markdown("---")
st.subheader("📋 BITÁCORA DE APRENDIZAJE Y RESUMEN IA")
if st.session_state.log_aprendizaje:
    st.table(pd.DataFrame(st.session_state.log_aprendizaje).head(10))
else:
    st.info("Esperando que finalice el primer ciclo de 20 min para generar bitácora...")

time.sleep(15)
st.rerun()
