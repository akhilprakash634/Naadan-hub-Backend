from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from app.core.utils import now_iso
from app.core.deps import get_current_user, require_roles, require_seller_approved

router = APIRouter()

@router.get("/{sellerId}")
def get_seller_profile(sellerId: str):
    s = db().collection("seller_profiles").document(sellerId).get()
    if not s.exists:
        raise HTTPException(404, detail="Seller profile not found")
    return s.to_dict()

@router.put("/{sellerId}")
def update_seller_profile(sellerId: str, payload: dict, user=Depends(get_current_user)):
    if user["role"] not in ["seller", "admin"]:
        raise HTTPException(403, detail="Forbidden")
    if user["role"] == "seller" and user["uid"] != sellerId:
        raise HTTPException(403, detail="Forbidden")

    # sellers can't approve themselves
    if user["role"] == "seller":
        payload.pop("approval_status", None)
        payload.pop("rejection_reason", None)
        payload.pop("is_verified", None)

    payload["updated_at"] = now_iso()
    db().collection("seller_profiles").document(sellerId).set(payload, merge=True)
    return {"message": "Seller profile updated"}

@router.get("/{sellerId}/stats")
def get_seller_stats(sellerId: str, user=Depends(get_current_user)):
    # seller or admin; seller only their own
    if user["role"] not in ["seller", "admin"]:
        raise HTTPException(403, detail="Forbidden")
    if user["role"] == "seller" and user["uid"] != sellerId:
        raise HTTPException(403, detail="Forbidden")

    # compute quickly (for large scale store seller_stats materialized)
    products = list(db().collection("products").where("seller_id", "==", sellerId).stream())
    active_products = [p for p in products if (p.to_dict() or {}).get("is_active") is True]
    orders = list(db().collection("orders").where("seller_id", "==", sellerId).stream())
    pending_orders = [o for o in orders if (o.to_dict() or {}).get("status") in ["pending","confirmed","packed","shipped"]]
    completed_orders = [o for o in orders if (o.to_dict() or {}).get("status") == "delivered"]

    revenue = 0.0
    for o in orders:
        revenue += float((o.to_dict() or {}).get("total_amount") or 0)

    reviews = list(db().collection("reviews").where("seller_id", "==", sellerId).stream())
    avg_rating = 0.0
    if reviews:
        avg_rating = sum(int((r.to_dict() or {}).get("rating") or 0) for r in reviews) / len(reviews)

    return {
        "seller_id": sellerId,
        "total_products": len(products),
        "active_products": len(active_products),
        "total_orders": len(orders),
        "pending_orders": len(pending_orders),
        "completed_orders": len(completed_orders),
        "total_revenue": revenue,
        "average_rating": avg_rating,
        "total_reviews": len(reviews),
        "last_updated": now_iso()
    }

@router.get("/{sellerId}/products")
def get_seller_products(sellerId: str):
    docs = db().collection("products").where("seller_id", "==", sellerId).stream()
    return {"items": [d.to_dict() for d in docs]}

@router.get("/{sellerId}/reviews")
def get_seller_reviews(sellerId: str):
    docs = db().collection("reviews").where("seller_id", "==", sellerId).stream()
    return {"items": [d.to_dict() for d in docs]}

# Dashboard Stats APIs (Seller)
@router.get("/{sellerId}/dashboard-stats")
def seller_dashboard_stats(sellerId: str, user=Depends(require_seller_approved)):
    if user["role"] == "seller" and user["uid"] != sellerId:
        raise HTTPException(403, detail="Forbidden")

    products = list(db().collection("products").where("seller_id", "==", sellerId).stream())
    orders = list(db().collection("orders").where("seller_id", "==", sellerId).stream())

    return {"products": len(products), "orders": len(orders)}
