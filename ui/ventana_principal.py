"""
Ventana Principal - Interfaz Gráfica Unificada
Combina todas las funcionalidades en una interfaz moderna y rápida
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from gestor_nfs import GestorNFS
from cliente_nfs import ClienteNFS
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
        
        # Punto de montaje (solo para referencia, se monta al aplicar cambios)
        ttk.Label(frame_agregar, text="Punto de Montaje (opcional):").grid(row=3, column=0, sticky='w', pady=5)
        self.entrada_punto_montaje_servidor = ttk.Entry(frame_agregar, width=45)
        self.entrada_punto_montaje_servidor.grid(row=3, column=1, sticky='ew', pady=5, padx=5)
        self.entrada_punto_montaje_servidor.insert(0, "/mnt/nfs_compartido")
        
        crear_boton(frame_agregar, "Explorar...", self._explorar_punto_montaje_servidor, tipo='info', width=12).grid(row=3, column=2, padx=5)
        
        ttk.Label(frame_agregar, text="Se montará al aplicar cambios", 
                 foreground=TemaColores.COLOR_TEXTO_MUTED).grid(row=4, column=1, sticky='w')
        
        frame_agregar.columnconfigure(1, weight=1)
        
        # Opciones NFS
        frame_opciones = ttk.LabelFrame(frame_agregar, text="Opciones NFS", padding=10)
        frame_opciones.grid(row=5, column=0, columnspan=3, sticky='ew', pady=10)
        
        self.opciones_vars = {}
        opciones_comunes = [
            ('rw', 'Lectura/Escritura'), ('ro', 'Solo Lectura'),
            ('sync', 'Sincronizado'), ('async', 'Asíncrono'),
            ('root_squash', 'Mapear root'), ('no_root_squash', 'Root sin mapear'),
            ('secure', 'Puertos seguros (<1024)'), ('insecure', 'Puertos inseguros (>1024)'),
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
        self.opciones_vars['secure'].set(True)
        self.opciones_vars['root_squash'].set(True)
        self.opciones_vars['no_subtree_check'].set(True)
        
        # Botón agregar
        crear_boton(frame_agregar, "{0} Agregar Exportación".format(Iconos.EXITO), 
                   self._agregar_exportacion_servidor, tipo='success').grid(row=6, column=0, columnspan=3, pady=10)
        
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
        """Explorar carpeta para exportar (solo directorios permitidos)"""
        ruta = filedialog.askdirectory(title="Seleccione CARPETA para exportar (NFS solo soporta directorios)")
        
        if ruta:
            self.entrada_ruta_servidor.delete(0, tk.END)
            self.entrada_ruta_servidor.insert(0, ruta)
    
    
    
    def _explorar_punto_montaje_servidor(self):
        """Explorar para seleccionar punto de montaje"""
        punto = filedialog.askdirectory(title="Seleccione carpeta para punto de montaje local")
        if punto:
            self.entrada_punto_montaje_servidor.delete(0, tk.END)
            self.entrada_punto_montaje_servidor.insert(0, punto)
    
    def _agregar_exportacion_servidor(self):
        """Agrega una nueva exportación NFS (sin montar aún)"""
        ruta = self.entrada_ruta_servidor.get().strip()
        hosts = self.entrada_hosts_servidor.get().strip()
        
        if not ruta or not hosts:
            messagebox.showerror("Error", "Debe completar ruta y hosts")
            return
        
        # Validar que la ruta sea un directorio
        if not os.path.isdir(ruta):
            messagebox.showerror("Error", "La ruta debe ser un DIRECTORIO")
            return
        
        # Recopilar opciones seleccionadas
        opciones = [opt for opt, var in self.opciones_vars.items() if var.get()]
        
        # Agregar configuración sin montar
        if self.gestor_nfs.agregar_configuracion(ruta, hosts, opciones, ajustar_permisos=False):
            punto_montaje = self.entrada_punto_montaje_servidor.get().strip()
            mensaje = "Exportación agregada correctamente\n\n"
            
            if punto_montaje:
                mensaje += "Punto de montaje guardado: {0}\n\n".format(punto_montaje)
            
            mensaje += "SIGUIENTE PASO:\n" +\
                      "1. Clic en 'Aplicar Cambios' para activar\n" +\
                      "2. Se montará automáticamente en: {0}".format(punto_montaje if punto_montaje else "/mnt/nfs_compartido")
            
            messagebox.showinfo("Éxito", mensaje)
            self._actualizar_exportaciones()
            
            # Limpiar solo ruta, dejar hosts y punto de montaje
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
        """Aplica los cambios con exportfs -ra Y monta si está configurado"""
        if not messagebox.askyesno(
            "Aplicar Cambios",
            "Esto ejecutará 'exportfs -ra' para activar las exportaciones.\n\n" +
            "Si especificó punto de montaje, también se montará.\n\n¿Continuar?"
        ):
            return
        
        if self.gestor_nfs.aplicar_cambios_nfs():
            mensajes = ["Cambios aplicados correctamente con exportfs -ra\n"]
            
            # Si hay punto de montaje especificado, intentar montar
            punto_montaje = self.entrada_punto_montaje_servidor.get().strip()
            ruta = self.entrada_ruta_servidor.get().strip()
            
            if punto_montaje and not ruta:
                # Obtener la última ruta exportada
                configs = self.gestor_nfs.leer_configuracion_actual()
                if configs:
                    ruta = configs[-1]['carpeta']
            
            if punto_montaje and ruta:
                resultado = self._montar_carpeta_servidor_local(ruta, punto_montaje)
                mensajes.append(resultado)
                messagebox.showinfo("Éxito", "\n".join(mensajes))
            else:
                messagebox.showinfo("Éxito", "\n".join(mensajes))
            
            self._actualizar_barra_estado("Cambios NFS aplicados", 'exito')
        else:
            messagebox.showerror("Error", "No se pudieron aplicar los cambios")
    
    def _montar_carpeta_servidor_local(self, ruta_local, punto_montaje):
        """Monta localmente con binding mount después de exportfs -ra"""
        try:
            # Crear punto de montaje si no existe
            if not os.path.exists(punto_montaje):
                try:
                    os.makedirs(punto_montaje, mode=0o755)
                except PermissionError:
                    return "[ADVERTENCIA] Sin permisos para crear directorio. Intente en /home"
                except Exception as e:
                    return "Error creando punto: {0}".format(str(e))
            
            # Usar binding mount que es más simple y directo
            comando = 'mount --bind "{0}" "{1}"'.format(ruta_local, punto_montaje)
            logger.info("Montando localmente: {0}".format(comando))
            resultado = self.gestor_nfs._run_command(comando)
            
            if resultado["success"]:
                logger.exito("Carpeta montada en {0}".format(punto_montaje))
                return "\n✓ Montaje local exitoso en: {0}".format(punto_montaje)
            else:
                stderr = resultado.get('stderr', '').lower()
                if "already mounted" in stderr or "busy" in stderr:
                    return "\n[ADVERTENCIA] Punto de montaje ya está en uso.\nPara desmontar: sudo umount {0}".format(punto_montaje)
                else:
                    return "\n[ERROR] Error al montar: {0}".format(resultado.get('stderr', 'desconocido'))
        except Exception as e:
            logger.error("Error en montaje local: {0}".format(str(e)))
            return "Error: {0}".format(str(e))
    
    
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
        frame_punto_montaje = tk.Frame(frame_montar, bg=TemaColores.COLOR_FONDO_CARD)
        frame_punto_montaje.grid(row=2, column=1, sticky='ew', pady=5, padx=5)
        
        self.entrada_punto_montaje = ttk.Entry(frame_punto_montaje, width=25)
        self.entrada_punto_montaje.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entrada_punto_montaje.insert(0, "/mnt/nfs_compartido")
        
        crear_boton(frame_punto_montaje, "Explorar...", self._explorar_punto_montaje, tipo='info', width=12).pack(side='right')
        
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
    
    def _explorar_punto_montaje(self):
        """Permite seleccionar o crear punto de montaje"""
        punto = filedialog.askdirectory(title="Seleccione o cree el punto de montaje")
        if punto:
            self.entrada_punto_montaje.delete(0, tk.END)
            self.entrada_punto_montaje.insert(0, punto)
    
    def _montar_recurso(self):
        """Monta el recurso NFS con validaciones adicionales"""
        ip = self.entrada_ip_cliente.get().strip()
        ruta_remota = self.entrada_ruta_remota.get().strip()
        punto_montaje = self.entrada_punto_montaje.get().strip()
        
        # Validaciones básicas
        if not all([ip, ruta_remota, punto_montaje]):
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        # Validar formato de IP
        from utils.validaciones import validar_ip
        valida_ip, msg_ip = validar_ip(ip)
        if not valida_ip:
            messagebox.showerror("Error de IP", msg_ip)
            return
        
        # Crear punto de montaje si no existe
        if not os.path.exists(punto_montaje):
            try:
                os.makedirs(punto_montaje)
                self._actualizar_texto_cliente("[INFO] Punto de montaje creado: {0}".format(punto_montaje))
            except Exception as e:
                messagebox.showerror("Error", "No se pudo crear el punto de montaje: {0}".format(str(e)))
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