import uvicorn
from fastapi import FastAPI
from app.api.sample import router as sample_router

app = FastAPI(title="individual_project_template", version="0.0.1")

app.include_router(sample_router)

if __name__ == "__main__":
    uvicorn.run(app="app")