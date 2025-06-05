import threading
import time
import sys

# Variables globales
want_p = False
want_q = False
deadlock_detected = False

# Barrera de sincronización para forzar simultaneidad
inicio_barrera = threading.Barrier(2)

# Función para imprimir con retardo
def imprimir(msg):
    print(msg)
    time.sleep(1)

def proceso_p():
    global want_p, want_q, deadlock_detected
    imprimir("🟦 P: Iniciando proceso P")
    
    inicio_barrera.wait()  # Sincroniza el inicio con Q
    
    want_p = True
    imprimir("🟦 P: Marcó want_p = True (quiere entrar a sección crítica)")

    start_wait = time.time()
    while want_q:
        imprimir("🟦 P: Esperando... (Q también quiere entrar)")
        if time.time() - start_wait > 10:
            deadlock_detected = True
            imprimir("🟥 P: ¡DEADLOCK detectado después de 10 segundos!")
            return
        time.sleep(1)
    
    imprimir("🟦 P: ENTRA a sección crítica (NO debería suceder)")
    time.sleep(1)
    imprimir("🟦 P: SALE de sección crítica")
    want_p = False

def proceso_q():
    global want_p, want_q, deadlock_detected
    imprimir("🟨 Q: Iniciando proceso Q")
    
    inicio_barrera.wait()  # Sincroniza el inicio con P

    want_q = True
    imprimir("🟨 Q: Marcó want_q = True (quiere entrar a sección crítica)")

    start_wait = time.time()
    while want_p:
        imprimir("🟨 Q: Esperando... (P también quiere entrar)")
        if time.time() - start_wait > 10:
            deadlock_detected = True
            imprimir("🟥 Q: ¡DEADLOCK detectado después de 10 segundos!")
            return
        time.sleep(1)
    
    imprimir("🟨 Q: ENTRA a sección crítica (NO debería suceder)")
    time.sleep(1)
    imprimir("🟨 Q: SALE de sección crítica")
    want_q = False

def monitor_deadlock():
    global deadlock_detected
    time.sleep(10.5)  # Margen adicional al timeout
    

# Configurar hilos
thread_p = threading.Thread(target=proceso_p)
thread_q = threading.Thread(target=proceso_q)
monitor_thread = threading.Thread(target=monitor_deadlock, daemon=True)

# Iniciar simulación
print("\n" + "="*70)
print("🔁 SIMULACIÓN: INTENTO 1 DEL ALGORITMO DE DEKKER")
print("🛑 OBJETIVO: Mostrar bloqueo mutuo (deadlock)")
print("="*70 + "\n")
time.sleep(1)

monitor_thread.start()
thread_p.start()
thread_q.start()

# Esperar a que terminen
thread_p.join(timeout=12)
thread_q.join(timeout=12)

# Resultado final
if deadlock_detected:
    print("\n" + "="*70)
    imprimir("❌ RESULTADO: DEADLOCK CONFIRMADO")
    imprimir("Ambos procesos marcaron que querían entrar")
    imprimir("y quedaron esperando mutuamente por 10 segundos.")
    imprimir("Esto demuestra que el intento 1 de Dekker")
    imprimir("NO garantiza exclusión mutua ni evita bloqueo.")
    print("="*70)
    sys.exit(0)
