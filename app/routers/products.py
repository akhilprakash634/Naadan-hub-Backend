from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.firebase import db
from app.core.utils import gen_uuid, now_iso
from app.core.deps import require_roles, require_seller_approved, get_current_user

router = APIRouter()

def _ensure_unique(collection: str, field: str, value: str, exclude_id: str | None = None):
    q = db().collection(collection).where(field, "==", value).limit(1).stream()
    for doc in q:
        if exclude_id and doc.id == exclude_id:
            continue
        raise HTTPException(409, detail=f"{field} must be unique")

@router.get("")
def get_all_products(
    category: str | None = None,
    subcategory: str | None = None,
    search: str | None = None,
    min_price: float | None = Query(default=None, alias="minPrice"),
    max_price: float | None = Query(default=None, alias="maxPrice"),
    is_active: bool | None = Query(default=True, alias="isActive")
):
    ref = db().collection("products")

    # Basic filters (Firestore composite indexes may be required)
    if is_active is not None:
        ref = ref.where("is_active", "==", bool(is_active))
    if category:
        ref = ref.where("category", "==", category)
    if subcategory:
        ref = ref.where("subcategory", "==", subcategory)
    if min_price is not None:
        ref = ref.where("price", ">=", float(min_price))
    if max_price is not None:
        ref = ref.where("price", "<=", float(max_price))

    items = [d.to_dict() for d in ref.stream()]

    if search:
        s = search.lower().strip()
        items = [x for x in items if s in (x.get("name","").lower() + " " + (x.get("description","") or "").lower())]

    return {"items": items}

@router.get("/{id}")
def get_product_by_id(id: str):
    doc = db().collection("products").document(id).get()
    if not doc.exists:
        raise HTTPException(404, detail="Product not found")
    return doc.to_dict()

@router.post("")
def create_product(payload: dict, user=Depends(require_seller_approved)):
    # seller/admin
    t = now_iso()
    pid = gen_uuid()

    # uniqueness checks
    if payload.get("slug"):
        _ensure_unique("products", "slug", payload["slug"])
    if payload.get("sku"):
        _ensure_unique("products", "sku", payload["sku"])

    doc = {
        "id": pid,
        "seller_id": payload.get("seller_id") or user["uid"],
        "name": payload.get("name"),
        "slug": payload.get("slug"),
        "description": payload.get("description"),
        "short_description": payload.get("short_description"),
        "category": payload.get("category"),
        "subcategory": payload.get("subcategory"),
        "price": payload.get("price", 0),
        "original_price": payload.get("original_price"),
        "discount_percentage": payload.get("discount_percentage"),
        "unit": payload.get("unit"),
        "stock_quantity": payload.get("stock_quantity", 0),
        "min_order_quantity": payload.get("min_order_quantity", 1),
        "max_order_quantity": payload.get("max_order_quantity"),
        "sku": payload.get("sku"),
        "images": payload.get("images", []),
        "nutritional_info": payload.get("nutritional_info", {}),
        "storage_instructions": payload.get("storage_instructions"),
        "shelf_life": payload.get("shelf_life"),
        "origin": payload.get("origin"),
        "is_organic": bool(payload.get("is_organic", False)),
        "is_featured": bool(payload.get("is_featured", False)),
        "is_active": bool(payload.get("is_active", True)),
        "total_sold": payload.get("total_sold", 0),
        "rating": payload.get("rating", 0),
        "review_count": payload.get("review_count", 0),
        "tags": payload.get("tags", []),
        "seo_title": payload.get("seo_title"),
        "seo_description": payload.get("seo_description"),
        "seo_keywords": payload.get("seo_keywords"),
        "created_at": t,
        "updated_at": t
    }

    db().collection("products").document(pid).set(doc)
    return {"message": "Product created", "id": pid}

@router.put("/{id}")
def update_product(id: str, payload: dict, user=Depends(require_seller_approved)):
    doc = db().collection("products").document(id).get()
    if not doc.exists:
        raise HTTPException(404, detail="Product not found")
    data = doc.to_dict() or {}

    # seller can update only their products
    if user["role"] == "seller" and data.get("seller_id") != user["uid"]:
        raise HTTPException(403, detail="Forbidden")

    # uniqueness checks on update
    if payload.get("slug"):
        _ensure_unique("products", "slug", payload["slug"], exclude_id=id)
    if payload.get("sku"):
        _ensure_unique("products", "sku", payload["sku"], exclude_id=id)

    payload["updated_at"] = now_iso()
    db().collection("products").document(id).set(payload, merge=True)
    return {"message": "Product updated"}

@router.delete("/{id}")
def delete_product(id: str, user=Depends(require_roles("admin"))):
    # admin only
    db().collection("products").document(id).delete()
    return {"message": "Product deleted"}

@router.patch("/{id}/status")
def toggle_product_status(id: str, payload: dict, user=Depends(require_seller_approved)):
    doc = db().collection("products").document(id).get()
    if not doc.exists:
        raise HTTPException(404, detail="Product not found")
    data = doc.to_dict() or {}
    if user["role"] == "seller" and data.get("seller_id") != user["uid"]:
        raise HTTPException(403, detail="Forbidden")

    is_active = bool(payload.get("is_active", payload.get("status", True)))
    db().collection("products").document(id).set({"is_active": is_active, "updated_at": now_iso()}, merge=True)
    return {"message": "Product status updated", "is_active": is_active}
