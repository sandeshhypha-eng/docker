# 3-Tier Docker Application - Task Management System

A complete full-stack web application built with Docker Compose, featuring a React frontend, Node.js/Express backend, and MongoDB database.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Traffic Flow Diagram](#traffic-flow-diagram)
4. [System Components](#system-components)
5. [Getting Started](#getting-started)
6. [API Endpoints](#api-endpoints)
7. [Project Structure](#project-structure)

---

## 🎯 Project Overview

This is a **Task Management Application** with three interconnected services:
- **Frontend**: React web interface for users to manage tasks
- **Backend**: Node.js/Express REST API for handling business logic
- **Database**: MongoDB for persistent data storage

All services run in Docker containers and communicate through a custom Docker network.

---

## 🏗️ Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                           │
│                    (http://localhost:3000)                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER BRIDGE NETWORK                         │
│                     (app-network)                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   FRONTEND CONTAINER                      │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │     React App (Port 3000)                          │  │   │
│  │  │  - Webpack Dev Server                              │  │   │
│  │  │  - setupProxy.js (Proxies /api to backend)         │  │   │
│  │  │  - Task Component (UI for managing tasks)          │  │   │
│  │  │  - taskServices.js (API client using /api/tasks)   │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                          │                                        │
│                          │ /api/tasks (relative URL)              │
│                          │ (via webpack dev server proxy)         │
│                          ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                  BACKEND CONTAINER                          │  │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │   Node.js/Express API Server (Port 3500)             │  │   │
│  │  │  - GET    /api/tasks       → Fetch all tasks        │  │   │
│  │  │  - POST   /api/tasks       → Create new task        │  │   │
│  │  │  - PUT    /api/tasks/:id   → Update task            │  │   │
│  │  │  - DELETE /api/tasks/:id   → Delete task            │  │   │
│  │  │  - GET    /healthz         → Health check           │  │   │
│  │  │  - GET    /ready           → Readiness check        │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                          │                                        │
│                          │ mongodb://mongo:27017/tasks            │
│                          │ (MongoDB connection string)            │
│                          ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                 MONGODB CONTAINER                          │  │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │   MongoDB Database (Port 27017)                       │  │   │
│  │  │  - Database: tasks                                     │  │   │
│  │  │  - Collections: tasks (stores all task documents)     │  │   │
│  │  │  - Volumes: mongo-data, mongo-config (persistence)   │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Traffic Flow Diagram

### User Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: User Opens Browser                                          │
│ └─> Browser visits http://localhost:3000                            │
│     └─> Frontend container's webpack dev server responds           │
│         └─> Serves React app (HTML, CSS, JS bundles)               │
└─────────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: React App Loads (componentDidMount)                        │
│ └─> taskServices.getTasks() called                                 │
│     └─> axios.get("/api/tasks")  [relative URL]                    │
│         └─> Webpack proxy intercepts request                       │
│             └─> setupProxy.js routes to http://backend:3500/api/tasks
└─────────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Backend Processes Request                                  │
│ └─> Express server receives GET /api/tasks                         │
│     └─> tasks router handles request                               │
│         └─> MongoDB findall() query executed                       │
│             └─> Returns all task documents from database           │
└─────────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Response Returns to Frontend                               │
│ └─> Backend sends JSON response (array of tasks)                  │
│     └─> Webpack dev server proxy relays response to browser        │
│         └─> Browser receives response                              │
│             └─> React updates state: setState({ tasks: data })    │
│                 └─> Component re-renders and displays tasks       │
└─────────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: User Interaction (e.g., Add Task)                          │
│ └─> User types task and clicks "Submit"                           │
│     └─> handleSubmit() called                                      │
│         └─> taskServices.addTask(taskObject)                       │
│             └─> axios.post("/api/tasks", taskObject)              │
│                 └─> Webpack proxy intercepts                       │
│                     └─> setupProxy.js routes to backend            │
└─────────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: Backend Processes Create Request                           │
│ └─> Express server receives POST /api/tasks                        │
│     └─> tasks router receives task data                            │
│         └─> MongoDB save() executed                                │
│             └─> New task document stored in database               │
│                 └─> Returns created task with _id                 │
└─────────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: Frontend Updates UI                                         │
│ └─> Response received by browser                                   │
│     └─> taskServices.addTask() returns promise                    │
│         └─> handleSubmit() adds task to local state               │
│             └─> Component re-renders                               │
│                 └─> New task appears in UI immediately             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 System Components

### Frontend Service (React)
- **Port**: 3000 (accessible at `http://localhost:3000`)
- **Technology**: React, Axios, Material-UI
- **Key Files**:
  - `Tasks.js`: Main component with task management logic
  - `taskServices.js`: API client using `/api/tasks` relative URLs
  - `setupProxy.js`: Webpack proxy configuration for API routing
- **How It Works**:
  1. Webpack dev server runs on port 3000
  2. setupProxy.js intercepts all `/api/*` requests
  3. Routes requests to `http://backend:3500` inside Docker network
  4. Returns responses to browser

### Backend Service (Node.js/Express)
- **Port**: 3500 (accessible at `http://localhost:3500`)
- **Technology**: Express.js, MongoDB Driver, Node.js
- **Key Files**:
  - `index.js`: Express server setup, route mounting, health checks
  - `routes/tasks.js`: REST API endpoints for CRUD operations
  - `models/task.js`: MongoDB Task schema
  - `db.js`: MongoDB connection logic
- **API Endpoints**:
  - `GET /api/tasks` - Retrieve all tasks
  - `POST /api/tasks` - Create new task
  - `PUT /api/tasks/:id` - Update task
  - `DELETE /api/tasks/:id` - Delete task
  - `GET /healthz` - Health status
  - `GET /ready` - Readiness status

### MongoDB Service
- **Port**: 27017 (accessible at `localhost:27017`)
- **Database**: `tasks`
- **Collection**: `tasks` (stores task documents)
- **Data Persistence**: 
  - `mongo-data` volume: Stores database files
  - `mongo-config` volume: Stores configuration files
- **Health Check**: Pings database every 10 seconds

---

## 🚀 Getting Started

### Prerequisites
- Docker Desktop installed and running
- Terminal/Command line access

### Starting the Application

```bash
# Navigate to the 3-tier-app directory
cd "/Users/fci/Desktop/untitled folder 3/docker/3-tier-app"

# Start all services
docker-compose up -d

# Wait for frontend to compile (watch logs)
docker logs frontend-app -f

# Once you see "Compiled successfully!", open browser
# Visit: http://localhost:3000
```

### Stopping the Application

```bash
# Stop all containers
docker-compose down

# Remove containers and images
docker-compose down -v

# Remove images
docker rmi 3-tier-app-frontend 3-tier-app-backend -f
```

### Viewing Logs

```bash
# Frontend logs
docker logs frontend-app -f

# Backend logs
docker logs backend-app -f

# MongoDB logs
docker logs mongodb -f

# All services logs
docker-compose logs -f
```

---

## 📡 API Endpoints

### Task Management Endpoints

#### Get All Tasks
```http
GET /api/tasks
Response: 200 OK
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "task": "Learn Docker",
    "completed": false,
    "__v": 0
  }
]
```

#### Create Task
```http
POST /api/tasks
Content-Type: application/json

{
  "task": "Build application",
  "completed": false
}

Response: 201 Created
{
  "_id": "507f1f77bcf86cd799439012",
  "task": "Build application",
  "completed": false,
  "__v": 0
}
```

#### Update Task
```http
PUT /api/tasks/507f1f77bcf86cd799439011
Content-Type: application/json

{
  "completed": true
}

Response: 200 OK
{
  "_id": "507f1f77bcf86cd799439011",
  "task": "Learn Docker",
  "completed": true,
  "__v": 0
}
```

#### Delete Task
```http
DELETE /api/tasks/507f1f77bcf86cd799439011

Response: 204 No Content
```

#### Health Check
```http
GET /healthz
Response: 200 OK
Healthy
```

#### Readiness Check
```http
GET /ready
Response: 200 OK
Ready
```

---

## 📁 Project Structure

```
3-tier-app/
├── docker-compose.yml          # Orchestrates all 3 services
├── README.md                    # This file
│
├── frontend/                    # React Application
│   ├── Dockerfile              # Builds React app
│   ├── package.json            # React dependencies
│   ├── .env                    # Environment variables
│   ├── public/                 # Static files
│   │   ├── index.html         # HTML entry point
│   │   ├── manifest.json      # PWA manifest
│   │   └── favicon.ico        # Website icon
│   └── src/                    # React source code
│       ├── index.js           # Entry point
│       ├── App.js             # Root component
│       ├── Tasks.js           # Task management component
│       ├── setupProxy.js       # Webpack proxy configuration
│       ├── services/
│       │   └── taskServices.js # API client
│       ├── App.css            # App styles
│       └── index.css          # Global styles
│
├── backend/                     # Node.js/Express API
│   ├── Dockerfile             # Builds Node.js app
│   ├── package.json           # Node dependencies
│   ├── index.js               # Express server & routes
│   ├── db.js                  # MongoDB connection
│   ├── models/
│   │   └── task.js            # Task schema
│   └── routes/
│       └── tasks.js           # REST endpoints
│
└── Database/                    # Kubernetes manifests (future use)
    ├── deployment.yaml
    ├── service.yaml
    ├── pvc.yaml
    ├── pv.yaml
    ├── secrets.yaml
    └── global-bundle.pem
```

---

## 🔐 Security Notes

- **CORS**: Enabled on backend (`Access-Control-Allow-Origin: *`)
- **MongoDB Authentication**: Disabled in development (set `USE_DB_AUTH=false`)
- **Environment Variables**: Stored in `.env` file (not in version control)
- **For Production**: 
  - Enable MongoDB authentication
  - Use environment-specific variables
  - Implement JWT authentication
  - Use HTTPS
  - Restrict CORS origins

---

## 🐛 Troubleshooting

### Frontend can't connect to backend
- Check if backend container is running: `docker ps`
- Verify backend logs: `docker logs backend-app`
- Check proxy configuration: `docker logs frontend-app | grep "Proxy created"`

### MongoDB connection fails
- Verify MongoDB is healthy: `docker ps` (check STATUS column)
- Check MongoDB logs: `docker logs mongodb`
- Ensure data volumes exist: `docker volume ls | grep mongo`

### Port conflicts
- Check if ports are in use: `lsof -i :3000` or `lsof -i :3500` or `lsof -i :27017`
- Kill processes using ports: `kill -9 <PID>`
- Or change ports in `docker-compose.yml`

---

## 📚 Learning Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [React Documentation](https://react.dev/)
- [Express.js Guide](https://expressjs.com/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [HTTP Proxy Middleware](https://github.com/chimurai/http-proxy-middleware)

---

## 📝 Notes

- All services are on the same Docker network (`app-network`)
- Services communicate using service names: `frontend`, `backend`, `mongo`
- Data persists in named volumes even after containers stop
- Frontend uses relative URLs (`/api/tasks`) which are proxied to the backend
- All services auto-restart if they crash (unless manually stopped)

---

## 📄 License

This project is for educational purposes.

---

**Last Updated**: December 6, 2025
