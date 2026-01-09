from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from app.core.utils import gen_uuid, now_iso
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/{userId}")
def get_cart(userId: str, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    docs = db().collection("cart_items").where("user_id", "==", userId).stream()
    return {"items": [d.to_dict() for d in docs]}

@router.post("/{userId}/items")
def add_to_cart(userId: str, payload: dict, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    t = now_iso()
    cid = gen_uuid()

    doc = {
        "id": cid,
        "user_id": userId,
        "product_id": payload.get("product_id"),
        "product_variant_id": payload.get("product_variant_id"),
        "quantity": int(payload.get("quantity", 1)),
        "created_at": t,
        "updated_at": t
    }
    if not doc["product_id"]:
        raise HTTPException(400, detail="product_id required")

    db().collection("cart_items").document(cid).set(doc)
    return {"message": "Added to cart", "id": cid}

@router.put("/{userId}/items/{itemId}")
def update_cart_item(userId: str, itemId: str, payload: dict, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    doc = db().collection("cart_items").document(itemId).get()
    if not doc.exists:
        raise HTTPException(404, detail="Cart item not found")

    data = doc.to_dict() or {}
    if data.get("user_id") != userId:
        raise HTTPException(403, detail="Forbidden")

    upd = {
        "quantity": int(payload.get("quantity", data.get("quantity", 1))),
        "updated_at": now_iso()
    }
    db().collection("cart_items").document(itemId).set(upd, merge=True)
    return {"message": "Cart item updated"}

@router.delete("/{userId}/items/{itemId}")
def remove_cart_item(userId: str, itemId: str, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    doc = db().collection("cart_items").document(itemId).get()
    if doc.exists and (doc.to_dict() or {}).get("user_id") != userId:
        raise HTTPException(403, detail="Forbidden")

    db().collection("cart_items").document(itemId).delete()
    return {"message": "Removed from cart"}

@router.delete("/{userId}")
def clear_cart(userId: str, user=Depends(get_current_user)):
    if user["role"] != "admin" and user["uid"] != userId:
        raise HTTPException(403, detail="Forbidden")

    docs = db().collection("cart_items").where("user_id", "==", userId).stream()
    for d in docs:
        db().collection("cart_items").document(d.id).delete()
    return {"message": "Cart cleared"}
