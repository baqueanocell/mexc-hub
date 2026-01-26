import streamlit as st
import ccxt

# 1. Configuración de Página (Sin cambios)
st.set_page_config(page_title="IA TERMINAL V3.6", layout="wide")

# 2. CSS Blindado (Más simple = Menos errores)
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    .card { background: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 12px; border-top: 4px solid #1f6feb; }
    .t-tag { color: #ffca28; font-size: 11px; font-weight: bold; border: 1px solid #ffca28; padding: 1px 4px; border-radius: 3px; }
    .s-tag { background: #238636; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; float: right; }
    .p-bar { background: #222; height: 18px; border-radius: 9px; display: flex; overflow: hidden; margin: 10px 0; border: 1px solid #444; }
    </style>
""", unsafe_allow_html=True)

# 3. Datos de Respaldo Estáticos (Para evitar el KeyError)
ASSETS = {
    'VEREM': {'t': 'IMPULSO', 's': 'AGRESIVO', 'in': 128.16, 'tgt': 132.65, 'sl': 125.80},
    'BTC': {'t': 'WHALES', 's': 'IA EXPERTO', 'in': 87746.0, 'tgt': 90817.0, 'sl': 86166.0},
    'ETH': {'t': 'INSTITUCIONAL', 's': 'MODO PRO', 'in': 2890.72, 'tgt': 2991.90, 'sl': 2838.69},
    'SOL': {'t': 'FIBONACCI', 's': 'SCALPING', 'in': 122.37, 'tgt': 126.65, 'sl': 120.17}
}

# 4. Header Fijo
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown('<h2 style="color:white;text-align:center;margin:0;">🛰️ IA TERMINAL ELITE | ACTIVA</h2>', unsafe_allow_html=True)
    st.markdown('<div class="p-bar"><div style="background:#3fb950;width:50%"></div><div style="background:#f85149;width:50%"></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div style="background:white;padding:5px;border-radius:8px;text-align:center;"><img src="https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=REPORTE" width="80"></div>', unsafe_allow_html=True)

# 5. Conexión Ultra-Rápida
prices = {}
try:
    mexc = ccxt.mexc({'timeout': 5000})
    ticks = mexc.fetch_tickers(['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT'])
    for k, v in ticks.items():
        prices[k.split('/')[0]] = v['last']
except:
    pass

# 6. Dibujo de Cuadros (Sin usar f-strings dentro de HTML para máxima seguridad)
cols = st.columns(4)
for i, name in enumerate(['VEREM', 'BTC', 'ETH', 'SOL']):
    data = ASSETS[name]
    curr_p = prices.get(name, 0.0)
    pnl = ((curr_p - data['in']) / data['in'] * 100) if curr_p > 0 else 0.0
    pnl_c = "#3fb950" if pnl >= 0 else "#f85149"
    
    with cols[i]:
        # Título y Estrategia
        st.markdown(f'<div class="card"><div><span class="s-tag">{data["s"]}</span><b style="color:white;font-size:20px;">{name} <span class="t-tag">[{data["t"]}]</span></b></div>', unsafe_allow_html=True)
        
        # Precio y PNL
        st.markdown(f'<div style="display:flex;justify-content:space-between;margin:15px 0;"><span style="color:#58a6ff;font-size:22px;font-weight:bold;">${curr_p:,.2f}</span><span style="color:{pnl_c};font-size:18px;font-weight:bold;">{pnl:.2f}%</span></div>', unsafe_allow_html=True)
        
        # Grilla de ejecución
        st.markdown(f'''
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;background:#000;padding:8px;border-radius:6px;text-align:center;border:1px solid #21262d;">
                <div style="color:white;font-size:10px;"><span style="color:#888;font-size:8px;">IN</span><br>{data["in"]}</div>
                <div style="color:#3fb950;font-size:10px;"><span style="color:#888;font-size:8px;">TGT</span><br>{data["tgt"]}</div>
                <div style="color:#f85149;font-size:10px;"><span style="color:#888;font-size:8px;">STOP</span><br>{data["sl"]}</div>
            </div></div>
        ''', unsafe_allow_html=True)

# 7. Refresco
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15000, key="boot")
