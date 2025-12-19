"""
Pestaña del Cliente NFS
Módulo independiente para montar y gestionar recursos NFS
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os

from .temas import (
    TemaColores, crear_boton, crear_text_widget,
    crear_frame_card, crear_label_estado, Iconos
)
from utils.logger import logger


class TabCliente:
    """
    Pestaña para cliente NFS
    """
    
    def __init__(self, parent, cliente_nfs, actualizar_barra_estado, set_transferencia):
        self.parent = parent
        self.cliente_nfs = cliente_nfs
        self.actualizar_barra_estado = actualizar_barra_estado
        self.set_transferencia = set_transferencia
        
        # Estado de montaje
        self.recurso_montado = False
        
        # Crear interfaz
        self._crear_interfaz()
        
        logger.info("TabCliente inicializado")
    
    def _crear_interfaz(self):
        """
        Crea la interfaz de la pestaña del cliente
        """
        # Sección 1: Montar recurso
        self._crear_seccion_montar()
        
        # Sección 2: Contenido y notificaciones
        self._crear_seccion_resultados()
    
    def _crear_seccion_montar(self):
        """
        Crea la sección para montar recursos
        """
        frame_montar = crear_frame_card(
            self.parent,
            title="1. {0} Montar Recurso NFS Remoto".format(Iconos.CLIENTE)
        )
        frame_montar.pack(fill='x', pady=(0, 10))
        
        # IP del servidor
        ttk.Label(frame_montar, text="IP del Servidor NFS:").grid(
            row=0, column=0, sticky='w', pady=5, padx=5
        )
        
        self.entrada_ip_cliente = ttk.Entry(frame_montar, width=35)
        self.entrada_ip_cliente.grid(
            row=0, column=1, sticky='ew', pady=5, padx=5
        )
        
        # Validación IP
        self.label_validacion_ip = ttk.Label(
            frame_montar,
            text="",
            foreground=TemaColores.COLOR_TEXTO_MUTED
        )
        self.label_validacion_ip.grid(row=1, column=1, sticky='w', padx=5)
        
        self.entrada_ip_cliente.bind('<KeyRelease>', self._validar_ip_tiempo_real)
        
        ttk.Label(
            frame_montar,
            text="Ejemplo: 192.168.1.50",
            foreground=TemaColores.COLOR_TEXTO_MUTED,
            font=('Segoe UI', 8, 'italic')
        ).grid(row=2, column=1, sticky='w', padx=5, pady=(0, 10))
        
        # Ruta remota
        ttk.Label(frame_montar, text="Ruta Remota (del servidor):").grid(
            row=3, column=0, sticky='w', pady=5, padx=5
        )
        
        self.entrada_ruta_remota = ttk.Entry(frame_montar, width=35)
        self.entrada_ruta_remota.grid(
            row=3, column=1, sticky='ew', pady=5, padx=5
        )
        
        ttk.Label(
            frame_montar,
            text="Ejemplo: /home/compartido",
            foreground=TemaColores.COLOR_TEXTO_MUTED,
            font=('Segoe UI', 8, 'italic')
        ).grid(row=4, column=1, sticky='w', padx=5, pady=(0, 10))
        
        # Punto de montaje local
        ttk.Label(frame_montar, text="Punto de Montaje (local):").grid(
            row=5, column=0, sticky='w', pady=5, padx=5
        )
        
        self.entrada_punto_montaje = ttk.Entry(frame_montar, width=35)
        self.entrada_punto_montaje.grid(
            row=5, column=1, sticky='ew', pady=5, padx=5
        )
        self.entrada_punto_montaje.insert(0, "/mnt/nfs_compartido")
        
        # Validación punto de montaje
        self.label_validacion_pm = ttk.Label(
            frame_montar,
            text="",
            foreground=TemaColores.COLOR_TEXTO_MUTED
        )
        self.label_validacion_pm.grid(row=6, column=1, sticky='w', padx=5)
        
        self.entrada_punto_montaje.bind('<KeyRelease>', self._validar_pm_tiempo_real)
        
        ttk.Label(
            frame_montar,
            text="Se creará automáticamente si no existe",
            foreground=TemaColores.COLOR_TEXTO_MUTED,
            font=('Segoe UI', 8, 'italic')
        ).grid(row=7, column=1, sticky='w', padx=5, pady=(0, 10))
        
        frame_montar.columnconfigure(1, weight=1)
        
        # Botones de control
        frame_botones = tk.Frame(frame_montar, bg=TemaColores.COLOR_FONDO_CARD)
        frame_botones.grid(row=8, column=0, columnspan=2, pady=10)
        
        crear_boton(
            frame_botones,
            "{0} Montar Recurso".format(Iconos.MONTADO),
            self._montar_recurso,
            tipo='success'
        ).pack(side='left', padx=3)
        
        crear_boton(
            frame_botones,
            "{0} Desmontar".format(Iconos.DESMONTADO),
            self._desmontar_recurso,
            tipo='warning'
        ).pack(side='left', padx=3)
        
        crear_boton(
            frame_botones,
            "{0} Ver Contenido".format(Iconos.CARPETA),
            self._ver_contenido_remoto,
            tipo='info'
        ).pack(side='left', padx=3)
        
        crear_boton(
            frame_botones,
            "{0} Verificar Conexión".format(Iconos.INFO),
            self._verificar_conexion,
            tipo='secondary'
        ).pack(side='left', padx=3)
        
        # Estado de montaje
        self.label_estado_montaje = crear_label_estado(
            frame_montar,
            "{0} No montado".format(Iconos.DESMONTADO),
            tipo='error'
        )
        self.label_estado_montaje.grid(row=9, column=0, columnspan=2, pady=10, sticky='ew')
    
    def _crear_seccion_resultados(self):
        """
        Crea la sección de resultados y notificaciones
        """
        frame_resultados = crear_frame_card(
            self.parent,
            title="2. {0} Contenido del Recurso y Notificaciones".format(Iconos.INFO)
        )
        frame_resultados.pack(fill='both', expand=True)
        
        # Text widget para mostrar resultados
        self.texto_cliente = crear_text_widget(frame_resultados, height=15)
        self.texto_cliente.pack(fill='both', expand=True, pady=5)
        
        # Mensaje inicial
        mensaje_inicial = (
            "Bienvenido al Cliente NFS\n\n"
            "Para comenzar:\n"
            "1. Ingrese la IP del servidor NFS\n"
            "2. Especifique la ruta remota a montar\n"
            "3. Defina el punto de montaje local\n"
            "4. Haga clic en 'Montar Recurso'\n\n"
            "Una vez montado, podrá:\n"
            "• Ver el contenido del recurso\n"
            "• Enviar y recibir archivos (pestaña Transferencias)\n"
            "• Trabajar con el recurso como si fuera local\n\n"
            "Notas importantes:\n"
            "• Necesita permisos de root para montar\n"
            "• El servidor debe tener el recurso exportado\n"
            "• Verifique que el firewall permita NFS (puerto 2049)\n"
        )
        
        self._actualizar_texto_cliente(mensaje_inicial)
    
    def _validar_ip_tiempo_real(self, event=None):
        """
        Valida la IP en tiempo real
        """
        from utils.validaciones import validar_ip
        
        ip = self.entrada_ip_cliente.get().strip()
        
        if not ip:
            self.label_validacion_ip.config(text="")
            return
        
        es_valida, mensaje = validar_ip(ip)
        
        if es_valida:
            self.label_validacion_ip.config(
                text="{0} {1}".format(Iconos.EXITO, mensaje),
                foreground=TemaColores.COLOR_SUCCESS
            )
        else:
            self.label_validacion_ip.config(
                text="{0} {1}".format(Iconos.ERROR, mensaje),
                foreground=TemaColores.COLOR_DANGER
            )
    
    def _validar_pm_tiempo_real(self, event=None):
        """
        Valida el punto de montaje en tiempo real
        """
        from utils.validaciones import validar_punto_montaje
        
        pm = self.entrada_punto_montaje.get().strip()
        
        if not pm:
            self.label_validacion_pm.config(text="")
            return
        
        es_valido, mensaje = validar_punto_montaje(pm)
        
        if es_valido:
            self.label_validacion_pm.config(
                text="{0} {1}".format(Iconos.EXITO, mensaje),
                foreground=TemaColores.COLOR_SUCCESS
            )
        else:
            self.label_validacion_pm.config(
                text="{0} {1}".format(Iconos.ERROR, mensaje),
                foreground=TemaColores.COLOR_DANGER
            )
    
    def _montar_recurso(self):
        """
        Monta el recurso NFS
        """
        ip = self.entrada_ip_cliente.get().strip()
        ruta_remota = self.entrada_ruta_remota.get().strip()
        punto_montaje = self.entrada_punto_montaje.get().strip()
        
        if not all([ip, ruta_remota, punto_montaje]):
            messagebox.showerror(
                "Error",
                "Debe completar todos los campos:\n" +
                "• IP del servidor\n" +
                "• Ruta remota\n" +
                "• Punto de montaje"
            )
            return
        
        # Validar campos
        from utils.validaciones import validar_ip, validar_punto_montaje
        
        valida_ip, msg_ip = validar_ip(ip)
        if not valida_ip:
            messagebox.showerror("Error", msg_ip)
            return
        
        valido_pm, msg_pm = validar_punto_montaje(punto_montaje)
        if not valido_pm:
            messagebox.showerror("Error", msg_pm)
            return
        
        # Configurar cliente
        self.cliente_nfs.punto_montaje = punto_montaje
        
        # Montar
        self._actualizar_texto_cliente("Montando recurso...\n")
        resultado = self.cliente_nfs.montar_recurso(ip, ruta_remota)
        
        self._actualizar_texto_cliente(resultado['message'])
        
        if resultado['success']:
            self.recurso_montado = True
            self.label_estado_montaje.config(
                text="{0} MONTADO en: {1}".format(Iconos.MONTADO, punto_montaje),
                bg=TemaColores.COLOR_MONTADO
            )
            
            # Crear instancia de transferencia
            from transferencia import TransferenciaNFS
            transferencia = TransferenciaNFS(punto_montaje)
            self.set_transferencia(transferencia)
            
            self.actualizar_barra_estado("Recurso montado correctamente", 'exito')
            logger.exito("Recurso montado: {0}:{1} en {2}".format(ip, ruta_remota, punto_montaje))
            
            # Mostrar contenido automáticamente
            self._ver_contenido_remoto()
        else:
            self.actualizar_barra_estado("Error al montar recurso", 'error')
            logger.error("Error montando recurso: {0}".format(resultado['message']))
    
    def _desmontar_recurso(self):
        """
        Desmonta el recurso NFS
        """
        if not self.recurso_montado:
            messagebox.showinfo("Información", "No hay ningún recurso montado")
            return
        
        if not messagebox.askyesno(
            "Confirmar Desmontaje",
            "¿Está seguro de desmontar el recurso?\n\n" +
            "Asegúrese de no tener archivos abiertos o procesos usando el recurso."
        ):
            return
        
        resultado = self.cliente_nfs.desmontar_recurso()
        self._actualizar_texto_cliente(resultado['message'])
        
        if resultado['success']:
            self.recurso_montado = False
            self.label_estado_montaje.config(
                text="{0} No montado".format(Iconos.DESMONTADO),
                bg=TemaColores.COLOR_DESMONTADO
            )
            
            # Limpiar transferencia
            self.set_transferencia(None)
            
            self.actualizar_barra_estado("Recurso desmontado", 'info')
            logger.info("Recurso desmontado correctamente")
        else:
            self.actualizar_barra_estado("Error al desmontar", 'error')
    
    def _ver_contenido_remoto(self):
        """
        Ver contenido del recurso montado
        """
        if not self.recurso_montado:
            messagebox.showwarning(
                "Advertencia",
                "Primero debe montar un recurso NFS"
            )
            return
        
        resultado = self.cliente_nfs.listar_contenido()
        
        if resultado['success'] and 'data' in resultado:
            contenido = resultado['message'] + "\n\n" + resultado['data']
            self._actualizar_texto_cliente(contenido)
        else:
            self._actualizar_texto_cliente(resultado['message'])
    
    def _verificar_conexion(self):
        """
        Verifica la conexión con el servidor
        """
        ip = self.entrada_ip_cliente.get().strip()
        
        if not ip:
            messagebox.showwarning("Advertencia", "Ingrese una IP para verificar")
            return
        
        import subprocess
        
        self._actualizar_texto_cliente("Verificando conexión con {0}...\n".format(ip))
        
        try:
            # Ping
            resultado = subprocess.run(
                ["ping", "-c", "3", ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=10
            )
            
            if resultado.returncode == 0:
                mensaje = "[OK] El servidor {0} está accesible\n\n".format(ip)
                mensaje += "Respuesta de ping:\n"
                mensaje += resultado.stdout
                self._actualizar_texto_cliente(mensaje)
            else:
                mensaje = "[ERROR] No se puede alcanzar el servidor {0}\n\n".format(ip)
                mensaje += "Verifique:\n"
                mensaje += "• La IP es correcta\n"
                mensaje += "• El servidor está encendido\n"
                mensaje += "• No hay firewall bloqueando\n"
                mensaje += "• Están en la misma red\n"
                self._actualizar_texto_cliente(mensaje)
        except subprocess.TimeoutExpired:
            self._actualizar_texto_cliente(
                "[ERROR] Timeout al intentar conectar con {0}\n".format(ip)
            )
        except Exception as e:
            self._actualizar_texto_cliente(
                "[ERROR] Error verificando conexión: {0}\n".format(str(e))
            )
    
    def _actualizar_texto_cliente(self, texto):
        """
        Actualiza el texto del cliente con colores
        """
        self.texto_cliente.config(state='normal')
        self.texto_cliente.delete('1.0', tk.END)
        self.texto_cliente.insert('1.0', texto)
        
        # Aplicar colores según el contenido
        contenido = self.texto_cliente.get('1.0', tk.END)
        
        # Buscar y colorear líneas con marcadores
        for i, linea in enumerate(contenido.split('\n'), 1):
            if '[OK]' in linea or '[ÉXITO]' in linea or '[EXITO]' in linea:
                self.texto_cliente.tag_add('exito', '{0}.0'.format(i), '{0}.end'.format(i))
            elif '[ERROR]' in linea or '[FALLO]' in linea:
                self.texto_cliente.tag_add('error', '{0}.0'.format(i), '{0}.end'.format(i))
            elif '[WARNING]' in linea or '[ADVERTENCIA]' in linea:
                self.texto_cliente.tag_add('warning', '{0}.0'.format(i), '{0}.end'.format(i))
            elif '[INFO]' in linea:
                self.texto_cliente.tag_add('info', '{0}.0'.format(i), '{0}.end'.format(i))
        
        self.texto_cliente.config(state='disabled')
        self.texto_cliente.see(tk.END)