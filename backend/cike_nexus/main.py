from fastapi import FastAPI

from cike_nexus.routers import UserRouter

app = FastAPI()

app.include_router(UserRouter.router, prefix="/api/users", tags=["Users"])


@app.get("/")
async def root():
    return {"message": "Hello World"}
