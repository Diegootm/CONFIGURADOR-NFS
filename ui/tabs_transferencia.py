"""
Pestaña de Transferencias
Módulo independiente para transferencias bidireccionales
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from .temas import (
    TemaColores, crear_boton, crear_listbox_personalizado,
    crear_frame_card, Iconos
)
from utils.logger import logger


class TabTransferencia:
    """
    Pestaña para transferencias bidireccionales
    """
    
    def __init__(self, parent, get_transferencia, actualizar_barra_estado):
        self.parent = parent
        self.get_transferencia = get_transferencia
        self.actualizar_barra_estado = actualizar_barra_estado
        
        # Crear interfaz
        self._crear_interfaz()
        
        logger.info("TabTransferencia inicializado")
    
    def _crear_interfaz(self):
        """
        Crea la interfaz de transferencias
        """
        # Frame principal dividido en dos columnas
        frame_principal = tk.Frame(self.parent, bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        frame_principal.pack(fill='both', expand=True)
        
        # Columna izquierda: Enviar
        self._crear_seccion_enviar(frame_principal)
        
        # Columna derecha: Recibir
        self._crear_seccion_recibir(frame_principal)
    
    def _crear_seccion_enviar(self, parent):
        """
        Crea la sección para enviar archivos
        """
        frame_enviar = crear_frame_card(
            parent,
            title="{0} Enviar al Recurso NFS".format(Iconos.COMPARTIR)
        )
        frame_enviar.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Información
        ttk.Label(
            frame_enviar,
            text="Envíe archivos y carpetas al recurso NFS montado",
            foreground=TemaColores.COLOR_TEXTO_SECONDARY,
            font=('Segoe UI', 9, 'italic')
        ).pack(pady=5, anchor='w')
        
        # Botones de envío
        crear_boton(
            frame_enviar,
            "{0} Seleccionar Archivos".format(Iconos.ARCHIVO),
            self._enviar_archivos,
            tipo='primary'
        ).pack(pady=5, fill='x', padx=10)
        
        crear_boton(
            frame_enviar,
            "{0} Seleccionar Carpeta".format(Iconos.CARPETA),
            self._enviar_carpeta,
            tipo='primary'
        ).pack(pady=5, fill='x', padx=10)
        
        crear_boton(
            frame_enviar,
            "{0} Seleccionar Múltiples".format(Iconos.COMPARTIR),
            self._enviar_multiples,
            tipo='info'
        ).pack(pady=5, fill='x', padx=10)
        
        # Separador
        ttk.Separator(frame_enviar, orient='horizontal').pack(fill='x', pady=10, padx=10)
        
        # Lista de archivos enviados
        ttk.Label(
            frame_enviar,
            text="{0} Archivos enviados recientemente:".format(Iconos.EXITO),
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=5, padx=10)
        
        frame_lista_env = tk.Frame(frame_enviar, bg=TemaColores.COLOR_FONDO_CARD)
        frame_lista_env.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.lista_enviados, scroll_env = crear_listbox_personalizado(
            frame_lista_env,
            height=12
        )
        self.lista_enviados.pack(side='left', fill='both', expand=True)
        scroll_env.pack(side='right', fill='y')
        
        # Botón limpiar lista
        crear_boton(
            frame_enviar,
            "Limpiar Lista",
            lambda: self.lista_enviados.delete(0, tk.END),
            tipo='secondary'
        ).pack(pady=5, padx=10)
    
    def _crear_seccion_recibir(self, parent):
        """
        Crea la sección para recibir archivos
        """
        frame_recibir = crear_frame_card(
            parent,
            title="{0} Recibir del Recurso NFS".format(Iconos.RECIBIR)
        )
        frame_recibir.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Información
        ttk.Label(
            frame_recibir,
            text="Descargue archivos y carpetas del recurso NFS",
            foreground=TemaColores.COLOR_TEXTO_SECONDARY,
            font=('Segoe UI', 9, 'italic')
        ).pack(pady=5, anchor='w')
        
        # Botón actualizar lista
        crear_boton(
            frame_recibir,
            "{0} Actualizar Lista de Archivos".format(Iconos.REFRESH),
            self._actualizar_lista_remotos,
            tipo='info'
        ).pack(pady=5, fill='x', padx=10)
        
        # Lista de archivos remotos
        ttk.Label(
            frame_recibir,
            text="{0} Archivos disponibles (selección múltiple):".format(Iconos.CARPETA),
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=5, padx=10)
        
        frame_lista_rem = tk.Frame(frame_recibir, bg=TemaColores.COLOR_FONDO_CARD)
        frame_lista_rem.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.lista_remotos, scroll_rem = crear_listbox_personalizado(
            frame_lista_rem,
            height=10,
            selectmode='multiple'
        )
        self.lista_remotos.pack(side='left', fill='both', expand=True)
        scroll_rem.pack(side='right', fill='y')
        
        # Separador
        ttk.Separator(frame_recibir, orient='horizontal').pack(fill='x', pady=10, padx=10)
        
        # Destino local
        ttk.Label(
            frame_recibir,
            text="{0} Carpeta de destino local:".format(Iconos.CARPETA),
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=5, padx=10)
        
        frame_destino = tk.Frame(frame_recibir, bg=TemaColores.COLOR_FONDO_CARD)
        frame_destino.pack(fill='x', pady=5, padx=10)
        
        self.entrada_destino_local = ttk.Entry(frame_destino, width=30)
        self.entrada_destino_local.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entrada_destino_local.insert(0, os.path.expanduser("~/Descargas"))
        
        crear_boton(
            frame_destino,
            "...",
            self._explorar_destino,
            tipo='secondary',
            width=3
        ).pack(side='right')
        
        # Botones de recepción
        frame_botones_recibir = tk.Frame(frame_recibir, bg=TemaColores.COLOR_FONDO_CARD)
        frame_botones_recibir.pack(fill='x', pady=10, padx=10)
        
        crear_boton(
            frame_botones_recibir,
            "{0} Recibir Seleccionados".format(Iconos.RECIBIR),
            self._recibir_archivos,
            tipo='success'
        ).pack(side='left', fill='x', expand=True, padx=3)
        
        crear_boton(
            frame_botones_recibir,
            "{0} Recibir Todo".format(Iconos.RECIBIR),
            self._recibir_todo,
            tipo='warning'
        ).pack(side='left', fill='x', expand=True, padx=3)
    
    def _verificar_montaje(self):
        """
        Verifica que haya un recurso montado
        """
        transferencia = self.get_transferencia()
        
        if not transferencia:
            messagebox.showwarning(
                "Recurso No Montado",
                "Primero debe montar un recurso NFS.\n\n" +
                "Vaya a la pestaña 'Cliente NFS' y monte un recurso."
            )
            return False
        
        valido, mensaje = transferencia.validar_montaje()
        if not valido:
            messagebox.showerror("Error", mensaje)
            return False
        
        return True
    
    def _enviar_archivos(self):
        """
        Envía archivos seleccionados
        """
        if not self._verificar_montaje():
            return
        
        archivos = filedialog.askopenfilenames(
            title="Seleccione archivos para enviar al recurso NFS",
            initialdir=os.path.expanduser("~")
        )
        
        if not archivos:
            return
        
        transferencia = self.get_transferencia()
        exitos = 0
        fallos = 0
        
        for archivo in archivos:
            resultado = transferencia.enviar_archivo(archivo)
            
            if resultado['success']:
                exitos += 1
                nombre = os.path.basename(archivo)
                self.lista_enviados.insert(
                    0,
                    "{0} {1}".format(Iconos.ARCHIVO, nombre)
                )
                logger.info("Archivo enviado: {0}".format(nombre))
            else:
                fallos += 1
                logger.error("Error enviando: {0}".format(archivo))
        
        if exitos > 0:
            messagebox.showinfo(
                "Envío Completado",
                "Archivos enviados: {0}\n" +
                "Archivos fallidos: {1}".format(exitos, fallos)
            )
            self.actualizar_barra_estado(
                "{0} archivos enviados".format(exitos),
                'exito'
            )
        else:
            messagebox.showerror("Error", "No se pudo enviar ningún archivo")
    
    def _enviar_carpeta(self):
        """
        Envía una carpeta completa
        """
        if not self._verificar_montaje():
            return
        
        carpeta = filedialog.askdirectory(
            title="Seleccione carpeta para enviar al recurso NFS",
            initialdir=os.path.expanduser("~")
        )
        
        if not carpeta:
            return
        
        # Confirmar
        if not messagebox.askyesno(
            "Confirmar Envío",
            "¿Desea enviar toda la carpeta y su contenido?\n\n" +
            "Carpeta: {0}".format(os.path.basename(carpeta))
        ):
            return
        
        transferencia = self.get_transferencia()
        resultado = transferencia.enviar_directorio(carpeta)
        
        if resultado['success']:
            nombre = os.path.basename(carpeta)
            self.lista_enviados.insert(
                0,
                "{0} {1} (carpeta)".format(Iconos.CARPETA, nombre)
            )
            messagebox.showinfo("Éxito", resultado['message'])
            self.actualizar_barra_estado("Carpeta enviada", 'exito')
            logger.exito("Carpeta enviada: {0}".format(nombre))
        else:
            messagebox.showerror("Error", resultado['message'])
    
    def _enviar_multiples(self):
        """
        Permite seleccionar múltiples archivos y carpetas
        """
        if not self._verificar_montaje():
            return
        
        # Ventana de selección
        ventana = tk.Toplevel(self.parent)
        ventana.title("Selección Múltiple")
        ventana.geometry("500x400")
        ventana.configure(bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        
        ttk.Label(
            ventana,
            text="Agregue archivos y carpetas para enviar:",
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=10)
        
        # Lista de items a enviar
        frame_lista = tk.Frame(ventana, bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)
        
        lista_items, scroll = crear_listbox_personalizado(frame_lista, height=10)
        lista_items.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        
        items_a_enviar = []
        
        def agregar_archivo():
            archivos = filedialog.askopenfilenames(title="Agregar archivos")
            for archivo in archivos:
                if archivo not in items_a_enviar:
                    items_a_enviar.append(archivo)
                    lista_items.insert(tk.END, "{0} {1}".format(
                        Iconos.ARCHIVO, os.path.basename(archivo)
                    ))
        
        def agregar_carpeta():
            carpeta = filedialog.askdirectory(title="Agregar carpeta")
            if carpeta and carpeta not in items_a_enviar:
                items_a_enviar.append(carpeta)
                lista_items.insert(tk.END, "{0} {1}".format(
                    Iconos.CARPETA, os.path.basename(carpeta)
                ))
        
        def quitar_seleccionado():
            sel = lista_items.curselection()
            if sel:
                idx = sel[0]
                del items_a_enviar[idx]
                lista_items.delete(idx)
        
        def enviar_todo():
            if not items_a_enviar:
                messagebox.showwarning("Advertencia", "No hay items para enviar")
                return
            
            transferencia = self.get_transferencia()
            resultado = transferencia.enviar_multiples(items_a_enviar)
            
            messagebox.showinfo("Resultado", resultado['message'])
            
            # Actualizar lista de enviados
            for item in items_a_enviar:
                nombre = os.path.basename(item)
                icono = Iconos.CARPETA if os.path.isdir(item) else Iconos.ARCHIVO
                self.lista_enviados.insert(0, "{0} {1}".format(icono, nombre))
            
            ventana.destroy()
            self.actualizar_barra_estado("Envío múltiple completado", 'exito')
        
        # Botones
        frame_botones = tk.Frame(ventana, bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        frame_botones.pack(pady=10)
        
        crear_boton(frame_botones, "Agregar Archivos", agregar_archivo, tipo='primary').pack(side='left', padx=3)
        crear_boton(frame_botones, "Agregar Carpeta", agregar_carpeta, tipo='primary').pack(side='left', padx=3)
        crear_boton(frame_botones, "Quitar", quitar_seleccionado, tipo='danger').pack(side='left', padx=3)
        crear_boton(frame_botones, "Enviar Todo", enviar_todo, tipo='success').pack(side='left', padx=3)
        crear_boton(frame_botones, "Cancelar", ventana.destroy, tipo='secondary').pack(side='left', padx=3)
    
    def _actualizar_lista_remotos(self):
        """
        Actualiza la lista de archivos remotos
        """
        if not self._verificar_montaje():
            return
        
        transferencia = self.get_transferencia()
        resultado = transferencia.listar_remoto()
        
        if resultado['success']:
            self.lista_remotos.delete(0, tk.END)
            
            if not resultado['items']:
                self.lista_remotos.insert(tk.END, "El recurso está vacío")
            else:
                for item in resultado['items']:
                    icono = Iconos.CARPETA if item['tipo'] == 'directorio' else Iconos.ARCHIVO
                    tamano = ""
                    if item['tipo'] == 'archivo' and item['tamano'] > 0:
                        if item['tamano'] < 1024:
                            tamano = " ({0} B)".format(item['tamano'])
                        elif item['tamano'] < 1024*1024:
                            tamano = " ({0:.1f} KB)".format(item['tamano']/1024)
                        else:
                            tamano = " ({0:.1f} MB)".format(item['tamano']/(1024*1024))
                    
                    texto = "{0} {1}{2}".format(icono, item['nombre'], tamano)
                    self.lista_remotos.insert(tk.END, texto)
            
            self.actualizar_barra_estado(
                "{0} items disponibles".format(len(resultado['items'])),
                'info'
            )
            logger.info("Lista remota actualizada: {0} items".format(len(resultado['items'])))
        else:
            messagebox.showerror("Error", resultado['message'])
    
    def _explorar_destino(self):
        """
        Explora carpeta de destino
        """
        destino = filedialog.askdirectory(
            title="Seleccione carpeta de destino",
            initialdir=self.entrada_destino_local.get()
        )
        
        if destino:
            self.entrada_destino_local.delete(0, tk.END)
            self.entrada_destino_local.insert(0, destino)
    
    def _recibir_archivos(self):
        """
        Recibe los archivos seleccionados
        """
        if not self._verificar_montaje():
            return
        
        seleccion = self.lista_remotos.curselection()
        if not seleccion:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione uno o más archivos para recibir.\n\n" +
                "Use Ctrl+clic para selección múltiple"
            )
            return
        
        # Obtener nombres (quitando iconos y tamaños)
        nombres = []
        for idx in seleccion:
            texto = self.lista_remotos.get(idx)
            # Extraer solo el nombre (después del icono y antes del tamaño)
            partes = texto.split(' ')
            if len(partes) >= 2:
                # Quitar icono (primer elemento) y posible tamaño (entre paréntesis)
                nombre = ' '.join([p for p in partes[1:] if not p.startswith('(')])
                nombres.append(nombre.strip())
        
        destino = self.entrada_destino_local.get().strip()
        
        if not destino or not os.path.exists(destino):
            messagebox.showerror(
                "Error",
                "La carpeta de destino no existe o no es válida"
            )
            return
        
        # Confirmar
        if not messagebox.askyesno(
            "Confirmar Recepción",
            "¿Desea recibir {0} archivo(s) en:\n{1}?".format(len(nombres), destino)
        ):
            return
        
        transferencia = self.get_transferencia()
        resultado = transferencia.recibir_multiples(nombres, destino)
        
        if resultado['success']:
            messagebox.showinfo("Éxito", resultado['message'])
            self.actualizar_barra_estado("Archivos recibidos", 'exito')
            logger.exito("Recibidos {0} archivos".format(len(nombres)))
        else:
            messagebox.showerror("Error", resultado['message'])
    
    def _recibir_todo(self):
        """
        Recibe todo el contenido del recurso
        """
        if not self._verificar_montaje():
            return
        
        # Contar items
        total = self.lista_remotos.size()
        if total == 0:
            messagebox.showinfo("Información", "No hay archivos para recibir")
            return
        
        destino = self.entrada_destino_local.get().strip()
        
        if not destino or not os.path.exists(destino):
            messagebox.showerror("Error", "Carpeta de destino inválida")
            return
        
        # Confirmar
        if not messagebox.askyesno(
            "Confirmar Recepción Total",
            "¿Desea recibir TODOS los archivos ({0}) en:\n{1}?\n\n" +
            "Esto puede tomar tiempo si hay muchos archivos.".format(total, destino)
        ):
            return
        
        # Obtener todos los nombres
        nombres = []
        for i in range(total):
            texto = self.lista_remotos.get(i)
            partes = texto.split(' ')
            if len(partes) >= 2:
                nombre = ' '.join([p for p in partes[1:] if not p.startswith('(')])
                nombres.append(nombre.strip())
        
        transferencia = self.get_transferencia()
        resultado = transferencia.recibir_multiples(nombres, destino)
        
        if resultado['success']:
            messagebox.showinfo("Éxito", resultado['message'])
            self.actualizar_barra_estado("Recepción total completada", 'exito')
        else:
            messagebox.showerror("Error", resultado['message'])