import streamlit as st
import time

# Variables globales simuladas
want_p = False
want_q = False
deadlock_detected = False
log = []

def log_estado(msg, log_container):
    log.append(msg)
    # Actualizar en la UI
    with log_container:
        st.write("\n".join(log))
    time.sleep(1)

def iniciar_simulacion(log_container):
    global want_p, want_q, deadlock_detected, log

    want_p = False
    want_q = False
    deadlock_detected = False
    log.clear()
    with log_container:
        st.write("")

    log_estado("🟦 P: Iniciando...", log_container)
    log_estado("🟨 Q: Iniciando...", log_container)

    # Ambos quieren entrar al mismo tiempo para forzar deadlock
    want_p = True
    log_estado("🟦 P: Quiere entrar (want_p = True)", log_container)

    want_q = True
    log_estado("🟨 Q: Quiere entrar (want_q = True)", log_container)

    start_wait = time.time()

    # Deadlock: P espera a que Q no quiera entrar y viceversa, pero ambos quieren entrar
    while True:
        log_estado("🟦 P: Esperando... (Q también quiere)", log_container)
        log_estado("🟨 Q: Esperando... (P también quiere)", log_container)
        if time.time() - start_wait > 5:  # reducir tiempo para demo
            deadlock_detected = True
            log_estado("🟥 ¡DEADLOCK detectado!", log_container)
            break

    # No se entra ni se sale de sección crítica debido al deadlock
    want_p = False
    want_q = False

st.title("🔁 Simulación de Dekker Intento 1 ")

log_container = st.empty()

if st.button("▶ Iniciar Simulación"):
    iniciar_simulacion(log_container)

# Mostrar el log actual (persistente)
if log:
    with log_container:
        st.write("\n".join(log))
