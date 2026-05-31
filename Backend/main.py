from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.api.chat import router as chat_router
from dotenv import load_dotenv, find_dotenv

# Ensure environment variables are loaded for the app
load_dotenv(find_dotenv())

app = FastAPI(title="CreatorJoy Video Intelligence API")

# Include the routers
app.include_router(ingest_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "Welcome to CreatorJoy API. Visit /docs for Swagger UI."}
