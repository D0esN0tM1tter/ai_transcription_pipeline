
from fastapi import FastAPI
from app.api.routers.pipeline_router import router as pipeline_router
from app.api.routers.downloads_router import router as downloads_router

app = FastAPI() 

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# registering thr router in the app :

# registering the routers in the app :
app.include_router(pipeline_router, prefix="/api", tags=["pipeline"])
app.include_router(downloads_router, prefix="/api", tags=["downloads"])

@app.get("/") 
def root() :
    return {"status" : "API is running"}