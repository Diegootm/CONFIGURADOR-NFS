"""
Sistema de logging centralizado
Registra eventos, errores y actividades del sistema
"""
import logging
import os
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """
    Formatter personalizado con colores para la consola
    """
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'EXITO': '\033[32m\033[1m',  # Verde brillante
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Agregar color según el nivel
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = "{0}{1}{2}".format(
            color, record.levelname, self.COLORS['RESET']
        )
        return super().format(record)


class ConfiguradorNFSLogger:
    """
    Clase principal del logger para el Configurador NFS
    """
    
    def __init__(self, nombre='configurador-nfs', nivel=logging.INFO):
        self.logger = logging.getLogger(nombre)
        self.logger.setLevel(nivel)
        
        # Evitar duplicados
        if self.logger.handlers:
            return
        
        # Configurar handlers
        self._configurar_console_handler()
        self._configurar_file_handler()
        
        # Agregar nivel personalizado EXITO
        logging.addLevelName(25, 'EXITO')
    
    def _configurar_console_handler(self):
        """
        Configura el handler para la consola con colores
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato para consola
        console_format = ColoredFormatter(
            '%(levelname)-8s | %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        self.logger.addHandler(console_handler)
    
    def _configurar_file_handler(self):
        """
        Configura el handler para archivo de log
        """
        # Crear directorio de logs si no existe
        log_dir = '/var/log'
        log_file = os.path.join(log_dir, 'configurador-nfs.log')
        
        # Si no tenemos permisos en /var/log, usar home del usuario
        if not os.access(log_dir, os.W_OK):
            log_dir = os.path.expanduser('~/.config/configurador-nfs')
            if not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir)
                except:
                    # Si falla, usar /tmp
                    log_dir = '/tmp'
            log_file = os.path.join(log_dir, 'configurador-nfs.log')
        
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Formato para archivo (más detallado)
            file_format = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            
            self.logger.addHandler(file_handler)
            
            # Log inicial
            self.logger.info("=" * 60)
            self.logger.info("Logger inicializado - Archivo: {0}".format(log_file))
            self.logger.info("=" * 60)
            
        except Exception as e:
            print("Advertencia: No se pudo crear el archivo de log: {0}".format(e))
    
    def debug(self, mensaje):
        """Log nivel DEBUG"""
        self.logger.debug(mensaje)
    
    def info(self, mensaje):
        """Log nivel INFO"""
        self.logger.info(mensaje)
    
    def warning(self, mensaje):
        """Log nivel WARNING"""
        self.logger.warning(mensaje)
    
    def error(self, mensaje):
        """Log nivel ERROR"""
        self.logger.error(mensaje)
    
    def critical(self, mensaje):
        """Log nivel CRITICAL"""
        self.logger.critical(mensaje)
    
    def exito(self, mensaje):
        """Log nivel EXITO (personalizado)"""
        self.logger.log(25, mensaje)
    
    def separador(self):
        """Imprime un separador visual en los logs"""
        self.logger.info("-" * 60)
    
    def seccion(self, titulo):
        """Imprime un título de sección"""
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info(" " + titulo)
        self.logger.info("=" * 60)


# Instancia global del logger
logger = ConfiguradorNFSLogger()


# Funciones de conveniencia
def debug(mensaje):
    """Wrapper para logger.debug()"""
    logger.debug(mensaje)


def info(mensaje):
    """Wrapper para logger.info()"""
    logger.info(mensaje)


def warning(mensaje):
    """Wrapper para logger.warning()"""
    logger.warning(mensaje)


def error(mensaje):
    """Wrapper para logger.error()"""
    logger.error(mensaje)


def critical(mensaje):
    """Wrapper para logger.critical()"""
    logger.critical(mensaje)


def exito(mensaje):
    """Wrapper para logger.exito()"""
    logger.exito(mensaje)


def separador():
    """Wrapper para logger.separador()"""
    logger.separador()


def seccion(titulo):
    """Wrapper para logger.seccion()"""
    logger.seccion(titulo)