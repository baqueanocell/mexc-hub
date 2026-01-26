import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="MEXC Inteligencia IA", layout="wide")

# --- CSS PROFESIONAL (BARRAS MICRO + NÚMEROS GRANDES) ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    [data-testid="column"] { width: 49% !important; flex: 1 1 49% !important; min-width: 49% !important; }
    div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; }
    
    /* Barras casi invisibles (Micro) */
    .stProgress > div > div > div > div { height: 2px !important; }
    
    /* Precios y PNL Grandes */
    .price-big { color: #58a6ff; font-size: 16px !important; font-weight: 800; font-family: 'Courier New', monospace; }
    .pnl-big { font-size: 14px !important; font-weight: bold; }
    .label-micro { font-size: 7px !important; color: #8b949e; margin-bottom: -18px; }
    .card-pro { background-color: #161b22; border-left: 3px solid #00ffcc; padding: 6px; margin-bottom: 4px; border-radius: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE IA Y EXCHANGE ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

# Inicializar memoria de la IA
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'historial_real' not in st.session_state: st.session_state.historial_real = []
if 'ia_mode' not in st.session_state: st.session_state.ia_mode = "Agresivo"

def get_data():
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

                # Lógica de Re-Cálculo de Señal (Cada 20 min)
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['expires']:
                    # APRENDIZAJE: Si hay muchas pérdidas, ensanchar el Stop Loss
                    risk_adj = 0.98 if st.session_state.ia_mode == "Defensivo" else 0.99
                    
                    # Cerrar señal anterior y guardar en historial
                    if s_name in st.session_state.signals:
                        old_sig = st.session_state.signals[s_name]
                        final_pnl = ((p - old_sig['entry']) / old_sig['entry']) * 100
                        st.session_state.historial_real.insert(0, {
                            "Hora": now.strftime("%H:%M"), "Moneda": s_name, "PNL": f"{final_pnl:.2f}%"
                        })
                        # Limitar a las últimas 10
                        st.session_state.historial_real = st.session_state.historial_real[:10]

                    st.session_state.signals[s_name] = {
                        'entry': p, 'tp': p * 1.02, 'sl': p * risk_adj,
                        'expires': now + timedelta(minutes=20), 'active': True
                    }
                
                sig = st.session_state.signals[s_name]
                pnl = ((p - sig['entry']) / sig['entry']) * 100

                current_data.append({
                    "n": s_name, "p": p, "entry": sig['entry'], "tp": sig['tp'], "sl": sig['sl'],
                    "pnl": pnl, "soc": min(max(80 + (ch * 1.5), 30), 98),
                    "ball": 75 if ch > 0 else 40, "imp": min(max(ch + 50, 10), 95)
                })
        
        # IA ANALIZANDO RESULTADOS
        losses = sum(1 for x in st.session_state.historial_real if "-" in x['PNL'])
        st.session_state.ia_mode = "Defensivo" if losses > 3 else "Experto"
        
        return current_data
    except: return []

# --- UI ---
st.markdown(f"### 🤖 MEXC INTELIGENCIA IA <span style='font-size:12px; color:#00ffcc;'>MODO: {st.session_state.ia_mode}</span>", unsafe_allow_html=True)
data = get_data()

# RECOMENDACIÓN TOP
if data:
    best = max(data, key=lambda x: x['imp'] + x['soc'])
    st.markdown(f"""
    <div style="background: #161b22; padding: 10px; border-radius: 4px; border: 1px solid #58a6ff;">
        <span style="color:#8b949e; font-size:10px;">TOP SEÑAL ({datetime.now(tz_arg).strftime('%H:%M:%S')} ARG)</span><br>
        <b style="font-size:20px; color:white;">{best['n']}</b> <span class="price-big">${best['p']}</span>
        <div style="color:{'#3fb950' if best['pnl'] >= 0 else '#f85149'}; font-size:16px; font-weight:bold;">
            PNL ACTUAL: {best['pnl']:.2f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# GRILLA 2 COLUMNAS
cols = st.columns(2)
for idx, m in enumerate(data):
    with cols[idx % 2]:
        pnl_color = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-pro">
            <span style="font-size:14px; font-weight:bold;">{m['n']}</span> 
            <span class="price-big" style="float:right;">${m['p']}</span><br>
            <span style="font-size:11px; color:{pnl_color};">PNL: {m['pnl']:.2f}%</span>
            <div style="font-size:8px; color:#8b949e; margin-top:4px;">
                E: {m['entry']:.3f} | T: {m['tp']:.3f} | S: {m['sl']:.3f}
            </div>
            <div class="label-micro">IA SCORE</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="label-micro">BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="label-micro">IMPULSO</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)

st.write("---")

# --- HISTORIAL DE APRENDIZAJE ---
st.markdown("### 📜 ÚLTIMAS 10 OPERACIONES (MEMORIA IA)")
if st.session_state.historial_real:
    st.table(pd.DataFrame(st.session_state.historial_real))
else:
    st.info("Analizando mercado... Esperando cierre del primer ciclo de 20 min.")
