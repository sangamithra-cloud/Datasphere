from dotenv import load_dotenv
import os

load_dotenv()  # loads .env file

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY found in .env")
