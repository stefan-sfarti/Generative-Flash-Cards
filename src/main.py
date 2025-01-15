from fastapi import FastAPI
from src.api.routes import question_routes
from src.api.dependencies.dependencies import init_app_dependencies

app = FastAPI()
app.include_router(question_routes.router)


@app.on_event("startup")
async def startup_event():
    await init_app_dependencies()