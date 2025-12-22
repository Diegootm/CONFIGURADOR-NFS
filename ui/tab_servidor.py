"""
Pestaña del Servidor NFS
Módulo independiente para configuración del servidor
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from .temas import (
    TemaColores, crear_boton, crear_listbox_personalizado,
    crear_frame_card, Iconos
)
from utils.logger import logger


class TabServidor:
    """
    Pestaña para configuración del servidor NFS
    """
    
    def __init__(self, parent, gestor_nfs, actualizar_barra_estado):
        self.parent = parent
        self.gestor_nfs = gestor_nfs
        self.actualizar_barra_estado = actualizar_barra_estado
        
        # Variables de opciones NFS
        self.opciones_vars = {}
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Cargar exportaciones iniciales
        self._actualizar_exportaciones()
        
        logger.info("TabServidor inicializado")
    
    def _crear_interfaz(self):
        """
        Crea la interfaz de la pestaña del servidor
        """
        # Sección 1: Agregar nueva exportación
        self._crear_seccion_agregar()
        
        # Sección 2: Exportaciones actuales
        self._crear_seccion_lista()
    
    def _crear_seccion_agregar(self):
        """
        Crea la sección para agregar nuevas exportaciones
        """
        frame_agregar = crear_frame_card(
            self.parent, 
            title="1. {0} Agregar Nueva Exportación".format(Iconos.SERVIDOR)
        )
        frame_agregar.pack(fill='x', pady=(0, 10))
        
        # Ruta a exportar
        ttk.Label(frame_agregar, text="Ruta a Exportar:").grid(
            row=0, column=0, sticky='w', pady=5, padx=5
        )
        
        self.entrada_ruta_servidor = ttk.Entry(frame_agregar, width=45)
        self.entrada_ruta_servidor.grid(
            row=0, column=1, sticky='ew', pady=5, padx=5
        )
        
        crear_boton(
            frame_agregar, 
            "{0} Explorar...".format(Iconos.CARPETA),
            self._explorar_ruta_servidor, 
            tipo='info', 
            width=15
        ).grid(row=0, column=2, padx=5)
        
        # Validación en tiempo real
        self.label_validacion_ruta = ttk.Label(
            frame_agregar, 
            text="",
            foreground=TemaColores.COLOR_TEXTO_MUTED
        )
        self.label_validacion_ruta.grid(row=1, column=1, sticky='w', padx=5)
        
        self.entrada_ruta_servidor.bind('<KeyRelease>', self._validar_ruta_tiempo_real)
        
        # Hosts permitidos
        ttk.Label(frame_agregar, text="Hosts Permitidos:").grid(
            row=2, column=0, sticky='w', pady=5, padx=5
        )
        
        self.entrada_hosts_servidor = ttk.Entry(frame_agregar, width=45)
        self.entrada_hosts_servidor.grid(
            row=2, column=1, sticky='ew', pady=5, padx=5
        )
        self.entrada_hosts_servidor.insert(0, "*")
        
        # Validación de hosts
        self.label_validacion_hosts = ttk.Label(
            frame_agregar,
            text="",
            foreground=TemaColores.COLOR_TEXTO_MUTED
        )
        self.label_validacion_hosts.grid(row=3, column=1, sticky='w', padx=5)
        
        self.entrada_hosts_servidor.bind('<KeyRelease>', self._validar_hosts_tiempo_real)
        
        # Ayuda
        ttk.Label(
            frame_agregar, 
            text="Ejemplos: 192.168.1.100 | 192.168.1.0/24 | * (todos)",
            foreground=TemaColores.COLOR_TEXTO_MUTED,
            font=('Segoe UI', 8, 'italic')
        ).grid(row=4, column=1, sticky='w', padx=5, pady=(0, 10))
        
        frame_agregar.columnconfigure(1, weight=1)
        
        # Opciones NFS
        self._crear_opciones_nfs(frame_agregar)
        
        # Botones de acción
        frame_botones = tk.Frame(frame_agregar, bg=TemaColores.COLOR_FONDO_CARD)
        frame_botones.grid(row=6, column=0, columnspan=3, pady=10)
        
        crear_boton(
            frame_botones,
            "{0} Agregar Exportación".format(Iconos.EXITO),
            self._agregar_exportacion_servidor,
            tipo='success'
        ).pack(side='left', padx=5)
        
        crear_boton(
            frame_botones,
            "Limpiar Campos",
            self._limpiar_campos,
            tipo='secondary'
        ).pack(side='left', padx=5)
    
    def _crear_opciones_nfs(self, parent):
        """
        Crea el frame de opciones NFS
        """
        frame_opciones = ttk.LabelFrame(
            parent, 
            text="Opciones NFS",
            padding=10
        )
        frame_opciones.grid(row=5, column=0, columnspan=3, sticky='ew', pady=10, padx=5)
        
        # Obtener opciones con descripciones
        opciones_info = self.gestor_nfs.obtener_opciones_con_descripciones()
        
        # Opciones más comunes para mostrar
        opciones_principales = [
            ('rw', 'Lectura/Escritura'),
            ('ro', 'Solo Lectura'),
            ('sync', 'Sincronizado (recomendado)'),
            ('async', 'Asíncrono (más rápido, menos seguro)'),
            ('root_squash', 'Mapear root a anónimo (seguro)'),
            ('no_root_squash', 'Root remoto = root local'),
            ('no_subtree_check', 'Sin verificación de subdirectorios'),
            ('all_squash', 'Todos los usuarios → anónimo')
        ]
        
        # Etiqueta informativa
        ttk.Label(
            frame_opciones,
            text="Configuración recomendada: rw, sync, no_subtree_check, root_squash",
            foreground=TemaColores.COLOR_INFO,
            font=('Segoe UI', 9, 'italic')
        ).grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 10))
        
        # Crear checkboxes
        fila = 1
        columna = 0
        max_columnas = 2
        
        for opt, desc in opciones_principales:
            var = tk.BooleanVar()
            self.opciones_vars[opt] = var
            
            # Crear frame para cada opción
            frame_opcion = tk.Frame(frame_opciones, bg=TemaColores.COLOR_FONDO_CARD)
            frame_opcion.grid(row=fila, column=columna, sticky='w', padx=10, pady=3)
            
            chk = ttk.Checkbutton(
                frame_opcion,
                text="{0}".format(opt),
                variable=var
            )
            chk.pack(side='left')
            
            ttk.Label(
                frame_opcion,
                text="({0})".format(desc),
                foreground=TemaColores.COLOR_TEXTO_MUTED,
                font=('Segoe UI', 8)
            ).pack(side='left', padx=5)
            
            # Avanzar a siguiente posición
            columna += 1
            if columna >= max_columnas:
                fila += 1
                columna = 0
        
        # Valores por defecto recomendados
        self.opciones_vars['rw'].set(True)
        self.opciones_vars['sync'].set(True)
        self.opciones_vars['no_subtree_check'].set(True)
        self.opciones_vars['root_squash'].set(True)
    
    def _crear_seccion_lista(self):
        """
        Crea la sección de lista de exportaciones
        """
        frame_lista = crear_frame_card(
            self.parent,
            title="2. {0} Exportaciones Actuales".format(Iconos.CONFIG)
        )
        frame_lista.pack(fill='both', expand=True, pady=(0, 10))
        
        # Frame para listbox
        frame_listbox = tk.Frame(frame_lista, bg=TemaColores.COLOR_FONDO_CARD)
        frame_listbox.pack(fill='both', expand=True, pady=5)
        
        self.lista_exportaciones, scrollbar = crear_listbox_personalizado(
            frame_listbox, 
            height=10
        )
        self.lista_exportaciones.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botones de control
        frame_botones = tk.Frame(frame_lista, bg=TemaColores.COLOR_FONDO_CARD)
        frame_botones.pack(fill='x', pady=10)
        
        crear_boton(
            frame_botones,
            "{0} Actualizar".format(Iconos.REFRESH),
            self._actualizar_exportaciones,
            tipo='primary'
        ).pack(side='left', padx=3)
        
        crear_boton(
            frame_botones,
            "{0} Eliminar Seleccionada".format(Iconos.DELETE),
            self._eliminar_exportacion,
            tipo='danger'
        ).pack(side='left', padx=3)
        
        crear_boton(
            frame_botones,
            "{0} Aplicar Cambios NFS".format(Iconos.EXITO),
            self._aplicar_cambios_nfs,
            tipo='success'
        ).pack(side='left', padx=3)
        
        crear_boton(
            frame_botones,
            "{0} Ver Espacio en Disco".format(Iconos.INFO),
            self._ver_espacio_disco,
            tipo='info'
        ).pack(side='left', padx=3)
    
    def _validar_ruta_tiempo_real(self, event=None):
        """
        Valida la ruta en tiempo real
        """
        from utils.validaciones import validar_ruta
        
        ruta = self.entrada_ruta_servidor.get().strip()
        
        if not ruta:
            self.label_validacion_ruta.config(text="")
            return
        
        es_valida, tipo, mensaje = validar_ruta(ruta)
        
        if es_valida:
            if tipo == 'directorio':
                self.label_validacion_ruta.config(
                    text="{0} Directorio válido".format(Iconos.EXITO),
                    foreground=TemaColores.COLOR_SUCCESS
                )
            elif tipo == 'archivo':
                self.label_validacion_ruta.config(
                    text="{0} Archivo válido (se agregará fsid)".format(Iconos.EXITO),
                    foreground=TemaColores.COLOR_INFO
                )
        else:
            self.label_validacion_ruta.config(
                text="{0} {1}".format(Iconos.ERROR, mensaje),
                foreground=TemaColores.COLOR_DANGER
            )
    
    def _validar_hosts_tiempo_real(self, event=None):
        """
        Valida los hosts en tiempo real
        """
        from utils.validaciones import validar_red
        
        hosts = self.entrada_hosts_servidor.get().strip()
        
        if not hosts:
            self.label_validacion_hosts.config(text="")
            return
        
        es_valida, mensaje = validar_red(hosts)
        
        if es_valida:
            self.label_validacion_hosts.config(
                text="{0} {1}".format(Iconos.EXITO, mensaje),
                foreground=TemaColores.COLOR_SUCCESS
            )
        else:
            self.label_validacion_hosts.config(
                text="{0} {1}".format(Iconos.ERROR, mensaje),
                foreground=TemaColores.COLOR_DANGER
            )
    
    def _explorar_ruta_servidor(self):
        """
        Abre explorador para seleccionar ruta
        """
        tipo = messagebox.askquestion(
            "Seleccionar Tipo",
            "¿Desea exportar una CARPETA completa?\n\n" +
            "(Seleccione 'No' para exportar un archivo individual)\n\n" +
            "NOTA: Los archivos requieren configuración especial (fsid automático)"
        )
        
        if tipo == 'yes':
            ruta = filedialog.askdirectory(
                title="Seleccione carpeta a exportar",
                initialdir="/home"
            )
        else:
            ruta = filedialog.askopenfilename(
                title="Seleccione archivo a exportar",
                initialdir="/home"
            )
        
        if ruta:
            self.entrada_ruta_servidor.delete(0, tk.END)
            self.entrada_ruta_servidor.insert(0, ruta)
            self._validar_ruta_tiempo_real()
    
    def _agregar_exportacion_servidor(self):
        """
        Agrega una nueva exportación NFS
        """
        ruta = self.entrada_ruta_servidor.get().strip()
        hosts = self.entrada_hosts_servidor.get().strip()
        
        if not ruta or not hosts:
            messagebox.showerror("Error", "Debe completar todos los campos")
            return
        
        # Recopilar opciones seleccionadas
        opciones = [opt for opt, var in self.opciones_vars.items() if var.get()]
        
        # Si no hay opciones seleccionadas, permitir continuar con los valores por defecto de NFS
        # El usuario puede deseleccionar todo si lo desea
        
        # Verificar permisos del filesystem
        permisos_ok, mensaje_permisos = self.gestor_nfs.verificar_y_ajustar_permisos(
            ruta, opciones
        )
        
        ajustar_permisos = False
        if not permisos_ok:
            respuesta = messagebox.askyesnocancel(
                "Verificación de Permisos",
                mensaje_permisos + "\n\n" +
                "¿Desea ajustar los permisos automáticamente?\n\n" +
                "SÍ: Ajustar permisos (recomendado)\n" +
                "NO: Continuar sin ajustar (puede causar errores)\n" +
                "CANCELAR: Abortar operación"
            )
            
            if respuesta is None:  # Cancelar
                return
            elif respuesta:  # Sí
                ajustar_permisos = True
        
        # Agregar configuración
        if self.gestor_nfs.agregar_configuracion(ruta, hosts, opciones, ajustar_permisos):
            mensaje = "Exportación agregada correctamente\n\n"
            if ajustar_permisos:
                mensaje += "Permisos del filesystem ajustados\n\n"
            mensaje += "IMPORTANTE: Debe aplicar los cambios para que tengan efecto"
            
            messagebox.showinfo("Éxito", mensaje)
            self._actualizar_exportaciones()
            self._limpiar_campos()
            self.actualizar_barra_estado("Exportación agregada", 'exito')
        else:
            messagebox.showerror(
                "Error",
                "No se pudo agregar la exportación.\n" +
                "Verifique los permisos y los logs del sistema."
            )
            self.actualizar_barra_estado("Error al agregar exportación", 'error')
    
    def _actualizar_exportaciones(self):
        """
        Actualiza la lista de exportaciones
        """
        self.lista_exportaciones.delete(0, tk.END)
        configs = self.gestor_nfs.leer_configuracion_actual()
        
        if not configs:
            self.lista_exportaciones.insert(
                tk.END,
                "No hay exportaciones configuradas"
            )
        else:
            for i, config in enumerate(configs):
                texto = "{0}. {1} -> {2} ({3})".format(
                    i+1,
                    config['carpeta'],
                    config['hosts'],
                    ', '.join(config['opciones'])
                )
                self.lista_exportaciones.insert(tk.END, texto)
        
        self.actualizar_barra_estado(
            "{0} exportaciones configuradas".format(len(configs)),
            'info'
        )
        
        logger.info("Lista de exportaciones actualizada: {0} items".format(len(configs)))
    
    def _eliminar_exportacion(self):
        """
        Elimina la exportación seleccionada
        """
        sel = self.lista_exportaciones.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione una exportación")
            return
        
        configs = self.gestor_nfs.leer_configuracion_actual()
        if sel[0] >= len(configs):
            return
        
        config = configs[sel[0]]
        
        if not messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Está seguro de eliminar esta exportación?\n\n{0}".format(
                config['linea_original']
            )
        ):
            return
        
        if self.gestor_nfs.eliminar_configuracion(sel[0]):
            messagebox.showinfo("Éxito", "Exportación eliminada correctamente")
            self._actualizar_exportaciones()
            self.actualizar_barra_estado("Exportación eliminada", 'exito')
        else:
            messagebox.showerror("Error", "No se pudo eliminar la exportación")
            self.actualizar_barra_estado("Error al eliminar", 'error')
    
    def _aplicar_cambios_nfs(self):
        """
        Aplica los cambios con exportfs -ra
        """
        # Verificar servicio NFS
        activo, mensaje = self.gestor_nfs.verificar_servicio_nfs()
        
        if not activo:
            respuesta = messagebox.askyesno(
                "Servicio NFS Inactivo",
                mensaje + "\n\n" +
                "¿Desea intentar iniciar el servicio automáticamente?"
            )
            
            if respuesta:
                import subprocess
                try:
                    subprocess.run(
                        ["sudo", "systemctl", "start", "nfs-server"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    messagebox.showinfo("Éxito", "Servicio NFS iniciado")
                except Exception:
                    messagebox.showerror(
                        "Error",
                        "No se pudo iniciar el servicio.\n" +
                        "Ejecute: sudo systemctl start nfs-server"
                    )
                    return
            else:
                return
        
        if not messagebox.askyesno(
            "Aplicar Cambios",
            "Esto ejecutará 'exportfs -ra' para aplicar los cambios.\n\n" +
            "¿Desea continuar?"
        ):
            return
        
        if self.gestor_nfs.aplicar_cambios_nfs():
            messagebox.showinfo(
                "Éxito",
                "Cambios aplicados correctamente\n\n" +
                "El servidor NFS ha sido actualizado.\n" +
                "Los clientes pueden ahora acceder a los recursos compartidos."
            )
            self.actualizar_barra_estado("Cambios NFS aplicados", 'exito')
        else:
            messagebox.showerror(
                "Error",
                "No se pudieron aplicar los cambios.\n\n" +
                "Posibles causas:\n" +
                "• No tiene permisos de root\n" +
                "• Hay errores de sintaxis en /etc/exports\n\n" +
                "Ejecute: sudo exportfs -ra"
            )
            self.actualizar_barra_estado("Error al aplicar cambios", 'error')
    
    def _ver_espacio_disco(self):
        """
        Muestra información de espacio en disco
        """
        resultado = self.gestor_nfs.verificar_montajes_y_disco()
        
        if resultado['success']:
            # Crear ventana para mostrar resultados
            ventana = tk.Toplevel(self.parent)
            ventana.title("Espacio en Disco y Montajes")
            ventana.geometry("800x500")
            ventana.configure(bg=TemaColores.COLOR_FONDO_PRINCIPAL)
            
            # Texto con resultados
            from .temas import crear_text_widget
            texto = crear_text_widget(ventana, height=20)
            texto.pack(fill='both', expand=True, padx=10, pady=10)
            texto.insert('1.0', resultado['data'])
            texto.config(state='disabled')
            
            # Botón cerrar
            crear_boton(
                ventana,
                "Cerrar",
                ventana.destroy,
                tipo='secondary'
            ).pack(pady=10)
        else:
            messagebox.showerror("Error", resultado['message'])
    
    def _limpiar_campos(self):
        """
        Limpia los campos del formulario
        """
        self.entrada_ruta_servidor.delete(0, tk.END)
        self.entrada_hosts_servidor.delete(0, tk.END)
        self.entrada_hosts_servidor.insert(0, "*")
        self.label_validacion_ruta.config(text="")
        self.label_validacion_hosts.config(text="")
        
        # Restablecer valores por defecto
        for var in self.opciones_vars.values():
            var.set(False)
        
        self.opciones_vars['rw'].set(True)
        self.opciones_vars['sync'].set(True)
        self.opciones_vars['no_subtree_check'].set(True)
        self.opciones_vars['root_squash'].set(True)