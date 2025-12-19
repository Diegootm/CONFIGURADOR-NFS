"""
Gestor NFS - Servidor
Basado en diegootm con mejoras de ambos repositorios
"""
import os
import shutil
import subprocess
import stat
import hashlib
from datetime import datetime

from utils.validaciones import validar_ruta, validar_red, validar_opciones_nfs
from utils.logger import logger


class GestorNFS:
    """
    Clase para gestionar /etc/exports de forma completa y segura
    Incluye gestión automática de permisos del sistema de archivos
    Soporta exportación de archivos individuales con fsid automático
    """

    def __init__(self, ruta_exports="/etc/exports"):
        self.ruta_exports = ruta_exports
        self.ruta_respaldo = "{0}.respaldo".format(ruta_exports)
        self.es_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        
        # Opciones NFS con sus descripciones
        self.opciones_info = {
            'ro': 'Solo lectura - Los clientes pueden leer pero no modificar',
            'rw': 'Lectura/Escritura - Los clientes pueden leer y modificar archivos',
            'sync': 'Sincronización - Cambios se escriben inmediatamente al disco',
            'async': 'Asíncrono - Mejora rendimiento pero menos seguro',
            'no_root_squash': 'Root remoto tiene privilegios de root',
            'root_squash': 'Root remoto se mapea a usuario anónimo (más seguro)',
            'all_squash': 'Todos los usuarios remotos se mapean a anónimo',
            'no_all_squash': 'Usuarios remotos mantienen sus IDs',
            'no_subtree_check': 'Desactiva verificación de subdirectorios (más rápido)',
            'subtree_check': 'Verifica permisos en subdirectorios (más seguro)',
            'insecure': 'Permite conexiones desde puertos > 1024',
            'secure': 'Solo permite conexiones desde puertos < 1024 (más seguro)',
            'no_secure': 'Alias de insecure - Permite puertos > 1024',
            'anonuid': 'UID del usuario anónimo (ejemplo: anonuid=1000)',
            'anongid': 'GID del grupo anónimo (ejemplo: anongid=1000)',
            'fsid': 'ID único del filesystem (requerido para archivos)'
        }
        
        self.opciones_validas = set(self.opciones_info.keys())
        
        logger.info("GestorNFS inicializado")

    def _run_command(self, command):
        """
        Ejecuta un comando del sistema
        """
        try:
            if not self.es_root and not command.startswith("sudo"):
                command = "sudo {0}".format(command)
            
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"success": False, "stdout": e.stdout, "stderr": e.stderr}

    def obtener_descripcion_opcion(self, opcion):
        """Retorna la descripción de una opción NFS"""
        return self.opciones_info.get(opcion, "Sin descripción disponible")

    def obtener_opciones_con_descripciones(self):
        """Retorna un diccionario con opciones y sus descripciones"""
        return self.opciones_info.copy()

    def generar_fsid_desde_ruta(self, ruta):
        """
        Genera un fsid único basado en la ruta del archivo
        Retorna un número entre 1 y 9999
        """
        hash_obj = hashlib.md5(ruta.encode())
        hash_hex = hash_obj.hexdigest()
        numero = int(hash_hex[:4], 16) % 9999 + 1
        return numero

    def obtener_fsids_usados(self):
        """
        Retorna un conjunto con todos los fsid ya usados en /etc/exports
        """
        fsids_usados = set()
        configuraciones = self.leer_configuracion_actual()
        
        for config in configuraciones:
            for opcion in config['opciones']:
                if opcion.startswith('fsid='):
                    try:
                        fsid = int(opcion.split('=')[1])
                        fsids_usados.add(fsid)
                    except ValueError:
                        pass
        
        return fsids_usados

    def verificar_y_ajustar_permisos(self, ruta, opciones):
        """
        Verifica y ajusta los permisos del sistema de archivos según las opciones NFS
        Retorna (exito, mensaje)
        """
        try:
            if not os.path.exists(ruta):
                return (False, "La ruta no existe: {0}".format(ruta))
            
            stat_info = os.stat(ruta)
            permisos_actuales = stat.filemode(stat_info.st_mode)
            
            mensajes = []
            mensajes.append("Verificando permisos de: {0}".format(ruta))
            mensajes.append("Permisos actuales: {0}".format(permisos_actuales))
            
            necesita_escritura = 'rw' in opciones
            
            if os.path.isdir(ruta):
                if necesita_escritura:
                    permisos_recomendados = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
                    modo_recomendado = "rwxr-xr-x (755)"
                else:
                    permisos_recomendados = stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
                    modo_recomendado = "r-xr-xr-x (555)"
            else:
                if necesita_escritura:
                    permisos_recomendados = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH
                    modo_recomendado = "rw-rw-rw- (666)"
                else:
                    permisos_recomendados = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
                    modo_recomendado = "r--r--r-- (444)"
            
            permisos_suficientes = (stat_info.st_mode & permisos_recomendados) == permisos_recomendados
            
            if not permisos_suficientes:
                mensajes.append("ADVERTENCIA: Los permisos actuales pueden no ser suficientes")
                mensajes.append("    Permisos recomendados: {0}".format(modo_recomendado))
                mensajes.append("")
                mensajes.append("¿Desea ajustar los permisos automáticamente?")
                mensajes.append("(Esto cambiará los permisos del sistema de archivos)")
                
                return (False, "\n".join(mensajes))
            else:
                mensajes.append("Los permisos son adecuados para la configuración NFS")
                return (True, "\n".join(mensajes))
                
        except Exception as e:
            return (False, "Error verificando permisos: {0}".format(str(e)))

    def aplicar_permisos_filesystem(self, ruta, opciones):
        """
        Aplica los permisos correctos al sistema de archivos según las opciones NFS
        Retorna (exito, mensaje)
        """
        try:
            if not os.path.exists(ruta):
                return (False, "La ruta no existe")
            
            necesita_escritura = 'rw' in opciones
            
            if os.path.isdir(ruta):
                if necesita_escritura:
                    nuevo_modo = 0o755
                    os.chmod(ruta, nuevo_modo)
                    logger.info("Permisos ajustados a 755 para: {0}".format(ruta))
                    return (True, "Permisos ajustados a 755 (rwxr-xr-x) para lectura/escritura")
                else:
                    nuevo_modo = 0o555
                    os.chmod(ruta, nuevo_modo)
                    logger.info("Permisos ajustados a 555 para: {0}".format(ruta))
                    return (True, "Permisos ajustados a 555 (r-xr-xr-x) para solo lectura")
            else:
                if necesita_escritura:
                    nuevo_modo = 0o666
                    os.chmod(ruta, nuevo_modo)
                    logger.info("Permisos ajustados a 666 para archivo: {0}".format(ruta))
                    return (True, "Permisos ajustados a 666 (rw-rw-rw-) para lectura/escritura")
                else:
                    nuevo_modo = 0o444
                    os.chmod(ruta, nuevo_modo)
                    logger.info("Permisos ajustados a 444 para archivo: {0}".format(ruta))
                    return (True, "Permisos ajustados a 444 (r--r--r--) para solo lectura")
                    
        except PermissionError:
            logger.error("No hay permisos para cambiar permisos de: {0}".format(ruta))
            return (False, "Error: Se requieren permisos de root para cambiar permisos")
        except Exception as e:
            logger.error("Error aplicando permisos: {0}".format(str(e)))
            return (False, "Error aplicando permisos: {0}".format(str(e)))

    def leer_configuracion_actual(self):
        """
        Lee /etc/exports y devuelve lista de configuraciones
        """
        configuraciones = []
        try:
            if not os.path.exists(self.ruta_exports):
                return configuraciones

            with open(self.ruta_exports, 'r') as f:
                for num, linea in enumerate(f, 1):
                    linea_raw = linea.rstrip("\n")
                    linea_strip = linea_raw.strip()
                    if not linea_strip or linea_strip.startswith('#'):
                        continue
                    
                    try:
                        idx_open = linea_raw.index('(')
                        idx_close = linea_raw.rindex(')')
                    except ValueError:
                        continue

                    antes = linea_raw[:idx_open].strip()
                    texto_opciones = linea_raw[idx_open+1:idx_close].strip()
                    partes_antes = antes.split()
                    if not partes_antes:
                        continue
                    
                    carpeta = partes_antes[0]
                    hosts = " ".join(partes_antes[1:]) if len(partes_antes) > 1 else "*"
                    opciones = [o.strip() for o in texto_opciones.split(',') if o.strip()]
                    
                    configuraciones.append({
                        'carpeta': carpeta,
                        'hosts': hosts,
                        'opciones': opciones,
                        'linea_original': linea_raw,
                        'numero_linea': num
                    })
            return configuraciones
        except Exception as e:
            logger.error("Error leyendo configuración: {0}".format(e))
            return []

    def _validar_parametros(self, carpeta, hosts, opciones):
        """
        Valida los parámetros antes de agregar configuración
        """
        if not carpeta or not hosts:
            logger.error("Carpeta y hosts son requeridos")
            return False
        
        if not isinstance(opciones, list):
            logger.error("Opciones deben ser lista")
            return False
        
        # Validar ruta
        valida, tipo, mensaje = validar_ruta(carpeta)
        if not valida:
            logger.error("Ruta inválida: {0}".format(mensaje))
            return False
        
        # Validar red/hosts
        valida_red, mensaje_red = validar_red(hosts)
        if not valida_red:
            logger.error("Hosts/Red inválida: {0}".format(mensaje_red))
            return False
        
        # Validar opciones
        valida_opts, mensaje_opts = validar_opciones_nfs(opciones)
        if not valida_opts:
            logger.error(mensaje_opts)
            return False
        
        return True

    def _formatear_linea_exports(self, carpeta, hosts, opciones):
        """
        Formatea una línea para /etc/exports
        """
        texto_opciones = ",".join(opciones)
        return "{0} {1}({2})".format(carpeta, hosts, texto_opciones)

    def _crear_respaldo(self):
        """
        Crea un respaldo de /etc/exports
        """
        try:
            if os.path.exists(self.ruta_exports):
                marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
                ruta_respaldo_timestamp = "{0}.{1}".format(self.ruta_respaldo, marca_tiempo)
                shutil.copy2(self.ruta_exports, ruta_respaldo_timestamp)
                logger.info("Respaldo creado: {0}".format(ruta_respaldo_timestamp))
        except Exception as e:
            logger.error("Error creando respaldo: {0}".format(e))

    def agregar_configuracion(self, carpeta, hosts, opciones, ajustar_permisos=False):
        """
        Agrega una nueva línea a /etc/exports
        Soporta archivos individuales agregando fsid automáticamente
        """
        try:
            if not self._validar_parametros(carpeta, hosts, opciones):
                return False
            
            # Si es un archivo, agregar fsid si no existe
            if os.path.isfile(carpeta):
                tiene_fsid = any('fsid=' in opt for opt in opciones)
                
                if not tiene_fsid:
                    fsid = self.generar_fsid_desde_ruta(carpeta)
                    fsids_usados = self.obtener_fsids_usados()
                    
                    while fsid in fsids_usados:
                        fsid = (fsid + 1) % 9999 + 1
                    
                    opciones.append('fsid={0}'.format(fsid))
                    logger.info("Archivo individual detectado - Agregando fsid={0}".format(fsid))
                
                if 'no_subtree_check' not in opciones and 'subtree_check' not in opciones:
                    opciones.append('no_subtree_check')
                    logger.info("Agregando no_subtree_check (recomendado para archivos)")
            
            # Si se solicita, ajustar permisos del filesystem
            if ajustar_permisos:
                exito, mensaje = self.aplicar_permisos_filesystem(carpeta, opciones)
                if not exito:
                    logger.warning("No se pudieron ajustar los permisos del filesystem")
            
            self._crear_respaldo()
            linea = self._formatear_linea_exports(carpeta, hosts, opciones)
            
            with open(self.ruta_exports, 'a') as f:
                f.write("\n" + linea + "\n")
            
            logger.exito("Configuración agregada: {0}".format(linea))
            return True
        except Exception as e:
            logger.error("Error agregando configuración: {0}".format(e))
            return False

    def eliminar_configuracion(self, indice):
        """
        Elimina la configuración por índice
        """
        try:
            configs = self.leer_configuracion_actual()
            if indice < 0 or indice >= len(configs):
                return False
            
            self._crear_respaldo()
            
            with open(self.ruta_exports, 'w') as f:
                for i, c in enumerate(configs):
                    if i == indice:
                        continue
                    f.write(c['linea_original'].rstrip("\n") + "\n")
            
            logger.info("Configuración {0} eliminada".format(indice))
            return True
        except Exception as e:
            logger.error("Error eliminando configuración: {0}".format(e))
            return False

    def aplicar_cambios_nfs(self):
        """
        Ejecuta 'exportfs -ra' para aplicar cambios
        """
        try:
            resultado = self._run_command("exportfs -ra")
            if resultado["success"]:
                logger.exito("Cambios NFS aplicados con exportfs -ra")
                return True
            else:
                logger.error("Error en exportfs: {0}".format(resultado["stderr"]))
                return False
        except Exception as e:
            logger.error("Error aplicando cambios NFS: {0}".format(e))
            return False

    def verificar_servicio_nfs(self):
        """
        Verifica el estado del servicio NFS
        """
        try:
            resultado = self._run_command("systemctl is-active nfs-server")
            
            if resultado["success"]:
                return (True, "Servicio NFS activo y funcionando")
            else:
                return (False, "Servicio NFS no está activo")
                
        except Exception as e:
            return (False, "No se pudo verificar el servicio NFS: {0}".format(str(e)))

    def verificar_montajes_y_disco(self):
        """
        Obtiene información de espacio en disco
        """
        resultado = self._run_command("df -h")
        if resultado["success"]:
            return {"success": True, "message": "Espacio en disco:", "data": resultado["stdout"]}
        else:
            return {"success": False, "message": "Error obteniendo información de disco"}

    def obtener_opciones_validas(self):
        """
        Retorna lista de opciones NFS válidas
        """
        return sorted(list(self.opciones_validas))