"""
Módulo de compatibilidad del sistema
Verifica requisitos y compatibilidad con OpenSUSE
"""
import sys
import os
import platform
import subprocess


def verificar_python_version():
    """
    Verifica que la versión de Python sea >= 3.6
    """
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("ERROR: Se requiere Python 3.6 o superior")
        print("Versión actual: Python {0}.{1}.{2}".format(
            version.major, version.minor, version.micro
        ))
        return False
    return True


def verificar_tkinter():
    """
    Verifica que Tkinter esté disponible
    """
    try:
        import tkinter
        return True
    except ImportError:
        print("ERROR: Tkinter no está instalado")
        print("Instale con: sudo zypper install python3-tk")
        return False


def verificar_sistema_operativo():
    """
    Verifica el sistema operativo
    Retorna información del SO
    """
    sistema = platform.system()
    distribucion = ""
    
    if sistema == "Linux":
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", 'r') as f:
                    for linea in f:
                        if linea.startswith("PRETTY_NAME="):
                            distribucion = linea.split('=')[1].strip().strip('"')
                            break
        except:
            distribucion = "Linux (desconocido)"
    
    return {
        'sistema': sistema,
        'distribucion': distribucion,
        'arquitectura': platform.machine(),
        'python': platform.python_version()
    }


def verificar_compatibilidad():
    """
    Verifica todos los requisitos de compatibilidad
    Retorna True si el sistema es compatible
    """
    print("Verificando compatibilidad del sistema...")
    
    # Verificar Python
    if not verificar_python_version():
        return False
    print("[OK] Python versión correcta")
    
    # Verificar Tkinter
    if not verificar_tkinter():
        return False
    print("[OK] Tkinter disponible")
    
    return True


def verificar_permisos_administrador():
    """
    Verifica si se está ejecutando como root/administrador
    """
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows u otro sistema sin geteuid
        return False


def relanzar_con_sudo():
    """
    Intenta relanzar el script con sudo
    """
    try:
        args = ['sudo', 'python3'] + sys.argv
        os.execvp('sudo', args)
    except Exception as e:
        print("No se pudo relanzar con sudo: {0}".format(e))
        return False


def verificar_nfs_instalado():
    """
    Verifica si NFS está instalado en el sistema
    """
    try:
        # Verificar si existe el comando exportfs
        resultado = subprocess.run(
            ['which', 'exportfs'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        
        if resultado.returncode == 0:
            return True
        
        # Verificar paquetes instalados
        resultado = subprocess.run(
            ['rpm', '-q', 'nfs-kernel-server'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        
        if resultado.returncode == 0:
            return True
            
        return False
        
    except Exception:
        return False


def verificar_nfs_server_activo():
    """
    Verifica si el servicio NFS está activo
    """
    try:
        resultado = subprocess.run(
            ['systemctl', 'is-active', 'nfs-server'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        
        return resultado.returncode == 0
        
    except Exception:
        return False


def obtener_info_sistema():
    """
    Obtiene información completa del sistema
    """
    info_so = verificar_sistema_operativo()
    
    return {
        'os': info_so.get('distribucion', 'Desconocido'),
        'python': info_so.get('python', sys.version.split()[0]),
        'es_root': verificar_permisos_administrador(),
        'nfs_instalado': verificar_nfs_instalado(),
        'nfs_activo': verificar_nfs_server_activo(),
        'arquitectura': info_so.get('arquitectura', 'Desconocido')
    }


def verificar_permisos_escritura(ruta):
    """
    Verifica si se tienen permisos de escritura en una ruta
    """
    try:
        if os.path.exists(ruta):
            return os.access(ruta, os.W_OK)
        else:
            # Si no existe, verificar el directorio padre
            directorio_padre = os.path.dirname(ruta)
            return os.access(directorio_padre, os.W_OK)
    except Exception:
        return False


def verificar_comando_disponible(comando):
    """
    Verifica si un comando está disponible en el sistema
    """
    try:
        resultado = subprocess.run(
            ['which', comando],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return resultado.returncode == 0
    except Exception:
        return False