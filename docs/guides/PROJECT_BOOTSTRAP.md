# PROJECT_BOOTSTRAP - Guía Profesional de Instalación de EREN

> **Este documento contiene instrucciones precisas para configurar el entorno de desarrollo de EREN.**
> **NO salte pasos. Siga el orden exacto.**
> **Tiempo estimado: 45-60 minutos**

---

## Declaración de Propósito

Esta guía proporciona instrucciones paso a paso para configurar un entorno de desarrollo profesional para EREN Cognitive Operating System. Sigue los estándares definidos en TECH_BIBLE.md y está alineado con VISION.md.

**Alineado con**: TECH_BIBLE.md v2.0.0, VISION.md v1.0.0

---

## Requisitos Previos

### Hardware Mínimo

- **CPU**: 4 cores o más (recomendado 8+ cores)
- **RAM**: 16 GB mínimo (recomendado 32 GB)
- **Disco**: 50 GB libres (SSD recomendado para performance)
- **GPU**: No requerida inicialmente (opcional para futuros modelos de ML)

### Software Base Requerido

1. **Windows 11** (o Windows 10 con actualizaciones recientes)
2. **WSL2** (Windows Subsystem for Linux 2)
3. **Ubuntu 24.04 LTS** (en WSL2)
4. **Docker Desktop** para Windows
5. **Git**
6. **VS Code**, **Cursor**, o **DevIn**
7. **Claude Code** (Cascade)

### Versiones Específicas

- **Windows**: Windows 11 22H2+ o Windows 10 21H2+
- **WSL2**: Versión 2.0.0+
- **Ubuntu**: 24.04 LTS
- **Docker Desktop**: 4.27+
- **Git**: 2.40+
- **Python**: 3.11+ (gestionado por uv)
- **Node.js**: 18 LTS+ (gestionado por pnpm)
- **uv**: 0.4+
- **pnpm**: 9+

---

## Paso 1: Configurar WSL2 y Ubuntu 24.04

### 1.1 Habilitar WSL2

Abrir PowerShell como Administrador:

```powershell
wsl --install
```

Reiniciar Windows cuando se solicite.

### 1.2 Verificar instalación

```powershell
wsl --list --verbose
```

Debería mostrar Ubuntu 24.04 LTS como DEFAULT.

### 1.3 Actualizar Ubuntu

Abrir terminal WSL (Ubuntu):

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Paso 2: Instalar Docker Desktop

### 2.1 Descargar Docker Desktop

Descargar desde: https://www.docker.com/products/docker-desktop/

### 2.2 Instalar

Ejecutar instalador con configuraciones por defecto.

### 2.3 Habilitar WSL2 Integration

En Docker Desktop:
- Settings → Resources → WSL Integration
- Habilitar "Enable integration with my default WSL distro"
- Habilitar Ubuntu-24.04

### 2.4 Verificar

```bash
docker --version
docker compose version
```

Salida esperada:
```
Docker version 27.x.x
Docker Compose version v2.x.x
```

---

## Paso 3: Instalar Git

### 3.1 En Windows

Descargar desde: https://git-scm.com/download/win

Instalar con opciones por defecto.

### 3.2 Configurar Git

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
git config --global init.defaultBranch main
git config --global core.autocrlf true
```

### 3.3 Verificar

```bash
git --version
```

Salida esperada: `git version 2.x.x`

---

## Paso 4: Instalar uv (Python Package Manager)

### 4.1 Instalar uv

En PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 4.2 Verificar instalación

```bash
uv --version
```

Salida esperada: `uv 0.x.x`

### 4.3 Configurar uv

```bash
uv config set global.python-preference only-managed
```

---

## Paso 5: Instalar pnpm (Node.js Package Manager)

### 5.1 Instalar Node.js (si no está instalado)

Descargar LTS desde: https://nodejs.org/

### 5.2 Instalar pnpm

```powershell
npm install -g pnpm
```

### 5.3 Verificar

```bash
pnpm --version
```

Salida esperada: `9.x.x`

---

## Paso 6: Clonar Repositorio

### 6.1 Crear directorio de proyectos

```bash
cd ~/CascadeProjects
```

Si no existe, crearlo:

```powershell
mkdir C:\Users\ASUS VIVOBOOK\CascadeProjects
```

### 6.2 Clonar repositorio

```bash
cd ~/CascadeProjects
git clone https://github.com/tu-usuario/eren.git
cd eren
```

**Nota**: Reemplazar con URL real del repositorio.

---

## Paso 7: Configurar Backend (Python)

### 7.1 Crear entorno virtual con uv

```bash
cd backend
uv venv
```

### 7.2 Activar entorno

```bash
source .venv/bin/activate
```

### 7.3 Instalar dependencias

```bash
uv pip install -r requirements.txt
```

### 7.4 Verificar instalación

```bash
python --version
```

Salida esperada: `Python 3.11+`

```bash
uv pip list
```

Debería mostrar FastAPI, uvicorn, etc.

---

## Paso 8: Configurar Frontend (Next.js)

### 8.1 Instalar dependencias

```bash
cd ../frontend
pnpm install
```

### 8.2 Verificar instalación

```bash
pnpm --version
node --version
```

---

## Paso 9: Instalar Supabase CLI

### 9.1 Instalar Supabase CLI

En PowerShell:

```powershell
npm install -g supabase
```

### 9.2 Verificar instalación

```bash
supabase --version
```

Salida esperada: `1.x.x`

### 9.3 Inicializar Supabase local (opcional)

```bash
supabase init
```

Esto crea la configuración local de Supabase.

---

## Paso 10: Configurar Qdrant

### 10.1 Iniciar Qdrant con Docker

Qdrant ya está incluido en docker-compose.yml. Iniciarlo:

```bash
docker compose up -d qdrant
```

### 10.2 Verificar Qdrant

```bash
curl http://localhost:6333/
```

Salida esperada: JSON response con status "ok"

### 10.3 Configurar API Key (opcional)

Para producción, configurar API key en docker-compose.yml:

```yaml
qdrant:
  environment:
    - QDRANT__SERVICE__API_KEY=tu_api_key
```

---

## Paso 11: Configurar Variables de Entorno

### 11.1 Copiar archivo de ejemplo

```bash
cd ..
cp .env.example .env.local
```

### 11.2 Editar .env.local

```bash
code .env.local
```

Configurar las siguientes variables:

```env
# Supabase
SUPABASE_URL=tu_supabase_url
SUPABASE_ANON_KEY=tu_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_supabase_service_role_key

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=tu_qdrant_api_key

# Backend
BACKEND_URL=http://localhost:8000
BACKEND_API_KEY=tu_backend_api_key

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=tu_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=tu_supabase_anon_key

# OpenAI (para modelos de lenguaje)
OPENAI_API_KEY=tu_openai_api_key

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Paso 12: Iniciar Servicios con Docker

### 12.1 Iniciar contenedores

```bash
docker compose up -d
```

Esto iniciará:
- Supabase (PostgreSQL)
- Qdrant (Vector DB)
- Redis (Caching)

### 12.2 Verificar contenedores

```bash
docker ps
```

Debería mostrar 3+ contenedores corriendo.

---

## Paso 13: Iniciar Backend

### 13.1 Activar entorno virtual

```bash
cd backend
source .venv/bin/activate
```

### 13.2 Iniciar servidor

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 13.3 Verificar

Abrir en navegador: http://localhost:8000/docs

Debería mostrar la documentación de FastAPI (Swagger).

---

## Paso 14: Iniciar Frontend

### 14.1 Nueva terminal

Abrir nueva terminal WSL.

### 14.2 Iniciar servidor de desarrollo

```bash
cd frontend
pnpm dev
```

### 14.3 Verificar

Abrir en navegador: http://localhost:3000

Debería mostrar la aplicación EREN.

---

## Paso 15: Ejecutar Tests

### 15.1 Tests de Backend

```bash
cd backend
source .venv/bin/activate
pytest
```

### 15.2 Tests de Frontend

```bash
cd frontend
pnpm test
```

---

## Paso 16: Verificar Configuración Completa

### Checklist de Validación

- [ ] WSL2 funcionando con Ubuntu 24.04
- [ ] Docker Desktop corriendo con WSL2 integration
- [ ] Git configurado correctamente
- [ ] uv instalado y funcionando
- [ ] pnpm instalado y funcionando
- [ ] Supabase CLI instalado
- [ ] Qdrant corriendo en Docker
- [ ] Repositorio clonado
- [ ] Entorno virtual Python creado con uv
- [ ] Dependencias backend instaladas
- [ ] Dependencias frontend instaladas
- [ ] Variables de entorno configuradas
- [ ] Contenedores Docker corriendo (Supabase, Qdrant, Redis)
- [ ] Backend accesible en http://localhost:8000/docs
- [ ] Frontend accesible en http://localhost:3000
- [ ] Tests de backend pasando
- [ ] Tests de frontend pasando

---

## Problemas Comunes y Soluciones

### Problema: WSL2 no inicia

**Solución**:
```powershell
wsl --update
wsl --shutdown
```

### Problema: Docker no se conecta a WSL2

**Solución**:
- Abrir Docker Desktop
- Settings → Resources → WSL Integration
- Deshabilitar y habilitar nuevamente
- Reiniciar Docker Desktop

### Problema: uv no se encuentra

**Solución**:
```bash
# Cerrar y abrir terminal nuevamente
# O agregar al PATH en ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
```

### Problema: Puerto ya en uso

**Solución**:
```bash
# Encontrar proceso usando puerto 8000
lsof -i :8000
# Matar proceso
kill -9 <PID>
```

### Problema: Dependencias no instalan

**Solución**:
```bash
# Limpiar caché de uv
uv cache clean

# Reinstalar
uv pip install -r requirements.txt
```

### Problema: Contenedores Docker no inician

**Solución**:
```bash
# Ver logs
docker compose logs

# Reconstruir
docker compose down
docker compose up -d --build
```

---

## Comandos Útiles

### Backend

```bash
# Activar entorno
source backend/.venv/bin/activate

# Iniciar servidor
uvicorn src.main:app --reload

# Ejecutar tests
pytest

# Ejecutar tests con coverage
pytest --cov=src

# Formatear código
black src/
isort src/

# Linter
ruff check src/

# Type checking
mypy src/
```

### Frontend

```bash
# Iniciar servidor
pnpm dev

# Ejecutar tests
pnpm test

# Build para producción
pnpm build

# Linter
pnpm lint

# Formatear
pnpm format
```

### Docker

```bash
# Iniciar contenedores
docker compose up -d

# Ver logs
docker compose logs -f

# Detener contenedores
docker compose down

# Reconstruir
docker compose up -d --build

# Ver contenedores
docker ps
```

### Git

```bash
# Estado
git status

# Commits
git add .
git commit -m "feat: descripción"

# Push
git push origin main

# Pull
git pull origin main

# Crear rama
git checkout -b feature/nueva-funcionalidad
```

---

## Versiones Específicas

### Python

```bash
# Versión 3.11+
python --version
```

### Node.js

```bash
# Versión 18 LTS o superior
node --version
```

### uv

```bash
# Versión 0.4+
uv --version
```

### pnpm

```bash
# Versión 9+
pnpm --version
```

### Docker

```bash
# Versión 27+
docker --version
```

---

## Próximos Pasos

Una vez completado el bootstrap:

1. Leer `VISION.md` - Máxima autoridad del proyecto
2. Leer `EREN_MANIFESTO.md` - Filosofía y principios
3. Leer `TECH_BIBLE.md` - Constitución técnica (OBLIGATORIO)
4. Revisar `docs/adr/README.md` - Índice de decisiones arquitectónicas
5. Configurar tu IDE (VS Code/Cursor/DevIn) con extensiones recomendadas
6. Comenzar desarrollo siguiendo TECH_BIBLE.md

### Extensiones Recomendadas para VS Code

- Python (Microsoft)
- Pylance (Microsoft)
- Black Formatter (Microsoft)
- isort (Microsoft)
- ESLint (Microsoft)
- Prettier (Prettier)
- Docker (Microsoft)
- GitLens (GitKraken)
- Thunder Client (Rest Client)
- Mermaid Preview (bierner)

---

## Soporte

Si encuentras problemas no documentados:

1. Verificar logs de Docker: `docker compose logs`
2. Verificar logs de backend: Ver terminal donde corre uvicorn
3. Verificar logs de frontend: Ver terminal donde corre pnpm dev
4. Crear issue en GitHub con:
   - Versión de Windows
   - Versión de WSL
   - Versión de Docker
   - Error completo
   - Pasos para reproducir

---

**Última actualización**: 2026-07-10  
**Versión**: 2.0.0  
**Autor**: Chief Software Architect / Principal AI Engineer / CTO  
**Alineado con**: TECH_BIBLE.md v2.0.0, VISION.md v1.0.0
