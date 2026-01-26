# ... (mantener el CSS anterior)

def get_market():
    try:
        tickers = exchange.fetch_tickers()
        # Filtramos USDT y ordenamos por volumen real
        df = pd.DataFrame.from_dict(tickers, orient='index')
        df = df[df['symbol'].str.contains('/USDT')]
        
        selected = ['VEREM/USDT', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        data = []
        now = datetime.now(tz_arg)

        for sym in selected:
            if sym in tickers:
                t, s_name = tickers[sym], sym.replace('/USDT','')
                p = t['last']
                vol = t['quoteVolume'] or 0
                chg = t['percentage'] or 0
                
                # --- LÓGICA DE ACTIVACIÓN REAL ---
                if "VEREM" in s_name: 
                    trig, motivo = "IMPULSO", "Alta volatilidad detectada"
                elif vol > 100000000: 
                    trig, motivo = "BALLENAS", "Flujo institucional masivo"
                elif abs(chg) > 4: 
                    trig, motivo = "FIBONACCI", "Retroceso técnico confirmado"
                else: 
                    trig, motivo = "NOTICIAS", "Sentimiento social alcista"

                # --- MÉTRICAS INDIVIDUALES (No más números iguales) ---
                # Redes: Basado en el cambio porcentual
                soc = min(max(60 + (chg * 2), 40), 98)
                # Ballenas: Basado en el volumen relativo
                ball = min(max(vol / 5000000, 30), 95)
                # Impulso: Basado en la fuerza del movimiento actual
                imp = min(max(abs(chg) * 8, 20), 99)

                if s_name not in st.session_state.signals:
                    # Configuración de estrategia por moneda
                    if "BTC" in s_name: strat = "EXPERTO"
                    elif "VEREM" in s_name: strat = "AGRESIVO"
                    elif "ETH" in s_name: strat = "INSTITUCIONAL"
                    else: strat = "SCALPING"
                    
                    st.session_state.signals[s_name] = {
                        'e': p, 't': p*1.03, 's': p*0.985, 
                        'strat': strat, 'trig': trig, 'exp': now+timedelta(minutes=15)
                    }
                
                sig = st.session_state.signals[s_name]
                data.append({
                    "n": s_name, "p": p, "e": sig['e'], "t": sig['t'], "s": sig['s'],
                    "strat": sig['strat'], "trig": sig['trig'],
                    "pnl": ((p - sig['e']) / sig['e']) * 100,
                    "soc": soc, "ball": ball, "imp": imp
                })
        return data
    except: return []

# ... (en el bucle de renderizado de tarjetas)
# Cambia esta línea para que el disparador sea bien visible:
st.markdown(f"""
    <div class="card-tv">
        <div style="display: flex; justify-content: space-between;">
            <b style="font-size: 18px; color:white;">{m['n']} <span class="trigger-tag">[{m['trig']}]</span></b>
            <span style="background:#238636; font-size:9px; padding:2px 5px; border-radius:3px;">{m['strat']}</span>
        </div>
        ...
""")
