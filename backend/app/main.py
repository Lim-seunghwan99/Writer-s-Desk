from fastapi import FastAPI
from contextlib import asynccontextmanager  
from pathlib import Path
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from .routers import words, works, episodes, characters, worlds, plannings, search, wordexamples
from .crud.opensearch_crud import create_works_content_index  
from . import config

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv(
    "DATABASE_URL"
) 
if DATABASE_URL is None:
    print(
        "경고: DATABASE_URL 환경 변수가 .env 파일에 설정되지 않았거나 로드되지 않았습니다."
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup (lifespan)...")
    print(
        f"Attempting to ensure OpenSearch index '{config.OPENSEARCH_RAG_INDEX_NAME}' exists..."
    )
    try:
        create_works_content_index()
        print(
            f"OpenSearch index '{config.OPENSEARCH_RAG_INDEX_NAME}' check/creation complete."
        )
    except Exception as e:
        print(
            f"!!! Critical Error during OpenSearch index setup on startup (lifespan): {e}"
        )
    yield
    print("Application shutdown (lifespan)...")


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",  
    "http://192.168.0.75:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(words.router)  
app.include_router(works.router)
app.include_router(episodes.router)
app.include_router(characters.router)
app.include_router(worlds.router)
app.include_router(plannings.router)
app.include_router(wordexamples. router)

@app.get("/")
async def root():
    return {"message": "Welcome to Personal Dictionary API"}


# python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
