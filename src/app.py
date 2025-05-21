# src/app.py

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from interfaces.web.routes import router
from interfaces.web.snapshot_level_routes import lvl_router
from interfaces.web.snapshot_pid_routes import plot_router
from interfaces.web.snapshot_pid_plot import plot_router

from starlette.exceptions import HTTPException as StarletteHTTPException


def create_app() -> FastAPI:
    """
    Create and configure FastAPI app with UI routes and static files.
    """
    app = FastAPI(title="Memory-metrics UI")

    app.mount("/static", StaticFiles(directory="src/interfaces/web/static"), name="static")

    app.include_router(router, prefix="/api/v1")
    app.include_router(lvl_router, prefix="/api/v1")
    app.include_router(plot_router, prefix="/api/v1")
    app.include_router(plot_router, prefix="/api/v1")

    @app.exception_handler(StarletteHTTPException)
    async def redirect_not_found(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return RedirectResponse(url="/api/v1/")
        raise exc

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:create_app", factory=True, host="0.0.0.0", port=8000)
