import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Proceso:
    # Paleta de colores contrastantes con el rojo (para bloqueos)
    COLORES_PROCESOS = [
        '#1f77b4',  # Azul
        '#2ca02c',  # Verde
        '#9467bd',  # Violeta
        '#8c564b',  # Marrón
        '#e377c2',  # Rosa
        '#7f7f7f',  # Gris
        '#bcbd22',  # Verde oliva
        '#17becf',  # Cyan
        '#ff7f0e',  # Naranja
        '#d62728'   # Rojo (no lo usaremos para procesos normales)
    ]
    
    def __init__(self, nombre, tiempo_llegada, rafaga):
        self.nombre = nombre
        self.tiempo_llegada = tiempo_llegada
        self.rafaga_total = rafaga
        self.rafaga_restante = rafaga
        self.tiempo_comienzo = -1
        self.tiempo_final = -1
        self.tiempo_espera = 0
        self.rafaga_ejecucion = 0
        self.bloqueado = False
        self.tiempo_bloqueado = 0
        self.tiempo_en_bloqueado = 0
        self.color = self.asignar_color(nombre)
    
    def asignar_color(self, nombre):
        # Asignar colores de la paleta de forma consistente
        hash_val = hash(nombre)
        return self.COLORES_PROCESOS[hash_val % len(self.COLORES_PROCESOS)]

class RoundRobinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Round Robin")
        self.root.geometry("1200x800")
        
        self.quantum = tk.IntVar(value=3)
        self.tiempo_bloqueo = tk.IntVar(value=2)
        self.procesos = []
        self.proceso_actual = None
        self.tiempo_actual = 0
        self.ejecutando = False
        self.pausado = False
        self.cola_listos = deque()
        self.cola_bloqueados = deque()
        self.historial = []
        self.gantt_data = []
        
        self.setup_ui()
        
    def setup_ui(self):
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(fill=tk.X)
        
        tk.Label(control_frame, text="Quantum:").grid(row=0, column=0, padx=5)
        tk.Entry(control_frame, textvariable=self.quantum, width=5).grid(row=0, column=1, padx=5)
        
        tk.Label(control_frame, text="Tiempo Bloqueo:").grid(row=0, column=2, padx=5)
        tk.Entry(control_frame, textvariable=self.tiempo_bloqueo, width=5).grid(row=0, column=3, padx=5)
        
        tk.Button(control_frame, text="Agregar Proceso", command=self.agregar_proceso).grid(row=0, column=4, padx=5)
        tk.Button(control_frame, text="Iniciar", command=self.iniciar_simulacion).grid(row=0, column=5, padx=5)
        tk.Button(control_frame, text="Pausar/Continuar", command=self.pausar_continuar).grid(row=0, column=6, padx=5)
        tk.Button(control_frame, text="Reiniciar", command=self.reiniciar).grid(row=0, column=7, padx=5)
        tk.Button(control_frame, text="Bloquear Actual", command=self.bloquear_actual).grid(row=0, column=8, padx=5)
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tabla_frame = tk.Frame(main_frame)
        tabla_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tabla_frame, columns=("PROCESO", "T.LLEGADA", "RAFAGA TOTAL", "T.COMIENZO", 
                                                      "T.FINAL", "T.ESPERA", "RAFAGA EJECUCION", "ESTADO", "COLOR"), 
                                show="headings")
        
        columnas = [
            ("PROCESO", 80),
            ("T.LLEGADA", 80),
            ("RAFAGA TOTAL", 100),
            ("T.COMIENZO", 100),
            ("T.FINAL", 80),
            ("T.ESPERA", 80),
            ("RAFAGA EJECUCION", 120),
            ("ESTADO", 100),
            ("COLOR", 70)
        ]
        
        for col, width in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        gantt_frame = tk.Frame(main_frame)
        gantt_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(10, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=gantt_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        colas_frame = tk.Frame(self.root)
        colas_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ready_frame = tk.Frame(colas_frame)
        ready_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(ready_frame, text="Cola de Listos", font=('Arial', 10, 'bold')).pack()
        self.ready_queue_label = tk.Label(ready_frame, text="[]", relief=tk.SUNKEN, width=30, height=2)
        self.ready_queue_label.pack(pady=5)
        
        blocked_frame = tk.Frame(colas_frame)
        blocked_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(blocked_frame, text="Cola de Bloqueados", font=('Arial', 10, 'bold')).pack()
        self.blocked_queue_label = tk.Label(blocked_frame, text="[]", relief=tk.SUNKEN, width=30, height=2)
        self.blocked_queue_label.pack(pady=5)
        
        current_frame = tk.Frame(colas_frame)
        current_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(current_frame, text="Proceso Actual", font=('Arial', 10, 'bold')).pack()
        self.current_process_label = tk.Label(current_frame, text="Ninguno", relief=tk.SUNKEN, width=20, height=2)
        self.current_process_label.pack(pady=5)
        
        time_frame = tk.Frame(colas_frame)
        time_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(time_frame, text="Tiempo Actual", font=('Arial', 10, 'bold')).pack()
        self.time_label = tk.Label(time_frame, text="0", relief=tk.SUNKEN, width=10, height=2)
        self.time_label.pack(pady=5)
    
    def agregar_proceso(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Proceso")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text="Nombre del proceso:").pack(pady=5)
        nombre_entry = tk.Entry(dialog)
        nombre_entry.pack(pady=5)
        
        tk.Label(dialog, text="Tiempo de llegada:").pack(pady=5)
        llegada_entry = tk.Entry(dialog)
        llegada_entry.pack(pady=5)
        
        tk.Label(dialog, text="Ráfaga total:").pack(pady=5)
        rafaga_entry = tk.Entry(dialog)
        rafaga_entry.pack(pady=5)
        
        def guardar_proceso():
            try:
                nombre = nombre_entry.get()
                llegada = int(llegada_entry.get())
                rafaga = int(rafaga_entry.get())
                
                if nombre and llegada >= 0 and rafaga > 0:
                    proceso = Proceso(nombre, llegada, rafaga)
                    self.procesos.append(proceso)
                    self.actualizar_tabla()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Datos inválidos")
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        
        tk.Button(dialog, text="Agregar", command=guardar_proceso).pack(pady=10)
    
    def actualizar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        procesos_ordenados = sorted(self.procesos, key=lambda p: p.tiempo_llegada)
        
        for proceso in procesos_ordenados:
            estado = "Bloqueado" if proceso.bloqueado else "Listo" if proceso.rafaga_restante > 0 else "Terminado"
            self.tree.insert("", "end", values=(
                proceso.nombre,
                proceso.tiempo_llegada,
                proceso.rafaga_total,
                proceso.tiempo_comienzo if proceso.tiempo_comienzo != -1 else "-",
                proceso.tiempo_final if proceso.tiempo_final != -1 else "-",
                proceso.tiempo_espera,
                f"{proceso.rafaga_ejecucion}/{proceso.rafaga_total}",
                estado,
                proceso.color
            ))
    
    def actualizar_colas(self):
        ready_names = [p.nombre for p in self.cola_listos]
        self.ready_queue_label.config(text=str(ready_names))
        
        blocked_names = [p.nombre for p in self.cola_bloqueados]
        self.blocked_queue_label.config(text=str(blocked_names))
        
        current = self.proceso_actual.nombre if self.proceso_actual else "Ninguno"
        self.current_process_label.config(text=current)
        
        self.time_label.config(text=str(self.tiempo_actual))
    
    def actualizar_diagrama_gantt(self):
        self.ax.clear()
        
        if not self.gantt_data:
            self.ax.set_title("Diagrama de Gantt")
            self.ax.set_xlabel("Tiempo")
            self.ax.set_yticks([])
            self.canvas.draw()
            return
        
        procesos = []
        for entry in self.gantt_data:
            name = entry['proceso']
            if name.startswith('BLOQ-'):
                name = name[5:]
            if name not in procesos and name != 'IDLE':
                procesos.append(name)
        
        procesos.sort(key=lambda x: int(x[1:]) if x[0] == 'P' else x)
        if 'IDLE' in [entry['proceso'] for entry in self.gantt_data]:
            procesos.append('IDLE')
        
        y_ticks = range(len(procesos))
        y_labels = procesos
        
        for i, proceso in enumerate(procesos):
            entries = [entry for entry in self.gantt_data if 
                      (entry['proceso'] == proceso or 
                       (entry['proceso'].startswith('BLOQ-') and entry['proceso'][5:] == proceso))]
            
            for entry in entries:
                # Usar rojo oscuro para bloques de bloqueo
                color = '#d62728' if entry['proceso'].startswith('BLOQ-') else \
                       '#f7f7f7' if entry['proceso'] == 'IDLE' else \
                       next((p.color for p in self.procesos if p.nombre == entry['proceso']), '#1f77b4')
                
                self.ax.broken_barh([(entry['inicio'], entry['duracion'])], (i-0.4, 0.8), 
                                   facecolors=color, edgecolor='black', linewidth=0.5)
        
        self.ax.set_title("Diagrama de Gantt")
        self.ax.set_yticks(y_ticks)
        self.ax.set_yticklabels(y_labels)
        self.ax.set_xlabel("Tiempo")
        self.ax.grid(True)
        
        max_time = max(entry['inicio'] + entry['duracion'] for entry in self.gantt_data) if self.gantt_data else 1
        self.ax.set_xlim(0, max_time + 1)
        
        # Leyenda mejorada
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#d62728', label='Bloqueado'),
            Patch(facecolor='#808080', label='Esperando proceso')
        ]
        # Añadir colores de procesos a la leyenda
        for p in self.procesos:
            legend_elements.append(Patch(facecolor=p.color, label=f'Proceso {p.nombre}'))
        
        self.ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1))
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def iniciar_simulacion(self):
        if self.ejecutando:
            return
        
        if not self.procesos:
            messagebox.showwarning("Advertencia", "No hay procesos para ejecutar")
            return
        
        self.ejecutando = True
        self.pausado = False
        self.tiempo_actual = 0
        self.cola_listos = deque()
        self.cola_bloqueados = deque()
        self.procesos.sort(key=lambda p: p.tiempo_llegada)
        threading.Thread(target=self.simular, daemon=True).start()
    
    def pausar_continuar(self):
        if not self.ejecutando:
            return
        
        self.pausado = not self.pausado
    
    def reiniciar(self):
        self.ejecutando = False
        self.pausado = False
        self.tiempo_actual = 0
        self.proceso_actual = None
        self.cola_listos = deque()
        self.cola_bloqueados = deque()
        self.gantt_data = []
        
        for proceso in self.procesos:
            proceso.rafaga_restante = proceso.rafaga_total
            proceso.tiempo_comienzo = -1
            proceso.tiempo_final = -1
            proceso.tiempo_espera = 0
            proceso.rafaga_ejecucion = 0
            proceso.bloqueado = False
            proceso.tiempo_bloqueado = 0
            proceso.tiempo_en_bloqueado = 0
        
        self.actualizar_tabla()
        self.actualizar_colas()
        self.actualizar_diagrama_gantt()
    
    def bloquear_actual(self):
        if not self.ejecutando or self.pausado or not self.proceso_actual:
            return
        
        # Registrar el final de la ejecución actual
        if self.gantt_data and self.gantt_data[-1]['proceso'] == self.proceso_actual.nombre:
            self.gantt_data[-1]['duracion'] = self.tiempo_actual - self.gantt_data[-1]['inicio']
        
        # Bloquear el proceso
        self.proceso_actual.bloqueado = True
        self.proceso_actual.tiempo_bloqueado = self.tiempo_bloqueo.get()
        self.cola_bloqueados.append(self.proceso_actual)
        
        # Registrar el bloqueo en el diagrama de Gantt (usando rojo oscuro)
        self.gantt_data.append({
            'proceso': f"BLOQ-{self.proceso_actual.nombre}",
            'inicio': self.tiempo_actual,
            'duracion': self.tiempo_bloqueo.get()
        })
        
        self.proceso_actual = None
        self.actualizar_tabla()
        self.actualizar_colas()
    
    def simular(self):
        quantum = self.quantum.get()
        
        while self.ejecutando:
            if self.pausado:
                time.sleep(0.1)
                continue
            
            # Verificar llegada de nuevos procesos
            for proceso in self.procesos:
                if proceso.tiempo_llegada == self.tiempo_actual and proceso not in self.cola_listos and proceso not in self.cola_bloqueados and not proceso.bloqueado and proceso.rafaga_restante > 0:
                    self.cola_listos.append(proceso)
            
            # Procesar cola de bloqueados
            if self.cola_bloqueados:
                proceso_bloqueado = self.cola_bloqueados[0]
                proceso_bloqueado.tiempo_en_bloqueado += 1
                
                if proceso_bloqueado.tiempo_en_bloqueado >= proceso_bloqueado.tiempo_bloqueado:
                    proceso_bloqueado = self.cola_bloqueados.popleft()
                    proceso_bloqueado.bloqueado = False
                    proceso_bloqueado.tiempo_bloqueado = 0
                    proceso_bloqueado.tiempo_en_bloqueado = 0
                    self.cola_listos.append(proceso_bloqueado)
            
            # Tomar nuevo proceso si no hay uno actual
            if not self.proceso_actual and self.cola_listos:
                self.proceso_actual = self.cola_listos.popleft()
                if self.proceso_actual.tiempo_comienzo == -1:
                    self.proceso_actual.tiempo_comienzo = self.tiempo_actual
                
                # Registrar en Gantt
                self.gantt_data.append({
                    'proceso': self.proceso_actual.nombre,
                    'inicio': self.tiempo_actual,
                    'duracion': 0
                })
            
            # Ejecutar proceso actual
            if self.proceso_actual:
                self.proceso_actual.rafaga_restante -= 1
                self.proceso_actual.rafaga_ejecucion += 1
                self.gantt_data[-1]['duracion'] += 1
                
                # Actualizar tiempos de espera
                for proceso in self.cola_listos:
                    if proceso != self.proceso_actual:
                        proceso.tiempo_espera += 1
                
                # Verificar si terminó
                if self.proceso_actual.rafaga_restante == 0:
                    self.proceso_actual.tiempo_final = self.tiempo_actual + 1
                    self.proceso_actual = None
                # Verificar fin de quantum
                elif self.proceso_actual.rafaga_ejecucion % quantum == 0:
                    self.cola_listos.append(self.proceso_actual)
                    self.proceso_actual = None
            else:
                # Tiempo ocioso
                if self.gantt_data and self.gantt_data[-1]['proceso'] == 'IDLE':
                    self.gantt_data[-1]['duracion'] += 1
                else:
                    self.gantt_data.append({
                        'proceso': 'IDLE',
                        'inicio': self.tiempo_actual,
                        'duracion': 1
                    })
            
            self.root.after(0, self.actualizar_interfaz)
            self.tiempo_actual += 1
            
            # Verificar si todos terminaron
            todos_terminados = all(p.rafaga_restante == 0 for p in self.procesos)
            if todos_terminados and not self.cola_bloqueados:
                self.ejecutando = False
                self.root.after(0, lambda: messagebox.showinfo("Simulación completada", "Todos los procesos han terminado"))
                break
            
            time.sleep(0.5)
    
    def actualizar_interfaz(self):
        self.actualizar_tabla()
        self.actualizar_colas()
        self.actualizar_diagrama_gantt()

if __name__ == "__main__":
    root = tk.Tk()
    app = RoundRobinApp(root)
    root.mainloop()