from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.routers import incidents, sources, auth, dashboard, analytics
from app.utils.websocket_manager import WebSocketManager
import structlog

logger = structlog.get_logger()

app = FastAPI(
    title="Indian Cyber Threat Intelligence Platform",
    description="Comprehensive framework for cyber incident collection and analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
websocket_manager = WebSocketManager()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Indian Cyber Threat Intelligence Platform</title>
        </head>
        <body>
            <h1>Indian Cyber Threat Intelligence Platform</h1>
            <p>API Documentation: <a href="/api/docs">/api/docs</a></p>
            <p>ReDoc: <a href="/api/redoc">/api/redoc</a></p>
            <p>Dashboard: <a href="http://localhost:3000">Frontend Dashboard</a></p>
        </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Indian Cyber Threat Intelligence Platform"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.websocket("/ws/incidents")
async def websocket_incidents(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and send real-time incident updates
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Indian Cyber Threat Intelligence Platform")
    # Initialize any startup tasks here
    pass

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Indian Cyber Threat Intelligence Platform")
    # Cleanup tasks here
    pass