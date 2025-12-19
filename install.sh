#!/bin/bash
# Script de instalación para Configurador NFS Unificado
# Compatible con OpenSUSE 15.6+

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}  Configurador NFS Unificado - Instalación${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Este script debe ejecutarse como root${NC}"
    echo -e "${YELLOW}   Ejecute: sudo ./install.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Ejecutando como root"

# Verificar sistema operativo
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$ID" != "opensuse-leap" ]] && [[ "$ID" != "opensuse-tumbleweed" ]]; then
        echo -e "${YELLOW}⚠  Advertencia: Este script está diseñado para OpenSUSE${NC}"
        echo -e "${YELLOW}   Su sistema: $PRETTY_NAME${NC}"
        read -p "¿Desea continuar de todos modos? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✓${NC} Sistema detectado: $PRETTY_NAME"
    fi
else
    echo -e "${YELLOW}⚠  No se pudo detectar el sistema operativo${NC}"
fi

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar Python 3
echo ""
echo -e "${BLUE}[1/6]${NC} Verificando Python 3..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python 3 instalado: v$PYTHON_VERSION"
else
    echo -e "${YELLOW}⚙  Instalando Python 3...${NC}"
    zypper install -y python3
    echo -e "${GREEN}✓${NC} Python 3 instalado"
fi

# Verificar Tkinter
echo ""
echo -e "${BLUE}[2/6]${NC} Verificando Tkinter..."
if python3 -c "import tkinter" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Tkinter ya está instalado"
else
    echo -e "${YELLOW}⚙  Instalando Tkinter...${NC}"
    zypper install -y python3-tk
    echo -e "${GREEN}✓${NC} Tkinter instalado"
fi

# Verificar/Instalar NFS
echo ""
echo -e "${BLUE}[3/6]${NC} Verificando NFS..."
if command_exists exportfs; then
    echo -e "${GREEN}✓${NC} NFS ya está instalado"
else
    echo -e "${YELLOW}⚙  Instalando NFS Kernel Server...${NC}"
    zypper install -y nfs-kernel-server
    echo -e "${GREEN}✓${NC} NFS instalado"
fi

# Habilitar y iniciar servicio NFS
echo ""
echo -e "${BLUE}[4/6]${NC} Configurando servicio NFS..."
systemctl enable nfs-server 2>/dev/null || echo -e "${YELLOW}⚠  Ya estaba habilitado${NC}"
systemctl start nfs-server 2>/dev/null || true

if systemctl is-active --quiet nfs-server; then
    echo -e "${GREEN}✓${NC} Servicio NFS activo"
else
    echo -e "${YELLOW}⚠  Servicio NFS no está activo${NC}"
    echo -e "${YELLOW}   Puede iniciarlo manualmente: sudo systemctl start nfs-server${NC}"
fi

# Crear directorio de instalación
echo ""
echo -e "${BLUE}[5/6]${NC} Instalando aplicación..."
INSTALL_DIR="/opt/configurador-nfs"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠  El directorio $INSTALL_DIR ya existe${NC}"
    read -p "¿Desea sobrescribir la instalación existente? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}✓${NC} Instalación anterior eliminada"
    else
        echo -e "${RED}❌ Instalación cancelada${NC}"
        exit 1
    fi
fi

mkdir -p "$INSTALL_DIR"
echo -e "${GREEN}✓${NC} Directorio creado: $INSTALL_DIR"

# Copiar archivos de la aplicación
echo -e "${YELLOW}⚙  Copiando archivos...${NC}"
cp -r main.py gestor_nfs.py cliente_nfs.py transferencia.py ui utils "$INSTALL_DIR/"
echo -e "${GREEN}✓${NC} Archivos copiados"

# Crear script ejecutable
echo -e "${YELLOW}⚙  Creando comando global...${NC}"
cat > /usr/local/bin/configurador-nfs << 'EOF'
#!/bin/bash
cd /opt/configurador-nfs
exec python3 main.py "$@"
EOF

chmod +x /usr/local/bin/configurador-nfs
echo -e "${GREEN}✓${NC} Comando global creado: configurador-nfs"

# Crear entrada en el menú de aplicaciones
echo ""
echo -e "${BLUE}[6/6]${NC} Creando entrada en el menú..."
cat > /usr/share/applications/configurador-nfs.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Configurador NFS
GenericName=NFS Configuration Tool
Comment=Configurador integral para servidor y cliente NFS en OpenSUSE
Exec=configurador-nfs
Icon=network-server
Terminal=false
StartupNotify=true
Categories=System;Settings;Network;
Keywords=nfs;server;client;network;configuration;opensuse;compartir;archivos;
EOF

echo -e "${GREEN}✓${NC} Entrada de menú creada"

# Configurar firewall (opcional)
echo ""
read -p "¿Desea configurar el firewall para NFS? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}⚙  Configurando firewall...${NC}"
    firewall-cmd --add-service=nfs --permanent 2>/dev/null || echo -e "${YELLOW}⚠  Firewall-cmd no disponible${NC}"
    firewall-cmd --add-service=rpc-bind --permanent 2>/dev/null || true
    firewall-cmd --add-service=mountd --permanent 2>/dev/null || true
    firewall-cmd --reload 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Firewall configurado"
fi

# Resumen final
echo ""
echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}  ✓ ¡Instalación completada con éxito!${NC}"
echo -e "${GREEN}======================================================${NC}"
echo ""
echo -e "${BLUE}📋 Resumen:${NC}"
echo -e "   • Python 3: ${GREEN}✓${NC}"
echo -e "   • Tkinter: ${GREEN}✓${NC}"
echo -e "   • NFS: ${GREEN}✓${NC}"
echo -e "   • Aplicación: ${GREEN}✓${NC}"
echo ""
echo -e "${BLUE}🚀 Para usar el Configurador NFS:${NC}"
echo ""
echo -e "${YELLOW}  Opción 1: Desde la terminal${NC}"
echo -e "    ${GREEN}configurador-nfs${NC}"
echo -e "    o"
echo -e "    ${GREEN}sudo configurador-nfs${NC} (para funcionalidad completa)"
echo ""
echo -e "${YELLOW}  Opción 2: Desde el menú${NC}"
echo -e "    Busca: ${GREEN}Configurador NFS${NC} en el menú de aplicaciones"
echo ""
echo -e "${BLUE}📖 Documentación:${NC}"
echo -e "    Consulta el README.md para más información"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "    /var/log/configurador-nfs.log"
echo ""
echo -e "${YELLOW}⚠  Nota importante:${NC}"
echo -e "    Para modificar /etc/exports y montar recursos,"
echo -e "    debe ejecutar la aplicación como root:"
echo -e "    ${GREEN}sudo configurador-nfs${NC}"
echo ""