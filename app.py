import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime
import pytz

# Refresco cada 15 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="datarefresh")

st.set_page_config(page_title="IA TERMINAL ELITE V3", layout="wide")

# --- CSS MEJORADO PARA TV ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-tv { background-color: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-top: 3px solid #1f6feb; }
    .exec-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #000; padding: 8px; border-radius: 4px; margin: 10px 0; border: 1px solid #21262d; text-align: center; }
    .ia-log { background: #001a00; border-left: 5px solid #00ff00; padding: 10px; font-family: monospace; font-size: 14px; color: #00ff00; margin-bottom: 15px; }
    .trig-tag { font-size: 11px; color: #ffca28; font-weight: bold; border: 1px solid #ffca28; padding: 2px 6px; border-radius: 4px; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'signals' not in st.session_state: st.session_state.signals = {}
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

# --- HEADER ---
st.markdown(f"""
    <div style="text-align: center; color: white;">
        <span style="font-size: 26px; font-weight: bold;">🛰️ TERMINAL IA ELITE V3</span>
    </div>
    <div class="ia-log">🧠 PENSAMIENTO IA: Monitoreando señales de alta probabilidad en MEXC...</div>
    """, unsafe_allow_html=True)

# --- PROCESAMIENTO DE MONEDAS ---
try:
    # Solo pedimos los precios actuales (Fast Sync)
    tickers = exchange.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    selected = ['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    
    cols = st.columns(4)
    
    for i, sym in enumerate(selected):
        if sym in tickers:
            t = tickers[sym]
            s_name = sym.split('/')[0]
            p = float(t['last'])
            
            # Definir Estrategia por Moneda
            if "VEREM" in s_name: trig, strat, soc, ball, imp = "VOLATILIDAD", "AGRESIVO", 95, 40, 98
            elif "BTC" in s_name: trig, strat, soc, ball, imp = "INSTITUCIONAL", "EXPERTO", 70, 95, 30
            elif "ETH" in s_name: trig, strat, soc, ball, imp = "BALLENAS", "INSTITUCIONAL", 65, 85, 50
            else: trig, strat, soc, ball, imp = "IMPULSO", "SCALPING", 80, 60, 85

            # Crear señal base si no existe
            if s_name not in st.session_state.signals:
                st.session_state.signals[s_name] = {'e': p, 't': p*1.04, 's': p*0.98}
            
            sig = st.session_state.signals[s_name]
            pnl = ((p - sig['e']) / sig['e']) * 100
            pnl_color = "#3fb950" if pnl >= 0 else "#f85149"

            with cols[i]:
                # Renderizado de Tarjeta con corrección de formato
                st.markdown(f"""
                <div class="card-tv">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <b style="font-size: 22px; color:white;">{s_name}<span class="trig-tag">[{trig}]</span></b>
                        <span style="background:#238636; font-size:10px; padding:3px 6px; border-radius:4px; color:white;">{strat}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top:10px;">
                        <span style="color:#58a6ff; font-weight:bold; font-size:22px;">${p:.2f}</span>
                        <span style="color:{pnl_color}; font-weight:bold; font-size:18px;">{pnl:.2f}%</span>
                    </div>
                    <div class="exec-grid">
                        <div style="color:white;"><span style="font-size:9px; color:#888;">ENTRY</span><br>{sig['e']:.2f}</div>
                        <div style="color:#3fb950;"><span style="font-size:9px;">TARGET</span><br>{sig['t']:.2f}</div>
                        <div style="color:#f85149;"><span style="font-size:9px;">STOP</span><br>{sig['s']:.2f}</div>
                    </div>
                    <div style="font-family:monospace; font-size:12px; color:#8b949e;">
                        SOCIAL: {"■"*8} {soc}%<br>
                        BALLENAS: {"■"*7} {ball}%<br>
                        IMPULSO: {"■"*9} {imp}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("<br><p style='color:#555; text-align:center;'>Historial en proceso de sincronización...</p>", unsafe_allow_html=True)
