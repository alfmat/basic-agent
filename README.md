# Basic Agent

A full-stack conversational AI weather assistant application featuring a LangGraph-based agent backend, FastAPI REST API server, and a modern React frontend.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Components](#components)
  - [Python Agent](#python-agent)
  - [Backend API](#backend-api)
  - [Frontend](#frontend)
  - [Vector Embeddings POC](#vector-embeddings-poc)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

Basic Agent is a comprehensive weather assistant application that demonstrates modern AI agent architecture. It combines:

- **Intelligent Weather Agent**: Built with LangGraph and LangChain, providing natural language weather queries
- **REST API Backend**: FastAPI server with streaming chat endpoints
- **Modern Web UI**: React + TypeScript + Vite frontend with real-time chat interface
- **Vector Embeddings**: Proof-of-concept module for semantic search capabilities

## 🏗️ Architecture

```
┌─────────────────┐
│   React         │  Frontend (Port 5173)
│   Frontend      │  - Chat interface
│   (Vite)        │  - Streaming responses
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│   FastAPI       │  Backend (Port 8000)
│   Server        │  - /chat endpoint
│                 │  - /health endpoint
└────────┬────────┘
         │
         │
┌────────▼────────┐
│   LangGraph     │  Python Agent
│   Weather       │  - Weather tools
│   Agent         │  - LLM integration
│                 │  - Memory management
└─────────────────┘
```

## ✅ Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **OpenAI API Key**: Required for the LLM
- **Optional API Keys**:
  - AirNow API key (for air quality data)
  - TimeZoneDB API key (for accurate timezone information)

## 📁 Project Structure

```
basic-agent/
├── backend/              # FastAPI server
│   ├── main.py          # API endpoints and CORS configuration
│   └── __pycache__/
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   │   └── Chat.tsx # Main chat interface
│   │   ├── App.tsx      # Root component
│   │   └── main.tsx     # Entry point
│   ├── public/          # Static assets
│   ├── package.json     # Node dependencies
│   ├── vite.config.ts   # Vite configuration
│   ├── tsconfig.json    # TypeScript config
│   └── tailwind.config.js # Tailwind CSS config
├── python_agent/        # LangGraph weather agent
│   ├── agent.py         # Agent implementation
│   ├── testing_vectors.py # Vector embeddings POC
│   ├── requirements.txt # Python dependencies
│   └── sample_tweets/   # Sample data for vectors
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/alfmat/basic-agent.git
cd basic-agent
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
AIRNOW_API_KEY=your_airnow_api_key_here
TIMEZONE_API_KEY=your_timezone_api_key_here
```

### 3. Install Python Dependencies

```bash
pip install -r python_agent/requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Start the Backend Server

```bash
cd backend
python main.py
```

The backend will start on `http://localhost:8000`

### 6. Start the Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### 7. Access the Application

Open your browser and navigate to `http://localhost:5173`

## 🔧 Components

### Python Agent

**Location**: `python_agent/`

A sophisticated weather assistant built with LangGraph and LangChain that provides comprehensive weather information for US cities.

#### Features

- **Current Weather & Forecast**: 7-day detailed forecast using NWS API
- **Hourly Forecast**: 12-hour detailed predictions
- **Weather Alerts**: Active weather warnings and watches
- **Solar & Lunar Information**: Sunrise/sunset times and moon phases
- **Air Quality Index**: Real-time AQI data with health recommendations
- **Clothing Recommendations**: Smart suggestions based on conditions

#### Running Standalone

```bash
cd python_agent
python agent.py
```

#### Commands

- `help` or `h`: Show available commands
- `history`: View conversation history
- `clear`: Clear conversation history
- `quit`, `exit`, or `q`: Exit the program

#### Example Queries

```
What's the weather in New York?
Give me the forecast for Seattle
Is it raining in Chicago?
What should I wear in Boston today?
Are there any weather alerts for Miami?
```

#### Architecture

- **Framework**: LangGraph for orchestration, LangChain for LLM integration
- **Model**: OpenAI GPT-4o-mini
- **Data Sources**:
  - National Weather Service (NWS) API
  - AirNow API (optional)
  - OpenStreetMap Nominatim for geocoding
  - Astral library for solar calculations
  - PyEphem for lunar phases

### Backend API

**Location**: `backend/`

FastAPI server that exposes the weather agent as a REST API with streaming support.

#### Endpoints

##### `POST /chat`

Send messages to the weather agent and receive streaming responses.

**Request Body**:
```json
{
  "message": "What's the weather in Boston?",
  "thread_id": "optional_thread_identifier"
}
```

**Response**: NDJSON stream
```json
{"content": "Weath"}
{"content": "er fo"}
{"content": "r Bos"}
...
```

##### `GET /health`

Health check endpoint.

**Response**:
```json
{
  "status": "ok"
}
```

#### Running the Backend

```bash
cd backend
python main.py
```

Or use uvicorn directly:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### CORS Configuration

The backend is configured to allow requests from any origin during development. For production, update the `allow_origins` in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-production-domain.com"],
    ...
)
```

### Frontend

**Location**: `frontend/`

Modern, responsive chat interface built with React, TypeScript, and Vite.

#### Tech Stack

- **React 19**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Styling
- **Framer Motion**: Animations
- **Axios**: HTTP client
- **React Markdown**: Markdown rendering

#### Scripts

```bash
# Development server (with hot reload)
npm run dev

# Production build
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

#### Configuration

The frontend expects the backend API to be available at `http://localhost:8000`. To change this, update the API endpoint in the source code.

#### Customization

- **Styling**: Modify `tailwind.config.js` for theme customization
- **Components**: Chat component located at `src/components/Chat.tsx`
- **Build**: Configure Vite settings in `vite.config.ts`

### Vector Embeddings POC

**Location**: `python_agent/testing_vectors.py`

A proof-of-concept module demonstrating vector embeddings and semantic search capabilities using LangChain.

#### Features

- Uses OpenAI's `text-embedding-3-large` model
- In-memory vector store
- Similarity search on sample documents

#### Running the POC

```bash
cd python_agent
python testing_vectors.py
```

#### Sample Data

Located in `python_agent/sample_tweets/`:
- `file1.txt`: Random test content
- `file2.txt`: Sample text with color references

The script demonstrates semantic search by finding documents similar to a query term.

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT models and embeddings |
| `AIRNOW_API_KEY` | No | AirNow API key for air quality data |
| `TIMEZONE_API_KEY` | No | TimeZoneDB API key for timezone information |

### API Key Setup

1. **OpenAI**: Sign up at [OpenAI Platform](https://platform.openai.com/)
2. **AirNow**: Register at [AirNow API](https://docs.airnowapi.org/account/request/)
3. **TimeZoneDB**: Sign up at [TimeZoneDB](https://timezonedb.com/)

## 💻 Development

### Linting

**Frontend**:
```bash
cd frontend
npm run lint
```

### Building

**Frontend**:
```bash
cd frontend
npm run build
```

This creates optimized production files in the `dist/` directory.

### Testing

Currently, the project uses manual testing. To test:

1. Start the backend server
2. Start the frontend development server
3. Navigate to `http://localhost:5173`
4. Test chat interactions with various weather queries

### Development Workflow

1. Make changes to the code
2. Backend changes: The server will need to be restarted manually
3. Frontend changes: Vite will hot-reload automatically
4. Test your changes in the browser
5. Commit your changes with descriptive messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is open source. Please check the license file for details.

## 🐛 Known Limitations

- Weather data limited to US cities (NWS API coverage)
- Air quality requires optional API key
- Real-time data dependent on external API availability
- No authentication/authorization currently implemented
- Backend runs in single-process mode (not production-ready for scale)

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [National Weather Service API](https://www.weather.gov/documentation/services-web-api)
