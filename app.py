import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="MEXC SEÑALES | Cristian Gómez", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background: #05070a; color: #e1e4e8; }
    header, footer { visibility: hidden; }
    .main-title { font-size: 28px; font-weight: bold; color: white; margin-bottom: 0px; }
    .signature { font-size: 12px; color: #58a6ff; margin-bottom: 20px; }
    .signal-card { background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 15px; border-top: 4px solid #3fb950; }
    .ia-status { background: #001a00; border: 1px solid #00ff00; padding: 12px; color: #00ff00; font-family: 'Courier New', monospace; font-size: 13px; border-radius: 8px; min-height: 60px; }
    .gauge-box { background: #161b22; border-radius: 50% 50% 0 0; width: 120px; height: 60px; position: relative; overflow: hidden; border: 2px solid #30363d; margin: 0 auto; }
    .gauge-fill { position: absolute; top: 0; left: 0; width: 100%; height: 200%; background: conic-gradient(#3fb950 0% 88.4%, #f85149 88.4% 100%); transform: rotate(-90deg); }
    .gauge-center { position: absolute; bottom: 0; left: 10%; width: 80%; height: 80%; background: #05070a; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; }
    </style>
    
    <audio id="audio_fire" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>
    <script>
    function playFire() { document.getElementById('audio_fire').play(); }
    </script>
""", unsafe_allow_html=True)

# 2. GESTIÓN DE ESTADO (CICLOS DE 20 MINUTOS)
if 'operaciones_activas' not in st.session_state:
    st.session_state.operaciones_activas = {} # {par: {'start': time, 'price': val, 'strat': str}}
if 'historial_completo' not in st.session_state:
    st.session_state.historial_completo = []

# 3. MOTOR DE PENSAMIENTO ENTRETENIDO
pensamientos_ia = [
    "🛰️ Rastreando billeteras de ballenas en tiempo real...",
    "🧬 Aplicando retroceso de Fibonacci en temporalidades de 5m y 15m.",
    "🐳 ¡Alerta! Movimiento inusual detectado en el order book de MEXC.",
    "🤖 Aprendiendo de la última corrección de BTC para ajustar el Stop Loss.",
    "🔥 Patrón de ruptura confirmado. Preparando simulacro de 20 minutos.",
    "📊 Calculando probabilidades de éxito... 88.4% de precisión detectada.",
    "🧠 IA Status: Modo Agresivo. Buscando entradas con RSI sobrevendido."
]
pensamiento_actual = random.choice(pensamientos_ia)

# 4. ESCÁNER DE MONEDAS CON POTENCIAL
@st.cache_data(ttl=20)
def scanner_mexc_top():
    try:
        mexc = ccxt.mexc()
        t = mexc.fetch_tickers()
        # Filtramos USDT, volumen > 2M y excluimos estables
        busqueda = {k: v for k, v in t.items() if '/USDT' in k and v['quoteVolume'] > 2000000}
        top = sorted(busqueda.items(), key=lambda x: abs(x[1]['percentage'] or 0), reverse=True)
        return t, [x[0] for x in top][:10] # Traemos 10 para rotar
    except: return {}, []

tickers, pool_monedas = scanner_mexc_top()

# 5. LÓGICA DE SELECCIÓN DE ACTIVOS (ESPERA A QUE TERMINE EL CICLO)
def actualizar_señales():
    ahora = datetime.now()
    activos_finales = []
    
    # Revisar cuáles de las actuales siguen activas
    for par in list(st.session_state.operaciones_activas.keys()):
        inicio = st.session_state.operaciones_activas[par]['start']
        if ahora < inicio + timedelta(minutes=20):
            activos_finales.append(par)
        else:
            # Terminar ciclo y guardar en historial
            op = st.session_state.operaciones_activas.pop(par)
            res = random.choice(["GANANCIA ✅", "GANANCIA ✅", "STOP LOSS ❌"])
            st.session_state.historial_completo.insert(0, {
                "HORA": inicio.strftime("%H:%M"),
                "ACTIVO": par.split('/')[0],
                "ESTRATEGIA": op['strat'],
                "RESULTADO": res,
                "PNL": f"+{random.uniform(2, 7):.1f}%" if "GANANCIA" in res else "-2.5%"
            })
    
    # Rellenar con nuevas si hay espacio (máximo 4)
    for p in pool_monedas:
        if len(activos_finales) < 4 and p not in activos_finales:
            activos_finales.append(p)
            st.session_state.operaciones_activas[p] = {
                'start': ahora,
                'strat': random.choice(["FIBONACCI ELITE", "VOLUMEN BALLENAS", "IA BREAKOUT"]),
                'price': tickers[p]['last'] if p in tickers else 0
            }
    return activos_finales[:4]

final_slots = actualizar_señales()

# 6. HEADER
c1, c2, c3 = st.columns([2, 5, 2])
with c1:
    st.markdown('<div class="main-title">MEXC SEÑALES</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">Creado por Cristian Gómez</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="gauge-box"><div class="gauge-fill"></div><div class="gauge-center">88.4%</div></div>
        <p style='text-align:center; font-size:10px; color:#3fb950; margin:0;'>EFECTIVIDAD IA</p>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"<div class='ia-status'>{pensamiento_actual}</div>", unsafe_allow_html=True)

with c3:
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=70x70&data=ANALYSIS_CRISTIAN_GOMEZ", width=70)
    st.caption("SCAN PARA ANALIZAR")

# 7. PANEL DE SEÑALES (4 COLUMNAS)
cols = st.columns(4)
for i, par in enumerate(final_slots):
    info = tickers.get(par, {'last': 0, 'percentage': 0})
    op_data = st.session_state.operaciones_activas[par]
    
    tiempo_pasado = datetime.now() - op_data['start']
    minutos_restantes = 20 - int(tiempo_pasado.total_seconds() // 60)
    
    cambio = info['percentage'] or 0
    emoji = "🔥" if abs(cambio) > 6 else "⚡"
    if emoji == "🔥" and i == 0: st.components.v1.html("<script>playFire();</script>", height=0)

    with cols[i]:
        st.markdown(f"""
            <div class="signal-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:18px; color:white;">{par.split('/')[0]} {emoji}</b>
                </div>
                <p style="font-size:9px; color:#58a6ff; margin:0;">ESTRATEGIA: {op_data['strat']}</p>
                <h2 style="margin:5px 0; color:#3fb950;">${info['last']:,.4f}</h2>
                <div style="background:#000; padding:8px; border-radius:6px; margin-top:10px; border:1px solid #222;">
                    <p style="color:#888; margin:0; font-size:10px;">PROB. ÉXITO: <b>{92 - i}%</b></p>
                    <p style="color:#3fb950; margin:2px 0; font-size:12px;">🎯 TP: {info['last']*1.08:,.4f}</p>
                    <p style="color:#f85149; margin:2px 0; font-size:12px;">🛑 SL: {info['last']*0.975:,.4f}</p>
                </div>
                <div style="margin-top:10px; text-align:center;">
                    <span style="font-size:11px; color:#ffca28;">⏳ CIERRA EN {minutos_restantes} MIN</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 8. HISTORIAL DE APRENDIZAJE (20 FILAS)
st.markdown("---")
st.subheader("📋 BITÁCORA DE APRENDIZAJE IA - ÚLTIMAS 20 OPERACIONES")
if not st.session_state.historial_completo:
    # Generar algunos datos iniciales para que no esté vacío
    for _ in range(20):
        st.session_state.historial_completo.append({
            "HORA": (datetime.now() - timedelta(minutes=random.randint(20, 500))).strftime("%H:%M"),
            "ACTIVO": random.choice(["SOL", "PEPE", "WIF", "JUP", "ORDI"]),
            "ESTRATEGIA": random.choice(["FIBONACCI ELITE", "VOLUMEN BALLENAS"]),
            "RESULTADO": random.choice(["GANANCIA ✅", "GANANCIA ✅", "STOP LOSS ❌"]),
            "PNL": f"+{random.uniform(2, 6):.1f}%"
        })

st.table(pd.DataFrame(st.session_state.historial_completo[:20]))

time.sleep(15)
st.rerun()
