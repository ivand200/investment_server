from fastapi import FastAPI
import uvicorn

from routers.indexes import indexes_router
from routers.stocks import stocks_router


app = FastAPI()


app.include_router(indexes_router, prefix="/api/indexes", tags="indexes")
app.include_router(stocks_router, prefix="/api/stocks", tags="stocks")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Investment app!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)