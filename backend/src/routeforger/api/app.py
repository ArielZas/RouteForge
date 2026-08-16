from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routeforger.api.routes import router
from routeforger.geo.road_graph import load_road_graph


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Load shared geographic data once for the application lifetime."""
    road_graph, district_polygon = load_road_graph()
    application.state.road_graph = road_graph
    application.state.district_polygon = district_polygon
    yield


def create_app() -> FastAPI:
    """Create and configure the RouteForger API application."""
    application = FastAPI(
        title="RouteForger API",
        version="0.1.0",
        description="HTTP interface for delivery-route optimization.",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    
    application.include_router(router, prefix="/api")
    return application


app = create_app()
