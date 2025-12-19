"""
Ventana Principal - Interfaz Gráfica Unificada
Combina todas las funcionalidades en una interfaz moderna y rápida
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from gestor_nfs import GestorNFS
from cliente_nfs import ClienteNFS
from transferencia import TransferenciaNFS
from utils.logger import logger
from .temas import (
    TemaColores, configurar_estilos, crear_boton,
    crear_listbox_personalizado, crear_text_widget,
    crear_frame_card, crear_label_estado, Iconos
)


class VentanaPrincipal:
    """
    Ventana principal que integra todas las funcionalidades
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Configurador NFS Integral - OpenSUSE")
        self.root.configure(bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        
        # Inicializar componentes
        self.gestor_nfs = GestorNFS()
        self.cliente_nfs = ClienteNFS()
        self.transferencia = None
        
        # Variables de estado
        self.recurso_montado = False
        
        # Configurar estilos
        configurar_estilos()
        
        # Crear interfaz
        self._crear_header()
        self._crear_barra_estado()
        self._crear_notebook()
        
        logger.info("Interfaz gráfica inicializada")
    
    def _crear_header(self):
        """
        Crea el encabezado de la aplicación
        """
        header_frame = tk.Frame(self.root, bg=TemaColores.COLOR_FONDO_DARK, height=60)
        header_frame.pack(side="top", fill="x")
        header_frame.pack_propagate(False)
        
        titulo = tk.Label(
            header_frame,
            text="{0} Configurador NFS Integral para OpenSUSE".format(Iconos.CONFIG),
            bg=TemaColores.COLOR_FONDO_DARK,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 16, 'bold')
        )
        titulo.pack(pady=15)
    
    def _crear_notebook(self):
        """
        Crea el notebook con todas las pestañas
        """
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña 1: Configuración del Servidor
        self.tab_servidor = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_servidor, text='{0} Servidor NFS'.format(Iconos.SERVIDOR))
        self._crear_tab_servidor()
        
        # Pestaña 2: Cliente NFS
        self.tab_cliente = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_cliente, text='{0} Cliente NFS'.format(Iconos.CLIENTE))
        self._crear_tab_cliente()
        
        # Pestaña 3: Transferencia de Archivos
        self.tab_transferencia = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_transferencia, text='{0} Transferencias'.format(Iconos.COMPARTIR))
        self._crear_tab_transferencia()
    
    # ============== PESTAÑA SERVIDOR NFS ==============
    
    def _crear_tab_servidor(self):
        """
        Crea la pestaña de configuración del servidor NFS
        """
        # Sección 1: Agregar nueva exportación
        frame_agregar = crear_frame_card(self.tab_servidor, title="1. Agregar Nueva Exportación")
        frame_agregar.pack(fill='x', pady=(0, 10))
        
        # Ruta a exportar
        ttk.Label(frame_agregar, text="Ruta a Exportar:").grid(row=0, column=0, sticky='w', pady=5)
        self.entrada_ruta_servidor = ttk.Entry(frame_agregar, width=45)
        self.entrada_ruta_servidor.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        
        crear_boton(frame_agregar, "Explorar...", self._explorar_ruta_servidor, tipo='info', width=12).grid(row=0, column=2, padx=5)
        
        # Hosts permitidos
        ttk.Label(frame_agregar, text="Hosts Permitidos:").grid(row=1, column=0, sticky='w', pady=5)
        self.entrada_hosts_servidor = ttk.Entry(frame_agregar, width=45)
        self.entrada_hosts_servidor.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        self.entrada_hosts_servidor.insert(0, "*")
        
        ttk.Label(frame_agregar, text="Ejemplos: 192.168.1.100, 192.168.1.0/24, *", 
                 foreground=TemaColores.COLOR_TEXTO_MUTED).grid(row=2, column=1, sticky='w')
        
        frame_agregar.columnconfigure(1, weight=1)
        
        # Opciones NFS
        frame_opciones = ttk.LabelFrame(frame_agregar, text="Opciones NFS", padding=10)
        frame_opciones.grid(row=3, column=0, columnspan=3, sticky='ew', pady=10)
        
        self.opciones_vars = {}
        opciones_comunes = [
            ('rw', 'Lectura/Escritura'), ('ro', 'Solo Lectura'),
            ('sync', 'Sincronizado'), ('async', 'Asíncrono'),
            ('root_squash', 'Mapear root'), ('no_root_squash', 'Root sin mapear'),
            ('no_subtree_check', 'Sin verificación subdirectorios')
        ]
        
        for i, (opt, desc) in enumerate(opciones_comunes):
            var = tk.BooleanVar()
            self.opciones_vars[opt] = var
            chk = ttk.Checkbutton(frame_opciones, text="{0} ({1})".format(opt, desc), variable=var)
            chk.grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)
        
        # Valores por defecto recomendados
        self.opciones_vars['rw'].set(True)
        self.opciones_vars['sync'].set(True)
        self.opciones_vars['no_subtree_check'].set(True)
        
        # Botón agregar
        crear_boton(frame_agregar, "{0} Agregar Exportación".format(Iconos.EXITO), 
                   self._agregar_exportacion_servidor, tipo='success').grid(row=4, column=0, columnspan=3, pady=10)
        
        # Sección 2: Exportaciones actuales
        frame_lista = crear_frame_card(self.tab_servidor, title="2. Exportaciones Actuales")
        frame_lista.pack(fill='both', expand=True, pady=(0, 10))
        
        # Listbox con exportaciones
        frame_listbox = tk.Frame(frame_lista, bg=TemaColores.COLOR_FONDO_CARD)
        frame_listbox.pack(fill='both', expand=True, pady=5)
        
        self.lista_exportaciones, scrollbar = crear_listbox_personalizado(frame_listbox, height=8)
        self.lista_exportaciones.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botones de control
        frame_botones = tk.Frame(frame_lista, bg=TemaColores.COLOR_FONDO_CARD)
        frame_botones.pack(fill='x', pady=5)
        
        crear_boton(frame_botones, "{0} Actualizar".format(Iconos.REFRESH), 
                   self._actualizar_exportaciones, tipo='primary').pack(side='left', padx=3)
        crear_boton(frame_botones, "{0} Eliminar".format(Iconos.DELETE), 
                   self._eliminar_exportacion, tipo='danger').pack(side='left', padx=3)
        crear_boton(frame_botones, "{0} Aplicar Cambios".format(Iconos.EXITO), 
                   self._aplicar_cambios_nfs, tipo='success').pack(side='left', padx=3)
        
        # Cargar exportaciones iniciales
        self._actualizar_exportaciones()
    
    def _explorar_ruta_servidor(self):
        """Explorar carpeta o archivo para exportar"""
        tipo = messagebox.askquestion(
            "Tipo de Recurso",
            "¿Desea exportar una CARPETA completa?\n\n(Seleccione 'No' para exportar un archivo individual)"
        )
        
        if tipo == 'yes':
            ruta = filedialog.askdirectory(title="Seleccione carpeta a exportar")
        else:
            ruta = filedialog.askopenfilename(title="Seleccione archivo a exportar")
        
        if ruta:
            self.entrada_ruta_servidor.delete(0, tk.END)
            self.entrada_ruta_servidor.insert(0, ruta)
    
    def _agregar_exportacion_servidor(self):
        """Agrega una nueva exportación NFS"""
        ruta = self.entrada_ruta_servidor.get().strip()
        hosts = self.entrada_hosts_servidor.get().strip()
        
        if not ruta or not hosts:
            messagebox.showerror("Error", "Debe completar todos los campos")
            return
        
        # Recopilar opciones seleccionadas
        opciones = [opt for opt, var in self.opciones_vars.items() if var.get()]
        
        if not opciones:
            messagebox.showwarning("Advertencia", "No seleccionó ninguna opción NFS")
            return
        
        # Preguntar si desea ajustar permisos
        ajustar = messagebox.askyesno(
            "Ajustar Permisos",
            "¿Desea ajustar automáticamente los permisos del sistema de archivos?\n\n" +
            "(Recomendado para evitar 'Permission Denied')"
        )
        
        # Agregar configuración
        if self.gestor_nfs.agregar_configuracion(ruta, hosts, opciones, ajustar):
            messagebox.showinfo(
                "Éxito",
                "Exportación agregada correctamente\n\n" +
                "IMPORTANTE: Debe aplicar los cambios para que tengan efecto"
            )
            self._actualizar_exportaciones()
            self.entrada_ruta_servidor.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "No se pudo agregar la exportación")
    
    def _actualizar_exportaciones(self):
        """Actualiza la lista de exportaciones"""
        self.lista_exportaciones.delete(0, tk.END)
        configs = self.gestor_nfs.leer_configuracion_actual()
        
        for i, config in enumerate(configs):
            texto = "{0}. {1} -> {2} ({3})".format(
                i+1, config['carpeta'], config['hosts'], ','.join(config['opciones'])
            )
            self.lista_exportaciones.insert(tk.END, texto)
        
        self._actualizar_barra_estado(
            "{0} exportaciones configuradas".format(len(configs)), 'info'
        )
    
    def _eliminar_exportacion(self):
        """Elimina la exportación seleccionada"""
        sel = self.lista_exportaciones.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione una exportación")
            return
        
        if not messagebox.askyesno("Confirmar", "¿Eliminar esta exportación?"):
            return
        
        if self.gestor_nfs.eliminar_configuracion(sel[0]):
            messagebox.showinfo("Éxito", "Exportación eliminada")
            self._actualizar_exportaciones()
        else:
            messagebox.showerror("Error", "No se pudo eliminar")
    
    def _aplicar_cambios_nfs(self):
        """Aplica los cambios con exportfs -ra"""
        if not messagebox.askyesno(
            "Aplicar Cambios",
            "Esto ejecutará 'exportfs -ra' para aplicar los cambios.\n\n¿Continuar?"
        ):
            return
        
        if self.gestor_nfs.aplicar_cambios_nfs():
            messagebox.showinfo("Éxito", "Cambios aplicados correctamente")
            self._actualizar_barra_estado("Cambios NFS aplicados", 'exito')
        else:
            messagebox.showerror("Error", "No se pudieron aplicar los cambios")
    
    # ============== PESTAÑA CLIENTE NFS ==============
    
    def _crear_tab_cliente(self):
        """Crea la pestaña de cliente NFS"""
        # Sección 1: Montar recurso
        frame_montar = crear_frame_card(self.tab_cliente, title="1. Montar Recurso NFS")
        frame_montar.pack(fill='x', pady=(0, 10))
        
        ttk.Label(frame_montar, text="IP del Servidor:").grid(row=0, column=0, sticky='w', pady=5)
        self.entrada_ip_cliente = ttk.Entry(frame_montar, width=30)
        self.entrada_ip_cliente.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        
        ttk.Label(frame_montar, text="Ruta Remota:").grid(row=1, column=0, sticky='w', pady=5)
        self.entrada_ruta_remota = ttk.Entry(frame_montar, width=30)
        self.entrada_ruta_remota.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        
        ttk.Label(frame_montar, text="Punto de Montaje:").grid(row=2, column=0, sticky='w', pady=5)
        self.entrada_punto_montaje = ttk.Entry(frame_montar, width=30)
        self.entrada_punto_montaje.grid(row=2, column=1, sticky='ew', pady=5, padx=5)
        self.entrada_punto_montaje.insert(0, "/mnt/nfs_compartido")
        
        frame_montar.columnconfigure(1, weight=1)
        
        # Botones de montaje
        frame_botones_montar = tk.Frame(frame_montar, bg=TemaColores.COLOR_FONDO_CARD)
        frame_botones_montar.grid(row=3, column=0, columnspan=2, pady=10)
        
        crear_boton(frame_botones_montar, "{0} Montar".format(Iconos.MONTADO), 
                   self._montar_recurso, tipo='success').pack(side='left', padx=3)
        crear_boton(frame_botones_montar, "{0} Desmontar".format(Iconos.DESMONTADO), 
                   self._desmontar_recurso, tipo='warning').pack(side='left', padx=3)
        crear_boton(frame_botones_montar, "{0} Ver Contenido".format(Iconos.CARPETA), 
                   self._ver_contenido_remoto, tipo='info').pack(side='left', padx=3)
        
        # Label de estado de montaje
        self.label_estado_montaje = crear_label_estado(frame_montar, 
                                                        "{0} No montado".format(Iconos.DESMONTADO), 
                                                        tipo='error')
        self.label_estado_montaje.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Sección 2: Resultados
        frame_resultados = crear_frame_card(self.tab_cliente, title="2. Contenido y Notificaciones")
        frame_resultados.pack(fill='both', expand=True)
        
        self.texto_cliente = crear_text_widget(frame_resultados, height=15)
        self.texto_cliente.pack(fill='both', expand=True)
    
    def _montar_recurso(self):
        """Monta el recurso NFS"""
        ip = self.entrada_ip_cliente.get().strip()
        ruta_remota = self.entrada_ruta_remota.get().strip()
        punto_montaje = self.entrada_punto_montaje.get().strip()
        
        if not all([ip, ruta_remota, punto_montaje]):
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        self.cliente_nfs.punto_montaje = punto_montaje
        resultado = self.cliente_nfs.montar_recurso(ip, ruta_remota)
        
        self._actualizar_texto_cliente(resultado['message'])
        
        if resultado['success']:
            self.recurso_montado = True
            self.label_estado_montaje.config(
                text="{0} Montado en: {1}".format(Iconos.MONTADO, punto_montaje),
                bg=TemaColores.COLOR_MONTADO
            )
            self.transferencia = TransferenciaNFS(punto_montaje)
            self._actualizar_barra_estado("Recurso montado correctamente", 'exito')
        else:
            self._actualizar_barra_estado("Error al montar recurso", 'error')
    
    def _desmontar_recurso(self):
        """Desmonta el recurso NFS"""
        resultado = self.cliente_nfs.desmontar_recurso()
        self._actualizar_texto_cliente(resultado['message'])
        
        if resultado['success']:
            self.recurso_montado = False
            self.label_estado_montaje.config(
                text="{0} No montado".format(Iconos.DESMONTADO),
                bg=TemaColores.COLOR_DESMONTADO
            )
            self.transferencia = None
            self._actualizar_barra_estado("Recurso desmontado", 'info')
    
    def _ver_contenido_remoto(self):
        """Ver contenido del recurso montado"""
        resultado = self.cliente_nfs.listar_contenido()
        
        if resultado['success'] and 'data' in resultado:
            self._actualizar_texto_cliente(resultado['message'] + "\n\n" + resultado['data'])
        else:
            self._actualizar_texto_cliente(resultado['message'])
    
    def _actualizar_texto_cliente(self, texto):
        """Actualiza el texto del cliente"""
        self.texto_cliente.config(state='normal')
        self.texto_cliente.delete('1.0', tk.END)
        self.texto_cliente.insert('1.0', texto)
        
        # Aplicar colores según el contenido
        if '[OK]' in texto or '[ÉXITO]' in texto:
            self.texto_cliente.tag_add('exito', '1.0', '1.end')
        elif '[ERROR]' in texto or '[FALLO]' in texto:
            self.texto_cliente.tag_add('error', '1.0', '1.end')
        elif '[WARNING]' in texto or '[ADVERTENCIA]' in texto:
            self.texto_cliente.tag_add('warning', '1.0', '1.end')
        
        self.texto_cliente.config(state='disabled')
    
    # ============== PESTAÑA TRANSFERENCIAS ==============
    
    def _crear_tab_transferencia(self):
        """Crea la pestaña de transferencias"""
        # Frame dividido en dos columnas
        frame_izq = crear_frame_card(self.tab_transferencia, title="{0} Enviar Archivos".format(Iconos.COMPARTIR))
        frame_izq.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        frame_der = crear_frame_card(self.tab_transferencia, title="{0} Recibir Archivos".format(Iconos.RECIBIR))
        frame_der.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # === ENVIAR ARCHIVOS ===
        crear_boton(frame_izq, "{0} Seleccionar Archivos".format(Iconos.ARCHIVO), 
                   self._enviar_archivos, tipo='primary').pack(pady=5, fill='x')
        crear_boton(frame_izq, "{0} Seleccionar Carpeta".format(Iconos.CARPETA), 
                   self._enviar_carpeta, tipo='primary').pack(pady=5, fill='x')
        
        ttk.Separator(frame_izq, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(frame_izq, text="Archivos enviados recientemente:").pack(anchor='w', pady=5)
        
        self.lista_enviados, scroll_env = crear_listbox_personalizado(frame_izq, height=12)
        self.lista_enviados.pack(fill='both', expand=True, pady=5)
        
        # === RECIBIR ARCHIVOS ===
        crear_boton(frame_der, "{0} Actualizar Lista".format(Iconos.REFRESH), 
                   self._actualizar_lista_remotos, tipo='info').pack(pady=5, fill='x')
        
        ttk.Label(frame_der, text="Archivos disponibles en el recurso:").pack(anchor='w', pady=5)
        
        self.lista_remotos, scroll_rem = crear_listbox_personalizado(frame_der, height=12, selectmode='multiple')
        self.lista_remotos.pack(fill='both', expand=True, pady=5)
        
        ttk.Label(frame_der, text="Destino local:").pack(anchor='w', pady=5)
        
        frame_destino = tk.Frame(frame_der, bg=TemaColores.COLOR_FONDO_CARD)
        frame_destino.pack(fill='x', pady=5)
        
        self.entrada_destino_local = ttk.Entry(frame_destino, width=30)
        self.entrada_destino_local.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entrada_destino_local.insert(0, os.path.expanduser("~/Descargas"))
        
        crear_boton(frame_destino, "...", self._explorar_destino, tipo='secondary', width=3).pack(side='right')
        
        crear_boton(frame_der, "{0} Recibir Seleccionados".format(Iconos.RECIBIR), 
                   self._recibir_archivos, tipo='success').pack(pady=10, fill='x')
    
    def _enviar_archivos(self):
        """Envía archivos seleccionados"""
        if not self.recurso_montado or not self.transferencia:
            messagebox.showwarning("Advertencia", "Primero debe montar un recurso NFS")
            return
        
        archivos = filedialog.askopenfilenames(title="Seleccione archivos para enviar")
        if not archivos:
            return
        
        resultado = self.transferencia.enviar_multiples(archivos)
        
        if resultado['success']:
            for archivo in archivos:
                self.lista_enviados.insert(0, os.path.basename(archivo))
            messagebox.showinfo("Éxito", resultado['message'])
            self._actualizar_barra_estado("Archivos enviados", 'exito')
        else:
            messagebox.showerror("Error", resultado['message'])
    
    def _enviar_carpeta(self):
        """Envía una carpeta completa"""
        if not self.recurso_montado or not self.transferencia:
            messagebox.showwarning("Advertencia", "Primero debe montar un recurso NFS")
            return
        
        carpeta = filedialog.askdirectory(title="Seleccione carpeta para enviar")
        if not carpeta:
            return
        
        resultado = self.transferencia.enviar_directorio(carpeta)
        
        if resultado['success']:
            self.lista_enviados.insert(0, "{0} (carpeta)".format(os.path.basename(carpeta)))
            messagebox.showinfo("Éxito", resultado['message'])
            self._actualizar_barra_estado("Carpeta enviada", 'exito')
        else:
            messagebox.showerror("Error", resultado['message'])
    
    def _actualizar_lista_remotos(self):
        """Actualiza la lista de archivos remotos"""
        if not self.recurso_montado or not self.transferencia:
            messagebox.showwarning("Advertencia", "Primero debe montar un recurso NFS")
            return
        
        resultado = self.transferencia.listar_remoto()
        
        if resultado['success']:
            self.lista_remotos.delete(0, tk.END)
            for item in resultado['items']:
                icono = Iconos.CARPETA if item['tipo'] == 'directorio' else Iconos.ARCHIVO
                texto = "{0} {1}".format(icono, item['nombre'])
                self.lista_remotos.insert(tk.END, texto)
            self._actualizar_barra_estado("{0} items disponibles".format(len(resultado['items'])), 'info')
        else:
            messagebox.showerror("Error", resultado['message'])
    
    def _explorar_destino(self):
        """Explora destino local"""
        destino = filedialog.askdirectory(title="Seleccione carpeta de destino")
        if destino:
            self.entrada_destino_local.delete(0, tk.END)
            self.entrada_destino_local.insert(0, destino)
    
    def _recibir_archivos(self):
        """Recibe archivos seleccionados"""
        if not self.recurso_montado or not self.transferencia:
            messagebox.showwarning("Advertencia", "Primero debe montar un recurso NFS")
            return
        
        seleccion = self.lista_remotos.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione archivos para recibir")
            return
        
        # Obtener nombres de archivos (quitando el icono)
        nombres = []
        for idx in seleccion:
            texto = self.lista_remotos.get(idx)
            nombre = texto.split(' ', 1)[1]  # Quitar icono
            nombres.append(nombre)
        
        destino = self.entrada_destino_local.get().strip()
        
        resultado = self.transferencia.recibir_multiples(nombres, destino)
        
        if resultado['success']:
            messagebox.showinfo("Éxito", resultado['message'])
            self._actualizar_barra_estado("Archivos recibidos", 'exito')
        else:
            messagebox.showerror("Error", resultado['message'])
    
    # ============== BARRA DE ESTADO ==============
    
    def _crear_barra_estado(self):
        """Crea la barra de estado"""
        self.barra_estado = tk.Label(
            self.root,
            text="Listo",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=TemaColores.COLOR_INFO,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 9),
            padx=10,
            pady=5
        )
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _actualizar_barra_estado(self, texto, tipo='info'):
        """Actualiza la barra de estado"""
        colores = {
            'exito': TemaColores.COLOR_SUCCESS,
            'error': TemaColores.COLOR_DANGER,
            'warning': TemaColores.COLOR_WARNING,
            'info': TemaColores.COLOR_INFO
        }
        
        self.barra_estado.config(
            text=texto,
            bg=colores.get(tipo, TemaColores.COLOR_INFO)
        )