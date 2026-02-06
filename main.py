from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel,EmailStr
from sqlalchemy.orm import Session
from models import Vendor,Products
from database import get_db
from typing import List, Optional, Dict, Any
from import_export import router as import_export_router

app=FastAPI()



class VendorCreate(BaseModel):
    vendor_code:str
    vendor_name:str
    contact_email:EmailStr
    contact_phone:str
    business_type:str
    industry:str
    country:str
    # vendor_logo_url:str
  
    dept1_poc_name:str
    dept1_email:str
    dept1_phone:str

    dept2_poc_name:str
    dept2_email:str
    dept2_phone:str

    dept3_poc_name:str
    dept3_email:str
    dept3_phone:str

    dept4_poc_name:str
    dept4_email:str
    dept4_phone:str

    dept5_poc_name:str
    dept5_email:str
    dept5_phone:str


#Create vendor
@app.post("/add_vendor")
def create_vendor(vendor:VendorCreate,db:Session=Depends(get_db)):
    existing_vendor=db.query(Vendor).filter(Vendor.vendor_code==vendor.vendor_code).first()
    if existing_vendor:
       raise HTTPException(status_code=400,detail="vendor already exists")
    
    db_vendor=Vendor(
    vendor_code=vendor.vendor_code,
    vendor_name=vendor.vendor_name,
    contact_email=vendor.contact_email,
    contact_phone=vendor.contact_phone,
  
    business_type=vendor.business_type,
    industry=vendor.industry,
    country=vendor.country,
    # vendor_logo_url=vendor.vendor_logo_url,
  
    dept1_poc_name=vendor.dept1_poc_name,
    dept1_email=vendor.dept1_email,
    dept1_phone=vendor.dept1_phone,
    
    dept2_poc_name=vendor.dept2_poc_name,
    dept2_email=vendor.dept2_email,
    dept2_phone=vendor.dept2_phone,

    dept3_poc_name=vendor.dept3_poc_name,
    dept3_email=vendor.dept3_email,
    dept3_phone=vendor.dept3_phone,

    dept4_poc_name=vendor.dept4_poc_name,
    dept4_email=vendor.dept4_email,
    dept4_phone=vendor.dept4_phone,

    dept5_poc_name=vendor.dept5_poc_name,
    dept5_email=vendor.dept5_email,
    dept5_phone=vendor.dept5_phone
    )

    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


class VendorResponse(BaseModel):
    vendor_code:str
    vendor_name:str
    contact_email:EmailStr
    contact_phone:str
    business_type:str
    industry:str
    country:str
    # vendor_logo_url:str
  
#READ
@app.get("/all_vendors",response_model=list[VendorResponse])
def view_vendors(db:Session=Depends(get_db)):
    return db.query(Vendor).all()


@app.get("/vendor/{id}",response_model=VendorResponse)
def get_user(id:int,db: Session = Depends(get_db)):
    db_vendor=db.query(Vendor).filter(Vendor.id==id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor


class VendorUpdate(BaseModel):
    vendor_code:str
    vendor_name:str
    contact_email:EmailStr
    contact_phone:str
    business_type:str
    industry:str
    country:str
    # vendor_logo_url:str
   
    dept1_poc_name:str
    dept1_email:str
    dept1_phone:str

    dept2_poc_name:str
    dept2_email:str
    dept2_phone:str

    dept3_poc_name:str
    dept3_email:str
    dept3_phone:str

    dept4_poc_name:str
    dept4_email:str
    dept4_phone:str

    dept5_poc_name:str
    dept5_email:str
    dept5_phone:str

#UPDATE
@app.put("/vendor/{id}", response_model=VendorResponse)
def update_vendor(id: int, vendor: VendorUpdate, db: Session = Depends(get_db)):
    db_vendor = db.query(Vendor).filter(Vendor.id == id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    
    for key, value in vendor.dict(exclude_unset=True).items():
        setattr(db_vendor, key, value)
    
    db.commit()
    db.refresh(db_vendor)
    return db_vendor



#DELETE

@app.delete("/vendor/{id}")
def delete_vendor(id:int,db:Session=Depends(get_db)):
     db_vendor=db.query(Vendor).filter(Vendor.id==id).first()
     if not db_vendor:
         raise HTTPException(status_code=400,detail="VEndor not found")
    #  db.delete(db_vendor)
     db_vendor.is_active = False
     db.commit()
     return{
        "message":"vendor DELETED"
     }




class ProductCreate(BaseModel):
    product_code: str
    product_name: str

    parent_sku:str
    variant_sku:str 
    product_type:str 
    brand_code:str 
    brand_name:str 
    vendor_code:str 
    vendor_name:str 
    category_code:str 
    category_1:str 
    category_2:str 
    category_3:str 
    category_4:str 
    category_5:str 
    category_6:str 
    category_7:str 
    category_8:str 
    industry_code:str
    industry_name:str

    mpn:str 
    gtin:str 
    upc:str 
    ean:str 
    unspc:str 

    description:str
    prod_short_desc:str
    prod_long_desc:str
    images: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    documents: Optional[List[str]] = []

    features_1: str
    features_2: str
    features_3: str
    features_4: str
    features_5: str
    features_6: str
    features_7: str
    features_8: str
    features_9: str
    features_10:str

    attributes: Optional[Dict[str, Any]] = {}


@app.post("/create_products")
def product(product:ProductCreate,db:Session=Depends(get_db)):
    existing = db.query(Products).filter(Products.product_code == product.product_code).first()

    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")
    
    db_product=Products(
    product_code=product.product_code,
    product_name=product.product_name,
    parent_sku=product.parent_sku,
    variant_sku=product.variant_sku,
    product_type=product.product_type,
    brand_code=product.brand_code,
    brand_name=product.brand_name,
    vendor_code=product.vendor_code,
    vendor_name=product.vendor_name,
    category_code=product.category_code,
    category_1=product.category_1,
    category_2=product.category_2,
    category_3=product.category_3,
    category_4=product.category_4,
    category_5=product.category_5,
    category_6=product.category_6,
    category_7=product.category_7,
    category_8=product.category_8,
    industry_code=product.industry_code,
    industry_name=product.industry_name,
    mpn=product.mpn,
    gtin=product.gtin,
    upc=product.upc,
    ean=product.ean,
    unspc=product.unspc,
    description=product.description,
    prod_short_desc=product.prod_short_desc,
    prod_long_desc=product.prod_long_desc,
    images=product.images,
    videos=product.videos,
    documents=product.documents,
    features_1=product.features_1,
    features_2=product.features_2,
    features_3=product.features_3,
    features_4=product.features_4,
    features_5=product.features_5,
    features_6=product.features_6,
    features_7=product.features_7,
    features_8=product.features_8,
    features_9=product.features_9,
    features_10=product.features_10,
    attributes=product.attributes
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product

class ProductResponse(BaseModel):
    product_code: str
    product_name: str
    parent_sku:str
    variant_sku:str 
    product_type:str 
    brand_code:str 
    brand_name:str 
    vendor_code:str 
    vendor_name:str 
    industry_code:str
    industry_name:str
    mpn:str 
    gtin:str 
    upc:str 
    ean:str 
    unspc:str 
    description:str
    prod_short_desc:str
    prod_long_desc:str
    images: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    documents: Optional[List[str]] = []

    attributes: Optional[Dict[str, Any]] = {} 


@app.get("/all_products",response_model=list[(ProductResponse)])
def view_products(db:Session=Depends(get_db)):
      return db.query(Products).all()



@app.get("/product/{product_code}",response_model=ProductResponse)
def get_product(code:str,db:Session=Depends(get_db)):
     db_product=db.query(Products).filter(Products.product_code==code).first()
     if not db_product:
         raise HTTPException(status_code=404,detail="product not found")
     return db_product


class ProductUpdate(BaseModel):
    product_code: str
    product_name: str
    parent_sku:str
    variant_sku:str 
    product_type:str 
    brand_code:str 
    brand_name:str 
    vendor_code:str 
    vendor_name:str 
    category_code:str 
    category_1:str 
    category_2:str 
    category_3:str 
    category_4:str 
    category_5:str 
    category_6:str 
    category_7:str 
    category_8:str 
    industry_code:str
    industry_name:str
    mpn:str 
    gtin:str 
    upc:str 
    ean:str 
    unspc:str 
    description:str
    prod_short_desc:str
    prod_long_desc:str
    images: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    documents: Optional[List[str]] = []
    features_1: str
    features_2: str
    features_3: str
    features_4: str
    features_5: str
    features_6: str
    features_7: str
    features_8: str
    features_9: str
    features_10:str

    attributes: Optional[Dict[str, Any]] = {}


@app.put("/product/{product_code}", response_model=ProductResponse)
def update_product(
    product_code: str,
    product: ProductUpdate,
    db: Session = Depends(get_db)):
    db_product = (
        db.query(Products)
        .filter(Products.product_code == product_code)
        .first()
    )
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product.dict(exclude_unset=True)
    update_data.pop("product_code", None)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)

    return db_product


@app.delete("/product/{product_code}", status_code=204)
def delete_product(
    product_code: str,
    db: Session = Depends(get_db)
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

    return


app.include_router(import_export_router, prefix="/api")