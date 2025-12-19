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
        
        # Crear directorio si no existe
        if not os.path.exists(self.punto_montaje):
            create_dir_result = self._run_command("mkdir -p {0}".format(self.punto_montaje))
            if not create_dir_result["success"]:
                logger.error("Error creando punto de montaje: {0}".format(create_dir_result['stderr']))
                return {"success": False, "message": "[ERROR] Al crear punto de montaje: {0}".format(create_dir_result['stderr'])}
        
        # Verificar si ya está montado
        if os.path.ismount(self.punto_montaje):
            logger.info("El recurso ya estaba montado en {0}".format(self.punto_montaje))
            return {"success": True, "message": "[INFO] El recurso ya estaba montado en {0}".format(self.punto_montaje)}
        
        # Montar el recurso
        mount_command = "mount -t nfs {0}:{1} {2}".format(ip_master, ruta_remota, self.punto_montaje)
        mount_result = self._run_command(mount_command)

        if not mount_result["success"]:
            stderr = mount_result["stderr"].lower()
            if "connection refused" in stderr or "no route" in stderr:
                logger.error("IP inaccesible o servidor NFS no disponible: {0}".format(ip_master))
                return {"success": False, "message": "[ERROR] IP inaccesible o servidor NFS no disponible ({0})".format(ip_master)}
            elif "permission denied" in stderr or "access denied" in stderr:
                logger.error("Acceso denegado por el servidor NFS")
                return {"success": False, "message": "[ERROR] Acceso denegado por el servidor NFS"}
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

    def compartir_archivos(self, archivos_a_copiar):
        """
        Copia una lista de archivos al punto de montaje
        """
        if not os.path.ismount(self.punto_montaje):
            logger.error("El recurso no está montado")
            return {"success": False, "message": "[ERROR] El recurso no está montado. Monta el recurso primero"}

        exitos = 0
        fallos = 0
        archivos_fallidos = []

        for archivo in archivos_a_copiar:
            command = 'cp -r "{0}" "{1}/"'.format(archivo, self.punto_montaje)
            result = self._run_command(command)
            if result["success"]:
                exitos += 1
                logger.info("Archivo copiado: {0}".format(os.path.basename(archivo)))
            else:
                fallos += 1
                nombre_archivo = os.path.basename(archivo)
                stderr = result["stderr"].lower()
                
                if "permission denied" in stderr:
                    archivos_fallidos.append("{0} (Permiso denegado)".format(nombre_archivo))
                elif "no such file" in stderr:
                    archivos_fallidos.append("{0} (No encontrado)".format(nombre_archivo))
                elif "is a directory" in stderr:
                    archivos_fallidos.append("{0} (Es un directorio)".format(nombre_archivo))
                else:
                    archivos_fallidos.append("{0} (Error: {1})".format(nombre_archivo, result['stderr'].strip()))
        
        informe = "[ÉXITO] Se compartieron {0} archivo(s)\n".format(exitos)
        if fallos > 0:
            informe += "[FALLO] No se pudieron compartir {0} archivo(s):\n".format(fallos)
            informe += "\n".join([" - {0}".format(f) for f in archivos_fallidos])
        
        if exitos > 0:
            logger.exito("Se compartieron {0} archivos".format(exitos))
        if fallos > 0:
            logger.error("Fallaron {0} archivos".format(fallos))
        
        return {"success": exitos > 0, "message": informe}

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

    def recibir_archivos(self, archivos_remotos, destino_local):
        """
        Copia archivos desde el punto de montaje a una ubicación local
        Nueva funcionalidad para recibir archivos
        """
        if not os.path.ismount(self.punto_montaje):
            logger.error("El recurso no está montado")
            return {"success": False, "message": "[ERROR] El recurso no está montado"}
        
        # Validar destino local
        if not os.path.exists(destino_local):
            try:
                os.makedirs(destino_local)
                logger.info("Directorio de destino creado: {0}".format(destino_local))
            except Exception as e:
                logger.error("Error creando directorio destino: {0}".format(str(e)))
                return {"success": False, "message": "[ERROR] No se pudo crear el directorio destino"}
        
        exitos = 0
        fallos = 0
        archivos_fallidos = []
        
        for archivo in archivos_remotos:
            ruta_completa = os.path.join(self.punto_montaje, archivo)
            command = 'cp -r "{0}" "{1}/"'.format(ruta_completa, destino_local)
            result = self._run_command(command)
            
            if result["success"]:
                exitos += 1
                logger.info("Archivo recibido: {0}".format(archivo))
            else:
                fallos += 1
                stderr = result["stderr"].lower()
                
                if "permission denied" in stderr:
                    archivos_fallidos.append("{0} (Permiso denegado)".format(archivo))
                elif "no such file" in stderr:
                    archivos_fallidos.append("{0} (No encontrado)".format(archivo))
                else:
                    archivos_fallidos.append("{0} (Error: {1})".format(archivo, result['stderr'].strip()))
        
        informe = "[ÉXITO] Se recibieron {0} archivo(s) en {1}\n".format(exitos, destino_local)
        if fallos > 0:
            informe += "[FALLO] No se pudieron recibir {0} archivo(s):\n".format(fallos)
            informe += "\n".join([" - {0}".format(f) for f in archivos_fallidos])
        
        if exitos > 0:
            logger.exito("Se recibieron {0} archivos".format(exitos))
        if fallos > 0:
            logger.error("Fallaron {0} archivos al recibir".format(fallos))
        
        return {"success": exitos > 0, "message": informe}

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