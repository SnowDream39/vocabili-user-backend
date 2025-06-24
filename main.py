import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.API_HOST, port=int(settings.PORT), log_level="info")