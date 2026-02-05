from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel,EmailStr
from sqlalchemy.orm import Session
from models import Vendor
from database import get_db

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
    return {
        "id": db_vendor.id,
        "vendor_code": db_vendor.vendor_code,
        "vendor_name": db_vendor.vendor_name,
        "contact_email": db_vendor.contact_email
    }


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