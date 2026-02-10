from fileinput import filename
import random
import string
import json
import pandas as pd
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Vendor, User,Products
from auth import get_current_user
from io import BytesIO
import xlrd

import_export_router = APIRouter(dependencies=[Depends(get_current_user)])



def generate_vendor_code(length: int = 6) -> str:
    generate= "VEND-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
    print(f"Generated vendor code: {generate}")
    return generate
    
import math
##FIXING NAN 
def clean_str(val):
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    val = str(val).strip()
    if val.lower() == "nan" or val == '""' or val == "":
        return None
    return val

def clean_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        val = val.strip()
        if val == "":
            return []
        try:
            parsed = json.loads(val)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []

def clean_dict(val):
    if val is None:
        return None
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        val = val.strip()
        if val == "":
            return None
        try:
            parsed = json.loads(val)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None
    return None




@import_export_router.post("/import/vendors/excel")
async def import_vendors_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    filename = file.filename.lower()
    try: 
         if filename.endswith(".csv"):
             df = pd.read_csv(file.file, dtype=str)
         elif filename.endswith(".xlsx"):
             df = pd.read_excel(file.file, engine="openpyxl", dtype=str)
         elif filename.endswith(".xls"):
              df = pd.read_excel(file.file, engine="xlrd", dtype=str)
         else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

         df = df.where(pd.notna(df), None)
         data = df.to_dict(orient="records")
         
    except Exception as e:
          raise HTTPException(status_code=400, detail=f"Failed to read Excel: {str(e)}")

    success_count = 0
    failed_records = []
    

    for idx, item in enumerate(data):
        vendor_code = clean_str(item.get("vendor_code"))
        vendor_name = clean_str(item.get("vendor_name"))

        if not vendor_code and not vendor_name:
            failed_records.append({
                "index": idx,
                "reason": "Either vendor_code or vendor_name must be provided"
            })
            continue

        # ---- Generate vendor code if missing (DB-safe) ----
        if not vendor_code:
            while True:
                vendor_code = generate_vendor_code()
                if not db.query(Vendor).filter(
                    Vendor.vendor_code == vendor_code
                ).first():
                    break

        # ---- Check duplicates ----
        duplicate = db.query(Vendor).filter(
            (Vendor.vendor_code == vendor_code) |
            (Vendor.vendor_name == vendor_name)
        ).first()

        if duplicate:
            failed_records.append({
                "index": idx,
                "reason": "Duplicate vendor_code or vendor_name"
            })
            continue

        vendor = Vendor(
            vendor_code=vendor_code,
            vendor_name=vendor_name,
            contact_email=clean_str(item.get("contact_email")),
            contact_phone=clean_str(item.get("contact_phone")),
            business_type=clean_str(item.get("business_type")),
            industry=clean_str(item.get("industry")),
            country=clean_str(item.get("country")),
            vendor_logo_url=clean_dict(item.get("vendor_logo_url")),
            dept1_poc_name=clean_str(item.get("dept1_poc_name")),
            dept1_email=clean_str(item.get("dept1_email")),
            dept1_phone=clean_str(item.get("dept1_phone")),
            dept2_poc_name=clean_str(item.get("dept2_poc_name")),
            dept2_email=clean_str(item.get("dept2_email")),
            dept2_phone=clean_str(item.get("dept2_phone")),
            dept3_poc_name=clean_str(item.get("dept3_poc_name")),
            dept3_email=clean_str(item.get("dept3_email")),
            dept3_phone=clean_str(item.get("dept3_phone")),
            dept4_poc_name=clean_str(item.get("dept4_poc_name")),
            dept4_email=clean_str(item.get("dept4_email")),
            dept4_phone=clean_str(item.get("dept4_phone")),
            dept5_poc_name=clean_str(item.get("dept5_poc_name")),
            dept5_email=clean_str(item.get("dept5_email")),
            dept5_phone=clean_str(item.get("dept5_phone")),
            is_active=True
        )

        db.add(vendor)
        try:
            db.commit()
            success_count += 1
        except Exception:
            db.rollback()
            failed_records.append({
                "index": idx,
                "reason": "Database error or duplicate detected"
            })

    return {
        "success_count": success_count,
        "failed_count": len(failed_records),
        "failed_records": failed_records
    }


@import_export_router.get("/export/vendors/excel")
def export_vendors_excel(db: Session = Depends(get_db)):
    vendors = db.query(Vendor).all()

    headers = [
        "vendor_code", "vendor_name", "contact_email", "contact_phone",
        "business_type", "industry", "country", "vendor_logo_url",
        "dept1_poc_name","dept1_email","dept1_phone",
        "dept2_poc_name","dept2_email","dept2_phone",
        "dept3_poc_name","dept3_email","dept3_phone",
        "dept4_poc_name","dept4_email","dept4_phone",
        "dept5_poc_name","dept5_email","dept5_phone"
    ]

    data = []
    for v in vendors:
        row = {}
        for h in headers:
            value = getattr(v, h, "")
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            row[h] = value
        data.append(row)

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Vendors")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=vendors.xlsx"}
    )



@import_export_router.post("/import/products/excel")
async def import_products_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename.lower()
    try: 
         if filename.endswith(".csv"):
             df = pd.read_csv(file.file, dtype=str)
         elif filename.endswith(".xlsx"):
             df = pd.read_excel(file.file, engine="openpyxl", dtype=str)
         elif filename.endswith(".xls"):
              df = pd.read_excel(file.file, engine="xlrd", dtype=str)
         else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

         df = df.where(pd.notna(df), None)
         data = df.to_dict(orient="records")
         
    except Exception as e:
          raise HTTPException(status_code=400, detail=f"Failed to read Excel: {str(e)}")

    success_count = 0
    failed_records = []

    for idx, item in enumerate(data):

        product_code = clean_str(item.get("product_code"))
        product_name = clean_str(item.get("product_name"))

        if not product_code or not product_name:
            failed_records.append({
                "index": idx,
                "reason": "product_code or product_name missing"
            })
            continue

        existing = db.query(Products).filter(Products.product_code == product_code).first()
        if existing:
            failed_records.append({
                "index": idx,
                "reason": "Duplicate product_code"
            })
            continue

        product = c(
            product_code=product_code,
            product_name=product_name,

            vendor_code=clean_str(item.get("vendor_code")),
            vendor_name=clean_str(item.get("vendor_name")),

            parent_sku=clean_str(item.get("parent_sku")),
            variant_sku=clean_str(item.get("variant_sku")),
            product_type=clean_str(item.get("product_type")),

            brand_code=clean_str(item.get("brand_code")),
            brand_name=clean_str(item.get("brand_name")),

         
            images=json.dumps(clean_list(item.get("images"))),
            videos=json.dumps(clean_list(item.get("videos"))),
            documents=json.dumps(clean_list(item.get("documents"))),
            attributes=json.dumps(clean_dict(item.get("attributes")) or {}),

            enrichment_status="pending"
        )

        db.add(product)
        try:
            db.commit()
            success_count += 1
        except Exception as e:
            db.rollback()
            failed_records.append({
                "index": idx,
                "reason": str(e)
            })

    return {
        "success_count": success_count,
        "failed_count": len(failed_records),
        "failed_records": failed_records
    }

@import_export_router.get("/export/products/excel")
def export_products_excel(db: Session = Depends(get_db)):
    products = db.query(Products).all()

    headers = [
        "product_code","product_name","parent_sku","variant_sku","product_type",
        "brand_code","brand_name","vendor_code","vendor_name",
        "category_code","category_1","category_2","category_3","category_4",
        "category_5","category_6","category_7","category_8",
        "industry_code","industry_name","mpn","gtin","upc","ean","unspc",
        "description","prod_short_desc","prod_long_desc",
        "images","videos","documents",
        "features_1","features_2","features_3","features_4","features_5",
        "features_6","features_7","features_8","features_9","features_10",
        "attributes"
    ]

    data = []
    for p in products:
        row = {}
        for h in headers:
            value = getattr(p, h, "")
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            row[h] = value
        data.append(row)

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Products")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=products.xlsx"}
    )
