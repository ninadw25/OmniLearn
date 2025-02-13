# from routes.rag_routes import app

# if __name__ == '__main__':
#     app.run(host='localhost', port=8000)
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routes.rag_routes import router

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)