import cloudinary.uploader

def upload_to_cloudinary(file,folder:str,resource_type:str="auto"):
      result=cloudinary.uploader.upload(file,folder=folder,resource_type=resource_type)
      return result["secure_url"]