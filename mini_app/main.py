from fastapi import FastAPI
from auth_router import router

app=FastAPI(
    title="Mini FastAPI app"

)

app.include_router(router)

app.get("/")
def root():
    return {
        "Message":"App is running."

    }