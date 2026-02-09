# Gaming Nexus - Live Web Agent System

🎮 **Sistema de asistencia gaming con IA** donde el 100% de la información se extrae en tiempo real de la web.

## Arquitectura

```
ProyectoNexus/
├── server/                 # Backend Python
│   ├── main.py            # FastAPI + SSE streaming
│   ├── agents/            # LangGraph agents
│   │   ├── orchestrator.py   # Intent routing
│   │   ├── news_scout.py     # Noticias/parches
│   │   ├── tactician.py      # Builds/meta
│   │   └── guide_navigator.py # Guías paso a paso
│   └── tools/             # Herramientas
│       ├── web_search.py     # DuckDuckGo search
│       ├── scraper.py        # Content extraction
│       └── formatter.py      # JSON artifacts
│
└── client/                 # Frontend Angular 17
    └── src/app/
        ├── services/nexus.service.ts    # SSE client
        └── components/
            ├── chat-stream/             # Chat UI
            ├── nexus-sidebar/           # Artifact panel
            ├── table-artifact/          # News tables
            ├── build-dashboard/         # Build stats
            └── step-guide/              # Progressive guides
```

## Requisitos

- **Python 3.11+**
- **Node.js 18+**
- **Ollama** con modelo `llama3.2` instalado

## Instalación

### 1. Backend

```bash
cd server

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Frontend

```bash
cd client
npm install
```

### 3. Ollama

Asegúrate de tener Ollama corriendo con el modelo:

```bash
ollama run llama3.2
```

## Ejecución

### Terminal 1 - Backend

```bash
cd server
venv\Scripts\activate
python main.py
```

El servidor estará en: `http://localhost:8000`

### Terminal 2 - Frontend

```bash
cd client
npm start
```

La aplicación estará en: `http://localhost:4200`

## Uso

### Ejemplos de preguntas:

- **Builds**: "¿Cuál es el mejor build para Jinx en LoL parche 14.2?"
- **Noticias**: "Últimas noticias de Elden Ring"
- **Guías**: "¿Cómo derrotar a Malenia en Elden Ring?"
- **Follow-up**: "Dime más sobre ese primer ítem"

### Características:

- 🔍 **Búsqueda en tiempo real** - Sin conocimiento estático
- 📡 **Streaming SSE** - Ve el "pensamiento" del agente
- 🎨 **Tema Cyber-Dark** - Estética gaming con neón
- 📊 **Artifacts dinámicos** - Tablas, builds, guías progresivas

## API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/chat/stream` | POST | Chat con streaming SSE |
| `/api/chat/history/{session_id}` | GET | Historial de conversación |
| `/api/chat/history/{session_id}` | DELETE | Limpiar historial |
| `/api/health` | GET | Health check |

## Colores del Tema

- **Fondo**: `#050505`
- **Acento primario (cyan)**: `#00f3ff`
- **Acento alerta (rojo)**: `#ff0055`
- **Acento éxito (verde)**: `#00ff88`
