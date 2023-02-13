from settings import Settings
import motor.motor_asyncio

settings = Settings()

client = motor.motor_asyncio.AsyncIOMotorClient(settings.DATABASE)
database = client.investments