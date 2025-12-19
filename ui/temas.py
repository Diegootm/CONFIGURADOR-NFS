"""
Tema personalizado y configuración de estilos para la interfaz
Versión mejorada y ampliada
"""
import tkinter as tk
from tkinter import ttk


class TemaColores:
    """
    Configuración de colores para la interfaz
    """
    
    # Colores principales
    COLOR_FONDO_PRINCIPAL = "#f0f0f0"
    COLOR_FONDO_FRAME = "#ffffff"
    COLOR_FONDO_DARK = "#2c3e50"
    COLOR_FONDO_CARD = "#ffffff"
    
    # Colores de acentos
    COLOR_PRIMARY = "#3498db"
    COLOR_SUCCESS = "#27ae60"
    COLOR_WARNING = "#f39c12"
    COLOR_DANGER = "#e74c3c"
    COLOR_INFO = "#2980b9"
    COLOR_SECONDARY = "#95a5a6"
    
    # Colores de texto
    COLOR_TEXTO = "#2c3e50"
    COLOR_TEXTO_LIGHT = "#ffffff"
    COLOR_TEXTO_SECONDARY = "#7f8c8d"
    COLOR_TEXTO_MUTED = "#95a5a6"
    
    # Colores para elementos específicos
    COLOR_BOTON_MASTER = "#e74c3c"
    COLOR_BOTON_CLIENTE = "#3498db"
    COLOR_BOTON_SUCCESS = "#27ae60"
    COLOR_BOTON_HOVER = "#2980b9"
    
    # Colores para listbox y text widgets
    COLOR_LISTBOX_BG = "#ecf0f1"
    COLOR_LISTBOX_FG = "#2c3e50"
    COLOR_LISTBOX_SELECT = "#3498db"
    
    # Colores para el área de logs
    COLOR_LOG_BG = "#2c3e50"
    COLOR_LOG_FG = "#ecf0f1"
    
    # Colores de estado
    COLOR_MONTADO = "#27ae60"
    COLOR_DESMONTADO = "#e74c3c"


def configurar_estilos():
    """
    Configura los estilos globales de ttk
    """
    style = ttk.Style()
    style.theme_use('clam')
    
    # Estilos para Notebook (pestañas)
    style.configure('TNotebook', background=TemaColores.COLOR_FONDO_PRINCIPAL)
    style.configure('TNotebook.Tab', 
                   padding=[20, 10], 
                   font=('Segoe UI', 10, 'bold'))
    style.map('TNotebook.Tab',
             background=[('selected', TemaColores.COLOR_PRIMARY)],
             foreground=[('selected', TemaColores.COLOR_TEXTO_LIGHT)])
    
    # Estilos para LabelFrame
    style.configure('TLabelframe', 
                   background=TemaColores.COLOR_FONDO_PRINCIPAL)
    style.configure('TLabelframe.Label', 
                   background=TemaColores.COLOR_FONDO_PRINCIPAL, 
                   foreground=TemaColores.COLOR_PRIMARY, 
                   font=('Segoe UI', 10, 'bold'))
    
    # Estilos para Labels
    style.configure('TLabel', 
                   background=TemaColores.COLOR_FONDO_PRINCIPAL,
                   font=('Segoe UI', 9))
    
    style.configure('Title.TLabel',
                   font=('Segoe UI', 14, 'bold'),
                   foreground=TemaColores.COLOR_PRIMARY)
    
    style.configure('Subtitle.TLabel',
                   font=('Segoe UI', 11, 'bold'),
                   foreground=TemaColores.COLOR_SECONDARY)
    
    # Estilos para Entry
    style.configure('TEntry', 
                   font=('Segoe UI', 9))
    
    # Estilos para Buttons
    style.configure('TButton',
                   font=('Segoe UI', 9))
    
    style.configure('Primary.TButton',
                   font=('Segoe UI', 10, 'bold'))
    
    style.configure('Success.TButton',
                   font=('Segoe UI', 10, 'bold'))
    
    style.configure('Warning.TButton',
                   font=('Segoe UI', 10, 'bold'))
    
    style.configure('Danger.TButton',
                   font=('Segoe UI', 10, 'bold'))
    
    # Estilos para Frame
    style.configure('TFrame',
                   background=TemaColores.COLOR_FONDO_PRINCIPAL)
    
    style.configure('Card.TFrame',
                   background=TemaColores.COLOR_FONDO_CARD,
                   relief='solid',
                   borderwidth=1)


def crear_boton(parent, text, command, tipo="primary", **kwargs):
    """
    Crea un botón estilizado
    
    tipo: 'primary', 'success', 'warning', 'danger', 'info', 'secondary'
    """
    colores = {
        'primary': TemaColores.COLOR_PRIMARY,
        'success': TemaColores.COLOR_SUCCESS,
        'warning': TemaColores.COLOR_WARNING,
        'danger': TemaColores.COLOR_DANGER,
        'info': TemaColores.COLOR_INFO,
        'secondary': TemaColores.COLOR_SECONDARY
    }
    
    color = colores.get(tipo, TemaColores.COLOR_PRIMARY)
    
    boton = tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=TemaColores.COLOR_TEXTO_LIGHT,
        font=('Segoe UI', 10, 'bold'),
        relief='flat',
        bd=0,
        padx=15,
        pady=8,
        cursor='hand2',
        **kwargs
    )
    
    # Efecto hover
    def on_enter(e):
        boton['bg'] = ajustar_brillo(color, 1.2)
    
    def on_leave(e):
        boton['bg'] = color
    
    boton.bind('<Enter>', on_enter)
    boton.bind('<Leave>', on_leave)
    
    return boton


def crear_listbox_personalizado(parent, **kwargs):
    """
    Crea un Listbox con estilos y una Scrollbar vertical asociada
    Devuelve una tupla (listbox, scrollbar) para ser empaquetada externamente
    """
    listbox = tk.Listbox(
        parent,
        bg=TemaColores.COLOR_LISTBOX_BG,
        fg=TemaColores.COLOR_LISTBOX_FG,
        selectbackground=TemaColores.COLOR_LISTBOX_SELECT,
        selectforeground=TemaColores.COLOR_TEXTO_LIGHT,
        font=('Consolas', 9),
        relief='flat',
        bd=1,
        highlightthickness=0,
        **kwargs
    )
    
    scrollbar = ttk.Scrollbar(
        parent,
        orient="vertical",
        command=listbox.yview
    )
    
    listbox.config(yscrollcommand=scrollbar.set)
    
    return listbox, scrollbar


def crear_text_widget(parent, **kwargs):
    """
    Crea un widget Text estilizado para logs o resultados
    """
    text_widget = tk.Text(
        parent,
        bg=TemaColores.COLOR_LOG_BG,
        fg=TemaColores.COLOR_LOG_FG,
        font=('Consolas', 9),
        relief='flat',
        bd=5,
        wrap='word',
        highlightthickness=0,
        **kwargs
    )
    
    # Configurar tags para colores
    text_widget.tag_config('exito', foreground='#27ae60')
    text_widget.tag_config('error', foreground='#e74c3c')
    text_widget.tag_config('warning', foreground='#f39c12')
    text_widget.tag_config('info', foreground='#3498db')
    
    return text_widget


def crear_frame_card(parent, title=None, **kwargs):
    """
    Crea un frame con estilo de tarjeta (card)
    """
    if title:
        frame = ttk.LabelFrame(
            parent,
            text=title,
            padding=15,
            **kwargs
        )
    else:
        frame = ttk.Frame(
            parent,
            style='Card.TFrame',
            padding=15,
            **kwargs
        )
    
    return frame


def ajustar_brillo(color_hex, factor):
    """
    Ajusta el brillo de un color hex
    factor > 1 = más claro, factor < 1 = más oscuro
    """
    # Convertir hex a RGB
    color_hex = color_hex.lstrip('#')
    r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    
    # Ajustar brillo
    r = min(255, int(r * factor))
    g = min(255, int(g * factor))
    b = min(255, int(b * factor))
    
    # Convertir de vuelta a hex
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def crear_separador(parent, orient='horizontal'):
    """
    Crea un separador visual
    """
    return ttk.Separator(parent, orient=orient)


def crear_label_estado(parent, text="", tipo="info"):
    """
    Crea un label para mostrar estados
    """
    colores = {
        'exito': TemaColores.COLOR_SUCCESS,
        'error': TemaColores.COLOR_DANGER,
        'warning': TemaColores.COLOR_WARNING,
        'info': TemaColores.COLOR_INFO
    }
    
    color = colores.get(tipo, TemaColores.COLOR_INFO)
    
    label = tk.Label(
        parent,
        text=text,
        bg=color,
        fg=TemaColores.COLOR_TEXTO_LIGHT,
        font=('Segoe UI', 9, 'bold'),
        padx=10,
        pady=5,
        relief='flat'
    )
    
    return label


class Iconos:
    """
    Símbolos ASCII para usar como iconos (compatible con Python 3.6 + Tcl)
    """
    EXITO = "[OK]"
    ERROR = "[ER]"
    WARNING = "[!]"
    INFO = "[i]"
    CARPETA = "[DIR]"
    ARCHIVO = "[F]"
    SERVIDOR = "[SRV]"
    CLIENTE = "[CLI]"
    COMPARTIR = "[TX]"
    RECIBIR = "[RX]"
    MONTADO = "[*]"
    DESMONTADO = "[-]"
    CONFIG = "[CFG]"
    REFRESH = "[R]"
    DELETE = "[X]"