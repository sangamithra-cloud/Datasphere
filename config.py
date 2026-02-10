from dotenv import load_dotenv
import os
import cloudinary 
from cloudinary.uploader import upload as cloudinary_upload
from fastapi import HTTPException

load_dotenv()  

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise HTTPException(status_code=500, detail="No SECRET_KEY found in .env")

DATABASE_URL=os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise HTTPException(status_code=500, detail="No DATABASE_URL found in .env")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)
if not all([cloudinary.config().cloud_name, cloudinary.config().api_key, cloudinary.config().api_secret]):
    raise HTTPException(status_code=500, detail="Cloudinary configuration is incomplete in .env")
