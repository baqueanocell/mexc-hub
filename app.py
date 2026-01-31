# DETALLE DE OPERACIÓN DINÁMICA V67 [cite: 2026-01-27]
with col1:
    st.markdown("---")
    st.subheader("🚀 OPERACIÓN EN CURSO: SOL/USDT")
    
    # Barra de progreso visual hacia la meta
    progreso_meta = 65  # Ejemplo: estamos al 65% del Take Profit
    st.write(f"**Progreso hacia Take Profit:** {progreso_meta}%")
    st.progress(progreso_meta / 100)
    
    # Grid de detalles técnicos entretenidos
    m1, m2, m3 = st.columns(3)
    m1.metric("Volumen 24h", "1.2B", "+5.4%")
    m2.metric("Sentimiento Social", "🔥 MUY ALTO", "89%")
    m3.metric("Tiempo Restante Est.", "08:42 min", "Scalping Mode")

    # Pensamiento de la IA sobre la jugada actual
    st.success("🧠 **LEÓN ALPHA:** 'Detecto presión de compra masiva. La ballena #402 está acumulando. Mantengo la posición con el 0.5% de riesgo intacto.'")
