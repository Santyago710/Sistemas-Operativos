import threading
import time
import tkinter as tk
from tkinter import ttk

# Variables globales
want_p = False
want_q = False
deadlock_detected = False
inicio_barrera = threading.Barrier(2)
estado_p = "🟦 P: Inactivo"
estado_q = "🟨 Q: Inactivo"

# GUI: funciones de actualización
def actualizar_gui():
    ventana.after(0, lambda: label_estado_p.config(text=estado_p))
    ventana.after(0, lambda: label_estado_q.config(text=estado_q))
    if deadlock_detected:
        ventana.after(0, lambda: label_resultado.config(text="❌ DEADLOCK DETECTADO", fg="red"))

def log_gui(mensaje):
    ventana.after(0, lambda: (text_log.insert(tk.END, mensaje + "\n"), text_log.see(tk.END)))

# Procesos
def proceso_p():
    global want_p, want_q, deadlock_detected, estado_p
    estado_p = "🟦 P: Iniciando..."
    actualizar_gui()
    log_gui(estado_p)

    inicio_barrera.wait()

    want_p = True
    estado_p = "🟦 P: Quiere entrar (want_p = True)"
    actualizar_gui()
    log_gui(estado_p)

    start_wait = time.time()
    while want_q:
        estado_p = "🟦 P: Esperando... (Q también quiere)"
        actualizar_gui()
        log_gui(estado_p)
        if time.time() - start_wait > 10:
            deadlock_detected = True
            estado_p = "🟥 P: ¡DEADLOCK detectado!"
            actualizar_gui()
            log_gui(estado_p)
            return
        time.sleep(1)

    estado_p = "🟦 P: ENTRA a sección crítica"
    actualizar_gui()
    log_gui(estado_p)
    time.sleep(1)

    estado_p = "🟦 P: SALE de sección crítica"
    want_p = False
    actualizar_gui()
    log_gui(estado_p)

def proceso_q():
    global want_p, want_q, deadlock_detected, estado_q
    estado_q = "🟨 Q: Iniciando..."
    actualizar_gui()
    log_gui(estado_q)

    inicio_barrera.wait()

    want_q = True
    estado_q = "🟨 Q: Quiere entrar (want_q = True)"
    actualizar_gui()
    log_gui(estado_q)

    start_wait = time.time()
    while want_p:
        estado_q = "🟨 Q: Esperando... (P también quiere)"
        actualizar_gui()
        log_gui(estado_q)
        if time.time() - start_wait > 10:
            deadlock_detected = True
            estado_q = "🟥 Q: ¡DEADLOCK detectado!"
            actualizar_gui()
            log_gui(estado_q)
            return
        time.sleep(1)

    estado_q = "🟨 Q: ENTRA a sección crítica"
    actualizar_gui()
    log_gui(estado_q)
    time.sleep(1)

    estado_q = "🟨 Q: SALE de sección crítica"
    want_q = False
    actualizar_gui()
    log_gui(estado_q)

# Iniciar simulación
def iniciar_simulacion():
    global deadlock_detected, want_p, want_q, estado_p, estado_q
    want_p = want_q = deadlock_detected = False
    estado_p = "🟦 P: Inactivo"
    estado_q = "🟨 Q: Inactivo"
    actualizar_gui()
    label_resultado.config(text="")
    text_log.delete("1.0", tk.END)

    threading.Thread(target=proceso_p).start()
    threading.Thread(target=proceso_q).start()

# GUI principal
ventana = tk.Tk()
ventana.title("Simulación Algoritmo de Dekker - Intento 1")
ventana.geometry("700x500")

titulo = ttk.Label(ventana, text="🔁 Intento 1 - Dekker (Deadlock)", font=("Arial", 16))
titulo.pack(pady=10)

label_estado_p = ttk.Label(ventana, text="🟦 P: Inactivo", font=("Arial", 12))
label_estado_p.pack(pady=5)

label_estado_q = ttk.Label(ventana, text="🟨 Q: Inactivo", font=("Arial", 12))
label_estado_q.pack(pady=5)

label_resultado = ttk.Label(ventana, text="", font=("Arial", 14))
label_resultado.pack(pady=10)

boton_inicio = ttk.Button(ventana, text="▶ Iniciar Simulación", command=iniciar_simulacion)
boton_inicio.pack(pady=10)

# Consola visual
frame_log = ttk.Frame(ventana)
frame_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

text_log = tk.Text(frame_log, height=10, font=("Courier", 10))
text_log.pack(fill=tk.BOTH, expand=True)

ventana.mainloop()
