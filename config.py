from starlette.config import Config

config = Config(".env")
API_URL: str = config("API_URL")
