from sqlalchemy import String,Boolean,Integer,Column,JSON,Text,Float
from database import Base

from sqlalchemy.dialects.postgresql import JSONB
class User(Base):
    __tablename__="users"

    id=Column(Integer,primary_key=True,index=True)
    username=Column(String)
    user_code=Column(String,unique=True)
    email=Column(String)
    password=Column(String)


class Vendor(Base):
    __tablename__="vendors"

    id=Column(Integer,primary_key=True,index=True)
    vendor_code=Column(String(100),unique=True,nullable=False)
    vendor_name=Column(String(30),nullable=False)
    contact_email=Column(String(30))
    contact_phone=Column(String(30))
    business_type=Column(String(30))
    industry=Column(String(30))
    country=Column(String(30))
    vendor_logo_url=Column(JSON)
  
    dept1_poc_name=Column(String)
    dept1_email=Column(String)
    dept1_phone=Column(String)

    dept2_poc_name=Column(String)
    dept2_email=Column(String)
    dept2_phone=Column(String)

    dept3_poc_name=Column(String)
    dept3_email=Column(String)
    dept3_phone=Column(String)

    dept4_poc_name=Column(String)
    dept4_email=Column(String)
    dept4_phone=Column(String)

    dept5_poc_name=Column(String)
    dept5_email=Column(String)
    dept5_phone=Column(String)
    
    is_active = Column(Boolean, default=True, nullable=False)

class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(100), unique=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    parent_sku = Column(String(100))
    variant_sku = Column(String(100))
    product_type = Column(String(50))
    brand_code = Column(String(50))
    brand_name = Column(String(100))
    vendor_code = Column(String(50))
    vendor_name = Column(String(100))
    category_code = Column(String(50))
    category_1 = Column(String(100))
    category_2 = Column(String(100))
    category_3 = Column(String(100))
    category_4 = Column(String(100))
    category_5 = Column(String(100))
    category_6 = Column(String(100))
    category_7 = Column(String(100))
    category_8 = Column(String(100))
    industry_code = Column(String(50))
    industry_name = Column(String(100))
    mpn = Column(String(100), index=True)  
    gtin = Column(String(100))
    upc = Column(String(100))
    ean = Column(String(100))
    unspc = Column(String(100))
    description = Column(Text)
    prod_short_desc = Column(String(255))
    prod_long_desc = Column(Text)
    images = Column(JSONB, default=list)
    videos = Column(JSONB, default=list)
    documents = Column(JSONB, default=list)
    attributes = Column(JSONB, default=dict)
  
    features_1 = Column(String(255))
    features_2 = Column(String(255))
    features_3 = Column(String(255))
    features_4 = Column(String(255))
    features_5 = Column(String(255))
    features_6 = Column(String(255))
    features_7 = Column(String(255))
    features_8 = Column(String(255))
    features_9 = Column(String(255))
    features_10 = Column(String(255))
    enrichment_status = Column(String(50), default="pending", nullable=False)
    completeness_score = Column(Float)
    completeness_details = Column(JSON)
   
