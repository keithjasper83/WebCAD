"""
WebCAD FastAPI Application

Main entry point for the WebCAD REST API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.feature import router as feature_router
from api.routes.model import router as model_router
from api.routes.sketch import router as sketch_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="WebCAD API",
        description="""
WebCAD is a browser-based CAD backend powered by OpenCASCADE.

## Features

* **Sketch System**: Create 2D profiles with lines, circles, and arcs
* **Dimensions**: Add parametric dimensions to control geometry
* **Features**: Extrude, fillet, and cut operations
* **Export**: Export to STL and STEP formats

## Architecture

WebCAD follows Domain-Driven Design (DDD) with clean separation:

* **Domain**: Pure business entities (no external dependencies)
* **Application**: Use cases and services
* **Infrastructure**: OCC kernel, persistence
* **API**: REST endpoints with Pydantic DTOs
        """,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS for browser access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(sketch_router)
    app.include_router(feature_router)
    app.include_router(model_router)

    @app.get("/", tags=["Root"])
    def root() -> dict:
        """Root endpoint with API information."""
        return {
            "name": "WebCAD API",
            "version": "0.1.0",
            "docs": "/docs",
            "status": "running",
        }

    @app.get("/health", tags=["Health"])
    def health() -> dict:
        """Health check endpoint."""
        from infrastructure.occ.kernel import OCCKernel

        kernel = OCCKernel()
        return {
            "status": "healthy",
            "occ_available": kernel.is_available,
        }

    return app


# Create the application instance
app = create_app()


def run() -> None:
    """Run the application using uvicorn."""
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run()
