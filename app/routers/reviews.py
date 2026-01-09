from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from app.core.utils import gen_uuid, now_iso
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/product/{productId}")
def get_product_reviews(productId: str):
    docs = db().collection("reviews").where("product_id", "==", productId).stream()
    return {"items": [d.to_dict() for d in docs]}

@router.post("")
def create_review(payload: dict, user=Depends(get_current_user)):
    """
    reviews fields:
    user_id, product_id?, seller_id?, order_id, rating, title, comment, images, is_verified_purchase, helpful_count
    """
    t = now_iso()
    rid = gen_uuid()

    doc = {
        "id": rid,
        "user_id": user["uid"],
        "product_id": payload.get("product_id"),
        "seller_id": payload.get("seller_id"),
        "order_id": payload.get("order_id"),
        "rating": int(payload.get("rating", 0)),
        "title": payload.get("title"),
        "comment": payload.get("comment"),
        "images": payload.get("images", []),
        "is_verified_purchase": bool(payload.get("is_verified_purchase", False)),
        "helpful_count": int(payload.get("helpful_count", 0)),
        "created_at": t,
        "updated_at": t
    }
    if not doc["order_id"]:
        raise HTTPException(400, detail="order_id required")

    db().collection("reviews").document(rid).set(doc)

    # optional: update product review_count/rating (simple naive update)
    if doc["product_id"]:
        prod_ref = db().collection("products").document(doc["product_id"])
        prod = prod_ref.get()
        if prod.exists:
            pdata = prod.to_dict() or {}
            rc = int(pdata.get("review_count", 0)) + 1
            old_rating = float(pdata.get("rating", 0))
            new_rating = ((old_rating * (rc - 1)) + doc["rating"]) / rc if rc > 0 else doc["rating"]
            prod_ref.set({"review_count": rc, "rating": new_rating, "updated_at": t}, merge=True)

    return {"message": "Review created", "id": rid}

@router.get("/seller/{sellerId}")
def get_seller_reviews(sellerId: str):
    docs = db().collection("reviews").where("seller_id", "==", sellerId).stream()
    return {"items": [d.to_dict() for d in docs]}
