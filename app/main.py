from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, medical
from app.database import Base, engine
from app.config import settings
from app.utils.logger import logger

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medical ChatBot API",
    version="1.0.0",
    description="Professional Medical Information Chatbot"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://medical-chatbot-frontend-25sg.onrender.com","http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(medical.router, prefix="/api/v1/medical", tags=["medical"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Medical ChatBot API...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)