"""
Cliente NFS
Basado en anistopera con mejoras
"""
import os
import subprocess

from utils.validaciones import validar_ip, validar_punto_montaje
from utils.logger import logger


class ClienteNFS:
    """
    Clase que maneja la lógica del cliente NFS
    Valida, monta, comparte archivos y lista el contenido
    """
    
    def __init__(self, punto_montaje=""):
        self.punto_montaje = punto_montaje
        self.es_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        logger.info("ClienteNFS inicializado")

    def _run_command(self, command):
        """
        Ejecuta un comando en el sistema y devuelve el resultado
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

    def montar_recurso(self, ip_master, ruta_remota):
        """
        Crea el punto de montaje y monta el recurso NFS
        Versión mejorada con mejor manejo de errores y compatibilidad con OpenSUSE 15.6
        """
        if not self.punto_montaje:
            logger.error("El punto de montaje está vacío")
            return {"success": False, "message": "[ERROR] El punto de montaje no puede estar vacío"}
        
        # Validar IP
        valida_ip, mensaje_ip = validar_ip(ip_master)
        if not valida_ip:
            logger.error("IP inválida: {0}".format(ip_master))
            return {"success": False, "message": "[ERROR] {0}".format(mensaje_ip)}
        
        # Validar punto de montaje
        valido_pm, mensaje_pm = validar_punto_montaje(self.punto_montaje)
        if not valido_pm:
            logger.error("Punto de montaje inválido: {0}".format(mensaje_pm))
            return {"success": False, "message": "[ERROR] {0}".format(mensaje_pm)}
        
        # Crear directorio si no existe (usando Python en lugar de comando del sistema)
        if not os.path.exists(self.punto_montaje):
            try:
                os.makedirs(self.punto_montaje)
                logger.info("Punto de montaje creado: {0}".format(self.punto_montaje))
            except Exception as e:
                logger.error("Error creando punto de montaje: {0}".format(str(e)))
                return {"success": False, "message": "[ERROR] No se pudo crear el punto de montaje: {0}".format(str(e))}
        
        # Verificar si ya está montado
        if os.path.ismount(self.punto_montaje):
            logger.info("El recurso ya estaba montado en {0}".format(self.punto_montaje))
            return {"success": True, "message": "[OK] El recurso ya estaba montado en {0}".format(self.punto_montaje)}
        
        # Primero intentar con versión 3 (más compatible)
        mount_command = "mount -t nfs -o vers=3 {0}:{1} {2}".format(ip_master, ruta_remota, self.punto_montaje)
        mount_result = self._run_command(mount_command)

        # Si falla con vers=3, intentar sin especificar versión
        if not mount_result["success"]:
            logger.info("Reintentando montaje sin especificar versión de NFS")
            mount_command = "mount -t nfs {0}:{1} {2}".format(ip_master, ruta_remota, self.punto_montaje)
            mount_result = self._run_command(mount_command)

        if not mount_result["success"]:
            stderr = mount_result["stderr"].lower()
            if "connection refused" in stderr or "no route" in stderr or "unreachable" in stderr:
                logger.error("IP inaccesible o servidor NFS no disponible: {0}".format(ip_master))
                return {"success": False, "message": "[ERROR] IP inaccesible o servidor NFS no disponible ({0}). Verifique que el servidor esté activo y accesible.".format(ip_master)}
            elif "permission denied" in stderr or "access denied" in stderr:
                logger.error("Acceso denegado por el servidor NFS")
                return {"success": False, "message": "[ERROR] Acceso denegado por el servidor NFS. Verifique los permisos en el servidor."}
            elif "operation not permitted" in stderr:
                logger.error("Operación no permitida - Verifique que sea root")
                return {"success": False, "message": "[ERROR] Operación no permitida. Requiere permisos de root."}
            elif "already mounted" in stderr or "busy" in stderr:
                # Puede estar montado en otro lugar
                logger.warning("Recurso ya montado o punto ocupado")
                return {"success": False, "message": "[ERROR] El recurso ya está montado o el punto está en uso."}
            else:
                logger.error("Error al montar: {0}".format(mount_result['stderr']))
                return {"success": False, "message": "[ERROR] Al montar el recurso: {0}".format(mount_result['stderr'])}

        logger.exito("Recurso montado en {0}".format(self.punto_montaje))
        return {"success": True, "message": "[OK] Recurso montado con éxito en {0}".format(self.punto_montaje)}

    def desmontar_recurso(self):
        """
        Desmonta el recurso NFS del sistema
        """
        if not os.path.ismount(self.punto_montaje):
            logger.info("El recurso no estaba montado")
            return {"success": True, "message": "[INFO] El recurso no estaba montado"}

        umount_result = self._run_command("umount {0}".format(self.punto_montaje))
        if umount_result["success"]:
            logger.exito("Recurso desmontado")
            return {"success": True, "message": "[OK] Recurso desmontado con éxito"}
        else:
            stderr = umount_result['stderr'].lower()
            if "target is busy" in stderr or "device is busy" in stderr:
                logger.error("No se pudo desmontar: recurso en uso")
                return {"success": False, "message": "[ERROR] No se pudo desmontar: el recurso está en uso"}
            logger.error("Error al desmontar: {0}".format(umount_result['stderr']))
            return {"success": False, "message": "[ERROR] Al desmontar: {0}".format(umount_result['stderr'])}

    def listar_contenido(self):
        """
        Lista el contenido del punto de montaje
        """
        if not os.path.ismount(self.punto_montaje):
            logger.error("El recurso no está montado")
            return {"success": False, "message": "[ERROR] El recurso no está montado"}
        
        list_result = self._run_command("ls -lA {0}".format(self.punto_montaje))
        if list_result["success"]:
            logger.info("Contenido listado correctamente")
            return {"success": True, "message": "[INFO] Contenido del recurso compartido:", "data": list_result["stdout"]}
        else:
            logger.error("Error al listar: {0}".format(list_result['stderr']))
            return {"success": False, "message": "[ERROR] Al listar el contenido: {0}".format(list_result['stderr'])}

    def obtener_archivos_disponibles(self):
        """
        Obtiene la lista de archivos y directorios disponibles en el punto de montaje
        """
        if not os.path.ismount(self.punto_montaje):
            return {"success": False, "message": "[ERROR] El recurso no está montado", "archivos": []}
        
        try:
            archivos = os.listdir(self.punto_montaje)
            logger.info("Se listaron {0} archivos disponibles".format(len(archivos)))
            return {"success": True, "message": "[OK] Archivos listados", "archivos": archivos}
        except Exception as e:
            logger.error("Error obteniendo archivos: {0}".format(str(e)))
            return {"success": False, "message": "[ERROR] {0}".format(str(e)), "archivos": []}