import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    print(f"swagger url: http://127.0.0.1:8020/docs")
    uvicorn.run(app="main:app", host="0.0.0.0", port=8020, reload=True)