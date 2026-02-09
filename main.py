from fastapi import FastAPI,Depends,HTTPException,APIRouter,UploadFile, File,Form
from pydantic import BaseModel,EmailStr, field_validator,root_validator
from sqlalchemy.orm import Session
from models import Vendor,Products,User
from database import get_db
from typing import List, Optional, Dict, Any
from import_export import import_export_router as import_export_router
from hash_password import hash_password,verify_password
from create_access import create_access_token
from auth import  get_current_user
from upload_files import upload_to_cloudinary
import json
import re
from fastapi import HTTPException, status 


app=FastAPI()



protected_router = APIRouter()


# class StrictBaseModel(BaseModel):
#     @field_validator("*", mode="before")
#     def strip_strings(cls, v):
#         if isinstance(v, str):
#             return v.strip() or None
#         return v





class StrictBaseModel(BaseModel):
    @field_validator("*", mode="before")
    def reject_empty_strings(cls, v, info):
        if v is None:
            return None  
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError(f"{info.field_name} cannot be empty")
            return v
        return v
    
#  @field_validator("*", mode="before")
#     def reject_empty_strings(cls, v, info):
#         if isinstance(v, str) and not v.strip():
#             raise ValueError(f"{info.field_name} cannot be empty")
#         return v





STRICT_REGEX = r"^[A-Za-z0-9 @_\-.]+$"


def clean_required(value: str, field: str) -> str:
    if value is None:
        raise HTTPException(status_code=400, detail=f"{field} is required")
    
    value = value.strip()
    
    if not value:
        raise HTTPException(status_code=400, detail=f"{field} cannot be empty or whitespace")
    
    if not re.fullmatch(STRICT_REGEX, value):
        raise HTTPException(
            status_code=400,
            detail=f"{field} cannot contain spaces or special characters"
        )
    
    return value


def clean_optional(value: str | None, field: str) -> str:
    if value is None or not value.strip():
        raise HTTPException(status_code=400, detail=f"{field} cannot be empty or whitespace")
    
    value = value.strip()
    
    if not re.fullmatch(STRICT_REGEX, value):
        raise HTTPException(
            status_code=400,
            detail=f"{field} cannot contain spaces or special characters"
        )
    
    return value



# USER
class UserCreate(StrictBaseModel):
        username: str
        user_code:str
        email:EmailStr
        password: str

class Token(StrictBaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter((User.email == user.email) | (User.user_code == user.user_code)).first():
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        user_code=user.user_code,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    token = create_access_token({"sub": db_user.user_code})
    return {"access_token": token}



class UserLogin(StrictBaseModel):
    user_code: str
    password: str

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_code == user.user_code).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": db_user.user_code})
    return {"access_token": token}



@protected_router.post("/create_vendor")
def Create_vendor(
    vendor_code:str=Form(...),
    vendor_name:str=Form(...),
    contact_email:str|None=Form(None),
    contact_phone:str|None=Form(None),
    business_type:str|None=Form(None),
    industry:str|None=Form(None),
    country:str|None=Form(None),
    vendor_logo: Optional[UploadFile] = File(None),
    dept1_poc_name:str|None=Form(None),
    dept1_email:str|None=Form(None),
    dept1_phone:str|None=Form(None),
    dept2_poc_name:str|None=Form(None),
    dept2_email:str|None=Form(None),
    dept2_phone:str|None=Form(None),
    dept3_poc_name:str|None=Form(None),
    dept3_email:str|None=Form(None),
    dept3_phone:str|None=Form(None),
    dept4_poc_name:str|None=Form(None),
    dept4_email:str|None=Form(None),
    dept4_phone:str|None=Form(None),
    dept5_poc_name:str|None=Form(None),
    dept5_email:str|None=Form(None),
    dept5_phone:str|None=Form(None),

    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)):
    
    vendor_code = vendor_code.strip()

    
   

    existing_vendor=db.query(Vendor).filter(
        Vendor.vendor_code==vendor_code
    ).first()
    if existing_vendor:
       raise HTTPException(status_code=400,detail="vendor already exists")
    
    vendor_logo_url=None
    if vendor_logo:
         vendor_logo_url=upload_to_cloudinary(vendor_logo.file,folder="vendors/logos")

    db_vendor=Vendor(
    vendor_code=clean_required(vendor_code, "Vendor Code"),
    vendor_name=clean_required(vendor_name, "Vendor Name"),
    contact_email=clean_optional(contact_email,"contact_email"),
    contact_phone=clean_optional(contact_phone,"contact_phone"),
    business_type=clean_optional(business_type,"business_type"),
    industry=clean_optional(industry,"industry"),
    country=clean_optional(country,"country"),
    vendor_logo_url=vendor_logo_url,
    dept1_poc_name=clean_optional(dept1_poc_name,"dept1_poc_name"),
    dept1_email=clean_optional(dept1_email,"dept1_email"),
    dept1_phone=clean_optional(dept1_phone,"dept1_phone"),
    dept2_poc_name=clean_optional(dept2_poc_name,"dept2_poc_name"),
    dept2_email=clean_optional(dept2_email,"dept2_email"),
    dept2_phone=clean_optional(dept2_phone,"dept2_phone"),
    dept3_poc_name=clean_optional(dept3_poc_name,"dept3_poc_name"),
    dept3_email=clean_optional(dept3_email,"dept3_email"),
    dept3_phone=clean_optional(dept3_phone,"dept3_phone"),
    dept4_poc_name=clean_optional(dept4_poc_name,"dept4_poc_name"),
    dept4_email=clean_optional(dept4_email,"dept4_email"),
    dept4_phone=clean_optional(dept4_phone,"dept4_phone"),
    dept5_poc_name=clean_optional(dept5_poc_name,"dept5_poc_name"),
    dept5_email=clean_optional(dept5_email,"dept5_email"),
    dept5_phone=clean_optional(dept5_phone,"dept5_phone")
    )

    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


class VendorResponse(StrictBaseModel):
    vendor_code:Optional[str] = None
    vendor_name:Optional[str] = None
    contact_email:Optional[str] = None
    contact_phone:Optional[str] = None
    business_type:Optional[str] = None
    industry:Optional[str] = None
    country:Optional[str] = None
    vendor_logo_url:Optional[str] = None
  
#READ
@protected_router.get("/all_vendors",response_model=list[VendorResponse])
def view_vendors(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    return db.query(Vendor).filter(Vendor.is_active==True).all()


@protected_router.get("/vendor/{vendor_code}",response_model=VendorResponse)
def get_user(vendor_code:str,db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    db_vendor=db.query(Vendor).filter(Vendor.vendor_code==vendor_code).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor


class VendorUpdate(StrictBaseModel):
    vendor_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    vendor_logo_url: Optional[str] = None

    dept1_poc_name: Optional[str] = None
    dept1_email: Optional[EmailStr] = None
    dept1_phone: Optional[str] = None

    dept2_poc_name: Optional[str] = None
    dept2_email: Optional[EmailStr] = None
    dept2_phone: Optional[str] = None

    dept3_poc_name: Optional[str] = None
    dept3_email: Optional[EmailStr] = None
    dept3_phone: Optional[str] = None

    dept4_poc_name: Optional[str] = None
    dept4_email: Optional[EmailStr] = None
    dept4_phone: Optional[str] = None

    dept5_poc_name: Optional[str] = None
    dept5_email: Optional[EmailStr] = None
    dept5_phone: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

@protected_router.put("/update_vendor/{vendor_code}", response_model=VendorResponse)
def update_vendor(
    vendor_code: str,
    payload: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_vendor = db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_vendor, key, value)

    db.commit()
    db.refresh(db_vendor)
    return db_vendor


#DELETE

@protected_router.delete("/vendor/{vendor_code}")
def delete_vendor(vendor_code:str,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
     db_vendor=db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
     if not db_vendor:
         raise HTTPException(status_code=400,detail="VEndor not found")
    #  db.delete(db_vendor)
     db_vendor.is_active = False
     db.commit()
     return{
        "message":"vendor DELETED"
     }

@protected_router.post("/create_products")
def product(
    product_code: str=Form(...),
    product_name: str=Form(...),
    parent_sku:str|None=Form(None),
    variant_sku:str|None=Form(None),
    product_type:str|None=Form(None),
    brand_code:str|None=Form(None),
    brand_name:str|None=Form(None),
    vendor_code:str=Form(...),
    vendor_name:str|None=Form(None),
    category_code:str|None=Form(None),
    category_1:str|None=Form(None),  
    category_2:str|None=Form(None), 
    category_3:str|None=Form(None), 
    category_4:str|None=Form(None), 
    category_5:str|None=Form(None), 
    category_6:str|None=Form(None), 
    category_7:str|None=Form(None), 
    category_8:str|None=Form(None), 
    industry_code:str|None=Form(None),
    industry_name:str|None=Form(None),
    mpn:str|None=Form(None), 
    gtin:str|None=Form(None),
    upc:str|None=Form(None),
    ean:str|None=Form(None), 
    unspc:str|None=Form(None), 
    description:str|None=Form(None),
    prod_short_desc:str|None=Form(None),
    prod_long_desc:str|None=Form(None),
    images:Optional[list[UploadFile]] = File(None),
    videos: Optional[list[UploadFile]] = File(None),
    documents:Optional[list[UploadFile]] = File(None),
    features_1: str|None=Form(None),
    features_2: str|None=Form(None),
    features_3: str|None=Form(None),
    features_4: str|None=Form(None),
    features_5: str|None=Form(None),
    features_6: str|None=Form(None),
    features_7: str|None=Form(None),
    features_8: str|None=Form(None),
    features_9: str|None=Form(None),
    features_10:str|None=Form(None),

    attributes: str|None=Form(None),
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)):
     
    vendor_code = vendor_code.strip()

    
    if not product_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor code cannot be empty or whitespace"
        )

    
    if not re.match(r'^[A-Za-z0-9_-]+$', product_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product code can only contain letters, numbers, hyphens, or underscores"
        )

    
    existing = db.query(Products).filter(Products.product_code == product_code).first()

    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")
    
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_VIDEO_TYPES = ["video/mp4", "video/avi", "video/mov"]
    ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    def validate_file(file, allowed_types, file_type_name):
       if file.content_type not in allowed_types:
             raise HTTPException(
            status_code=400,
            detail=f"Invalid {file_type_name} file type: {file.content_type}"
        )

    image_url = []
    if images:
      for img in images:
        validate_file(img, ALLOWED_IMAGE_TYPES, "image")
        url = upload_to_cloudinary(img.file, folder="products/images")
        image_url.append(url)

    video_url = []
    if videos:
      for vid in videos:
        validate_file(vid, ALLOWED_VIDEO_TYPES, "video")
        url = upload_to_cloudinary(vid.file, folder="products/videos")
        video_url.append(url)

    documents_url = []
    if documents:
      for doc in documents:
        validate_file(doc, ALLOWED_DOCUMENT_TYPES, "document")
        url = upload_to_cloudinary(doc.file, folder="products/documents")
        documents_url.append(url)

    import json
    try:
        attributes_data = json.loads(attributes) if attributes else None
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid attributes JSON")


    db_product = Products(
        product_code=clean_required(product_code),
        product_name=clean_required(product_name),
        parent_sku=clean_optional(parent_sku),
        variant_sku=clean_optional(variant_sku),
        product_type=clean_optional(product_type),
        brand_code=clean_optional(brand_code),
        brand_name=clean_optional(brand_name),
        vendor_code=clean_optional(vendor_code),
        vendor_name=clean_optional(vendor_name),
        category_code=clean_optional(category_code),
        category_1=clean_optional(category_1),
        category_2=clean_optional(category_2),
        category_3=clean_optional(category_3),
        category_4=clean_optional(category_4),
        category_5=clean_optional(category_5),
        category_6=clean_optional(category_6),
        category_7=clean_optional(category_7),
        category_8=clean_optional(category_8),
        industry_code=clean_optional(industry_code),
        industry_name=clean_optional(industry_name),
        mpn=clean_optional(mpn),
        gtin=clean_optional(gtin),
        upc=clean_optional(upc),
        ean=clean_optional(ean),
        unspc=clean_optional(unspc),
        description=clean_optional(description),
        prod_short_desc=clean_optional(prod_short_desc),
        prod_long_desc=clean_optional(prod_long_desc),
        features_1=clean_optional(features_1),
        features_2=clean_optional(features_2),
        features_3=clean_optional(features_3),
        features_4=clean_optional(features_4),
        features_5=clean_optional(features_5),
        features_6=clean_optional(features_6),
        features_7=clean_optional(features_7),
        features_8=clean_optional(features_8),
        features_9=clean_optional(features_9),
        features_10=clean_optional(features_10),
        images=image_url,
        videos=video_url,
        documents=documents_url,
        attributes=attributes_data
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    print(db_product)
    return db_product
    
    
class ProductResponse(StrictBaseModel):
    product_code: str
    product_name: str

    parent_sku: Optional[str] = None
    variant_sku: Optional[str] = None
    product_type: Optional[str] = None

    brand_code: Optional[str] = None
    brand_name: Optional[str] = None

    vendor_code: Optional[str] = None
    vendor_name: Optional[str] = None

    industry_code: Optional[str] = None
    industry_name: Optional[str] = None

    mpn: Optional[str] = None
    gtin: Optional[str] = None
    upc: Optional[str] = None
    ean: Optional[str] = None
    unspc: Optional[str] = None

    description: Optional[str] = None
    prod_short_desc: Optional[str] = None
    prod_long_desc: Optional[str] = None

    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    documents: Optional[List[str]] = None

    attributes: Optional[Dict[str, Any]] = None

    model_config = {
        "from_attributes": True
    }

def parse_json_field(value, default):
    if value is None:
        return default
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default
    return value
    
@protected_router.get("/all_products", response_model=list[ProductResponse])
def view_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    products = db.query(Products).all()
    result = []

    for product in products:
        result.append({
            "product_code": product.product_code,
            "product_name": product.product_name,
            "parent_sku": product.parent_sku,
            "variant_sku": product.variant_sku,
            "product_type": product.product_type,
            "brand_code": product.brand_code,
            "brand_name": product.brand_name,
            "vendor_code": product.vendor_code,
            "vendor_name": product.vendor_name,
            "industry_code": product.industry_code,
            "industry_name": product.industry_name,
            "mpn": product.mpn,
            "gtin": product.gtin,
            "upc": product.upc,
            "ean": product.ean,
            "unspc": product.unspc,
            "description": product.description,
            "prod_short_desc": product.prod_short_desc,
            "prod_long_desc": product.prod_long_desc,
            "images": parse_json_field(product.images, []),
            "videos": parse_json_field(product.videos, []),
            "documents": parse_json_field(product.documents, []),
            "attributes": parse_json_field(product.attributes, {}),
 
        
        })
    return result


@protected_router.get("/product/{product_code}", response_model=ProductResponse)
def get_product(product_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_product = db.query(Products).filter(Products.product_code == product_code).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "product_code": db_product.product_code,
        "product_name": db_product.product_name,
        "parent_sku": db_product.parent_sku,
        "variant_sku": db_product.variant_sku,
        "product_type": db_product.product_type,
        "brand_code": db_product.brand_code,
        "brand_name": db_product.brand_name,
        "vendor_code": db_product.vendor_code,
        "vendor_name": db_product.vendor_name,
        "industry_code": db_product.industry_code,
        "industry_name": db_product.industry_name,
        "mpn": db_product.mpn,
        "gtin": db_product.gtin,
        "upc": db_product.upc,
        "ean": db_product.ean,
        "unspc": db_product.unspc,
        "description": db_product.description,
        "prod_short_desc": db_product.prod_short_desc,
        "prod_long_desc": db_product.prod_long_desc,
        "images": parse_json_field(db_product.images, []),
        "videos": parse_json_field(db_product.videos, []),
        "documents": parse_json_field(db_product.documents, []),
        "attributes": parse_json_field(db_product.attributes, {}),
    }

# class ProductUpdate(StrictBaseModel):
#     product_name: Optional[str] = None
#     parent_sku: Optional[str] = None
#     variant_sku: Optional[str] = None
#     product_type: Optional[str] = None

#     brand_code: Optional[str] = None
#     brand_name: Optional[str] = None

#     vendor_code: Optional[str] = None
#     vendor_name: Optional[str] = None

#     category_code: Optional[str] = None
#     category_1: Optional[str] = None
#     category_2: Optional[str] = None
#     category_3: Optional[str] = None
#     category_4: Optional[str] = None
#     category_5: Optional[str] = None
#     category_6: Optional[str] = None
#     category_7: Optional[str] = None
#     category_8: Optional[str] = None

#     industry_code: Optional[str] = None
#     industry_name: Optional[str] = None

#     mpn: Optional[str] = None
#     gtin: Optional[str] = None
#     upc: Optional[str] = None
#     ean: Optional[str] = None
#     unspc: Optional[str] = None

#     description: Optional[str] = None
#     prod_short_desc: Optional[str] = None
#     prod_long_desc: Optional[str] = None

#     images: Optional[List[str]] = None
#     videos: Optional[List[str]] = None
#     documents: Optional[List[str]] = None

#     features_1: Optional[str] = None
#     features_2: Optional[str] = None
#     features_3: Optional[str] = None
#     features_4: Optional[str] = None
#     features_5: Optional[str] = None
#     features_6: Optional[str] = None
#     features_7: Optional[str] = None
#     features_8: Optional[str] = None
#     features_9: Optional[str] = None
#     features_10: Optional[str] = None

#     attributes: Optional[Dict[str, Any]] = None
#    

# @protected_router.put("/product/{product_code}", response_model=ProductResponse)
# def update_product(
#     product_code: str,
#     payload: ProductUpdate,
#     db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
#     db_product = (
#         db.query(Products)
#         .filter(Products.product_code == product_code)
#         .first()
#     )
#     if not db_product:
#         raise HTTPException(status_code=404, detail="Product not found")

#     update_data = payload.dict(exclude_unset=True)
    
#     for key, value in update_data.items():
#         setattr(db_product, key, value)
    
#     db.commit()
#     db.refresh(db_product)

#     return {
#         "product_code": db_product.product_code,
#         "product_name": db_product.product_name,
#         "parent_sku": db_product.parent_sku,
#         "variant_sku": db_product.variant_sku,
#         "product_type": db_product.product_type,
#         "brand_code": db_product.brand_code,
#         "brand_name": db_product.brand_name,
#         "vendor_code": db_product.vendor_code,
#         "vendor_name": db_product.vendor_name,
#         "industry_code": db_product.industry_code,
#         "industry_name": db_product.industry_name,
#         "mpn": db_product.mpn,
#         "gtin": db_product.gtin,
#         "upc": db_product.upc,
#         "ean": db_product.ean,
#         "unspc": db_product.unspc,
#         "description": db_product.description,
#         "prod_short_desc": db_product.prod_short_desc,
#         "prod_long_desc": db_product.prod_long_desc,
#         "images": parse_json_field(db_product.images, []),
#         "videos": parse_json_field(db_product.videos, []),
#         "documents": parse_json_field(db_product.documents, []),
#         "attributes": parse_json_field(db_product.attributes, {}),
#     }


    


@protected_router.delete("/product/{product_code}", status_code=204)
def delete_product(
    product_code: str,
    db: Session = Depends(get_db),current_user:User=Depends(get_current_user)
):
    db_product = (
        db.query(Products)
        .filter(Products.product_code == product_code)
        .first()
    )

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(db_product)
    db.commit()

    return {
        "message": "Product deleted successfully"   
    }


app.include_router(protected_router, prefix="/api")
app.include_router(import_export_router,prefix="/import-export")

@app.post("/logout")
def logout():
    return {
        "message": "Logout successful. Please delete the token on the client."
    }
