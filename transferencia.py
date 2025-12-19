"""
Módulo de Transferencia Bidireccional
Nueva funcionalidad que combina envío y recepción de archivos/directorios
"""
import os
import shutil
from utils.logger import logger


class TransferenciaNFS:
    """
    Clase para manejar transferencias bidireccionales de archivos y directorios
    """
    
    def __init__(self, punto_montaje):
        self.punto_montaje = punto_montaje
        logger.info("TransferenciaNFS inicializado con punto de montaje: {0}".format(punto_montaje))
    
    def validar_montaje(self):
        """
        Verifica que el punto de montaje esté montado
        """
        if not self.punto_montaje:
            return (False, "Punto de montaje no definido")
        
        if not os.path.ismount(self.punto_montaje):
            return (False, "El recurso NFS no está montado en {0}".format(self.punto_montaje))
        
        return (True, "Punto de montaje válido")
    
    def enviar_archivo(self, ruta_origen, nombre_destino=None):
        """
        Envía un archivo individual al recurso NFS
        """
        valido, mensaje = self.validar_montaje()
        if not valido:
            logger.error(mensaje)
            return {"success": False, "message": "[ERROR] {0}".format(mensaje)}
        
        if not os.path.exists(ruta_origen):
            logger.error("Archivo origen no existe: {0}".format(ruta_origen))
            return {"success": False, "message": "[ERROR] El archivo no existe"}
        
        if not os.path.isfile(ruta_origen):
            logger.error("La ruta no es un archivo: {0}".format(ruta_origen))
            return {"success": False, "message": "[ERROR] La ruta debe ser un archivo"}
        
        try:
            if nombre_destino:
                ruta_destino = os.path.join(self.punto_montaje, nombre_destino)
            else:
                ruta_destino = os.path.join(self.punto_montaje, os.path.basename(ruta_origen))
            
            shutil.copy2(ruta_origen, ruta_destino)
            logger.exito("Archivo enviado: {0}".format(os.path.basename(ruta_origen)))
            return {"success": True, "message": "[OK] Archivo enviado correctamente"}
        except Exception as e:
            logger.error("Error enviando archivo: {0}".format(str(e)))
            return {"success": False, "message": "[ERROR] {0}".format(str(e))}
    
    def enviar_directorio(self, ruta_origen, nombre_destino=None):
        """
        Envía un directorio completo al recurso NFS
        """
        valido, mensaje = self.validar_montaje()
        if not valido:
            logger.error(mensaje)
            return {"success": False, "message": "[ERROR] {0}".format(mensaje)}
        
        if not os.path.exists(ruta_origen):
            logger.error("Directorio origen no existe: {0}".format(ruta_origen))
            return {"success": False, "message": "[ERROR] El directorio no existe"}
        
        if not os.path.isdir(ruta_origen):
            logger.error("La ruta no es un directorio: {0}".format(ruta_origen))
            return {"success": False, "message": "[ERROR] La ruta debe ser un directorio"}
        
        try:
            if nombre_destino:
                ruta_destino = os.path.join(self.punto_montaje, nombre_destino)
            else:
                ruta_destino = os.path.join(self.punto_montaje, os.path.basename(ruta_origen))
            
            shutil.copytree(ruta_origen, ruta_destino, dirs_exist_ok=True)
            logger.exito("Directorio enviado: {0}".format(os.path.basename(ruta_origen)))
            return {"success": True, "message": "[OK] Directorio enviado correctamente"}
        except Exception as e:
            logger.error("Error enviando directorio: {0}".format(str(e)))
            return {"success": False, "message": "[ERROR] {0}".format(str(e))}
    
    def recibir_archivo(self, nombre_archivo, destino_local):
        """
        Recibe un archivo desde el recurso NFS
        """
        valido, mensaje = self.validar_montaje()
        if not valido:
            logger.error(mensaje)
            return {"success": False, "message": "[ERROR] {0}".format(mensaje)}
        
        ruta_origen = os.path.join(self.punto_montaje, nombre_archivo)
        
        if not os.path.exists(ruta_origen):
            logger.error("Archivo remoto no existe: {0}".format(nombre_archivo))
            return {"success": False, "message": "[ERROR] El archivo no existe en el recurso NFS"}
        
        if not os.path.isfile(ruta_origen):
            logger.error("La ruta remota no es un archivo: {0}".format(nombre_archivo))
            return {"success": False, "message": "[ERROR] La ruta debe ser un archivo"}
        
        try:
            # Crear directorio destino si no existe
            dir_destino = os.path.dirname(destino_local)
            if dir_destino and not os.path.exists(dir_destino):
                os.makedirs(dir_destino)
            
            shutil.copy2(ruta_origen, destino_local)
            logger.exito("Archivo recibido: {0}".format(nombre_archivo))
            return {"success": True, "message": "[OK] Archivo recibido correctamente"}
        except Exception as e:
            logger.error("Error recibiendo archivo: {0}".format(str(e)))
            return {"success": False, "message": "[ERROR] {0}".format(str(e))}
    
    def recibir_directorio(self, nombre_directorio, destino_local):
        """
        Recibe un directorio completo desde el recurso NFS
        """
        valido, mensaje = self.validar_montaje()
        if not valido:
            logger.error(mensaje)
            return {"success": False, "message": "[ERROR] {0}".format(mensaje)}
        
        ruta_origen = os.path.join(self.punto_montaje, nombre_directorio)
        
        if not os.path.exists(ruta_origen):
            logger.error("Directorio remoto no existe: {0}".format(nombre_directorio))
            return {"success": False, "message": "[ERROR] El directorio no existe en el recurso NFS"}
        
        if not os.path.isdir(ruta_origen):
            logger.error("La ruta remota no es un directorio: {0}".format(nombre_directorio))
            return {"success": False, "message": "[ERROR] La ruta debe ser un directorio"}
        
        try:
            shutil.copytree(ruta_origen, destino_local, dirs_exist_ok=True)
            logger.exito("Directorio recibido: {0}".format(nombre_directorio))
            return {"success": True, "message": "[OK] Directorio recibido correctamente"}
        except Exception as e:
            logger.error("Error recibiendo directorio: {0}".format(str(e)))
            return {"success": False, "message": "[ERROR] {0}".format(str(e))}
    
    def listar_remoto(self):
        """
        Lista el contenido del recurso NFS montado
        """
        valido, mensaje = self.validar_montaje()
        if not valido:
            logger.error(mensaje)
            return {"success": False, "message": "[ERROR] {0}".format(mensaje), "items": []}
        
        try:
            items = []
            for item in os.listdir(self.punto_montaje):
                ruta_completa = os.path.join(self.punto_montaje, item)
                tipo = "directorio" if os.path.isdir(ruta_completa) else "archivo"
                try:
                    tamano = os.path.getsize(ruta_completa) if os.path.isfile(ruta_completa) else 0
                except:
                    tamano = 0
                
                items.append({
                    "nombre": item,
                    "tipo": tipo,
                    "tamano": tamano,
                    "ruta": ruta_completa
                })
            
            logger.info("Se listaron {0} items del recurso remoto".format(len(items)))
            return {"success": True, "message": "[OK] Contenido listado", "items": items}
        except Exception as e:
            logger.error("Error listando contenido: {0}".format(str(e)))
            return {"success": False, "message": "[ERROR] {0}".format(str(e)), "items": []}
    
    def enviar_multiples(self, rutas_origen):
        """
        Envía múltiples archivos y/o directorios
        """
        resultados = {
            "exitos": 0,
            "fallos": 0,
            "detalles": []
        }
        
        for ruta in rutas_origen:
            if os.path.isfile(ruta):
                resultado = self.enviar_archivo(ruta)
            elif os.path.isdir(ruta):
                resultado = self.enviar_directorio(ruta)
            else:
                resultado = {"success": False, "message": "Ruta no válida"}
            
            if resultado["success"]:
                resultados["exitos"] += 1
            else:
                resultados["fallos"] += 1
            
            resultados["detalles"].append({
                "ruta": ruta,
                "resultado": resultado
            })
        
        mensaje_final = "[RESUMEN] Enviados: {0} | Fallidos: {1}".format(
            resultados["exitos"], resultados["fallos"]
        )
        logger.info(mensaje_final)
        
        return {
            "success": resultados["exitos"] > 0,
            "message": mensaje_final,
            "resultados": resultados
        }
    
    def recibir_multiples(self, nombres_remotos, destino_local):
        """
        Recibe múltiples archivos y/o directorios
        """
        resultados = {
            "exitos": 0,
            "fallos": 0,
            "detalles": []
        }
        
        for nombre in nombres_remotos:
            ruta_remota = os.path.join(self.punto_montaje, nombre)
            ruta_local = os.path.join(destino_local, nombre)
            
            if os.path.isfile(ruta_remota):
                resultado = self.recibir_archivo(nombre, ruta_local)
            elif os.path.isdir(ruta_remota):
                resultado = self.recibir_directorio(nombre, ruta_local)
            else:
                resultado = {"success": False, "message": "Elemento no encontrado"}
            
            if resultado["success"]:
                resultados["exitos"] += 1
            else:
                resultados["fallos"] += 1
            
            resultados["detalles"].append({
                "nombre": nombre,
                "resultado": resultado
            })
        
        mensaje_final = "[RESUMEN] Recibidos: {0} | Fallidos: {1}".format(
            resultados["exitos"], resultados["fallos"]
        )
        logger.info(mensaje_final)
        
        return {
            "success": resultados["exitos"] > 0,
            "message": mensaje_final,
            "resultados": resultados
        }
    
    def sincronizar(self, ruta_local, direccion="enviar"):
        """
        Sincroniza un directorio local con el recurso NFS
        direccion: "enviar" o "recibir"
        """
        valido, mensaje = self.validar_montaje()
        if not valido:
            logger.error(mensaje)
            return {"success": False, "message": "[ERROR] {0}".format(mensaje)}
        
        if not os.path.exists(ruta_local):
            return {"success": False, "message": "[ERROR] La ruta local no existe"}
        
        if not os.path.isdir(ruta_local):
            return {"success": False, "message": "[ERROR] La ruta debe ser un directorio"}
        
        try:
            if direccion == "enviar":
                # Sincronizar local -> remoto
                for item in os.listdir(ruta_local):
                    ruta_item = os.path.join(ruta_local, item)
                    if os.path.isfile(ruta_item):
                        self.enviar_archivo(ruta_item)
                    elif os.path.isdir(ruta_item):
                        self.enviar_directorio(ruta_item)
                
                mensaje = "[OK] Sincronización completada (local -> remoto)"
            else:
                # Sincronizar remoto -> local
                for item in os.listdir(self.punto_montaje):
                    ruta_remota = os.path.join(self.punto_montaje, item)
                    ruta_local_item = os.path.join(ruta_local, item)
                    
                    if os.path.isfile(ruta_remota):
                        self.recibir_archivo(item, ruta_local_item)
                    elif os.path.isdir(ruta_remota):
                        self.recibir_directorio(item, ruta_local_item)
                
                mensaje = "[OK] Sincronización completada (remoto -> local)"
            
            logger.exito(mensaje)
            return {"success": True, "message": mensaje}
        except Exception as e:
            logger.error("Error en sincronización: {0}".format(str(e)))
            return {"success": False, "message": "[ERROR] {0}".format(str(e))}