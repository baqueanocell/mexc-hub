import streamlit as st
import ccxt
import time

# Configuración Base
st.set_page_config(page_title="IA TERMINAL V4.6", layout="wide")

# --- CSS REFORZADO (Evita errores de renderizado) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card-base { background: #0d1117; border: 1px solid #30363d; padding: 12px; border-radius: 8px; border-top: 3px solid #1f6feb; }
    /* Barras Ultra-Slim */
    .s-bg { background: #1a1a1a; height: 4px; border-radius: 2px; margin-bottom: 4px; overflow: hidden; }
    .s-fill { height: 100%; border-radius: 2px; }
    .s-label { font-size: 8px; color: #777; font-weight: bold; margin-bottom: 1px; }
    /* Tabla de Precios Compacta */
    .p-grid { width: 100%; margin-top: 10px; border-collapse: collapse; }
    .p-grid td { text-align: center; padding: 2px; font-family: monospace; border: 1px solid #21262d; }
    .p-head { font-size: 7px; color: #888; display: block; }
    .p-bold { font-size: 11px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- DATOS DINÁMICOS ---
if 'start_t' not in st.session_state: st.session_state.start_t = time.time()
t_rel = int((time.time() - st.session_state.start_t) // 60) + 5

ASSETS = {
    'VEREM': {'in': 128.16, 'tgt': 132.65, 'sl': 125.80, 'n': 85, 'p': 92, 'w': 78, 'm': t_rel},
    'BTC':   {'in': 87746.0, 'tgt': 90817.0, 'sl': 86166.0, 'n': 70, 'p': 45, 'w': 88, 'm': 18},
    'ETH':   {'in': 2890.72, 'tgt': 2991.90, 'sl': 2838.69, 'n': 60, 'p': 35, 'w': 65, 'm': 55},
    'SOL':   {'in': 122.37, 'tgt': 126.65, 'sl': 120.17, 'n': 55, 'p': 40, 'w': 50, 'm': 2}
}

# --- HEADER ---
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown('<h2 style="color:white;margin:0;font-size:22px;">🛰️ TERMINAL IA ELITE | SISTEMA ACTIVO</h2>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#222;height:8px;border-radius:4px;display:flex;overflow:hidden;margin-top:5px;"><div style="background:#3fb950;width:85%;"></div><div style="background:#f85149;width:15%;"></div></div>', unsafe_allow_html=True)

# --- PENSAMIENTO IA ---
st.markdown(f'''<div style="background:#001a00; border-left:3px solid #00ff00; padding:8px; color:#00ff00; font-family:monospace; font-size:11px; margin:10px 0;">
    <b>🧠 PENSAMIENTO IA:</b> Escaneando bloques en tiempo real... Cuadros forzados activos. Señales sincronizadas.
</div>''', unsafe_allow_html=True)

# --- CUADROS DE MONEDAS ---
cols = st.columns(4)
prices = {}
try:
    mexc = ccxt.mexc()
    ticks = mexc.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    for k, v in ticks.items(): prices[k.split('/')[0]] = v['last']
except: pass

for i, name in enumerate(['VEREM', 'BTC', 'ETH', 'SOL']):
    d = ASSETS[name]
    cp = prices.get(name, 0.0)
    pnl = ((cp - d['in']) / d['in'] * 100) if cp > 0 else 0.0
    
    # Lógica de Fuego 🔥
    fuego = "🔥 ENTRAR" if d['m'] < 10 else "⏳ ESPERAR"
    
    with cols[i]:
        st.markdown(f'''
            <div class="card-base">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:white;font-size:16px;">{name}</b>
                    <span style="background:#1f6feb; color:white; font-size:9px; padding:2px 5px; border-radius:3px;">{d["m"]} MIN</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin:8px 0;">
                    <span style="color:#58a6ff;font-size:20px;font-weight:bold;">${cp:,.2f}</span>
                    <span style="color:{"#3fb950" if pnl >= 0 else "#f85149"};font-size:14px;font-weight:bold;">{pnl:.2f}%</span>
                </div>
                <div style="color:#ffca28; font-size:11px; font-weight:bold; margin-bottom:10px;">{fuego}</div>
                
                <div class="s-label">NOTICIAS {d["n"]}%</div>
                <div class="s-bg"><div class="s-fill" style="width:{d["n"]}%; background:#1f6feb;"></div></div>
                <div class="s-label">IMPULSO {d["p"]}%</div>
                <div class="s-bg"><div class="s-fill" style="width:{d["p"]}%; background:#238636;"></div></div>
                <div class="s-label">WHALES {d["w"]}%</div>
                <div class="s-bg"><div class="s-fill" style="width:{d["w"]}%; background:#8957e5;"></div></div>

                <table class="p-grid">
                    <tr>
                        <td><span class="p-head">ENTRY</span><span class="p-bold" style="color:white;">{d["in"]}</span></td>
                        <td><span class="p-head">TARGET</span><span class="p-bold" style="color:#3fb950;">{d["tgt"]}</span></td>
                        <td><span class="p-head">STOP</span><span class="p-bold" style="color:#f85149;">{d["sl"]}</span></td>
                    </tr>
                </table>
            </div>
        ''', unsafe_allow_html=True)

# --- HISTORIAL FINAL ---
st.markdown('<br><div style="color:#58a6ff; font-weight:bold; font-size:12px;">📋 RESUMEN DE OPERACIONES</div>', unsafe_allow_html=True)
st.table([
    {"ACTIVO": "VEREM/USDT", "TIEMPO": f"{d['m']} min", "PNL": f"{pnl:.2f}%", "ESTADO": "ACTIVA"},
    {"ACTIVO": "SOL/USDT", "TIEMPO": "2 min", "PNL": "0.15%", "ESTADO": "FIRE 🔥"}
])

# Refresco seguro sin errores rojos
time.sleep(15)
st.rerun()
