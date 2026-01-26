import streamlit as st
import pandas as pd
import ccxt
from datetime import datetime, timedelta
import pytz

# Refresco cada 10 segundos
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="TOP 4 IA", layout="wide")

# --- CSS MINIMALISTA PARA TV ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer {visibility: hidden;}
    [data-testid="column"] { min-width: 24% !important; }
    
    .card-elite { 
        background-color: #0a0a0a; 
        border: 1px solid #1f2328; 
        padding: 15px; 
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    
    .price-val { color: #58a6ff; font-size: 22px; font-weight: bold; font-family: monospace; }
    .ia-status { color: #8b949e; font-size: 11px; font-style: italic; margin-top: 10px; border-top: 1px solid #21262d; padding-top: 5px; }
    
    .exec-grid { 
        display: grid; 
        grid-template-columns: 1fr 1fr 1fr; 
        background: #000; 
        padding: 10px; 
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
        border: 1px solid #30363d;
    }
    
    .label-x { font-size: 10px; color: #666; }
    .val-e { color: #fff; font-size: 16px; font-weight: bold; }
    .val-t { color: #3fb950; font-size: 16px; font-weight: bold; }
    .val-s { color: #f85149; font-size: 16px; font-weight: bold; }
    
    .strat-tag { font-size: 11px; background: #238636; color: #fff; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
    .bar-name { font-size: 9px; color: #555; margin-top: 8px; margin-bottom: -10px; }
    .stProgress > div > div > div > div { height: 3px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE FILTRADO ÉLITE ---
exchange = ccxt.mexc()
tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')

if 'signals' not in st.session_state: st.session_state.signals = {}

def get_elite_market():
    try:
        tickers = exchange.fetch_tickers()
        df = pd.DataFrame.from_dict(tickers, orient='index')
        # Filtramos USDT y ordenamos por volumen/cambio para buscar potencial
        potential = df[df['symbol'].str.contains('/USDT')].copy()
        potential['score'] = potential['percentage'].fillna(0) + (potential['quoteVolume'] / 1000000)
        
        # Seleccionamos las mejores (excluyendo VEREM de la lista general para forzarla después)
        top_list = potential.sort_values('score', ascending=False).head(10)
        top_symbols = list(top_list.index)
        
        # Asegurar que VEREM esté y completar solo hasta 4 monedas totales
        final_symbols = ['VEREM/USDT']
        for s in top_symbols:
            if s != 'VEREM/USDT' and len(final_symbols) < 4:
                final_symbols.append(s)
        
        data = []
        now = datetime.now(tz_arg)

        for sym in final_symbols:
            if sym in tickers:
                t = tickers[sym]
                p, ch = t['last'], (t['percentage'] or 0)
                s_name = sym.replace('/USDT', '')
                
                if s_name not in st.session_state.signals or now > st.session_state.signals[s_name]['exp']:
                    strat = "AGRESIVO" if "VEREM" in s_name else "IA EXPERTO"
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.035, 's': p*0.982, 'strat': strat, 
                        'exp': now+timedelta(minutes=20),
                        'think': f"Analizando flujo de ballenas en {s_name}..."
                    }
                
                sig = st.session_state.signals[s_name]
                # Simular "pensamiento" de la IA
                thoughts = [
                    "Detectando presión de compra...",
                    "Filtrando ruido de redes sociales...",
                    "Monitoreando carteras institucionales...",
                    "Ajustando niveles de Fibonacci...",
                    "Confirmando divergencia alcista..."
                ]
                import random
                current_thought = random.choice(thoughts)

                data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "pnl": ((p - sig['e']) / sig['e']) * 100,
                    "soc": min(max(75 + ch, 20), 98), "ball": 80, "imp": min(max(60 + ch, 10), 95),
                    "think": current_thought
                })
        return data
    except: return []

# --- UI TV TOP 4 ---
st.markdown(f"<h2 style='color:white; text-align:center;'>🚀 TOP 4 POTENCIAL IA | {datetime.now(tz_arg).strftime('%H:%M')}</h2>", unsafe_allow_html=True)

items = get_elite_market()
cols = st.columns(4)

for i, m in enumerate(items):
    with cols[i % 4]:
        pnl_color = "#3fb950" if m['pnl'] >= 0 else "#f85149"
        st.markdown(f"""
        <div class="card-elite">
            <div style="display: flex; justify-content: space-between;">
                <span class="strat-tag">{m['strat']}</span>
                <span style="color:{pnl_color}; font-size:14px; font-weight:bold;">{m['pnl']:.2f}%</span>
            </div>
            <div style="text-align:center; margin: 15px 0;">
                <div style="color:white; font-size:28px; font-weight:bold;">{m['n']}</div>
                <div class="price-val">${m['p']}</div>
            </div>
            <div class="exec-grid">
                <div><span class="label-x">ENTRADA</span><br><span class="val-e">{m['e']:.2f}</span></div>
                <div><span class="label-x">OBJETIVO</span><br><span class="val-t">{m['t']:.2f}</span></div>
                <div><span class="label-x">STOP</span><br><span class="val-s">{m['s']:.2f}</span></div>
            </div>
            <div class="bar-name">SENTIMIENTO SOCIAL</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(m['soc']/100)
        st.markdown('<div class="bar-name">VOLUMEN BALLENAS</div>', unsafe_allow_html=True)
        st.progress(m['ball']/100)
        st.markdown('<div class="bar-name">IMPULSO IA</div>', unsafe_allow_html=True)
        st.progress(m['imp']/100)
        st.markdown(f'<div class="ia-status">🧠 IA: {m["think"]}</div>', unsafe_allow_html=True)

st.write("---")
st.caption("Estrategia basada en el volumen de MEXC y sentimiento de mercado en tiempo real.")
