from fastapi import FastAPI
from datetime import datetime
from app.config import settings

app = FastAPI(
    title= "VulnScan Pro",
    description="AI-powered Web Security Scanner",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "VulnScan Pro API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy","timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)