from fastapi import FastAPI
from src.api.routes import question_routes
from src.api.dependencies.dependencies import init_app_dependencies
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Or whatever your React app's origin is
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(question_routes.router)


@app.on_event("startup")
async def startup_event():
    await init_app_dependencies()