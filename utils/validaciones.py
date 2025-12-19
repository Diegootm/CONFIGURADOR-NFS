"""
Módulo de validaciones centralizadas
Combina y mejora las validaciones de ambos repositorios
"""
import os
import ipaddress
import re


def validar_ruta(ruta):
    """
    Valida que la ruta existe y es accesible
    Retorna (es_valida, tipo, mensaje)
    tipo puede ser: 'directorio', 'archivo', 'no_existe', 'sin_permisos'
    """
    if not ruta:
        return (False, None, "La ruta está vacía")
    
    ruta = ruta.strip()
    
    if not os.path.exists(ruta):
        return (False, 'no_existe', "La ruta no existe: {0}".format(ruta))
    
    if not os.access(ruta, os.R_OK):
        return (False, 'sin_permisos', "No hay permisos de lectura en: {0}".format(ruta))
    
    if os.path.isdir(ruta):
        return (True, 'directorio', "Directorio válido")
    elif os.path.isfile(ruta):
        return (True, 'archivo', "Archivo válido")
    else:
        return (False, 'desconocido', "Tipo de ruta no reconocido")


def validar_ip(ip):
    """
    Valida si el string proporcionado tiene formato de IPv4 válido
    Compatible con ambas implementaciones
    """
    if not ip or not ip.strip():
        return (False, "La dirección IP está vacía")
    
    ip = ip.strip()
    
    # Permitir wildcard
    if ip == '*':
        return (True, "Permitir acceso desde cualquier host")
    
    try:
        ipaddress.IPv4Address(ip)
        return (True, "Dirección IP válida")
    except (ipaddress.AddressValueError, ValueError):
        return (False, "Formato de IP inválido: '{0}'".format(ip))


def validar_red(hosts):
    """
    Valida que el formato de red/host sea correcto
    Acepta: IP, red CIDR, hostname, wildcard (*)
    """
    if not hosts or not hosts.strip():
        return (False, "El campo de hosts/red está vacío")
    
    hosts = hosts.strip()
    
    # Permitir wildcard
    if hosts == '*':
        return (True, "Permitir acceso desde cualquier host")
    
    # Validar formato CIDR (ej: 192.168.1.0/24)
    if '/' in hosts:
        partes = hosts.split('/')
        if len(partes) != 2:
            return (False, "Formato CIDR inválido. Use: 192.168.1.0/24")
        
        ip_parte = partes[0]
        try:
            mascara = int(partes[1])
            if mascara < 0 or mascara > 32:
                return (False, "La máscara debe estar entre 0 y 32")
        except ValueError:
            return (False, "La máscara de red debe ser un número")
        
        # Validar la parte IP
        octetos = ip_parte.split('.')
        if len(octetos) != 4:
            return (False, "La dirección IP debe tener 4 octetos")
        
        for octeto in octetos:
            try:
                num = int(octeto)
                if num < 0 or num > 255:
                    return (False, "Cada octeto debe estar entre 0 y 255")
            except ValueError:
                return (False, "Los octetos deben ser números")
        
        return (True, "Red CIDR válida")
    
    # Validar IP simple (ej: 192.168.1.100)
    octetos = hosts.split('.')
    if len(octetos) == 4:
        try:
            for octeto in octetos:
                num = int(octeto)
                if num < 0 or num > 255:
                    return (False, "Cada octeto debe estar entre 0 y 255")
            return (True, "Dirección IP válida")
        except ValueError:
            # Podría ser un hostname con puntos
            pass
    
    # Asumir que es un hostname
    if hosts.replace('-', '').replace('.', '').replace('_', '').isalnum():
        return (True, "Hostname válido")
    
    return (False, "Formato no reconocido. Use: IP, red/máscara o hostname")


def validar_opciones_nfs(opciones):
    """
    Valida que las opciones NFS sean correctas
    """
    opciones_validas = {
        'ro', 'rw', 'sync', 'async', 'no_root_squash', 'root_squash',
        'all_squash', 'no_subtree_check', 'subtree_check', 'insecure',
        'secure', 'anonuid', 'anongid', 'fsid', 'no_all_squash'
    }
    
    if not isinstance(opciones, list):
        return (False, "Las opciones deben ser una lista")
    
    for opt in opciones:
        if '=' in opt:
            clave = opt.split('=', 1)[0]
        else:
            clave = opt
        
        if clave not in opciones_validas:
            return (False, "Opción inválida: {0}".format(opt))
    
    return (True, "Opciones válidas")


def validar_permisos_root():
    """
    Verifica si se está ejecutando como root
    """
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows o plataforma sin geteuid
        return True


def validar_espacio_disco(ruta, tamano_necesario_mb=100):
    """
    Verifica si hay suficiente espacio en disco
    Retorna (tiene_espacio, espacio_disponible_mb, mensaje)
    """
    try:
        import shutil
        stat = shutil.disk_usage(ruta)
        espacio_disponible_mb = stat.free / (1024 * 1024)
        
        if espacio_disponible_mb >= tamano_necesario_mb:
            return (True, espacio_disponible_mb, 
                    "Espacio disponible: {0:.2f} MB".format(espacio_disponible_mb))
        else:
            return (False, espacio_disponible_mb,
                    "Espacio insuficiente. Disponible: {0:.2f} MB, Necesario: {1} MB".format(
                        espacio_disponible_mb, tamano_necesario_mb))
    except Exception as e:
        return (False, 0, "Error verificando espacio: {0}".format(str(e)))


def validar_punto_montaje(punto_montaje):
    """
    Valida que el punto de montaje sea válido
    """
    if not punto_montaje or not punto_montaje.strip():
        return (False, "El punto de montaje está vacío")
    
    punto_montaje = punto_montaje.strip()
    
    # Debe ser una ruta absoluta
    if not punto_montaje.startswith('/'):
        return (False, "El punto de montaje debe ser una ruta absoluta")
    
    # Si existe, debe ser un directorio
    if os.path.exists(punto_montaje) and not os.path.isdir(punto_montaje):
        return (False, "El punto de montaje existe pero no es un directorio")
    
    return (True, "Punto de montaje válido")


def sanitizar_ruta(ruta):
    """
    Limpia y normaliza una ruta
    """
    if not ruta:
        return ""
    
    ruta = ruta.strip()
    ruta = os.path.normpath(ruta)
    ruta = os.path.abspath(ruta)
    
    return ruta