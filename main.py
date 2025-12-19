#!/usr/bin/env python3
"""
Configurador Integral NFS para OpenSUSE - Versión Unificada
Combina lo mejor de ambos repositorios (diegootm + anistopera)

Características:
- Configuración completa de servidor NFS
- Cliente NFS con montaje de recursos
- Transferencia bidireccional de archivos y directorios
- Interfaz gráfica moderna y rápida
- Validaciones robustas
- Sistema de logs

Autor: Versión Unificada
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Agregar ruta de módulos locales
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.compatibilidad import (
    verificar_compatibilidad,
    verificar_permisos_administrador,
    relanzar_con_sudo,
    verificar_nfs_instalado,
    verificar_nfs_server_activo,
    obtener_info_sistema
)
from utils.logger import logger


def mostrar_info_inicio():
    """
    Muestra información del sistema al inicio
    """
    print("=" * 70)
    print("  Configurador NFS Integral para OpenSUSE - Versión Unificada")
    print("=" * 70)
    print("")
    
    info = obtener_info_sistema()
    
    print("[INFO] Información del Sistema:")
    print("   Sistema Operativo: {0}".format(info.get('os', 'Desconocido')))
    print("   Python: {0}".format(info.get('python', 'Desconocido')))
    print("   Ejecutando como root: {0}".format("Sí" if info.get('es_root') else "No"))
    print("   NFS instalado: {0}".format("Sí" if info.get('nfs_instalado') else "No"))
    print("   Servicio NFS activo: {0}".format("Sí" if info.get('nfs_activo') else "No"))
    print("")


def verificar_requisitos():
    """
    Verifica que se cumplan todos los requisitos
    """
    print("[*] Verificando requisitos del sistema...")
    print("")
    
    # 1. Verificar compatibilidad básica
    if not verificar_compatibilidad():
        print("[ER] El sistema no cumple con los requisitos mínimos")
        return False
    
    # 2. Verificar permisos de root
    if not verificar_permisos_administrador():
        print("")
        print("[!] ADVERTENCIA: No se está ejecutando como root")
        print("   Algunas funcionalidades estarán limitadas:")
        print("   • No se podrá modificar /etc/exports")
        print("   • No se podrán montar recursos NFS")
        print("   • No se podrán ajustar permisos del sistema")
        print("")
        print("   Para funcionalidad completa, ejecute:")
        print("   sudo python3 main.py")
        print("")
        
        # Preguntar si desea continuar
        respuesta = input("¿Desea continuar de todos modos? (s/N): ")
        if respuesta.lower() != 's':
            print("Operación cancelada por el usuario")
            return False
    
    # 3. Verificar NFS instalado
    if not verificar_nfs_instalado():
        print("[ER] NFS no está instalado en el sistema")
        print("")
        print("Para instalar NFS en OpenSUSE, ejecute:")
        print("  sudo zypper install nfs-kernel-server")
        print("  sudo systemctl enable nfs-server")
        print("  sudo systemctl start nfs-server")
        print("")
        return False
    
    print("[OK] Todos los requisitos básicos cumplidos")
    print("")
    return True


def main():
    """
    Función principal de la aplicación
    """
    try:
        # Mostrar información del sistema
        mostrar_info_inicio()
        
        # Verificar requisitos
        if not verificar_requisitos():
            sys.exit(1)
        
        # Log de inicio
        logger.info("=" * 50)
        logger.info("Iniciando Configurador NFS Unificado")
        logger.info("=" * 50)
        
        # Importar e inicializar la interfaz gráfica
        from ui.ventana_principal import VentanaPrincipal
        
        print("[*] Iniciando interfaz gráfica...")
        print("")
        
        # Crear ventana principal
        root = tk.Tk()
        
        # Configurar geometría
        root.geometry("1100x800")
        
        # Centrar ventana
        try:
            root.eval('tk::PlaceWindow . center')
        except:
            root.update_idletasks()
            ancho = root.winfo_width()
            alto = root.winfo_height()
            x = (root.winfo_screenwidth() // 2) - (ancho // 2)
            y = (root.winfo_screenheight() // 2) - (alto // 2)
            root.geometry('{0}x{1}+{2}+{3}'.format(ancho, alto, x, y))
        
        # Crear aplicación
        app = VentanaPrincipal(root)
        
        print("[OK] Interfaz gráfica cargada correctamente")
        print("")
        print("=" * 70)
        print("  Aplicación iniciada - Listo para usar")
        print("=" * 70)
        print("")
        
        logger.info("Interfaz gráfica iniciada correctamente")
        
        # Iniciar loop de eventos
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n\n[!] Programa interrumpido por el usuario")
        logger.info("Programa interrumpido por el usuario")
        sys.exit(0)
    
    except Exception as e:
        print("\n\n[ER] Error fatal: {0}".format(e))
        logger.error("Error fatal: {0}".format(e))
        
        import traceback
        traceback.print_exc()
        
        sys.exit(1)


if __name__ == "__main__":
    main()