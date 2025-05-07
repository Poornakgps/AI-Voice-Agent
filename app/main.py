import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.routes import status, admin, twilio_webhook
from app.routes import audio_test
from app.routes import websocket

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    logger.info("Starting Voice AI Restaurant Agent application")
    
    yield

    logger.info("Shutting down Voice AI Restaurant Agent application")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(audio_test.router, tags=["Testing"])
app.include_router(websocket.router, tags=["WebSocket"])

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """
    Global error handling middleware to catch and log exceptions.
    """
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(e) if settings.DEBUG else None},
        )

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """
    Middleware to log all incoming requests and their processing time.
    """
    import time
    
    start_time = time.time()
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Request completed: {request.method} {request.url.path} - {process_time:.3f}s")
    
    return response

app.include_router(status.router, tags=["Status"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(twilio_webhook.router, prefix="/webhook", tags=["Webhook"])

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """
    Redirect root URL to API documentation.
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    """
    Run the application using Uvicorn when executed directly.
    """
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.DEBUG,
    )