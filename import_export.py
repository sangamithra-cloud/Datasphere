from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd
import json
from database import get_db
from models import Vendor, Products

router = APIRouter()


@router.post("/import/vendors/excel")
async def import_vendors_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files are supported")

    try:
        df = pd.read_excel(file.file)
        data = df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read Excel: {str(e)}")

    success_count = 0
    failed_records = []

    for idx, item in enumerate(data):
        if not item.get("vendor_code") or not item.get("vendor_name"):
            failed_records.append({"index": idx, "reason": "vendor_code or vendor_name missing"})
            continue

        existing = db.query(Vendor).filter_by(vendor_code=item["vendor_code"]).first()
        if existing:
            failed_records.append({"index": idx, "reason": "Duplicate vendor_code"})
            continue

        vendor = Vendor(**item)
        db.add(vendor)
        try:
            db.commit()
            success_count += 1
        except Exception as e:
            db.rollback()
            failed_records.append({"index": idx, "reason": str(e)})

    return {
        "success_count": success_count,
        "failed_count": len(failed_records),
        "failed_records": failed_records
    }


@router.get("/export/vendors/excel")
def export_vendors_excel(db: Session = Depends(get_db)):
    vendors = db.query(Vendor).all()
    data = []
    headers = [
        "vendor_code", "vendor_name", "contact_email", "contact_phone", "business_type",
        "industry", "country", "vendor_logo_url",
        "dept1_poc_name","dept1_email","dept1_phone",
        "dept2_poc_name","dept2_email","dept2_phone",
        "dept3_poc_name","dept3_email","dept3_phone",
        "dept4_poc_name","dept4_email","dept4_phone",
        "dept5_poc_name","dept5_email","dept5_phone"
    ]

    for v in vendors:
        row = {h: getattr(v, h, "") for h in headers}
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


@router.post("/import/products/excel")
async def import_products_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files are supported")

    try:
        df = pd.read_excel(file.file)
        data = df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read Excel: {str(e)}")

    success_count = 0
    failed_records = []

    for idx, item in enumerate(data):
        if not item.get("product_code") or not item.get("product_name"):
            failed_records.append({"index": idx, "reason": "product_code or product_name missing"})
            continue

    
        item["images"] = item.get("images", [])
        item["videos"] = item.get("videos", [])
        item["documents"] = item.get("documents", [])
        item["attributes"] = item.get("attributes", {})

        existing = db.query(Products).filter_by(product_code=item["product_code"]).first()
        if existing:
            failed_records.append({"index": idx, "reason": "Duplicate product_code"})
            continue

        product = Products(**item)
        db.add(product)
        try:
            db.commit()
            success_count += 1
        except Exception as e:
            db.rollback()
            failed_records.append({"index": idx, "reason": str(e)})

    return {
        "success_count": success_count,
        "failed_count": len(failed_records),
        "failed_records": failed_records
    }

@router.get("/export/products/excel")
def export_products_excel(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    data = []
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

    for p in products:
        row = {}
        for h in headers:
            value = getattr(p, h, "")
            if isinstance(value, list) or isinstance(value, dict):
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
