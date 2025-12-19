# 🖥️ Configurador NFS Integral para OpenSUSE

Herramienta completa con interfaz gráfica para configurar y gestionar servidores y clientes NFS en OpenSUSE.

## 🌟 Características

### Servidor NFS
- ✅ Gestión completa de `/etc/exports`
- ✅ Soporte para archivos individuales y directorios
- ✅ Asignación automática de `fsid` para archivos
- ✅ Ajuste automático de permisos del filesystem
- ✅ Validación en tiempo real de configuraciones
- ✅ Aplicación de cambios con `exportfs -ra`
- ✅ Verificación del servicio NFS

### Cliente NFS
- ✅ Montaje de recursos remotos
- ✅ Validación de conexión al servidor
- ✅ Visualización del contenido montado
- ✅ Desmontaje seguro de recursos
- ✅ Gestión de puntos de montaje

### Transferencia de Archivos
- ✅ Envío de archivos al recurso NFS
- ✅ Envío de carpetas completas
- ✅ Recepción de archivos desde NFS
- ✅ Selección múltiple
- ✅ Sincronización bidireccional

## 📋 Requisitos

### Sistema Operativo
- **OpenSUSE Leap 15.6+** o **Tumbleweed**
- Arquitectura: x86_64, ARM64

### Software Necesario
- Python 3.6 o superior
- Tkinter (python3-tk)
- NFS Kernel Server (nfs-kernel-server)

## 🚀 Instalación

### Instalación Automática (Recomendada)

```bash
# Clonar o descargar el proyecto
cd configurador-nfs

# Dar permisos de ejecución al instalador
chmod +x install.sh

# Ejecutar el instalador como root
sudo ./install.sh
```

El script de instalación:
1. Verifica el sistema operativo
2. Instala Python 3 y Tkinter si es necesario
3. Instala y configura NFS
4. Copia los archivos a `/opt/configurador-nfs`
5. Crea un comando global `configurador-nfs`
6. Crea una entrada en el menú de aplicaciones

### Instalación Manual

```bash
# Instalar dependencias
sudo zypper install python3 python3-tk nfs-kernel-server

# Habilitar e iniciar NFS
sudo systemctl enable nfs-server
sudo systemctl start nfs-server

# Copiar archivos
sudo mkdir -p /opt/configurador-nfs
sudo cp -r * /opt/configurador-nfs/

# Crear comando global
sudo cat > /usr/local/bin/configurador-nfs << 'EOF'
#!/bin/bash
cd /opt/configurador-nfs
exec python3 main.py "$@"
EOF
sudo chmod +x /usr/local/bin/configurador-nfs

# Copiar entrada del menú
sudo cp configurador-nfs.desktop /usr/share/applications/
```

## 🎯 Uso

### Desde Terminal

```bash
# Con permisos de root (funcionalidad completa)
sudo configurador-nfs

# Sin permisos de root (solo lectura)
configurador-nfs
```

### Desde el Menú

Busca "Configurador NFS" en el menú de aplicaciones de tu escritorio.

## 📖 Guía de Uso

### Configurar Servidor NFS

1. Ve a la pestaña **"Servidor NFS"**
2. Haz clic en "Explorar" para seleccionar una carpeta o archivo
3. Especifica los hosts permitidos (ej: `192.168.1.0/24` o `*`)
4. Selecciona las opciones NFS deseadas
5. Haz clic en "Agregar Exportación"
6. Haz clic en "Aplicar Cambios" para activar

### Montar Recurso NFS (Cliente)

1. Ve a la pestaña **"Cliente NFS"**
2. Ingresa la IP del servidor NFS
3. Especifica la ruta remota a montar
4. Define el punto de montaje local
5. Haz clic en "Montar"

### Transferir Archivos

1. Monta un recurso NFS primero (pestaña Cliente)
2. Ve a la pestaña **"Transferencias"**
3. Para enviar: Usa "Seleccionar Archivos" o "Seleccionar Carpeta"
4. Para recibir: Haz clic en "Actualizar Lista" y selecciona archivos

## ⚙️ Configuración Recomendada

### Para Carpetas Compartidas
```
Opciones: rw, sync, no_subtree_check, root_squash
```

### Para Archivos Individuales
```
Opciones: rw, sync, no_subtree_check, fsid=<auto>
```

### Para Solo Lectura
```
Opciones: ro, sync, no_subtree_check, root_squash
```

## 🔥 Configuración del Firewall

Si usas firewall, permite NFS:

```bash
sudo firewall-cmd --add-service=nfs --permanent
sudo firewall-cmd --add-service=rpc-bind --permanent
sudo firewall-cmd --add-service=mountd --permanent
sudo firewall-cmd --reload
```

## 📝 Logs

Los logs del sistema se guardan en:
- `/var/log/configurador-nfs.log` (con permisos de root)
- `~/.config/configurador-nfs/configurador-nfs.log` (sin permisos de root)

## 🐛 Solución de Problemas

### "Permission Denied" al montar
- Ejecuta con `sudo configurador-nfs`
- Verifica que el servidor tenga la carpeta exportada
- Verifica permisos del filesystem en el servidor

### El servicio NFS no inicia
```bash
sudo systemctl status nfs-server
sudo journalctl -xeu nfs-server
```

### Error al aplicar cambios
- Verifica sintaxis de `/etc/exports`
- Revisa los logs: `sudo journalctl -xeu nfs-server`

### No puedo escribir en el recurso montado
- Verifica que la exportación use `rw` (no `ro`)
- Verifica permisos del filesystem en el servidor
- Verifica que no use `root_squash` si necesitas acceso root

## 🏗️ Estructura del Proyecto

```
configurador-nfs/
├── main.py                    # Punto de entrada
├── gestor_nfs.py             # Lógica del servidor
├── cliente_nfs.py            # Lógica del cliente
├── transferencia.py          # Transferencias bidireccionales
├── install.sh                # Script de instalación
├── configurador-nfs.desktop  # Entrada del menú
├── ui/
│   ├── __init__.py
│   ├── ventana_principal.py  # Ventana principal
│   ├── tab_servidor.py       # Pestaña servidor
│   ├── tab_cliente.py        # Pestaña cliente
│   ├── tabs_transferencia.py # Pestaña transferencias
│   └── temas.py              # Estilos y tema
├── utils/
│   ├── __init__.py
│   ├── compatibilidad.py     # Verificación del sistema
│   ├── validaciones.py       # Validaciones
│   └── logger.py             # Sistema de logs
└── README.md                 # Este archivo
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Haz push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

## 👥 Autores

- Versión unificada basada en los repositorios de diegootm y anistopera
- Combina lo mejor de ambas implementaciones

## 🙏 Agradecimientos

- Comunidad de OpenSUSE
- Desarrolladores de Python y Tkinter
- Proyecto NFS

## 📧 Soporte

Si encuentras problemas o tienes sugerencias:
- Abre un issue en GitHub
- Consulta los logs del sistema
- Revisa la documentación de NFS

---

**Hecho con ❤️ para la comunidad OpenSUSE**